location        = "East US"
tenant_id       = "your-tenant-id"       # Replace with your actual tenant ID
subscription_id = "your-subscription-id" # Replace with your actual subscription ID

# Naming Convention Variables
workgroup_name  = "workgroup"
environment     = "prod"
sequence_number = "1"

# Network Configuration
vnet_address_space    = "10.0.0.0/16"
subnet_address_prefix = "10.0.0.0/20"
ssh_source_ip_range   = ["0.0.0.0/0"] # Allow from anywhere by default; restrict for better security
vm_ip_type            = "public"      # Options: "public", "nat"

# VM Configuration
vm_size  = "Standard_D4alds_v6"
vm_image = "ubuntu-24_04-lts"

# Rhino Specific Information
rhino_orchestrator_ip_range = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future

# Disk size configuration (in GB)
boot_disk_size_gb      = 250
secondary_disk_size_gb = 2048
