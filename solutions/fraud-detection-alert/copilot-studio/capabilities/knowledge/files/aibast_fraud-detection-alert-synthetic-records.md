# Fraud Detection and Alert Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/fraud_detection_alert_stack/fraud_detection_alert_agent.py`
- Source SHA-256: `dd4891fd0e476ed0a03e54e73023b561508e3003f089397b12383c2786c19724`
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
      "RULE-004",
      "RULE-006"
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

### `OVERNIGHT_QUEUE`

```json
[
  {
    "action": "Immediate review",
    "alerts": 23,
    "priority": "Critical",
    "value": 892000
  },
  {
    "action": "Today",
    "alerts": 67,
    "priority": "High",
    "value": 1400000
  },
  {
    "action": "48-hour queue",
    "alerts": 234,
    "priority": "Medium",
    "value": 2100000
  },
  {
    "action": "Auto-disposition",
    "alerts": 923,
    "priority": "Low",
    "value": 3200000
  }
]
```

### `CRITICAL_BREAKDOWN`

```json
[
  {
    "alerts": 8,
    "avg_value": 34000,
    "trigger": "Credential change + transfer",
    "type": "Account takeover"
  },
  {
    "alerts": 6,
    "avg_value": 28000,
    "trigger": "Multi-location velocity",
    "type": "Card fraud ring"
  },
  {
    "alerts": 5,
    "avg_value": 67000,
    "trigger": "First-time international",
    "type": "Wire fraud"
  },
  {
    "alerts": 4,
    "avg_value": 42000,
    "trigger": "Duplicate deposit",
    "type": "Check fraud"
  }
]
```

### `IMMEDIATE_ALERTS`

```json
[
  {
    "alert": "F-78234",
    "summary": "$127K wire to high-risk jurisdiction",
    "team": "Wire Team"
  },
  {
    "alert": "F-78156",
    "summary": "takeover in progress",
    "team": "Senior Analyst (SIU)"
  },
  {
    "alert": "F-78089",
    "summary": "card testing",
    "team": "Card Team"
  }
]
```

### `FRAUD_RINGS`

```json
[
  {
    "accounts": 12,
    "alert": "F-78156",
    "case_id": "FRD-2024-1847",
    "confidence_pct": 94,
    "evidence": [
      "Alert #F-78156, 12 connected accounts, $340K exposure",
      "Pattern: Same device fingerprint, 8 password resets in 2 hours"
    ],
    "exposure": 340000,
    "priority": "critical",
    "ring": "Ring 1 - Account Takeover Network",
    "short": "ATO Ring",
    "team": "Senior Analyst"
  },
  {
    "accounts": 18,
    "alert": "F-78089",
    "case_id": "FRD-2024-1848",
    "confidence_pct": 87,
    "evidence": [
      "47 cards tested in 4 hours",
      "Pattern: Gas stations (small amounts), 3 states",
      "Success rate: 23% (stolen batch indicator)"
    ],
    "exposure": 127000,
    "priority": "high",
    "ring": "Ring 2 - Card Testing",
    "short": "Card Testing",
    "team": "Card Team"
  },
  {
    "accounts": 5,
    "alert": "F-78234",
    "case_id": "FRD-2024-1849",
    "confidence_pct": 91,
    "evidence": [
      "5 accounts opened in the last 30 days",
      "Similar deposits, attempting international wires",
      "Destination: Known mule accounts"
    ],
    "exposure": 224000,
    "priority": "high",
    "ring": "Ring 3 - Wire Fraud",
    "short": "Wire Fraud",
    "team": "Wire Team"
  }
]
```

### `ATO_RING_ACCOUNTS`

```json
[
  {
    "account": "***4521",
    "balance": 89000,
    "customer": "J. Morrison",
    "status": "Compromised"
  },
  {
    "account": "***7834",
    "balance": 67000,
    "customer": "S. Chen",
    "status": "Compromised"
  },
  {
    "account": "***2156",
    "balance": 54000,
    "customer": "M. Williams",
    "status": "Attempted"
  },
  {
    "account": "***3390",
    "balance": 22000,
    "customer": "A. Patel",
    "status": "Linked (same device)"
  },
  {
    "account": "***6612",
    "balance": 18000,
    "customer": "R. Okafor",
    "status": "Linked (same device)"
  },
  {
    "account": "***1478",
    "balance": 16000,
    "customer": "L. Brooks",
    "status": "Linked (same device)"
  },
  {
    "account": "***9025",
    "balance": 15000,
    "customer": "T. Nguyen",
    "status": "Linked (same device)"
  },
  {
    "account": "***5307",
    "balance": 14000,
    "customer": "K. Alvarez",
    "status": "Linked (same device)"
  },
  {
    "account": "***8841",
    "balance": 13000,
    "customer": "D. Fischer",
    "status": "Linked (same device)"
  },
  {
    "account": "***2763",
    "balance": 12000,
    "customer": "E. Rossi",
    "status": "Linked (same device)"
  },
  {
    "account": "***4419",
    "balance": 11000,
    "customer": "P. Kim",
    "status": "Linked (same device)"
  },
  {
    "account": "***7150",
    "balance": 9000,
    "customer": "G. Hart",
    "status": "Linked (same device)"
  }
]
```

