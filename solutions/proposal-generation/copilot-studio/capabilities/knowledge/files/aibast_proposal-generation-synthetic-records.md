# Proposal Generation Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/b2b_sales_stacks/proposal_generation_stack/proposal_generation_agent.py`
- Strict transcript evidence: `solutions/proposal-generation/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:41:48.365516+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_RFPS` | 3 |
| `_PRODUCT_CATALOG` | 6 |
| `_SOLUTION_CONFIGS` | 3 |
| `_DISCOUNT_RULES` | 3 |
| `_REFERENCES` | 8 |
| `_COMPETITOR_CAPABILITIES` | 3 |
| `_OUR_CAPABILITIES` | 7 |
| `_IMPL_PHASES` | 3 |

## Exact dataset `_RFPS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "contoso": {
    "account": "Contoso Technologies",
    "budget_ceiling": 850000,
    "competitors_shortlisted": [
      "CompetitorA"
    ],
    "deal_value": 800000,
    "decision_timeline_days": 21,
    "existing_assets": [
      "Cloud migration playbook",
      "SOC 2 Type II audit report",
      "Multi-cloud architecture reference"
    ],
    "id": "RFP-2024-0152",
    "industry": "Technology",
    "key_stakeholder": "VP Engineering Alex Kim",
    "project": "Cloud Migration & Modernization",
    "requirements": [
      {
        "category": "Technical",
        "id": "R1",
        "text": "Multi-cloud orchestration (AWS + Azure)",
        "weight": 0.3
      },
      {
        "category": "Delivery",
        "id": "R2",
        "text": "Zero-downtime migration methodology",
        "weight": 0.25
      },
      {
        "category": "Compliance",
        "id": "R3",
        "text": "SOC 2 Type II compliance",
        "weight": 0.15
      },
      {
        "category": "Support",
        "id": "R4",
        "text": "24/7 managed services post-migration",
        "weight": 0.2
      },
      {
        "category": "Training",
        "id": "R5",
        "text": "Knowledge transfer and runbooks",
        "weight": 0.1
      }
    ]
  },
  "meridian": {
    "account": "Meridian Healthcare",
    "budget_ceiling": 1250000,
    "competitors_shortlisted": [
      "CompetitorA",
      "CompetitorB"
    ],
    "deal_value": 1200000,
    "decision_timeline_days": 14,
    "existing_assets": [
      "Healthcare case study (Memorial Health System)",
      "HIPAA compliance documentation",
      "Implementation methodology deck",
      "Training curriculum template"
    ],
    "id": "RFP-2024-0147",
    "industry": "Healthcare",
    "key_stakeholder": "CIO Amanda Foster",
    "project": "Digital Transformation Platform",
    "requirements": [
      {
        "category": "Technical",
        "id": "R1",
        "text": "EHR integration capabilities",
        "weight": 0.25
      },
      {
        "category": "Compliance",
        "id": "R2",
        "text": "HIPAA compliance certification",
        "weight": 0.2
      },
      {
        "category": "Support",
        "id": "R3",
        "text": "24/7 support SLA with <15-min response",
        "weight": 0.15
      },
      {
        "category": "Delivery",
        "id": "R4",
        "text": "Implementation under 16 weeks",
        "weight": 0.2
      },
      {
        "category": "Training",
        "id": "R5",
        "text": "Comprehensive staff training program",
        "weight": 0.1
      },
      {
        "category": "Technical",
        "id": "R6",
        "text": "Data migration from legacy systems",
        "weight": 0.1
      }
    ]
  },
  "pinnacle": {
    "account": "Pinnacle Financial Group",
    "budget_ceiling": 1600000,
    "competitors_shortlisted": [
      "CompetitorA",
      "CompetitorB",
      "CompetitorC"
    ],
    "deal_value": 1500000,
    "decision_timeline_days": 30,
    "existing_assets": [
      "Financial services case study (Atlantic Credit Union)",
      "PCI-DSS compliance package",
      "Branch rollout methodology"
    ],
    "id": "RFP-2024-0159",
    "industry": "Financial Services",
    "key_stakeholder": "CTO Marcus Webb",
    "project": "Core Banking Platform Upgrade",
    "requirements": [
      {
        "category": "Technical",
        "id": "R1",
        "text": "Real-time transaction processing (<50ms)",
        "weight": 0.25
      },
      {
        "category": "Compliance",
        "id": "R2",
        "text": "PCI-DSS Level 1 and SOX compliance",
        "weight": 0.25
      },
      {
        "category": "Support",
        "id": "R3",
        "text": "99.999% uptime SLA",
        "weight": 0.2
      },
      {
        "category": "Delivery",
        "id": "R4",
        "text": "Phased rollout across 120 branches",
        "weight": 0.2
      },
      {
        "category": "Training",
        "id": "R5",
        "text": "End-user and admin training certification",
        "weight": 0.1
      }
    ]
  }
}
```

## Exact dataset `_PRODUCT_CATALOG`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "analytics_module": {
    "category": "Software",
    "list_price": 80000,
    "margin_floor": 0.45,
    "name": "Analytics & Reporting"
  },
  "implementation": {
    "category": "Services",
    "list_price": 380000,
    "margin_floor": 0.35,
    "name": "Implementation Services"
  },
  "integration_suite": {
    "category": "Software",
    "list_price": 180000,
    "margin_floor": 0.4,
    "name": "Integration Suite"
  },
  "platform_core": {
    "category": "Software",
    "list_price": 420000,
    "margin_floor": 0.38,
    "name": "Platform Core License"
  },
  "support_3yr": {
    "category": "Support",
    "list_price": 180000,
    "margin_floor": 0.55,
    "name": "3-Year Premium Support"
  },
  "training": {
    "category": "Services",
    "list_price": 120000,
    "margin_floor": 0.5,
    "name": "Training Program"
  }
}
```

