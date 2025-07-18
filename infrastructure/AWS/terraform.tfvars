aws_region                        = "us-east-1"
availability_zone                 = "us-east-1a"

# Naming Convention Variables
workgroup_name                    = "workgroup"
environment                       = "prod"
sequence_number                   = "1"

# Network Configuration
vpc_cidr_block                    = "10.0.0.0/16"
public_subnet_cidr_block          = "10.0.1.0/24"
private_subnet_cidr_block         = "10.0.2.0/24"
vm_machine_type                   = "t3.medium"
ubuntu_version                    = "24.04"

# Rhino Specific Information
rhino_orchestrator_ip_range       = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future
rhino_agent_id                    = ""

# Disk size configuration (in GB)
boot_disk_size_gb                 = 250
secondary_disk_size_gb            = 2048 
