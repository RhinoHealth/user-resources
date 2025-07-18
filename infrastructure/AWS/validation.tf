# --- Data Validation ---------------------------------------------------------------------------------------------------------------
# Data sources and validation rules for the Terraform configuration

# Validate AWS region
data "aws_region" "current" {}

# Validate availability zone
data "aws_availability_zone" "selected" {
  name = var.availability_zone
}

# Validate AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["*ubuntu*${var.ubuntu_version}*amd64*server*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# Validate VPC CIDR block
locals {
  vpc_cidr_validation       = can(cidrhost(var.vpc_cidr_block, 0))
  public_subnet_validation  = can(cidrhost(var.public_subnet_cidr_block, 0))
  private_subnet_validation = can(cidrhost(var.private_subnet_cidr_block, 0))

  # Validate that subnets are within VPC CIDR
  public_subnet_in_vpc  = can(cidrsubnet(var.vpc_cidr_block, 8, 1))
  private_subnet_in_vpc = can(cidrsubnet(var.vpc_cidr_block, 8, 2))

  # Validate that the Ubuntu version is supported
  ubuntu_version_validation = contains(["22.04", "24.04"], var.ubuntu_version)
}

# Validation rules
resource "null_resource" "validation" {
  lifecycle {
    precondition {
      condition     = local.vpc_cidr_validation
      error_message = "Invalid VPC CIDR block: ${var.vpc_cidr_block}"
    }

    precondition {
      condition     = local.public_subnet_validation
      error_message = "Invalid public subnet CIDR block: ${var.public_subnet_cidr_block}"
    }

    precondition {
      condition     = local.private_subnet_validation
      error_message = "Invalid private subnet CIDR block: ${var.private_subnet_cidr_block}"
    }

    precondition {
      condition     = length(var.rhino_orchestrator_ip_range) > 0
      error_message = "At least one IP range must be specified for rhino_orchestrator_ip_range"
    }

    precondition {
      condition     = var.boot_disk_size_gb >= 20
      error_message = "Boot disk size must be at least 20 GB"
    }

    precondition {
      condition     = var.secondary_disk_size_gb >= 1
      error_message = "Secondary disk size must be at least 1 GB"
    }

    precondition {
      condition     = length(var.workgroup_name) > 0
      error_message = "Workgroup name cannot be empty"
    }

    precondition {
      condition     = contains(["dev", "test", "staging", "prod"], var.environment)
      error_message = "Environment must be one of: dev, test, staging, prod"
    }
    
    precondition {
      condition     = local.ubuntu_version_validation
      error_message = "Ubuntu version must be one of: 22.04, 24.04"
    }
  }
}
