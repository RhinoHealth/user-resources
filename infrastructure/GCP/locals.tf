# --- Local Values for Naming Convention ---
locals {
  # VPC Network: {workgroup name}-rhino-client-{environment}-vpc-{seq#}
  vpc_network_name = "${var.workgroup_name}-rhino-client-${var.environment}-vpc-${var.sequence_number}"
  
  # Subnet: {workgroup name}-rhino-client-{environment}-vpc-{seq#}-subnet-{seq#}
  subnet_name = "${var.workgroup_name}-rhino-client-${var.environment}-vpc-${var.sequence_number}-subnet-${var.sequence_number}"
  
  # VM: {workgroup name}-rhino-client-{environment}-{seq#}
  vm_instance_name = "${var.workgroup_name}-rhino-client-${var.environment}-${var.sequence_number}"
  
  # Firewall: {workgroup name}-rhino-client-{protocol}-{port}-{action}
  firewall_egress_name = "${var.workgroup_name}-rhino-client-tcp-443-allow"
  
  # Buckets: {workgroup name}-rhino-client-{type}-{seq#}
  bucket_output_logs_name = "${var.workgroup_name}-rhino-client-output-data-${var.sequence_number}"
  bucket_source_data_name = "${var.workgroup_name}-rhino-client-input-data-${var.sequence_number}"
  bucket_logs_name = "${var.workgroup_name}-rhino-client-log-${var.sequence_number}"
  
  # Standard tags for cost aggregation
  common_tags = {
    workgroup   = var.workgroup_name
    environment = var.environment
    purpose     = "rhino-client"
    managed_by  = "terraform"
  }
}
