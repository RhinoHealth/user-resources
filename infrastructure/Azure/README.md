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

3. **Generate SSH key pair** (if you don't have one):
   ```sh
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
   ```

4. **Edit `terraform.tfvars` and create `secret.auto.tfvars`**
   - Set your `location` and other variables as needed in `terraform.tfvars`.
   - Ensure `rhino_orchestrator_ip_range` includes all required IPs.
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
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

## Infrastructure Components

This configuration creates the following Azure resources:

### Resource Management
- **Resource Group**: Container for all resources

### Networking
- **Virtual Network**: Custom VNet with specified address space
- **Subnet**: Private subnet in the specified address range
- **Network Security Group**: Controls inbound/outbound traffic
- **NAT Gateway**: For private subnet internet access
- **Public IP**: For NAT Gateway connectivity

### Storage
- **Storage Accounts**: Three storage accounts for output logs, source data, and audit logs
- **Blob Containers**: Private containers within each storage account
- **Managed Disk**: Secondary encrypted disk for additional storage

### Compute
- **Virtual Machine**: Ubuntu-based VM with Rhino Health agent
- **Network Interface**: Network interface for the VM
- **User-Assigned Managed Identity**: Service identity for the VM
- **Role Assignments**: Storage account access permissions

### Logging & Monitoring
- **Log Analytics Workspace**: For centralized logging
- **Diagnostic Settings**: For VM and storage account monitoring

## Notes
- Make sure required Azure services are enabled: Virtual Machines, Storage Accounts, Network Security Groups, Log Analytics
- Network Security Groups are configured for egress traffic to Rhino orchestrator
- All storage accounts have encryption and versioning enabled
- Managed disks are encrypted by default
- For troubleshooting, check the Azure Portal and Log Analytics workspace

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Azure Terraform Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure VM Custom Data](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/using-cloud-init) 