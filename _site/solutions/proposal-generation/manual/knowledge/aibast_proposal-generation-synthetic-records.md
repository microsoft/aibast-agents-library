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
| `_GROUP_DISCOUNTS` | 3 |
| `_REFERENCES` | 8 |
| `_COMPETITOR_CAPABILITIES` | 3 |
| `_OUR_CAPABILITIES` | 7 |
| `_CAPABILITY_FIT` | 13 |
| `_IMPL_PHASES` | 3 |
| `_PROPOSAL_SECTIONS` | 8 |
| `_DELIVERY_PACKAGE` | 3 |

## Demo scenario (default account: Meridian Healthcare)

- Deal: Meridian Healthcare, Digital Transformation Platform, RFP-2024-0147; deal value $1.2M; decision in 2 weeks;
  stakeholder CIO Amanda Foster; competition 2 vendors shortlisted; budget ceiling $1,250,000.
- RFP requirements: EHR integration, HIPAA compliance, 24/7 support, 16-week implementation, training.
  Existing assets found: Healthcare case study, HIPAA docs, Implementation deck.
- Executive summary (Your Need -> Our Solution): EHR Integration -> Epic & Cerner certified; HIPAA Compliance ->
  SOC 2 + HIPAA certified; Deployment -> 12 weeks (beats your 16); Support -> 24/7, 15-min SLA. Proof: Memorial
  Health achieved 34% efficiency gain, $2.4M savings. Investment: $1.18M (3 years support + training included).
- 12-Week Plan: Foundation (wks 1-4) > Rollout (wks 5-10) > Optimization (wks 11-12).
- Pricing (computed from `_PRODUCT_CATALOG` and `_GROUP_DISCOUNTS`, proposed prices rounded to the nearest $1,000):
  Software list $681,000 -> $620K (9% savings); Implementation $382,000 -> $340K (11%); Training + Support
  $293,000 -> $220K (25%); Total $1,356,000 -> $1.18M (13% savings, $176,000). Cost $684,400, so margin 42%
  maintained (target 40%+).
- References (same industry): Memorial Health 34% efficiency gain; Pacific Medical $2.4M/year savings; Summit
  Healthcare 12-week go-live. Your edge vs competition: Implementation 12 wks (vs 16-20); Epic integration Native
  (not third-party); Support SLA 15 min (vs 1-4 hours). Win Theme: Speed + Compliance + Support.
- Compiled draft: 38 pages (sum of `_PROPOSAL_SECTIONS`); Package Contents: Executive Summary + Solution
  Architecture, 12-week Implementation Plan, Pricing ($1.18M) + References (3), HIPAA + SOC 2 certificates
  attached; Delivery Package (drafts): PDF proposal, 12-slide exec presentation, pricing spreadsheet; Checklist:
  Legal, Pricing and Branding ready for review. Nothing is sent; the seller shares the package after review.

