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

  user_data = <<-EOT
    #!/bin/bash
    set -e

    # Mount secondary EBS volume to /rhino
    MOUNT_POINT="/rhino"

    # Wait for the device to be attached (check for /dev/sdf or NVMe equivalent)
    echo "Waiting for secondary disk to be attached..."
    for i in {1..30}; do
      if [ -e /dev/sdf ]; then
        DISK_PATH="/dev/sdf"
        break
      elif [ -e /dev/nvme1n1 ]; then
        DISK_PATH="/dev/nvme1n1"
        break
      fi
      sleep 2
    done

    if [ -z "$DISK_PATH" ]; then
      echo "Error: Secondary disk not found after 60 seconds"
      exit 1
    fi

    echo "Found secondary disk at $DISK_PATH"

    # Check if the disk is already formatted, if not, format it
    if ! sudo blkid "$DISK_PATH"; then
      echo "Formatting $DISK_PATH..."
      sudo mkfs.ext4 -F "$DISK_PATH"
    else
      echo "$DISK_PATH is already formatted."
    fi

    # Create mount point if it doesn't exist
    sudo mkdir -p "$MOUNT_POINT"

    # Get the UUID of the disk
    UUID=$(sudo blkid -s UUID -o value "$DISK_PATH")

    # Add entry to /etc/fstab if not already present
    if ! grep -q "UUID=$UUID $MOUNT_POINT" /etc/fstab; then
      echo "Adding entry to /etc/fstab for $DISK_PATH..."
      echo "UUID=$UUID $MOUNT_POINT ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
    else
      echo "Entry for $DISK_PATH already exists in /etc/fstab."
    fi

    # Mount the disk if not already mounted
    if ! mountpoint -q "$MOUNT_POINT"; then
      echo "Mounting $DISK_PATH to $MOUNT_POINT..."
      sudo mount "$MOUNT_POINT"
    else
      echo "$MOUNT_POINT is already mounted."
    fi

    echo "Secondary disk successfully mounted to $MOUNT_POINT"

    # Install Rhino agent
    curl -fsS --proto '=https' https://activate.rhinohealth.com | sudo RHINO_AGENT_ID='${var.rhino_agent_id}' FLEET_ENROLL_SECRET='${var.rhino_enroll_secret}' PACKAGE_REGISTRY_USER='${var.rhino_package_registry_user}' PACKAGE_REGISTRY_PASSWORD='${var.rhino_package_registry_password}' SKIP_HW_CHECK=True bash -
  EOT

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
    Name = "${local.vm_instance_name}-secondary"
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
  bucket = local.bucket_clinical_wg_name

  tags = merge(local.common_tags, {
    Name = local.bucket_clinical_wg_name
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
  bucket = local.bucket_ai_wg_name

  tags = merge(local.common_tags, {
    Name = local.bucket_ai_wg_name
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
