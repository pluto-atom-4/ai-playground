# 📸 Sample Dashboard Layout (Text‑Only Description)

## Layout Summary:
* Two rows, two charts per row for a clean 2×2 grid.
* Top row focuses on technical health (latency + drift).
* Bottom row focuses on business KPIs (FPR + FCR).
* Threshold lines and color cues make it easy to spot anomalies at a glance.
* Analysts can filter by time range (last 24h, 7d, 30d) using workbook controls.

When you open the Fraud Detection Workbook, the dashboard will be organized into four main panels arranged in a grid:

### Top Row:

#### ⚡ Average Request Latency (ms)
* A time‑series line chart showing average latency over 5‑minute bins.
* X‑axis: Time (last 24 hours or 7 days).
* Y‑axis: Latency in milliseconds.
* Visual cue: Spikes above 2000 ms highlighted in red.

#### 📊 Model Drift (PSI)
* A daily line chart showing the Population Stability Index (PSI).
* X‑axis: Date.
* Y‑axis: PSI values.
* Threshold line at 0.2 to indicate drift alert zone.
* Visual cue: Bars or dots turning orange/red when PSI exceeds threshold.

### Bottom Row

#### 🚫 False Positive Rate (FPR)
* A daily line chart showing the percentage of legitimate transactions incorrectly flagged.
* X‑axis: Date.
* Y‑axis: Percentage (0–100%).
* Threshold line at 5%.
* Visual cue: Red shading when FPR > 5%.

#### ✅ Fraud Capture Rate (FCR)
* A daily line chart showing the percentage of fraudulent transactions correctly identified.
* X‑axis: Date.
* Y‑axis: Percentage (0–100%).
* Threshold line at 90%.
* Visual cue: Green shading when FCR ≥ 90%, orange/red when below.
