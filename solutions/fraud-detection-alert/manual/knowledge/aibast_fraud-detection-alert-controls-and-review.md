# Fraud Detection and Alert Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Turn alert volume into explainable investigator priority. Connect alert severity, transaction evidence, pattern hypotheses, and case routing in one fraud-operations view that never treats a score as proof or claims a protective action occurred.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize fraud accusations or determinations, legal or regulatory advice, customer contact, card or account blocks, payment or wire actions, case routing, SAR or other filings, or external record changes.
- Required reviewers: fraud analyst, SIU investigator, fraud-operations authority, legal or compliance reviewer, filing officer, and authorized protective-action owner.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for fraud-analyst, SIU, or risk-leader requests about overnight fraud activity and the most urgent alert, pattern analysis and connected rings, investigating the account takeover ring, account activity behind the Dubai alert, creating investigation cases and protective actions, fraud prevention performance and trends, or the morning summary and action items. Every operation has demo defaults, so call it right away. Do not answer those requests from general knowledge. Uses fictional records only; a flag is not proof of fraud and the tool never blocks funds, changes an account, contacts a customer, files a SAR, or performs another protective action. Human investigation and authorized human review and approval are mandatory.",
  "display_name": "Fraud Detection & Alert Agent",
  "name": "FraudDetectionAlertAgent",
  "parameters": {
    "properties": {
      "account": {
        "description": "Synthetic account mapping: the Dubai alert or James Peterson is 4532-XXXX-8891; Lisa Wang/crypto is 4716-XXXX-3304; Robert Miles/critical wire is 5412-XXXX-6678; Elena Vasquez is 4024-XXXX-1190. Takeover-ring accounts: J. Morrison ***4521, S. Chen ***7834, M. Williams ***2156. Omit for the takeover ring.",
        "type": "string"
      },
      "case_id": {
        "description": "Synthetic case mapping: the Dubai/card-cloning case is INV-2025-301; the critical wire case is INV-2025-302; the crypto case is INV-2025-303; the ATO ring case is FRD-2024-1847, card testing FRD-2024-1848, wire fraud ring FRD-2024-1849. Omit to prepare the three ring cases.",
        "type": "string"
      },
      "operation": {
        "description": "Choose alert_triage to review overnight activity, the overnight queue, the most urgent alert, severity, or why an alert is urgent. Choose pattern_detection for pattern analysis and connected activity, coordinated fraud rings, known patterns, or why a match is only a hypothesis. Choose transaction_analysis to investigate the account takeover ring and its accounts (default), or for account activity behind the Dubai alert (account 4532-XXXX-8891), merchant sequence, or transactions. Choose investigation_summary to create investigation cases and take protective action (returns proposed actions awaiting authorized execution), for a named case, the critical wire case, SIU preparation, or what protective actions actually occurred. Choose prevention_metrics for fraud prevention performance and concerning trends. Choose morning_summary to summarize everything and give the action items.",
        "enum": [
          "alert_triage",
          "transaction_analysis",
          "pattern_detection",
          "investigation_summary",
          "prevention_metrics",
          "morning_summary"
        ],
        "type": "string"
      }
    },
    "required": [
      "operation"
    ],
    "type": "object"
  }
}
```

## Deployment and architecture contract

### Deployment recipe excerpt

```json
{
  "copilot_studio": {
    "authoring_mode": "manual-upload",
    "manual_knowledge_files": [
      "manual/knowledge/aibast_fraud-detection-alert-synthetic-records.md",
      "manual/knowledge/aibast_fraud-detection-alert-controls-and-review.md"
    ],
    "manual_skill_count": 6,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "alert_triage",
      "transaction_analysis",
      "pattern_detection",
      "investigation_summary",
      "prevention_metrics",
      "morning_summary"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Approved transaction-monitoring data",
      "Dynamics 365 fraud or investigation cases",
      "Microsoft Sentinel or approved security signals",
      "Microsoft Teams SIU escalation",
      "Authorized filing and protective-action workflows"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish.",
    "validated_manual": {
      "bot_id": "5ac43ae1-9a67-460f-991c-1c0c5c7aea87",
      "display_name": "Fraud Detection Manual",
      "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
      "environment_name": "kodyv8",
      "knowledge_files": 2,
      "model": "Sonnet46",
      "preview_cases_passed": 4,
      "preview_cases_total": 4,
      "published": false,
      "skills": 4,
      "status": "Draft",
      "web_search_removed": true
    },
    "validated_pilot": {
      "bot_id": "8f9fd956-5fc4-4c2e-a200-61399060507a",
      "changes_pushed": 7,
      "display_name": "Fraud Detection Pilot",
      "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
      "environment_name": "kodyv8",
      "knowledge_files": 2,
      "model": "Sonnet46",
      "preview_cases_passed": 4,
      "preview_cases_total": 4,
      "published": false,
      "schema_name": "aibast_FraudDetectionandAlertPilo",
      "skills": 4,
      "status": "Draft"
    }
  },
  "expected_tool": "FraudDetectionAlertAgent",
  "smoke_test": {
    "must_call": "FraudDetectionAlertAgent",
    "must_include": [
      "TXN-90006",
      "Critical"
    ],
    "prompt": "What is the most urgent alert in the overnight queue, and what evidence makes it urgent?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 6 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Fraud Analyst",
      "SIU Investigator",
      "Risk Leader",
      "Microsoft 365 Copilot or Copilot Studio",
      "Fraud Detection and Alert Agent",
      "Approved transaction-monitoring data",
      "Dynamics 365 fraud or investigation cases",
      "Microsoft Sentinel or approved security signals",
      "Microsoft Teams SIU escalation",
      "Authorized filing and protective-action workflows"
    ],
    "capabilities": [
      {
        "name": "Alert triage",
        "operation": "alert_triage",
        "purpose": "Prioritizes fictional alerts by transparent risk evidence and rule severity."
      },
      {
        "name": "Transaction evidence review",
        "operation": "transaction_analysis",
        "purpose": "Summarizes monitored transactions and account-level activity for investigation."
      },
      {
        "name": "Fraud-pattern hypotheses",
        "operation": "pattern_detection",
        "purpose": "Compares active cases with known indicators without declaring fraud."
      },
      {
        "name": "Case preparation and routing",
        "operation": "investigation_summary",
        "purpose": "Builds a review-ready case summary and proposed queue without taking a protective or filing action."
      },
      {
        "name": "Prevention performance and trends",
        "operation": "prevention_metrics",
        "purpose": "Compares fictional detection, false-positive, speed and loss-prevention metrics with targets and flags 30-day fraud trends with recommended controls."
      },
      {
        "name": "Morning summary and action items",
        "operation": "morning_summary",
        "purpose": "Summarizes the overnight review, prepared cases and value to protect with immediate and strategic actions for authorized owners."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Fraud Detection and Alert Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/fraud-detection-alert/deployment.json. Upload both synthetic knowledge files and all 4 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
    "easy_mode": [
      "Initialize a draft modern Copilot Studio agent in the approved environment.",
      "Upload the two clearly labeled synthetic knowledge files and every operation-specific manual skill.",
      "Bind approved least-privilege connection references only; keep consequential actions behind explicit approval.",
      "Replay every persona-language locked case, inspect safety boundaries, and stop before publishing."
    ],
    "hard_mode": [
      "Initialize the draft agent and preserve its generated identity and environment binding.",
      "Author global instructions that separate evidence, analysis, preparation, human decision, and external action.",
      "Upload the two synthetic knowledge files and one SKILL.md per implemented operation.",
      "Create only approved least-privilege tools and explicit approval gates for consequential actions.",
      "Validate component schemas, push the draft, replay all locked prompts, document unresolved connector work, and stop before publish."
    ],
    "local_install_prompt": "Install and validate the AI BAST Fraud Detection and Alert Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/fraud-detection-alert/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Fraud Detection and Alert Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Approved transaction-monitoring data",
      "Dynamics 365 fraud or investigation cases",
      "Microsoft Sentinel or approved security signals",
      "Microsoft Teams SIU escalation",
      "Authorized filing and protective-action workflows"
    ]
  },
  "blueprint_role": "Establishes a governed fraud-investigation layer connecting monitoring evidence, case preparation, SIU routing, and authorized protective actions.",
  "business_value": [
    "Improves transparency and consistency in alert triage.",
    "Accelerates investigation preparation by linking cases to transactions, rules, and pattern evidence.",
    "Preserves human authority over blocks, customer contact, payment actions, and regulatory filings."
  ],
  "card_pitch": "Connect alert severity, transaction evidence, pattern hypotheses, and case routing in one fraud-operations view that never treats a score as proof or claims a protective action occurred.",
  "customer_challenge": "A bank fraud team is balancing high alert volume, fragmented transaction evidence, pattern investigation, routing, and filing deadlines. Critical activity can be buried while rushed automation risks acting before evidence and authority are confirmed.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the investigator workspace. Dynamics 365 manages cases, approved transaction and identity services contribute evidence, Microsoft Sentinel can provide security signals, and Microsoft Teams supports SIU and operations escalation.",
  "sales_headline": "Turn alert volume into explainable investigator priority"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### FDA-01 — Fraud Operations Manager

- User wording: Review overnight fraud activity and show me what needs immediate attention.
- Route: `alert_triage` via `FraudDetectionAlertAgent`
- Required evidence: `1,247 overnight alerts`, `$892K`, `F-78234`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Yes, investigate the account takeover ring and show me the accounts.
- Route: `transaction_analysis` via `FraudDetectionAlertAgent`
- Required evidence: `***4521`, `2:34 AM`, `$340K`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Yes, show me the pattern analysis and connected activity.
- Route: `pattern_detection` via `FraudDetectionAlertAgent`
- Required evidence: `3 organized fraud rings`, `94%`, `INV-2025-301`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Yes, create investigation cases and take protective action.
- Route: `investigation_summary` via `FraudDetectionAlertAgent`
- Required evidence: `FRD-2024-1847`, `Ready for authorized execution`, `no external action`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Yes, show me our fraud prevention performance and any concerning trends.
- Route: `prevention_metrics` via `FraudDetectionAlertAgent`
- Required evidence: `94.2%`, `+34%`, `Exceeding`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Yes, summarize everything and give me the action items.
- Route: `morning_summary` via `FraudDetectionAlertAgent`
- Required evidence: `$691K`, `SAR filing`, `1,247`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Show me the account activity behind the Dubai alert so I can investigate the sequence.
- Route: `transaction_analysis` via `FraudDetectionAlertAgent`
- Required evidence: `4532-XXXX-8891`, `TXN-90002`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Which active case resembles a coordinated fraud pattern, and what makes that only a hypothesis?
- Route: `pattern_detection` via `FraudDetectionAlertAgent`
- Required evidence: `INV-2025-301`, `Card Cloning`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

- User wording: Prepare the critical wire case for SIU review and tell me what actions actually occurred.
- Route: `investigation_summary` via `FraudDetectionAlertAgent`
- Required evidence: `INV-2025-302`, `no external action`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FraudDetectionAlertAgent] > **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been blocked, changed, submitted, or completed.

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

