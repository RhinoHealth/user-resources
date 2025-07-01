#!/bin/bash

set -e

# Variables passed from Terraform
STORAGE_ACCOUNT_NAME="${storage_account_name}"
SHARE_NAME="${share_name}"
MOUNT_POINT="${mount_point}"
MOUNT_OPTIONS="${mount_options}"
MAKE_PERSISTENT="${make_persistent}"

echo "=== Azure Files Setup Script ==="

# Step 1: Install Azure CLI first and ensure it's in PATH
echo "Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Ensure Azure CLI is in PATH for this session
export PATH="/usr/bin:/usr/local/bin:$PATH"

# Verify Azure CLI installation
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI installation failed or not in PATH"
    echo "Checking possible locations..."
    find /usr -name "az" 2>/dev/null || echo "az command not found anywhere"
    exit 1
else
    echo "✅ Azure CLI installed successfully"
    az version --output table
fi

# Step 2: Install other required packages
echo "Installing required packages..."
sudo apt-get update -y
sudo apt-get install -y cifs-utils jq dnsutils

# Step 3: Create mount point
echo "Creating mount point: $MOUNT_POINT"
sudo mkdir -p "$MOUNT_POINT"

# Step 4: Enhanced DNS resolution testing
echo "Testing DNS resolution with enhanced retry logic..."
STORAGE_FQDN="$STORAGE_ACCOUNT_NAME.file.core.windows.net"
DNS_RESOLVED=false

echo "Target FQDN: $STORAGE_FQDN"
echo "Looking for private IP resolution (10.0.x.x range)"

for i in {1..20}; do
    echo "DNS resolution attempt $i/20..."
    
    # Try nslookup first
    NSLOOKUP_RESULT=$(nslookup "$STORAGE_FQDN" 2>/dev/null || echo "failed")
    if echo "$NSLOOKUP_RESULT" | grep -q "10\.0\."; then
        RESOLVED_IP=$(echo "$NSLOOKUP_RESULT" | grep "Address:" | tail -1 | awk '{print $2}')
        echo "✅ DNS resolved via nslookup to private IP: $RESOLVED_IP"
        DNS_RESOLVED=true
        break
    fi
    
    # Try dig as alternative
    DIG_RESULT=$(dig +short "$STORAGE_FQDN" 2>/dev/null || echo "failed")
    if echo "$DIG_RESULT" | grep -q "^10\.0\."; then
        echo "✅ DNS resolved via dig to private IP: $DIG_RESULT"
        DNS_RESOLVED=true
        break
    fi
    
    # Try host command as third option
    HOST_RESULT=$(host "$STORAGE_FQDN" 2>/dev/null || echo "failed")
    if echo "$HOST_RESULT" | grep -q "10\.0\."; then
        RESOLVED_IP=$(echo "$HOST_RESULT" | grep "has address" | awk '{print $4}')
        echo "✅ DNS resolved via host to private IP: $RESOLVED_IP"
        DNS_RESOLVED=true
        break
    fi
    
    # Show what we're getting instead
    echo "❌ DNS not yet resolved to private IP. Current resolution:"
    echo "   nslookup: $(echo "$NSLOOKUP_RESULT" | grep "Address:" | tail -1 || echo "no result")"
    echo "   dig: $DIG_RESULT"
    
    if [ $i -le 15 ]; then
        echo "   Waiting 30 seconds before retry..."
        sleep 30
    else
        echo "   Waiting 60 seconds before retry (final attempts)..."
        sleep 60
    fi
done

if [ "$DNS_RESOLVED" = false ]; then
    echo "⚠️  WARNING: DNS still not resolving to private IP after 20 attempts"
    echo "   This may cause mount issues, but continuing..."
    echo "   Final DNS resolution:"
    nslookup "$STORAGE_FQDN" || echo "   DNS lookup completely failed"
fi

# Step 5: Test connectivity to storage endpoint
echo "Testing connectivity to storage endpoint..."
if timeout 10 nc -zv "$STORAGE_FQDN" 445 2>/dev/null; then
    echo "✅ Port 445 connectivity successful"
else
    echo "❌ Port 445 connectivity failed - this may indicate network issues"
fi

# Step 6: Login using managed identity
echo "Authenticating with managed identity..."
# Verify az command is available before using it
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not available - installation may have failed"
    exit 1
fi

az login --identity

# Step 7: Try to get storage account key with robust retry logic
echo "Retrieving storage account key using managed identity..."
STORAGE_KEY=""

# Method 1: Try with resource group specified
for i in {1..5}; do
    echo "Attempt $i: Trying to get storage key with resource group..."
    STORAGE_KEY=$(az storage account keys list \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --resource-group "$(curl -s -H "Metadata: true" "http://169.254.169.254/metadata/instance/compute/resourceGroupName?api-version=2021-02-01&format=text")" \
        --query '[0].value' \
        --output tsv 2>/dev/null || echo "")
    
    if [ ! -z "$STORAGE_KEY" ] && [ "$STORAGE_KEY" != "null" ]; then
        echo "✅ Successfully retrieved storage key using resource group method"
        break
    fi
    
    echo "❌ Resource group method failed, waiting 30 seconds..."
    sleep 30
