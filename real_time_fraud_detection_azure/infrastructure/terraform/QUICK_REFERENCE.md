# Terraform Quick Reference

## Getting Started (5 minutes)

### 1. Prerequisites
```bash
# Verify Terraform is installed
terraform -version

# Verify Azure CLI is installed
az --version

# Login to Azure
az login
```

### 2. Navigate to Terraform Directory
```bash
cd infrastructure/terraform
```

### 3. Initialize Terraform
```bash
terraform init
```

### 4. Choose Environment
- `dev.tfvars` - Development (low cost, minimal resources)
- `staging.tfvars` - Staging (production-like)
- `prod.tfvars` - Production (high availability)

### 5. Plan Deployment
```bash
terraform plan -var-file=environments/dev.tfvars
```

### 6. Apply (Create Resources)
```bash
terraform apply -var-file=environments/dev.tfvars
```

---

## Common Commands

### Planning & Deployment
```bash
# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Plan changes (view what will be created/modified)
terraform plan -var-file=environments/dev.tfvars

# Save plan to file
terraform plan -var-file=environments/dev.tfvars -out=dev.tfplan

# Apply plan
terraform apply dev.tfplan

# Auto-approve (use with caution!)
terraform apply -var-file=environments/dev.tfvars -auto-approve
```

### State Management
```bash
# Show current state
terraform show

# Show specific resource
terraform show azurerm_resource_group.rg

# List resources in state
terraform state list

# Refresh state (sync with Azure)
terraform refresh -var-file=environments/dev.tfvars
```

### Outputs & Information
```bash
# Show all outputs
terraform output

# Show specific output
terraform output aks_cluster_name

# Show as JSON
terraform output -json

# Show sensitive values (use carefully!)
terraform output -raw keyvault_uri
```

### Modification & Updates
```bash
# Destroy all resources (WARNING: Data loss!)
terraform destroy -var-file=environments/dev.tfvars

# Destroy specific resource
terraform destroy -target=azurerm_resource_group.rg

# Taint resource (force recreation)
terraform taint azurerm_kubernetes_cluster.aks

# Untaint resource
terraform untaint azurerm_kubernetes_cluster.aks
```

---

## Environment Switching

### Deploy Dev
```bash
terraform apply -var-file=environments/dev.tfvars
```

### Deploy Staging
```bash
terraform apply -var-file=environments/staging.tfvars
```

### Deploy Production
```bash
terraform apply -var-file=environments/prod.tfvars
```

### Switch Between Environments
```bash
# The state file is local by default, so switching environments
# is safe. Each environment has its own resources.

# To use remote state, configure backend.tf and run:
terraform init -migrate-state
```

---

## Troubleshooting

### Issue: "Invalid provider version"
```bash
terraform init -upgrade
```

### Issue: "State lock timeout"
```bash
terraform force-unlock LOCK_ID
```

### Issue: "Authentication failed"
```bash
az login
az account set --subscription "SUBSCRIPTION_ID"
```

### Issue: "Resource already exists"
```bash
# Option 1: Import existing resource
terraform import azurerm_resource_group.rg /subscriptions/ID/resourceGroups/name

# Option 2: Destroy and recreate
terraform destroy -target=resource_type.name
terraform apply -var-file=environments/dev.tfvars
```

---

## Module Structure

Each module has 3 files:

```
modules/MODULE_NAME/
├── main.tf          # Resource definitions
├── variables.tf     # Input parameters
└── outputs.tf       # Output values
```

### Available Modules
1. **azure_ml** - Machine Learning infrastructure
2. **aks** - Kubernetes cluster
3. **networking** - Virtual Network
4. **monitoring** - Logging and alerts
5. **service_bus** - Event messaging
6. **cosmosdb** - Distributed database
7. **keyvault** - Secrets management

---

## Variable Management

### Using tfvars Files
```bash
# Single environment file
terraform apply -var-file=environments/dev.tfvars

# Override with additional variables
terraform apply \
  -var-file=environments/dev.tfvars \
  -var="node_count=5"
```

### Environment Variables
```bash
# Set via environment variable
export TF_VAR_environment=dev
terraform apply -var-file=environments/dev.tfvars
```

