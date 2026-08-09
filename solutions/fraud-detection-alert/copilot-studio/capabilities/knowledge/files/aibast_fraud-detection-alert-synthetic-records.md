# Fraud Detection and Alert Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/fraud_detection_alert_stack/fraud_detection_alert_agent.py`
- Source SHA-256: `da09e0e8d345d0aa5fa21abcbf5e504aaf4accd85d45d4c33fa6e9a8163e2ee0`
- Expected tool: `FraudDetectionAlertAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `TRANSACTIONS`

```json
{
  "TXN-90001": {
    "account": "4532-XXXX-8891",
    "amount": 4850.0,
    "cardholder": "James Peterson",
    "category": "electronics",
    "channel": "card_present",
    "country": "AE",
    "merchant": "ElectroMax Dubai",
    "risk_score": 88,
    "timestamp": "2025-03-05T02:15:00"
  },
  "TXN-90002": {
    "account": "4532-XXXX-8891",
    "amount": 2100.0,
    "cardholder": "James Peterson",
    "category": "jewelry",
    "channel": "card_present",
    "country": "AE",
    "merchant": "Gold Souq Trading",
    "risk_score": 92,
    "timestamp": "2025-03-05T02:42:00"
  },
  "TXN-90003": {
    "account": "4716-XXXX-3304",
    "amount": 12500.0,
    "cardholder": "Lisa Wang",
    "category": "crypto",
    "channel": "online",
    "country": "US",
    "merchant": "CryptoSwap Exchange",
    "risk_score": 75,
    "timestamp": "2025-03-04T18:30:00"
  },
  "TXN-90004": {
    "account": "4716-XXXX-3304",
    "amount": 9800.0,
    "cardholder": "Lisa Wang",
    "category": "crypto",
    "channel": "online",
    "country": "US",
    "merchant": "CryptoSwap Exchange",
    "risk_score": 82,
    "timestamp": "2025-03-04T18:35:00"
  },
  "TXN-90005": {
    "account": "5412-XXXX-6678",
    "amount": 189.99,
    "cardholder": "Robert Miles",
    "category": "retail",
    "channel": "online",
    "country": "US",
    "merchant": "Amazon.com",
    "risk_score": 12,
    "timestamp": "2025-03-05T10:20:00"
  },
  "TXN-90006": {
    "account": "5412-XXXX-6678",
    "amount": 3200.0,
    "cardholder": "Robert Miles",
    "category": "wire_transfer",
    "channel": "online",
    "country": "NG",
    "merchant": "WireTransfer-NG",
    "risk_score": 95,
    "timestamp": "2025-03-05T11:05:00"
  },
  "TXN-90007": {
    "account": "4024-XXXX-1190",
    "amount": 67.5,
    "cardholder": "Elena Vasquez",
    "category": "grocery",
    "channel": "contactless",
    "country": "US",
    "merchant": "Whole Foods Market",
    "risk_score": 5,
    "timestamp": "2025-03-05T09:15:00"
  }
}
```

### `ALERT_RULES`

```json
{
  "RULE-001": {
    "description": "Multiple high-value transactions within 1 hour",
    "name": "Velocity Check",
    "severity": "high",
    "threshold": "2+ transactions over $1,000 within 60 minutes"
  },
  "RULE-002": {
    "description": "Transaction in country with no prior history",
    "name": "Geographic Anomaly",
    "severity": "high",
    "threshold": "First transaction in high-risk country"
  },
  "RULE-003": {
    "description": "Unusual crypto exchange activity",
    "name": "Crypto Purchase Spike",
    "severity": "medium",
    "threshold": "Crypto transactions exceeding 3x normal volume"
  },
  "RULE-004": {
    "description": "Wire transfer to FATF grey/black list country",
    "name": "Wire to High-Risk Country",
    "severity": "critical",
    "threshold": "Any wire to listed jurisdiction"
  },
  "RULE-005": {
    "description": "Rapid online purchases across merchants",
    "name": "Card-Not-Present Velocity",
    "severity": "medium",
    "threshold": "5+ online transactions within 30 minutes"
  },
  "RULE-006": {
    "description": "Password change followed by high-value transaction",
    "name": "Account Takeover Pattern",
    "severity": "critical",
    "threshold": "Transaction within 2 hours of credential change"
  }
}
```

### `FRAUD_PATTERNS`

```json
{
  "account_takeover": {
    "description": "Unauthorized access to account via compromised credentials",
    "frequency": "increasing",
    "indicators": [
      "Login from new device/IP",
      "Immediate password and contact info change",
      "Large transfer or purchase within hours"
    ]
  },
  "bust_out": {
    "description": "Deliberate credit line exhaustion before default",
    "frequency": "moderate",
    "indicators": [
      "Rapid utilization increase to near-limit",
      "Cash advance activity",
      "Payments stop after utilization spike"
    ]
  },
  "card_cloning": {
    "description": "Physical card duplicated; used at multiple locations simultaneously",
    "frequency": "common",
    "indicators": [
      "Transactions in geographically distant locations within short timeframe",
      "Card-present transactions after reported card-not-present use"
    ]
  },
  "synthetic_identity": {
    "description": "Fictitious identity created using mixed real and fake data",
    "frequency": "increasing",
    "indicators": [
      "SSN with no credit history prior to 2 years ago",
      "Authorized user on multiple unrelated accounts",
      "Address inconsistencies"
    ]
  }
}
```

### `INVESTIGATION_CASES`

```json
{
  "INV-2025-301": {
    "alert_txns": [
      "TXN-90001",
      "TXN-90002"
    ],
    "analyst": "Karen Wright",
    "notes": "Synthetic contact evidence indicates no travel. Card block and replacement are proposed protective actions pending authorization.",
    "opened": "2025-03-05",
    "pattern": "card_cloning",
    "priority": "high",
    "rules_triggered": [
      "RULE-001",
      "RULE-002"
    ],
    "status": "open"
  },
  "INV-2025-302": {
    "alert_txns": [
      "TXN-90006"
    ],
    "analyst": "David Chen",
    "notes": "Synthetic wire followed a password reset by 90 minutes. Escalation and SAR review are proposed; no filing or account action occurred.",
    "opened": "2025-03-05",
    "pattern": "account_takeover",
    "priority": "critical",
    "rules_triggered": [
      "RULE-004"
    ],
    "status": "escalated"
  },
  "INV-2025-303": {
    "alert_txns": [
      "TXN-90003",
      "TXN-90004"
    ],
    "analyst": "Karen Wright",
    "notes": "Customer confirmed crypto purchases. Monitoring for additional activity.",
    "opened": "2025-03-04",
    "pattern": null,
    "priority": "medium",
    "rules_triggered": [
      "RULE-003"
    ],
    "status": "under_review"
  }
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### FDA-01 — Fraud Operations Manager

- Prompt: What is the most urgent alert in the overnight queue, and what evidence makes it urgent?
- Operation: `alert_triage`
- Arguments: `{}`
- Required factual anchors: `TXN-90006`, `Critical`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Fraud Alert Triage

**High-Risk Transactions:** 5
**Flagged Amount:** $32,450.00
**Open Cases:** 3

## Flagged Transactions

| TXN ID | Account | Amount | Merchant | Country | Risk | Level |
|---|---|---|---|---|---|---|
| TXN-90001 | 4532-XXXX-8891 | $4,850.00 | ElectroMax Dubai | AE | 88 | Critical |
| TXN-90002 | 4532-XXXX-8891 | $2,100.00 | Gold Souq Trading | AE | 92 | Critical |
| TXN-90003 | 4716-XXXX-3304 | $12,500.00 | CryptoSwap Exchange | US | 75 | High |
| TXN-90004 | 4716-XXXX-3304 | $9,800.00 | CryptoSwap Exchange | US | 82 | Critical |
| TXN-90006 | 5412-XXXX-6678 | $3,200.00 | WireTransfer-NG | NG | 95 | Critical |

## Alert Rules Triggered

- **RULE-001 (Velocity Check):** Multiple high-value transactions within 1 hour [HIGH]
- **RULE-002 (Geographic Anomaly):** Transaction in country with no prior history [HIGH]
- **RULE-003 (Crypto Purchase Spike):** Unusual crypto exchange activity [MEDIUM]
- **RULE-004 (Wire to High-Risk Country):** Wire transfer to FATF grey/black list country [CRITICAL]
- **RULE-005 (Card-Not-Present Velocity):** Rapid online purchases across merchants [MEDIUM]
- **RULE-006 (Account Takeover Pattern):** Password change followed by high-value transaction [CRITICAL]
```

### FDA-02 — Fraud Analyst

- Prompt: Show me the account activity behind the Dubai alert so I can investigate the sequence.
- Operation: `transaction_analysis`
- Arguments: `{}`
- Required factual anchors: `4532-XXXX-8891`, `TXN-90002`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Transaction Analysis

## All Monitored Transactions

| TXN ID | Cardholder | Amount | Merchant | Category | Country | Channel | Risk |
|---|---|---|---|---|---|---|---|
| TXN-90001 | James Peterson | $4,850.00 | ElectroMax Dubai | electronics | AE | card_present | 88 |
| TXN-90002 | James Peterson | $2,100.00 | Gold Souq Trading | jewelry | AE | card_present | 92 |
| TXN-90003 | Lisa Wang | $12,500.00 | CryptoSwap Exchange | crypto | US | online | 75 |
| TXN-90004 | Lisa Wang | $9,800.00 | CryptoSwap Exchange | crypto | US | online | 82 |
| TXN-90005 | Robert Miles | $189.99 | Amazon.com | retail | US | online | 12 |
| TXN-90006 | Robert Miles | $3,200.00 | WireTransfer-NG | wire_transfer | NG | online | 95 |
| TXN-90007 | Elena Vasquez | $67.50 | Whole Foods Market | grocery | US | contactless | 5 |

## Account-Level Summary

| Account | Transactions | Total Amount | Max Risk |
|---|---|---|---|
| 4532-XXXX-8891 | 2 | $6,950.00 | 92 |
| 4716-XXXX-3304 | 2 | $22,300.00 | 82 |
| 5412-XXXX-6678 | 2 | $3,389.99 | 95 |
| 4024-XXXX-1190 | 1 | $67.50 | 5 |
```

### FDA-03 — SIU Investigator

- Prompt: Which active case resembles a coordinated fraud pattern, and what makes that only a hypothesis?
- Operation: `pattern_detection`
- Arguments: `{}`
- Required factual anchors: `INV-2025-301`, `Card Cloning`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Fraud Pattern Detection

## Known Fraud Patterns

### Card Cloning

**Description:** Physical card duplicated; used at multiple locations simultaneously
**Frequency:** Common

**Indicators:**

- Transactions in geographically distant locations within short timeframe
- Card-present transactions after reported card-not-present use

### Account Takeover

**Description:** Unauthorized access to account via compromised credentials
**Frequency:** Increasing

**Indicators:**

- Login from new device/IP
- Immediate password and contact info change
- Large transfer or purchase within hours

### Bust Out

**Description:** Deliberate credit line exhaustion before default
**Frequency:** Moderate

**Indicators:**

- Rapid utilization increase to near-limit
- Cash advance activity
- Payments stop after utilization spike

### Synthetic Identity

**Description:** Fictitious identity created using mixed real and fake data
**Frequency:** Increasing

**Indicators:**

- SSN with no credit history prior to 2 years ago
- Authorized user on multiple unrelated accounts
- Address inconsistencies

## Pattern Matches in Active Cases

- **INV-2025-301:** Card Cloning — Physical card duplicated; used at multiple locations simultaneously
- **INV-2025-302:** Account Takeover — Unauthorized access to account via compromised credentials
```

### FDA-04 — Risk Leader

- Prompt: Prepare the critical wire case for SIU review and tell me what actions actually occurred.
- Operation: `investigation_summary`
- Arguments: `{"case_id": "INV-2025-302"}`
- Required factual anchors: `INV-2025-302`, `no external action`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Investigation: INV-2025-302

- **Status:** Escalated
- **Priority:** Critical
- **Analyst:** David Chen
- **Opened:** 2025-03-05
- **Pattern:** Account Takeover
- **Notes:** Synthetic wire followed a password reset by 90 minutes. Escalation and SAR review are proposed; no filing or account action occurred.

## Associated Transactions

- **TXN-90006:** $3,200.00 at WireTransfer-NG (NG) — Risk: 95

## Rules Triggered

- **RULE-004:** Wire to High-Risk Country [CRITICAL]

## Proposed Routing

- Queue: SIU
- Status: Prepared for authorized investigator review; no external action taken
```

## Evidence boundary

This snapshot does not authorize fraud accusations or determinations, legal or regulatory advice, customer contact, card or account blocks, payment or wire actions, case routing, SAR or other filings, or external record changes. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
