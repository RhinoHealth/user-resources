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

# --- VM Variables ---
variable "vm_size" {
  description = "The size of the Virtual Machine (e.g., 'Standard_B2s')."
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