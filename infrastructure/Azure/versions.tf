# Defines the providers and versions used in the Terraform configuration for Microsoft Azure.
terraform {
#  backend "azurerm" {
#    resource_group_name  = "<YOUR_RESOURCE_GROUP_NAME>"
#    storage_account_name = "<YOUR_STORAGE_ACCOUNT_NAME>"
#    container_name       = "<YOUR_CONTAINER_NAME>"
#    key                  = "<YOUR_STATE_FILE_KEY>"
#  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Pin to a specific version or range
    }
  }

  required_version = ">= 1.0"
}

# Defines the Azure provider and sets the default location for all resources.
provider "azurerm" {
  features {}
} 