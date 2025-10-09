variable "account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "terraform_role_name" {
  description = "Name of the existing Terraform management role"
  type        = string
}

variable "edge_node_vpc" {
  type        = string
  description = "VPC ID"
}

variable "workgroup_name" {
  description = "The workgroup name for resource naming convention (e.g., 'example-workgroup')."
  type        = string
}

variable "sequence_number" {
  description = "The sequence number for resource naming convention (e.g., '1', '2')."
  type        = string
  default     = "1"
}

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

variable "vm_machine_type" {
  description = "The instance type for the EC2 instance (e.g., 't3.medium')."
  type        = string
}

variable "vm_image" {
  description = "The AMI ID or name for the EC2 instance (e.g., 'ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*')."
  type        = string
}

variable "rhino_agent_id" {
  description = "The agent ID for the Rhino Health installation."
  type        = string
}

# Sensitive Variables
variable "rhino_enroll_secret" {
  description = "The Fleet Enrollment Secret"
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

variable "boot_disk_size_gb" {
  description = "The size of the EC2 instance's boot disk in GB."
  type        = number
}

variable "secondary_disk_size_gb" {
  description = "The size of the secondary EBS volume in GB."
  type        = number
}

variable "aws_region" {
  description = "The AWS region where resources will be deployed (e.g., 'us-east-1')."
  type        = string
}

variable "availability_zone" {
  description = "The specific availability zone within the AWS region to deploy zonal resources like the EC2 instance (e.g., 'us-east-1a')."
  type        = string
}

variable "lza_s3_kms" {
  description = "ID of existing KMS"
  type        = string
}

variable "edge_node_private_subnet" {
  description = "Private subnet ID"
  type        = string
}

variable "session_key" {
  description = "KMS Session key"
  type        = string
}

variable "ebs_key" {
  description = "EBS Key"
  type        = string
}

variable "accel_kms" {
  description = "Accelerator Key"
  type        = string
}

# Log Delivery

variable "destination_bucket_name" {
  description = "Name of the S3 bucket that delivers logs to Cribl"
  type        = string
}

variable "s3_prefix" {
  description = "S3 prefix (subfolder path) where logs will be stored for CAIA."
  type        = string
  default     = "caia/"

  validation {
    condition     = var.s3_prefix == "" || can(regex("/$", var.s3_prefix))
    error_message = "The s3_prefix must end with '/' if specified."
  }
}

variable "log_group_name" {
  description = "Name of the CloudWatch Log Group"
  type        = string
}

variable "log_retention_days" {
  description = "Number of days to retain logs in CloudWatch"
  type        = number
  default     = 30
}

variable "log_filter_pattern" {
  description = "Filter pattern for log subscription"
  type        = string
  default     = ""
}

variable "log_delivery_role_name" {
  description = "Name of the IAM role for log delivery"
  type        = string
}

variable "firehose_delivery_stream_name" {
  description = "Name of the Kinesis Data Firehose delivery stream"
  type        = string
}

variable "destination_account_id" {
  description = "AWS Account ID of the destination account (where S3 bucket is)"
  type        = string
}

# Capacity reservation

variable "capacity_block_reservation" {
  description = "ID of the EC2 capacity block reservation"
  type        = string
}