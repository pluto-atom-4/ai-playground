output "resource_group_id" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.rg.id
}

output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.rg.name
}

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

