# Defines the providers and versions used in the Terraform configuration for Google Cloud Platform (GCP).
terraform {
#  backend "gcs" {
#    bucket  = "<YOUR_BUCKET_NAME>"
#    prefix  = "<YOUR_STATE_FILE_PREFIX>"
#  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.4" # Pin to a specific version or range
    }
  }
}

# Defines the Google Cloud provider and sets the default project, region, and zone for all resources.
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
