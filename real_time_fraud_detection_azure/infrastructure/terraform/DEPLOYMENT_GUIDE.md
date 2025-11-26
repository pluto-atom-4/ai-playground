# Terraform Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Real-time Fraud Detection infrastructure using Terraform.

## Prerequisites

### Tools Installation

1. **Terraform** (>= 1.0)
   ```bash
   choco install terraform
   # Windows with Chocolatey
   # Manual download: https://www.terraform.io/downloads
   ```

2. **Azure CLI**
   ```bash
   choco install azure-cli
   # Windows installer or Chocolatey
   ```

3. **kubectl** (for Kubernetes management)
   ```bash
   az aks install-cli
   ```

### Azure Setup

1. Create an Azure account and subscription
2. Authenticate with Azure:
   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

3. Ensure you have appropriate permissions:
   - Contributor role on the subscription
   - Ability to create resource groups and resources

## Deployment Steps

### Step 1: Prepare Variables

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your subscription ID:
   ```bash
   subscription_id = "your-subscription-id-here"
   ```

3. For environment-specific deployments, update the appropriate file in `environments/`:
   - `environments/dev.tfvars` for development
   - `environments/staging.tfvars` for staging
   - `environments/prod.tfvars` for production

### Step 2: Configure Remote State (Optional but Recommended)

For team deployments, configure remote state:

1. Create a storage account for state:
   ```bash
   az group create --name rg-terraform-state --location eastus
   az storage account create \
     --name tfstateXXXXXX \
     --resource-group rg-terraform-state \
     --location eastus \
     --sku Standard_LRS
   az storage container create \
     --name tfstate \
     --account-name tfstateXXXXXX
   ```

2. Uncomment and update `backend.tf`:
   ```hcl
   backend "azurerm" {
     resource_group_name  = "rg-terraform-state"
     storage_account_name = "tfstateXXXXXX"
     container_name       = "tfstate"
     key                  = "fraud-detection/terraform.tfstate"
   }
   ```

3. Initialize Terraform:
   ```bash
   terraform init
   ```

### Step 3: Initialize Terraform

```bash
terraform init
# Download required providers and modules

terraform validate
# Validate configuration

terraform fmt -recursive
# Format code (recommended)
```

### Step 4: Plan Deployment

For **Development**:
```bash
terraform plan -var-file=environments/dev.tfvars -out=dev.tfplan
```

For **Staging**:
```bash
terraform plan -var-file=environments/staging.tfvars -out=staging.tfplan
```

For **Production**:
```bash
terraform plan -var-file=environments/prod.tfvars -out=prod.tfplan
```

Review the plan output carefully to ensure all resources are as expected.

### Step 5: Apply Configuration

The deployment will take 20-40 minutes depending on the environment.

```bash
terraform apply dev.tfplan
# Development

terraform apply staging.tfplan
# Staging

terraform apply prod.tfplan
# Production
```

### Step 6: Post-Deployment

1. **Get output values**:
   ```bash
   terraform output
   ```

2. **Configure kubectl** for AKS:
   ```bash
   az aks get-credentials \
     --resource-group rg-fraud-detection-dev \
     --name aks-fraud-det-dev
   # Verify connection
   kubectl get nodes
   ```

3. **Access Key Vault secrets**:
   ```bash
   az keyvault secret list --vault-name kv-fraud-detection-dev
   ```

4. **Configure Azure ML**:
   - Navigate to Azure Portal
   - Find the Azure ML workspace
   - Download config.json for SDK access

## Updating Infrastructure

### Add or Modify Resources

1. Edit the appropriate `.tf` file or module
2. Plan the changes:
   ```bash
   terraform plan -var-file=environments/dev.tfvars
   ```

3. Review the plan carefully
4. Apply:
   ```bash
   terraform apply -var-file=environments/dev.tfvars
   ```

### Update Environment Variables

1. Edit the relevant `.tfvars` file in `environments/`
2. Plan and apply as above

## Destroying Infrastructure

### WARNING: Data Loss Risk

Destroying Cosmos DB and other stateful resources will result in data loss.

```bash
# Destroy development environment
terraform destroy -var-file=environments/dev.tfvars

# Destroy with auto-approval (dangerous!)
terraform destroy -var-file=environments/dev.tfvars -auto-approve
```

## Troubleshooting

### Authentication Errors

```bash
az logout
# Clear Azure CLI cache

az login
az account set --subscription "SUBSCRIPTION_ID"
# Specify subscription
```

### Provider Issues

```bash
# Reinstall providers
rm -rf .terraform
terraform init
```

### State Lock Issues

```bash
# Check locks
terraform force-unlock LOCK_ID
```

### Resource Creation Failures

1. Check Azure quotas in the region
2. Verify subscription limits
3. Check network connectivity
4. Review Azure Activity Log for detailed errors

## Cost Monitoring

### Estimate Costs Before Deployment

Check Azure pricing for resources in the plan.

```bash
terraform plan -var-file=environments/prod.tfvars
```

### Monitor Costs After Deployment

1. Azure Portal → Cost Management + Billing
2. Set up budget alerts
3. Review resource utilization regularly

## Best Practices

1. **Always use `-var-file`** to specify environment
2. **Store tfplan files** before applying
3. **Review plans carefully** before applying
4. **Use descriptive names** for resources
5. **Tag resources** appropriately for billing
6. **Keep terraform.tfvars in .gitignore**
7. **Regularly backup state files**
8. **Document environment-specific settings**

## Next Steps

1. Deploy Kubernetes manifests (see `../kubernetes/`)
2. Configure container images in Azure Container Registry
3. Deploy fraud detection services to AKS
4. Set up CI/CD pipeline for automated deployments
5. Configure monitoring and alerting rules

