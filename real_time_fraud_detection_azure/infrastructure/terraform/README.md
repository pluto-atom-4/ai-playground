# Terraform Infrastructure as Code

This directory contains all Terraform configurations for the Real-time Fraud Detection system on Azure.

## Directory Structure

```
├── main.tf                  # Root module configuration with all resources
├── variables.tf            # Variable definitions for all configurations
├── outputs.tf              # Output values from all modules
├── backend.tf              # Remote state configuration
├── terraform.tfvars.example # Example variables file
│
├── modules/                # Reusable Terraform modules
│   ├── azure_ml/          # Azure Machine Learning resources
│   ├── aks/               # Azure Kubernetes Service configuration
│   ├── networking/        # Virtual Network and networking resources
│   ├── monitoring/        # Logging, monitoring, and alerting
│   ├── service_bus/       # Azure Service Bus messaging
│   ├── cosmosdb/          # Cosmos DB data store
│   └── keyvault/          # Key Vault secrets management
│
└── environments/           # Environment-specific variable files
    ├── dev.tfvars        # Development environment configuration
    ├── staging.tfvars    # Staging environment configuration
    └── prod.tfvars       # Production environment configuration
```

## Quick Start

### Prerequisites

1. Install Terraform >= 1.0: https://www.terraform.io/downloads
2. Azure CLI installed and authenticated: `az login`
3. Azure subscription with sufficient permissions

### Initialization

```bash
# Initialize Terraform (download providers and modules)
terraform init
```

### Plan and Apply

```bash
# For Development environment
terraform plan -var-file=environments/dev.tfvars -out=dev.tfplan
terraform apply dev.tfplan

# For Staging environment
terraform plan -var-file=environments/staging.tfvars -out=staging.tfplan
terraform apply staging.tfplan

# For Production environment
terraform plan -var-file=environments/prod.tfvars -out=prod.tfplan
terraform apply prod.tfplan
```

### Remote State Management

To use remote state with Azure Storage Account:

1. Create a resource group and storage account for Terraform state:
```bash
az group create --name rg-terraform-state --location eastus
az storage account create --name tfstateaccount --resource-group rg-terraform-state --location eastus
az storage container create --name tfstate --account-name tfstateaccount
```

2. Uncomment the backend configuration in `backend.tf` and update values

3. Run `terraform init` again

## Module Documentation

### azure_ml
Creates Azure Machine Learning workspace with training clusters and compute instances.
- **Files**: `modules/azure_ml/`
- **Resources**: ML Workspace, Training Cluster, Compute Instance

### aks
Deploys Azure Kubernetes Service cluster with monitoring integration.
- **Files**: `modules/aks/`
- **Resources**: AKS Cluster, Kubernetes Namespaces

### networking
Sets up Virtual Networks, Subnets, and Network Security Groups.
- **Files**: `modules/networking/`
- **Resources**: VNet, Subnets, NSGs

### monitoring
Configures Log Analytics, Application Insights, and alerting.
- **Files**: `modules/monitoring/`
- **Resources**: Log Analytics Workspace, App Insights, Action Groups

### service_bus
Creates Service Bus namespace with topics and queues for event streaming.
- **Files**: `modules/service_bus/`
- **Resources**: Service Bus Namespace, Topics, Queues, Subscriptions

### cosmosdb
Deploys Cosmos DB account with containers for data storage.
- **Files**: `modules/cosmosdb/`
- **Resources**: Cosmos DB Account, Database, Containers

### keyvault
Sets up Key Vault for secrets management and security.
- **Files**: `modules/keyvault/`
- **Resources**: Key Vault, Secrets, Diagnostic Settings

## Environment Configuration

Each environment has its own `.tfvars` file:

- **dev.tfvars**: Minimal resources for development (Dev ML instance enabled)
- **staging.tfvars**: Production-like configuration for testing
- **prod.tfvars**: Full production setup with high availability and strong consistency

## Common Commands

```bash
# Show what will be changed (no changes made)
terraform plan -var-file=environments/dev.tfvars

# Apply changes
terraform apply -var-file=environments/dev.tfvars

# Destroy all resources
terraform destroy -var-file=environments/dev.tfvars

# Show current state
terraform show

# Validate configuration syntax
terraform validate

# Format code
terraform fmt -recursive

# Get outputs
terraform output
```

## Security Best Practices

1. **Never commit terraform.tfvars** - Use environment-specific files in `environments/`
2. **Store sensitive values in Key Vault** - Reference via module outputs
3. **Use RBAC** - Enable RBAC in Key Vault and AKS modules
4. **Private endpoints** - Consider adding private endpoints for sensitive services
5. **Network isolation** - Subnets have NSGs with restricted inbound rules

## Troubleshooting

### Provider Authentication Issues
```bash
# Re-authenticate with Azure
az login

# Set subscription
az account set --subscription YOUR_SUBSCRIPTION_ID
```

### Module Errors
```bash
# Re-initialize modules
rm -rf .terraform
terraform init
```

### State Lock Issues
```bash
# Force unlock (use with caution!)
terraform force-unlock LOCK_ID
```

## Cost Optimization

- Use Dev environment for development and testing
- Staging uses Standard SKUs instead of Premium
- Production uses Premium SKUs for high availability
- Consider reserved instances for long-term workloads
- Review Azure Cost Management regularly

## Support and Updates

- Terraform Documentation: https://registry.terraform.io/providers/hashicorp/azurerm
- Azure Provider: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
- Terraform Best Practices: https://www.terraform.io/docs/language/index.html