### `ACCOUNT_EVENTS`

```json
{
  "***4521": [
    {
      "event": "Password reset (new IP)",
      "time": "2:14 AM"
    },
    {
      "event": "Email changed",
      "time": "2:18 AM"
    },
    {
      "event": "Phone changed",
      "time": "2:22 AM"
    },
    {
      "event": "$15K wire initiated",
      "time": "2:34 AM"
    },
    {
      "event": "Transfer held by the AI risk model",
      "time": "2:35 AM"
    }
  ]
}
```

### `PROTECTIVE_ACTIONS`

```json
[
  {
    "action": "Account freeze",
    "count": "12",
    "status": "Ready for authorized execution"
  },
  {
    "action": "Cards blocked",
    "count": "18",
    "status": "Ready for authorized execution"
  },
  {
    "action": "Wires held",
    "count": "5 pending",
    "status": "Ready for authorized execution"
  },
  {
    "action": "Password reset",
    "count": "12",
    "status": "Queued for approval"
  }
]
```

### `PERFORMANCE_METRICS`

```json
[
  {
    "current": "94.2%",
    "current_value": 94.2,
    "higher_is_better": true,
    "metric": "Detection rate",
    "target": "90%",
    "target_value": 90
  },
  {
    "current": "2.8%",
    "current_value": 2.8,
    "higher_is_better": false,
    "metric": "False positive",
    "target": "5%",
    "target_value": 5
  },
  {
    "current": "4.2 sec",
    "current_value": 4.2,
    "higher_is_better": false,
    "metric": "Detection time",
    "target": "10 sec",
    "target_value": 10
  },
  {
    "current": "$4.8M",
    "current_value": 4.8,
    "higher_is_better": true,
    "metric": "Losses prevented",
    "target": "$4M",
    "target_value": 4
  }
]
```

### `FRAUD_TRENDS`

```json
[
  {
    "change": "+34%",
    "concern": "High concern - correlates with dark web dump",
    "type": "Account takeover"
  },
  {
    "change": "-12%",
    "concern": "Low",
    "type": "Card present"
  },
  {
    "change": "+2%",
    "concern": "Medium",
    "type": "Wire fraud"
  }
]
```

### `RECOMMENDED_CONTROLS`

```json
[
  "Deploy adaptive authentication",
  "Pilot behavioral biometrics",
  "Increase monitoring for credential changes"
]
```

### `SUMMARY_ACTIONS`

```json
{
  "immediate": [
    "SAR filing for ATO (48-hour deadline) - draft ready for the BSA officer",
    "Customer outreach (4 high-value accounts)",
    "Coordinate card team on testing pattern"
  ],
  "strategic": "Address 34% ATO increase, pilot behavioral biometrics, review credential monitoring"
}
```

### Demo walkthrough (video scenario)

A bank's 1,247-alert overnight queue. Every operation has demo defaults; nothing is blocked, sent or filed.

| Turn | User prompt | Operation | Key values |
|---|---|---|---|
| 1 | Review overnight fraud activity and show me what needs immediate attention | `alert_triage` | 1,247 alerts; Critical 23 / $892K (immediate review), High 67 / $1.4M (today), Medium 234 / $2.1M (48-hour queue), Low 923 / $3.2M (auto-disposition); critical breakdown ATO 8 ($34K avg), card ring 6 ($28K), wire 5 ($67K), check 4 ($42K); immediate #F-78234 ($127K wire), #F-78156 (takeover), #F-78089 (card testing) |
| 2 | Yes, show me the pattern analysis and connected activity | `pattern_detection` | 3 organized fraud rings: ATO network (#F-78156, 12 accounts, $340K, same device fingerprint, 8 resets in 2 hours, 94%); card testing (47 cards in 4 hours, gas stations, 3 states, 23% success, 87%); wire fraud (5 new accounts, mule destinations, 91%) |
| 3 | Yes, investigate the account takeover ring and show me the accounts | `transaction_analysis` | 12 accounts, $340K; ***4521 J. Morrison $89K compromised, ***7834 S. Chen $67K compromised, ***2156 M. Williams $54K attempted; timeline 2:14 / 2:18 / 2:22 / 2:34 ($15K wire) / 2:35 AM held; customer verified no activity at 6 AM |
| 4 | Yes, create investigation cases and take protective action | `investigation_summary` | Proposed actions ready for authorized execution: freeze 12, cards 18, wires 5 pending, password reset 12; draft cases FRD-2024-1847 ATO Ring $340K (Senior Analyst), FRD-2024-1848 Card Testing $127K (Card Team), FRD-2024-1849 Wire Fraud $224K (Wire Team); SAR draft; communications drafted |
| 5 | Yes, show me our fraud prevention performance and any concerning trends | `prevention_metrics` | Detection 94.2% vs 90%; false positive 2.8% vs 5%; detection time 4.2 sec vs 10 sec; losses prevented $4.8M vs $4M; ATO +34%, card present -12%, wire +2% |
| 6 | Yes, summarize everything and give me the action items | `morning_summary` | 1,247 reviewed; 23 critical; 3 rings; 12 accounts; $691K ($340K ATO + $351K other); 3 cases; SAR (48-hour deadline), 4 high-value outreach, card team coordination |

The video's critical-breakdown averages are rounded (8 x $34K + 6 x $28K + 5 x $67K + 4 x $42K is about $943K against the
$892K critical-tier value); both are shown as recorded. The video's "protective actions executed" and "12 alerts sent"
are staged for authorized execution here.
## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### FDA-01 — Fraud Operations Manager

