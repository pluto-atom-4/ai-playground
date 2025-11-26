variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
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

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
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

variable "log_retention_days" {
  description = "Log Analytics retention in days"
  type        = number
  default     = 30

  validation {
    condition     = var.log_retention_days >= 7 && var.log_retention_days <= 730
    error_message = "Retention days must be between 7 and 730."
  }
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

