variable "project_name" {
  type        = string
  description = <<-EOT
    Name of the project or application.
    
    Used for resource naming and tagging across all resources.
    Should be short and descriptive.
    
    Example: "myapp", "dataplatform", "webapi"
  EOT

  validation {
    condition = length(var.project_name) >= 2 && length(var.project_name) <= 20
    error_message = "Project name must be between 2 and 20 characters."
  }
}

variable "environment" {
  type        = string
  description = <<-EOT
    Environment designation for the deployment.
    
    Used for resource naming and tagging.
    
    Example: "dev", "test", "staging", "prod"
  EOT

  validation {
    condition = contains(["dev", "test", "staging", "prod", "sandbox", "demo"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, prod, sandbox, demo."
  }
}

variable "additional_tags" {
  type        = map(string)
  default     = {}
  description = <<-EOT
    Additional tags to apply to all resources.
    
    These will be merged with standard tags (Project, Environment, ManagedBy).
    
    Example: {
      CostCenter = "12345"
      Owner      = "team@company.com"
    }
  EOT
}

#
# Landing Zone Infrastructure Control
# Controls existing network resources that may be shared across multiple applications
#

variable "allow_landing_zone_updates" {
  type        = bool
  default     = false
  description = <<-EOT
    Allow Terraform to update existing landing zone topology (VNets, subnets, NSGs, route tables).

    - true:  Terraform can modify existing network resources and create new ones as needed
    - false: Terraform will only use existing network resources without modification

    IMPORTANT: Setting this to true may impact existing workloads connected to the same landing zone.
    Only enable this if you understand the potential impact on your landing zone topology.
  EOT
}

variable "confirm_landing_zone_changes" {
  type        = bool
  default     = false
  description = <<-EOT
    Confirmation that you understand the impact of landing zone topology changes.
    Required to be true when allow_landing_zone_updates is true.
    
    This variable serves as a safety check to ensure you've considered:
    - Impact on existing VMs and services
    - Routing changes that might affect connectivity
    - NSG rule modifications that might affect security
    - Subnet changes that might affect IP allocation
  EOT

  validation {
    condition     = !var.allow_landing_zone_updates || (var.allow_landing_zone_updates && var.confirm_landing_zone_changes)
    error_message = "When allow_landing_zone_updates is true, confirm_landing_zone_changes must also be true to acknowledge you understand the potential impact."
  }
}

variable "landing_zone_subscription_id" {
  type        = string
  default     = null
  description = <<-EOT
    Azure subscription ID where the existing landing zone resources are deployed.
    
    Required when both allow_landing_zone_updates and confirm_landing_zone_changes are true.
    This is the connectivity or hub subscription in enterprise architectures.
    
    Example: "12345678-1234-1234-1234-123456789abc"
  EOT

  validation {
    condition = !(var.allow_landing_zone_updates && var.confirm_landing_zone_changes) || (var.landing_zone_subscription_id != null && can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.landing_zone_subscription_id)))
    error_message = "When allow_landing_zone_updates and confirm_landing_zone_changes are both true, landing_zone_subscription_id must be a valid Azure subscription GUID."
  }
}

variable "landing_zone_virtual_network_resource_group" {
  type        = string
  default     = null
  description = <<-EOT
    Resource group name containing the existing landing zone virtual network.
    
    Required when both allow_landing_zone_updates and confirm_landing_zone_changes are true.
    This resource group must exist in the landing zone subscription.
    
    Example: "rg-network-hub-prod"
  EOT

  validation {
    condition = !(var.allow_landing_zone_updates && var.confirm_landing_zone_changes) || (var.landing_zone_virtual_network_resource_group != null && length(var.landing_zone_virtual_network_resource_group) >= 1)
    error_message = "When allow_landing_zone_updates and confirm_landing_zone_changes are both true, landing_zone_virtual_network_resource_group must be specified."
  }
}

variable "landing_zone_virtual_network_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the existing virtual network in the landing zone subscription.
    
    Required when both allow_landing_zone_updates and confirm_landing_zone_changes are true.
    This is the hub VNet or shared network infrastructure where application subnets will be created.
    
    This VNet must already exist in the specified resource group.
    
    Example: "vnet-hub-prod-eastus2"
  EOT

  validation {
    condition = !(var.allow_landing_zone_updates && var.confirm_landing_zone_changes) || (var.landing_zone_virtual_network_name != null && length(var.landing_zone_virtual_network_name) >= 2)
    error_message = "When allow_landing_zone_updates and confirm_landing_zone_changes are both true, landing_zone_virtual_network_name must be at least 2 characters long."
  }
}

