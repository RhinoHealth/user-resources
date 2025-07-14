location                           = "East US"

# Naming Convention Variables
workgroup_name                     = "workgroup"
environment                        = "prod"
sequence_number                    = "1"

# Network Configuration
vnet_address_space                 = "10.0.0.0/16"
subnet_address_prefix              = "10.0.0.0/20"
vm_size                           = "Standard_B2s"

# Rhino Specific Information
rhino_orchestrator_ip_range        = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future
rhino_agent_id                     = ""

# Disk size configuration (in GB)
boot_disk_size_gb                  = 250
secondary_disk_size_gb             = 2048 