- Prompt: Review overnight fraud activity and show me what needs immediate attention.
- Operation: `alert_triage`
- Arguments: `{}`
- Required factual anchors: `1,247 overnight alerts`, `$892K`, `F-78234`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Fraud Alert Triage

1,247 overnight alerts analyzed. 23 critical requiring immediate action.

| Priority | Alerts | Value | Action |
|---|---|---|---|
| Critical | 23 | $892K | Immediate review |
| High | 67 | $1.4M | Today |
| Medium | 234 | $2.1M | 48-hour queue |
| Low | 923 | $3.2M | Auto-disposition |

## Critical Breakdown

- Account takeover: 8 ($34K avg) - Credential change + transfer
- Card fraud ring: 6 ($28K avg) - Multi-location velocity
- Wire fraud: 5 ($67K avg) - First-time international
- Check fraud: 4 ($42K avg) - Duplicate deposit

**Immediate:** Alert #F-78234 ($127K wire to high-risk jurisdiction), Alert #F-78156 (takeover in progress), Alert #F-78089 (card testing). Most urgent: #F-78234 - route to the Wire Team.

## Monitored Card Transactions (sample)

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
- **RULE-004 (Wire to High-Risk Country):** Wire transfer to FATF grey/black list country [CRITICAL]
- **RULE-006 (Account Takeover Pattern):** Password change followed by high-value transaction [CRITICAL]
- **RULE-003 (Crypto Purchase Spike):** Unusual crypto exchange activity [MEDIUM]

Next step: see the pattern analysis?
```

### FDA-02 — Fraud Analyst

- Prompt: Yes, investigate the account takeover ring and show me the accounts.
- Operation: `transaction_analysis`
- Arguments: `{}`
- Required factual anchors: `***4521`, `2:34 AM`, `$340K`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Transaction Analysis: Account Takeover Ring

12-account takeover ring investigated. $340K at immediate risk.

| Account | Customer | Balance | Status |
|---|---|---|---|
| ***4521 | J. Morrison | $89K | Compromised |
| ***7834 | S. Chen | $67K | Compromised |
| ***2156 | M. Williams | $54K | Attempted |
| ***3390 | A. Patel | $22K | Linked (same device) |
| ***6612 | R. Okafor | $18K | Linked (same device) |
| ***1478 | L. Brooks | $16K | Linked (same device) |
| ***9025 | T. Nguyen | $15K | Linked (same device) |
| ***5307 | K. Alvarez | $14K | Linked (same device) |
| ***8841 | D. Fischer | $13K | Linked (same device) |
| ***2763 | E. Rossi | $12K | Linked (same device) |
| ***4419 | P. Kim | $11K | Linked (same device) |
| ***7150 | G. Hart | $9K | Linked (same device) |
| **Total** | 12 accounts | **$340K** | |

## Primary - J. Morrison (***4521) Timeline

- 2:14 AM: Password reset (new IP)
- 2:18 AM: Email changed
- 2:22 AM: Phone changed
- 2:34 AM: $15K wire initiated
- 2:35 AM: Transfer held by the AI risk model

**Indicators:** Foreign IP, new device, unusual navigation, all changes in 20 minutes. Customer verified no activity (contacted 6 AM).

Next step: create investigation cases and propose protective actions?
```

### FDA-03 — SIU Investigator

- Prompt: Yes, show me the pattern analysis and connected activity.
- Operation: `pattern_detection`
- Arguments: `{}`
- Required factual anchors: `3 organized fraud rings`, `94%`, `INV-2025-301`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Fraud Pattern Detection

