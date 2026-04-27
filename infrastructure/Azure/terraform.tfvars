location        = "North Central US"
tenant_id       = "02e2a2b7-0604-47c6-b2b2-0866ae5b7aac"       # Replace with your actual tenant ID
subscription_id = "44604625-113d-4bfc-94dc-608200f1dff0" # Replace with your actual subscription ID

# Naming Convention Variables
workgroup_name  = "bpontz-azure-test"
environment     = "dev"
sequence_number = "1"

# Network Configuration
vnet_address_space    = "10.0.0.0/16"
subnet_address_prefix = "10.0.0.0/20"
ssh_source_ip_range   = ["0.0.0.0/0"] # Allow from anywhere by default; restrict for better security
vm_ip_type            = "public"      # Options: "public", "nat"

# VM Configuration
vm_size  = "Standard_D4s_v3"
vm_image = "ubuntu-24_04-lts"

# Rhino Specific Information
rhino_orchestrator_ip_range = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future

# Disk size configuration (in GB)
boot_disk_size_gb      = 250
secondary_disk_size_gb = 2048
