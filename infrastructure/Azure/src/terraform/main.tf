#
# Local Values and Logic
#

locals {
  # Standard tags for all resources
  standard_tags = merge({
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }, var.additional_tags)

  # Determine if we're working with landing zone
  landing_zone_enabled = var.allow_landing_zone_updates && var.confirm_landing_zone_changes
  
  # Auto-determine subnet creation logic
  create_app_subnet = coalesce(
    var.create_application_subnet,
    var.create_application_virtual_network
  )
  
  create_pe_subnet = coalesce(
    var.create_private_endpoint_subnet,
    var.create_application_virtual_network
  )
  
  # Resource naming with auto-generation
  app_resource_group_name = coalesce(
    var.application_resource_group_name,
    "rg-${random_id.deployment.hex}"
  )
  
  app_vnet_name = coalesce(
    var.application_virtual_network_name,
    "vnet-app-${random_id.deployment.hex}"
  )
  
  app_subnet_name = coalesce(
    var.application_subnet_name,
    "snet-app-${random_id.deployment.hex}"
  )
  
  pe_subnet_name = coalesce(
    var.private_endpoint_subnet_name,
    "snet-pe-${random_id.deployment.hex}"
  )
  
  storage_account_name = coalesce(
    var.storage_account_name,
    "st${random_id.deployment.hex}"
  )
}

#
# Data Sources - Current Context
#

data "azurerm_client_config" "current" {}

resource "random_id" "deployment" {
  byte_length = 4
}

#
# Landing Zone Connections - Establish links to existing shared infrastructure
#

# Get reference to existing landing zone VNet
data "azurerm_virtual_network" "landing_zone" {
  count               = local.landing_zone_enabled ? 1 : 0
  name                = var.landing_zone_virtual_network_name
  resource_group_name = var.landing_zone_virtual_network_resource_group
  provider            = azurerm.landing_zone
}

# Get reference to landing zone private DNS resource group (if DNS updates enabled)
data "azurerm_resource_group" "landing_zone_dns" {
  count    = var.apply_landing_zone_private_dns_updates ? 1 : 0
  name     = var.landing_zone_private_dns_resource_group
  provider = azurerm.landing_zone
}

#
# Application Resource Group
#

resource "azurerm_resource_group" "application" {
  count    = var.create_application_resource_group ? 1 : 0
  name     = local.app_resource_group_name
  location = var.application_location
  
  tags = local.standard_tags
}

# Reference to application resource group (created or existing)
data "azurerm_resource_group" "application" {
  count = var.create_application_resource_group ? 0 : 1
  name  = var.application_resource_group_name
}

locals {
  # Unified reference to the application resource group
  app_resource_group = var.create_application_resource_group ? azurerm_resource_group.application[0] : data.azurerm_resource_group.application[0]
}

#
# Application Virtual Network
#

resource "azurerm_virtual_network" "application" {
  count               = var.create_application_virtual_network ? 1 : 0
  name                = local.app_vnet_name
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name
  address_space       = var.application_virtual_network_address_space
  
  tags = local.standard_tags
}

# Reference to application VNet (created or existing)
data "azurerm_virtual_network" "application" {
  count               = var.create_application_virtual_network ? 0 : 1
  name                = var.application_virtual_network_name
  resource_group_name = coalesce(var.application_virtual_network_resource_group, local.app_resource_group.name)
}

locals {
  # Unified reference to the application VNet
  app_vnet = var.create_application_virtual_network ? azurerm_virtual_network.application[0] : data.azurerm_virtual_network.application[0]
}

#
# VNet Peering to Landing Zone (if enabled)
#

resource "azurerm_virtual_network_peering" "app_to_landing_zone" {
  count                        = var.enable_vnet_peering_to_landing_zone && local.landing_zone_enabled ? 1 : 0
  name                         = "peer-${local.app_vnet.name}-to-${data.azurerm_virtual_network.landing_zone[0].name}"
  resource_group_name          = local.app_resource_group.name
  virtual_network_name         = local.app_vnet.name
  remote_virtual_network_id    = data.azurerm_virtual_network.landing_zone[0].id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = false  # Spoke doesn't provide gateway
  use_remote_gateways          = var.landing_zone_has_gateway && var.enable_application_to_onprem_connectivity

  # Ensure VNet and subnets are fully created before peering
  depends_on = [
    azurerm_virtual_network.application,
    azurerm_subnet.application,
    azurerm_subnet.private_endpoint
  ]  
}

