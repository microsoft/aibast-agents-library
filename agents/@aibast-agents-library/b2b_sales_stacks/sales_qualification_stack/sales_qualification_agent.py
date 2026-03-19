"""
Sales Qualification Agent

Scores inbound leads against an Ideal Customer Profile, performs BANT
analysis, generates personalized outreach, routes leads to AEs by
territory and expertise, and enforces SLA-based follow-up tracking.

Where a real deployment would call Salesforce, ZoomInfo, 6sense, etc.,
this agent uses a synthetic data layer so it runs anywhere without
credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/sales-qualification",
    "version": "1.0.0",
    "display_name": "Sales Qualification",
    "description": "ICP scoring, BANT analysis, personalized outreach, AE routing, and SLA tracking for inbound leads.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "lead-qualification", "bant", "icp-scoring", "lead-routing"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# Stands in for CRM, ZoomInfo, 6sense, Clearbit, etc.
# ═══════════════════════════════════════════════════════════════

_ICP = {
    "size_weight": 0.20,
    "industry_weight": 0.25,
    "tech_fit_weight": 0.20,
    "budget_weight": 0.20,
    "authority_weight": 0.15,
    "ideal_employees_min": 200,
    "ideal_employees_max": 10000,
    "ideal_industries": ["Technology", "Financial Services", "Healthcare", "Manufacturing", "SaaS"],
    "ideal_tech": ["Salesforce", "AWS", "Snowflake", "Kubernetes", "Databricks", "Azure"],
    "budget_tiers": {"confirmed": 1.0, "planned": 0.7, "exploring": 0.4, "tbd": 0.2},
    "authority_tiers": {"C-Level": 1.0, "VP": 0.85, "Director": 0.7, "Manager": 0.5, "Individual": 0.3},
}

_AE_TEAM = [
    {"name": "Mike Rodriguez", "territory": "West", "specialty": "Enterprise Tech", "current_capacity_pct": 62, "max_leads": 12},
    {"name": "Sarah Kim", "territory": "East", "specialty": "Healthcare / FinServ", "current_capacity_pct": 55, "max_leads": 14},
    {"name": "James Chen", "territory": "Central", "specialty": "Manufacturing / Industrial", "current_capacity_pct": 70, "max_leads": 10},
    {"name": "Lisa Park", "territory": "West", "specialty": "Mid-Market SaaS", "current_capacity_pct": 48, "max_leads": 15},
    {"name": "David Okafor", "territory": "East", "specialty": "Enterprise FinServ", "current_capacity_pct": 58, "max_leads": 12},
]

_SLA_RULES = {
    "Hot":          {"response_hours": 4,  "escalation": "Manager alert + Slack DM",     "sequence": "Immediate call + personalized email"},
    "Warm":         {"response_hours": 24, "escalation": "Team channel alert",            "sequence": "Personalized email day 0, call day 1"},
    "Nurture":      {"response_hours": 48, "escalation": "Weekly digest flag",            "sequence": "3-email drip over 10 days"},
    "Disqualified": {"response_hours": 0,  "escalation": "None — routed to marketing",   "sequence": "Marketing nurture list"},
}

_LEADS = [
    {"id": "L001", "company": "TechFlow Industries",    "contact_name": "Sarah Nguyen",    "title": "VP Engineering",        "employees": 520,  "industry": "Technology",          "revenue": 85_000_000,   "source": "Trade Show",     "budget": "confirmed", "authority_level": "VP",        "need": "Consolidate 12 data sources into unified pipeline",              "timeline": "Q1",    "engagement_signals": ["Visited pricing page", "Attended booth demo twice", "Downloaded whitepaper"],                  "tech_stack": ["AWS", "Snowflake", "Kubernetes"]},
    {"id": "L002", "company": "Meridian Corp",          "contact_name": "James Walker",    "title": "CTO",                   "employees": 1200, "industry": "Healthcare",          "revenue": 340_000_000,  "source": "Trade Show",     "budget": "confirmed", "authority_level": "C-Level",   "need": "Replace legacy EHR integration layer",                          "timeline": "60 days", "engagement_signals": ["Asked technical questions at session", "Requested architecture doc"],                          "tech_stack": ["Azure", "Salesforce", "Databricks"]},
    {"id": "L003", "company": "Apex Solutions",         "contact_name": "Diana Reyes",     "title": "Director of IT",        "employees": 780,  "industry": "SaaS",                "revenue": 120_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "Director",  "need": "Displace incumbent vendor, contract ending Q1",                  "timeline": "Q1",    "engagement_signals": ["Competitor displacement signal", "Visited comparison page", "Booth conversation 15 min"],       "tech_stack": ["AWS", "Kubernetes", "Salesforce"]},
    {"id": "L004", "company": "Summit Technologies",    "contact_name": "Robert Kim",      "title": "VP Operations",         "employees": 450,  "industry": "Manufacturing",       "revenue": 95_000_000,   "source": "Trade Show",     "budget": "tbd",       "authority_level": "VP",        "need": "Scale production monitoring across 8 plants",                    "timeline": "90 days", "engagement_signals": ["Attended keynote", "Visited booth"],                                                           "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L005", "company": "DataCorp Analytics",     "contact_name": "Emily Tran",      "title": "IT Manager",            "employees": 310,  "industry": "Technology",          "revenue": 52_000_000,   "source": "Trade Show",     "budget": "confirmed", "authority_level": "Manager",   "need": "Improve data pipeline efficiency by 40%",                        "timeline": "Q2",    "engagement_signals": ["Downloaded ROI calculator", "Signed up for trial"],                                            "tech_stack": ["Snowflake", "AWS"]},
    {"id": "L006", "company": "Greenfield Health",      "contact_name": "Maria Santos",    "title": "Chief Digital Officer",  "employees": 2800, "industry": "Healthcare",          "revenue": 620_000_000,  "source": "Webinar",        "budget": "confirmed", "authority_level": "C-Level",   "need": "Unified patient data platform across 14 facilities",             "timeline": "Q1",    "engagement_signals": ["Watched full webinar", "Booked follow-up meeting", "Downloaded case study"],                   "tech_stack": ["Azure", "Salesforce", "Snowflake"]},
    {"id": "L007", "company": "Pinnacle Financial",     "contact_name": "Kevin Okafor",    "title": "VP Technology",         "employees": 1800, "industry": "Financial Services",  "revenue": 450_000_000,  "source": "Referral",       "budget": "planned",   "authority_level": "VP",        "need": "Real-time fraud detection pipeline",                             "timeline": "60 days", "engagement_signals": ["Referral from existing customer", "Requested demo"],                                           "tech_stack": ["AWS", "Databricks", "Kubernetes"]},
    {"id": "L008", "company": "Orion Manufacturing",    "contact_name": "Thomas Park",     "title": "CTO",                   "employees": 3200, "industry": "Manufacturing",       "revenue": 780_000_000,  "source": "Trade Show",     "budget": "confirmed", "authority_level": "C-Level",   "need": "IoT data ingestion for predictive maintenance",                  "timeline": "Q1",    "engagement_signals": ["Booth demo", "Technical deep-dive session", "Exchanged business cards with CEO"],              "tech_stack": ["AWS", "Kubernetes", "Snowflake"]},
    {"id": "L009", "company": "Velocity SaaS",          "contact_name": "Rachel Green",    "title": "Director of Engineering","employees": 180,  "industry": "SaaS",                "revenue": 28_000_000,   "source": "Trade Show",     "budget": "exploring", "authority_level": "Director",  "need": "Microservices observability platform",                           "timeline": "Q2",    "engagement_signals": ["Visited booth briefly"],                                                                       "tech_stack": ["Kubernetes", "AWS"]},
    {"id": "L010", "company": "Atlas Logistics",        "contact_name": "Brian Murphy",    "title": "IT Director",           "employees": 950,  "industry": "Logistics",           "revenue": 210_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "Director",  "need": "Supply chain visibility dashboard",                              "timeline": "90 days", "engagement_signals": ["Attended breakout session", "Asked about integrations"],                                        "tech_stack": ["Salesforce", "Azure"]},
    {"id": "L011", "company": "Quantum Health Systems", "contact_name": "Jennifer Lee",    "title": "VP IT",                 "employees": 4100, "industry": "Healthcare",          "revenue": 1_200_000_000,"source": "Inbound Form",   "budget": "confirmed", "authority_level": "VP",        "need": "HIPAA-compliant analytics for 200+ providers",                   "timeline": "Q1",    "engagement_signals": ["Filled detailed form", "Requested pricing", "Downloaded compliance guide"],                    "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L012", "company": "Sterling Partners",      "contact_name": "Michael Chen",    "title": "Managing Director",     "employees": 85,   "industry": "Financial Services",  "revenue": 15_000_000,   "source": "Trade Show",     "budget": "tbd",       "authority_level": "C-Level",   "need": "Portfolio analytics automation",                                 "timeline": "Q3",    "engagement_signals": ["Brief booth visit"],                                                                           "tech_stack": ["Salesforce"]},
    {"id": "L013", "company": "NovaTech Solutions",     "contact_name": "Amanda Torres",   "title": "CTO",                   "employees": 650,  "industry": "Technology",          "revenue": 110_000_000,  "source": "Referral",       "budget": "confirmed", "authority_level": "C-Level",   "need": "Replace custom ETL with managed platform",                       "timeline": "60 days", "engagement_signals": ["Referral from board member", "Requested architecture review", "Downloaded migration guide"],     "tech_stack": ["AWS", "Snowflake", "Databricks", "Kubernetes"]},
    {"id": "L014", "company": "Cascade Energy",         "contact_name": "Daniel Wright",   "title": "VP Operations",         "employees": 1500, "industry": "Energy",              "revenue": 380_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "SCADA data integration for grid monitoring",                     "timeline": "Q2",    "engagement_signals": ["Attended demo", "Exchanged cards"],                                                            "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L015", "company": "BlueWave Analytics",     "contact_name": "Samantha Hall",   "title": "Director Data Science",  "employees": 240,  "industry": "SaaS",                "revenue": 42_000_000,   "source": "Trade Show",     "budget": "exploring", "authority_level": "Director",  "need": "ML pipeline orchestration",                                      "timeline": "Q2",    "engagement_signals": ["Technical questions at booth", "Signed up for newsletter"],                                     "tech_stack": ["AWS", "Databricks", "Kubernetes"]},
    {"id": "L016", "company": "Pacific Mutual Insurance","contact_name": "Gregory Adams",  "title": "CIO",                   "employees": 5200, "industry": "Financial Services",  "revenue": 2_100_000_000,"source": "Executive Event","budget": "confirmed", "authority_level": "C-Level",   "need": "Claims processing automation with AI/ML",                        "timeline": "Q1",    "engagement_signals": ["1-on-1 executive meeting", "Requested proposal", "Site visit scheduled"],                       "tech_stack": ["AWS", "Salesforce", "Snowflake", "Databricks"]},
    {"id": "L017", "company": "Redstone Manufacturing", "contact_name": "Laura Martinez",  "title": "Plant Manager",         "employees": 2200, "industry": "Manufacturing",       "revenue": 540_000_000,  "source": "Trade Show",     "budget": "tbd",       "authority_level": "Manager",   "need": "Quality control data capture across lines",                      "timeline": "Q3",    "engagement_signals": ["Booth visit"],                                                                                 "tech_stack": ["Azure"]},
    {"id": "L018", "company": "Horizon Biotech",        "contact_name": "Andrew Liu",      "title": "VP Technology",         "employees": 380,  "industry": "Healthcare",          "revenue": 68_000_000,   "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Lab data integration for clinical trials",                       "timeline": "90 days", "engagement_signals": ["Detailed booth conversation", "Downloaded case study", "Requested references"],                 "tech_stack": ["AWS", "Snowflake"]},
    {"id": "L019", "company": "Vertex Cloud",           "contact_name": "Nicole Brown",    "title": "CEO",                   "employees": 130,  "industry": "SaaS",                "revenue": 18_000_000,   "source": "Inbound Form",   "budget": "exploring", "authority_level": "C-Level",   "need": "Data infrastructure for new product line",                       "timeline": "Q3",    "engagement_signals": ["Form fill"],                                                                                   "tech_stack": ["AWS", "Kubernetes"]},
    {"id": "L020", "company": "Continental Logistics",  "contact_name": "Paul Wilson",     "title": "IT Manager",            "employees": 6800, "industry": "Logistics",           "revenue": 1_800_000_000,"source": "Trade Show",     "budget": "tbd",       "authority_level": "Manager",   "need": "Fleet telematics data warehousing",                              "timeline": "Q3",    "engagement_signals": ["Booth scan only"],                                                                             "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L021", "company": "Nexus Health Network",   "contact_name": "Christina Park",  "title": "CMIO",                  "employees": 7500, "industry": "Healthcare",          "revenue": 3_200_000_000,"source": "Referral",       "budget": "confirmed", "authority_level": "C-Level",   "need": "Population health analytics across 30 hospitals",                "timeline": "Q1",    "engagement_signals": ["Executive referral", "Requested ROI model", "Reviewed case studies"],                           "tech_stack": ["Azure", "Snowflake", "Salesforce", "Databricks"]},
    {"id": "L022", "company": "Ironclad Security",      "contact_name": "Mark Stevens",    "title": "VP Engineering",        "employees": 420,  "industry": "Technology",          "revenue": 75_000_000,   "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Security event log aggregation at scale",                        "timeline": "60 days", "engagement_signals": ["Attended technical session", "Downloaded architecture doc", "Booth demo"],                      "tech_stack": ["AWS", "Kubernetes", "Snowflake"]},
    {"id": "L023", "company": "Maple Financial Group",  "contact_name": "Karen Zhao",      "title": "SVP Operations",        "employees": 3400, "industry": "Financial Services",  "revenue": 920_000_000,  "source": "Executive Event","budget": "confirmed", "authority_level": "VP",        "need": "Regulatory reporting data pipeline",                             "timeline": "Q1",    "engagement_signals": ["Executive dinner attendee", "Scheduled follow-up call", "Compliance use case discussed"],       "tech_stack": ["Salesforce", "Snowflake", "Databricks"]},
    {"id": "L024", "company": "Bright Horizons Edu",    "contact_name": "Steven Miller",   "title": "CTO",                   "employees": 900,  "industry": "Education",           "revenue": 145_000_000,  "source": "Trade Show",     "budget": "exploring", "authority_level": "C-Level",   "need": "Student analytics platform consolidation",                       "timeline": "Q2",    "engagement_signals": ["Booth conversation", "Requested demo video"],                                                  "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L025", "company": "Titan Aerospace",        "contact_name": "Angela White",    "title": "Director of IT",        "employees": 2600, "industry": "Manufacturing",       "revenue": 680_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "Director",  "need": "Supply chain data unification across 6 plants",                  "timeline": "90 days", "engagement_signals": ["Attended breakout", "Asked about security compliance"],                                         "tech_stack": ["AWS", "Salesforce", "Snowflake"]},
    {"id": "L026", "company": "CoreBridge Insurance",   "contact_name": "Jason Taylor",    "title": "VP Data & Analytics",   "employees": 4800, "industry": "Financial Services",  "revenue": 1_500_000_000,"source": "Inbound Form",   "budget": "confirmed", "authority_level": "VP",        "need": "Actuarial data lake modernization",                              "timeline": "60 days", "engagement_signals": ["Detailed form fill", "Requested customer references", "Downloaded ROI calculator"],             "tech_stack": ["AWS", "Snowflake", "Databricks", "Salesforce"]},
    {"id": "L027", "company": "Silverline Consulting",  "contact_name": "Tara Robinson",   "title": "Partner",               "employees": 60,   "industry": "Professional Services","revenue": 8_000_000,  "source": "Trade Show",     "budget": "tbd",       "authority_level": "C-Level",   "need": "Client reporting dashboard",                                     "timeline": "Q3",    "engagement_signals": ["Booth scan"],                                                                                  "tech_stack": ["Salesforce"]},
    {"id": "L028", "company": "Westfield Medical",      "contact_name": "Priya Sharma",    "title": "VP Clinical Informatics","employees": 1900, "industry": "Healthcare",          "revenue": 420_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Clinical data warehouse for research analytics",                 "timeline": "Q1",    "engagement_signals": ["Booth demo", "Requested HIPAA compliance docs", "Technical Q&A"],                               "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L029", "company": "FusionTech Labs",        "contact_name": "Derek Johnson",   "title": "CTO",                   "employees": 290,  "industry": "SaaS",                "revenue": 48_000_000,   "source": "Referral",       "budget": "confirmed", "authority_level": "C-Level",   "need": "Migrate from on-prem Hadoop to cloud-native",                    "timeline": "60 days", "engagement_signals": ["Customer referral", "Requested migration assessment", "Downloaded migration guide"],             "tech_stack": ["AWS", "Kubernetes", "Databricks"]},
    {"id": "L030", "company": "National Grid Services", "contact_name": "Barbara Collins", "title": "IT Director",           "employees": 8200, "industry": "Energy",              "revenue": 4_500_000_000,"source": "Trade Show",     "budget": "tbd",       "authority_level": "Director",  "need": "Smart meter data aggregation platform",                          "timeline": "Q3",    "engagement_signals": ["Booth conversation", "Exchanged cards"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L031", "company": "Elevate Commerce",       "contact_name": "Ryan Mitchell",   "title": "VP Engineering",        "employees": 350,  "industry": "Technology",          "revenue": 62_000_000,   "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Real-time inventory sync across marketplace channels",           "timeline": "90 days", "engagement_signals": ["Attended session", "Downloaded integration guide"],                                             "tech_stack": ["AWS", "Snowflake", "Kubernetes"]},
    {"id": "L032", "company": "Summit Health Partners", "contact_name": "Lisa Nakamura",   "title": "Chief Analytics Officer","employees": 5600, "industry": "Healthcare",          "revenue": 1_600_000_000,"source": "Executive Event","budget": "confirmed", "authority_level": "C-Level",   "need": "Enterprise analytics platform for value-based care",             "timeline": "Q1",    "engagement_signals": ["1-on-1 exec meeting", "Requested business case template", "Reviewed 3 case studies"],           "tech_stack": ["Azure", "Snowflake", "Salesforce", "Databricks"]},
    {"id": "L033", "company": "Pioneer Robotics",       "contact_name": "Alex Petrov",     "title": "Director of Automation", "employees": 410,  "industry": "Manufacturing",       "revenue": 88_000_000,   "source": "Trade Show",     "budget": "exploring", "authority_level": "Director",  "need": "Robotics telemetry data pipeline",                               "timeline": "Q2",    "engagement_signals": ["Booth demo", "Technical questions"],                                                           "tech_stack": ["AWS", "Kubernetes"]},
    {"id": "L034", "company": "Heritage Bank",          "contact_name": "Sandra Lee",      "title": "SVP Technology",        "employees": 2100, "industry": "Financial Services",  "revenue": 580_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Anti-money laundering data pipeline modernization",              "timeline": "60 days", "engagement_signals": ["Detailed booth conversation", "Requested compliance references"],                               "tech_stack": ["AWS", "Salesforce", "Snowflake"]},
    {"id": "L035", "company": "ClearView Optics",       "contact_name": "Nathan Ford",     "title": "IT Manager",            "employees": 160,  "industry": "Manufacturing",       "revenue": 22_000_000,   "source": "Trade Show",     "budget": "tbd",       "authority_level": "Manager",   "need": "Quality inspection image data storage",                          "timeline": "Q3",    "engagement_signals": ["Booth scan only"],                                                                             "tech_stack": ["Azure"]},
    {"id": "L036", "company": "Axiom Data Systems",     "contact_name": "Michelle Yang",   "title": "CEO",                   "employees": 95,   "industry": "SaaS",                "revenue": 12_000_000,   "source": "Trade Show",     "budget": "exploring", "authority_level": "C-Level",   "need": "Data pipeline as a service offering",                            "timeline": "Q3",    "engagement_signals": ["Brief booth stop"],                                                                            "tech_stack": ["AWS"]},
    {"id": "L037", "company": "Metro Health Alliance",  "contact_name": "David Nguyen",    "title": "VP Data Engineering",   "employees": 3800, "industry": "Healthcare",          "revenue": 890_000_000,  "source": "Webinar",        "budget": "planned",   "authority_level": "VP",        "need": "Real-time patient flow analytics for 18 facilities",             "timeline": "90 days", "engagement_signals": ["Webinar attendee", "Downloaded guide", "Requested pricing"],                                    "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L038", "company": "Vanguard Logistics",     "contact_name": "Carlos Mendez",   "title": "CTO",                   "employees": 1400, "industry": "Logistics",           "revenue": 320_000_000,  "source": "Trade Show",     "budget": "planned",   "authority_level": "C-Level",   "need": "Cross-border shipment tracking data platform",                   "timeline": "Q2",    "engagement_signals": ["Attended demo", "Booth conversation"],                                                         "tech_stack": ["AWS", "Salesforce"]},
    {"id": "L039", "company": "TrueNorth Energy",       "contact_name": "Helen Foster",    "title": "VP Technology",         "employees": 2900, "industry": "Energy",              "revenue": 750_000_000,  "source": "Trade Show",     "budget": "tbd",       "authority_level": "VP",        "need": "Renewable energy asset performance analytics",                   "timeline": "Q3",    "engagement_signals": ["Keynote attendee", "Brief booth visit"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L040", "company": "Paragon Pharma",         "contact_name": "William Chang",   "title": "Director of R&D IT",    "employees": 1100, "industry": "Healthcare",          "revenue": 290_000_000,  "source": "Trade Show",     "budget": "exploring", "authority_level": "Director",  "need": "Genomics data pipeline for drug discovery",                      "timeline": "Q2",    "engagement_signals": ["Technical session attendee", "Downloaded whitepaper"],                                          "tech_stack": ["AWS", "Databricks"]},
    {"id": "L041", "company": "Crestline Financial",    "contact_name": "Patricia Adams",  "title": "Chief Data Officer",    "employees": 6200, "industry": "Financial Services",  "revenue": 2_800_000_000,"source": "Referral",       "budget": "confirmed", "authority_level": "C-Level",   "need": "Enterprise data mesh architecture implementation",               "timeline": "Q1",    "engagement_signals": ["Board-level referral", "Requested executive briefing", "Scheduled site visit"],                 "tech_stack": ["AWS", "Snowflake", "Databricks", "Kubernetes", "Salesforce"]},
    {"id": "L042", "company": "Bridgepoint Retail",     "contact_name": "Scott Thompson",  "title": "IT Manager",            "employees": 720,  "industry": "Retail",              "revenue": 165_000_000,  "source": "Trade Show",     "budget": "tbd",       "authority_level": "Manager",   "need": "POS data aggregation for analytics",                             "timeline": "Q3",    "engagement_signals": ["Booth scan"],                                                                                  "tech_stack": ["Salesforce"]},
    {"id": "L043", "company": "Sapphire Biomedical",    "contact_name": "Rebecca Foster",  "title": "VP Informatics",        "employees": 480,  "industry": "Healthcare",          "revenue": 76_000_000,   "source": "Trade Show",     "budget": "planned",   "authority_level": "VP",        "need": "Clinical trial data harmonization",                              "timeline": "90 days", "engagement_signals": ["Booth demo", "Requested case study", "Technical Q&A"],                                          "tech_stack": ["AWS", "Snowflake"]},
    {"id": "L044", "company": "Forge Industrial",       "contact_name": "Christopher Hall","title": "Plant Director",         "employees": 3500, "industry": "Manufacturing",       "revenue": 920_000_000,  "source": "Trade Show",     "budget": "exploring", "authority_level": "Director",  "need": "Predictive maintenance data platform",                           "timeline": "Q2",    "engagement_signals": ["Attended session", "Brief booth visit"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L045", "company": "Luminary Wealth",        "contact_name": "Jessica Wang",    "title": "VP Technology",         "employees": 250,  "industry": "Financial Services",  "revenue": 38_000_000,   "source": "Trade Show",     "budget": "exploring", "authority_level": "VP",        "need": "Client portfolio reporting automation",                          "timeline": "Q3",    "engagement_signals": ["Booth conversation"],                                                                          "tech_stack": ["Salesforce", "AWS"]},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS — real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _icp_score(lead):
    """Compute ICP fit score (0-100) from weighted criteria."""
    # Size score
    emp = lead["employees"]
    if _ICP["ideal_employees_min"] <= emp <= _ICP["ideal_employees_max"]:
        size_score = 100
    elif emp < _ICP["ideal_employees_min"]:
        size_score = max(10, int((emp / _ICP["ideal_employees_min"]) * 100))
    else:
        size_score = max(40, 100 - int((emp - _ICP["ideal_employees_max"]) / 200))

    # Industry score
    industry_score = 100 if lead["industry"] in _ICP["ideal_industries"] else 30

    # Tech fit score
    overlap = len(set(lead["tech_stack"]) & set(_ICP["ideal_tech"]))
    tech_score = min(100, int((overlap / max(len(_ICP["ideal_tech"]), 1)) * 150))

    # Budget score
    budget_score = int(_ICP["budget_tiers"].get(lead["budget"], 0.2) * 100)

    # Authority score
    authority_score = int(_ICP["authority_tiers"].get(lead["authority_level"], 0.3) * 100)

    total = (
        size_score * _ICP["size_weight"]
        + industry_score * _ICP["industry_weight"]
        + tech_score * _ICP["tech_fit_weight"]
        + budget_score * _ICP["budget_weight"]
        + authority_score * _ICP["authority_weight"]
    )
    return min(100, max(0, int(total)))


def _bant_scores(lead):
    """Score each BANT dimension independently (0-100)."""
    budget_map = {"confirmed": 95, "planned": 70, "exploring": 40, "tbd": 15}
    b = budget_map.get(lead["budget"], 15)

    authority_map = {"C-Level": 95, "VP": 80, "Director": 60, "Manager": 40, "Individual": 20}
    a = authority_map.get(lead["authority_level"], 20)

    n = min(100, 50 + len(lead["need"]) // 3 + len(lead["engagement_signals"]) * 8)

    timeline_val = lead["timeline"].upper()
    if "60" in timeline_val or "Q1" in timeline_val:
        t = 90
    elif "90" in timeline_val:
        t = 70
    elif "Q2" in timeline_val:
        t = 55
    else:
        t = 25

    composite = int(b * 0.30 + a * 0.25 + n * 0.25 + t * 0.20)
    return {"budget": b, "authority": a, "need": n, "timeline": t, "composite": composite}


def _tier_lead(icp_score, bant_composite):
    """Assign tier from combined ICP and BANT scores."""
    combined = int(icp_score * 0.55 + bant_composite * 0.45)
    if combined >= 88:
        return "Hot", combined
    elif combined >= 73:
        return "Warm", combined
    elif combined >= 55:
        return "Nurture", combined
    else:
        return "Disqualified", combined


def _match_ae(lead, team):
    """Route lead to best AE by specialty keyword match and capacity."""
    industry = lead["industry"].lower()
    best_ae = None
    best_score = -1
    for ae in team:
        spec = ae["specialty"].lower()
        score = 0
        if industry in spec:
            score += 50
        if "enterprise" in spec and lead["employees"] >= 1000:
            score += 20
        elif "mid-market" in spec and lead["employees"] < 1000:
            score += 20
        if "finserv" in spec and "financial" in industry:
            score += 30
        if "tech" in spec and industry in ("technology", "saas"):
            score += 25
        if "health" in spec and "healthcare" in industry:
            score += 30
        if "manufactur" in spec and "manufacturing" in industry:
            score += 30
        capacity_bonus = max(0, (100 - ae["current_capacity_pct"]) // 5)
        score += capacity_bonus
        if score > best_score:
            best_score = score
            best_ae = ae
    return best_ae


def _generate_outreach(lead, tier, icp_score):
    """Build personalized outreach elements from lead context."""
    company = lead["company"]
    first_name = lead["contact_name"].split()[0]
    need_short = lead["need"][:60]

    if tier == "Hot":
        subject = f"Following up on our {lead['source'].lower()} conversation, {first_name}"
        hook = f'You mentioned "{need_short}" — we have a proven path to solve this in {lead["timeline"]}.'
        cta = "15-minute deep dive this week?"
    elif tier == "Warm":
        subject = f"{company} + DataSync: {need_short[:40]}"
        hook = f"Teams like yours at {company} are solving {need_short.lower()} with our platform."
        cta = "Quick call to explore fit?"
    else:
        subject = f"Resource: solving {need_short[:35].lower()} at scale"
        hook = f"Thought you would find our latest guide on {lead['industry'].lower()} data challenges useful."
        cta = "Reply if you would like a walkthrough."

    return {"subject": subject, "hook": hook, "cta": cta}


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class SalesQualificationAgent(BasicAgent):
    """
    Scores, qualifies, and routes inbound leads.

    Operations:
        score_leads          - ICP scoring + tiering for all leads
        bant_analysis        - BANT breakdown for top-tier leads
        create_outreach      - Personalized email outreach per lead
        assign_leads         - Route to AEs by territory/expertise/capacity
        setup_tracking       - SLA rules and escalation configuration
        qualification_report - Full pipeline summary with conversion targets
    """

    def __init__(self):
        self.name = "SalesQualificationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "score_leads", "bant_analysis",
                            "create_outreach", "assign_leads",
                            "setup_tracking", "qualification_report",
                        ],
                        "description": "The qualification operation to perform",
                    },
                    "tier_filter": {
                        "type": "string",
                        "description": "Optional tier filter: Hot, Warm, Nurture, Disqualified",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)
        self._scored = None

    def _ensure_scored(self):
        """Lazily compute and cache scored leads."""
        if self._scored is not None:
            return self._scored
        results = []
        for lead in _LEADS:
            icp = _icp_score(lead)
            bant = _bant_scores(lead)
            tier, combined = _tier_lead(icp, bant["composite"])
            results.append({**lead, "icp_score": icp, "bant": bant, "tier": tier, "combined_score": combined})
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        self._scored = results
        return results

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "score_leads")
        dispatch = {
            "score_leads": self._score_leads,
            "bant_analysis": self._bant_analysis,
            "create_outreach": self._create_outreach,
            "assign_leads": self._assign_leads,
            "setup_tracking": self._setup_tracking,
            "qualification_report": self._qualification_report,
        }
        handler = dispatch.get(op)
        if not handler:
            return json.dumps({"status": "error", "message": f"Unknown operation: {op}"})
        return handler(kwargs.get("tier_filter"))

    # ── score_leads ───────────────────────────────────────────
    def _score_leads(self, tier_filter):
        scored = self._ensure_scored()
        tiers = {"Hot": [], "Warm": [], "Nurture": [], "Disqualified": []}
        for s in scored:
            tiers[s["tier"]].append(s)

        summary = (
            "| Tier | Leads | Avg Score | Recommended Action |\n"
            "|---|---|---|---|\n"
        )
        actions = {"Hot": "Immediate AE handoff", "Warm": "SDR qualification call",
                   "Nurture": "Automated email sequence", "Disqualified": "Marketing nurture list"}
        for tier_name in ["Hot", "Warm", "Nurture", "Disqualified"]:
            group = tiers[tier_name]
            avg = int(sum(l["combined_score"] for l in group) / max(len(group), 1))
            summary += f"| {tier_name} | {len(group)} | {avg}/100 | {actions[tier_name]} |\n"

        top_hot = tiers["Hot"][:5]
        top_lines = ""
        for i, lead in enumerate(top_hot, 1):
            top_lines += f"{i}. **{lead['company']}** — Score: {lead['combined_score']} — {lead['contact_name']}, {lead['title']}, {lead['need'][:50]}\n"

        filtered = ""
        if tier_filter and tier_filter in tiers:
            filtered = f"\n**{tier_filter} Leads Detail:**\n\n"
            filtered += "| Company | Contact | Score | Industry | Signals |\n|---|---|---|---|---|\n"
            for l in tiers[tier_filter]:
                sigs = ", ".join(l["engagement_signals"][:2])
                filtered += f"| {l['company']} | {l['contact_name']} | {l['combined_score']} | {l['industry']} | {sigs} |\n"

        return (
            f"**Lead Qualification Summary — {len(scored)} Leads Scored**\n\n"
            f"{summary}\n"
            f"**Top Hot Leads:**\n{top_lines}"
            f"{filtered}\n"
            "Source: [CRM + ZoomInfo + 6sense Intent Data]\n"
            "Agents: LeadEnrichmentAgent, ICPMatchingAgent"
        )

    # ── bant_analysis ─────────────────────────────────────────
    def _bant_analysis(self, tier_filter):
        scored = self._ensure_scored()
        hot = [s for s in scored if s["tier"] == "Hot"]
        targets = hot[:8]

        table = "| Lead | Budget | Authority | Need | Timeline | BANT Score |\n|---|---|---|---|---|---|\n"
        for lead in targets:
            b = lead["bant"]
            budget_label = f"{lead['budget'].capitalize()} ({b['budget']})"
            auth_label = f"{lead['authority_level']} ({b['authority']})"
            need_label = f"{b['need']}"
            time_label = f"{lead['timeline']} ({b['timeline']})"
            table += f"| {lead['company']} | {budget_label} | {auth_label} | {need_label} | {time_label} | {b['composite']} |\n"

        signals = "\n**Strongest Engagement Signals:**\n"
        for lead in targets[:3]:
            sigs = ", ".join(lead["engagement_signals"])
            signals += f"- **{lead['company']}**: {sigs}\n"

        risks = "\n**Risk Flags:**\n"
        for lead in targets:
            if lead["bant"]["budget"] < 50:
                risks += f"- {lead['company']}: Budget not confirmed ({lead['budget']})\n"
            if lead["bant"]["authority"] < 60:
                risks += f"- {lead['company']}: Decision maker not yet engaged ({lead['authority_level']})\n"

        return (
            f"**BANT Analysis — Top {len(targets)} Hot Leads**\n\n"
            f"{table}{signals}{risks}\n"
            "Source: [CRM + Booth Interactions + Intent Data]\n"
            "Agents: BANTScoringAgent"
        )

    # ── create_outreach ───────────────────────────────────────
    def _create_outreach(self, tier_filter):
        scored = self._ensure_scored()
        tier = tier_filter if tier_filter in ("Hot", "Warm") else "Hot"
        targets = [s for s in scored if s["tier"] == tier][:5]

        blocks = ""
        for lead in targets:
            o = _generate_outreach(lead, lead["tier"], lead["icp_score"])
            blocks += (
                f"**{lead['company']} Outreach:**\n\n"
                f"**Subject:** {o['subject']}\n\n"
                f"**Hook:** \"{o['hook']}\"\n\n"
                f"**CTA:** {o['cta']}\n\n---\n\n"
            )

        sequence = (
            "**Sequence Cadence (all leads):**\n"
            "- Day 0: Personalized email (above)\n"
            "- Day 1: LinkedIn connection + note\n"
            "- Day 2: Phone attempt #1\n"
            "- Day 3: Value content email\n"
            "- Day 5: Phone attempt #2\n"
        )

        return (
            f"**Personalized Outreach — {len(targets)} {tier} Leads**\n\n"
            f"{blocks}{sequence}\n"
            "Source: [Content Library + Booth Notes + LinkedIn]\n"
            "Agents: PersonalizedOutreachAgent"
        )

    # ── assign_leads ──────────────────────────────────────────
    def _assign_leads(self, tier_filter):
        scored = self._ensure_scored()
        actionable = [s for s in scored if s["tier"] in ("Hot", "Warm")]
        assignments = {ae["name"]: {"ae": ae, "leads": [], "value": 0} for ae in _AE_TEAM}

        for lead in actionable:
            ae = _match_ae(lead, _AE_TEAM)
            if ae:
                est_value = int(lead["revenue"] * 0.001)
                assignments[ae["name"]]["leads"].append(lead)
                assignments[ae["name"]]["value"] += est_value

        summary_table = "| AE | Leads | Est. Pipeline | Specialty Match | Capacity |\n|---|---|---|---|---|\n"
        for ae_name, data in assignments.items():
            if data["leads"]:
                summary_table += (
                    f"| {ae_name} | {len(data['leads'])} | ${data['value']:,} | "
                    f"{data['ae']['specialty']} | {data['ae']['current_capacity_pct']}% |\n"
                )

        detail = "\n**Assignment Detail:**\n"
        for ae_name, data in assignments.items():
            for lead in data["leads"][:3]:
                est_value = int(lead["revenue"] * 0.001)
                detail += f"- {lead['company']} (${est_value:,}) -> {ae_name} ({data['ae']['specialty']})\n"

        handoff = (
            "\n**Handoff Package per Lead:**\n"
            "- Lead score + BANT summary\n"
            "- Booth interaction / source notes\n"
            "- Personalized email draft\n"
            "- Recommended talk track\n"
        )

        return (
            f"**Lead Assignments — {len(actionable)} Leads Routed**\n\n"
            f"{summary_table}{detail}{handoff}\n"
            "Source: [Territory Rules + Capacity Dashboard]\n"
            "Agents: LeadRoutingAgent"
        )

    # ── setup_tracking ────────────────────────────────────────
    def _setup_tracking(self, tier_filter):
        scored = self._ensure_scored()
        tiers = {"Hot": 0, "Warm": 0, "Nurture": 0, "Disqualified": 0}
        for s in scored:
            tiers[s["tier"]] += 1

        sla_table = "| Lead Tier | Response SLA | Escalation | Sequence |\n|---|---|---|---|\n"
        for tier_name in ["Hot", "Warm", "Nurture", "Disqualified"]:
            rule = _SLA_RULES[tier_name]
            hrs = f"{rule['response_hours']}h" if rule["response_hours"] > 0 else "N/A"
            sla_table += f"| {tier_name} ({tiers[tier_name]} leads) | {hrs} | {rule['escalation']} | {rule['sequence']} |\n"

        monitoring = (
            "\n**Monitoring Activated:**\n"
            "- Real-time dashboard tracking all 45 leads\n"
            "- Slack alerts when SLA at risk (50% time elapsed)\n"
            "- Daily summary report at 9:00 AM\n"
            "- Weekly conversion tracking by tier\n"
        )

        escalation = (
            "\n**Escalation Rules:**\n"
            "- Hot lead no contact in 4h: Manager DM + email\n"
            "- Warm lead no contact in 24h: Team channel alert\n"
            "- Any lead no response after full sequence: Re-route to alternate AE\n"
            "- Meeting booked: Auto-update opportunity stage in CRM\n"
        )

        return (
            f"**SLA Tracking Configuration — {len(scored)} Leads**\n\n"
            f"{sla_table}{monitoring}{escalation}\n"
            "Source: [SLA Engine + Notification System]\n"
            "Agents: SLAMonitoringAgent"
        )

    # ── qualification_report ──────────────────────────────────
    def _qualification_report(self, tier_filter):
        scored = self._ensure_scored()
        tiers = {"Hot": [], "Warm": [], "Nurture": [], "Disqualified": []}
        for s in scored:
            tiers[s["tier"]].append(s)

        hot_value = sum(int(l["revenue"] * 0.001) for l in tiers["Hot"])
        warm_value = sum(int(l["revenue"] * 0.001) for l in tiers["Warm"])
        total_pipeline = hot_value + warm_value

        summary_table = (
            "| Metric | Value |\n|---|---|\n"
            f"| Total leads scored | {len(scored)} |\n"
            f"| Hot leads | {len(tiers['Hot'])} |\n"
            f"| Warm leads | {len(tiers['Warm'])} |\n"
            f"| Nurture leads | {len(tiers['Nurture'])} |\n"
            f"| Disqualified | {len(tiers['Disqualified'])} |\n"
            f"| Hot pipeline value | ${hot_value:,} |\n"
            f"| Warm pipeline value | ${warm_value:,} |\n"
            f"| **Total qualified pipeline** | **${total_pipeline:,}** |\n"
        )

        industry_counts = {}
        for s in scored:
            ind = s["industry"]
            industry_counts[ind] = industry_counts.get(ind, 0) + 1
        industry_table = "\n**Leads by Industry:**\n\n| Industry | Count | Hot | Warm |\n|---|---|---|---|\n"
        for ind in sorted(industry_counts, key=industry_counts.get, reverse=True):
            hot_ct = sum(1 for l in tiers["Hot"] if l["industry"] == ind)
            warm_ct = sum(1 for l in tiers["Warm"] if l["industry"] == ind)
            industry_table += f"| {ind} | {industry_counts[ind]} | {hot_ct} | {warm_ct} |\n"

        conversion = (
            "\n**Conversion Targets:**\n"
            f"- Hot to meeting: 40% ({int(len(tiers['Hot']) * 0.4)} meetings)\n"
            f"- Meeting to opportunity: 60% ({int(len(tiers['Hot']) * 0.4 * 0.6)} opportunities)\n"
            f"- Warm to meeting: 20% ({int(len(tiers['Warm']) * 0.2)} meetings)\n"
            f"- Expected pipeline from hot leads: ${int(hot_value * 0.4 * 0.6):,}\n"
        )

        actions = (
            "\n**Immediate Actions:**\n"
            f"1. {len(tiers['Hot'])} hot leads — AE outreach within 4 hours\n"
            f"2. {len(tiers['Warm'])} warm leads — SDR calls today/tomorrow\n"
            f"3. {len(tiers['Nurture'])} nurture leads — Email sequence starts automatically\n"
            f"4. {len(tiers['Disqualified'])} disqualified — Routed to marketing nurture\n"
        )

        return (
            f"**Qualification Report — Full Pipeline Summary**\n\n"
            f"{summary_table}{industry_table}{conversion}{actions}\n"
            "Source: [All Qualification Systems]\n"
            "Agents: QualificationReportAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = SalesQualificationAgent()
    for op in ["score_leads", "bant_analysis", "create_outreach",
               "assign_leads", "setup_tracking", "qualification_report"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
