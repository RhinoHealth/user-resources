project_id                      = ""
region                          = "us-central1"
zone                            = "us-central1-c"
bucket_name_output_and_logs     = ""
bucket_name_cancercenter_data   = ""
vpc_network_name                = "confidential-vpc"
subnet_name                     = "confidential-subnet"
subnet_ip_cidr_range            = "10.0.0.0/20"
vm_instance_name                = "confidential-vm"
vm_machine_type                 = "n2d-standard-2"
vm_image                        = "ubuntu-os-cloud/ubuntu-2204-lts"

# Rhino Specific Information
rhino_orechestrator_ip_range    = ["0.0.0.0/0"] # Rhino to provide list of IPs in the future
rhino_agent_id                  = ""
rhino_package_registry_user     = ""
rhino_package_registry_password = ""