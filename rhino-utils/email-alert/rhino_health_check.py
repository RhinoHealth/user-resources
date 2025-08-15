#!/usr/bin/env python3
"""
Rhino Health Agent Health Check Script

This script queries the Rhino Health API to check agent status and sends email alerts
if the status is not "Completed".
"""

import argparse
import json
import smtplib
import sys
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional


class AgentStatus:
    COMPLETED = "Completed"
    UNKNOWN = "Unknown"


class ErrorTypes:
    API_ERROR = "API_ERROR"
    SCRIPT_ERROR = "SCRIPT_ERROR"


class TokenCache:
    """Simple token cache to avoid re-authentication."""
    def __init__(self):
        self.access_token: Optional[str] = None
        self.expires_at: Optional[float] = None
    
    def get_valid_token(self, config: Dict[str, Any]) -> str:
        """Get a valid token, refreshing if necessary."""
        if self.access_token and self.expires_at and time.time() < self.expires_at:
            return self.access_token
        return self.refresh_token(config)
    
    def refresh_token(self, config: Dict[str, Any]) -> str:
        """Authenticate and cache the new token."""
        token = authenticate_rhino_impl(config)
        self.access_token = token
        # Set expiration to 4 minutes (tokens expire in 5 minutes)
        self.expires_at = time.time() + 240
        return token


# Global token cache
_token_cache = TokenCache()


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure and required fields."""
    # Validate authentication config
    auth_config = config.get("rhino_auth", {})
    required_auth = ["username", "password"]
    missing_auth = [key for key in required_auth if not auth_config.get(key)]
    if missing_auth:
        raise ValueError(f"Missing required authentication configuration: {missing_auth}")
    
    # Validate email config
    email_config = config.get("email", {})
    required_email = ["smtp_server", "username", "password", "from_email", "to_emails"]
    missing_email = [key for key in required_email if not email_config.get(key)]
    if missing_email:
        raise ValueError(f"Missing required email configuration: {missing_email}")
    
    # Validate email addresses format (basic validation)
    to_emails = email_config.get("to_emails", [])
    if not isinstance(to_emails, list) or not to_emails:
        raise ValueError("to_emails must be a non-empty list")


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        validate_config(config)
        return config
    except FileNotFoundError:
        error_msg = f"Config file '{config_path}' not found"
        print(f"Error: {error_msg}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in config file: {e}"
        print(f"Error: {error_msg}")
        sys.exit(1)
    except ValueError as e:
        error_msg = f"Configuration validation failed: {e}"
        print(f"Error: {error_msg}")
        sys.exit(1)


def authenticate_rhino(config: Dict[str, Any]) -> str:
    """Get a valid access token, using cache when possible."""
    return _token_cache.get_valid_token(config)


def authenticate_rhino_impl(config: Dict[str, Any]) -> str:
    """Authenticate with Rhino Health API and return access token."""
    rhino_auth = config.get("rhino_auth", {})
    username = rhino_auth.get("username")
    password = rhino_auth.get("password")
    
    # Get configurable base URL
    base_url = config.get("api_base_url", "https://prod.rhinohealth.com")
    auth_url = f"{base_url}/api/v1/auth/obtain_token"
    
    auth_data = {
        "email": username,
        "password": password
    }
    
    try:
        response = requests.post(auth_url, data=auth_data, timeout=30)
        response.raise_for_status()
        
        auth_response = response.json()
        
        if "access" in auth_response:
            return auth_response["access"]
        else:
            errors = auth_response.get("errors", [])
            error_message = errors[0].get("message", None) if errors else None
            if error_message:
                raise Exception(f"Failed to authenticate: {error_message}")
            else:
                raise Exception(f"Authentication failed: {auth_response}")
                
    except requests.exceptions.HTTPError as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                raise Exception("Authentication failed: Invalid credentials")
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e}")
        else:
            raise Exception(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {e}")
    except Exception as e:
        raise Exception(f"Authentication failed: {e}")


def check_agent_health(agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Query the Rhino Health API for agent health status."""
    access_token = authenticate_rhino(config)
    
    # Get configurable base URL
    base_url = config.get("api_base_url", "https://prod.rhinohealth.com")
    url = f"{base_url}/api/v1/agents/{agent_id}/health_check?sync=true"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        health_data = response.json()
        
        # Validate response structure
        if not isinstance(health_data, dict):
            raise ValueError("Invalid response format: expected JSON object")
            
        return health_data
        
    except requests.exceptions.HTTPError as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                raise Exception("API authentication failed: Token may be expired")
            elif e.response.status_code == 404:
                raise Exception(f"Agent '{agent_id}' not found")
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e}")
        else:
            raise Exception(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {e}")
    except Exception as e:
        raise Exception(f"Health check failed: {e}")


def send_email_alert(config: Dict[str, Any], agent_id: str, status: str, full_response: Dict[str, Any], error_message: str = None):
    """Send email alert for non-completed status or errors."""
    email_config = config.get("email", {})
    
    smtp_server = email_config.get("smtp_server")
    smtp_port = email_config.get("smtp_port", 587)
    username = email_config.get("username")
    password = email_config.get("password")
    from_email = email_config.get("from_email")
    to_emails = email_config.get("to_emails", [])
    
    if not all([smtp_server, username, password, from_email, to_emails]):
        print("Error: Incomplete email configuration")
        return
    
    if error_message:
        subject = f"Rhino Health Agent Error - Agent {agent_id}"
        body = f"""
Error: Rhino Health Agent Health Check Failed

Agent ID: {agent_id}
Error: {error_message}

Please investigate the issue.
        """.strip()
    else:
        subject = f"Rhino Health Agent Alert - Agent {agent_id} Status: {status}"
        body = f"""
Alert: Rhino Health Agent Health Check Failed

Agent ID: {agent_id}
Status: {status}
Expected Status: {AgentStatus.COMPLETED}

Full Response:
{json.dumps(full_response, indent=2)}

Please investigate the agent status.
        """.strip()
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        print(f"Alert email sent for agent {agent_id}")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    parser = argparse.ArgumentParser(description="Check Rhino Health agent status")
    parser.add_argument("agent_id", help="Agent ID to check")
    parser.add_argument("-c", "--config", default="config.json", 
                       help="Path to config file (default: config.json)")
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        response = check_agent_health(args.agent_id, config)
        
        # Extract status with safe navigation
        data = response.get("data", {})
        if not isinstance(data, dict):
            status = AgentStatus.UNKNOWN
        else:
            status = data.get("status", AgentStatus.UNKNOWN)
        
        print(f"Agent {args.agent_id} status: {status}")
        
        # Send alert if status is not "Completed"
        if status != AgentStatus.COMPLETED:
            print(f"Status is not '{AgentStatus.COMPLETED}', sending email alert...")
            send_email_alert(config, args.agent_id, status, response)
        else:
            print(f"Status is '{AgentStatus.COMPLETED}', no alert needed")
            # Safe extraction of version info
            task_output = data.get("task_output", {}) if isinstance(data, dict) else {}
            version = task_output.get("version", AgentStatus.UNKNOWN) if isinstance(task_output, dict) else AgentStatus.UNKNOWN
            print(f"Agent version: {version}")
    
    except Exception as e:
        # Improved error handling - avoid bare except
        error_msg = f"Script error: {e}"
        print(f"Error: {error_msg}")
        
        # Try to send error notification if possible
        try:
            config = load_config(args.config)
            send_email_alert(config, args.agent_id, ErrorTypes.SCRIPT_ERROR, {}, error_msg)
        except Exception as email_error:
            print(f"Failed to send error notification email: {email_error}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
