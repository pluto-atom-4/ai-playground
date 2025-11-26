## Resource Group Outputs
output "resource_group_id" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.rg.id
}

output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.rg.name
}

## Storage Account Outputs
output "storage_account_id" {
  description = "Storage Account ID"
  value       = azurerm_storage_account.storage.id
}

output "storage_account_name" {
  description = "Storage Account name"
  value       = azurerm_storage_account.storage.name
}

output "storage_account_primary_connection_string" {
  description = "Storage Account connection string"
  value       = azurerm_storage_account.storage.primary_connection_string
  sensitive   = true
}

## Container Registry Outputs
output "container_registry_id" {
  description = "Container Registry ID"
  value       = azurerm_container_registry.acr.id
}

output "container_registry_name" {
  description = "Container Registry name"
  value       = azurerm_container_registry.acr.name
}

output "container_registry_login_server" {
  description = "Container Registry login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "container_registry_admin_username" {
  description = "Container Registry admin username"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "container_registry_admin_password" {
  description = "Container Registry admin password"
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

## Networking Module Outputs
output "vnet_id" {
  description = "Virtual Network ID"
  value       = module.networking.vnet_id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = module.networking.vnet_name
}

output "aks_subnet_id" {
  description = "AKS Subnet ID"
  value       = module.networking.aks_subnet_id
}

output "ml_subnet_id" {
  description = "ML Subnet ID"
  value       = module.networking.ml_subnet_id
}

## Monitoring Module Outputs
output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = module.monitoring.log_analytics_workspace_id
}

output "log_analytics_workspace_name" {
  description = "Log Analytics Workspace name"
  value       = module.monitoring.log_analytics_workspace_name
}

output "application_insights_id" {
  description = "Application Insights ID"
  value       = module.monitoring.application_insights_id
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.application_insights_instrumentation_key
  sensitive   = true
}

output "action_group_id" {
  description = "Monitor Action Group ID"
  value       = module.monitoring.action_group_id
}

## Key Vault Module Outputs
output "keyvault_id" {
  description = "Key Vault ID"
  value       = module.keyvault.keyvault_id
}

output "keyvault_uri" {
  description = "Key Vault URI"
  value       = module.keyvault.keyvault_uri
}

## AKS Module Outputs
output "aks_cluster_id" {
  description = "AKS Cluster ID"
  value       = module.aks.aks_cluster_id
}

output "aks_cluster_name" {
  description = "AKS Cluster name"
  value       = module.aks.aks_cluster_name
}

output "aks_fqdn" {
  description = "AKS Cluster FQDN"
  value       = module.aks.aks_fqdn
}

output "fraud_detection_namespace" {
  description = "Kubernetes namespace for fraud detection"
  value       = module.aks.fraud_detection_namespace
}

output "monitoring_namespace" {
  description = "Kubernetes namespace for monitoring"
  value       = module.aks.monitoring_namespace
}

## Azure ML Module Outputs
output "ml_workspace_id" {
  description = "Azure ML Workspace ID"
  value       = module.azure_ml.ml_workspace_id
}

output "ml_workspace_name" {
  description = "Azure ML Workspace name"
  value       = module.azure_ml.ml_workspace_name
}

output "training_cluster_id" {
  description = "Training Cluster ID"
  value       = module.azure_ml.training_cluster_id
}

## Service Bus Module Outputs
output "service_bus_namespace_id" {
  description = "Service Bus Namespace ID"
  value       = module.service_bus.service_bus_namespace_id
}

output "service_bus_namespace_name" {
  description = "Service Bus Namespace name"
  value       = module.service_bus.service_bus_namespace_name
}

output "transactions_topic_id" {
  description = "Transactions Topic ID"
  value       = module.service_bus.transactions_topic_id
}

output "decisions_topic_id" {
  description = "Decisions Topic ID"
  value       = module.service_bus.decisions_topic_id
}

## Cosmos DB Module Outputs
output "cosmosdb_account_id" {
  description = "Cosmos DB Account ID"
  value       = module.cosmosdb.cosmosdb_account_id
}

output "cosmosdb_endpoint" {
  description = "Cosmos DB Endpoint URL"
  value       = module.cosmosdb.cosmosdb_endpoint
}

output "cosmosdb_connection_string" {
  description = "Cosmos DB Connection String"
  value       = module.cosmosdb.cosmosdb_connection_string
  sensitive   = true
}

}

output "application_insights_id" {
  description = "Application Insights ID"
  value       = azurerm_application_insights.appinsights.id
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.appinsights.instrumentation_key
  sensitive   = true
}

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = azurerm_log_analytics_workspace.law.id
}

output "log_analytics_workspace_name" {
  description = "Log Analytics Workspace name"
  value       = azurerm_log_analytics_workspace.law.name
}

