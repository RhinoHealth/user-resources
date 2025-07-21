# AWS Terraform Infrastructure with OpenTofu

This directory contains Terraform configuration files for deploying infrastructure on Amazon Web Services (AWS) using [OpenTofu](https://opentofu.org/) (a community fork of Terraform).

## Prerequisites

- [OpenTofu](https://opentofu.org/) (>= 1.10.x) installed (`brew install opentofu` on macOS)
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- AWS account with sufficient permissions (EC2, IAM, S3, CloudWatch, VPC, etc.)
- AWS region and availability zone selected

## Setup

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <repo-url>
   cd infrastructure/AWS
   ```

2. **Configure AWS credentials:**
   ```sh
   aws configure
   # or set environment variables:
   export AWS_ACCESS_KEY_ID=<your-access-key>
   export AWS_SECRET_ACCESS_KEY=<your-secret-key>
   export AWS_DEFAULT_REGION=<your-region>
   ```

3. **Edit `terraform.tfvars` and create `secret.auto.tfvars`**
   - Set your `aws_region`, `availability_zone`, and other variables as needed in `terraform.tfvars`.
   - Ensure `rhino_orchestrator_ip_range` includes all required IPs.
   - Create a file named `secret.auto.tfvars` (not committed to git) and set sensitive variables like:
     ```hcl
     rhino_package_registry_user     = "<rhino-provided-username>"
     rhino_package_registry_password = "<rhino-provided-password>"
     ```
   - Make sure `secret.auto.tfvars` is listed in `.gitignore` to avoid committing secrets.

4. **(Optional) Configure remote state**
   - Edit `versions.tf` to set your S3 bucket and key for state storage.

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

This configuration creates the following AWS resources:

### Networking
- **VPC**: Custom VPC with specified CIDR block
- **Subnet**: Private subnet in the specified availability zone
- **Internet Gateway**: For VPC internet connectivity
- **NAT Gateway**: For private subnet internet access
- **Route Table**: Routes traffic through NAT Gateway
- **Security Group**: Controls inbound/outbound traffic

### Storage
- **S3 Buckets**: Three buckets for output logs, source data, and audit logs
- **EBS Volume**: Secondary encrypted volume for additional storage

### Compute
- **EC2 Instance**: Ubuntu-based instance with Rhino Health agent
- **IAM Role**: Service role for EC2 instance
- **IAM Policy**: S3 access permissions
- **Instance Profile**: Links IAM role to EC2 instance

### Logging & Monitoring
- **CloudWatch Log Group**: For application logs
- **CloudTrail**: For API call auditing
- **S3 Bucket Policy**: Allows CloudTrail to write logs

## Notes
- Make sure required AWS services are enabled: EC2, IAM, S3, CloudWatch, VPC, CloudTrail
- Security groups are configured for egress traffic to Rhino orchestrator
- All S3 buckets have encryption and public access blocking enabled
- EBS volumes are encrypted by default
- For troubleshooting, check the AWS Console and CloudWatch logs

## References
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html) 