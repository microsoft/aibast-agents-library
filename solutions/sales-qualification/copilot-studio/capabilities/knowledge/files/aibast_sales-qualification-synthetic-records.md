# Sales Qualification Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/b2b_sales_stacks/sales_qualification_stack/sales_qualification_agent.py`
- Strict transcript evidence: `solutions/sales-qualification/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:32:16.965358+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_ICP` | 11 |
| `_AE_TEAM` | 5 |
| `_SLA_RULES` | 4 |
| `_LEADS` | 45 |

## Exact dataset `_ICP`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "authority_tiers": {
    "C-Level": 1.0,
    "Director": 0.7,
    "Individual": 0.3,
    "Manager": 0.5,
    "VP": 0.85
  },
  "authority_weight": 0.15,
  "budget_tiers": {
    "confirmed": 1.0,
    "exploring": 0.4,
    "planned": 0.7,
    "tbd": 0.2
  },
  "budget_weight": 0.2,
  "ideal_employees_max": 10000,
  "ideal_employees_min": 200,
  "ideal_industries": [
    "Technology",
    "Financial Services",
    "Healthcare",
    "Manufacturing",
    "SaaS"
  ],
  "ideal_tech": [
    "Salesforce",
    "AWS",
    "Snowflake",
    "Kubernetes",
    "Databricks",
    "Azure"
  ],
  "industry_weight": 0.25,
  "size_weight": 0.2,
  "tech_fit_weight": 0.2
}
```

## Exact dataset `_AE_TEAM`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "current_capacity_pct": 62,
    "max_leads": 12,
    "name": "Mike Rodriguez",
    "specialty": "Enterprise Tech",
    "territory": "West"
  },
  {
    "current_capacity_pct": 55,
    "max_leads": 14,
    "name": "Sarah Kim",
    "specialty": "Healthcare / FinServ",
    "territory": "East"
  },
  {
    "current_capacity_pct": 70,
    "max_leads": 10,
    "name": "James Chen",
    "specialty": "Manufacturing / Industrial",
    "territory": "Central"
  },
  {
    "current_capacity_pct": 48,
    "max_leads": 15,
    "name": "Lisa Park",
    "specialty": "Mid-Market SaaS",
    "territory": "West"
  },
  {
    "current_capacity_pct": 58,
    "max_leads": 12,
    "name": "David Okafor",
    "specialty": "Enterprise FinServ",
    "territory": "East"
  }
]
```