## Exact dataset `_RFPS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "contoso": {
    "account": "Contoso Technologies",
    "budget_ceiling": 850000,
    "certificates": [
      "SOC 2"
    ],
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
    ],
    "summary_rows": [
      [
        "Multi-cloud",
        "AWS + Azure orchestration layer"
      ],
      [
        "Zero downtime",
        "Blue-green migration with rollback"
      ],
      [
        "Compliance",
        "SOC 2 Type II audit current"
      ],
      [
        "Support",
        "24/7 managed services, 15-min SLA"
      ]
    ]
  },
  "meridian": {
    "account": "Meridian Healthcare",
    "budget_ceiling": 1250000,
    "certificates": [
      "HIPAA",
      "SOC 2"
    ],
    "competitors_shortlisted": [
      "CompetitorA",
      "CompetitorB"
    ],
    "deal_value": 1200000,
    "decision_timeline_days": 14,
    "existing_assets": [
      "Healthcare case study",
      "HIPAA docs",
      "Implementation deck"
    ],
    "id": "RFP-2024-0147",
    "industry": "Healthcare",
    "key_stakeholder": "CIO Amanda Foster",
    "project": "Digital Transformation Platform",
    "requirements": [
      {
        "category": "Technical",
        "id": "R1",
        "text": "EHR integration",
        "weight": 0.25
      },
      {
        "category": "Compliance",
        "id": "R2",
        "text": "HIPAA compliance",
        "weight": 0.25
      },
      {
        "category": "Support",
        "id": "R3",
        "text": "24/7 support",
        "weight": 0.15
      },
      {
        "category": "Delivery",
        "id": "R4",
        "text": "16-week implementation",
        "weight": 0.2
      },
      {
        "category": "Training",
        "id": "R5",
        "text": "Training",
        "weight": 0.15
      }
    ],
    "summary_rows": [
      [
        "EHR Integration",
        "Epic & Cerner certified"
      ],
      [
        "HIPAA Compliance",
        "SOC 2 + HIPAA certified"
      ],
      [
        "Deployment",
        "12 weeks (beats your 16)"
      ],
      [
        "Support",
        "24/7, 15-min SLA"
      ]
    ]
  },
  "pinnacle": {
    "account": "Pinnacle Financial Group",
    "budget_ceiling": 1600000,
    "certificates": [
      "PCI-DSS Level 1",
      "SOC 2"
    ],
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
    ],
    "summary_rows": [
      [
        "Real-time processing",
        "Sub-30ms transaction processing"
      ],
      [
        "Compliance",
        "PCI-DSS Level 1 certified"
      ],
      [
        "Uptime",
        "Architecture supports five-nines"
      ],
      [
        "Rollout",
        "Branch-by-branch methodology"
      ]
    ]
  }
}
```

## Exact dataset `_PRODUCT_CATALOG`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "analytics_module": {
    "cost": 35000,
    "group": "Software",
    "list_price": 80000,
    "name": "Analytics & Reporting"
  },
  "implementation": {
    "cost": 238000,
    "group": "Implementation",
    "list_price": 382000,
    "name": "Implementation Services"
  },
  "integration_suite": {
    "cost": 85000,
    "group": "Software",
    "list_price": 180000,
    "name": "Integration Suite"
  },
  "platform_core": {
    "cost": 190000,
    "group": "Software",
    "list_price": 421000,
    "name": "Platform Core License"
  },
  "support_3yr": {
    "cost": 75000,
    "group": "Training + Support",
    "list_price": 180000,
    "name": "3-Year Premium Support"
  },
  "training": {
    "cost": 61400,
    "group": "Training + Support",
    "list_price": 113000,
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

## Exact dataset `_GROUP_DISCOUNTS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "discount_pct": 9,
    "group": "Software"
  },
  {
    "discount_pct": 11,
    "group": "Implementation"
  },
  {
    "discount_pct": 25,
    "group": "Training + Support"
  }
]
```

## Exact dataset `_REFERENCES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "contact_ready": true,
    "customer": "Memorial Health",
    "headline": "34% efficiency gain",
    "impl_weeks": 11,
    "industry": "Healthcare",
    "results": "34% efficiency gain, $2.4M savings",
    "size": "8 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Pacific Medical",
    "headline": "$2.4M/year savings",
    "impl_weeks": 14,
    "industry": "Healthcare",
    "results": "$2.4M/year savings, 99.9% uptime",
    "size": "15 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Summit Healthcare",
    "headline": "12-week go-live",
    "impl_weeks": 12,
    "industry": "Healthcare",
    "results": "12-week go-live, 28% cost reduction",
    "size": "6 facilities"
  },
  {
    "contact_ready": true,
    "customer": "Atlas Cloud Services",
    "headline": "Zero-downtime migration",
    "impl_weeks": 10,
    "industry": "Technology",
    "results": "Zero-downtime migration, 40% infra cost reduction",
    "size": "800 employees"
  },
  {
    "contact_ready": false,
    "customer": "Nexus Software Corp",
    "headline": "3x deployment velocity",
    "impl_weeks": 8,
    "industry": "Technology",
    "results": "3x deployment velocity, 99.95% uptime",
    "size": "2,400 employees"
  },
  {
    "contact_ready": true,
    "customer": "Atlantic Credit Union",
    "headline": "Sub-30ms latency",
    "impl_weeks": 16,
    "industry": "Financial Services",
    "results": "Sub-30ms latency, zero audit findings",
    "size": "120 branches"
  },
  {
    "contact_ready": true,
    "customer": "Sentinel Insurance",
    "headline": "PCI-DSS compliant in 90 days",
    "impl_weeks": 14,
    "industry": "Financial Services",
    "results": "PCI-DSS compliant in 90 days, 22% ops savings",
    "size": "$4B AUM"
  },
  {
    "contact_ready": false,
    "customer": "Vanguard Logistics",
    "headline": "18% throughput improvement",
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
    "ehr_integration": "Third-party",
    "hipaa_certified": false,
    "impl_weeks": 16,
    "pricing_position": "+5% above market",
    "strengths": [
      "Modern UI",
      "Aggressive pricing on licenses"
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
    "Native Epic integration eliminates middleware costs",
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

## Exact dataset `_CAPABILITY_FIT`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "evidence": "Native Epic & Cerner connectors, certified",
    "keyword": "ehr",
    "score": 95
  },
  {
    "evidence": "SOC 2 Type II + HIPAA certified",
    "keyword": "hipaa",
    "score": 100
  },
  {
    "evidence": "24/7/365 with 15-min response SLA",
    "keyword": "24/7",
    "score": 98
  },
  {
    "evidence": "12-week methodology with accelerators",
    "keyword": "implementation",
    "score": 92
  },
  {
    "evidence": "Role-based curriculum with certification",
    "keyword": "training",
    "score": 92
  },
  {
    "evidence": "AWS + Azure + GCP orchestration layer",
    "keyword": "multi-cloud",
    "score": 91
  },
  {
    "evidence": "Blue-green deployment with automated rollback",
    "keyword": "zero-downtime",
    "score": 93
  },
  {
    "evidence": "SOC 2 Type II audit current",
    "keyword": "soc 2",
    "score": 100
  },
  {
    "evidence": "Structured runbook and shadowing program",
    "keyword": "knowledge transfer",
    "score": 85
  },
  {
    "evidence": "Sub-30ms processing demonstrated at Atlantic CU",
    "keyword": "real-time",
    "score": 87
  },
  {
    "evidence": "PCI-DSS Level 1 certified",
    "keyword": "pci-dss",
    "score": 100
  },
  {
    "evidence": "99.99% historical, architecture supports five-nines",
    "keyword": "99.999%",
    "score": 88
  },
  {
    "evidence": "Proven branch-by-branch methodology",
    "keyword": "phased rollout",
    "score": 92
  }
]
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

