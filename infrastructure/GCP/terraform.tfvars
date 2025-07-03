project_id                      = ""
region                          = "us-central1"
zone                            = "us-central1-c"

# Naming Convention Variables
workgroup_name                  = "example-workgroup"
environment                     = "prod"
sequence_number                 = "1"

# Legacy bucket variables (kept for backward compatibility but not used in new naming)
bucket_name_output_and_logs     = ""
bucket_name_cancercenter_data   = ""

# Network Configuration
subnet_ip_cidr_range            = "10.0.0.0/20"
vm_machine_type                 = "n2d-standard-2"
vm_image                        = "ubuntu-os-cloud/ubuntu-2204-lts"

# Rhino Specific Information
rhino_orechestrator_ip_range    = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future
rhino_agent_id                  = ""
rhino_package_registry_user     = ""
rhino_package_registry_password = ""