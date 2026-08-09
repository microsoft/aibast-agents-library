# Deal Progression Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/b2b_sales_stacks/deal_progression_stack/deal_progression_agent.py`
- Strict transcript evidence: `solutions/deal-progression/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:38:36.589382+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_STAGE_BENCHMARKS` | 5 |
| `_REPS` | 5 |
| `_PIPELINE` | 47 |
| `_BLOCKER_PLAYBOOK` | 5 |
| `_ACTIVE_STAGES` | 5 |

## Exact dataset `_STAGE_BENCHMARKS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "Contract": 10,
  "Discovery": 18,
  "Negotiation": 12,
  "Proposal": 16,
  "Qualification": 14
}
```

## Exact dataset `_REPS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "active_deals": 11,
    "capacity": 14,
    "name": "Mike Chen",
    "specialty": "executive alignment",
    "title": "Sr. Account Executive"
  },
  {
    "active_deals": 9,
    "capacity": 12,
    "name": "Lisa Torres",
    "specialty": "contract negotiation",
    "title": "Account Executive"
  },
  {
    "active_deals": 12,
    "capacity": 14,
    "name": "James Park",
    "specialty": "technical sales",
    "title": "Sr. Account Executive"
  },
  {
    "active_deals": 8,
    "capacity": 12,
    "name": "Sarah Kim",
    "specialty": "executive alignment",
    "title": "Account Executive"
  },
  {
    "active_deals": 7,
    "capacity": 12,
    "name": "Ryan Davis",
    "specialty": "mid-market",
    "title": "Account Executive"
  }
]
```

## Exact dataset `_PIPELINE`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "account": "TechCorp Industries",
    "blocker": "executive_change",
    "champion_name": "VP IT - Mark Reynolds",
    "champion_status": "Silent",
    "days_in_stage": 34,
    "id": "OPP-001",
    "last_contact_days": 18,
    "name": "TechCorp Industries",
    "owner": "Mike Chen",
    "stage": "Proposal",
    "value": 890000
  },
  {
    "account": "Global Manufacturing",
    "blocker": "legal_review",
    "champion_name": "Dir. Ops - Rachel Green",
    "champion_status": "Active frustrated",
    "days_in_stage": 28,
    "id": "OPP-002",
    "last_contact_days": 5,
    "name": "Global Manufacturing",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 720000
  },
  {
    "account": "Apex Financial Group",
    "blocker": "competitor_eval",
    "champion_name": "CTO - David Liu",
    "champion_status": "Disengaged",
    "days_in_stage": 25,
    "id": "OPP-003",
    "last_contact_days": 12,
    "name": "Apex Financial",
    "owner": "James Park",
    "stage": "Discovery",
    "value": 580000
  },
  {
    "account": "Metro Health Systems",
    "blocker": "budget_hold",
    "champion_name": "VP Digital - Sandra Patel",
    "champion_status": "Active",
    "days_in_stage": 22,
    "id": "OPP-004",
    "last_contact_days": 9,
    "name": "Metro Healthcare",
    "owner": "Mike Chen",
    "stage": "Proposal",
    "value": 440000
  },
  {
    "account": "Pinnacle Logistics Inc.",
    "blocker": "no_champion",
    "champion_name": "IT Dir - Tom Bradley",
    "champion_status": "Silent",
    "days_in_stage": 20,
    "id": "OPP-005",
    "last_contact_days": 14,
    "name": "Pinnacle Logistics",
    "owner": "James Park",
    "stage": "Qualification",
    "value": 360000
  },
  {
    "account": "Summit Retail Group",
    "blocker": "competitor_eval",
    "champion_name": "COO - Angela Morris",
    "champion_status": "Lukewarm",
    "days_in_stage": 24,
    "id": "OPP-006",
    "last_contact_days": 11,
    "name": "Summit Retail Group",
    "owner": "Sarah Kim",
    "stage": "Discovery",
    "value": 310000
  },
  {
    "account": "Vanguard Energy Corp",
    "blocker": "executive_change",
    "champion_name": "VP Eng - Carlos Reyes",
    "champion_status": "Silent",
    "days_in_stage": 21,
    "id": "OPP-007",
    "last_contact_days": 16,
    "name": "Vanguard Energy",
    "owner": "Ryan Davis",
    "stage": "Proposal",
    "value": 270000
  },
  {
    "account": "Cascade Media Holdings",
    "blocker": "legal_review",
    "champion_name": "Dir. Tech - Nina Chow",
    "champion_status": "Active",
    "days_in_stage": 18,
    "id": "OPP-008",
    "last_contact_days": 7,
    "name": "Cascade Media",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 220000
  },
  {
    "account": "Atlas Construction Co.",
    "blocker": "no_champion",
    "champion_name": "None identified",
    "champion_status": "None",
    "days_in_stage": 19,
    "id": "OPP-009",
    "last_contact_days": 20,
    "name": "Atlas Construction",
    "owner": "James Park",
    "stage": "Qualification",
    "value": 180000
  },
  {
    "account": "Horizon Pharmaceuticals",
    "blocker": "budget_hold",
    "champion_name": "VP R&D - Greg Foster",
    "champion_status": "Disengaged",
    "days_in_stage": 22,
    "id": "OPP-010",
    "last_contact_days": 13,
    "name": "Horizon Pharma",
    "owner": "Sarah Kim",
    "stage": "Discovery",
    "value": 150000
  },
  {
    "account": "Sterling Insurance Co.",
    "blocker": "competitor_eval",
    "champion_name": "CIO - Barbara Wells",
    "champion_status": "Lukewarm",
    "days_in_stage": 20,
    "id": "OPP-011",
    "last_contact_days": 15,
    "name": "Sterling Insurance",
    "owner": "Mike Chen",
    "stage": "Proposal",
    "value": 130000
  },
  {
    "account": "Redwood Education Group",
    "blocker": "budget_hold",
    "champion_name": "Dir. IT - Paul Simmons",
    "champion_status": "Active",
    "days_in_stage": 18,
    "id": "OPP-012",
    "last_contact_days": 10,
    "name": "Redwood Education",
    "owner": "Ryan Davis",
    "stage": "Qualification",
    "value": 110000
  },
  {
    "account": "Pacific Telecom Inc.",
    "blocker": "procurement_process",
    "champion_name": "SVP Ops - Diana Cruz",
    "champion_status": "Active",
    "days_in_stage": 14,
    "id": "OPP-013",
    "last_contact_days": 3,
    "name": "Pacific Telecom",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 780000
  },
  {
    "account": "Northstar Aerospace",
    "blocker": "technical_validation",
    "champion_name": "VP IT - Kyle Jensen",
    "champion_status": "Active",
    "days_in_stage": 17,
    "id": "OPP-014",
    "last_contact_days": 4,
    "name": "Northstar Aerospace",
    "owner": "Mike Chen",
    "stage": "Proposal",
    "value": 650000
  },
  {
    "account": "Beacon Financial Corp",
    "blocker": "stakeholder_alignment",
    "champion_name": "CTO - Amy Nakamura",
    "champion_status": "Active",
    "days_in_stage": 19,
    "id": "OPP-015",
    "last_contact_days": 6,
    "name": "Beacon Financial",
    "owner": "James Park",
    "stage": "Discovery",
    "value": 520000
  },
  {
    "account": "Crestline Hospitality",
    "blocker": "timeline_uncertainty",
    "champion_name": "Dir. Digital - Frank Russo",
    "champion_status": "Active",
    "days_in_stage": 15,
    "id": "OPP-016",
    "last_contact_days": 5,
    "name": "Crestline Hotels",
    "owner": "Sarah Kim",
    "stage": "Qualification",
    "value": 480000
  },
  {
    "account": "Ironbridge Steel Corp",
    "blocker": "stakeholder_alignment",
    "champion_name": "VP Mfg - Helen Park",
    "champion_status": "Active",
    "days_in_stage": 17,
    "id": "OPP-017",
    "last_contact_days": 4,
    "name": "Ironbridge Steel",
    "owner": "Ryan Davis",
    "stage": "Proposal",
    "value": 410000
  },
  {
    "account": "Emerald Biotech Ltd.",
    "blocker": "procurement_process",
    "champion_name": "CIO - Roger Tran",
    "champion_status": "Active",
    "days_in_stage": 13,
    "id": "OPP-018",
    "last_contact_days": 2,
    "name": "Emerald Biotech",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 370000
  },
  {
    "account": "Sapphire Analytics Inc.",
    "blocker": "technical_validation",
    "champion_name": "VP Data - Megan Lowe",
    "champion_status": "Active",
    "days_in_stage": 19,
    "id": "OPP-019",
    "last_contact_days": 7,
    "name": "Sapphire Analytics",
    "owner": "James Park",
    "stage": "Discovery",
    "value": 290000
  },
  {
    "account": "DataFlow Corp",
    "blocker": "none",
    "champion_name": "VP Eng - Steve Hall",
    "champion_status": "Active",
    "days_in_stage": 3,
    "id": "OPP-020",
    "last_contact_days": 1,
    "name": "DataFlow Corp",
    "owner": "Lisa Torres",
    "stage": "Contract",
    "value": 340000
  },
  {
    "account": "Summit Industries Inc.",
    "blocker": "none",
    "champion_name": "CTO - Laura Adams",
    "champion_status": "Active",
    "days_in_stage": 5,
    "id": "OPP-021",
    "last_contact_days": 1,
    "name": "Summit Industries",
    "owner": "Mike Chen",
    "stage": "Contract",
    "value": 280000
  },
  {
    "account": "Tech Dynamics LLC",
    "blocker": "none",
    "champion_name": "IT Dir - Ben Wright",
    "champion_status": "Active",
    "days_in_stage": 2,
    "id": "OPP-022",
    "last_contact_days": 0,
    "name": "Tech Dynamics",
    "owner": "Sarah Kim",
    "stage": "Contract",
    "value": 190000
  },
  {
    "account": "Orion Software Inc.",
    "blocker": "none",
    "champion_name": "VP Prod - Jill Carter",
    "champion_status": "Active",
    "days_in_stage": 5,
    "id": "OPP-023",
    "last_contact_days": 1,
    "name": "Orion Software",
    "owner": "James Park",
    "stage": "Negotiation",
    "value": 420000
  },
  {
    "account": "Vertex Solutions Corp",
    "blocker": "none",
    "champion_name": "CIO - Dan Mitchell",
    "champion_status": "Active",
    "days_in_stage": 8,
    "id": "OPP-024",
    "last_contact_days": 2,
    "name": "Vertex Solutions",
    "owner": "Ryan Davis",
    "stage": "Proposal",
    "value": 380000
  },
  {
    "account": "Phoenix Consulting Grp",
    "blocker": "none",
    "champion_name": "CEO - Tina Brooks",
    "champion_status": "Active",
    "days_in_stage": 10,
    "id": "OPP-025",
    "last_contact_days": 3,
    "name": "Phoenix Consulting",
    "owner": "Mike Chen",
    "stage": "Discovery",
    "value": 310000
  },
  {
    "account": "Cirrus Cloud Services",
    "blocker": "none",
    "champion_name": "VP Infra - Raj Patel",
    "champion_status": "Active",
    "days_in_stage": 7,
    "id": "OPP-026",
    "last_contact_days": 2,
    "name": "Cirrus Cloud Services",
    "owner": "Lisa Torres",
    "stage": "Proposal",
    "value": 540000
  },
  {
    "account": "Quantum Analytics LLC",
    "blocker": "none",
    "champion_name": "CTO - Eric Saunders",
    "champion_status": "Active",
    "days_in_stage": 9,
    "id": "OPP-027",
    "last_contact_days": 4,
    "name": "Quantum Analytics",
    "owner": "Sarah Kim",
    "stage": "Discovery",
    "value": 290000
  },
  {
    "account": "Bluewave Telecom Inc.",
    "blocker": "none",
    "champion_name": "SVP Tech - Maria Gonzalez",
    "champion_status": "Active",
    "days_in_stage": 6,
    "id": "OPP-028",
    "last_contact_days": 1,
    "name": "Bluewave Telecom",
    "owner": "James Park",
    "stage": "Negotiation",
    "value": 460000
  },
  {
    "account": "Granite Capital Mgmt",
    "blocker": "none",
    "champion_name": "Dir. IT - Jake Morton",
    "champion_status": "Active",
    "days_in_stage": 7,
    "id": "OPP-029",
    "last_contact_days": 3,
    "name": "Granite Capital",
    "owner": "Mike Chen",
    "stage": "Qualification",
    "value": 350000
  },
  {
    "account": "Silverline Media Group",
    "blocker": "none",
    "champion_name": "VP Tech - Olivia Hart",
    "champion_status": "Active",
    "days_in_stage": 6,
    "id": "OPP-030",
    "last_contact_days": 2,
    "name": "Silverline Media",
    "owner": "Ryan Davis",
    "stage": "Proposal",
    "value": 230000
  },
  {
    "account": "Trident Mfg Corp",
    "blocker": "none",
    "champion_name": "COO - William Chen",
    "champion_status": "Active",
    "days_in_stage": 4,
    "id": "OPP-031",
    "last_contact_days": 1,
    "name": "Trident Manufacturing",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 510000
  },
  {
    "account": "Falcon Logistics Inc.",
    "blocker": "none",
    "champion_name": "VP Ops - Christine Lee",
    "champion_status": "Active",
    "days_in_stage": 11,
    "id": "OPP-032",
    "last_contact_days": 3,
    "name": "Falcon Logistics",
    "owner": "Sarah Kim",
    "stage": "Discovery",
    "value": 270000
  },
  {
    "account": "Prism Technologies LLC",
    "blocker": "none",
    "champion_name": "CTO - Derek Nash",
    "champion_status": "Active",
    "days_in_stage": 9,
    "id": "OPP-033",
    "last_contact_days": 2,
    "name": "Prism Technologies",
    "owner": "James Park",
    "stage": "Proposal",
    "value": 390000
  },
  {
    "account": "Keystone Health Corp",
    "blocker": "none",
    "champion_name": "VP Digital - Susan Park",
    "champion_status": "Active",
    "days_in_stage": 8,
    "id": "OPP-034",
    "last_contact_days": 4,
    "name": "Keystone Health",
    "owner": "Mike Chen",
    "stage": "Qualification",
    "value": 320000
  },
  {
    "account": "Neptune Shipping Co.",
    "blocker": "none",
    "champion_name": "CIO - Alan Foster",
    "champion_status": "Active",
    "days_in_stage": 6,
    "id": "OPP-035",
    "last_contact_days": 2,
    "name": "Neptune Shipping",
    "owner": "Ryan Davis",
    "stage": "Discovery",
    "value": 180000
  },
  {
    "account": "Ember Software Inc.",
    "blocker": "none",
    "champion_name": "VP Eng - Kevin Zhao",
    "champion_status": "Active",
    "days_in_stage": 5,
    "id": "OPP-036",
    "last_contact_days": 1,
    "name": "Ember Software",
    "owner": "Lisa Torres",
    "stage": "Proposal",
    "value": 450000
  },
  {
    "account": "Ridgeline Capital Grp",
    "blocker": "none",
    "champion_name": "Dir. Tech - Nancy White",
    "champion_status": "Active",
    "days_in_stage": 3,
    "id": "OPP-037",
    "last_contact_days": 1,
    "name": "Ridgeline Capital",
    "owner": "Sarah Kim",
    "stage": "Negotiation",
    "value": 260000
  },
  {
    "account": "Aurora Aerospace Ltd.",
    "blocker": "none",
    "champion_name": "SVP Eng - Robert Kim",
    "champion_status": "Active",
    "days_in_stage": 8,
    "id": "OPP-038",
    "last_contact_days": 3,
    "name": "Aurora Aerospace",
    "owner": "James Park",
    "stage": "Discovery",
    "value": 530000
  },
  {
    "account": "Cobalt Chemical Corp",
    "blocker": "none",
    "champion_name": "VP IT - Dorothy Mills",
    "champion_status": "Active",
    "days_in_stage": 5,
    "id": "OPP-039",
    "last_contact_days": 2,
    "name": "Cobalt Chemicals",
    "owner": "Mike Chen",
    "stage": "Qualification",
    "value": 200000
  },
  {
    "account": "Zenith Insurance Group",
    "blocker": "none",
    "champion_name": "CTO - Philip Grant",
    "champion_status": "Active",
    "days_in_stage": 4,
    "id": "OPP-040",
    "last_contact_days": 1,
    "name": "Zenith Insurance",
    "owner": "Ryan Davis",
    "stage": "Proposal",
    "value": 340000
  },
  {
    "account": "Legacy Health Systems",
    "blocker": "none",
    "champion_name": "Dir. Digital - Kelly Young",
    "champion_status": "Active",
    "days_in_stage": 7,
    "id": "OPP-041",
    "last_contact_days": 2,
    "name": "Legacy Healthcare",
    "owner": "Lisa Torres",
    "stage": "Negotiation",
    "value": 280000
  },
  {
    "account": "Pinnacle Software Inc.",
    "blocker": "none",
    "champion_name": "VP Prod - Brian Hughes",
    "champion_status": "Active",
    "days_in_stage": 7,
    "id": "OPP-042",
    "last_contact_days": 3,
    "name": "Pinnacle Software",
    "owner": "Sarah Kim",
    "stage": "Discovery",
    "value": 410000
  },
  {
    "account": "Titan Energy Corp",
    "blocker": "none",
    "champion_name": "CIO - Martha Clark",
    "champion_status": "Active",
    "days_in_stage": 10,
    "id": "OPP-043",
    "last_contact_days": 2,
    "name": "Titan Energy",
    "owner": "James Park",
    "stage": "Proposal",
    "value": 370000
  },
  {
    "account": "Axiom Partners LLC",
    "blocker": "none",
    "champion_name": "CEO - Janet Rivera",
    "champion_status": "Won",
    "days_in_stage": 0,
    "id": "OPP-044",
    "last_contact_days": 0,
    "name": "Axiom Partners",
    "owner": "Mike Chen",
    "stage": "Closed Won",
    "value": 520000
  },
  {
    "account": "Delta Dynamics Corp",
    "blocker": "none",
    "champion_name": "VP Ops - Scott Morgan",
    "champion_status": "Won",
    "days_in_stage": 0,
    "id": "OPP-045",
    "last_contact_days": 0,
    "name": "Delta Dynamics",
    "owner": "Lisa Torres",
    "stage": "Closed Won",
    "value": 310000
  },
  {
    "account": "Vector Analytics Inc.",
    "blocker": "none",
    "champion_name": "CTO - Lisa Brown",
    "champion_status": "Won",
    "days_in_stage": 0,
    "id": "OPP-046",
    "last_contact_days": 0,
    "name": "Vector Analytics",
    "owner": "Sarah Kim",
    "stage": "Closed Won",
    "value": 190000
  },
  {
    "account": "Omega Systems Inc.",
    "blocker": "competitor_won",
    "champion_name": "VP IT - Chris Taylor",
    "champion_status": "Lost",
    "days_in_stage": 0,
    "id": "OPP-047",
    "last_contact_days": 0,
    "name": "Omega Systems",
    "owner": "James Park",
    "stage": "Closed Lost",
    "value": 430000
  }
]
```