variable "apply_landing_zone_private_dns_updates" {
  type        = bool
  default     = false
  description = <<-EOT
    Apply updates to private DNS zones in the landing zone.
    
    - true:  Terraform will create DNS records and link VNets to existing private DNS zones
    - false: Terraform will not modify private DNS zones in the landing zone
    
    This is separate from allow_landing_zone_updates to provide granular control over DNS changes.
    DNS changes can affect name resolution across the entire landing zone.
  EOT
}

#
# Private DNS Zone Configuration
# Controls where private DNS zones are created and managed
#

variable "apply_application_private_dns" {
  type        = bool
  default     = true
  description = <<-EOT
    Create and manage private DNS zones in the application resource group.
    
    - true:  Create private DNS zones in application resource group and link to VNets
    - false: Do not create private DNS zones in application resource group
    
    This is for standalone deployments or when DNS is managed separately.
    Cannot be true if apply_landing_zone_private_dns_updates is true.
  EOT

  validation {
    condition = !var.apply_application_private_dns || !var.apply_landing_zone_private_dns_updates
    error_message = "Cannot have both apply_application_private_dns and apply_landing_zone_private_dns_updates set to true. Choose one DNS management approach."
  }
}

variable "landing_zone_private_dns_resource_group" {
  type        = string
  default     = null
  description = <<-EOT
    Resource group name containing the private DNS zones in the landing zone.
    
    Required when apply_landing_zone_private_dns_updates is true.
    This resource group must exist in the landing zone subscription and contain
    the private DNS zones for services like privatelink.file.core.windows.net.
    
    Example: "rg-dns-hub-prod"
  EOT

  validation {
    condition = !var.apply_landing_zone_private_dns_updates || (var.landing_zone_private_dns_resource_group != null && length(var.landing_zone_private_dns_resource_group) >= 1)
    error_message = "When apply_landing_zone_private_dns_updates is true, landing_zone_private_dns_resource_group must be specified."
  }
}

variable "landing_zone_private_dns_zones_exist" {
  description = <<-EOT
    Whether private DNS zones for storage services already exist in the landing zone.
    When true, will use existing zones instead of creating new ones.
    Only applies when apply_landing_zone_private_dns_updates is true.
  EOT
  type        = bool
  default     = false
  
  validation {
    condition     = !var.landing_zone_private_dns_zones_exist || var.apply_landing_zone_private_dns_updates
    error_message = "landing_zone_private_dns_zones_exist can only be true when apply_landing_zone_private_dns_updates is also true."
  }
}

#
# Application Infrastructure Control
# Controls application resources that may be in a different subscription from the landing zone
#

variable "application_subscription_id" {
  type        = string
  description = <<-EOT
    Azure subscription ID where the application resources will be deployed.
    
    This is typically a separate subscription from the landing zone for:
    - Cost isolation and management
    - Security and access control boundaries
    - Compliance and governance requirements
    
    Example: "87654321-4321-4321-4321-cba987654321"
  EOT

  validation {
    condition = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.application_subscription_id))
    error_message = "Application subscription ID must be a valid Azure subscription GUID format."
  }
}

variable "application_location" {
  type        = string
  description = <<-EOT
    Azure region where application resources will be deployed.
    
    This should typically match or be close to the landing zone region for optimal networking.
    
    Example: "East US 2", "West Europe", "Southeast Asia"
  EOT

  validation {
    condition = length(var.application_location) > 0
    error_message = "Location must be specified."
  }
}

variable "create_application_resource_group" {
  type        = bool
  default     = true
  description = <<-EOT
    Create a new resource group for application resources.
    
    - true:  Create a new resource group in the application subscription
    - false: Use an existing resource group (requires application_resource_group_name)
  EOT
}

variable "application_resource_group_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the resource group for application resources.
    
    - If create_application_resource_group is true: Name for the new resource group
    - If create_application_resource_group is false: Name of existing resource group
    
    If null and create_application_resource_group is true, will be auto-generated.
    
    Example: "rg-myapp-prod-eastus2"
  EOT

  validation {
    condition = var.create_application_resource_group || (var.application_resource_group_name != null && length(var.application_resource_group_name) >= 1)
    error_message = "When create_application_resource_group is false, application_resource_group_name must be specified."
  }
}

