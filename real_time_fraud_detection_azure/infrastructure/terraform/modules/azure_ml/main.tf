terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Azure Machine Learning Workspace
resource "azurerm_machine_learning_workspace" "ml_workspace" {
  name                    = var.ml_workspace_name
  location                = var.location
  resource_group_name     = var.resource_group_name
  application_insights_id = var.application_insights_id
  key_vault_id            = var.key_vault_id
  storage_account_id      = var.storage_account_id

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Azure ML Compute Cluster for training
resource "azurerm_machine_learning_compute_cluster" "training_cluster" {
  name                          = var.training_cluster_name
  location                      = var.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.ml_workspace.id
  node_count                    = var.training_node_count
  vm_priority                   = "Dedicated"
  vm_size                       = var.training_vm_size

  scale_settings {
    max_node_count = var.training_max_nodes
    min_node_count = var.training_min_nodes
  }

  tags = var.tags
}

# Azure ML Compute Instance for development (optional)
resource "azurerm_machine_learning_compute_instance" "dev_instance" {
  count                         = var.create_dev_instance ? 1 : 0
  name                          = var.dev_instance_name
  location                      = var.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.ml_workspace.id
  virtual_machine_size          = var.dev_vm_size

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Azure ML Online Endpoint for real-time model serving
resource "azurerm_machine_learning_model_deployment" "online_endpoint" {
  name                          = var.online_endpoint_name
  location                      = var.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.ml_workspace.id
  auth_mode                     = "Key"

  tags = var.tags
}

