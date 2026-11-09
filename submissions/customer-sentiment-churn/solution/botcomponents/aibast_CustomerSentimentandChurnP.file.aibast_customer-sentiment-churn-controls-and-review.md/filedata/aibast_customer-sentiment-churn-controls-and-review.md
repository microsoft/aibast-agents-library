# Customer Sentiment and Churn Prediction Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** See relationship risk before outreach becomes reactive. Unify sentiment, complaints, engagement, and product context into a transparent review queue with human-controlled retention options and no automated customer action.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize claims about a real person, protected-trait inference, deterministic churn predictions, customer contact, offers, fee changes, account actions, or external record changes.
- Required reviewers: relationship manager, retention specialist, customer-success lead, privacy reviewer, compliance reviewer, and authorized offer owner.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for relationship-manager, retention, or customer-success requests about customer sentiment across the banking portfolio, accounts at highest churn risk, early warning signals, profiles of the highest-value at-risk customers, retention strategies for each customer or for a named customer such as Marcus before contact or a fee change, assigning outreach and tracking, or which segment is below benchmark. Every operation has demo defaults, so call it right away. Do not answer those requests from general knowledge. Uses fictional records only, does not infer protected traits, and never contacts a customer, changes fees, makes an offer, or takes account action without authorized human review.",
  "display_name": "Customer Sentiment & Churn Agent",
  "name": "CustomerSentimentChurnAgent",
  "parameters": {
    "properties": {
      "customer_id": {
        "description": "Synthetic customer mapping: Robert Martinez is CUST-8001; Marcus Johnson or Marcus is CUST-8002; Sarah Thompson is CUST-8003; James Lee is CUST-8004; Priya Sharma is CUST-8005. Omit for portfolio-wide reports and the top-5 views.",
        "type": "string"
      },
      "operation": {
        "description": "Choose sentiment_dashboard to analyze customer sentiment across the banking portfolio, NPS, negative drivers, or which accounts are at highest churn risk. Choose early_warning_signals for the early warning signals to watch for. Choose churn_prediction for profiles of the highest-value at-risk customers, who to review first, or the evidence behind a churn score. Choose retention_actions for retention strategies for each customer, or to prepare options for Marcus or another customer before outreach, offers, or fee changes. Choose outreach_plan to assign the outreach and set up tracking. Choose segment_analysis for segment benchmarks or which segment is under its experience benchmark.",
        "enum": [
          "sentiment_dashboard",
          "churn_prediction",
          "retention_actions",
          "segment_analysis",
          "early_warning_signals",
          "outreach_plan"
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
      "manual/knowledge/aibast_customer-sentiment-churn-synthetic-records.md",
      "manual/knowledge/aibast_customer-sentiment-churn-controls-and-review.md"
    ],
    "manual_skill_count": 6,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "sentiment_dashboard",
      "churn_prediction",
      "retention_actions",
      "segment_analysis",
      "early_warning_signals",
      "outreach_plan"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 Customer Service or CRM",
      "Approved voice, chat, survey, and complaint analytics",
      "Power BI",
      "Microsoft Teams outreach review"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish.",
    "validated_manual": {
      "bot_id": "c93c1ae6-304b-4656-ab29-8fdd9da5fbb6",
      "display_name": "Customer Sentiment Manual",
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
      "bot_id": "66d29ea2-de55-418c-986b-bf233ee4a480",
      "changes_pushed": 7,
      "display_name": "Customer Sentiment Pilot",
      "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
      "environment_name": "kodyv8",
      "knowledge_files": 2,
      "model": "Sonnet46",
      "preview_cases_passed": 4,
      "preview_cases_total": 4,
      "published": false,
      "schema_name": "aibast_CustomerSentimentandChurnP",
      "skills": 4,
      "status": "Draft"
    }
  },
  "expected_tool": "CustomerSentimentChurnAgent",
  "smoke_test": {
    "must_call": "CustomerSentimentChurnAgent",
    "must_include": [
      "CUST-8002",
      "Negative"
    ],
    "prompt": "What are customers telling us across channels, and which relationship needs attention first?"
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
      "Relationship Manager",
      "Retention Specialist",
      "Customer Success Lead",
      "Microsoft 365 Copilot or Copilot Studio",
      "Customer Sentiment and Churn Prediction Agent",
      "Dynamics 365 Customer Service or CRM",
      "Approved voice, chat, survey, and complaint analytics",
      "Power BI",
      "Microsoft Teams outreach review"
    ],
    "capabilities": [
      {
        "name": "Cross-channel sentiment view",
        "operation": "sentiment_dashboard",
        "purpose": "Aggregates fictional interaction sentiment and NPS evidence across touchpoints."
      },
      {
        "name": "Churn-review prioritization",
        "operation": "churn_prediction",
        "purpose": "Applies a transparent heuristic to prioritize human review without predicting an individual outcome."
      },
      {
        "name": "Retention option preparation",
        "operation": "retention_actions",
        "purpose": "Prepares reviewable service-recovery and outreach options without contacting customers or making offers."
      },
      {
        "name": "Segment context",
        "operation": "segment_analysis",
        "purpose": "Compares synthetic segment aggregates with fixed benchmarks."
      },
      {
        "name": "Early warning signals",
        "operation": "early_warning_signals",
        "purpose": "Lists fictional predictive signals, critical combinations and today's alerts with the highest-value customers at risk."
      },
      {
        "name": "Outreach assignment plan",
        "operation": "outreach_plan",
        "purpose": "Proposes owners, channels, due times, tracking and escalation rules for the manager to confirm; nothing is sent."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Customer Sentiment and Churn Prediction Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/customer-sentiment-churn/deployment.json. Upload both synthetic knowledge files and all 4 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Customer Sentiment and Churn Prediction Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/customer-sentiment-churn/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Customer Sentiment and Churn Prediction Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 Customer Service or CRM",
      "Approved voice, chat, survey, and complaint analytics",
      "Power BI",
      "Microsoft Teams outreach review"
    ]
  },
  "blueprint_role": "Creates a governed relationship-intelligence layer connecting customer signals, transparent prioritization, service recovery, and approved outreach.",
  "business_value": [
    "Improves visibility into cross-channel experience signals.",
    "Makes churn prioritization explainable rather than presenting a hidden prediction as fact.",
    "Keeps outreach, offers, fee changes, and account actions under authorized human control."
  ],
  "card_pitch": "Unify sentiment, complaints, engagement, and product context into a transparent review queue with human-controlled retention options and no automated customer action.",
  "customer_challenge": "A regional bank has customer feedback, complaints, surveys, and engagement signals spread across channels. Teams react late and may apply generic offers without a clear evidence trail or review control.",
  "microsoft_ai_story": "Microsoft Copilot Studio gives relationship teams a governed conversational view. Dynamics 365 supplies customer-service context, approved interaction analytics contribute signals, Power BI shows segment trends, and Microsoft Teams supports outreach review.",
  "sales_headline": "See relationship risk before outreach becomes reactive"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### CSC-01 — Customer Success Lead

- User wording: Analyze customer sentiment across our banking portfolio and identify accounts at highest churn risk.
- Route: `sentiment_dashboard` via `CustomerSentimentChurnAgent`
- Required evidence: `180K customers analyzed`, `$8.2M`, `Negative sentiment up 18%`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Customer Sentiment Dashboard

180K customers analyzed. 2,400 high churn risk representing $8.2M annual revenue.

| Sentiment | Customers | % |
|---|---|---|
| Promoters | 72,000 | 40% |
| Passives | 81,000 | 45% |
| Detractors | 27,000 | 15% |

## High Risk

- **Critical (>80%):** 840 customers, $2.8M revenue, $3,333 avg
- **High (60-80%):** 1,560 customers, $5.4M revenue, $3,462 avg

**Top Negative Drivers:** Digital banking (2,400 mentions), Fee transparency (1,800 mentions), Wait times (1,200 mentions).

**Alert:** Negative sentiment up 18% this month.

## Highest-Value At-Risk Sample (interaction sentiment)

Sample interactions analyzed: 12 (Positive 0, Neutral 3, Negative 9)

| Customer | Segment | NPS | Churn Probability | Recent Sentiment |
|---|---|---|---|---|
| Robert Martinez (CUST-8001) | Affluent | 4 | 84% (critical) | Negative |
| Sarah Thompson (CUST-8003) | Affluent | 6 | 78% (high) | Neutral |
| James Lee (CUST-8004) | Emerging Affluent | 3 | 76% (high) | Negative |
| Marcus Johnson (CUST-8002) | Mass Market | 4 | 64% (high) | Negative |
| Priya Sharma (CUST-8005) | Emerging Affluent | 7 | 62% (high) | Neutral |

Next step: see the early warning signals?
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report: Highest-Value At-Risk Customers

Top 5 at-risk profiles prepared.

### Robert Martinez (CUST-8001) - Priority 1

- $890K deposits, $12K annual revenue
- Risk: 84% (critical); review score 60/100
- Signals: Competitor app download (Summit National Bank), Reduced logins
- Last survey: Detractor (4/10) - "Your app is years behind"
- Recent contact: Asked about wire fees
- Segment: Affluent, tenure 12 years, products: checking, savings, investment

## Top 5 Summary

| Priority | Customer | Deposits | Revenue | Risk | Key Signal |
|---|---|---|---|---|---|
| 1 | R. Martinez (CUST-8001) | $890K | $12K | 84% | competitor app |
| 2 | S. Thompson (CUST-8003) | $450K | $8K | 78% | deposit changed |
| 3 | J. Lee (CUST-8004) | $340K | $6K | 76% | 3 complaints |
| 4 | M. Johnson (CUST-8002) | $280K | $5K | 64% | 5 complaints |
| 5 | P. Sharma (CUST-8005) | $220K | $4K | 62% | reduced logins |

**Combined Risk:** $2.18M deposits, $35K annual revenue at risk. Replacement cost if lost: $16K.

## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below half of the segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days before the demo date

These scores prioritize review; they do not predict an individual outcome.

Next step: generate retention strategies?
```

### CSC-02 — Retention Specialist

- User wording: Show me profiles of our highest-value at-risk customers.
- Route: `churn_prediction` via `CustomerSentimentChurnAgent`
- Required evidence: `Robert Martinez`, `$2.18M`, `prioritize review`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report: Highest-Value At-Risk Customers

Top 5 at-risk profiles prepared.

### Robert Martinez (CUST-8001) - Priority 1

- $890K deposits, $12K annual revenue
- Risk: 84% (critical); review score 60/100
- Signals: Competitor app download (Summit National Bank), Reduced logins
- Last survey: Detractor (4/10) - "Your app is years behind"
- Recent contact: Asked about wire fees
- Segment: Affluent, tenure 12 years, products: checking, savings, investment

## Top 5 Summary

| Priority | Customer | Deposits | Revenue | Risk | Key Signal |
|---|---|---|---|---|---|
| 1 | R. Martinez (CUST-8001) | $890K | $12K | 84% | competitor app |
| 2 | S. Thompson (CUST-8003) | $450K | $8K | 78% | deposit changed |
| 3 | J. Lee (CUST-8004) | $340K | $6K | 76% | 3 complaints |
| 4 | M. Johnson (CUST-8002) | $280K | $5K | 64% | 5 complaints |
| 5 | P. Sharma (CUST-8005) | $220K | $4K | 62% | reduced logins |

**Combined Risk:** $2.18M deposits, $35K annual revenue at risk. Replacement cost if lost: $16K.

## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below half of the segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days before the demo date

These scores prioritize review; they do not predict an individual outcome.

Next step: generate retention strategies?
```

### CSC-03 — Relationship Manager

- User wording: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.
- Route: `retention_actions` via `CustomerSentimentChurnAgent`
- Required evidence: `Marcus Johnson`, `No customer was contacted`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Retention Action Recommendations

### Marcus Johnson (CUST-8002) Strategy

- Approach: Relationship manager call
- Message: "We reviewed your fees and complaints"
- Offer: Complaint resolution with a fee review
- Incentive: Waive monthly maintenance fees for 6 months ($72 value)
- Urgency: Within 3 days
- Success probability (modeled): 55%
- Draft talk track: "Mr. Johnson, I reviewed your recent fee disputes and want to walk you through what we can fix."


## Available Actions Catalog

| Action | Description | Cost | Success Rate |
|---|---|---|---|
| Fee Waiver | Waive monthly maintenance fees for 6 months | $72 | 45% |
| Rate Upgrade | Offer premium savings rate for 12 months | $150 | 35% |
| Personal Outreach | Schedule call with relationship manager | $25 | 55% |
| Product Bundle | Offer discounted product bundle with waived fees | $200 | 60% |
| Loyalty Bonus | Credit loyalty bonus to account | $100 | 50% |
| Complaint Resolution | Escalate to service recovery team | $50 | 65% |

Every option requires relationship-manager review, policy validation, customer consent where applicable, and approved execution. No customer was contacted and no offer was made.

Next step: assign the outreach and set up tracking?
```

### CSC-04 — Head of Customer Experience

- User wording: Which segment is under its experience benchmark, and what should we investigate?
- Route: `segment_analysis` via `CustomerSentimentChurnAgent`
- Required evidence: `Mass Market`, `benchmark`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Segment Analysis

## Segment Benchmarks

| Segment | Avg NPS | Avg Products | Avg Tenure | Avg Transactions |
|---|---|---|---|---|
| Affluent | 8.2 | 4.1 | 10 yrs | 55/mo |
| Emerging Affluent | 7.0 | 3.2 | 5 yrs | 35/mo |
| Mass Market | 6.5 | 2.0 | 4 yrs | 20/mo |
| Small Business | 6.8 | 3.0 | 5 yrs | 90/mo |

## Current Customer Performance vs Benchmark

### Affluent (2 customers)

- NPS: 5.0 (benchmark: 8.2)
- Products: 3.0 (benchmark: 4.1)

### Emerging Affluent (2 customers)

- NPS: 5.0 (benchmark: 7.0)
- Products: 3.0 (benchmark: 3.2)

### Mass Market (1 customers)

- NPS: 4.0 (benchmark: 6.5)
- Products: 2.0 (benchmark: 2.0)

```

### CSC-05 — Retention Specialist

- User wording: Yes, what are the early warning signals we should watch for?
- Route: `early_warning_signals` via `CustomerSentimentChurnAgent`
- Required evidence: `Reduced logins`, `89% churn`, `Robert Martinez`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Early Warning Signals

4 key predictive signals identified, shown 30-60 days before leaving.

| Signal | Customers | Churn Rate |
|---|---|---|
| Reduced logins | 3,400 | 72% |
| Competitor app download | 1,200 | 68% |
| Direct deposit change | 890 | 78% |
| Balance decline >30% | 2,100 | 54% |

## Critical Combinations

- Competitor app + balance decline: 89% churn
- Deposit change + reduced logins: 82% churn
- 2+ complaints: 67% churn

## Real-Time Alerts Today

- 47 customers: Competitor app detected
- 23 customers: External transfers >$10K
- 12 customers: Direct deposit changed

**High-Value at Risk:** Robert Martinez ($890K, competitor app), Sarah Thompson ($450K, deposit changed), James Lee ($340K, 3 complaints)

Next step: profile the highest-value at-risk customers?
```

### CSC-06 — Customer Success Lead

- User wording: Yes, assign the outreach and set up tracking.
- Route: `outreach_plan` via `CustomerSentimentChurnAgent`
- Required evidence: `VP Chen`, `Escalation Rules`, `No customer was contacted`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Proposed Outreach Assignments and Tracking

Outreach plan ready for the manager to confirm: all 5 high-priority customers have a proposed owner, channel and due time.

| Customer | Assigned To | Channel | Due |
|---|---|---|---|
| R. Martinez (CUST-8001) | VP Chen | Phone | Today 2 PM |
| S. Thompson (CUST-8003) | Sr. RM Johnson | Video call | Tomorrow |
| J. Lee (CUST-8004) | Sr. RM Williams | In-person | Tomorrow |
| M. Johnson (CUST-8002) | RM Patel | Phone | Day 3 |
| P. Sharma (CUST-8005) | RM Garcia | Phone + email | Day 3 |

**Prepared for release (not sent):** customer briefs and talk tracks drafted, offers queued for approval, calendar holds proposed.

## Tracking

- Contact attempts: real-time
- Outcomes: RM updates
- Offer acceptance: immediate
- Account activity: 30-day monitoring

## Escalation Rules

- No contact in 48 hours -> alert manager
- Declines offer -> escalate to VP
- Balance withdrawal -> immediate notification

No customer was contacted, no offer was made, and no assignment, brief or calendar hold was sent; the manager confirms the plan in the CRM.
```
## Sentiment Distribution

- **Positive:** 2 (20.0%)
- **Neutral:** 4 (40.0%)
- **Negative:** 4 (40.0%)

## Customer NPS Scores

| Customer | Segment | NPS | Products | Complaints (12m) |
|---|---|---|---|---|
| Elizabeth Warren-Hayes (CUST-8001) | Affluent | 9 | 4 | 0 |
| Marcus Johnson (CUST-8002) | Mass Market | 4 | 2 | 5 |
| Priya Sharma (CUST-8003) | Emerging Affluent | 7 | 4 | 1 |
| Gerald Thompson (CUST-8004) | Mass Market | 3 | 1 | 2 |
| Diana Castellano (CUST-8005) | Small Business | 6 | 3 | 3 |
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report

| Customer | Segment | Churn Score | NPS | Transactions | Complaints |
|---|---|---|---|---|---|
| Elizabeth Warren-Hayes (CUST-8001) | Affluent | 0 (Low) | 9 | 48 | 0 |
| Marcus Johnson (CUST-8002) | Mass Market | 45 (Medium) | 4 | 15 | 5 |
| Priya Sharma (CUST-8003) | Emerging Affluent | 0 (Low) | 7 | 32 | 1 |
| Gerald Thompson (CUST-8004) | Mass Market | 70 (High) | 3 | 4 | 2 |
| Diana Castellano (CUST-8005) | Small Business | 20 (Low) | 6 | 120 | 3 |

## High-Risk Customers

### Gerald Thompson (CUST-8004) — Score: 70

- Segment: Mass Market
- Tenure: 8 years
- Products: checking
- Recent sentiment: neutral


## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days ago

These scores prioritize review; they do not predict an individual outcome.
```

### CSC-02 — Retention Specialist

- User wording: Who should my team review first today, and what evidence drove the priority?
- Route: `churn_prediction` via `CustomerSentimentChurnAgent`
- Required evidence: `CUST-8004`, `prioritize review`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report

| Customer | Segment | Churn Score | NPS | Transactions | Complaints |
|---|---|---|---|---|---|
| Elizabeth Warren-Hayes (CUST-8001) | Affluent | 0 (Low) | 9 | 48 | 0 |
| Marcus Johnson (CUST-8002) | Mass Market | 45 (Medium) | 4 | 15 | 5 |
| Priya Sharma (CUST-8003) | Emerging Affluent | 0 (Low) | 7 | 32 | 1 |
| Gerald Thompson (CUST-8004) | Mass Market | 70 (High) | 3 | 4 | 2 |
| Diana Castellano (CUST-8005) | Small Business | 20 (Low) | 6 | 120 | 3 |

## High-Risk Customers

### Gerald Thompson (CUST-8004) — Score: 70

- Segment: Mass Market
- Tenure: 8 years
- Products: checking
- Recent sentiment: neutral


## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days ago

These scores prioritize review; they do not predict an individual outcome.
```

### CSC-03 — Relationship Manager

- User wording: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.
- Route: `retention_actions` via `CustomerSentimentChurnAgent`
- Required evidence: `Marcus Johnson`, `No customer was contacted`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Retention Action Recommendations

## Available Actions

| Action | Description | Cost | Success Rate |
|---|---|---|---|
| Fee Waiver | Waive monthly maintenance fees for 6 months | $72 | 45% |
| Rate Upgrade | Offer premium savings rate for 12 months | $150 | 35% |
| Personal Outreach | Schedule call with relationship manager | $25 | 55% |
| Product Bundle | Offer discounted product bundle with waived fees | $200 | 60% |
| Loyalty Bonus | Credit loyalty bonus to account | $100 | 50% |
| Complaint Resolution | Escalate to service recovery team | $50 | 65% |

## Recommended Actions by Customer

### Marcus Johnson (CUST-8002) — Churn Score: 45

1. **Complaint Resolution** — Escalate to service recovery team
2. **Personal Outreach** — Schedule call with relationship manager
3. **Product Bundle** — Offer discounted product bundle with waived fees

### Gerald Thompson (CUST-8004) — Churn Score: 70

2. **Personal Outreach** — Schedule call with relationship manager
3. **Product Bundle** — Offer discounted product bundle with waived fees


Every option requires relationship-manager review, policy validation, customer consent where applicable, and approved execution. No customer was contacted and no offer was made.
```

### CSC-04 — Head of Customer Experience

- User wording: Which segment is under its experience benchmark, and what should we investigate?
- Route: `segment_analysis` via `CustomerSentimentChurnAgent`
- Required evidence: `Mass Market`, `benchmark`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[CustomerSentimentChurnAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Segment Analysis

## Segment Benchmarks

| Segment | Avg NPS | Avg Products | Avg Tenure | Avg Transactions |
|---|---|---|---|---|
| Affluent | 8.2 | 4.1 | 10 yrs | 55/mo |
| Emerging Affluent | 7.0 | 3.2 | 5 yrs | 35/mo |
| Mass Market | 6.5 | 2.0 | 4 yrs | 20/mo |
| Small Business | 6.8 | 3.0 | 5 yrs | 90/mo |

## Current Customer Performance vs Benchmark

### Affluent (1 customers)

- NPS: 9.0 (benchmark: 8.2)
- Products: 4.0 (benchmark: 4.1)

### Mass Market (2 customers)

- NPS: 3.5 (benchmark: 6.5)
- Products: 1.5 (benchmark: 2.0)

### Emerging Affluent (1 customers)

- NPS: 7.0 (benchmark: 7.0)
- Products: 4.0 (benchmark: 3.2)

### Small Business (1 customers)

- NPS: 6.0 (benchmark: 6.8)
- Products: 3.0 (benchmark: 3.0)

```

## Packaged skill contracts

### `manual/skills/aibast_churn-prediction_02/SKILL.md`

````markdown
---
name: churn-prediction
description: Use for churn-review prioritization questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Churn-review prioritization

Applies a transparent heuristic to prioritize human review without predicting an individual outcome.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Retention Specialist

Prompt: Show me profiles of our highest-value at-risk customers.

Expected synthetic evidence: Robert Martinez, $2.18M, prioritize review.
````

### `manual/skills/aibast_early-warning-signals_05/SKILL.md`

````markdown
---
name: early-warning-signals
description: "Use when a retention specialist asks something like \"Yes, what are the early warning signals we should watch for\""
---
<!-- bic:source=blank -->
# Early warning signals

Use when a retention specialist asks something like "Yes, what are the early warning signals we should watch for"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `Reduced logins`
- `89% churn`
- `Robert Martinez`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_outreach-plan_06/SKILL.md`

````markdown
---
name: outreach-plan
description: "Use when a customer success lead asks something like \"Yes, assign the outreach and set up tracking\""
---
<!-- bic:source=blank -->
# Outreach plan

Use when a customer success lead asks something like "Yes, assign the outreach and set up tracking"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `VP Chen`
- `Escalation Rules`
- `No customer was contacted`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_retention-actions_03/SKILL.md`

````markdown
---
name: retention-actions
description: Use for retention option preparation questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Retention option preparation

Prepares reviewable service-recovery and outreach options without contacting customers or making offers.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Relationship Manager

Prompt: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.

Expected synthetic evidence: Marcus Johnson, No customer was contacted.
````

### `manual/skills/aibast_segment-analysis_04/SKILL.md`

````markdown
---
name: segment-analysis
description: Use for segment context questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Segment context

Compares synthetic segment aggregates with fixed benchmarks.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Head of Customer Experience

Prompt: Which segment is under its experience benchmark, and what should we investigate?

Expected synthetic evidence: Mass Market, benchmark.
````

### `manual/skills/aibast_sentiment-dashboard_01/SKILL.md`

````markdown
---
name: sentiment-dashboard
description: Use for cross-channel sentiment view questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Cross-channel sentiment view

Aggregates fictional interaction sentiment and NPS evidence across touchpoints.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Customer Success Lead

Prompt: Analyze customer sentiment across our banking portfolio and identify accounts at highest churn risk.

Expected synthetic evidence: 180K customers analyzed, $8.2M, Negative sentiment up 18%.
````
## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Retention Specialist

Prompt: Who should my team review first today, and what evidence drove the priority?

Expected synthetic evidence: CUST-8004, prioritize review.
````

### `manual/skills/aibast_retention-actions_03/SKILL.md`

````markdown
---
name: retention-actions
description: Use for retention option preparation questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Retention option preparation

Prepares reviewable service-recovery and outreach options without contacting customers or making offers.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Relationship Manager

Prompt: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.

Expected synthetic evidence: Marcus Johnson, No customer was contacted.
````

### `manual/skills/aibast_segment-analysis_04/SKILL.md`

````markdown
---
name: segment-analysis
description: Use for segment context questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Segment context

Compares synthetic segment aggregates with fixed benchmarks.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Head of Customer Experience

Prompt: Which segment is under its experience benchmark, and what should we investigate?

Expected synthetic evidence: Mass Market, benchmark.
````

### `manual/skills/aibast_sentiment-dashboard_01/SKILL.md`

````markdown
---
name: sentiment-dashboard
description: Use for cross-channel sentiment view questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Cross-channel sentiment view

Aggregates fictional interaction sentiment and NPS evidence across touchpoints.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Customer Success Lead

Prompt: What are customers telling us across channels, and which relationship needs attention first?

Expected synthetic evidence: CUST-8002, Negative.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
