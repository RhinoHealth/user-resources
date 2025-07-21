
# AWS Terraform Infrastructure with Tofu

This directory contains Terraform configuration files for deploying infrastructure on Amazon Web Services (AWS) using [OpenTofu](https://opentofu.org/).

## Prerequisites

- [OpenTofu](https://opentofu.org/) (>= 1.10.x) installed (`brew install opentofu` on macOS)
- [AWS CLI](https://aws.amazon.com/cli/) (>= 2.0.x) installed and configured
- AWS account with sufficient permissions (EC2, IAM, S3, CloudWatch, VPC, CloudTrail, etc.)
- Valid AWS credentials (via `aws configure` or environment variables)

## Setup

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <repo-url>
   cd infrastructure/AWS
   ```

2. **Configure AWS Credentials:**
   You can configure your AWS credentials in one of two ways:

   - **Using the AWS CLI (recommended for most users):**
     ```sh
     aws configure
     ```
     This will prompt you to enter your AWS Access Key, Secret Access Key, region, and output format, and will save them in `~/.aws/credentials` and `~/.aws/config`.

   - **Or by setting environment variables (useful for CI/CD or temporary sessions):**
     ```sh
     export AWS_ACCESS_KEY_ID="<your-access-key>"
     export AWS_SECRET_ACCESS_KEY="<your-secret-key>"
     export AWS_DEFAULT_REGION="<your-region>"  # optional but recommended
     ```

3. **Edit `terraform.tfvars` and create `secret.auto.tfvars`**
   - Set your `aws_region`, `availability_zone`, and other variables as needed in `terraform.tfvars`.
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
     rhino_agent_id                  = "<rhino-provided-agent-id>"
     rhino_package_registry_user     = "<rhino-provided-username>"
     rhino_package_registry_password = "<rhino-provided-password>"
     ```
   - Make sure `secret.auto.tfvars` is listed in `.gitignore` to avoid committing secrets.

4. **(Optional) Configure remote state**
   - Edit `versions.tf` to set your S3 bucket and prefix for state storage if desired.

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
- Make sure required AWS services are enabled: EC2, IAM, S3, VPC, etc.
- Ensure you have sufficient service quotas for all resources.
- If you encounter issues destroying S3 buckets (due to remaining objects or versions), you may need to manually empty the buckets before running `tofu destroy`.

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/)
