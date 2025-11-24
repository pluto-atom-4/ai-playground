# 📊 How to Apply `model_drift_monitor.yaml`

This document explains how to use the `model_drift_monitor.yaml` file to configure **Azure ML Data Drift Monitoring** for the fraud detection model.

---

## 🧩 Purpose

The drift monitor compares **live transaction features** against a **baseline dataset**.  
It triggers alerts if statistical thresholds are exceeded, indicating that the model may no longer be aligned with current data.

---

## 🚀 Steps to Apply

1. **Open Azure ML Studio**  
   Navigate to your **Azure Machine Learning workspace**.

2. **Create a new monitor**  
   - Go to **Monitoring** → **Data Drift**.  
   - Choose **Import from YAML**.  
   - Upload the `model_drift_monitor.yaml` file.

3. **Update placeholders**  
   Replace the following values in the YAML with your actual Azure ML resources:  
   - `azureml:transactions_dataset@latest` → Your production dataset  
   - `azureml:fraud_model_output@latest` → Your deployed fraud detection model  
   - `azureml:transactions_baseline_dataset@latest` → Your baseline dataset (e.g., last month’s clean data)  
   - `fraud-alert-group` → Your configured Action Group for notifications

4. **Save and enable**  
   Once imported, the monitor will run **daily checks** comparing live data against the baseline.

5. **Verify alerts**  
   Ensure your **Action Group** is configured to notify via email, SMS, Teams, Slack, or trigger Logic Apps.

---

## 🔧 Customization

- **Thresholds**:  
  - Adjust `PopulationStabilityIndex` threshold (default 0.2) for stricter or looser drift detection.  
  - Modify `KolmogorovSmirnovTest` threshold (default 0.05) for sensitivity to distribution changes.

- **Frequency**:  
  - Change `schedule.frequency: Daily` to `Weekly` or `Hourly` depending on your monitoring needs.

- **Actions**:  
  - Add multiple action groups for different notification channels (e.g., SOC team, data science team).

---

## 📊 Best Practices

- Combine drift monitoring with **latency and error monitoring** for full coverage.  
- Use **Azure Monitor Workbooks** to visualize drift metrics over time.  
- Trigger **automated retraining pipelines** when drift alerts fire, ensuring models stay fresh.  
- Periodically update the **baseline dataset** to reflect new normal behavior.

---
