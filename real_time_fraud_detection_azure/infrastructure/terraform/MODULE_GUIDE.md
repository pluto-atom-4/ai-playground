# Module Implementation Guide

## Overview

This guide explains each Terraform module and how they work together.

## Module Architecture

```
root/main.tf
├── networking
│   └── vnet, subnets, nsgs
├── monitoring
│   └── log analytics, app insights
├── keyvault
│   └── secrets management
├── aks
│   └── kubernetes cluster
├── azure_ml
│   └── ml workspace & compute
├── service_bus
│   └── messaging infrastructure
└── cosmosdb
    └── database storage
```

## Module Descriptions

### 1. Networking Module (`modules/networking/`)

**Purpose**: Creates Virtual Network infrastructure with proper segmentation and security.

**Resources**:
- Virtual Network (10.0.0.0/8)
- AKS Subnet (10.1.0.0/16)
- ML Subnet (10.2.0.0/16)
- Network Security Groups with inbound rules

**Key Variables**:
- `vnet_name`: Name of the VNet
- `aks_subnet_address`: CIDR for AKS subnet
- `ml_subnet_address`: CIDR for ML subnet

**Outputs**:
- VNet ID and name
- Subnet IDs for AKS and ML
- NSG IDs for security reference

**Dependencies**: Resource Group

---

### 2. Monitoring Module (`modules/monitoring/`)

**Purpose**: Centralizes logging, monitoring, and alerting infrastructure.

**Resources**:
- Log Analytics Workspace
- Application Insights
- Monitor Action Groups
- Diagnostic Settings

**Key Variables**:
- `workspace_name`: Log Analytics workspace name
- `appinsights_name`: Application Insights instance name
- `retention_in_days`: Log retention period

**Outputs**:
- Workspace ID for integration with other services
- Instrumentation keys for application configuration
- Action group ID for alert routing

**Dependencies**: Resource Group

---

### 3. Key Vault Module (`modules/keyvault/`)

**Purpose**: Manages secrets and cryptographic keys securely.

**Resources**:
- Key Vault
- Secrets (connection strings, API keys, credentials)
- Diagnostic Settings

**Key Variables**:
- `vault_name`: Key Vault name
- `enable_rbac`: Enable Azure RBAC
- Various secret inputs (optional)

**Outputs**:
- Key Vault URI
- Secret IDs for programmatic access

**Dependencies**: Resource Group, Monitoring (for diagnostics)

**Security Features**:
- RBAC authorization
- Network rules
- Audit logging

---

### 4. AKS Module (`modules/aks/`)

**Purpose**: Deploys Azure Kubernetes Service cluster with Container Insights.

**Resources**:
- AKS Cluster
- Node Pool with auto-scaling
- Kubernetes Namespaces
- Storage Classes
- RBAC role assignments

**Key Variables**:
- `cluster_name`: AKS cluster name
- `node_count`: Initial number of nodes
- `vm_size`: VM size for nodes
- `min_nodes`, `max_nodes`: Auto-scaling limits

**Outputs**:
- Cluster ID and FQDN
- Kubeconfig credentials
- Namespace names

**Dependencies**: Resource Group, Networking, Monitoring

**Namespaces Created**:
- `fraud-detection`: For fraud detection services
- `monitoring`: For monitoring/observability stack

---

### 5. Azure ML Module (`modules/azure_ml/`)

**Purpose**: Sets up machine learning infrastructure for model training and serving.

**Resources**:
- ML Workspace
- Training Compute Cluster
- Dev Compute Instance (optional)
- Online Endpoint (for real-time serving)

**Key Variables**:
- `ml_workspace_name`: Workspace name
- `training_cluster_name`: Cluster name
- `training_vm_size`: VM size for training
- `create_dev_instance`: Whether to create a dev instance

**Outputs**:
- Workspace ID and name
- Training cluster details
- Online endpoint configuration

**Dependencies**: Resource Group, Monitoring, Key Vault, Storage

---

### 6. Service Bus Module (`modules/service_bus/`)

**Purpose**: Creates messaging infrastructure for event streaming and queuing.

**Resources**:
- Service Bus Namespace
- Topics (transactions, decisions)
- Queues (case-review, fraud-alerts, model-updates)
- Subscriptions for topic filtering
- Shared Access Policies

