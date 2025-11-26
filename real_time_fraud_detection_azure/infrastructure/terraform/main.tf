terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Uncomment and configure to use remote state
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform-state"
  #   storage_account_name = "tfstateaccount"
  #   container_name       = "tfstate"
  #   key                  = "prod.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = local.common_tags
}

# Storage Account for data and models
resource "azurerm_storage_account" "storage" {
  name                     = "st${replace(var.project_name, "-", "")}${var.environment}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = local.common_tags
}

# Container Registry for Docker images
resource "azurerm_container_registry" "acr" {
  name                = "acr${replace(var.project_name, "-", "")}${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.container_registry_sku

  admin_enabled = true

  tags = local.common_tags
}

# Application Insights for monitoring
resource "azurerm_application_insights" "appinsights" {
  name                = "ai-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"

  tags = local.common_tags
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days

  tags = local.common_tags
}

locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }
}

