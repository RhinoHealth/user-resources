#!/bin/bash

# Exit on any error
set -e

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a /var/log/rhino/user-data.log
}

# Create log directory
mkdir -p /var/log/rhino

log "Starting user data script execution"

# Update system packages
log "Updating system packages"
apt-get update
apt-get upgrade -y

# Install required packages
log "Installing required packages"
apt-get install -y curl wget unzip

# Ensure SSM agent is installed and up to date via snap (default on Ubuntu 20.04+)
log "Ensuring SSM agent is installed and up to date via snap"
if snap list amazon-ssm-agent >/dev/null 2>&1; then
    log "SSM agent already installed via snap, refreshing..."
    snap refresh amazon-ssm-agent
else
    log "SSM agent not found via snap, installing..."
    snap install amazon-ssm-agent --classic
fi
systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent
systemctl start snap.amazon-ssm-agent.amazon-ssm-agent

# Install Rhino Health agent
log "Installing Rhino Health agent"
curl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='${rhino_agent_id}' PACKAGE_REGISTRY_USER='${rhino_package_registry_user}' PACKAGE_REGISTRY_PASSWORD='${rhino_package_registry_password}' SKIP_HW_CHECK=True bash -

# Mount the secondary EBS volume
log "Setting up secondary EBS volume"
# Wait for the volume to be available
sleep 10

# Check if the volume is attached
if [ -e /dev/sdf ]; then
    log "Secondary volume found at /dev/sdf"
    
    # Create filesystem if it doesn't exist
    if ! blkid /dev/sdf; then
        log "Creating filesystem on secondary volume"
        mkfs.ext4 /dev/sdf
    else
        log "Filesystem already exists on secondary volume"
    fi
    
    # Create mount point
    mkdir -p /mnt/data
    
    # Add to fstab for persistence
    if ! grep -q "/dev/sdf" /etc/fstab; then
        echo "/dev/sdf /mnt/data ext4 defaults,nofail 0 2" >> /etc/fstab
        log "Added secondary volume to fstab"
    fi
    
    # Mount the volume
    mount /mnt/data
    log "Secondary volume mounted successfully"
else
    log "WARNING: Secondary volume not found at /dev/sdf"
fi

# Create log directory
mkdir -p /var/log/rhino

# Set up log rotation
cat > /etc/logrotate.d/rhino << EOF
/var/log/rhino/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# Configure system for better security
log "Configuring system security settings"

# Disable password authentication for SSH
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH service
systemctl restart ssh

# Set up CloudWatch agent for system metrics
log "Setting up CloudWatch agent"
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# Create CloudWatch agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/bin/config.json << EOF
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/rhino/*.log",
                        "log_group_name": "/aws/ec2/${vm_instance_name}",
                        "log_stream_name": "rhino-application",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/syslog",
                        "log_group_name": "/aws/ec2/${vm_instance_name}",
                        "log_stream_name": "rhino-system",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent

# Log the completion
log "User data script completed successfully"