resource "azurerm_virtual_network_peering" "landing_zone_to_app" {
  count                        = var.enable_vnet_peering_to_landing_zone && local.landing_zone_enabled ? 1 : 0
  name                         = "peer-${data.azurerm_virtual_network.landing_zone[0].name}-to-${local.app_vnet.name}"
  resource_group_name          = var.landing_zone_virtual_network_resource_group
  virtual_network_name         = var.landing_zone_virtual_network_name
  remote_virtual_network_id    = local.app_vnet.id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = var.landing_zone_has_gateway && var.enable_application_to_onprem_connectivity  # Hub shares its gateway
  use_remote_gateways          = false  # Hub doesn't use remote gateways
  provider                     = azurerm.landing_zone

  # Ensure the first peering is complete to avoid race conditions
  depends_on = [azurerm_virtual_network_peering.app_to_landing_zone]
}

#
# Application Subnet
#

resource "azurerm_subnet" "application" {
  count                = local.create_app_subnet ? 1 : 0
  name                 = local.app_subnet_name
  resource_group_name  = coalesce(var.application_virtual_network_resource_group, local.app_resource_group.name)  # Fixed
  virtual_network_name = local.app_vnet.name
  address_prefixes     = [var.application_subnet_address_prefix]
}

# Reference to application subnet (created or existing)
data "azurerm_subnet" "application" {
  count                = local.create_app_subnet ? 0 : 1
  name                 = var.application_subnet_name
  virtual_network_name = local.app_vnet.name
  resource_group_name  = coalesce(var.application_virtual_network_resource_group, local.app_resource_group.name)
}

locals {
  # Unified reference to the application subnet
  app_subnet = local.create_app_subnet ? azurerm_subnet.application[0] : data.azurerm_subnet.application[0]
}

#
# Application Subnet Network Security Group
#

resource "azurerm_network_security_group" "application" {
  count               = local.create_app_subnet && var.create_application_subnet_nsg ? 1 : 0
  name                = coalesce(var.application_subnet_nsg_name, "nsg-${local.app_subnet_name}")
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name

  tags = local.standard_tags
}

resource "azurerm_subnet_network_security_group_association" "application" {
  count                     = local.create_app_subnet && var.create_application_subnet_nsg ? 1 : 0
  subnet_id                 = azurerm_subnet.application[0].id
  network_security_group_id = azurerm_network_security_group.application[0].id
}

#
# Application Subnet Route Table
#

resource "azurerm_route_table" "application" {
  count               = local.create_app_subnet && var.create_application_subnet_route_table ? 1 : 0
  name                = coalesce(var.application_subnet_route_table_name, "rt-${local.app_subnet_name}")
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name

  tags = local.standard_tags
}

resource "azurerm_route" "application" {
  count                  = local.create_app_subnet && var.create_application_subnet_route_table ? length(var.application_subnet_routes) : 0
  name                   = var.application_subnet_routes[count.index].name
  resource_group_name    = local.app_resource_group.name
  route_table_name       = azurerm_route_table.application[0].name
  address_prefix         = var.application_subnet_routes[count.index].address_prefix
  next_hop_type          = var.application_subnet_routes[count.index].next_hop_type
  next_hop_in_ip_address = var.application_subnet_routes[count.index].next_hop_in_ip_address
}

resource "azurerm_subnet_route_table_association" "application" {
  count          = local.create_app_subnet && var.create_application_subnet_route_table ? 1 : 0
  subnet_id      = azurerm_subnet.application[0].id
  route_table_id = azurerm_route_table.application[0].id
}

#
# Private Endpoint Subnet
#

resource "azurerm_subnet" "private_endpoint" {
  count                = local.create_pe_subnet ? 1 : 0
  name                 = local.pe_subnet_name
  resource_group_name  = coalesce(var.application_virtual_network_resource_group, local.app_resource_group.name)  # Fixed
  virtual_network_name = local.app_vnet.name
  address_prefixes     = [var.private_endpoint_subnet_address_prefix]
}

# Reference to private endpoint subnet (created or existing)
data "azurerm_subnet" "private_endpoint" {
  count                = local.create_pe_subnet ? 0 : 1
  name                 = var.private_endpoint_subnet_name
  virtual_network_name = local.app_vnet.name
  resource_group_name  = coalesce(var.application_virtual_network_resource_group, local.app_resource_group.name)
}

locals {
  # Unified reference to the private endpoint subnet
  pe_subnet = local.create_pe_subnet ? azurerm_subnet.private_endpoint[0] : data.azurerm_subnet.private_endpoint[0]
}

#
# Private Endpoint Subnet Network Security Group
#