variable "create_application_virtual_network" {
  type        = bool
  default     = true
  description = <<-EOT
    Create a new virtual network for application resources.
    
    - true:  Create a new VNet in the application subscription (spoke VNet pattern)
    - false: Use existing VNet or deploy directly into landing zone VNet
    
    When true, this VNet can be peered with the landing zone VNet for connectivity.
  EOT
}

variable "application_virtual_network_resource_group" {
  type        = string
  default     = null
  description = <<-EOT
    Resource group containing the existing virtual network.
    
    Only used when create_application_virtual_network is false.
    If null, will use the application resource group.
    
    This allows using VNets from different resource groups than where 
    the application resources are being deployed.
    
    Example: "rg-shared-network-prod"
  EOT

  validation {
    condition = var.create_application_virtual_network || var.application_virtual_network_resource_group == null || length(var.application_virtual_network_resource_group) >= 1
    error_message = "When specified, application_virtual_network_resource_group must not be empty."
  }
}

variable "application_virtual_network_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the virtual network for application resources.
    
    - If create_application_virtual_network is true: Name for the new VNet
    - If create_application_virtual_network is false: Name of existing VNet to use
    
    If null and create_application_virtual_network is true, will be auto-generated.
    
    Example: "vnet-myapp-spoke-eastus2"
  EOT

  validation {
    condition = var.create_application_virtual_network || (var.application_virtual_network_name != null && length(var.application_virtual_network_name) >= 2)
    error_message = "When create_application_virtual_network is false, application_virtual_network_name must be specified."
  }
}

variable "application_virtual_network_address_space" {
  type        = list(string)
  default     = ["10.1.0.0/16"]
  description = <<-EOT
    Address space for the application virtual network.
    
    Only used when create_application_virtual_network is true.
    Should not overlap with landing zone VNet address space if peering is planned.
    
    Example: ["10.1.0.0/16"] or ["172.16.0.0/12"]
  EOT

  validation {
    condition = length(var.application_virtual_network_address_space) > 0
    error_message = "At least one address space must be specified for the application virtual network."
  }
}

variable "enable_vnet_peering_to_landing_zone" {
  type        = bool
  default     = false
  description = <<-EOT
    Enable VNet peering between application VNet and landing zone VNet.
    
    Requires:
    - create_application_virtual_network = true
    - Landing zone variables properly configured
    - Non-overlapping address spaces
    - Appropriate permissions in both subscriptions
    
    This creates a hub-and-spoke network topology.
  EOT

  validation {
    condition = !var.enable_vnet_peering_to_landing_zone || var.create_application_virtual_network
    error_message = "VNet peering requires create_application_virtual_network to be true."
  }
}

variable "landing_zone_has_gateway" {
  type        = bool
  default     = false
  description = <<-EOT
    Indicates if the landing zone (hub) VNet has a VPN Gateway or ExpressRoute Gateway.
    
    When true:
    - Landing zone will allow gateway transit to spoke
    - Spoke will use remote gateway from hub
    - Enables on-premises connectivity through landing zone    
    
    Set to true if the landing zone has VPN or ExpressRoute connectivity to on-premises.
  EOT
}

variable "enable_application_to_onprem_connectivity" {
  type        = bool
  default     = true
  description = <<-EOT
    Enable connectivity from spoke to on-premises networks through the hub gateway.
    
    Only applies when landing_zone_has_gateway is true and VNet peering is enabled.
    Allows resources in the spoke to reach on-premises networks.
  EOT
}

#
# Application Subnet Configuration
#

variable "create_application_subnet" {
  type        = bool
  default     = null
  description = <<-EOT
    Create a new subnet for application resources (VMs, etc.).
    
    - true:  Create a new application subnet
    - false: Use an existing application subnet (requires application_subnet_name)
    - null:  Auto-determine based on create_application_virtual_network
             (true if creating new VNet, false if using existing VNet)
  EOT
}

variable "application_subnet_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the application subnet.
    
    - If create_application_subnet is true: Name for the new subnet
    - If create_application_subnet is false: Name of existing subnet to use
    
    If null and create_application_subnet is true, will be auto-generated.
    
    Example: "snet-app-prod" or "snet-myapp-compute"
  EOT

  validation {
    condition = var.create_application_subnet != false || (var.application_subnet_name != null && length(var.application_subnet_name) >= 1)
    error_message = "When create_application_subnet is false, application_subnet_name must be specified."
  }
}