## Exact dataset `_SOLUTION_CONFIGS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "Financial Services": [
    "platform_core",
    "integration_suite",
    "analytics_module",
    "implementation",
    "training",
    "support_3yr"
  ],
  "Healthcare": [
    "platform_core",
    "integration_suite",
    "analytics_module",
    "implementation",
    "training",
    "support_3yr"
  ],
  "Technology": [
    "platform_core",
    "integration_suite",
    "implementation",
    "training",
    "support_3yr"
  ]
}
```

## Exact dataset `_DISCOUNT_RULES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "Services": {
    "base": 0.1,
    "max": 0.18,
    "volume_bonus": 0.04,
    "volume_threshold": 400000
  },
  "Software": {
    "base": 0.08,
    "max": 0.15,
    "volume_bonus": 0.03,
    "volume_threshold": 600000
  },
  "Support": {
    "base": 0.25,
    "max": 0.35,
    "volume_bonus": 0.05,
    "volume_threshold": 150000
  }
}
```

## Exact dataset `_REFERENCES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "contact_ready": true,
    "customer": "Memorial Health System",
    "impl_weeks": 11,
    "industry": "Healthcare",
    "results": "34% efficiency gain, $2.4M annual savings",
    "size": "8 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Pacific Medical Group",
    "impl_weeks": 14,
    "industry": "Healthcare",
    "results": "$2.4M savings/year, 99.9% uptime",
    "size": "15 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Summit Healthcare Network",
    "impl_weeks": 12,
    "industry": "Healthcare",
    "results": "12-week go-live, 28% cost reduction",
    "size": "6 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Atlas Cloud Services",
    "impl_weeks": 10,
    "industry": "Technology",
    "results": "Zero-downtime migration, 40% infra cost reduction",
    "size": "800 employees"
  },
  {
    "contact_ready": false,
    "customer": "Nexus Software Corp",
    "impl_weeks": 8,
    "industry": "Technology",
    "results": "3x deployment velocity, 99.95% uptime",
    "size": "2,400 employees"
  },
  {
    "contact_ready": true,
    "customer": "Atlantic Credit Union",
    "impl_weeks": 16,
    "industry": "Financial Services",
    "results": "Sub-30ms latency, zero audit findings",
    "size": "120 branches"
  },
  {
    "contact_ready": true,
    "customer": "Sentinel Insurance",
    "impl_weeks": 14,
    "industry": "Financial Services",
    "results": "PCI-DSS compliant in 90 days, 22% ops savings",
    "size": "$4B AUM"
  },
  {
    "contact_ready": false,
    "customer": "Vanguard Logistics",
    "impl_weeks": 12,
    "industry": "Manufacturing",
    "results": "18% throughput improvement",
    "size": "3,200 employees"
  }
]
```

## Exact dataset `_COMPETITOR_CAPABILITIES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "CompetitorA": {
    "ehr_integration": "Third-party",
    "hipaa_certified": true,
    "impl_weeks": 20,
    "pricing_position": "Market rate",
    "strengths": [
      "Large install base",
      "Brand recognition"
    ],
    "support_sla_min": 240,
    "weaknesses": [
      "Slow implementation",
      "Middleware dependency"
    ]
  },
  "CompetitorB": {
    "ehr_integration": "Native",
    "hipaa_certified": false,
    "impl_weeks": 16,
    "pricing_position": "+5% above market",
    "strengths": [
      "Native integrations",
      "Modern UI"
    ],
    "support_sla_min": 60,
    "weaknesses": [
      "HIPAA pending",
      "Limited references"
    ]
  },
  "CompetitorC": {
    "ehr_integration": "Third-party",
    "hipaa_certified": true,
    "impl_weeks": 24,
    "pricing_position": "-10% below market",
    "strengths": [
      "Low price",
      "Long track record"
    ],
    "support_sla_min": 120,
    "weaknesses": [
      "Legacy architecture",
      "High customization cost"
    ]
  }
}
```

## Exact dataset `_OUR_CAPABILITIES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "certifications": [
    "SOC 2 Type II",
    "HIPAA",
    "ISO 27001",
    "PCI-DSS Level 1"
  ],
  "differentiators": [
    "Pre-built healthcare accelerators cut implementation by 40%",
    "Native EHR integration eliminates middleware costs",
    "15-minute support SLA is fastest in industry",
    "API-first architecture for seamless ecosystem integration"
  ],
  "ehr_integration": "Native",
  "hipaa_certified": true,
  "impl_weeks": 12,
  "pricing_position": "Market rate",
  "support_sla_min": 15
}
```

## Exact dataset `_IMPL_PHASES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "activities": [
      "Infrastructure assessment",
      "Connector deployment",
      "Security configuration",
      "Core team training"
    ],
    "duration_weeks": 4,
    "name": "Foundation",
    "phase": 1
  },
  {
    "activities": [
      "Phased facility deployment",
      "Workflow integration",
      "Staff certification",
      "Go-live support"
    ],
    "duration_weeks": 6,
    "name": "Rollout",
    "phase": 2
  },
  {
    "activities": [
      "Performance tuning",
      "Advanced training",
      "Success metrics validation",
      "Handoff to support"
    ],
    "duration_weeks": 2,
    "name": "Optimization",
    "phase": 3
  }
]
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