resource "azurerm_network_security_group" "private_endpoint" {
  count               = local.create_pe_subnet && var.create_private_endpoint_subnet_nsg ? 1 : 0
  name                = coalesce(var.private_endpoint_subnet_nsg_name, "nsg-${local.pe_subnet_name}")
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name

  tags = local.standard_tags
}

resource "azurerm_subnet_network_security_group_association" "private_endpoint" {
  count                     = local.create_pe_subnet && var.create_private_endpoint_subnet_nsg ? 1 : 0
  subnet_id                 = azurerm_subnet.private_endpoint[0].id
  network_security_group_id = azurerm_network_security_group.private_endpoint[0].id
}

#
# Storage Account (mandatory)
#

resource "azurerm_storage_account" "main" {
  name                     = local.storage_account_name
  resource_group_name      = local.app_resource_group.name
  location                 = local.app_resource_group.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type
  account_kind             = var.storage_account_kind
  access_tier              = var.storage_account_access_tier

  # Security settings - enforce private access
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false  # Force private endpoint usage
  
  # Data Lake Gen2 support
  is_hns_enabled = var.enable_data_lake_gen2

  tags = local.standard_tags
}

#
# Storage Account Private Endpoint (mandatory)
#

resource "azurerm_private_endpoint" "storage" {
  for_each            = toset(var.storage_private_endpoint_subresource_names)
  name                = length(var.storage_private_endpoint_subresource_names) > 1 ? (
    var.storage_private_endpoint_name != null ? "${var.storage_private_endpoint_name}-${each.key}" : "pe-${azurerm_storage_account.main.name}-${each.key}"
  ) : (
    coalesce(var.storage_private_endpoint_name, "pe-${azurerm_storage_account.main.name}-${each.key}")
  )
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name
  subnet_id           = local.pe_subnet.id

  private_service_connection {
    name                           = "psc-${azurerm_storage_account.main.name}-${each.key}"
    private_connection_resource_id = azurerm_storage_account.main.id
    subresource_names              = [each.key]
    is_manual_connection           = false
  }

  # Single DNS Zone Group - chooses application OR landing zone DNS
  dynamic "private_dns_zone_group" {
    for_each = (local.create_application_dns || local.create_landing_zone_dns) ? [1] : []
    content {
      name = "pdz-group-${each.key}"
      private_dns_zone_ids = [
        local.create_application_dns ? azurerm_private_dns_zone.storage_application[each.key].id : (
          var.landing_zone_private_dns_zones_exist 
          ? data.azurerm_private_dns_zone.storage_landing_zone_existing[each.key].id
          : azurerm_private_dns_zone.storage_landing_zone[each.key].id
        )
      ]
    }
  } 

  tags = local.standard_tags
}

#
# Private DNS Zones for Storage Services
#

locals {
  # DNS zone mappings for storage services (we define both, but only create what user selected)
  storage_dns_zone_names = {
    blob = "privatelink.blob.core.windows.net"
    dfs  = "privatelink.dfs.core.windows.net"
  }
  
  # Determine DNS management approach - either landing zone OR application, never both
  create_landing_zone_dns = local.landing_zone_enabled && var.apply_landing_zone_private_dns_updates
  create_application_dns = !local.create_landing_zone_dns && var.apply_application_private_dns
  
  # Only create DNS zones for the services the user actually selected
  storage_dns_zones_to_create = (local.create_application_dns || local.create_landing_zone_dns) ? {
    for service in var.storage_private_endpoint_subresource_names :
    service => local.storage_dns_zone_names[service]
    if contains(keys(local.storage_dns_zone_names), service)
  } : {}
}

# Create DNS zones in application resource group
resource "azurerm_private_dns_zone" "storage_application" {
  for_each            = local.create_application_dns ? local.storage_dns_zones_to_create : {}
  name                = each.value
  resource_group_name = local.app_resource_group.name

  tags = local.standard_tags
}

# Data sources to reference existing DNS zones in landing zone (when they exist)
data "azurerm_private_dns_zone" "storage_landing_zone_existing" {
  for_each            = local.create_landing_zone_dns && var.landing_zone_private_dns_zones_exist ? local.storage_dns_zones_to_create : {}
  name                = each.value
  resource_group_name = var.landing_zone_private_dns_resource_group
  provider            = azurerm.landing_zone
}

