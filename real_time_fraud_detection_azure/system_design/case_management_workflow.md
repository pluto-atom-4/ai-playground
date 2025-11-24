# 📄 Case management workflow for analyst review (Service Bus + Logic Apps)

```text
                ┌─────────────────────┐
                │   Decision Service  │
                │   (AKS Fraud API)   │
                └─────────┬───────────┘
                          │
                          │ Case events (gray zone, review needed)
                          ▼
                ┌─────────────────────┐
                │   Azure Service Bus │
                │  fraud-cases-inbound│
                └─────────┬───────────┘
                          │
                          │ Routes to topic subscriptions
                          ▼
        ┌───────────────────────────────────────────┐
        │ fraud-cases-topic                         │
        │  ├─ high-risk subscription                │
        │  ├─ medium-risk subscription              │
        │  ├─ kyc-review subscription               │
        │  └─ merchant-escalation subscription      │
        └───────────────────────────────────────────┘
                          │
                          │ Messages delivered
                          ▼
                ┌─────────────────────┐
                │    Logic Apps       │
                │  Case Orchestration │
                └─────────┬───────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ Enrichment │   │ Assignment │   │ SLA/Alerts │
   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
         │                │                │
         ▼                ▼                ▼
   ┌───────────────────────────────────────────┐
   │ Analyst Case UI (Portal/Teams/Email link) │
   └───────────────────────────────────────────┘
                          │
                          │ Analyst reviews, adds notes, resolves
                          ▼
                ┌─────────────────────┐
                │   Case Database     │
                │ (Cosmos DB / SQL)   │
                └─────────┬───────────┘
                          │
                          │ Feedback loop
                          ▼
                ┌─────────────────────┐
                │   Event Hub / ML    │
                │ Retraining Pipeline │
                └─────────────────────┘

```

## 🔎 Diagram Highlights
* **Decision Service** emits case events when confidence is low or rules require human review.
* **Service Bus** queues and topics route cases to appropriate subscriptions (high‑risk, medium‑risk, KYC, merchant escalation).
* **Logic Apps** orchestrate intake, enrichment, assignment, SLA timers, and notifications.
* **Analysts** triage cases via portal or Teams/Email links.
* **Case Database** stores records and audit logs.
* **Event Hub + ML Pipeline** receive feedback for retraining models._

---

## 🧠 Purpose and outcomes

* **Goal**: Route high-risk or ambiguous fraud decisions to human analysts for timely review, resolution, and feedback into the ML pipeline.
* **Outcomes**: Reduced false positives, faster fraud containment, structured feedback loop, and auditable actions.

---

## 🏗️ Architecture overview

* **Decision service (AKS)**: Emits case events for review when confidence falls in a gray zone or rules require human verification.
* **Azure Service Bus**: Decouples producers and consumers; queues capture cases, topics enable fan-out to specialized flows.
* **Azure Logic Apps**: Orchestrates case lifecycle: intake, enrichment, routing, notifications, SLAs, and resolution updates.
* **Case UI** (e.g., internal portal): Analysts triage, add notes, change status, and submit outcomes.
* **Data sinks**: Cosmos DB/SQL for case records; ADLS for audit logs; Event Hub for feedback signals to ML.

## 🧩 Service Bus design

* **Namespace**: fraud-ops-bus
* **Entities**:
  - **Queue**: fraud-cases-inbound
    + **Purpose**: Primary intake from Decision service
  - **Topic**: fraud-cases-topic 
    + **Subscriptions**:
      * high-risk (score ≥ threshold_high)
      * medium-risk (threshold_mid ≤ score < threshold_high)
      * kyc-review (identity anomalies)
      * merchant-escalation (merchant-triggered disputes)
* **Dead-letter queues**: Enabled on all entities for poison messages and processing failures.

---

## 🧾 Message schema

* **id**: Unique case ID (UUID)
* **timestamp**: ISO-8601 event time
* **actor**: User/account ID, merchant ID
* **transaction**: Amount, currency, merchant, device, IP, geo
* **risk**: Score, model_version, rules_triggered[]
* **context**: Featureset_id, session_id
* **action_suggested**: block | challenge | allow_with_review
* **sla**: priority, due_at
* **links**: deep links to Decision logs, SHAP/explanations, trace IDs

---

## 🔄 Logic Apps workflows

### Case intake and enrichment

* **Trigger**: Service Bus queue message (fraud-cases-inbound)
* **Steps**:
  - **Validate**: Schema and required fields 
  - **Enrich**:
    + Pull user history and velocity features (Feature Store API)
    + Fetch merchant risk profile (Cosmos DB/SQL)
    + Attach explainability artifacts (SHAP summaries)
  - **Persist**: Create case record (Cosmos DB/SQL) with status=open 
  - **Route**: Publish to fraud-cases-topic with routing properties (risk tier, KYC flags)

### Routing and assignment

* **Trigger**: Topic subscription (e.g., high-risk)
* **Steps**:
  - **Assign**: Choose analyst based on skill/availability (table lookup)
  - **Notify**: Send Teams/Email to assigned analyst with case link 
  - **Start SLA timer**: Create reminder and escalation timer (Logic Apps recurrence)

