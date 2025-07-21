# Defines the providers and versions used in the Terraform configuration for Amazon Web Services (AWS).
terraform {
#  backend "s3" {
#    bucket  = "<YOUR_BUCKET_NAME>"
#    key     = "<YOUR_STATE_FILE_KEY>"
#    region  = "<YOUR_BUCKET_REGION>"
#  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Pin to a specific version or range
    }
  }

  required_version = ">= 1.0"
}

# Defines the AWS provider and sets the default region for all resources.
provider "aws" {
  region = var.aws_region
} 