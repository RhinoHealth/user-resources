# AWS Terraform Infrastructure for Rhino Health

This directory contains Terraform configuration files for deploying a secure, production-ready infrastructure on Amazon Web Services (AWS) for Rhino Health applications. The infrastructure follows AWS Well-Architected Framework principles and implements security best practices.

## 🏗️ Architecture Overview

The infrastructure creates a secure, multi-tier architecture with the following components:

### Networking Layer
- **VPC**: Custom VPC with isolated network segments
- **Public Subnet**: Hosts NAT Gateway for internet connectivity
- **Private Subnet**: Hosts EC2 instances with no direct internet access
- **Internet Gateway**: Provides internet connectivity to the VPC
- **NAT Gateway**: Enables private instances to access internet securely
- **Route Tables**: Separate routing for public and private subnets
- **Security Groups**: Granular traffic control with least-privilege access

### Compute Layer
- **EC2 Instance**: Ubuntu-based instance with Rhino Health agent
- **EBS Volumes**: Encrypted boot and secondary storage volumes
- **IAM Role**: Service role with minimal required permissions
- **Instance Profile**: Links IAM role to EC2 instance
- **SSM Agent**: Enables secure remote access via Session Manager

### Storage Layer
- **S3 Buckets**: Three separate buckets for different data types
  - Output/Logs bucket: For application outputs and logs
  - Source Data bucket: For input data (read-only access)
  - Audit Logs bucket: For CloudTrail and audit logs
- **Lifecycle Policies**: Automated data lifecycle management
- **Encryption**: Server-side encryption enabled on all buckets
- **Access Controls**: Public access blocked, ownership controls enforced

### Monitoring & Logging
- **CloudWatch Logs**: Centralized log collection and monitoring
- **CloudTrail**: API call auditing and compliance
- **CloudWatch Agent**: System metrics and log forwarding
- **Log Retention**: Configurable retention policies

## 🔒 Security Features

### Network Security
- Private subnet deployment for EC2 instances
- NAT Gateway for controlled internet access
- Security groups with least-privilege egress rules
- No inbound access to EC2 instances

### Data Security
- All EBS volumes encrypted at rest
- S3 buckets encrypted with AES-256
- Public access blocked on all S3 buckets
- Bucket ownership controls enforced

### Access Control
- IAM roles with minimal required permissions
- No hardcoded credentials in configuration
- IMDSv2 enabled on EC2 instances
- SSH password authentication disabled
- SSM Session Manager for secure remote access

### Compliance & Auditing
- CloudTrail enabled for API call logging
- S3 bucket policies for CloudTrail integration
- Comprehensive tagging for cost allocation
- Log retention policies for compliance

## 📋 Prerequisites