variable "application_subnet_address_prefix" {
  type        = string
  default     = "10.1.1.0/24"
  description = <<-EOT
    Address prefix for the application subnet.
    
    Only used when create_application_subnet is true.
    Must be within the VNet address space.
    
    Example: "10.1.1.0/24" or "172.16.1.0/24"
  EOT
}

#
# Application Subnet Network Security Group
#

variable "create_application_subnet_nsg" {
  type        = bool
  default     = true
  description = <<-EOT
    Create a network security group for the application subnet.
    
    - true:  Create a new NSG and associate it with the application subnet
    - false: Do not create or associate an NSG with the application subnet
    
    Only applies when create_application_subnet is true.
  EOT
}

variable "application_subnet_nsg_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the network security group for the application subnet.
    
    Only used when create_application_subnet_nsg is true.
    If null, will be auto-generated.
    
    Example: "nsg-app-prod" or "nsg-myapp-compute"
  EOT
}

#
# Application Subnet Route Table
#

variable "create_application_subnet_route_table" {
  type        = bool
  default     = false
  description = <<-EOT
    Create a route table for the application subnet.
    
    - true:  Create a new route table and associate it with the application subnet
    - false: Do not create or associate a route table with the application subnet
    
    Only applies when create_application_subnet is true.
  EOT
}

variable "application_subnet_route_table_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the route table for the application subnet.
    
    Only used when create_application_subnet_route_table is true.
    If null, will be auto-generated.
    
    Example: "rt-app-prod" or "rt-myapp-compute"
  EOT
}

variable "application_subnet_routes" {
  type = list(object({
    name                   = string
    address_prefix         = string
    next_hop_type          = string
    next_hop_in_ip_address = optional(string)
  }))
  default     = []
  description = <<-EOT
    Routes to add to the application subnet route table.
    
    Only used when create_application_subnet_route_table is true.
    
    Example:
    [
      {
        name           = "route-to-firewall"
        address_prefix = "0.0.0.0/0"
        next_hop_type  = "VirtualAppliance"
        next_hop_in_ip_address = "10.0.1.4"
      },
      {
        name           = "route-to-internet"
        address_prefix = "0.0.0.0/0"
        next_hop_type  = "Internet"
      }
    ]
  EOT
}

#
# Private Endpoint Subnet Configuration
#

variable "create_private_endpoint_subnet" {
  type        = bool
  default     = null
  description = <<-EOT
    Create a new subnet for private endpoints.
    
    - true:  Create a new private endpoint subnet
    - false: Use an existing private endpoint subnet (requires private_endpoint_subnet_name)
    - null:  Auto-determine based on create_application_virtual_network
             (true if creating new VNet, false if using existing VNet)
  EOT
}

variable "private_endpoint_subnet_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the private endpoint subnet.
    
    - If create_private_endpoint_subnet is true: Name for the new subnet
    - If create_private_endpoint_subnet is false: Name of existing subnet to use
    
    If null and create_private_endpoint_subnet is true, will be auto-generated.
    
    Example: "snet-pe-prod" or "snet-privateendpoints"
  EOT

  validation {
    condition = var.create_private_endpoint_subnet != false || var.private_endpoint_subnet_name == null || (var.private_endpoint_subnet_name != null && length(var.private_endpoint_subnet_name) >= 1)
    error_message = "When create_private_endpoint_subnet is false, private_endpoint_subnet_name must be specified if provided."
  }
}

variable "private_endpoint_subnet_address_prefix" {
  type        = string
  default     = "10.1.2.0/24"
  description = <<-EOT
    Address prefix for the private endpoint subnet.
    
    Only used when create_private_endpoint_subnet is true.
    Must be within the VNet address space and not overlap with application subnet.
    
    Example: "10.1.2.0/24" or "172.16.2.0/24"
  EOT
}

#
# Private Endpoint Subnet Network Security Group
#

variable "create_private_endpoint_subnet_nsg" {
  type        = bool
  default     = true
  description = <<-EOT
    Create a network security group for the private endpoint subnet.
    
    - true:  Create a new NSG and associate it with the private endpoint subnet
    - false: Do not create or associate an NSG with the private endpoint subnet
    
    Only applies when create_private_endpoint_subnet is true.
    Private endpoint subnets typically need minimal NSG rules.
  EOT
}

