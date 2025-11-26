# Pipelines

This directory contains Azure DevOps or GitHub Actions pipeline configurations for the fraud detection system.

## Structure

```
pipelines/
├── training/         # ML model training pipelines
├── deployment/       # Model and service deployment pipelines
└── monitoring/       # Monitoring and alerting pipelines
```

## Training Pipelines

- `fraud_detection_training_pipeline.yml` - Main training pipeline
- `fraud_detection_training_pipeline_with_schedule.yml` - Scheduled training (e.g., daily/weekly retraining)

## Deployment Pipelines

- `decision_service_deployment.yaml` - Deployment configuration for the fraud detection decision service

## Monitoring Pipelines

Reserved for monitoring and health check pipelines.

## Usage

Pipelines can be executed via:
- Azure DevOps Pipeline UI
- GitHub Actions
- Manual triggers via CLI