3 organized fraud rings detected (hypotheses for investigator review, not proof). Alert #F-78156 connects to 12 accounts.

### Ring 1 - Account Takeover Network

- Alert #F-78156, 12 connected accounts, $340K exposure
- Pattern: Same device fingerprint, 8 password resets in 2 hours
- Confidence: 94%

### Ring 2 - Card Testing

- 47 cards tested in 4 hours
- Pattern: Gas stations (small amounts), 3 states
- Success rate: 23% (stolen batch indicator)
- Confidence: 87%

### Ring 3 - Wire Fraud

- 5 accounts opened in the last 30 days
- Similar deposits, attempting international wires
- Destination: Known mule accounts
- Confidence: 91%

Next step: investigate the takeover ring first?

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

- Prompt: Yes, create investigation cases and take protective action.
- Operation: `investigation_summary`
- Arguments: `{}`
- Required factual anchors: `FRD-2024-1847`, `Ready for authorized execution`, `no external action`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Investigation Cases and Proposed Protective Actions

Draft cases prepared and protective actions staged for authorized execution: 12 accounts, $340K to protect. Nothing has been blocked, frozen or sent.

| Proposed Action | Accounts | Status |
|---|---|---|
| Account freeze | 12 | Ready for authorized execution |
| Cards blocked | 18 | Ready for authorized execution |
| Wires held | 5 pending | Ready for authorized execution |
| Password reset | 12 | Queued for approval |

## Draft Cases (proposed routing)

- FRD-2024-1847: ATO Ring, $340K (Senior Analyst)
- FRD-2024-1848: Card Testing, $127K (Card Team)
- FRD-2024-1849: Wire Fraud, $224K (Wire Team)

**Evidence:** Device fingerprints, IPs, timeline, customer statements collected. SAR draft prepared for review.

**Communications (drafts, not sent):** 12 customer alerts drafted, 4 high-value customers flagged for a personal call, new credentials to schedule.

## Existing Investigation Queue

| Case ID | Pattern | Status | Priority | Analyst | Opened |
|---|---|---|---|---|---|
| INV-2025-301 | Card Cloning | Open | High | Karen Wright | 2025-03-05 |
| INV-2025-302 | Account Takeover | Escalated | Critical | David Chen | 2025-03-05 |
| INV-2025-303 | TBD | Under Review | Medium | Karen Wright | 2025-03-04 |

Status: prepared for authorized investigator review; no external action taken.

Next step: show fraud metrics and trends?
```

### FDA-05 — Risk Leader

- Prompt: Yes, show me our fraud prevention performance and any concerning trends.
- Operation: `prevention_metrics`
- Arguments: `{}`
- Required factual anchors: `94.2%`, `+34%`, `Exceeding`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Fraud Prevention Performance

Strong prevention but an emerging ATO trend requires attention.

| Metric | Current | Target | Status |
|---|---|---|---|
| Detection rate | 94.2% | 90% | Exceeding |
| False positive | 2.8% | 5% | Exceeding |
| Detection time | 4.2 sec | 10 sec | Exceeding |
| Losses prevented | $4.8M | $4M | Exceeding |

## Trends (30-Day)

- Account takeover: +34% (High concern - correlates with dark web dump)
- Card present: -12% (Low)
- Wire fraud: +2% (Medium)

**ATO Analysis:** Specific segment targeted (high-balance), bypassing 2FA, increasing sophistication.

**Recommended controls (for approval):** Deploy adaptive authentication; Pilot behavioral biometrics; Increase monitoring for credential changes.

Next step: generate the summary and action items?
```

### FDA-06 — Fraud Operations Manager

- Prompt: Yes, summarize everything and give me the action items.
- Operation: `morning_summary`
- Arguments: `{}`
- Required factual anchors: `$691K`, `SAR filing`, `1,247`

```text
> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

# Morning Fraud Review Summary

| Accomplishment | Result |
|---|---|
| Alerts reviewed | 1,247 overnight |
| Critical identified | 23 requiring action |
| Rings detected | 3 organized schemes |
| Accounts to secure | 12 compromised or linked (actions staged for authorized execution) |
| Value protected (on execution) | $691K ($340K ATO + $351K other) |

## Cases Prepared

- FRD-2024-1847: ATO Ring ($340K, critical)
- FRD-2024-1848: Card Testing ($127K, high)
- FRD-2024-1849: Wire Fraud ($224K, high)

## Immediate Actions

1. SAR filing for ATO (48-hour deadline) - draft ready for the BSA officer
2. Customer outreach (4 high-value accounts)
3. Coordinate card team on testing pattern

**Strategic:** Address 34% ATO increase, pilot behavioral biometrics, review credential monitoring

No SAR has been filed and no customer has been contacted; each action needs its authorized owner.
```
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
