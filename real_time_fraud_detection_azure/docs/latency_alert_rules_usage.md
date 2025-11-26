# ⚙️ How to Apply `latency_alert_rules.json`

This document explains how to use the `latency_alert_rules.json` file to configure Azure Monitor alerts for the **fraud decision service**.

---

## 🧩 Purpose

The alert rule monitors **average request latency** for the Decision service.  
It triggers an alert if latency exceeds **2000 ms** over a 5‑minute window.

---

## 🚀 Steps to Apply

1. **Open Azure Portal**  
   Navigate to your **Application Insights** resource linked to the Decision service.

2. **Import the alert rule**  
   - Go to **Alerts** → **Create Alert Rule**.  
   - Choose **Import from JSON**.  
   - Upload the `latency_alert_rules.json` file.

3. **Update placeholders**  
   Replace the following values in the JSON with your actual Azure details:  
   - `<sub-id>` → Subscription ID  
   - `<rg-name>` → Resource Group name  
   - `<app-insights-name>` → Application Insights resource name  
   - `<action-group>` → Action Group resource ID

4. **Save and enable**  
   Once imported, the rule will evaluate latency every 5 minutes and trigger alerts if thresholds are breached.

5. **Verify notifications**  
   Ensure your **Action Group** is configured to send alerts via email, SMS, Teams, Slack, or trigger Logic Apps.

---

## 🔧 Customization

- **Thresholds**: Adjust `"threshold": 2000` to a stricter SLA (e.g., 1000 ms).  
- **Frequency**: Modify `"evaluationFrequency": "PT5M"` for faster or slower checks.  
- **Actions**: Add multiple action groups for different notification channels.

---

## 📊 Best Practices

- Combine latency alerts with **error rate alerts** for full coverage.  
- Use **Azure Monitor Workbooks** to visualize latency trends.  
- Integrate alerts into **DevOps pipelines** for automated rollback or scaling actions.

---
