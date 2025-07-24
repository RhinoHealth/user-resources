# --- Key Vault Variables ---
variable "tenant_id" {
  description = "The Azure Active Directory tenant ID for Key Vault."
  type        = string
}

variable "subscription_id" {
  description = "The Azure subscription ID where resources will be deployed."
  type        = string

}

# --- Variables ---------------------------------------------------------------------------------------------------------------
# --- General Project Variables ---
variable "location" {
  description = "The Azure region where resources will be deployed (e.g., 'East US')."
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
variable "vnet_address_space" {
  description = "The address space for the Virtual Network (e.g., '10.0.0.0/16')."
  type        = string
}

variable "subnet_address_prefix" {
  description = "The address prefix for the subnet (e.g., '10.0.0.0/20')."
  type        = string
}

variable "rhino_orchestrator_ip_range" {
  description = "A list of IP ranges in CIDR notation allowed for egress traffic to the Rhino orchestrator."
  type        = list(string)
}

variable "ssh_source_ip_range" {
  description = "A list of IP ranges in CIDR notation allowed to SSH (port 22) to the VM."
  type        = list(string)
  default     = ["*"] # Allow from anywhere by default; restrict for better security
}

variable "vm_ip_type" {
  description = <<EOT
Type of VM IP assignment for the VM network interface:
  - "public": Assign a public IP to the VM (default)
  - "nat":    No public IP assigned to the VM (use NAT Gateway for outbound only)
Note: You cannot use both at the same time. If 'nat' is selected, the VM will not have a public IP.
EOT
  type        = string
  default     = "nat"
  validation {
    condition     = contains(["public", "nat"], var.vm_ip_type)
    error_message = "vm_ip_type must be either 'public' or 'nat'."
  }
}

# --- VM Variables ---
variable "vm_size" {
  description = "The size of the Virtual Machine (e.g., 'Standard_B2s')."
  type        = string
}

variable "vm_image" {
  description = "The image reference for the Virtual Machine (e.g., 'ubuntu-24_04-lts')."
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
  description = "The size of the secondary managed disk in GB."
  type        = number
}
