# Azure Terraform Infrastructure with OpenTofu

This directory contains Terraform configuration files for deploying infrastructure on Microsoft Azure using [OpenTofu](https://opentofu.org/) (a community fork of Terraform).

## Prerequisites

- [OpenTofu](https://opentofu.org/) (>= 1.10.x) installed (`brew install opentofu` on macOS)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated
- Azure subscription with sufficient permissions (Virtual Machines, Storage Accounts, Network Security Groups, etc.)
- SSH key pair for VM access
- Azure region selected

## Setup

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <repo-url>
   cd infrastructure/Azure
   ```

2. **Authenticate with Azure:**
   ```sh
   az login
   # or set environment variables:
   export ARM_CLIENT_ID=<your-client-id>
   export ARM_CLIENT_SECRET=<your-client-secret>
   export ARM_SUBSCRIPTION_ID=<your-subscription-id>
   export ARM_TENANT_ID=<your-tenant-id>
   ```

3. **Update client variables**
   - Update the [terraform variables](./terraform.tfvars) to describe client you are installing. For example, if you are building the fourth client to connect to the AWS orchestrator, you would use the following:
     ``` 
     # Naming Convention Variables
     workgroup_name  = "<my-workgroup>"
     environment     = "aws-prod"
     sequence_number = "4"
     ```
   - Set your `location` and other variables as needed in `terraform.tfvars`.
   - Ensure `rhino_orchestrator_ip_range` includes all required IPs.

4. **Create `secret.auto.tfvars`**
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
     rhino_agent_id                  = "<rhino-provided-agent-id>"
     rhino_enroll_secret             = "<rhino-provided-enroll-secret>"
     rhino_package_registry_user     = "<rhino-provided-username>"
     rhino_package_registry_password = "<rhino-provided-password>"
     ```
   - Make sure `secret.auto.tfvars` is listed in `.gitignore` to avoid committing secrets.

5. **(Optional) Configure remote state**
   - Edit `versions.tf` to set your Azure Storage account and container for state storage.

## Running OpenTofu

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

- The SSH private key is stored in Azure Key Vault as a secret. The Key Vault name is `${var.workgroup_name}-rhino-${var.environment}-kv`.

- The `vm_ip_type` variable controls how the VM is accessed:
  - `vm_ip_type = "public"` (default): VM gets a public IP for direct access.
  - `vm_ip_type = "nat"`: Use this if you have access to the internal network (no public IP is assigned; access is via NAT gateway or internal routing).

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Azure Terraform Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure VM Custom Data](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/using-cloud-init)
