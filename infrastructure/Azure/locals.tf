# --- Local Values for Naming Convention ---
locals {
  # Resource Group: {workgroup name}-rhino-{environment}-rg-{seq#}
  resource_group_name = "${var.workgroup_name}-rhino-${var.environment}-rg-${var.sequence_number}"
  
  # Virtual Network: {workgroup name}-rhino-{environment}-vnet-{seq#}
  vnet_name = "${var.workgroup_name}-rhino-${var.environment}-vnet-${var.sequence_number}"
  
  # Subnet: {workgroup name}-rhino-{environment}-vnet-{seq#}-subnet-{seq#}
  subnet_name = "${var.workgroup_name}-rhino-${var.environment}-vnet-${var.sequence_number}-subnet-${var.sequence_number}"
  
  # Virtual Machine: {workgroup name}-rhino-{environment}-{seq#}
  vm_name = "${var.workgroup_name}-rhino-${var.environment}-${var.sequence_number}"
  
  # Storage Accounts: {workgroup name}rhino{type}{seq#} (lowercase, no hyphens for Azure storage account naming)
  storage_account_output_logs_name = "${replace(var.workgroup_name, "-", "")}rhinooutput${var.sequence_number}"
  storage_account_source_data_name = "${replace(var.workgroup_name, "-", "")}rhinoinput${var.sequence_number}"
  storage_account_logs_name = "${replace(var.workgroup_name, "-", "")}rhinolog${var.sequence_number}"
  
  # Standard tags for cost aggregation
  common_tags = {
    workgroup   = var.workgroup_name
    environment = var.environment
    purpose     = "rhino-client"
    managed_by  = "terraform"
  }
} 