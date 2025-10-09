# Copyright 2025 Amazon Web Services

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
# - You will need to enable EC2, IAM, S3, CloudWatch, and VPC services

# --- Networking ------------------------------------------------------------------------------------------------------------------
# Creates a VPC with specified CIDR block
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = local.vpc_name
  })
}

# Creates a public subnet for NAT Gateway
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr_block
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-public"
    Type = "Public"
  })
}

# Creates a private subnet for EC2 instances
resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidr_block
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = false

  tags = merge(local.common_tags, {
    Name = local.subnet_name
    Type = "Private"
  })
}

# Creates an Internet Gateway for the VPC
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-igw"
  })
}

# Creates a route table for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-public-rt"
  })
}

# Associates the public route table with the public subnet
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Creates a NAT Gateway for private subnet internet access
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-nat-eip"
  })
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

# Creates a route table for the private subnet
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.vpc_name}-private-rt"
  })
}

# Associates the private route table with the private subnet
resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Creates a security group for the EC2 instance
resource "aws_security_group" "main" {
  name_prefix = "${local.vm_instance_name}-sg"
  vpc_id      = aws_vpc.main.id

  # Allow outbound HTTPS traffic to Rhino orchestrator
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.rhino_orchestrator_ip_range
    description = "Allow HTTPS egress to Rhino orchestrator"
  }

  # Allow all outbound traffic (for NAT Gateway access)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.vm_instance_name}-sg"
  })
}

# --- Storage ------------------------------------------------------------------------------------------------------------------
# Creates S3 bucket for storing outputs and logs
resource "aws_s3_bucket" "output_logs" {
  bucket = local.bucket_output_logs_name

  tags = merge(local.common_tags, {
    Name = local.bucket_output_logs_name
  })
}

# Configures bucket versioning
resource "aws_s3_bucket_versioning" "output_logs" {
  bucket = aws_s3_bucket.output_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configures bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "output_logs" {
  bucket = aws_s3_bucket.output_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configures bucket public access block
resource "aws_s3_bucket_public_access_block" "output_logs" {
  bucket = aws_s3_bucket.output_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configures bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "output_logs" {
  bucket = aws_s3_bucket.output_logs.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Configures bucket lifecycle policy
resource "aws_s3_bucket_lifecycle_configuration" "output_logs" {
  bucket = aws_s3_bucket.output_logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    expiration {
      days = 90 # 3 months
    }
  }
}

# Creates S3 bucket for storing source data
resource "aws_s3_bucket" "source_data" {
  bucket = local.bucket_source_data_name

  tags = merge(local.common_tags, {
    Name = local.bucket_source_data_name
  })
}

# Configures bucket versioning
resource "aws_s3_bucket_versioning" "source_data" {
  bucket = aws_s3_bucket.source_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configures bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "source_data" {
  bucket = aws_s3_bucket.source_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configures bucket public access block
resource "aws_s3_bucket_public_access_block" "source_data" {
  bucket = aws_s3_bucket.source_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configures bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "source_data" {
  bucket = aws_s3_bucket.source_data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Creates S3 bucket for storing logs
resource "aws_s3_bucket" "logs" {
  bucket = local.bucket_logs_name

  tags = merge(local.common_tags, {
    Name = local.bucket_logs_name
  })
}

# Configures bucket versioning
resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configures bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configures bucket public access block
resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configures bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Configures bucket lifecycle policy
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    expiration {
      days = 90 # 3 months
    }
  }
}

# --- IAM & Service Accounts ------------------------------------------------------------------------------------------------------------------
# Creates an IAM role for the EC2 instance
resource "aws_iam_role" "ec2" {
  name = "${var.workgroup_name}-rhino-${var.environment}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Creates an IAM policy for S3 access
resource "aws_iam_policy" "s3_access" {
  name        = "${var.workgroup_name}-rhino-${var.environment}-s3-policy"
  description = "Policy for S3 bucket access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.source_data.arn,
          "${aws_s3_bucket.source_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.output_logs.arn,
          "${aws_s3_bucket.output_logs.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      }
    ]
  })
}

# Creates an IAM policy for KMS access
resource "aws_iam_policy" "kms_access" {
  name        = "${var.workgroup_name}-rhino-${var.environment}-kms-policy"
  description = "Policy for KMS decrypt access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attaches the S3 policy to the EC2 role
resource "aws_iam_role_policy_attachment" "ec2_s3" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Attaches the AWS managed policy for SSM to the EC2 role
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Attaches the KMS policy to the EC2 role
resource "aws_iam_role_policy_attachment" "ec2_kms" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.kms_access.arn
}

# Creates an instance profile for the EC2 instance
resource "aws_iam_instance_profile" "ec2" {
  name = "${var.workgroup_name}-rhino-${var.environment}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# --- Compute ------------------------------------------------------------------------------------------------------------------
# Creates an EBS volume for additional storage
resource "aws_ebs_volume" "secondary" {
  availability_zone = var.availability_zone
  size              = var.secondary_disk_size_gb
  type              = "gp3"
  encrypted         = true

  tags = merge(local.common_tags, {
    Name = "${local.vm_instance_name}-secondary"
  })
}

# Creates the EC2 instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.vm_image.id
  instance_type          = var.vm_machine_type
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.main.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size = var.boot_disk_size_gb
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = format(
    "#!/bin/bash\ncurl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='%s' FLEET_ENROLL_SECRET='%s' PACKAGE_REGISTRY_USER='%s' PACKAGE_REGISTRY_PASSWORD='%s' SKIP_HW_CHECK=True bash -",
    var.rhino_agent_id,
    var.rhino_enroll_secret,
    var.rhino_package_registry_user,
    var.rhino_package_registry_password
  )

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  tags = merge(local.common_tags, {
    Name = local.vm_instance_name
  })

  depends_on = [aws_ebs_volume.secondary]
}

# Attaches the secondary EBS volume to the EC2 instance
resource "aws_volume_attachment" "secondary" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.secondary.id
  instance_id = aws_instance.main.id
}