## Packaged skill contracts

### `manual/skills/aibast_alert-triage_01/SKILL.md`

````markdown
---
name: alert-triage
description: Use for alert triage questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Alert triage

Prioritizes fictional alerts by transparent risk evidence and rule severity.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Fraud Operations Manager

Prompt: Review overnight fraud activity and show me what needs immediate attention.

Expected synthetic evidence: 1,247 overnight alerts, $892K, F-78234.
````

### `manual/skills/aibast_investigation-summary_04/SKILL.md`

````markdown
---
name: investigation-summary
description: Use for case preparation and routing questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Case preparation and routing

Builds a review-ready case summary and proposed queue without taking a protective or filing action.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Risk Leader

Prompt: Yes, create investigation cases and take protective action.

Expected synthetic evidence: FRD-2024-1847, Ready for authorized execution, no external action.
````

### `manual/skills/aibast_morning-summary_06/SKILL.md`

````markdown
---
name: morning-summary
description: "Use when a fraud operations manager asks something like \"Yes, summarize everything and give me the action items\""
---
<!-- bic:source=blank -->
# Morning summary

Use when a fraud operations manager asks something like "Yes, summarize everything and give me the action items"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `$691K`
- `SAR filing`
- `1,247`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_pattern-detection_03/SKILL.md`

````markdown
---
name: pattern-detection
description: Use for fraud-pattern hypotheses questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Fraud-pattern hypotheses

Compares active cases with known indicators without declaring fraud.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: SIU Investigator

Prompt: Yes, show me the pattern analysis and connected activity.

Expected synthetic evidence: 3 organized fraud rings, 94%, INV-2025-301.
````

### `manual/skills/aibast_prevention-metrics_05/SKILL.md`

````markdown
---
name: prevention-metrics
description: "Use when a risk leader asks something like \"Yes, show me our fraud prevention performance and any concerning trends\""
---
<!-- bic:source=blank -->
# Prevention metrics

Use when a risk leader asks something like "Yes, show me our fraud prevention performance and any concerning trends"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `94.2%`
- `+34%`
- `Exceeding`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_transaction-analysis_02/SKILL.md`

