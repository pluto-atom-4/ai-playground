# 🛡️ System design: Real-time fraud detection system with Azure


## 🧠 Overview

Real-time fraud detection identifies and blocks suspicious activity (e.g., payments, logins, account changes) in 
milliseconds while maintaining high precision and minimizing user friction. This design combines streaming ingestion, 
low-latency inference, rules, and ML models with continuous learning loops and robust MLOps on Azure.

--- 

## 🎯 Goals

* Low-latency decisions
* High precision/recall
* Scalable and resilient
* Continuous learning
* Governance-first

---

## 🏗️ Azure-based Architecture

```text
+----------------------+        +-----------------------+        +--------------a----------+
| Client apps / APIs   | --->   | Azure API Management  | --->   | Decision service (AKS) |
| (Web, Mobile, POS)   |        | (throttling, auth)    |        | w/ Rules + ML scoring  |
+----------------------+        +-----------------------+        +------------------------+
          |                                                          |             |
          v                                                          v             v
+----------------------+     +---------------------------+     +------------------------+
| Event ingestion      | --> | Stream processing (ASA or| --> | Features & cache (Redis|
| (Event Hubs / Kafka) |     | Functions/Databricks)    |     | + Azure Feature Store) |
+----------------------+     +---------------------------+     +------------------------+
          |                                                          |
          v                                                          v
+----------------------+     +---------------------------+     +------------------------+
| Transaction store    |     | Models (Azure ML Online  |     | Case mgmt & alerts     |
| (Cosmos DB / SQL DB) |     | Endpoints / AKS)         |     | (Service Bus + Logic   |
+----------------------+     +---------------------------+     | Apps / Sentinel)       |
                                                               +------------------------+
          |
          v
+----------------------+
| Data lake & warehouse|
| (ADLS + Synapse)     |
+----------------------+
          |
          v
+----------------------+
| Training pipelines   |
| (Azure ML Pipelines) |
+----------------------+

```

## 🧩 Components

🧩 **Decision service (AKS / App Service)**
  - **Real-time scoring API**: Accepts transaction context, fetches features, applies rules, calls ML endpoint, and returns risk + action. 
  - **Policy engine**: Business rules (velocity checks, geo anomalies, device reputation) with explainable outputs. 
  - **Action router**: Block, step-up auth, hold for review, or allow. 

🧩 **Event ingestion (Event Hubs / Kafka)**
  - **Stream of events**: Transactions, logins, device changes, chargebacks, user feedback.
  - **Partitioning strategy**: By account/merchant/region for ordering and scale.

🧩 **Stream processing (Azure Stream Analytics / Functions / Databricks)**
  - **Feature updates**: Sliding window aggregates (e.g., spend velocity, device frequency, failed attempts).
  - **Anomaly signals**: Real-time outlier scores, graph edge updates.

🧩 **Feature store & cache (Azure Feature Store + Redis)**
  - **Hot features**: Recent counts, velocity metrics, device reputation cached for sub-ms retrieval.
  - **Consistency**: Same features for training and inference.

🧩 **Models (Azure ML Online Endpoints / AKS)**
  - **Primary ranker**: Gradient boosted trees (e.g., LightGBM/XGBoost) for tabular signals.
  - **Deep models**: Sequence models (Transformers) for behavioral patterns; graph embeddings for collusion rings.
  - **Ensemble**: Blend ML score with calibrated thresholds and rules.

🧩 **Data stores (Cosmos DB / SQL)**
  - **Transactions & entities**: Users, devices, merchants, cards, IPs, session metadata.
  - **Embeddings & profiles**: Persist per-entity features for audits and analysis.

🧩 **Data lake & warehouse (ADLS + Synapse)**
  - **Immutable logs**: Raw events, decisions, outcomes (chargebacks, disputes).
  - **Analytics**: Offline aggregates, cohort analyses, feature backfills.

🧩 **Case management & alerts (Service Bus + Logic Apps + Sentinel)**
  - **Queues for review**: Route high-risk cases to analysts.
  - **Alerting**: Incident creation, dashboards, SOC integration.

🧩 **Observability (Azure Monitor + Application Insights)**
  - **Latency and reliability**: P95–P99 decision latency, error rates.
  - **Model health**: Drift, performance, feature pipeline freshness.

---

## 🧪 Models and Features

### **🧬Feature categories**:

🧬 **Velocity features**:
  - **Examples**: Transactions per minute, amount deltas, failed attempts rate.

🧬 **Device & network signals**:
  - **Examples**: Device fingerprint rarity, IP ASN reputation, VPN/TOR detection.