## Exact dataset `_BLOCKER_PLAYBOOK`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "budget_hold": {
    "diagnosis": "Budget approval stalled or deprioritized",
    "resource": "value engineering team",
    "week1": [
      "Day 1: Confirm budget timeline with champion",
      "Day 2: Build CFO-ready business case with 3-year TCO",
      "Day 3: Offer phased implementation to reduce upfront cost",
      "Day 5: Provide flexible payment terms proposal"
    ],
    "week2": [
      "Schedule CFO meeting with ROI walkthrough",
      "Share peer company case study with hard ROI numbers"
    ]
  },
  "competitor_eval": {
    "diagnosis": "Active competitive evaluation in progress",
    "resource": "competitive intelligence team",
    "week1": [
      "Day 1: Request competitive landscape details from champion",
      "Day 2: Prepare head-to-head comparison deck",
      "Day 3: Schedule technical deep-dive vs competitor capabilities",
      "Day 5: Deliver customer reference calls in same vertical"
    ],
    "week2": [
      "Provide proof-of-value pilot offer",
      "Executive peer reference call",
      "Submit best-and-final with differentiated terms"
    ]
  },
  "executive_change": {
    "diagnosis": "Champion disengaged, economic buyer changed",
    "resource": "exec alignment specialist",
    "week1": [
      "Day 1: Research new executive background (LinkedIn, news)",
      "Day 2: Call existing champion — acknowledge gap, request intro",
      "Day 3: Send executive-tailored ROI analysis",
      "Day 5: Executive sponsor outreach (your VP to their exec)"
    ],
    "week2": [
      "Schedule executive meeting with business case",
      "Re-present proposal with finance lens",
      "Establish new champion relationship"
    ]
  },
  "legal_review": {
    "diagnosis": "Process bottleneck, not relationship issue",
    "resource": "legal team fast-track review",
    "week1": [
      "Today: Call champion — acknowledge legal delay",
      "Tomorrow: Prepare the synthetic contract template for authorized legal and seller review",
      "Day 3: Offer 30-day out clause to reduce perceived risk",
      "Day 5: Legal-to-legal call to resolve remaining items"
    ],
    "week2": [
      "Follow up on outstanding redline items",
      "Escalate any remaining blockers to VP Legal"
    ]
  },
  "no_champion": {
    "diagnosis": "No internal champion identified or engaged",
    "resource": "senior AE for relationship building",
    "week1": [
      "Day 1: Map org chart and identify 3 potential champions",
      "Day 2: Multi-thread outreach via LinkedIn and email",
      "Day 3: Offer executive briefing or lunch-and-learn",
      "Day 5: Ask existing contacts for warm introductions"
    ],
    "week2": [
      "Host on-site workshop to build relationships",
      "Provide industry insights to create value before selling",
      "Identify and cultivate power sponsor"
    ]
  }
}
```

## Exact dataset `_ACTIVE_STAGES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "Contract",
  "Discovery",
  "Negotiation",
  "Proposal",
  "Qualification"
]
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