# Create DNS zones in landing zone (only when they don't already exist)
resource "azurerm_private_dns_zone" "storage_landing_zone" {
  for_each            = local.create_landing_zone_dns && !var.landing_zone_private_dns_zones_exist ? local.storage_dns_zones_to_create : {}
  name                = each.value
  resource_group_name = var.landing_zone_private_dns_resource_group
  provider            = azurerm.landing_zone

  tags = local.standard_tags
}

# Link application DNS zones to application VNet
resource "azurerm_private_dns_zone_virtual_network_link" "storage_to_app_vnet" {
  for_each = local.create_application_dns ? local.storage_dns_zones_to_create : {}
  
  name                  = "pdz-link-${local.app_vnet.name}-${replace(each.key, ".", "-")}"
  resource_group_name   = local.app_resource_group.name
  private_dns_zone_name = azurerm_private_dns_zone.storage_application[each.key].name
  virtual_network_id    = local.app_vnet.id
  registration_enabled  = false

  tags = local.standard_tags
}

# Link landing zone DNS zones to hub VNet
resource "azurerm_private_dns_zone_virtual_network_link" "storage_landing_zone_to_hub_vnet" {
  for_each = var.enable_vnet_peering_to_landing_zone && local.landing_zone_enabled && local.create_landing_zone_dns ? local.storage_dns_zones_to_create : {}
  
  name                  = "pdz-link-hub-${replace(each.key, ".", "-")}"
  resource_group_name   = var.landing_zone_private_dns_resource_group
  private_dns_zone_name = (
    var.landing_zone_private_dns_zones_exist 
    ? data.azurerm_private_dns_zone.storage_landing_zone_existing[each.key].name
    : azurerm_private_dns_zone.storage_landing_zone[each.key].name
  )
  virtual_network_id    = data.azurerm_virtual_network.landing_zone[0].id
  registration_enabled  = false
  provider              = azurerm.landing_zone

  tags = local.standard_tags
}

#
# Virtual Machine and Supporting Resources
#

# VM Local Values
locals {
  vm_name = coalesce(var.virtual_machine_name, "vm-${random_id.deployment.hex}")
  
  # Determine if this is a GPU-enabled VM
  is_gpu_enabled = can(regex("^Standard_N[CDGV]", var.virtual_machine_size))
}

# Network Interface for VM
resource "azurerm_network_interface" "main" {
  name                = "${local.vm_name}-nic"
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = local.app_subnet.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = local.standard_tags
}

# Data Disk (optional)
resource "azurerm_managed_disk" "main" {
  count = var.create_data_disk ? 1 : 0
  
  name                 = "${local.vm_name}-data-disk"
  location             = local.app_resource_group.location
  resource_group_name  = local.app_resource_group.name
  storage_account_type = var.data_disk_type
  create_option        = "Empty"
  disk_size_gb         = var.data_disk_size_gb

  tags = local.standard_tags
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "main" {
  name                = local.vm_name
  location            = local.app_resource_group.location
  resource_group_name = local.app_resource_group.name
  size                = var.virtual_machine_size
  admin_username      = var.admin_username
  admin_password      = var.authentication_type == "Password" ? var.admin_password : null

  disable_password_authentication = var.authentication_type == "SSH"

  network_interface_ids = [
    azurerm_network_interface.main.id,
  ]

  dynamic "admin_ssh_key" {
    for_each = var.authentication_type == "SSH" && var.ssh_public_key != null ? [1] : []
    content {
      username   = var.admin_username
      public_key = var.ssh_public_key
    }
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.os_disk_type
    disk_size_gb         = var.os_disk_size_gb
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  identity {
    type = "SystemAssigned" 
  }

  tags = local.standard_tags
}

# Data Disk Attachment
resource "azurerm_virtual_machine_data_disk_attachment" "main" {
  count = var.create_data_disk ? 1 : 0
  
  managed_disk_id    = azurerm_managed_disk.main[0].id
  virtual_machine_id = azurerm_linux_virtual_machine.main.id
  lun                = "1"
  caching            = var.data_disk_caching
}

# GPU Driver Extension (if GPU VM and drivers requested)
resource "azurerm_virtual_machine_extension" "nvidia_gpu_driver" {
  count = local.is_gpu_enabled && var.install_gpu_drivers ? 1 : 0
  
  name                 = "${local.vm_name}-nvidia-gpu-driver"
  virtual_machine_id   = azurerm_linux_virtual_machine.main.id
  publisher            = "Microsoft.HpcCompute"
  type                 = "NvidiaGpuDriverLinux"
  type_handler_version = "1.9"
  
  settings = jsonencode({
    "DriverType" = var.gpu_driver_type
  })

  tags = local.standard_tags
}