done

# Method 2: Try without resource group if Method 1 failed
if [ -z "$STORAGE_KEY" ] || [ "$STORAGE_KEY" = "null" ]; then
    echo "Trying without resource group specification..."
    for i in {1..5}; do
        echo "Attempt $i: Trying to get storage key without resource group..."
        STORAGE_KEY=$(az storage account keys list \
            --account-name "$STORAGE_ACCOUNT_NAME" \
            --query '[0].value' \
            --output tsv 2>/dev/null || echo "")
        
        if [ ! -z "$STORAGE_KEY" ] && [ "$STORAGE_KEY" != "null" ]; then
            echo "✅ Successfully retrieved storage key without resource group"
            break
        fi
        
        echo "❌ Method 2 failed, waiting 30 seconds..."
        sleep 30
    done
fi

# Method 3: Try REST API approach if Azure CLI fails
if [ -z "$STORAGE_KEY" ] || [ "$STORAGE_KEY" = "null" ]; then
    echo "Azure CLI methods failed, trying REST API..."
    
    # Get access token
    ACCESS_TOKEN=$(curl -s -H "Metadata: true" \
        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" \
        | jq -r '.access_token')
    
    if [ ! -z "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "null" ]; then
        RG_NAME=$(curl -s -H "Metadata: true" "http://169.254.169.254/metadata/instance/compute/resourceGroupName?api-version=2021-02-01&format=text")
        SUB_ID=$(curl -s -H "Metadata: true" "http://169.254.169.254/metadata/instance/compute/subscriptionId?api-version=2021-02-01&format=text")
        
        echo "Trying REST API to get storage key..."
        STORAGE_KEY=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
            "https://management.azure.com/subscriptions/$SUB_ID/resourceGroups/$RG_NAME/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME/listKeys?api-version=2021-04-01" \
            | jq -r '.keys[0].value' 2>/dev/null || echo "")
        
        if [ ! -z "$STORAGE_KEY" ] && [ "$STORAGE_KEY" != "null" ]; then
            echo "✅ Successfully retrieved storage key via REST API"
        fi
    fi
fi

# Final check
if [ -z "$STORAGE_KEY" ] || [ "$STORAGE_KEY" = "null" ]; then
    echo "❌ ERROR: All methods to retrieve storage account key failed"
    echo "This suggests RBAC permissions may not be properly configured"
    echo "Manual intervention required - please check:"
    echo "1. VM managed identity has 'Storage Account Key Operator Service Role'"
    echo "2. Role assignment has propagated (can take 5-10 minutes)"
    echo "3. Storage account exists and is accessible"
    exit 1
fi

echo "✅ Successfully retrieved storage account key"

# Step 8: Create credentials file
echo "Creating credentials file..."
sudo bash -c "cat > /etc/azure-files-credentials <<EOF
username=$STORAGE_ACCOUNT_NAME
password=$STORAGE_KEY
EOF"
sudo chmod 600 /etc/azure-files-credentials

# Step 9: Mount the share
echo "Mounting Azure Files share..."
UNC_PATH="//$STORAGE_FQDN/$SHARE_NAME"
echo "Mount command: sudo mount -t cifs '$UNC_PATH' '$MOUNT_POINT' -o '$MOUNT_OPTIONS'"

if sudo mount -t cifs "$UNC_PATH" "$MOUNT_POINT" -o "$MOUNT_OPTIONS"; then
    echo "✅ Mount successful"
else
    echo "❌ Mount failed, additional diagnostics:"
    echo "   DNS resolution check:"
    nslookup "$STORAGE_FQDN" || echo "   DNS lookup failed"
    echo "   Connectivity check:"
    nc -zv "$STORAGE_FQDN" 445 || echo "   Port 445 connectivity failed"
    echo "   Mount options used: $MOUNT_OPTIONS"
    exit 1
fi

# Step 10: Verify and set permissions
if mountpoint -q "$MOUNT_POINT"; then
    echo "✅ SUCCESS: Azure Files share mounted at $MOUNT_POINT"
    sudo chown -R $(whoami):$(whoami) "$MOUNT_POINT" 2>/dev/null || true
    echo "Mount details:"
    ls -la "$MOUNT_POINT"
    mount | grep "$MOUNT_POINT"
else
    echo "❌ ERROR: Mount verification failed"
    exit 1
fi

# Step 11: Make persistent if requested
if [ "$MAKE_PERSISTENT" = "true" ]; then
    echo "Adding to /etc/fstab for persistent mounting..."
    FSTAB_ENTRY="$UNC_PATH $MOUNT_POINT cifs $MOUNT_OPTIONS 0 0"
    
    if ! grep -q "$UNC_PATH" /etc/fstab 2>/dev/null; then
        echo "$FSTAB_ENTRY" | sudo tee -a /etc/fstab
        echo "✅ Added to /etc/fstab: $FSTAB_ENTRY"
    else
        echo "ℹ️  Entry already exists in /etc/fstab"
    fi
fi

echo "🎉 === Azure Files setup completed successfully ==="