### Investigation and resolution

* **Trigger**: Webhook from Case UI on status change
* **Steps**:
  - **Update**: Persist notes, attachments, final decision (confirm_fraud | legit | partial)
  - **Emit feedback**:
    + Event to Event Hub: model_feedback with label and featureset_id
    + Queue to retraining trigger if label volume threshold met
  - **Close case**: status=closed, store audit trail to ADLS
  - **Notify**: Merchant/customer comms via Logic Apps if policy requires

### Escalation handling

* **Trigger**: SLA breach or repeated reopen
* **Steps**:
  - **Escalate**: Reassign to senior analyst or Fraud Ops lead
  - **Notify**: Priority alert to SOC channel
  - **Snapshot**: Export case bundle (evidence, logs) to ADLS for compliance

## 🎛️ Routing logic

* **High risk**: score ≥ threshold_high → high-risk subscription, priority=P1, due_at=+2h
* **Medium risk**: threshold_mid ≤ score < threshold_high → medium-risk, priority=P2, due_at=+8h
* **Identity flags**: rules_triggered contains KYC → kyc-review subscription
* **Merchant disputes**: merchant_escalation=true → merchant-escalation subscription

---

## 🔐 Security and governance

* **AuthN/AuthZ**: Managed identities for Logic Apps; RBAC on Service Bus and databases
* **Data protection**: PII minimized in messages; sensitive fields encrypted at rest; private endpoints
* **Auditability**: Immutable logs in ADLS; correlation IDs across Decision service, Logic Apps, and Case UI
* **Compliance**: Retention policies per region; access reviews and least privilege

---

## ⚙️ Deployment notes

### Infrastructure:

* Provision Service Bus namespace, queues, topic + subscriptions
* Deploy Logic Apps with connections (Service Bus, Cosmos DB/SQL, Event Hub, Email/Teams)

### Configs:

Thresholds (threshold_mid, threshold_high) via App Config/Key Vault
SLA timers and escalation contacts in Config tables

### Observability:

* Logic Apps run history alerts on failures
* Metrics: case volume by tier, SLA breaches, time-to-resolution

---

## 🔁 Feedback loop to ML

* **Label capture**: Final decision written with label and featureset_id
* **Event emission**: model_feedback events to Event Hub for ingestion
* **Retraining triggers**: Batch labels daily; auto-trigger retraining when drift/KPI alerts coincide with label volume threshold

---

## 🧪 Testing scenarios

* **Poison message**: Invalid schema → DLQ, alert, sample message retained
* **SLA breach**: Medium-risk case exceeds due_at → escalation flow verifies
* **KYC route**: Identity anomaly correctly lands in kyc-review subscription
* **Feedback path**: Closed case produces model_feedback and appears in training dataset

---

## 📋 Checklist for go-live

* **Service Bus**: Queues/topics/subscriptions created, DLQs monitored
* **Logic Apps**: Connections authorized, error handling added, alerts configured
* **Case UI**: Webhooks integrated, deep links functioning, RBAC enforced
* **Data**: Cosmos DB/SQL schemas validated, ADLS containers versioned
* **Runbooks**: On-call rotation aware; escalation contacts verified

---

## 📖 Glossary of Terms

- **ADLS (Azure Data Lake Storage):** A scalable cloud storage service from Azure designed for big data analytics.  
  🔗 [Azure Data Lake Storage documentation](https://learn.microsoft.com/azure/storage/data-lake-storage/)

- **IP (Internet Protocol):** A numerical label assigned to each device connected to a computer network that uses the Internet Protocol for communication.  
  🔗 [What is IP?](https://learn.microsoft.com/windows-server/networking/technologies/ip-addressing/)

- **SHAP (SHapley Additive exPlanations):** A popular explainability method that assigns feature importance values to individual predictions.  
  🔗 [SHAP explainability overview](https://shap.readthedocs.io/en/latest/)

- **KYC (Know Your Customer):** Regulatory process of verifying the identity of clients to prevent fraud, money laundering, and terrorism financing.  
  🔗 [Know Your Customer (KYC) basics](https://www.investopedia.com/terms/k/knowyourcustomer.asp)

- **SOC (Security Operations Center):** A centralized unit that deals with security issues on an organizational and technical level.  
  🔗 [What is a SOC?](https://learn.microsoft.com/security/operations/)

- **SLA (Service Level Agreement):** A documented commitment between a service provider and a client that specifies performance standards.  
  🔗 [Service Level Agreement definition](https://azure.microsoft.com/support/legal/sla/)

- **DLQ (Dead-Letter Queue):** A secondary queue used to store messages that cannot be processed or delivered successfully.  
  🔗 [Dead-letter queues in Azure Service Bus](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-dead-letter-queues)

---

## 📚 References

- Azure Service Bus: [Service Bus overview](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview)  
- Azure Logic Apps: [Logic Apps overview](https://learn.microsoft.com/azure/logic-apps/logic-apps-overview)  
- Azure Monitor: [Azure Monitor overview](https://learn.microsoft.com/azure/azure-monitor/overview)
