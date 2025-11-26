# Infrastructure Setup

This directory contains all infrastructure-as-code and deployment configurations for the Real-Time Fraud Detection system on Azure.

## Directory Structure

```
infrastructure/
├── terraform/              # Terraform IaC for Azure resource provisioning
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Variable definitions
│   ├── outputs.tf         # Output values
│   └── modules/           # Reusable Terraform modules
├── kubernetes/            # Kubernetes manifests (if using AKS)
├── scripts/               # Deployment and setup scripts
└── README.md             # This file
```

## Terraform Structure

The `terraform/` directory contains configurations to provision:
- Azure Resource Group
- Storage accounts for data and models
- Container Registry for Docker images
- Machine Learning resources
- Monitoring and logging infrastructure
- Networking and security configurations

### Terraform Files

- **main.tf**: Main provider configuration and resource definitions
- **variables.tf**: Input variables for the infrastructure
- **outputs.tf**: Output values exposed after deployment
- **modules/**: Modular components for better code organization and reusability

## Prerequisites

- Terraform >= 1.0
- Azure CLI installed and authenticated
- Azure subscription with appropriate permissions

## Quick Start

1. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```

2. Plan the deployment:
   ```bash
   terraform plan -out=tfplan
   ```

3. Apply the configuration:
   ```bash
   terraform apply tfplan
   ```

## Environment Configuration

Create a `terraform.tfvars` file to customize your deployment:
```hcl
project_name = "fraud-detection"
environment  = "dev"
region       = "eastus"
```

## Kubernetes (Optional)

If using Azure Kubernetes Service (AKS), Kubernetes manifests should be placed in the `kubernetes/` directory.

## Scripts

The `scripts/` directory contains helper scripts for:
- Infrastructure setup
- Deployment automation
- Resource cleanup

## State Management

Terraform state files should be stored in Azure Storage for team collaboration:
```bash
# Configure remote state (run once)
terraform init -backend-config="..."
```

## Contributing

When adding new infrastructure:
1. Use Terraform modules for reusability
2. Document variables and outputs
3. Include examples in README
4. Test in dev environment first

## Troubleshooting

Common issues and solutions are documented in individual module READMEs.

