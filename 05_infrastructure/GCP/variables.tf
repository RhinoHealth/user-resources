# --- Variables ---------------------------------------------------------------------------------------------------------------
# --- General Project Variables ---
variable "project_id" {
  description = "The unique identifier for your Google Cloud project."
  type        = string
}
variable "region" {
  description = "The Google Cloud region where resources will be deployed (e.g., 'us-central1')."
  type        = string
}
variable "zone" {
  description = "The specific zone within the Google Cloud region to deploy zonal resources like the VM (e.g., 'us-central1-c')."
  type        = string
}

# --- Naming Convention Variables ---
variable "workgroup_name" {
  description = "The workgroup name for resource naming convention (e.g., 'example-workgroup')."
  type        = string
}
variable "environment" {
  description = "The environment for resource naming convention (e.g., 'prod', 'dev', 'test')."
  type        = string
}
variable "sequence_number" {
  description = "The sequence number for resource naming convention (e.g., '1', '2')."
  type        = string
  default     = "1"
}

# --- Network Variables ---
variable "rhino_orchestrator_ip_range" {
  description = "A list of IP ranges in CIDR notation allowed for egress traffic to the Rhino orchestrator."
  type        = list(string)
}
variable "subnet_ip_cidr_range" {
  description = "The internal IP address range for the subnet in CIDR notation (e.g., '10.0.0.0/20')."
  type        = string
}

# --- VM Variables ---
variable "vm_image" {
  description = "The source image for the VM's boot disk (e.g., 'ubuntu-os-cloud/ubuntu-2204-lts')."
  type        = string
}
variable "vm_machine_type" {
  description = "The machine type for the VM, which must support Confidential Computing (e.g., 'n2d-standard-2')."
  type        = string
}

# --- VM & Script Variables ---
variable "rhino_agent_id" {
  description = "The agent ID for the Rhino Health installation."
  type        = string
  sensitive   = true
}

variable "rhino_package_registry_user" {
  description = "The user for the Rhino Health package registry."
  type        = string
  sensitive   = true
}

variable "rhino_package_registry_password" {
  description = "The password for the Rhino Health package registry."
  type        = string
  sensitive   = true
}

# --- Disk Size Variables ---
variable "boot_disk_size_gb" {
  description = "The size of the VM's boot disk in GB."
  type        = number
}

variable "secondary_disk_size_gb" {
  description = "The size of the secondary persistent disk in GB."
  type        = number
}
