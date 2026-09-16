# Rhino FCP Infrastructure

This folder contains [OpenTofu](https://opentofu.org/) (a community fork of Terraform) modules for provisioning the infrastructure needed to run a Rhino on-prem client/workgroup connector - the component that lets your own cloud account or data center securely connect to and run jobs for the Rhino Federated Computing Platform (FCP).

## Structure

Each subfolder is a self-contained OpenTofu module for one cloud provider - pick the one matching where you want to deploy:

- **[`AWS/`](./AWS/README.md)** - Deploy on Amazon Web Services.
- **[`Azure/`](./Azure/README.md)** - Deploy on Microsoft Azure.
- **[`GCP/`](./GCP/README.md)** - Deploy on Google Cloud Platform.

Each module follows the same general shape (`main.tf`, `variables.tf`, `locals.tf`, `versions.tf`, `terraform.tfvars`), and the same overall workflow:

1. Install OpenTofu and the relevant cloud provider's CLI, and authenticate.
2. Fill in `terraform.tfvars` with naming/environment variables for the client you're deploying (workgroup name, environment, sequence number, region, etc).
3. Create an untracked `secret.auto.tfvars` file with Rhino-provided credentials (`rhino_agent_id`, `rhino_package_registry_user`, `rhino_package_registry_password`) - never commit this file.
4. Run `tofu init`, `tofu plan`, and `tofu apply`.

See each module's own README for provider-specific prerequisites, variables, and notes - they differ in the details (e.g. Azure's SSH key is stored in Key Vault; GCP requires specific APIs to be enabled; AWS state can be stored in S3).

# Getting Help

For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
