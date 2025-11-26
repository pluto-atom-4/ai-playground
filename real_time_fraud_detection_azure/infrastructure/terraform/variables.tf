## Azure Configuration
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "fraud-detection"

  validation {
    condition     = length(var.project_name) <= 20
    error_message = "Project name must be 20 characters or less."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "fraud-detection"
    ManagedBy   = "Terraform"
  }
}

## Storage Configuration
variable "storage_account_sku" {
  description = "Storage Account SKU (Standard_LRS, Standard_GRS, etc.)"
  type        = string
  default     = "Standard_GRS"
}

variable "container_registry_sku" {
  description = "Container Registry SKU"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.container_registry_sku)
    error_message = "SKU must be one of: Basic, Standard, Premium."
  }
}

## Networking Configuration
variable "vnet_name" {
  description = "Virtual Network name"
  type        = string
  default     = "vnet-fraud-detection"
}

variable "vnet_address_space" {
  description = "Virtual Network address space"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "aks_subnet_address" {
  description = "AKS subnet address space"
  type        = list(string)
  default     = ["10.1.0.0/16"]
}

variable "ml_subnet_address" {
  description = "ML subnet address space"
  type        = list(string)
  default     = ["10.2.0.0/16"]
}

## AKS Configuration
variable "aks_cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "aks-fraud-detection"
}

variable "aks_dns_prefix" {
  description = "DNS prefix for AKS cluster"
  type        = string
  default     = "aks-fraud-det"
}

variable "aks_node_count" {
  description = "Initial number of AKS nodes"
  type        = number
  default     = 3
}

variable "aks_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "aks_min_nodes" {
  description = "Minimum number of AKS nodes"
  type        = number
  default     = 2
}

variable "aks_max_nodes" {
  description = "Maximum number of AKS nodes"
  type        = number
  default     = 5
}

variable "enable_aks_monitoring" {
  description = "Enable monitoring for AKS"
  type        = bool
  default     = true
}

## Azure ML Configuration
variable "ml_workspace_name" {
  description = "Azure ML Workspace name"
  type        = string
  default     = "mlw-fraud-detection"
}

variable "training_cluster_name" {
  description = "Training cluster name"
  type        = string
  default     = "training-cluster"
}

variable "training_vm_size" {
  description = "Training cluster VM size"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "training_node_count" {
  description = "Training cluster node count"
  type        = number
  default     = 2
}

variable "training_min_nodes" {
  description = "Training cluster minimum nodes"
  type        = number
  default     = 0
}

variable "training_max_nodes" {
  description = "Training cluster maximum nodes"
  type        = number
  default     = 4
}

variable "create_dev_instance" {
  description = "Create development compute instance"
  type        = bool
  default     = false
}

variable "dev_instance_name" {
  description = "Development instance name"
  type        = string
  default     = "dev-instance"
}

## Monitoring Configuration
variable "log_analytics_sku" {
  description = "Log Analytics SKU"
  type        = string
  default     = "PerGB2018"
}

variable "log_retention_days" {
  description = "Log Analytics retention in days"
  type        = number
  default     = 30

  validation {
    condition     = var.log_retention_days >= 7 && var.log_retention_days <= 730
    error_message = "Retention days must be between 7 and 730."
  }
}

## Service Bus Configuration
variable "servicebus_namespace" {
  description = "Service Bus namespace name"
  type        = string
  default     = "sb-fraud-detection"
}

variable "servicebus_sku" {
  description = "Service Bus SKU"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.servicebus_sku)
    error_message = "SKU must be one of: Basic, Standard, Premium."
  }
}

## Cosmos DB Configuration
variable "cosmosdb_account_name" {
  description = "Cosmos DB account name"
  type        = string
  default     = "cosmos-fraud-detection"
}

variable "cosmosdb_consistency" {
  description = "Cosmos DB consistency level"
  type        = string
  default     = "BoundedStaleness"
}

variable "cosmosdb_throughput" {
  description = "Cosmos DB throughput (RU/s)"
  type        = number
  default     = 400
}

## Key Vault Configuration
variable "keyvault_name" {
  description = "Key Vault name"
  type        = string
  default     = "kv-fraud-detection"
}

variable "keyvault_sku" {
  description = "Key Vault SKU"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.keyvault_sku)
    error_message = "SKU must be one of: standard, premium."
  }
}

variable "enable_rbac" {
  description = "Enable RBAC for Key Vault"
  type        = bool
  default     = true
}