### Interactive Input
```bash
# Terraform will prompt for variables not provided
terraform apply
```

---

## Monitoring & Debugging

### Enable Debug Logging
```bash
export TF_LOG=DEBUG
terraform apply -var-file=environments/dev.tfvars
```

### View Detailed Plan
```bash
terraform plan -var-file=environments/dev.tfvars -no-color > plan.txt
```

### Check Resource Details
```bash
# List all resources
terraform state list

# Show specific resource config
terraform state show azurerm_kubernetes_cluster.aks
```

---

## Post-Deployment

### Get AKS Credentials
```bash
az aks get-credentials \
  --resource-group rg-fraud-detection-dev \
  --name aks-fraud-det-dev
```

### Access Azure ML
```bash
# Navigate to Azure Portal
# Search for "Machine Learning"
# Select your workspace
```

### Get Connection Strings
```bash
terraform output cosmosdb_connection_string
terraform output service_bus_namespace_name
```

### Access Key Vault
```bash
az keyvault secret list --vault-name kv-fraud-detection-dev
```

---

## Cost Management

### Estimate Costs
```bash
# Review plan output for resource types
terraform plan -var-file=environments/dev.tfvars

# Use Azure Pricing Calculator
# https://azure.microsoft.com/pricing/calculator/
```

### Reduce Costs
```bash
# Use dev.tfvars for non-production
# Reduce throughput in cosmosdb_throughput variable
# Use smaller VM sizes
# Reduce log retention in log_retention_days
```

### Monitor Costs
```bash
# Azure Portal → Cost Management + Billing
# Set up budget alerts
# Use resource tags for cost allocation
```

---

## Best Practices

✅ **Always use `terraform plan` before `apply`**
✅ **Review plan output carefully**
✅ **Use environment-specific `.tfvars` files**
✅ **Keep `terraform.tfvars` in `.gitignore`**
✅ **Use `terraform fmt` to maintain consistency**
✅ **Tag resources for cost tracking**
✅ **Use remote state for team collaboration**
✅ **Back up state files regularly**
✅ **Use `terraform validate` before commits**
✅ **Document variable changes**

---

## Quick Reference - File Locations

| What | Where |
|------|-------|
| Core config | `main.tf`, `variables.tf`, `outputs.tf` |
| Azure ML | `modules/azure_ml/` |
| Kubernetes | `modules/aks/` |
| Network | `modules/networking/` |
| Monitoring | `modules/monitoring/` |
| Messaging | `modules/service_bus/` |
| Database | `modules/cosmosdb/` |
| Secrets | `modules/keyvault/` |
| Dev config | `environments/dev.tfvars` |
| Staging config | `environments/staging.tfvars` |
| Prod config | `environments/prod.tfvars` |

---

## Documentation Links

| Document | Purpose |
|----------|---------|
| `README.md` | Quick start and commands |
| `DEPLOYMENT_GUIDE.md` | Step-by-step instructions |
| `MODULE_GUIDE.md` | Module documentation |
| `infrastructure/README.md` | Infrastructure overview |

---

## Emergency Procedures

### Rollback Deployment
```bash
# If deployment fails, review error
terraform show

# Fix configuration and re-run
terraform apply -var-file=environments/dev.tfvars
```

### Emergency Destroy
```bash
# DANGER: This deletes all resources!
# WARNING: Data in Cosmos DB will be lost!

terraform destroy -var-file=environments/dev.tfvars -auto-approve
```

### Recover from State Corruption
```bash
# Backup current state
cp terraform.tfstate terraform.tfstate.backup

# Refresh state from Azure
terraform refresh -var-file=environments/dev.tfvars

# If still corrupted, re-initialize
rm -rf .terraform
terraform init
```

---

## Support

For detailed information, see:
- `DEPLOYMENT_GUIDE.md` - Full deployment walkthrough
- `MODULE_GUIDE.md` - Module architecture and integration
- `README.md` - Quick reference and common tasks

---

**Last Updated: November 26, 2025**
**Version: 1.0**
**Status: Production Ready**

