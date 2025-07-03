# Copyright 2025 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Note:
# - This code should not be used in a production environment and should be treated as demonstration/example code 
# - You will need to enable Compute Engine API, IAM API, Cloud Logging API, and Cloud Resource Manager API

# Defines the Google Cloud provider and sets the default project, region, and zone for all resources.
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

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

# --- Storage Variables ---
variable "bucket_name_cancercenter_data" {
  description = "The globally unique name for the Cloud Storage bucket containing the source data from the cancer center."
  type        = string
}
variable "bucket_name_output_and_logs" {
  description = "The globally unique name for the Cloud Storage bucket that will store processed outputs and exported logs."
  type        = string
}

# --- Network Variables ---
variable "rhino_orechestrator_ip_range" {
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

# --- Local Values for Naming Convention ---
locals {
  # VPC Network: {workgroup name}-rhino-client-{environment}-vpc-{seq#}
  vpc_network_name = "${var.workgroup_name}-rhino-client-${var.environment}-vpc-${var.sequence_number}"
  
  # Subnet: {workgroup name}-rhino-client-{environment}-vpc-{seq#}-subnet-{seq#}
  subnet_name = "${var.workgroup_name}-rhino-client-${var.environment}-vpc-${var.sequence_number}-subnet-${var.sequence_number}"
  
  # VM: {workgroup name}-rhino-client-{environment}-{seq#}
  vm_instance_name = "${var.workgroup_name}-rhino-client-${var.environment}-${var.sequence_number}"
  
  # Firewall: {workgroup name}-rhino-client-{protocol}-{port}-{action}
  firewall_egress_name = "${var.workgroup_name}-rhino-client-tcp-443-allow"
  
  # Buckets: {workgroup name}-rhino-client-{type}-{seq#}
  bucket_output_logs_name = "${var.workgroup_name}-rhino-client-output-data-${var.sequence_number}"
  bucket_source_data_name = "${var.workgroup_name}-rhino-client-input-data-${var.sequence_number}"
  bucket_logs_name = "${var.workgroup_name}-rhino-client-log-${var.sequence_number}"
  
  # Standard tags for cost aggregation
  common_tags = {
    workgroup   = var.workgroup_name
    environment = var.environment
    purpose     = "rhino-client"
    managed_by  = "terraform"
  }
}

# --- Networking ------------------------------------------------------------------------------------------------------------------
# Creates a custom mode Virtual Private Cloud (VPC) network to provide an isolated environment.
resource "google_compute_network" "main" {
  project                       = var.project_id
  name                          = local.vpc_network_name
  auto_create_subnetworks       = false
  routing_mode                  = "REGIONAL"
  delete_default_routes_on_create = false
}

# Creates a subnet within the VPC, defining its IP range and enabling Private Google Access and Flow Logs.
resource "google_compute_subnetwork" "main" {
  project                  = var.project_id
  name                     = local.subnet_name
  ip_cidr_range            = var.subnet_ip_cidr_range
  region                   = var.region
  network                  = google_compute_network.main.self_link
  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# NOT RECOMMENDED TO USE FOR SECURITY REASONS
# Allows SSH traffic from any source IP address (highly discouraged for production).
# resource "google_compute_firewall" "allow_ssh" {
#   project       = var.project_id
#   name          = "${local.vpc_network_name}-allow-ssh"
#   network       = google_compute_network.main.name
#   description   = "Allows SSH access to instances."
#   source_ranges = ["0.0.0.0/0"]

#   allow {
#     protocol = "tcp"
#     ports    = ["22"]
#   }

#   log_config {
#     metadata = "INCLUDE_ALL_METADATA"
#   }
# }

# Allows outbound (egress) TCP traffic on port 443 to specified destination IPs.
resource "google_compute_firewall" "allow_egress_rhino" {
  project            = var.project_id
  name               = local.firewall_egress_name
  network            = google_compute_network.main.name
  description        = "Allows egress traffic to the Rhino orchestrator."
  destination_ranges = var.rhino_orechestrator_ip_range
  direction          = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Creates a Cloud Router, which is a prerequisite for using Cloud NAT.
resource "google_compute_router" "main" {
  project = var.project_id
  name    = "${local.vpc_network_name}-router"
  region  = var.region
  network = google_compute_network.main.self_link
}

# Configures Cloud NAT to allow VM instances with no public IPs to access the internet.
resource "google_compute_router_nat" "main" {
  project                            = var.project_id
  name                               = "${local.vpc_network_name}-nat"
  router                             = google_compute_router.main.name
  region                             = google_compute_router.main.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ALL"
  }
}

# --- Storage ------------------------------------------------------------------------------------------------------------------
# Creates the Cloud Storage bucket for storing outputs and logs.
resource "google_storage_bucket" "output_logs" {
  name                        = local.bucket_output_logs_name
  location                    = var.region
  storage_class               = "STANDARD"
  project                     = var.project_id
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
  
  labels = local.common_tags
}

# Creates the Cloud Storage bucket for storing the source cancer center data.
resource "google_storage_bucket" "source_data" {
  name                        = local.bucket_source_data_name
  location                    = var.region
  storage_class               = "STANDARD"
  project                     = var.project_id
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
  
  labels = local.common_tags
}

# Creates the Cloud Storage bucket for storing logs.
resource "google_storage_bucket" "logs" {
  name                        = local.bucket_logs_name
  location                    = var.region
  storage_class               = "STANDARD"
  project                     = var.project_id
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
  
  labels = local.common_tags
}

# --- IAM & Service Accounts ------------------------------------------------------------------------------------------------------------------
# Creates a dedicated service account for the Confidential Compute VM.
resource "google_service_account" "vm" {
  project      = var.project_id
  account_id   = "${var.workgroup_name}-rhino-client-${var.environment}-sa"
  display_name = "VM Storage Access Service Account"
}

# Defines a custom IAM role with fine-grained permissions for object management.
resource "google_project_iam_custom_role" "object_read_write_lister" {
  project     = var.project_id
  role_id     = "objectReadWriteLister"
  title       = "Object Read, Write, and Lister"
  description = "Allows reading, writing, and listing of GCS objects."
  permissions = [
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",
    "storage.objects.update"
  ]
}

# Grants the VM's service account read-only access to the source data bucket.
resource "google_storage_bucket_iam_member" "vm_ro_on_source_data" {
  bucket = google_storage_bucket.source_data.name
  role   = "roles/storage.objectViewer"
  member = google_service_account.vm.member
}

# Assigns the custom role to the VM's service account for the output and logs bucket.
resource "google_storage_bucket_iam_member" "vm_rw_on_output_logs" {
  bucket = google_storage_bucket.output_logs.name
  role   = google_project_iam_custom_role.object_read_write_lister.id
  member = google_service_account.vm.member
}

# --- Compute ------------------------------------------------------------------------------------------------------------------
# Creates a standard persistent disk (HDD) to be attached to the VM instance.
resource "google_compute_disk" "secondary" {
  project = var.project_id
  name    = "${local.vm_instance_name}-secondary-hdd"
  type    = "pd-standard"
  zone    = var.zone
  size    = 2048 # 2TB
  
  labels = local.common_tags
}

# Creates the Confidential Compute VM instance with specified hardware and software settings.
resource "google_compute_instance" "main" {
  project                   = var.project_id
  name                      = local.vm_instance_name
  machine_type              = var.vm_machine_type
  zone                      = var.zone
  allow_stopping_for_update = true

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  confidential_instance_config {
    enable_confidential_compute = true
  }

  service_account {
    email  = google_service_account.vm.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = 250
      type  = "pd-ssd"
    }
  }

  attached_disk {
    source = google_compute_disk.secondary.self_link
  }

  network_interface {
    network    = google_compute_network.main.self_link
    subnetwork = google_compute_subnetwork.main.self_link
  }

  # metadata_startup_script = file("${path.module}/install.sh")
  metadata_startup_script = format(
    "#! /bin/bash\ncurl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='%s' PACKAGE_REGISTRY_USER='%s' PACKAGE_REGISTRY_PASSWORD='%s' SKIP_HW_CHECK=True bash -",
    var.rhino_agent_id,
    var.rhino_package_registry_user,
    var.rhino_package_registry_password
  )

  labels = merge(local.common_tags, {
    purpose = "confidential-compute"
  })

  depends_on = [google_compute_disk.secondary]
}

# --- Logging & Auditing ---------------------------------------------------------------------------------------------
# Creates a log sink to export all project logs to the designated Cloud Storage bucket.
resource "google_logging_project_sink" "to_gcs" {
  name                   = "${var.workgroup_name}-rhino-client-${var.environment}-log-sink"
  project                = var.project_id
  destination            = "storage.googleapis.com/${google_storage_bucket.logs.name}"
  unique_writer_identity = true
}

# Grants the log sink's unique service account permission to create objects in the bucket.
resource "google_storage_bucket_iam_member" "log_sink_writer" {
  bucket = google_storage_bucket.logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.to_gcs.writer_identity
}

# Configures Cloud Audit Logs to record admin activities and data access for all services.
resource "google_project_iam_audit_config" "all" {
  project = var.project_id
  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}