## Exact dataset `_SLA_RULES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "Disqualified": {
    "escalation": "None — routed to marketing",
    "response_hours": 0,
    "sequence": "Marketing nurture list"
  },
  "Hot": {
    "escalation": "Manager alert + Slack DM",
    "response_hours": 4,
    "sequence": "Immediate call + personalized email"
  },
  "Nurture": {
    "escalation": "Weekly digest flag",
    "response_hours": 48,
    "sequence": "3-email drip over 10 days"
  },
  "Warm": {
    "escalation": "Team channel alert",
    "response_hours": 24,
    "sequence": "Personalized email day 0, call day 1"
  }
}
```

## Exact dataset `_LEADS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "authority_level": "VP",
    "budget": "confirmed",
    "company": "TechFlow Industries",
    "contact_name": "Sarah Nguyen",
    "employees": 520,
    "engagement_signals": [
      "Visited pricing page",
      "Attended booth demo twice",
      "Downloaded whitepaper"
    ],
    "id": "L001",
    "industry": "Technology",
    "need": "Consolidate 12 data sources into unified pipeline",
    "revenue": 85000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Snowflake",
      "Kubernetes"
    ],
    "timeline": "Q1",
    "title": "VP Engineering"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Meridian Corp",
    "contact_name": "James Walker",
    "employees": 1200,
    "engagement_signals": [
      "Asked technical questions at session",
      "Requested architecture doc"
    ],
    "id": "L002",
    "industry": "Healthcare",
    "need": "Replace legacy EHR integration layer",
    "revenue": 340000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce",
      "Databricks"
    ],
    "timeline": "60 days",
    "title": "CTO"
  },
  {
    "authority_level": "Director",
    "budget": "planned",
    "company": "Apex Solutions",
    "contact_name": "Diana Reyes",
    "employees": 780,
    "engagement_signals": [
      "Competitor displacement signal",
      "Visited comparison page",
      "Booth conversation 15 min"
    ],
    "id": "L003",
    "industry": "SaaS",
    "need": "Displace incumbent vendor, contract ending Q1",
    "revenue": 120000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Kubernetes",
      "Salesforce"
    ],
    "timeline": "Q1",
    "title": "Director of IT"
  },
  {
    "authority_level": "VP",
    "budget": "tbd",
    "company": "Summit Technologies",
    "contact_name": "Robert Kim",
    "employees": 450,
    "engagement_signals": [
      "Attended keynote",
      "Visited booth"
    ],
    "id": "L004",
    "industry": "Manufacturing",
    "need": "Scale production monitoring across 8 plants",
    "revenue": 95000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "90 days",
    "title": "VP Operations"
  },
  {
    "authority_level": "Manager",
    "budget": "confirmed",
    "company": "DataCorp Analytics",
    "contact_name": "Emily Tran",
    "employees": 310,
    "engagement_signals": [
      "Downloaded ROI calculator",
      "Signed up for trial"
    ],
    "id": "L005",
    "industry": "Technology",
    "need": "Improve data pipeline efficiency by 40%",
    "revenue": 52000000,
    "source": "Trade Show",
    "tech_stack": [
      "Snowflake",
      "AWS"
    ],
    "timeline": "Q2",
    "title": "IT Manager"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Greenfield Health",
    "contact_name": "Maria Santos",
    "employees": 2800,
    "engagement_signals": [
      "Watched full webinar",
      "Booked follow-up meeting",
      "Downloaded case study"
    ],
    "id": "L006",
    "industry": "Healthcare",
    "need": "Unified patient data platform across 14 facilities",
    "revenue": 620000000,
    "source": "Webinar",
    "tech_stack": [
      "Azure",
      "Salesforce",
      "Snowflake"
    ],
    "timeline": "Q1",
    "title": "Chief Digital Officer"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Pinnacle Financial",
    "contact_name": "Kevin Okafor",
    "employees": 1800,
    "engagement_signals": [
      "Referral from existing customer",
      "Requested demo"
    ],
    "id": "L007",
    "industry": "Financial Services",
    "need": "Real-time fraud detection pipeline",
    "revenue": 450000000,
    "source": "Referral",
    "tech_stack": [
      "AWS",
      "Databricks",
      "Kubernetes"
    ],
    "timeline": "60 days",
    "title": "VP Technology"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Orion Manufacturing",
    "contact_name": "Thomas Park",
    "employees": 3200,
    "engagement_signals": [
      "Booth demo",
      "Technical deep-dive session",
      "Exchanged business cards with CEO"
    ],
    "id": "L008",
    "industry": "Manufacturing",
    "need": "IoT data ingestion for predictive maintenance",
    "revenue": 780000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Kubernetes",
      "Snowflake"
    ],
    "timeline": "Q1",
    "title": "CTO"
  },
  {
    "authority_level": "Director",
    "budget": "exploring",
    "company": "Velocity SaaS",
    "contact_name": "Rachel Green",
    "employees": 180,
    "engagement_signals": [
      "Visited booth briefly"
    ],
    "id": "L009",
    "industry": "SaaS",
    "need": "Microservices observability platform",
    "revenue": 28000000,
    "source": "Trade Show",
    "tech_stack": [
      "Kubernetes",
      "AWS"
    ],
    "timeline": "Q2",
    "title": "Director of Engineering"
  },
  {
    "authority_level": "Director",
    "budget": "planned",
    "company": "Atlas Logistics",
    "contact_name": "Brian Murphy",
    "employees": 950,
    "engagement_signals": [
      "Attended breakout session",
      "Asked about integrations"
    ],
    "id": "L010",
    "industry": "Logistics",
    "need": "Supply chain visibility dashboard",
    "revenue": 210000000,
    "source": "Trade Show",
    "tech_stack": [
      "Salesforce",
      "Azure"
    ],
    "timeline": "90 days",
    "title": "IT Director"
  },
  {
    "authority_level": "VP",
    "budget": "confirmed",
    "company": "Quantum Health Systems",
    "contact_name": "Jennifer Lee",
    "employees": 4100,
    "engagement_signals": [
      "Filled detailed form",
      "Requested pricing",
      "Downloaded compliance guide"
    ],
    "id": "L011",
    "industry": "Healthcare",
    "need": "HIPAA-compliant analytics for 200+ providers",
    "revenue": 1200000000,
    "source": "Inbound Form",
    "tech_stack": [
      "Azure",
      "Snowflake",
      "Salesforce"
    ],
    "timeline": "Q1",
    "title": "VP IT"
  },
  {
    "authority_level": "C-Level",
    "budget": "tbd",
    "company": "Sterling Partners",
    "contact_name": "Michael Chen",
    "employees": 85,
    "engagement_signals": [
      "Brief booth visit"
    ],
    "id": "L012",
    "industry": "Financial Services",
    "need": "Portfolio analytics automation",
    "revenue": 15000000,
    "source": "Trade Show",
    "tech_stack": [
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "Managing Director"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "NovaTech Solutions",
    "contact_name": "Amanda Torres",
    "employees": 650,
    "engagement_signals": [
      "Referral from board member",
      "Requested architecture review",
      "Downloaded migration guide"
    ],
    "id": "L013",
    "industry": "Technology",
    "need": "Replace custom ETL with managed platform",
    "revenue": 110000000,
    "source": "Referral",
    "tech_stack": [
      "AWS",
      "Snowflake",
      "Databricks",
      "Kubernetes"
    ],
    "timeline": "60 days",
    "title": "CTO"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Cascade Energy",
    "contact_name": "Daniel Wright",
    "employees": 1500,
    "engagement_signals": [
      "Attended demo",
      "Exchanged cards"
    ],
    "id": "L014",
    "industry": "Energy",
    "need": "SCADA data integration for grid monitoring",
    "revenue": 380000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q2",
    "title": "VP Operations"
  },
  {
    "authority_level": "Director",
    "budget": "exploring",
    "company": "BlueWave Analytics",
    "contact_name": "Samantha Hall",
    "employees": 240,
    "engagement_signals": [
      "Technical questions at booth",
      "Signed up for newsletter"
    ],
    "id": "L015",
    "industry": "SaaS",
    "need": "ML pipeline orchestration",
    "revenue": 42000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Databricks",
      "Kubernetes"
    ],
    "timeline": "Q2",
    "title": "Director Data Science"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Pacific Mutual Insurance",
    "contact_name": "Gregory Adams",
    "employees": 5200,
    "engagement_signals": [
      "1-on-1 executive meeting",
      "Requested proposal",
      "Site visit scheduled"
    ],
    "id": "L016",
    "industry": "Financial Services",
    "need": "Claims processing automation with AI/ML",
    "revenue": 2100000000,
    "source": "Executive Event",
    "tech_stack": [
      "AWS",
      "Salesforce",
      "Snowflake",
      "Databricks"
    ],
    "timeline": "Q1",
    "title": "CIO"
  },
  {
    "authority_level": "Manager",
    "budget": "tbd",
    "company": "Redstone Manufacturing",
    "contact_name": "Laura Martinez",
    "employees": 2200,
    "engagement_signals": [
      "Booth visit"
    ],
    "id": "L017",
    "industry": "Manufacturing",
    "need": "Quality control data capture across lines",
    "revenue": 540000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure"
    ],
    "timeline": "Q3",
    "title": "Plant Manager"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Horizon Biotech",
    "contact_name": "Andrew Liu",
    "employees": 380,
    "engagement_signals": [
      "Detailed booth conversation",
      "Downloaded case study",
      "Requested references"
    ],
    "id": "L018",
    "industry": "Healthcare",
    "need": "Lab data integration for clinical trials",
    "revenue": 68000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Snowflake"
    ],
    "timeline": "90 days",
    "title": "VP Technology"
  },
  {
    "authority_level": "C-Level",
    "budget": "exploring",
    "company": "Vertex Cloud",
    "contact_name": "Nicole Brown",
    "employees": 130,
    "engagement_signals": [
      "Form fill"
    ],
    "id": "L019",
    "industry": "SaaS",
    "need": "Data infrastructure for new product line",
    "revenue": 18000000,
    "source": "Inbound Form",
    "tech_stack": [
      "AWS",
      "Kubernetes"
    ],
    "timeline": "Q3",
    "title": "CEO"
  },
  {
    "authority_level": "Manager",
    "budget": "tbd",
    "company": "Continental Logistics",
    "contact_name": "Paul Wilson",
    "employees": 6800,
    "engagement_signals": [
      "Booth scan only"
    ],
    "id": "L020",
    "industry": "Logistics",
    "need": "Fleet telematics data warehousing",
    "revenue": 1800000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "IT Manager"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Nexus Health Network",
    "contact_name": "Christina Park",
    "employees": 7500,
    "engagement_signals": [
      "Executive referral",
      "Requested ROI model",
      "Reviewed case studies"
    ],
    "id": "L021",
    "industry": "Healthcare",
    "need": "Population health analytics across 30 hospitals",
    "revenue": 3200000000,
    "source": "Referral",
    "tech_stack": [
      "Azure",
      "Snowflake",
      "Salesforce",
      "Databricks"
    ],
    "timeline": "Q1",
    "title": "CMIO"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Ironclad Security",
    "contact_name": "Mark Stevens",
    "employees": 420,
    "engagement_signals": [
      "Attended technical session",
      "Downloaded architecture doc",
      "Booth demo"
    ],
    "id": "L022",
    "industry": "Technology",
    "need": "Security event log aggregation at scale",
    "revenue": 75000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Kubernetes",
      "Snowflake"
    ],
    "timeline": "60 days",
    "title": "VP Engineering"
  },
  {
    "authority_level": "VP",
    "budget": "confirmed",
    "company": "Maple Financial Group",
    "contact_name": "Karen Zhao",
    "employees": 3400,
    "engagement_signals": [
      "Executive dinner attendee",
      "Scheduled follow-up call",
      "Compliance use case discussed"
    ],
    "id": "L023",
    "industry": "Financial Services",
    "need": "Regulatory reporting data pipeline",
    "revenue": 920000000,
    "source": "Executive Event",
    "tech_stack": [
      "Salesforce",
      "Snowflake",
      "Databricks"
    ],
    "timeline": "Q1",
    "title": "SVP Operations"
  },
  {
    "authority_level": "C-Level",
    "budget": "exploring",
    "company": "Bright Horizons Edu",
    "contact_name": "Steven Miller",
    "employees": 900,
    "engagement_signals": [
      "Booth conversation",
      "Requested demo video"
    ],
    "id": "L024",
    "industry": "Education",
    "need": "Student analytics platform consolidation",
    "revenue": 145000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q2",
    "title": "CTO"
  },
  {
    "authority_level": "Director",
    "budget": "planned",
    "company": "Titan Aerospace",
    "contact_name": "Angela White",
    "employees": 2600,
    "engagement_signals": [
      "Attended breakout",
      "Asked about security compliance"
    ],
    "id": "L025",
    "industry": "Manufacturing",
    "need": "Supply chain data unification across 6 plants",
    "revenue": 680000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Salesforce",
      "Snowflake"
    ],
    "timeline": "90 days",
    "title": "Director of IT"
  },
  {
    "authority_level": "VP",
    "budget": "confirmed",
    "company": "CoreBridge Insurance",
    "contact_name": "Jason Taylor",
    "employees": 4800,
    "engagement_signals": [
      "Detailed form fill",
      "Requested customer references",
      "Downloaded ROI calculator"
    ],
    "id": "L026",
    "industry": "Financial Services",
    "need": "Actuarial data lake modernization",
    "revenue": 1500000000,
    "source": "Inbound Form",
    "tech_stack": [
      "AWS",
      "Snowflake",
      "Databricks",
      "Salesforce"
    ],
    "timeline": "60 days",
    "title": "VP Data & Analytics"
  },
  {
    "authority_level": "C-Level",
    "budget": "tbd",
    "company": "Silverline Consulting",
    "contact_name": "Tara Robinson",
    "employees": 60,
    "engagement_signals": [
      "Booth scan"
    ],
    "id": "L027",
    "industry": "Professional Services",
    "need": "Client reporting dashboard",
    "revenue": 8000000,
    "source": "Trade Show",
    "tech_stack": [
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "Partner"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Westfield Medical",
    "contact_name": "Priya Sharma",
    "employees": 1900,
    "engagement_signals": [
      "Booth demo",
      "Requested HIPAA compliance docs",
      "Technical Q&A"
    ],
    "id": "L028",
    "industry": "Healthcare",
    "need": "Clinical data warehouse for research analytics",
    "revenue": 420000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Snowflake",
      "Salesforce"
    ],
    "timeline": "Q1",
    "title": "VP Clinical Informatics"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "FusionTech Labs",
    "contact_name": "Derek Johnson",
    "employees": 290,
    "engagement_signals": [
      "Customer referral",
      "Requested migration assessment",
      "Downloaded migration guide"
    ],
    "id": "L029",
    "industry": "SaaS",
    "need": "Migrate from on-prem Hadoop to cloud-native",
    "revenue": 48000000,
    "source": "Referral",
    "tech_stack": [
      "AWS",
      "Kubernetes",
      "Databricks"
    ],
    "timeline": "60 days",
    "title": "CTO"
  },
  {
    "authority_level": "Director",
    "budget": "tbd",
    "company": "National Grid Services",
    "contact_name": "Barbara Collins",
    "employees": 8200,
    "engagement_signals": [
      "Booth conversation",
      "Exchanged cards"
    ],
    "id": "L030",
    "industry": "Energy",
    "need": "Smart meter data aggregation platform",
    "revenue": 4500000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "IT Director"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Elevate Commerce",
    "contact_name": "Ryan Mitchell",
    "employees": 350,
    "engagement_signals": [
      "Attended session",
      "Downloaded integration guide"
    ],
    "id": "L031",
    "industry": "Technology",
    "need": "Real-time inventory sync across marketplace channels",
    "revenue": 62000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Snowflake",
      "Kubernetes"
    ],
    "timeline": "90 days",
    "title": "VP Engineering"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Summit Health Partners",
    "contact_name": "Lisa Nakamura",
    "employees": 5600,
    "engagement_signals": [
      "1-on-1 exec meeting",
      "Requested business case template",
      "Reviewed 3 case studies"
    ],
    "id": "L032",
    "industry": "Healthcare",
    "need": "Enterprise analytics platform for value-based care",
    "revenue": 1600000000,
    "source": "Executive Event",
    "tech_stack": [
      "Azure",
      "Snowflake",
      "Salesforce",
      "Databricks"
    ],
    "timeline": "Q1",
    "title": "Chief Analytics Officer"
  },
  {
    "authority_level": "Director",
    "budget": "exploring",
    "company": "Pioneer Robotics",
    "contact_name": "Alex Petrov",
    "employees": 410,
    "engagement_signals": [
      "Booth demo",
      "Technical questions"
    ],
    "id": "L033",
    "industry": "Manufacturing",
    "need": "Robotics telemetry data pipeline",
    "revenue": 88000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Kubernetes"
    ],
    "timeline": "Q2",
    "title": "Director of Automation"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Heritage Bank",
    "contact_name": "Sandra Lee",
    "employees": 2100,
    "engagement_signals": [
      "Detailed booth conversation",
      "Requested compliance references"
    ],
    "id": "L034",
    "industry": "Financial Services",
    "need": "Anti-money laundering data pipeline modernization",
    "revenue": 580000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Salesforce",
      "Snowflake"
    ],
    "timeline": "60 days",
    "title": "SVP Technology"
  },
  {
    "authority_level": "Manager",
    "budget": "tbd",
    "company": "ClearView Optics",
    "contact_name": "Nathan Ford",
    "employees": 160,
    "engagement_signals": [
      "Booth scan only"
    ],
    "id": "L035",
    "industry": "Manufacturing",
    "need": "Quality inspection image data storage",
    "revenue": 22000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure"
    ],
    "timeline": "Q3",
    "title": "IT Manager"
  },
  {
    "authority_level": "C-Level",
    "budget": "exploring",
    "company": "Axiom Data Systems",
    "contact_name": "Michelle Yang",
    "employees": 95,
    "engagement_signals": [
      "Brief booth stop"
    ],
    "id": "L036",
    "industry": "SaaS",
    "need": "Data pipeline as a service offering",
    "revenue": 12000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS"
    ],
    "timeline": "Q3",
    "title": "CEO"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Metro Health Alliance",
    "contact_name": "David Nguyen",
    "employees": 3800,
    "engagement_signals": [
      "Webinar attendee",
      "Downloaded guide",
      "Requested pricing"
    ],
    "id": "L037",
    "industry": "Healthcare",
    "need": "Real-time patient flow analytics for 18 facilities",
    "revenue": 890000000,
    "source": "Webinar",
    "tech_stack": [
      "Azure",
      "Snowflake",
      "Salesforce"
    ],
    "timeline": "90 days",
    "title": "VP Data Engineering"
  },
  {
    "authority_level": "C-Level",
    "budget": "planned",
    "company": "Vanguard Logistics",
    "contact_name": "Carlos Mendez",
    "employees": 1400,
    "engagement_signals": [
      "Attended demo",
      "Booth conversation"
    ],
    "id": "L038",
    "industry": "Logistics",
    "need": "Cross-border shipment tracking data platform",
    "revenue": 320000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Salesforce"
    ],
    "timeline": "Q2",
    "title": "CTO"
  },
  {
    "authority_level": "VP",
    "budget": "tbd",
    "company": "TrueNorth Energy",
    "contact_name": "Helen Foster",
    "employees": 2900,
    "engagement_signals": [
      "Keynote attendee",
      "Brief booth visit"
    ],
    "id": "L039",
    "industry": "Energy",
    "need": "Renewable energy asset performance analytics",
    "revenue": 750000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "VP Technology"
  },
  {
    "authority_level": "Director",
    "budget": "exploring",
    "company": "Paragon Pharma",
    "contact_name": "William Chang",
    "employees": 1100,
    "engagement_signals": [
      "Technical session attendee",
      "Downloaded whitepaper"
    ],
    "id": "L040",
    "industry": "Healthcare",
    "need": "Genomics data pipeline for drug discovery",
    "revenue": 290000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Databricks"
    ],
    "timeline": "Q2",
    "title": "Director of R&D IT"
  },
  {
    "authority_level": "C-Level",
    "budget": "confirmed",
    "company": "Crestline Financial",
    "contact_name": "Patricia Adams",
    "employees": 6200,
    "engagement_signals": [
      "Board-level referral",
      "Requested executive briefing",
      "Scheduled site visit"
    ],
    "id": "L041",
    "industry": "Financial Services",
    "need": "Enterprise data mesh architecture implementation",
    "revenue": 2800000000,
    "source": "Referral",
    "tech_stack": [
      "AWS",
      "Snowflake",
      "Databricks",
      "Kubernetes",
      "Salesforce"
    ],
    "timeline": "Q1",
    "title": "Chief Data Officer"
  },
  {
    "authority_level": "Manager",
    "budget": "tbd",
    "company": "Bridgepoint Retail",
    "contact_name": "Scott Thompson",
    "employees": 720,
    "engagement_signals": [
      "Booth scan"
    ],
    "id": "L042",
    "industry": "Retail",
    "need": "POS data aggregation for analytics",
    "revenue": 165000000,
    "source": "Trade Show",
    "tech_stack": [
      "Salesforce"
    ],
    "timeline": "Q3",
    "title": "IT Manager"
  },
  {
    "authority_level": "VP",
    "budget": "planned",
    "company": "Sapphire Biomedical",
    "contact_name": "Rebecca Foster",
    "employees": 480,
    "engagement_signals": [
      "Booth demo",
      "Requested case study",
      "Technical Q&A"
    ],
    "id": "L043",
    "industry": "Healthcare",
    "need": "Clinical trial data harmonization",
    "revenue": 76000000,
    "source": "Trade Show",
    "tech_stack": [
      "AWS",
      "Snowflake"
    ],
    "timeline": "90 days",
    "title": "VP Informatics"
  },
  {
    "authority_level": "Director",
    "budget": "exploring",
    "company": "Forge Industrial",
    "contact_name": "Christopher Hall",
    "employees": 3500,
    "engagement_signals": [
      "Attended session",
      "Brief booth visit"
    ],
    "id": "L044",
    "industry": "Manufacturing",
    "need": "Predictive maintenance data platform",
    "revenue": 920000000,
    "source": "Trade Show",
    "tech_stack": [
      "Azure",
      "Salesforce"
    ],
    "timeline": "Q2",
    "title": "Plant Director"
  },
  {
    "authority_level": "VP",
    "budget": "exploring",
    "company": "Luminary Wealth",
    "contact_name": "Jessica Wang",
    "employees": 250,
    "engagement_signals": [
      "Booth conversation"
    ],
    "id": "L045",
    "industry": "Financial Services",
    "need": "Client portfolio reporting automation",
    "revenue": 38000000,
    "source": "Trade Show",
    "tech_stack": [
      "Salesforce",
      "AWS"
    ],
    "timeline": "Q3",
    "title": "VP Technology"
  }
]
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