````markdown
---
name: transaction-analysis
description: Use for transaction evidence review questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Transaction evidence review

Summarizes monitored transactions and account-level activity for investigation.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Fraud Analyst

Prompt: Yes, investigate the account takeover ring and show me the accounts.

Expected synthetic evidence: ***4521, 2:34 AM, $340K.
````
## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Fraud Operations Manager

Prompt: What is the most urgent alert in the overnight queue, and what evidence makes it urgent?

Expected synthetic evidence: TXN-90006, Critical.
````

### `manual/skills/aibast_investigation-summary_04/SKILL.md`

````markdown
---
name: investigation-summary
description: Use for case preparation and routing questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Case preparation and routing

Builds a review-ready case summary and proposed queue without taking a protective or filing action.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Risk Leader

Prompt: Prepare the critical wire case for SIU review and tell me what actions actually occurred.

Expected synthetic evidence: INV-2025-302, no external action.
````

### `manual/skills/aibast_pattern-detection_03/SKILL.md`

````markdown
---
name: pattern-detection
description: Use for fraud-pattern hypotheses questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Fraud-pattern hypotheses

Compares active cases with known indicators without declaring fraud.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: SIU Investigator

Prompt: Which active case resembles a coordinated fraud pattern, and what makes that only a hypothesis?

Expected synthetic evidence: INV-2025-301, Card Cloning.
````

### `manual/skills/aibast_transaction-analysis_02/SKILL.md`

````markdown
---
name: transaction-analysis
description: Use for transaction evidence review questions in the Fraud Detection and Alert Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Transaction evidence review

Summarizes monitored transactions and account-level activity for investigation.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Fraud Analyst

Prompt: Show me the account activity behind the Dubai alert so I can investigate the sequence.

Expected synthetic evidence: 4532-XXXX-8891, TXN-90002.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
