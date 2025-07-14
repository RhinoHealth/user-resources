# Copyright 2025 Microsoft Corporation

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
# - You will need to enable Virtual Machines, Storage Accounts, Network Security Groups, and other Azure services

# --- Resource Group ------------------------------------------------------------------------------------------------------------------
# Creates a resource group to contain all resources
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location

  tags = local.common_tags
}

# --- Networking ------------------------------------------------------------------------------------------------------------------
# Creates a Virtual Network with specified address space
resource "azurerm_virtual_network" "main" {
  name                = local.vnet_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  address_space       = [var.vnet_address_space]

  tags = merge(local.common_tags, {
    Name = local.vnet_name
  })
}

# Creates a subnet within the Virtual Network
resource "azurerm_subnet" "main" {
  name                 = local.subnet_name
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_address_prefix]
}

# Creates a Network Security Group for the subnet
resource "azurerm_network_security_group" "main" {
  name                = "${local.vm_name}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Allow outbound HTTPS traffic to Rhino orchestrator
  security_rule {
    name                       = "AllowRhinoHTTPS"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Allow all outbound traffic (for internet access)
  security_rule {
    name                       = "AllowAllOutbound"
    priority                   = 200
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = merge(local.common_tags, {
    Name = "${local.vm_name}-nsg"
  })
}

# Associates the NSG with the subnet
resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}

# Creates a public IP for the NAT Gateway
resource "azurerm_public_ip" "nat" {
  name                = "${local.vnet_name}-nat-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = merge(local.common_tags, {
    Name = "${local.vnet_name}-nat-pip"
  })
}

# Creates a NAT Gateway for private subnet internet access
resource "azurerm_nat_gateway" "main" {
  name                = "${local.vnet_name}-nat"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = "Standard"

  tags = merge(local.common_tags, {
    Name = "${local.vnet_name}-nat"
  })
}

# Associates the NAT Gateway with the public IP
resource "azurerm_nat_gateway_public_ip_association" "main" {
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat.id
}

# Associates the NAT Gateway with the subnet
resource "azurerm_subnet_nat_gateway_association" "main" {
  subnet_id      = azurerm_subnet.main.id
  nat_gateway_id = azurerm_nat_gateway.main.id
}

# --- Storage ------------------------------------------------------------------------------------------------------------------
# Creates a storage account for storing outputs and logs
resource "azurerm_storage_account" "output_logs" {
  name                     = local.storage_account_output_logs_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
  }

  tags = merge(local.common_tags, {
    Name = local.storage_account_output_logs_name
  })
}

# Creates a container for output logs
resource "azurerm_storage_container" "output_logs" {
  name                  = "output-logs"
  storage_account_name  = azurerm_storage_account.output_logs.name
  container_access_type = "private"
}

# Creates a storage account for storing source data
resource "azurerm_storage_account" "source_data" {
  name                     = local.storage_account_source_data_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
  }

  tags = merge(local.common_tags, {
    Name = local.storage_account_source_data_name
  })
}

# Creates a container for source data
resource "azurerm_storage_container" "source_data" {
  name                  = "source-data"
  storage_account_name  = azurerm_storage_account.source_data.name
  container_access_type = "private"
}

# Creates a storage account for storing logs
resource "azurerm_storage_account" "logs" {
  name                     = local.storage_account_logs_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
  }

  tags = merge(local.common_tags, {
    Name = local.storage_account_logs_name
  })
}

# Creates a container for logs
resource "azurerm_storage_container" "logs" {
  name                  = "logs"
  storage_account_name  = azurerm_storage_account.logs.name
  container_access_type = "private"
}

# --- IAM & Service Accounts ------------------------------------------------------------------------------------------------------------------
# Creates a User-Assigned Managed Identity for the VM
resource "azurerm_user_assigned_identity" "vm" {
  name                = "${var.workgroup_name}-rhino-${var.environment}-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = local.common_tags
}

# Creates a role assignment for storage account access
resource "azurerm_role_assignment" "vm_storage_source_data" {
  scope                = azurerm_storage_account.source_data.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_user_assigned_identity.vm.principal_id
}

resource "azurerm_role_assignment" "vm_storage_output_logs" {
  scope                = azurerm_storage_account.output_logs.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.vm.principal_id
}

# --- Compute ------------------------------------------------------------------------------------------------------------------
# Creates a managed disk for additional storage
resource "azurerm_managed_disk" "secondary" {
  name                 = "${local.vm_name}-secondary"
  location             = azurerm_resource_group.main.location
  resource_group_name  = azurerm_resource_group.main.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = var.secondary_disk_size_gb

  tags = merge(local.common_tags, {
    Name = "${local.vm_name}-secondary"
  })
}

# Creates the Virtual Machine
resource "azurerm_linux_virtual_machine" "main" {
  name                = local.vm_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = "azureuser"

  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.main.id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = var.boot_disk_size_gb
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.vm.id]
  }

  custom_data = base64encode(templatefile("${path.module}/custom_data.sh", {
    rhino_agent_id                  = var.rhino_agent_id
    rhino_package_registry_user     = var.rhino_package_registry_user
    rhino_package_registry_password = var.rhino_package_registry_password
  }))

  tags = merge(local.common_tags, {
    Name = local.vm_name
  })
}

# Creates a network interface for the VM
resource "azurerm_network_interface" "main" {
  name                = "${local.vm_name}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.vm_name}-nic"
  })
}

# Attaches the secondary managed disk to the VM
resource "azurerm_virtual_machine_data_disk_attachment" "secondary" {
  managed_disk_id    = azurerm_managed_disk.secondary.id
  virtual_machine_id = azurerm_linux_virtual_machine.main.id
  lun                = 10
  caching            = "ReadWrite"
}

# --- Logging & Auditing ---------------------------------------------------------------------------------------------
# Creates a Log Analytics workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.workgroup_name}-rhino-${var.environment}-workspace"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.common_tags
}

# Creates a diagnostic setting for the VM
resource "azurerm_monitor_diagnostic_setting" "vm" {
  name                       = "${local.vm_name}-diagnostics"
  target_resource_id         = azurerm_linux_virtual_machine.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  log {
    category = "BootDiagnostics"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  log {
    category = "SerialConsole"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  metric {
    category = "AllMetrics"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }
}

# Creates a diagnostic setting for the storage accounts
resource "azurerm_monitor_diagnostic_setting" "storage_logs" {
  name                       = "${azurerm_storage_account.logs.name}-diagnostics"
  target_resource_id         = azurerm_storage_account.logs.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  log {
    category = "StorageRead"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  log {
    category = "StorageWrite"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  log {
    category = "StorageDelete"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }

  metric {
    category = "Transaction"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 30
    }
  }
} 