🧬 **User behavior sequences**:
  - **Examples**: Time-between-actions, navigation paths, day-of-week patterns.

🧬 **Graph features**:
  - **Examples**: Shared devices/cards/emails; centrality, community membership.

🧬 **Merchant/context features**
  - **Examples**: MCC risk, average ticket size, refund ratio, geo distance.

### **Model options**:
 
| Model type                                         | Strengths              | Use cases            |
|----------------------------------------------------|------------------------|----------------------|
| Gradient boosted trees (GBDT)                      | Robust, interpretable  | Primary risk scoring |
| Sequence transformers <br/>(BERT-style for events) | Temporal patterns      | Account takeover     |
| Graph embeddings<br/>(GraphSAGE/Node2Vec)          | Collusion detection    | Synthetic identity   |
| Autoencoders / Isolation Forest                    | Unsupervised anomalies | Cold-start entities  |

---

## 🏋️ Training Pipelines on Azure

🏋️ **Data ingestion & labeling (Data Factory / Synapse)**:
  - **Inputs**: Transactions, device logs, disputes/chargebacks, analyst labels.
  - **Labeling logic**: Positive labels from confirmed fraud; negatives from aged non-disputed transactions.

🏋️ **Preprocessing (Databricks / Azure ML)**:
  - **Balancing**: Stratified sampling, class weights, focal loss for imbalance.
  - **Data balancing**: Windowed aggregates, graph construction, embeddings.

🏋️ **Model training (Azure ML Pipelines)**:
  - **GBDT track**: LightGBM/XGBoost with hyperparameter sweep.
  - **Sequence track**: PyTorch transformers on event sequences.
  - **Graph track**: Embedding generation + downstream classifier.
  - **Calibration**: Platt scaling/Isotonic regression for calibrated risk scores.

🏋️ **Evaluation**:
  - **Metrics**: ROC-AUC, PR-AUC, F1, cost-based utility, false positive rate at target recall.
  - **Backtesting**: Rolling windows; temporal cross-validation; cohort-specific metrics.

🏋️ **Registration & deployment (Azure ML Registry + Online Endpoints)**:
  - **Versioning**: Full lineage of data, features, code, params.
  - **Rollout**: Shadow mode → canary → phased regional rollout; autoscaling on AKS.

🏋️ **Monitoring & retraining (Azure Monitor + ML Pipelines)**:
  - **Drift detection**: PSI on features, KS tests, performance triggers.
  - **Automated retraining**: Nightly incremental training; hotfix pipelines for incidents.

---

## ⚡ Real-time Decisioning Flow

1. **Receive transaction**: API Management forwards to Decision service.
2. **Assemble context**: Fetch hot features from Redis; enrich with entity profiles from Cosmos DB.
3. **Apply rules**: Quick eliminations (e.g., blacklist), velocity hard-thresholds.
4. **Score with ML**: Call Azure ML endpoint; get calibrated risk score and reason codes.
5. **Decide action**: Block, challenge (MFA/step-up), allow, or queue for review via Service Bus.
6. **Log and emit events**: Persist decision, push to Event Hubs and ADLS for feedback.
7. **Feedback**: Outcomes (chargebacks, user confirmations) feed training datasets.

---

## 🌍 Scalability, Reliability, and Security

📈 **Performance**:
  - **Caching**: Redis for hot features and prior decisions.
  - **Batch precompute**: Nightly feature updates for cold features; on-demand delta updates.

🛡️ **Resilience**:
  - **Circuit breakers**: Fallback to rules-only mode if ML endpoint degrades.
  - **Idempotency**: Transaction keys to avoid double-processing.
  - **Geo-redundancy:**: Multi-region deployment with traffic manager failover.

🔒 **Security & governance**:
  - **Private endpoints**: Secure service-to-service calls.
  - **Managed identities**: Least-privilege access to data and models.
  - **Audit trails**: Full decision trace, features snapshot, model version.
 
---

## 📊 Evaluation, Explainability, and Operations

📊 **Continuous evaluation**:
  - **Dashboards**: P95 latency, approval/deny rates, precision/recall, business impact.
  - **Segment health**: New users, high-value merchants, regions.

🧑‍💻 **Explainability**:
  - **SHAP/feature importance**: Provide reason codes for analyst review and policy tuning.
  - ** Decision logs**: Store inputs, features, model version, rule hits.

⚙️ **Operations**:
  - **Runbooks**: Incident response for latency spikes, error rates.
  - **A/B testing**: Policy variants and model versions with guardrails.
---