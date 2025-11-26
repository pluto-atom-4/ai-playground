# 🛡️ Fraud Detection System Runbook

This runbook provides **step-by-step operational guidance** for responding to alerts in the real-time fraud detection system.  
It covers latency issues, model drift, and business KPI breaches (False Positive Rate, Fraud Capture Rate).

---

## ⚡ Latency Alert Response

**Trigger:** Latency > 2000 ms (from `latency_alert_rules.json`)

**Steps:**
1. **Check Application Insights**  
   - Review request traces for spikes in duration.  
   - Identify whether latency is API Gateway, AKS container, or ML endpoint.

2. **Scale AKS Deployment**  
   - Increase replicas in `decision_service_deployment.yaml`.  
   - Verify autoscaler is enabled.

3. **Check Redis Cache**  
   - Ensure feature lookups are cached.  
   - Flush stale entries if needed.

4. **Escalation**  
   - If latency persists > 1 hour, escalate to DevOps team.  
   - Document incident in monitoring log.

---

## 📊 Model Drift Alert Response

**Trigger:** PSI > 0.2 or KS test p-value < 0.05 (from `model_drift_monitor.yaml`)

**Steps:**
1. **Validate Drift Metrics**  
   - Confirm drift is consistent across multiple features.  
   - Identify which features are most affected.

2. **Investigate Data Pipeline**  
   - Check ingestion jobs for schema changes or anomalies.  
   - Validate baseline dataset freshness.

3. **Retrain Model**  
   - Trigger retraining pipeline (`fraud_detection_training_pipeline_with_schedule.yml`).  
   - Use latest labeled data.

4. **Update Baseline Dataset**  
   - Refresh baseline to reflect new normal if drift is expected (e.g., seasonal changes).

5. **Escalation**  
   - If drift persists after retraining, escalate to Data Science team.  
   - Document incident and corrective actions.

---

## 🚫 False Positive Rate (FPR) Alert Response

**Trigger:** FPR > 5% (from `business_kpi_monitor.yaml`)

**Steps:**
1. **Review Blocked Transactions**  
   - Sample recent false positives.  
   - Identify common patterns (merchant, region, device).

2. **Adjust Rules**  
   - Relax overly strict rules in Decision service.  
   - Add exceptions for trusted merchants.

3. **Retrain Model**  
   - Balance training dataset with more legitimate transactions.  
   - Apply explainability tools (SHAP) to identify bias.

4. **Escalation**  
   - If FPR remains high > 24 hours, escalate to Fraud Ops team.  
   - Document customer impact.

---

## ✅ Fraud Capture Rate (FCR) Alert Response

**Trigger:** FCR < 90% (from `business_kpi_monitor.yaml`)

**Steps:**
1. **Review Missed Fraud Cases**  
   - Sample recent fraudulent transactions not flagged.  
   - Identify gaps in features or model logic.

2. **Enhance Feature Engineering**  
   - Add new signals (velocity, device fingerprinting, graph features).  
   - Validate feature store freshness.

3. **Retrain Model**  
   - Include recent fraud cases in training.  
   - Consider ensemble models for robustness.

4. **Escalation**  
   - If FCR remains low > 24 hours, escalate to Data Science + Fraud Ops.  
   - Document financial impact.

---

## 🧭 Combined Incident Response

If **multiple alerts fire together** (e.g., latency + drift + KPI breaches):
1. Trigger **full retraining pipeline** immediately.  
2. Scale AKS deployment to handle load.  
3. Escalate to both DevOps and Data Science teams.  
4. Document incident in central log and notify stakeholders.

---

## 📚 References

- [latency_alert_rules_usage.md](./latency_alert_rules_usage.md)  
- [model_drift_monitor_usage.md](./model_drift_monitor_usage.md)  
- [business_kpi_monitor.yaml](./business_kpi_monitor.yaml)  
- [fraud_detection_workbook.json](./fraud_detection_workbook.json)

---
