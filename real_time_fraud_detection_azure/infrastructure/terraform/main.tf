terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Configure Kubernetes provider
provider "kubernetes" {
  host                   = module.aks.aks_fqdn
  client_certificate     = base64decode(module.aks.aks_client_certificate)
  client_key             = base64decode(module.aks.aks_client_key)
  cluster_ca_certificate = base64decode(module.aks.aks_cluster_ca_certificate)
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  })
}

# Storage Account for data and models
resource "azurerm_storage_account" "storage" {
  name                     = "st${replace(var.project_name, "-", "")}${var.environment}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = var.storage_account_sku == "Standard_LRS" ? "LRS" : "GRS"

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })
}

# Container Registry for Docker images
resource "azurerm_container_registry" "acr" {
  name                = "acr${replace(var.project_name, "-", "")}${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.container_registry_sku

  admin_enabled = true

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })
}

# Networking Module
module "networking" {
  source = "./modules/networking"

  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  vnet_name           = var.vnet_name
  address_space       = var.vnet_address_space
  aks_subnet_name     = "subnet-aks-${var.environment}"
  aks_subnet_address  = var.aks_subnet_address
  aks_nsg_name        = "nsg-aks-${var.environment}"
  ml_subnet_name      = "subnet-ml-${var.environment}"
  ml_subnet_address   = var.ml_subnet_address
  ml_nsg_name         = "nsg-ml-${var.environment}"

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg]
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_name      = "law-${var.project_name}-${var.environment}"
  appinsights_name    = "ai-${var.project_name}-${var.environment}"
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_retention_days

  action_group_name       = "ag-${var.project_name}-${var.environment}"
  action_group_short_name = substr("ag-${var.project_name}-${var.environment}", 0, 12)

  email_receivers = []
  webhook_receivers = []

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg]
}

# Key Vault Module
module "keyvault" {
  source = "./modules/keyvault"

  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  vault_name          = var.keyvault_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = var.keyvault_sku
  enable_rbac         = var.enable_rbac

  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  enable_diagnostics         = true

  storage_account_key         = azurerm_storage_account.storage.primary_access_key
  storage_connection_string   = azurerm_storage_account.storage.primary_connection_string
  appinsights_instrumentation_key = module.monitoring.application_insights_instrumentation_key
  acr_admin_username          = azurerm_container_registry.acr.admin_username
  acr_admin_password          = azurerm_container_registry.acr.admin_password

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg, module.monitoring]
}

# AKS Cluster Module
module "aks" {
  source = "./modules/aks"

  cluster_name            = var.aks_cluster_name
  dns_prefix              = var.aks_dns_prefix
  location                = var.location
  resource_group_name     = azurerm_resource_group.rg.name
  subnet_id               = module.networking.aks_subnet_id
  node_count              = var.aks_node_count
  vm_size                 = var.aks_vm_size
  min_nodes               = var.aks_min_nodes
  max_nodes               = var.aks_max_nodes
  container_registry_id   = azurerm_container_registry.acr.id
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  enable_monitoring       = var.enable_aks_monitoring

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg, module.networking, module.monitoring]
}

# Azure ML Module
module "azure_ml" {
  source = "./modules/azure_ml"

  location                = var.location
  resource_group_name     = azurerm_resource_group.rg.name
  ml_workspace_name       = var.ml_workspace_name
  application_insights_id = module.monitoring.application_insights_id
  key_vault_id            = module.keyvault.keyvault_id
  storage_account_id      = azurerm_storage_account.storage.id

  training_cluster_name   = var.training_cluster_name
  training_vm_size        = var.training_vm_size
  training_node_count     = var.training_node_count
  training_min_nodes      = var.training_min_nodes
  training_max_nodes      = var.training_max_nodes

  create_dev_instance     = var.create_dev_instance
  dev_instance_name       = var.dev_instance_name

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg, module.monitoring, module.keyvault]
}

# Service Bus Module
module "service_bus" {
  source = "./modules/service_bus"

  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  namespace_name      = var.servicebus_namespace
  sku                 = var.servicebus_sku

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg]
}

# Cosmos DB Module
module "cosmosdb" {
  source = "./modules/cosmosdb"

  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = var.cosmosdb_account_name
  consistency_level   = var.cosmosdb_consistency
  database_throughput = var.cosmosdb_throughput
  container_throughput = var.cosmosdb_throughput

  tags = merge(var.common_tags, {
    Environment = var.environment
    Project     = var.project_name
  })

  depends_on = [azurerm_resource_group.rg]
}

# Data source for current Azure client config
data "azurerm_client_config" "current" {}