variable "private_endpoint_subnet_nsg_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the network security group for the private endpoint subnet.
    
    Only used when create_private_endpoint_subnet_nsg is true.
    If null, will be auto-generated.
    
    Example: "nsg-pe-prod" or "nsg-privateendpoints"
  EOT
}

#
# Subnet Auto-Configuration Logic
#

locals {
  # Auto-determine subnet creation logic
  _create_app_subnet = coalesce(
    var.create_application_subnet,
    var.create_application_virtual_network  # If creating new VNet, create subnet
  )
  
  _create_pe_subnet = coalesce(
    var.create_private_endpoint_subnet,
    var.create_application_virtual_network  # If creating new VNet, create PE subnet
  )
}

#
# Storage Account Configuration
# Storage account with private endpoint is required for this deployment
#

variable "storage_account_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the storage account.
    
    Must be globally unique, 3-24 characters, lowercase letters and numbers only.
    If null, will be auto-generated with random suffix.
    
    Example: "mystorageacct001"
  EOT

  validation {
    condition = var.storage_account_name == null || can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters of lowercase letters and numbers only."
  }
}

variable "storage_account_tier" {
  type        = string
  default     = "Standard"
  description = <<-EOT
    Performance tier for the storage account.
    
    Valid values: "Standard", "Premium"
  EOT

  validation {
    condition = contains(["Standard", "Premium"], var.storage_account_tier)
    error_message = "Storage account tier must be either 'Standard' or 'Premium'."
  }
}

variable "storage_account_replication_type" {
  type        = string
  default     = "LRS"
  description = <<-EOT
    Replication type for the storage account.
    
    Valid values: "LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"
  EOT

  validation {
    condition = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.storage_account_replication_type)
    error_message = "Storage account replication type must be one of: LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS."
  }
}

variable "storage_account_kind" {
  type        = string
  default     = "StorageV2"
  description = <<-EOT
    Kind of storage account.
    
    Valid values: 
    - "StorageV2": General-purpose v2 (supports blob and Data Lake Gen2)
    - "BlobStorage": Blob-only storage account
    - "BlockBlobStorage": Premium block blob storage
    
    StorageV2 is recommended for Data Lake Gen2 support.
  EOT

  validation {
    condition = contains(["StorageV2", "BlobStorage", "BlockBlobStorage"], var.storage_account_kind)
    error_message = "Storage account kind must be one of: StorageV2, BlobStorage, BlockBlobStorage."
  }
}

variable "storage_account_access_tier" {
  type        = string
  default     = "Hot"
  description = <<-EOT
    Access tier for the storage account.
    
    Valid values: "Hot", "Cool"
  EOT

  validation {
    condition = contains(["Hot", "Cool"], var.storage_account_access_tier)
    error_message = "Storage account access tier must be either 'Hot' or 'Cool'."
  }
}

variable "enable_data_lake_gen2" {
  type        = bool
  default     = false
  description = <<-EOT
    Enable Azure Data Lake Storage Gen2 hierarchical namespace.
    
    - true:  Enable Data Lake Gen2 features (requires StorageV2)
    - false: Standard blob storage only
    
    When enabled, allows for big data analytics workloads and file system semantics.
  EOT

  validation {
    condition = !var.enable_data_lake_gen2 || var.storage_account_kind == "StorageV2"
    error_message = "Data Lake Gen2 requires storage_account_kind to be 'StorageV2'."
  }

  validation {
    condition = !var.enable_data_lake_gen2 || var.storage_account_tier == "Standard"
    error_message = "Data Lake Gen2 (hierarchical namespace) is only supported with Standard storage tier, not Premium. Either set storage_account_tier to 'Standard' or disable Data Lake Gen2."
  }  
}

#
# Storage Account Private Endpoint Configuration
# Private endpoint is always created for secure access
#

variable "storage_private_endpoint_name" {
  type        = string
  default     = null
  description = <<-EOT
    Name of the storage account private endpoint.
    
    If null, will be auto-generated.
    
    Example: "pe-mystorageacct001"
  EOT
}

