project_id = ""
region     = "us-central1"
zone       = "us-central1-c"

# Naming Convention Variables
workgroup_name  = "workgroup"
environment     = "prod"
sequence_number = "1"

# Network Configuration
subnet_ip_cidr_range = "10.0.0.0/20"

# VM Configuration
vm_machine_type = "n2d-standard-2"
vm_image        = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"

# Rhino Specific Information
rhino_orchestrator_ip_range = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future

# Disk size configuration (in GB)
boot_disk_size_gb      = 250
secondary_disk_size_gb = 2048
