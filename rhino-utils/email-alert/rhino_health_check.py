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
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        error_msg = f"Config file '{config_path}' not found"
        print(f"Error: {error_msg}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in config file: {e}"
        print(f"Error: {error_msg}")
        sys.exit(1)


def authenticate_rhino(config: Dict[str, Any]) -> str:
    """Authenticate with Rhino Health API using SDK method and return access token."""
    rhino_auth = config.get("rhino_auth", {})
    username = rhino_auth.get("username")  # Should be email
    password = rhino_auth.get("password")
    
    if not username or not password:
        error_msg = "Rhino authentication credentials not found in config.json"
        print(f"Error: {error_msg}")
        raise ValueError(error_msg)
    
    try:
        # Use the obtain_token endpoint as documented in swagger
        base_url = "https://prod.rhinohealth.com"
        auth_url = f"{base_url}/api/v1/auth/obtain_token"
        
        auth_data = {
            "email": username,  # SDK uses 'email' not 'username'
            "password": password
        }
        
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
        if e.response.status_code == 401:
            error_msg = "Authentication failed: Invalid credentials"
        else:
            error_msg = f"Rhino API authentication failed: {e}"
        print(f"Error: {error_msg}")
        raise
    except Exception as e:
        error_msg = f"Rhino API authentication failed: {e}"
        print(f"Error: {error_msg}")
        raise


def check_agent_health(agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Query the Rhino Health API for agent health status."""
    try:
        access_token = authenticate_rhino(config)
        
        # Make the API call with Bearer authentication (same as SDK)
        url = f"https://prod.rhinohealth.com/api/v1/agents/{agent_id}/health_check?sync=true"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        error_msg = f"Error querying API: {e}"
        if "401" in str(e) or "Unauthorized" in str(e):
            error_msg += " - Please check your Rhino Health credentials in config.json"
        print(error_msg)
        send_email_alert(config, agent_id, "API_ERROR", {}, error_msg)
        sys.exit(1)


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
Expected Status: Completed

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
        # Load configuration
        config = load_config(args.config)
        
        # Check agent health
        response = check_agent_health(args.agent_id, config)
        
        # Extract status
        status = response.get("data", {}).get("status", "Unknown")
        
        print(f"Agent {args.agent_id} status: {status}")
        
        # Send alert if status is not "Completed"
        if status != "Completed":
            print(f"Status is not 'Completed', sending email alert...")
            send_email_alert(config, args.agent_id, status, response)
        else:
            print("Status is 'Completed', no alert needed")
            version = response.get("data", {}).get("task_output", {}).get("version", "Unknown")
            print(f"Agent version: {version}")
    
    except Exception as e:
        # Fallback error handling - try to send email if config is available
        try:
            config = load_config(args.config)
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            send_email_alert(config, args.agent_id, "SCRIPT_ERROR", {}, error_msg)
        except:
            print(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