variable "storage_private_endpoint_subresource_names" {
  type        = list(string)
  default     = ["blob"]
  description = <<-EOT
    Storage account subresources to create private endpoints for.
    
    Valid values: 
    - "blob": Blob storage access
    - "dfs": Data Lake Storage Gen2 access (only when enable_data_lake_gen2 = true)
    
    Example: ["blob"] for blob only, or ["blob", "dfs"] for both blob and Data Lake
  EOT

  validation {
    condition = length(var.storage_private_endpoint_subresource_names) > 0 && alltrue([
      for subresource in var.storage_private_endpoint_subresource_names :
      contains(["blob", "dfs"], subresource)
    ])
    error_message = "Storage private endpoint subresource names must be a non-empty list containing only: blob, dfs."
  }

  validation {
    condition = !contains(var.storage_private_endpoint_subresource_names, "dfs") || var.enable_data_lake_gen2
    error_message = "DFS subresource requires enable_data_lake_gen2 to be true."
  }
}

#
# Virtual Machine Configuration
#

variable "virtual_machine_name" {
  description = "Name of the virtual machine"
  type        = string
  default     = "default-vm"
}

variable "virtual_machine_size" {
  description = "SKU/size of the virtual machine"
  type        = string
  default     = "Standard_D4s_v5"
  
  validation {
    condition = can(regex("^Standard_", var.virtual_machine_size))
    error_message = "VM size must be a valid Azure VM SKU starting with 'Standard_'."
  }
}

variable "admin_username" {
  description = "Administrator username for the VM"
  type        = string
  default     = "azureuser"
  
  validation {
    condition = length(var.admin_username) >= 1 && length(var.admin_username) <= 64
    error_message = "Admin username must be between 1 and 64 characters."
  }
}

variable "authentication_type" {
  description = "Type of authentication (SSH or Password)"
  type        = string
  default     = "SSH"
  
  validation {
    condition = contains(["SSH", "Password"], var.authentication_type)
    error_message = "Authentication type must be either 'SSH' or 'Password'."
  }
}

variable "admin_password" {
  description = "Administrator password (only used if authentication_type is Password)"
  type        = string
  default     = null
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for authentication (only used if authentication_type is SSH)"
  type        = string
  default     = null
}

variable "os_disk_size_gb" {
  description = "Size of the OS disk in GB"
  type        = number
  default     = 250
  
  validation {
    condition = var.os_disk_size_gb >= 30 && var.os_disk_size_gb <= 4095
    error_message = "OS disk size must be between 30 GB and 4095 GB."
  }
}

variable "os_disk_type" {
  description = "Storage type for OS disk"
  type        = string
  default     = "Premium_LRS"
  
  validation {
    condition = contains(["Standard_LRS", "StandardSSD_LRS", "Premium_LRS", "UltraSSD_LRS"], var.os_disk_type)
    error_message = "OS disk type must be Standard_LRS, StandardSSD_LRS, Premium_LRS, or UltraSSD_LRS."
  }
}

variable "create_data_disk" {
  description = "Create an additional data disk"
  type        = bool
  default     = false
}

variable "data_disk_size_gb" {
  description = "Size of the data disk in GB"
  type        = number
  default     = 512
  
  validation {
    condition = var.data_disk_size_gb >= 4 && var.data_disk_size_gb <= 32767
    error_message = "Data disk size must be between 4 GB and 32767 GB."
  }
}

variable "data_disk_type" {
  description = "Storage type for data disk"
  type        = string
  default     = "Premium_LRS"
  
  validation {
    condition = contains(["Standard_LRS", "StandardSSD_LRS", "Premium_LRS", "UltraSSD_LRS"], var.data_disk_type)
    error_message = "Data disk type must be Standard_LRS, StandardSSD_LRS, Premium_LRS, or UltraSSD_LRS."
  }
}

variable "data_disk_caching" {
  description = "Caching type for the data disk"
  type        = string
  default     = "None"
  
  validation {
    condition = contains(["None", "ReadOnly", "ReadWrite"], var.data_disk_caching)
    error_message = "Data disk caching must be None, ReadOnly, or ReadWrite."
  }  
}

variable "install_gpu_drivers" {
  description = "Install NVIDIA GPU drivers (if VM supports GPU)"
  type        = bool
  default     = true
}

variable "gpu_driver_type" {
  description = "Type of GPU driver to install"
  type        = string
  default     = "CUDA"
  
  validation {
    condition = contains(["CUDA", "GRID"], var.gpu_driver_type)
    error_message = "GPU driver type must be either 'CUDA' (for compute) or 'GRID' (for graphics)."
  }
}

