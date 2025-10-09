# Random suffix for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Edge Node Instance

resource "aws_instance" "main" {
  ami = "ami-0cb150ec8f12de138"

  # data.aws_ami.vm_image.id

  instance_market_options {
    market_type = "capacity-block"
  }

  lifecycle {
    ignore_changes = [
      instance_market_options,
    ]
  }

  instance_type          = var.vm_machine_type
  subnet_id              = data.aws_subnet.edge_node_private_subnet.id
  vpc_security_group_ids = [aws_security_group.main.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  availability_zone      = var.availability_zone

  capacity_reservation_specification {
    capacity_reservation_target {
      capacity_reservation_id = var.capacity_block_reservation
    }
  }

  root_block_device {
    volume_size = var.boot_disk_size_gb
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = format(
    "#! /bin/bash\ncurl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='%s' FLEET_ENROLL_SECRET='%s' PACKAGE_REGISTRY_USER='%s' PACKAGE_REGISTRY_PASSWORD='%s' SKIP_HW_CHECK=True bash -",
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
# resource "aws_s3_bucket_public_access_block" "output_logs" {
#   bucket = aws_s3_bucket.output_logs.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

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
# resource "aws_s3_bucket_public_access_block" "source_data" {
#   bucket = aws_s3_bucket.source_data.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

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
# resource "aws_s3_bucket_public_access_block" "logs" {
#   bucket = aws_s3_bucket.logs.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

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

# Creates an EBS volume for additional storage
resource "aws_ebs_volume" "secondary" {
  availability_zone = var.availability_zone
  size              = var.secondary_disk_size_gb
  type              = "gp3"
  encrypted         = true

  tags = merge(local.common_tags, {
    Name = "fred-hutch-caia-rhino-aws-prod-1-secondary"
  })
}

# Attaches the secondary EBS volume to the EC2 instance
resource "aws_volume_attachment" "secondary" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.secondary.id
  instance_id = aws_instance.main.id
}

# Creates S3 bucket for VM Clinical
resource "aws_s3_bucket" "clinical-wg" {
  bucket = "clinical-wg"

  tags = merge(local.common_tags, {
    Name = "clinical-wg"
  })
}

# Configures bucket versioning
resource "aws_s3_bucket_versioning" "clinical-wg" {
  bucket = aws_s3_bucket.clinical-wg.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configures bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "clinical-wg" {
  bucket = aws_s3_bucket.clinical-wg.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configures bucket public access block
# resource "aws_s3_bucket_public_access_block" "source_data" {
#   bucket = aws_s3_bucket.source_data.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# Configures bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "clinical-wg" {
  bucket = aws_s3_bucket.clinical-wg.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Creates S3 bucket for VM AI
resource "aws_s3_bucket" "ai-wg" {
  bucket = "ai-wg"

  tags = merge(local.common_tags, {
    Name = "ai-wg"
  })
}

# Configures bucket versioning
resource "aws_s3_bucket_versioning" "ai-wg" {
  bucket = aws_s3_bucket.ai-wg.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configures bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ai-wg" {
  bucket = aws_s3_bucket.ai-wg.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configures bucket public access block
# resource "aws_s3_bucket_public_access_block" "source_data" {
#   bucket = aws_s3_bucket.source_data.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# Configures bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "ai-wg" {
  bucket = aws_s3_bucket.ai-wg.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}