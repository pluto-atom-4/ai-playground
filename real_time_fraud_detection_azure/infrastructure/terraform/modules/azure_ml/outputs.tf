output "ml_workspace_id" {
  description = "Azure ML Workspace ID"
  value       = azurerm_machine_learning_workspace.ml_workspace.id
}

output "ml_workspace_name" {
  description = "Azure ML Workspace name"
  value       = azurerm_machine_learning_workspace.ml_workspace.name
}

output "training_cluster_id" {
  description = "Training compute cluster ID"
  value       = azurerm_machine_learning_compute_cluster.training_cluster.id
}

output "training_cluster_name" {
  description = "Training compute cluster name"
  value       = azurerm_machine_learning_compute_cluster.training_cluster.name
}

output "dev_instance_id" {
  description = "Dev compute instance ID"
  value       = try(azurerm_machine_learning_compute_instance.dev_instance[0].id, null)
}

output "dev_instance_name" {
  description = "Dev compute instance name"
  value       = try(azurerm_machine_learning_compute_instance.dev_instance[0].name, null)
}

output "online_endpoint_id" {
  description = "Online endpoint ID"
  value       = azurerm_machine_learning_model_deployment.online_endpoint.id
}

output "online_endpoint_name" {
  description = "Online endpoint name"
  value       = azurerm_machine_learning_model_deployment.online_endpoint.name
}

