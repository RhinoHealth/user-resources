terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }    
  }
}

# default provider - application subscription
provider "azurerm" {
  features {}
  subscription_id = var.application_subscription_id
}

# landing zone provider - for existing shared infrastructure
provider "azurerm" {
  alias   = "landing_zone"
  features {
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
  subscription_id = var.landing_zone_subscription_id
}

provider "random" {  
}

provider "time" {  
}