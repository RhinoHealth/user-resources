# GCP Terraform Infrastructure with Tofu

This directory contains Terraform configuration files for deploying infrastructure on Google Cloud Platform (GCP) using [OpenTofu](https://opentofu.org/) (a community fork of Terraform).

## Prerequisites

- [OpenTofu](https://opentofu.org/) (>= 1.10.x) installed (`brew install opentofu` on macOS)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated
- Service account with sufficient permissions (Compute, Storage, IAM, Logging, etc.)
- Service account key JSON file (if not using gcloud auth)
- GCP project and billing enabled

## Setup

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <repo-url>
   cd infrastructure/GCP
   ```

2. **Authenticate with Google Cloud:**
   ```sh
   gcloud auth application-default login
   # or, if using a service account key:
   export GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account.json>
   ```

3. **Edit `terraform.tfvars` and create `secret.auto.tfvars`**
   - Set your `project_id`, `region`, and other variables as needed in `terraform.tfvars`.
   - Ensure `rhino_orechestrator_ip_range` includes all required IPs.
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
     rhino_package_registry_user     = "<rhino-provided-username>"
     rhino_package_registry_password = "<rhino-provided-password>"
     ```
   - Make sure `secret.auto.tfvars` is listed in `.gitignore` to avoid committing secrets.

4. **(Optional) Configure remote state**
   - Edit `versions.tf` to set your GCS bucket and prefix for state storage.

## Running Tofu

1. **Initialize the working directory:**
   ```sh
   tofu init
   ```

2. **Review the planned changes:**
   ```sh
   tofu plan
   ```

3. **Apply the changes:**
   ```sh
   tofu apply
   ```
   - Review the output and type `yes` to confirm.

4. **(Optional) Destroy resources:**
   ```sh
   tofu destroy
   ```

## Notes
- Make sure required APIs are enabled: Compute Engine, IAM, Cloud Logging, Cloud Resource Manager.
- Firewall rules are configured for IAP SSH and egress as needed.
- For troubleshooting, check the GCP Console and logs.

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Google Cloud Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud IAP SSH](https://cloud.google.com/iap/docs/using-tcp-forwarding)
