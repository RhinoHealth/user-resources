# --- Variables ---------------------------------------------------------------------------------------------------------------
# --- General Project Variables ---
variable "aws_region" {
  description = "The AWS region where resources will be deployed (e.g., 'us-east-1')."
  type        = string
}

variable "availability_zone" {
  description = "The specific availability zone within the AWS region to deploy zonal resources like the EC2 instance (e.g., 'us-east-1a')."
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
variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC (e.g., '10.0.0.0/16')."
  type        = string
}

variable "public_subnet_cidr_block" {
  description = "The CIDR block for the public subnet where NAT Gateway will be deployed (e.g., '10.0.1.0/24')."
  type        = string
}

variable "private_subnet_cidr_block" {
  description = "The CIDR block for the private subnet where EC2 instances will be deployed (e.g., '10.0.2.0/24')."
  type        = string
}

variable "rhino_orchestrator_ip_range" {
  description = "A list of IP ranges in CIDR notation allowed for egress traffic to the Rhino orchestrator."
  type        = list(string)
}

# --- VM Variables ---
variable "vm_machine_type" {
  description = "The instance type for the EC2 instance (e.g., 't3.medium')."
  type        = string
}

variable "ubuntu_version" {
  description = "The Ubuntu version to use for the EC2 instance. Supported versions: 20.04 (Focal), 22.04 (Jammy), 24.04 (Noble)."
  type        = string
}

# --- Rhino Configuration Variables ---
variable "rhino_agent_id" {
  description = "The agent ID for the Rhino Health installation."
  type        = string
}

# --- Sensitive Variables ---
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
  description = "The size of the EC2 instance's boot disk in GB."
  type        = number
}

variable "secondary_disk_size_gb" {
  description = "The size of the secondary EBS volume in GB."
  type        = number
}
