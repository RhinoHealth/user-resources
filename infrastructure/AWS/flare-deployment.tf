# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {}
data "aws_ssm_parameter" "ubuntu_ami" {
  name = "/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

# Random suffix for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# KMS Key for encryption
resource "aws_kms_key" "edge_node_kms_key" {
  description             = "KMS key for Edge Node data encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })

  tags = {
    DataClassification = "Confidential"
    Environment       = "Production"
  }
}

# Log bucket
resource "aws_s3_bucket" "edge_node_log_bucket" {
  bucket        = "edge-node-logs-${data.aws_caller_identity.current.account_id}-${random_id.bucket_suffix.hex}"
  force_destroy = true

  tags = {
    DataClassification = "Confidential"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "edge_node_log_bucket_encryption" {
  bucket = aws_s3_bucket.edge_node_log_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "edge_node_log_bucket_pab" {
  bucket = aws_s3_bucket.edge_node_log_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "edge_node_log_bucket_versioning" {
  bucket = aws_s3_bucket.edge_node_log_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Edge Node VPC
resource "aws_vpc" "edge_node_vpc" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name               = "EdgeNodeDeployment/EdgeNode/EdgeNodeVpc"
    DataClassification = "Confidential"
  }
}

resource "aws_subnet" "edge_node_private_subnet" {
  vpc_id            = aws_vpc.edge_node_vpc.id
  cidr_block        = "10.1.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name               = "EdgeNodeDeployment/EdgeNode/EdgeNodeVpc/PrivateSubnet1"
    DataClassification = "Confidential"
  }
}

# Edge Node Security Group
resource "aws_security_group" "edge_node_sg" {
  name_prefix = "edge-node-sg"
  vpc_id      = aws_vpc.edge_node_vpc.id

  ingress {
    from_port   = 8002
    to_port     = 8003
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming Edge Node traffic"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "EdgeNodeSecurityGroup"
  }
}

# Edge Node IAM Role
resource "aws_iam_role" "edge_node_instance_role" {
  name = "EdgeNodeInstanceRole"

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
}

resource "aws_iam_role_policy_attachment" "edge_node_ssm" {
  role       = aws_iam_role.edge_node_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "edge_node_cloudwatch" {
  role       = aws_iam_role.edge_node_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy" "edge_node_instance_policy" {
  name = "EdgeNodeInstancePolicy"
  role = aws_iam_role.edge_node_instance_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.edge_node_data_bucket.arn,
          "${aws_s3_bucket.edge_node_data_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.edge_node_kms_key.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "edge_node_instance_profile" {
  name = "EdgeNodeInstanceProfile"
  role = aws_iam_role.edge_node_instance_role.name
}

# Edge Node Instance
resource "aws_instance" "edge_node" {
  ami                    = data.aws_ssm_parameter.ubuntu_ami.value
  instance_type          = "g4dn.xlarge"
  subnet_id              = aws_subnet.edge_node_private_subnet.id
  vpc_security_group_ids = [aws_security_group.edge_node_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.edge_node_instance_profile.name
  availability_zone      = data.aws_availability_zones.available.names[0]

  root_block_device {
    volume_size = 100
    encrypted   = true
    kms_key_id  = aws_kms_key.edge_node_kms_key.arn
  }

  user_data_base64 = base64encode(file("${path.module}/edge_node_userdata.sh"))

  tags = {
    Name               = "EdgeNodeDeployment/EdgeNode/EdgeNode-1"
    DataClassification = "Confidential"
  }
}

# Edge Node S3 bucket
resource "aws_s3_bucket" "edge_node_data_bucket" {
  bucket        = "edge-node-data-${data.aws_caller_identity.current.account_id}-site-1-${random_id.bucket_suffix.hex}"
  force_destroy = true

  tags = {
    DataClassification = "Confidential"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "edge_node_bucket_encryption" {
  bucket = aws_s3_bucket.edge_node_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.edge_node_kms_key.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "edge_node_bucket_pab" {
  bucket = aws_s3_bucket.edge_node_data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "edge_node_bucket_versioning" {
  bucket = aws_s3_bucket.edge_node_data_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "edge_node_monitoring" {
  dashboard_name = "EdgeNodeDashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.edge_node.id]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.id
          title  = "Edge Node CPU Utilization"
        }
      }
    ]
  })
}

# SNS Topic
resource "aws_sns_topic" "edge_node_notifications" {
  name         = "edge-node-alerts"
  display_name = "EdgeNodeAlerts"
}

# CloudWatch Alarm
resource "aws_cloudwatch_metric_alarm" "edge_node_cpu" {
  alarm_name          = "edge-node-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alarm if edge node CPU exceeds 80% for 15 minutes"
  alarm_actions       = [aws_sns_topic.edge_node_notifications.arn]

  dimensions = {
    InstanceId = aws_instance.edge_node.id
  }
}

# Outputs
output "edge_node_private_dns" {
  description = "DNS for edge node instance"
  value       = aws_instance.edge_node.private_dns
}

output "edge_node_bucket_name" {
  description = "Edge node data bucket name"
  value       = aws_s3_bucket.edge_node_data_bucket.id
}