#!/bin/bash

# Update system packages
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y curl wget unzip

# Install Rhino Health agent
curl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='${rhino_agent_id}' PACKAGE_REGISTRY_USER='${rhino_package_registry_user}' PACKAGE_REGISTRY_PASSWORD='${rhino_package_registry_password}' SKIP_HW_CHECK=True bash -

# Mount the secondary EBS volume
# Wait for the volume to be available
sleep 10

# Check if the volume is attached
if [ -e /dev/sdf ]; then
    # Create filesystem if it doesn't exist
    if ! blkid /dev/sdf; then
        mkfs.ext4 /dev/sdf
    fi
    
    # Create mount point
    mkdir -p /mnt/data
    
    # Add to fstab for persistence
    echo "/dev/sdf /mnt/data ext4 defaults,nofail 0 2" >> /etc/fstab
    
    # Mount the volume
    mount /mnt/data
fi

# Create log directory
mkdir -p /var/log/rhino

# Log the completion
echo "$(date): User data script completed successfully" >> /var/log/rhino/user-data.log 