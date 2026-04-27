# --- Local Values for Naming Convention ---
locals {
  workgroup_name_lower = lower(var.workgroup_name)
  workgroup_name_alnum = replace(local.workgroup_name_lower, "-", "")

  # Resource Group: {workgroup name}-rhino-{environment}-rg-{seq#}
  resource_group_name = "${var.workgroup_name}-rhino-${var.environment}-rg-${var.sequence_number}"

  # Virtual Network: {workgroup name}-rhino-{environment}-vnet-{seq#}
  vnet_name = "${var.workgroup_name}-rhino-${var.environment}-vnet-${var.sequence_number}"

  # Subnet: {workgroup name}-rhino-{environment}-vnet-{seq#}-subnet-{seq#}
  subnet_name = "${var.workgroup_name}-rhino-${var.environment}-vnet-${var.sequence_number}-subnet-${var.sequence_number}"

  # Virtual Machine: {workgroup name}-rhino-{environment}-{seq#}
  vm_name = "${var.workgroup_name}-rhino-${var.environment}-${var.sequence_number}"

  # Azure storage account names are limited to 24 lowercase alphanumeric characters.
  storage_account_prefix_max_length = 24 - length(var.sequence_number) - 3
  storage_account_prefix            = substr(local.workgroup_name_alnum, 0, local.storage_account_prefix_max_length)
  storage_account_output_logs_name  = "${local.storage_account_prefix}out${var.sequence_number}"
  storage_account_source_data_name  = "${local.storage_account_prefix}in${var.sequence_number}"
  storage_account_logs_name         = "${local.storage_account_prefix}log${var.sequence_number}"

  # Azure Key Vault names are limited to 24 characters and allow dashes.
  key_vault_prefix_max_length = 24 - length(var.environment) - 7
  key_vault_prefix            = trimsuffix(substr(local.workgroup_name_lower, 0, local.key_vault_prefix_max_length), "-")
  key_vault_name              = "${local.key_vault_prefix}-rh-${var.environment}-kv"

  # Standard tags for cost aggregation
  common_tags = {
    workgroup   = var.workgroup_name
    environment = var.environment
    purpose     = "rhino-client"
    managed_by  = "terraform"
  }
}