## Exact dataset `_PROPOSAL_SECTIONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "pages": 3,
    "section": "Executive Summary (personalized)"
  },
  {
    "pages": 4,
    "section": "Company Overview + Industry Expertise"
  },
  {
    "pages": 8,
    "section": "Solution Architecture + Roadmap"
  },
  {
    "pages": 5,
    "section": "12-week Implementation Plan"
  },
  {
    "pages": 4,
    "section": "Pricing + Investment Summary"
  },
  {
    "pages": 6,
    "section": "Customer References + Case Studies"
  },
  {
    "pages": 3,
    "section": "Team Bios (Industry specialists)"
  },
  {
    "pages": 5,
    "section": "Terms + Conditions"
  }
]
```

## Exact dataset `_DELIVERY_PACKAGE`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "PDF proposal",
  "12-slide exec presentation",
  "pricing spreadsheet"
]
```

## Locked cases

| Case | Operation | Locked prompt | Required evidence |
|---|---|---|---|
| PG-01 | analyze_rfp | Analyze the synthetic Meridian Healthcare RFP and show the traceable requirement checklist. | RFP Analysis; Requirements Analysis; Evidence boundary |
| PG-02 | executive_summary | Draft an executive summary for the synthetic Meridian Healthcare opportunity that reflects the buyer priorities and remains subject to review. | Executive Summary; Personalization Applied; Evidence boundary |
| PG-03 | solution_pricing | Compare the synthetic solution and pricing assumptions for Meridian Healthcare without approving a price, discount, or concession. | Solution & Pricing; Budget Analysis; Evidence boundary |
| PG-04 | references_positioning | Prepare synthetic reference and competitive positioning options for Meridian Healthcare, with availability checks before use. | References & Competitive Positioning; Win Theme; Evidence boundary |
| PG-05 | compile_proposal | Outline the synthetic Meridian Healthcare proposal package and every human review required before delivery. | Proposal Package; Required Human Review Before Delivery; Evidence boundary |
| PG-06 | delivery_summary | Summarize the synthetic Meridian Healthcare draft readiness and the decisions authorized reviewers must make next. | Delivery Summary; Human-Governed Next-Step Options; Evidence boundary |

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
