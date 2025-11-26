# Real-Time Fraud Detection System - Azure

A comprehensive real-time fraud detection system built on Microsoft Azure with ML model training, deployment pipelines, and monitoring infrastructure.

## Project Structure

```
real_time_fraud_detection_azure/
├── docs/                      # Documentation and runbooks
│   ├── implementation_plan_mvp.md
│   ├── real_time_fraud_detection.md
│   ├── fraud_detection_runbook.md
│   └── README.md
│
├── infrastructure/            # Infrastructure-as-Code
│   ├── terraform/            # Terraform configurations
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   ├── kubernetes/           # Kubernetes manifests (optional)
│   ├── scripts/              # Deployment scripts
│   └── README.md
│
├── pipelines/                # Azure DevOps/GitHub Actions pipelines
│   ├── training/            # ML model training
│   ├── deployment/          # Service deployment
│   └── monitoring/          # Monitoring pipelines
│
├── monitoring/              # Dashboards and alerts
│   ├── dashboards/         # Power BI, Grafana, Workbooks
│   ├── alerts/            # Alert configurations
│   ├── rules/             # Monitoring rules
│   └── README.md
│
├── case-management/        # Case management workflows
│   └── case_management_workflow.md
│
├── notebooks/              # Jupyter notebooks for analysis
│
└── src/                    # Application source code
```

## Quick Start

### 1. Infrastructure Setup with Terraform

```bash
cd infrastructure/terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
# - subscription_id
# - region (optional)
# - environment (dev/staging/prod)

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply configuration
terraform apply tfplan
```

### 2. Azure DevOps Pipelines

The `pipelines/` directory contains:
- **Training**: Automated model retraining pipelines
- **Deployment**: Service deployment and updates
- **Monitoring**: Health checks and diagnostics

### 3. Monitoring Setup

Configure monitoring using resources in `monitoring/`:
- Import dashboards
- Set up alert rules
- Configure monitoring rules

## Key Features

- **Real-time Detection**: Low-latency fraud detection
- **Model Training**: Automated ML training pipelines
- **Infrastructure as Code**: Full Terraform automation
- **Monitoring & Alerts**: Comprehensive observability
- **Scalability**: Built for Azure cloud scale

## Technology Stack

- **Cloud Platform**: Microsoft Azure
- **Infrastructure**: Terraform
- **Container Registry**: Azure Container Registry (ACR)
- **ML/Analytics**: Azure Machine Learning
- **Monitoring**: Application Insights, Log Analytics
- **Pipelines**: Azure DevOps / GitHub Actions

## Prerequisites

- Azure subscription
- Terraform >= 1.0
- Azure CLI
- Docker (for building container images)
- Python 3.8+ (for local development)

## Configuration

### Environment Variables

```bash
# Azure credentials
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_CLIENT_ID="your-client-id"
export ARM_CLIENT_SECRET="your-client-secret"
export ARM_TENANT_ID="your-tenant-id"
```

### Terraform Variables

See `infrastructure/terraform/terraform.tfvars.example` for all available options.

## Deployment

### Development Environment

```bash
cd infrastructure/terraform
terraform apply -var-file=dev.tfvars
```

### Production Environment

```bash
cd infrastructure/terraform
terraform apply -var-file=prod.tfvars
```

## Documentation

- [Infrastructure Setup](infrastructure/README.md)
- [Pipeline Configuration](pipelines/README.md)
- [Monitoring Guide](monitoring/README.md)
- [System Design](docs/real_time_fraud_detection.md)
- [Implementation Plan](docs/implementation_plan_mvp.md)
- [Operations Runbook](docs/fraud_detection_runbook.md)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test in dev environment
4. Submit pull request

## License

[Add your license here]

## Support

For issues and questions, please refer to:
- [Runbook](docs/fraud_detection_runbook.md)
- [System Design](docs/real_time_fraud_detection.md)