**Key Variables**:
- `namespace_name`: Service Bus namespace name
- `sku`: Service Bus SKU (Basic/Standard/Premium)

**Outputs**:
- Namespace ID and connection strings
- Topic/Queue IDs
- Authorization rule connection strings

**Dependencies**: Resource Group

**Topics and Queues**:
- `transactions` topic → for transaction events
- `decisions` topic → for decision logs
- `case-review` queue → for review workflow
- `fraud-alerts` queue → for alert notifications
- `model-updates` queue → for model deployment

---

### 7. Cosmos DB Module (`modules/cosmosdb/`)

**Purpose**: Provides globally distributed NoSQL database for real-time data access.

**Resources**:
- Cosmos DB Account
- SQL Database
- Containers (transactions, users, entities, decisions, features)
- Role Definitions for RBAC

**Key Variables**:
- `account_name`: Cosmos DB account name
- `consistency_level`: Consistency guarantees
- `database_throughput`: RU/s allocation

**Outputs**:
- Account ID, endpoint, connection string
- Container IDs for application reference

**Dependencies**: Resource Group

**Containers**:
- `transactions`: Transaction records
- `users`: User profiles and behavior
- `entities`: Shared entities (devices, cards, IPs)
- `decisions`: Decision audit logs
- `features`: Precomputed features

---

## Module Integration Points

### Data Flow

```
Networking
    ↓
Monitoring ←→ Key Vault
    ↓           ↓
   AKS     Azure ML ← Key Vault
    ↓           ↓
Service Bus ← Cosmos DB
```

### Cross-Module References

1. **Storage Account** → Used by Azure ML and Key Vault
2. **Container Registry** → Used by AKS for image pulls
3. **Application Insights** → Used by Azure ML for experiment tracking
4. **Log Analytics** → Receives logs from all modules
5. **Key Vault** → Stores secrets for all services

---

## Module Usage Example

### In main.tf

```hcl
# Call networking module
module "networking" {
  source = "./modules/networking"
  
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  vnet_name           = var.vnet_name
  # ... other variables
}

# Call AKS module using networking outputs
module "aks" {
  source = "./modules/aks"
  
  location    = var.location
  subnet_id   = module.networking.aks_subnet_id  # Reference networking output
  # ... other variables
}
```

---

## Adding Custom Resources to Modules

### To add a resource to a module:

1. Add the resource definition in `modules/xxx/main.tf`
2. Define any new variables in `modules/xxx/variables.tf`
3. Export outputs in `modules/xxx/outputs.tf`
4. Update root `main.tf` to use new variables/outputs if needed
5. Document the changes in module README

### Example: Adding a new container to Cosmos DB

```hcl
# In modules/cosmosdb/main.tf
resource "azurerm_cosmosdb_sql_container" "new_container" {
  name                = var.new_container_name
  database_name       = azurerm_cosmosdb_sql_database.database.name
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.cosmosdb.name
  partition_key_path  = "/id"
}

# In modules/cosmosdb/variables.tf
variable "new_container_name" {
  description = "Name of new container"
  type        = string
  default     = "new-container"
}

# In modules/cosmosdb/outputs.tf
output "new_container_id" {
  value = azurerm_cosmosdb_sql_container.new_container.id
}
```

---

## Troubleshooting Module Issues

### Module initialization fails
```bash
# Clear and reinitialize
rm -rf .terraform/modules
terraform init
```

### Cannot reference module outputs
- Verify module block has `source` defined
- Check module name matches in root and outputs
- Ensure module has `depends_on` if needed

### State corruption
- Check `.terraform/terraform.tfstate` integrity
- Use `terraform refresh` to sync state
- Consider using `terraform plan -refresh-only`

---

## Performance Considerations

1. **Parallel deployments**: Terraform deploys in parallel where possible
2. **Module dependencies**: Explicitly set with `depends_on`
3. **Large clusters**: AKS deployment takes longest (15-30 minutes)
4. **Cosmos DB**: Scale-out is slower than scale-in

---

## Cost Optimization by Module

- **Networking**: Fixed cost, minimal optimization needed
- **Monitoring**: Reduce `retention_in_days` to save costs
- **AKS**: Use auto-scaling and lower `max_nodes` for dev
- **Azure ML**: Disable dev instance in non-dev environments
- **Service Bus**: Use Basic tier for dev, Standard for prod
- **Cosmos DB**: Reduce throughput in dev environments

