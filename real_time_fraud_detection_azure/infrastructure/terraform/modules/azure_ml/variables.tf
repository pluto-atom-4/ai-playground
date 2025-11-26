variable "location" {
  description = "Azure region for Azure ML resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "ml_workspace_name" {
  description = "Name of the Azure ML Workspace"
  type        = string
}

variable "application_insights_id" {
  description = "Application Insights resource ID for logging and monitoring"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault resource ID for secrets management"
  type        = string
}

variable "storage_account_id" {
  description = "Storage Account resource ID for data and model storage"
  type        = string
}

variable "training_cluster_name" {
  description = "Name of the Azure ML training compute cluster"
  type        = string
  default     = "training-cluster"
}

variable "training_vm_size" {
  description = "VM size for training cluster"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "training_node_count" {
  description = "Number of nodes in training cluster"
  type        = number
  default     = 2
}

variable "training_min_nodes" {
  description = "Minimum number of nodes for auto-scaling"
  type        = number
  default     = 0
}

variable "training_max_nodes" {
  description = "Maximum number of nodes for auto-scaling"
  type        = number
  default     = 4
}

variable "create_dev_instance" {
  description = "Whether to create a dev compute instance"
  type        = bool
  default     = true
}

variable "dev_instance_name" {
  description = "Name of the development compute instance"
  type        = string
  default     = "dev-instance"
}

variable "dev_vm_size" {
  description = "VM size for dev instance"
  type        = string
  default     = "Standard_D3_v2"
}

variable "online_endpoint_name" {
  description = "Name of the online endpoint for real-time model serving"
  type        = string
  default     = "fraud-detection-endpoint"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

