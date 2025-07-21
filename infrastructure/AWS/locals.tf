# --- Local Values for Naming Convention ---
locals {
  # VPC: {workgroup name}-rhino-{environment}-vpc-{seq#}
  vpc_name = "${var.workgroup_name}-rhino-${var.environment}-vpc-${var.sequence_number}"
  
  # Subnet: {workgroup name}-rhino-{environment}-vpc-{seq#}-subnet-{seq#}
  subnet_name = "${var.workgroup_name}-rhino-${var.environment}-vpc-${var.sequence_number}-subnet-${var.sequence_number}"
  
  # EC2 Instance: {workgroup name}-rhino-{environment}-{seq#}
  vm_instance_name = "${var.workgroup_name}-rhino-${var.environment}-${var.sequence_number}"
  
  # Security Group: {workgroup name}-rhino-{protocol}-{port}-{action}
  security_group_name = "${var.workgroup_name}-rhino-tcp-443-allow"
  
  # S3 Buckets: {workgroup name}-rhino-{type}-{seq#}
  bucket_output_logs_name = "${var.workgroup_name}-rhino-output-data-${var.sequence_number}"
  bucket_source_data_name = "${var.workgroup_name}-rhino-input-data-${var.sequence_number}"
  bucket_logs_name = "${var.workgroup_name}-rhino-log-${var.sequence_number}"
  
  # Standard tags for cost aggregation
  common_tags = {
    workgroup   = var.workgroup_name
    environment = var.environment
    purpose     = "rhino-client"
    managed_by  = "terraform"
  }
} 