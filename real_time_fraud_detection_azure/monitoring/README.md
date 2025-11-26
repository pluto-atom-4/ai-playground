# Monitoring

This directory contains monitoring, alerting, and dashboarding configurations for the fraud detection system.

## Structure

```
monitoring/
├── dashboards/       # Grafana, Power BI, or Azure dashboards
├── alerts/          # Alert rules and configurations
└── rules/           # Monitoring rules (KPI, drift detection)
```

## Dashboards

- `fraud_detection_workbook.json` - Azure Workbook for fraud detection metrics
- `faud_detection_dashboard_sample_layout.md` - Dashboard layout reference

## Alerts

- `app_insights_config.yaml` - Application Insights configuration
- `latency_alert_rules.json` - Alert rules for latency monitoring

## Monitoring Rules

- `business_kpi_monitor.yaml` - Business KPI monitoring configuration
- `model_drift_monitor.yaml` - Model drift detection rules

## Documentation

- `latency_alert_rules_usage.md` - How to use latency alert rules
- `model_drift_monitor_usage.md` - Model drift monitoring guide

## Setup

1. Import dashboard configurations into your monitoring platform
2. Configure alert rules according to your thresholds
3. Link monitoring rules to notification channels

