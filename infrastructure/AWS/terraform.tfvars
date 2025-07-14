aws_region                        = "us-east-1"
availability_zone                 = "us-east-1a"

# Naming Convention Variables
workgroup_name                    = "workgroup"
environment                       = "prod"
sequence_number                   = "1"

# Network Configuration
vpc_cidr_block                    = "10.0.0.0/16"
subnet_cidr_block                 = "10.0.0.0/20"
vm_machine_type                   = "t3.medium"
vm_image                          = "ami-0c02fb55956c7d316" # Ubuntu 22.04 LTS in us-east-1

# Rhino Specific Information
rhino_orchestrator_ip_range       = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future
rhino_agent_id                    = ""

# Disk size configuration (in GB)
boot_disk_size_gb                 = 250
secondary_disk_size_gb            = 2048 