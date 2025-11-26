# 📄 Implementation Plan – Real‑Time Fraud Detection System (MVP)

## 🎯 Goal

Deliver a minimum viable product (MVP) of the fraud detection system that:

* Scores transactions in real time via an API
* Logs telemetry and latency
* Monitors drift and business KPIs
* Routes ambiguous cases to analysts via Service Bus + Logic Apps

## 📂 Phase Breakdown

### Phase 1 – Environment & Infrastructure Setup (6–8 hours)

* Provision **Azure ML workspace**, **AKS** cluster, **Application Insights**, **Service Bus**, and **Logic Apps**.
* Configure Cosmos DB/SQL for case records and ADLS for audit logs.
* Set up resource groups, Key Vault, and App Config for secrets and thresholds.

### Phase 2 – Model Training Pipeline (8–10 hours)

* Implement fraud_detection_training_pipeline.yml:
  - Data preprocessing (transaction features, velocity, device signals).
  - Train baseline model (GBDT or lightweight transformer).
  - Evaluate with ROC‑AUC, PR‑AUC, F1.
  - Register model in Azure ML.
* Add fraud_detection_training_pipeline_with_schedule.yml for daily/weekly retraining triggers.

### Phase 3 – Real‑Time Decision Service Deployment (8–10 hours)

* Containerize fraud decision API (Python/Flask or FastAPI).
* Deploy to AKS using decision_service_deployment.yaml.
* Integrate with Azure ML Online Endpoint for scoring.
* Expose via LoadBalancer with autoscaling enabled.
* Connect Redis cache for feature lookups.

### Phase 4 – Monitoring & Alerts (6–8 hours)

* Apply `app_insights_config.yaml` to AKS deployment.
* Import `latency_alert_rules.json` into Azure Monitor.
* Configure `model_drift_monitor.yaml` for drift detection.
* Add `business_kpi_monitor.yam`l for FPR and FCR.
* Deploy `fraud_detection_workbook.json` for unified dashboard.

### Phase 5 – Case Management Workflow (8–10 hours)

* Implement `case_management_workflow.md` design:
  - Decision service emits case events to Service Bus.
  - Logic Apps orchestrate intake, enrichment, assignment, SLA timers.
  - Analysts triage via Case UI (Teams/Email links).
  - Feedback loop sends labels to Event Hub → retraining pipeline.
* Test SLA breach, KYC routing, and feedback ingestion.

### Phase 6 – Documentation & Runbook (4–6 hours)

* Finalize `README.md` with references to all manifests and usage guides.
* Add `fraud_detection_runbook.md` for operational response.
* Include glossary and ASCII diagram in `case_management_workflow.md`.
* Provide Quick Interpretation Guide for dashboard signals.

## 🕒 Estimated Timeline (40–50 hours)


| Phase                | Hours  | Deliverables                                                     |
|----------------------|--------|------------------------------------------------------------------|
| 1. Infra Setup       | 6–8    | Azure ML, AKS, App Insights, Service Bus, Logic Apps provisioned |
| 2. Training Pipeline | 8–10   | Baseline fraud model + retraining pipeline                       |
| 3. Decision Service  | 8–10   | AKS API deployed + ML endpoint integration                       |
| 4. Monitoring        | 6–8    | Latency, drift, KPI monitors + workbook dashboard                |
| 5. Case Management   | 8–10   | Service Bus + Logic Apps workflow + analyst UI                   |
| 6. Docs & Runbook    | 4–6    | README, runbook, glossary, diagrams                              |


**Total**: ~40–50 hours

## ✅ MVP Completion Criteria

* Fraud decision API live on AKS, scoring transactions in real time.
* Application Insights collecting latency metrics.
* Azure Monitor alerts firing for latency and drift.
* Business KPIs (FPR, FCR) tracked daily.
* Case management workflow routing ambiguous cases to analysts.
* Documentation and runbook ready for operations.