### Required Software
- [OpenTofu](https://opentofu.org/) (>= 1.10.x) or [Terraform](https://www.terraform.io/) (>= 1.0.x)
- [AWS CLI](https://aws.amazon.com/cli/) (>= 2.0.x)
- Bash shell (for script execution)

### Installation Commands
```bash
# macOS
brew install opentofu
brew install awscli

# Ubuntu/Debian
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
sudo apt-get update && sudo apt-get install terraform

# Windows
# Download from https://www.terraform.io/downloads.html
```

### AWS Requirements
- AWS account with appropriate permissions
- Enabled services: EC2, IAM, S3, CloudWatch, VPC, CloudTrail
- Sufficient service quotas for resources
- Valid AWS credentials configured

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd infrastructure/AWS
```

### 2. Configure AWS Credentials
```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

### 3. Configure Variables
Edit `terraform.tfvars` with your specific values:
```hcl
aws_region        = "us-east-1"
availability_zone = "us-east-1a"
workgroup_name    = "your-workgroup"
environment       = "prod"
rhino_agent_id    = "your-rhino-agent-id"
ubuntu_version    = "24.04"
# ... other variables
```

Create `secret.auto.tfvars` for sensitive data only:
```hcl
rhino_package_registry_user     = "your-username"
rhino_package_registry_password = "your-password"
```

### 4. Initialize and Deploy
```bash
# Initialize Terraform
tofu init

# Review the plan
tofu plan -out=tf.plan

# Apply the configuration
tofu apply tf.plan
```

### 5. Verify Deployment
```bash
# View outputs
tofu output

# Check AWS Console
# - EC2 instances should be running
# - S3 buckets should be created
# - CloudWatch logs should be available
```

## ⚙️ Configuration

### Network Configuration
The infrastructure creates a VPC with the following CIDR blocks:
- **VPC**: `10.0.0.0/16`
- **Public Subnet**: `10.0.1.0/24` (for NAT Gateway)
- **Private Subnet**: `10.0.2.0/24` (for EC2 instances)

### Instance Configuration
- **Instance Type**: t3.medium (configurable)
- **AMI**: Ubuntu LTS (configurable version: 22.04 "Jammy", 24.04 "Noble")
- **Boot Disk**: 250GB GP3 encrypted volume
- **Secondary Disk**: 2TB GP3 encrypted volume

### S3 Bucket Configuration
- **Versioning**: Enabled on all buckets
- **Encryption**: AES-256 server-side encryption
- **Lifecycle**: 30 days → Standard-IA, 90 days → Deletion
- **Access**: Public access blocked, ownership controls enforced

## 🔧 Customization

### Adding Additional Resources
1. Create new resource blocks in `main.tf`
2. Add corresponding variables in `variables.tf`
3. Update `terraform.tfvars` with new values
4. Add outputs in `outputs.tf` if needed

### Modifying Security Groups
Edit the security group rules in `main.tf`:
```hcl
resource "aws_security_group" "main" {
  # Add/modify egress rules as needed
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["specific-ip-range"]
    description = "Custom HTTPS access"
  }
}
```

### Updating IAM Permissions
Modify IAM policies in `main.tf`:
```hcl
resource "aws_iam_policy" "custom_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject"]
        Resource = ["arn:aws:s3:::bucket-name/*"]
      }
    ]
  })
}
```

## 📊 Monitoring and Troubleshooting

### CloudWatch Logs
- Application logs: `/aws/ec2/${var.workgroup_name}-rhino-${var.environment}-${var.sequence_number}` (CloudWatch log group, log stream: `rhino-application`)
- System logs: `/aws/ec2/${var.workgroup_name}-rhino-${var.environment}-${var.sequence_number}` (CloudWatch log group, log stream: `rhino-system`)
- User data logs: Available in `/var/log/rhino/` on the instance

### CloudTrail
- API call logs stored in S3 bucket
- Management events and data events logged
- Multi-region trail available (disabled by default)

### SSM Session Manager
The EC2 instance is configured with SSM Session Manager for secure remote access without SSH keys.

#### Connect via AWS CLI

> **Note:** The AWS CLI SSM Session Manager requires the [Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) to be installed on your local machine. See [AWS documentation](http://docs.aws.amazon.com/console/systems-manager/session-manager-plugin-not-found) for installation instructions.

```bash
# Connect using instance ID from outputs
aws ssm start-session --target $(tofu output -raw ec2_instance_id) --region $(tofu output -raw aws_region)
```

#### Connect via AWS Console
1. Go to EC2 Console → Instances
2. Select your instance
3. Click "Connect" → "Session Manager"
4. Click "Connect"

#### Benefits of SSM Session Manager
- ✅ No SSH keys required
- ✅ No inbound ports needed
- ✅ IAM-based access control
- ✅ Session logging and auditing
- ✅ Works through NAT Gateway

## 🧹 Infrastructure Cleanup

The easiest way to clean up all resources is using OpenTofu:

```bash
# Review what will be destroyed
tofu plan -destroy -out=tf.destroy

# Destroy all resources
tofu apply tf.destroy

# Note: If you encounter issues during resource destruction (e.g., S3 buckets not being deleted due to remaining objects or versions),
# you may need to manually clean up the buckets as shown below.
# Get bucket names from outputs
OUTPUT_BUCKET=$(tofu output -raw s3_bucket_output_logs)
SOURCE_BUCKET=$(tofu output -raw s3_bucket_source_data)
LOGS_BUCKET=$(tofu output -raw s3_bucket_logs)

# Remove all objects and all versions from the current bucket
for BUCKET in "$OUTPUT_BUCKET" "$SOURCE_BUCKET" "$LOGS_BUCKET"; do
  aws s3api list-object-versions --bucket "$BUCKET" --output json \
    | jq -r '.Versions[]?, .DeleteMarkers[]? | [.Key, .VersionId] | @tsv' \
    | while read key version; do
        aws s3api delete-object --bucket "$BUCKET" --key "$key" --version-id "$version"
      done
done

# Review what will be destroyed
tofu plan -destroy -out=tf.destroy

# Destroy all resources
tofu apply tf.destroy
```

### Cost Considerations
- **NAT Gateway**: ~$45/month per NAT Gateway
- **EBS Volumes**: ~$0.10/GB/month for GP3 volumes
- **EC2 Instances**: Varies by instance type (t3.medium ~$30/month)
- **S3 Storage**: ~$0.023/GB/month for Standard storage
- **CloudTrail**: ~$2.00/month for management events

### Cleanup Best Practices
1. **Always use `tofu destroy` first** - it's the safest method
2. **Review the plan** before destroying to understand what will be removed
3. **Backup important data** before cleanup
4. **Verify cleanup completion** to avoid unexpected charges
5. **Use resource tagging** to easily identify resources for cleanup
6. **Monitor costs** after cleanup to ensure no orphaned resources remain

## 🔗 References

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [OpenTofu Documentation](https://opentofu.org/docs/)
- [AWS EC2 User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
- [AWS S3 Security](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security.html)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Important Notes

- This infrastructure is designed for demonstration and development purposes
- Review and modify security settings for production use
- Ensure compliance with your organization's security policies
- Regularly update AMIs and dependencies
- Monitor costs and adjust resources as needed
- Backup important data before making changes
