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
    "display_name": "Sales Qualification Agent",
    "description": "Automate lead scoring and qualification to accelerate pipeline generation, improve conversion rates, and drive proactive sales.",
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
    {"name": "Mike Rodriguez", "territory": "West", "specialty": "Enterprise", "current_capacity_pct": 62, "max_leads": 12},
    {"name": "Sarah Kim", "territory": "East", "specialty": "Healthcare", "current_capacity_pct": 55, "max_leads": 14},
    {"name": "James Chen", "territory": "Central", "specialty": "Manufacturing", "current_capacity_pct": 70, "max_leads": 10},
    {"name": "Lisa Park", "territory": "West", "specialty": "Mid-Market SaaS", "current_capacity_pct": 48, "max_leads": 15},
    {"name": "David Okafor", "territory": "East", "specialty": "Financial Services", "current_capacity_pct": 58, "max_leads": 12},
]

# Combined lead score = ICP fit, BANT and third-party intent data, weighted; tiers 80+ / 60-79 / <60.
_SCORE_WEIGHTS = {"icp": 0.35, "bant": 0.25, "intent": 0.40}
_TIER_THRESHOLDS = {"Hot": 80, "Warm": 60}
_TIERS = ["Hot", "Warm", "Nurture"]

_SLA_RULES = {
    "Hot":     {"response_hours": 4,  "escalation": "Manager alert", "owner": "AE handoff", "sequence": "Personalized email today, then the 4-step sequence"},
    "Warm":    {"response_hours": 24, "escalation": "Team alert",    "owner": "SDR call",   "sequence": "SDR qualification call + follow-up email"},
    "Nurture": {"response_hours": 48, "escalation": "Auto-sequence", "owner": "Email sequence", "sequence": "Automated email nurture sequence"},
}

_SEQUENCE = [("Today", "Personalized email"), ("Day 2", "LinkedIn connection + note"),
             ("Day 3", "Value content email"), ("Day 4", "Phone call")]

_TARGETS = {"hot_contact_rate": 100, "meeting_conversion": 40, "alert_hours_remaining": 2}

# Talking points for the hot leads (booth notes + intent data), used by score, BANT and outreach views.
_HOT_PLAYBOOK = {
    "L001": {"highlight": "VP Eng, active eval", "signal": "Demo booth visited twice", "angle": "Connecting 12 data sources in weeks", "cta": "15-min deep dive"},
    "L002": {"highlight": "CTO, budget approved", "signal": "CTO asked technical questions", "angle": "60-day migration playbook attached", "cta": "Stack discussion"},
    "L003": {"highlight": "Competitor displacement", "signal": "Competitor contract ending", "angle": "40% of [Competitor] customers switched", "cta": "Comparison call"},
    "L004": {"highlight": "VP Ops, 8-plant rollout", "signal": "Keynote + booth visit", "angle": "Monitoring 8 plants from one pipeline", "cta": "Plant-rollout walkthrough"},
    "L005": {"highlight": "Trial started", "signal": "Signed up for trial", "angle": "40% faster pipelines on your trial data", "cta": "Trial review call"},
    "L006": {"highlight": "CDO, follow-up booked", "signal": "Booked follow-up meeting", "angle": "One patient record across 14 facilities", "cta": "Architecture session"},
    "L008": {"highlight": "CTO, deep-dive attended", "signal": "Technical deep-dive session", "angle": "Predictive maintenance from IoT data in 90 days", "cta": "Pilot scoping call"},
    "L029": {"highlight": "CTO, referral", "signal": "Requested migration assessment", "angle": "Hadoop to cloud-native migration assessment", "cta": "Assessment kickoff"},
}

_LEADS = [
    {"id": "L001", "company": "TechFlow Industries",    "contact_name": "Sarah Nguyen",    "title": "VP Engineering",        "employees": 520,  "industry": "Technology",          "revenue": 85_000_000,   "source": "Trade Show",     "budget": "confirmed", "budget_usd": 200000, "intent_score": 98, "authority_level": "VP",        "need": "Consolidate 12 data sources into unified pipeline",              "timeline": "Q1",    "engagement_signals": ["Visited pricing page", "Attended booth demo twice", "Downloaded whitepaper"],                  "tech_stack": ["AWS", "Snowflake", "Kubernetes"]},
    {"id": "L002", "company": "Meridian Corp",          "contact_name": "James Walker",    "title": "CTO",                   "employees": 1200, "industry": "Healthcare",          "revenue": 340_000_000,  "source": "Trade Show",     "budget": "confirmed", "budget_usd": 150000, "intent_score": 88, "authority_level": "C-Level",   "need": "Replace legacy EHR integration layer",                          "timeline": "60 days", "engagement_signals": ["Asked technical questions at session", "Requested architecture doc"],                          "tech_stack": ["Azure", "Salesforce", "Databricks"]},
    {"id": "L003", "company": "Apex Solutions",         "contact_name": "Diana Reyes",     "title": "Director of IT",        "employees": 780,  "industry": "SaaS",                "revenue": 120_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 180000, "intent_score": 98, "authority_level": "Director",  "need": "Displace incumbent vendor, contract ending Q1",                  "timeline": "Q1",    "engagement_signals": ["Competitor displacement signal", "Visited comparison page", "Booth conversation 15 min"],       "tech_stack": ["AWS", "Kubernetes", "Salesforce"]},
    {"id": "L004", "company": "Summit Technologies",    "contact_name": "Robert Kim",      "title": "VP Operations",         "employees": 450,  "industry": "Manufacturing",       "revenue": 95_000_000,   "source": "Trade Show",     "budget": "tbd",       "budget_usd": 40000, "intent_score": 97, "authority_level": "VP",        "need": "Scale production monitoring across 8 plants",                    "timeline": "60 days", "engagement_signals": ["Attended keynote", "Visited booth"],                                                           "tech_stack": ["Azure", "Salesforce", "Snowflake", "Databricks"]},
    {"id": "L005", "company": "DataCorp Analytics",     "contact_name": "Emily Tran",      "title": "IT Manager",            "employees": 310,  "industry": "Technology",          "revenue": 52_000_000,   "source": "Trade Show",     "budget": "confirmed", "budget_usd": 90000, "intent_score": 94, "authority_level": "Manager",   "need": "Improve data pipeline efficiency by 40%",                        "timeline": "Q2",    "engagement_signals": ["Downloaded ROI calculator", "Signed up for trial"],                                            "tech_stack": ["Snowflake", "AWS"]},
    {"id": "L006", "company": "Greenfield Health",      "contact_name": "Maria Santos",    "title": "Chief Digital Officer",  "employees": 2800, "industry": "Healthcare",          "revenue": 620_000_000,  "source": "Webinar",        "budget": "confirmed", "budget_usd": 60000, "intent_score": 64, "authority_level": "C-Level",   "need": "Unified patient data platform across 14 facilities",             "timeline": "Q1",    "engagement_signals": ["Watched full webinar", "Booked follow-up meeting", "Downloaded case study"],                   "tech_stack": ["Azure", "Salesforce", "Snowflake"]},
    {"id": "L007", "company": "Pinnacle Financial",     "contact_name": "Kevin Okafor",    "title": "VP Technology",         "employees": 1800, "industry": "Financial Services",  "revenue": 450_000_000,  "source": "Referral",       "budget": "planned",   "budget_usd": 30000, "intent_score": 50, "authority_level": "VP",        "need": "Real-time fraud detection pipeline",                             "timeline": "60 days", "engagement_signals": ["Referral from existing customer", "Requested demo"],                                           "tech_stack": ["AWS", "Databricks", "Kubernetes"]},
    {"id": "L008", "company": "Orion Manufacturing",    "contact_name": "Thomas Park",     "title": "CTO",                   "employees": 3200, "industry": "Manufacturing",       "revenue": 780_000_000,  "source": "Trade Show",     "budget": "confirmed", "budget_usd": 60000, "intent_score": 61, "authority_level": "C-Level",   "need": "IoT data ingestion for predictive maintenance",                  "timeline": "Q1",    "engagement_signals": ["Booth demo", "Technical deep-dive session", "Exchanged business cards with CEO"],              "tech_stack": ["AWS", "Kubernetes", "Snowflake"]},
    {"id": "L009", "company": "Velocity SaaS",          "contact_name": "Rachel Green",    "title": "Director of Engineering","employees": 180,  "industry": "SaaS",                "revenue": 28_000_000,   "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 26, "authority_level": "Director",  "need": "Microservices observability platform",                           "timeline": "Q2",    "engagement_signals": ["Visited booth briefly"],                                                                       "tech_stack": ["Kubernetes", "AWS"]},
    {"id": "L010", "company": "Atlas Logistics",        "contact_name": "Brian Murphy",    "title": "IT Director",           "employees": 950,  "industry": "Logistics",           "revenue": 210_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 0, "intent_score": 26, "authority_level": "Director",  "need": "Supply chain visibility dashboard",                              "timeline": "90 days", "engagement_signals": ["Attended breakout session", "Asked about integrations"],                                        "tech_stack": ["Salesforce", "Azure"]},
    {"id": "L011", "company": "Quantum Health Systems", "contact_name": "Jennifer Lee",    "title": "VP IT",                 "employees": 4100, "industry": "Healthcare",          "revenue": 1_200_000_000,"source": "Inbound Form",   "budget": "confirmed", "budget_usd": 30000, "intent_score": 49, "authority_level": "VP",        "need": "HIPAA-compliant analytics for 200+ providers",                   "timeline": "Q1",    "engagement_signals": ["Filled detailed form", "Requested pricing", "Downloaded compliance guide"],                    "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L012", "company": "Sterling Partners",      "contact_name": "Michael Chen",    "title": "Managing Director",     "employees": 85,   "industry": "Financial Services",  "revenue": 15_000_000,   "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 34, "authority_level": "C-Level",   "need": "Portfolio analytics automation",                                 "timeline": "Q3",    "engagement_signals": ["Brief booth visit"],                                                                           "tech_stack": ["Salesforce"]},
    {"id": "L013", "company": "NovaTech Solutions",     "contact_name": "Amanda Torres",   "title": "CTO",                   "employees": 650,  "industry": "Technology",          "revenue": 110_000_000,  "source": "Referral",       "budget": "confirmed", "budget_usd": 40000, "intent_score": 52, "authority_level": "C-Level",   "need": "Replace custom ETL with managed platform",                       "timeline": "60 days", "engagement_signals": ["Referral from board member", "Requested architecture review", "Downloaded migration guide"],     "tech_stack": ["AWS", "Snowflake", "Databricks", "Kubernetes"]},
    {"id": "L014", "company": "Cascade Energy",         "contact_name": "Daniel Wright",   "title": "VP Operations",         "employees": 1500, "industry": "Energy",              "revenue": 380_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 0, "intent_score": 24, "authority_level": "VP",        "need": "SCADA data integration for grid monitoring",                     "timeline": "Q2",    "engagement_signals": ["Attended demo", "Exchanged cards"],                                                            "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L015", "company": "BlueWave Analytics",     "contact_name": "Samantha Hall",   "title": "Director Data Science",  "employees": 240,  "industry": "SaaS",                "revenue": 42_000_000,   "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 23, "authority_level": "Director",  "need": "ML pipeline orchestration",                                      "timeline": "Q2",    "engagement_signals": ["Technical questions at booth", "Signed up for newsletter"],                                     "tech_stack": ["AWS", "Databricks", "Kubernetes"]},
    {"id": "L016", "company": "Pacific Mutual Insurance","contact_name": "Gregory Adams",  "title": "CIO",                   "employees": 5200, "industry": "Financial Services",  "revenue": 2_100_000_000,"source": "Executive Event","budget": "confirmed", "budget_usd": 35000, "intent_score": 49, "authority_level": "C-Level",   "need": "Claims processing automation with AI/ML",                        "timeline": "Q1",    "engagement_signals": ["1-on-1 executive meeting", "Requested proposal", "Site visit scheduled"],                       "tech_stack": ["AWS", "Salesforce", "Snowflake", "Databricks"]},
    {"id": "L017", "company": "Redstone Manufacturing", "contact_name": "Laura Martinez",  "title": "Plant Manager",         "employees": 2200, "industry": "Manufacturing",       "revenue": 540_000_000,  "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 36, "authority_level": "Manager",   "need": "Quality control data capture across lines",                      "timeline": "Q3",    "engagement_signals": ["Booth visit"],                                                                                 "tech_stack": ["Azure"]},
    {"id": "L018", "company": "Horizon Biotech",        "contact_name": "Andrew Liu",      "title": "VP Technology",         "employees": 380,  "industry": "Healthcare",          "revenue": 68_000_000,   "source": "Trade Show",     "budget": "planned",   "budget_usd": 25000, "intent_score": 41, "authority_level": "VP",        "need": "Lab data integration for clinical trials",                       "timeline": "90 days", "engagement_signals": ["Detailed booth conversation", "Downloaded case study", "Requested references"],                 "tech_stack": ["AWS", "Snowflake"]},
    {"id": "L019", "company": "Vertex Cloud",           "contact_name": "Nicole Brown",    "title": "CEO",                   "employees": 130,  "industry": "SaaS",                "revenue": 18_000_000,   "source": "Inbound Form",   "budget": "exploring", "budget_usd": 0, "intent_score": 25, "authority_level": "C-Level",   "need": "Data infrastructure for new product line",                       "timeline": "Q3",    "engagement_signals": ["Form fill"],                                                                                   "tech_stack": ["AWS", "Kubernetes"]},
    {"id": "L020", "company": "Continental Logistics",  "contact_name": "Paul Wilson",     "title": "IT Manager",            "employees": 6800, "industry": "Logistics",           "revenue": 1_800_000_000,"source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 42, "authority_level": "Manager",   "need": "Fleet telematics data warehousing",                              "timeline": "Q3",    "engagement_signals": ["Booth scan only"],                                                                             "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L021", "company": "Nexus Health Network",   "contact_name": "Christina Park",  "title": "CMIO",                  "employees": 7500, "industry": "Healthcare",          "revenue": 3_200_000_000,"source": "Referral",       "budget": "confirmed", "budget_usd": 35000, "intent_score": 47, "authority_level": "C-Level",   "need": "Population health analytics across 30 hospitals",                "timeline": "Q1",    "engagement_signals": ["Executive referral", "Requested ROI model", "Reviewed case studies"],                           "tech_stack": ["Azure", "Snowflake", "Salesforce", "Databricks"]},
    {"id": "L022", "company": "Ironclad Security",      "contact_name": "Mark Stevens",    "title": "VP Engineering",        "employees": 420,  "industry": "Technology",          "revenue": 75_000_000,   "source": "Trade Show",     "budget": "planned",   "budget_usd": 30000, "intent_score": 44, "authority_level": "VP",        "need": "Security event log aggregation at scale",                        "timeline": "60 days", "engagement_signals": ["Attended technical session", "Downloaded architecture doc", "Booth demo"],                      "tech_stack": ["AWS", "Kubernetes", "Snowflake"]},
    {"id": "L023", "company": "Maple Financial Group",  "contact_name": "Karen Zhao",      "title": "SVP Operations",        "employees": 3400, "industry": "Financial Services",  "revenue": 920_000_000,  "source": "Executive Event","budget": "confirmed", "budget_usd": 30000, "intent_score": 44, "authority_level": "VP",        "need": "Regulatory reporting data pipeline",                             "timeline": "Q1",    "engagement_signals": ["Executive dinner attendee", "Scheduled follow-up call", "Compliance use case discussed"],       "tech_stack": ["Salesforce", "Snowflake", "Databricks"]},
    {"id": "L024", "company": "Bright Horizons Edu",    "contact_name": "Steven Miller",   "title": "CTO",                   "employees": 900,  "industry": "Education",           "revenue": 145_000_000,  "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 27, "authority_level": "C-Level",   "need": "Student analytics platform consolidation",                       "timeline": "Q2",    "engagement_signals": ["Booth conversation", "Requested demo video"],                                                  "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L025", "company": "Titan Aerospace",        "contact_name": "Angela White",    "title": "Director of IT",        "employees": 2600, "industry": "Manufacturing",       "revenue": 680_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 0, "intent_score": 16, "authority_level": "Director",  "need": "Supply chain data unification across 6 plants",                  "timeline": "90 days", "engagement_signals": ["Attended breakout", "Asked about security compliance"],                                         "tech_stack": ["AWS", "Salesforce", "Snowflake"]},
    {"id": "L026", "company": "CoreBridge Insurance",   "contact_name": "Jason Taylor",    "title": "VP Data & Analytics",   "employees": 4800, "industry": "Financial Services",  "revenue": 1_500_000_000,"source": "Inbound Form",   "budget": "confirmed", "budget_usd": 30000, "intent_score": 38, "authority_level": "VP",        "need": "Actuarial data lake modernization",                              "timeline": "60 days", "engagement_signals": ["Detailed form fill", "Requested customer references", "Downloaded ROI calculator"],             "tech_stack": ["AWS", "Snowflake", "Databricks", "Salesforce"]},
    {"id": "L027", "company": "Silverline Consulting",  "contact_name": "Tara Robinson",   "title": "Partner",               "employees": 60,   "industry": "Professional Services","revenue": 8_000_000,  "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 43, "authority_level": "C-Level",   "need": "Client reporting dashboard",                                     "timeline": "Q3",    "engagement_signals": ["Booth scan"],                                                                                  "tech_stack": ["Salesforce"]},
    {"id": "L028", "company": "Westfield Medical",      "contact_name": "Priya Sharma",    "title": "VP Clinical Informatics","employees": 1900, "industry": "Healthcare",          "revenue": 420_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 25000, "intent_score": 41, "authority_level": "VP",        "need": "Clinical data warehouse for research analytics",                 "timeline": "Q1",    "engagement_signals": ["Booth demo", "Requested HIPAA compliance docs", "Technical Q&A"],                               "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L029", "company": "FusionTech Labs",        "contact_name": "Derek Johnson",   "title": "CTO",                   "employees": 290,  "industry": "SaaS",                "revenue": 48_000_000,   "source": "Referral",       "budget": "confirmed", "budget_usd": 20000, "intent_score": 59, "authority_level": "C-Level",   "need": "Migrate from on-prem Hadoop to cloud-native",                    "timeline": "60 days", "engagement_signals": ["Customer referral", "Requested migration assessment", "Downloaded migration guide"],             "tech_stack": ["AWS", "Kubernetes", "Databricks"]},
    {"id": "L030", "company": "National Grid Services", "contact_name": "Barbara Collins", "title": "IT Director",           "employees": 8200, "industry": "Energy",              "revenue": 4_500_000_000,"source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 38, "authority_level": "Director",  "need": "Smart meter data aggregation platform",                          "timeline": "Q3",    "engagement_signals": ["Booth conversation", "Exchanged cards"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L031", "company": "Elevate Commerce",       "contact_name": "Ryan Mitchell",   "title": "VP Engineering",        "employees": 350,  "industry": "Technology",          "revenue": 62_000_000,   "source": "Trade Show",     "budget": "planned",   "budget_usd": 0, "intent_score": 13, "authority_level": "VP",        "need": "Real-time inventory sync across marketplace channels",           "timeline": "90 days", "engagement_signals": ["Attended session", "Downloaded integration guide"],                                             "tech_stack": ["AWS", "Snowflake", "Kubernetes"]},
    {"id": "L032", "company": "Summit Health Partners", "contact_name": "Lisa Nakamura",   "title": "Chief Analytics Officer","employees": 5600, "industry": "Healthcare",          "revenue": 1_600_000_000,"source": "Executive Event","budget": "confirmed", "budget_usd": 30000, "intent_score": 44, "authority_level": "C-Level",   "need": "Enterprise analytics platform for value-based care",             "timeline": "Q1",    "engagement_signals": ["1-on-1 exec meeting", "Requested business case template", "Reviewed 3 case studies"],           "tech_stack": ["Azure", "Snowflake", "Salesforce", "Databricks"]},
    {"id": "L033", "company": "Pioneer Robotics",       "contact_name": "Alex Petrov",     "title": "Director of Automation", "employees": 410,  "industry": "Manufacturing",       "revenue": 88_000_000,   "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 25, "authority_level": "Director",  "need": "Robotics telemetry data pipeline",                               "timeline": "Q2",    "engagement_signals": ["Booth demo", "Technical questions"],                                                           "tech_stack": ["AWS", "Kubernetes"]},
    {"id": "L034", "company": "Heritage Bank",          "contact_name": "Sandra Lee",      "title": "SVP Technology",        "employees": 2100, "industry": "Financial Services",  "revenue": 580_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 25000, "intent_score": 40, "authority_level": "VP",        "need": "Anti-money laundering data pipeline modernization",              "timeline": "60 days", "engagement_signals": ["Detailed booth conversation", "Requested compliance references"],                               "tech_stack": ["AWS", "Salesforce", "Snowflake"]},
    {"id": "L035", "company": "ClearView Optics",       "contact_name": "Nathan Ford",     "title": "IT Manager",            "employees": 160,  "industry": "Manufacturing",       "revenue": 22_000_000,   "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 38, "authority_level": "Manager",   "need": "Quality inspection image data storage",                          "timeline": "Q3",    "engagement_signals": ["Booth scan only"],                                                                             "tech_stack": ["Azure"]},
    {"id": "L036", "company": "Axiom Data Systems",     "contact_name": "Michelle Yang",   "title": "CEO",                   "employees": 95,   "industry": "SaaS",                "revenue": 12_000_000,   "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 29, "authority_level": "C-Level",   "need": "Data pipeline as a service offering",                            "timeline": "Q3",    "engagement_signals": ["Brief booth stop"],                                                                            "tech_stack": ["AWS"]},
    {"id": "L037", "company": "Metro Health Alliance",  "contact_name": "David Nguyen",    "title": "VP Data Engineering",   "employees": 3800, "industry": "Healthcare",          "revenue": 890_000_000,  "source": "Webinar",        "budget": "planned",   "budget_usd": 25000, "intent_score": 33, "authority_level": "VP",        "need": "Real-time patient flow analytics for 18 facilities",             "timeline": "90 days", "engagement_signals": ["Webinar attendee", "Downloaded guide", "Requested pricing"],                                    "tech_stack": ["Azure", "Snowflake", "Salesforce"]},
    {"id": "L038", "company": "Vanguard Logistics",     "contact_name": "Carlos Mendez",   "title": "CTO",                   "employees": 1400, "industry": "Logistics",           "revenue": 320_000_000,  "source": "Trade Show",     "budget": "planned",   "budget_usd": 0, "intent_score": 22, "authority_level": "C-Level",   "need": "Cross-border shipment tracking data platform",                   "timeline": "Q2",    "engagement_signals": ["Attended demo", "Booth conversation"],                                                         "tech_stack": ["AWS", "Salesforce"]},
    {"id": "L039", "company": "TrueNorth Energy",       "contact_name": "Helen Foster",    "title": "VP Technology",         "employees": 2900, "industry": "Energy",              "revenue": 750_000_000,  "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 35, "authority_level": "VP",        "need": "Renewable energy asset performance analytics",                   "timeline": "Q3",    "engagement_signals": ["Keynote attendee", "Brief booth visit"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L040", "company": "Paragon Pharma",         "contact_name": "William Chang",   "title": "Director of R&D IT",    "employees": 1100, "industry": "Healthcare",          "revenue": 290_000_000,  "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 25, "authority_level": "Director",  "need": "Genomics data pipeline for drug discovery",                      "timeline": "Q2",    "engagement_signals": ["Technical session attendee", "Downloaded whitepaper"],                                          "tech_stack": ["AWS", "Databricks"]},
    {"id": "L041", "company": "Crestline Financial",    "contact_name": "Patricia Adams",  "title": "Chief Data Officer",    "employees": 6200, "industry": "Financial Services",  "revenue": 2_800_000_000,"source": "Referral",       "budget": "confirmed", "budget_usd": 30000, "intent_score": 42, "authority_level": "C-Level",   "need": "Enterprise data mesh architecture implementation",               "timeline": "Q1",    "engagement_signals": ["Board-level referral", "Requested executive briefing", "Scheduled site visit"],                 "tech_stack": ["AWS", "Snowflake", "Databricks", "Kubernetes", "Salesforce"]},
    {"id": "L042", "company": "Bridgepoint Retail",     "contact_name": "Scott Thompson",  "title": "IT Manager",            "employees": 720,  "industry": "Retail",              "revenue": 165_000_000,  "source": "Trade Show",     "budget": "tbd",       "budget_usd": 0, "intent_score": 44, "authority_level": "Manager",   "need": "POS data aggregation for analytics",                             "timeline": "Q3",    "engagement_signals": ["Booth scan"],                                                                                  "tech_stack": ["Salesforce"]},
    {"id": "L043", "company": "Sapphire Biomedical",    "contact_name": "Rebecca Foster",  "title": "VP Informatics",        "employees": 480,  "industry": "Healthcare",          "revenue": 76_000_000,   "source": "Trade Show",     "budget": "planned",   "budget_usd": 30000, "intent_score": 33, "authority_level": "VP",        "need": "Clinical trial data harmonization",                              "timeline": "90 days", "engagement_signals": ["Booth demo", "Requested case study", "Technical Q&A"],                                          "tech_stack": ["AWS", "Snowflake"]},
    {"id": "L044", "company": "Forge Industrial",       "contact_name": "Christopher Hall","title": "Plant Director",         "employees": 3500, "industry": "Manufacturing",       "revenue": 920_000_000,  "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 25, "authority_level": "Director",  "need": "Predictive maintenance data platform",                           "timeline": "Q2",    "engagement_signals": ["Attended session", "Brief booth visit"],                                                       "tech_stack": ["Azure", "Salesforce"]},
    {"id": "L045", "company": "Luminary Wealth",        "contact_name": "Jessica Wang",    "title": "VP Technology",         "employees": 250,  "industry": "Financial Services",  "revenue": 38_000_000,   "source": "Trade Show",     "budget": "exploring", "budget_usd": 0, "intent_score": 25, "authority_level": "VP",        "need": "Client portfolio reporting automation",                          "timeline": "Q3",    "engagement_signals": ["Booth conversation"],                                                                          "tech_stack": ["Salesforce", "AWS"]},
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


def _tier_lead(icp_score, bant_composite, intent_score):
    """Assign tier from the weighted ICP, BANT and intent scores: Hot 80+, Warm 60-79, Nurture below 60."""
    w = _SCORE_WEIGHTS
    combined = int(round(icp_score * w["icp"] + bant_composite * w["bant"] + intent_score * w["intent"]))
    if combined >= _TIER_THRESHOLDS["Hot"]:
        return "Hot", combined
    if combined >= _TIER_THRESHOLDS["Warm"]:
        return "Warm", combined
    return "Nurture", combined


def _match_ae(lead):
    """Route by expertise: healthcare, manufacturing and financial services specialists; technology and SaaS
    accounts of 300+ employees to Enterprise, smaller SaaS to Mid-Market."""
    industry = lead["industry"]
    if industry == "Healthcare":
        specialty = "Healthcare"
    elif industry == "Manufacturing":
        specialty = "Manufacturing"
    elif industry == "Financial Services":
        specialty = "Financial Services"
    elif lead["employees"] >= 300:
        specialty = "Enterprise"
    else:
        specialty = "Mid-Market SaaS"
    for ae in _AE_TEAM:
        if ae["specialty"] == specialty:
            return ae
    return _AE_TEAM[0]


def _money_k(value):
    if value >= 1000000:
        return f"${value / 1000000:.2f}M"
    return f"${value // 1000}K"


def _budget_label(lead):
    if lead["budget"] == "tbd":
        return f"TBD (est. {_money_k(lead['budget_usd'])})"
    return _money_k(lead["budget_usd"])


def _short_title(lead):
    return lead["title"].replace("Engineering", "Eng").replace("Director of IT", "Director")


def _generate_outreach(lead, tier):
    """Personalized outreach elements from the playbook (hot) or lead context."""
    first_name = lead["contact_name"].split()[0]
    play = _HOT_PLAYBOOK.get(lead["id"])
    if play:
        return {"subject": f"{first_name}, {play['angle'].lower()}", "hook": play["angle"], "cta": f"{play['cta']} CTA"}
    need_short = lead["need"][:60]
    if tier == "Warm":
        return {"subject": f"{lead['company']}: {need_short[:40]}",
                "hook": f"Teams like yours at {lead['company']} are solving {need_short.lower()}.",
                "cta": "Quick call to explore fit"}
    return {"subject": f"Resource: solving {need_short[:35].lower()} at scale",
            "hook": f"Our latest guide on {lead['industry'].lower()} data challenges.",
            "cta": "Reply for a walkthrough"}


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = ["score_leads", "bant_analysis", "create_outreach", "assign_leads", "setup_tracking",
               "qualification_report"]


class SalesQualificationAgent(BasicAgent):
    """
    Scores, qualifies, and routes the 45 synthetic inbound conference leads.

    Operations:
        score_leads          - ICP + BANT + intent scoring and tiering (8 Hot / 15 Warm / 22 Nurture)
        bant_analysis        - BANT breakdown for the top 5 hot leads, signals and risks
        create_outreach      - Personalized outreach drafts for every hot lead + 4-step sequence
        assign_leads         - Route hot leads to AEs by territory/expertise/capacity
        setup_tracking       - SLA rules, alerts and targets (draft plan, not activated)
        qualification_report - Summary, pipeline and action plan
    """

    def __init__(self):
        self.name = "SalesQualificationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always call this tool when a sales user asks to qualify or "
                "prioritize the 45 inbound conference leads, wants a BANT breakdown of the hot leads, personalized "
                "outreach sequences, AE assignment by territory and expertise, SLA follow-up tracking, or a "
                "summary and action plan. Short follow-ups such as 'yes, assign to AEs' or 'yes, summarize "
                "everything' continue the same workflow; call the tool right away, it has the demo data. Uses "
                "bundled synthetic leads and produces read-only scoring, draft outreach, routing recommendations, "
                "and SLA plans for human review. It never sends outreach, assigns leads, creates alerts, or "
                "writes CRM data."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "score_leads to qualify and prioritize the inbound leads (tiers + top hot leads); "
                            "bant_analysis for the BANT breakdown of the top hot leads; create_outreach for "
                            "personalized outreach sequences for the hot leads; assign_leads to assign or route "
                            "leads to AEs by territory and expertise; setup_tracking to set up tracking or hit the "
                            "follow-up SLAs; qualification_report to summarize everything with the action plan."
                        ),
                    },
                    "tier_filter": {
                        "type": "string",
                        "enum": list(_TIERS),
                        "description": (
                            "Only when the user explicitly asks to list every lead in one tier (Hot, Warm or "
                            "Nurture). Omit it for qualifying, prioritizing, review-first, BANT, outreach, routing, "
                            "tracking and summary requests."
                        ),
                    },
                    "data_source": {
                        "type": "string",
                        "enum": ["synthetic"],
                        "description": "Deterministic source route. Only bundled synthetic evidence is supported.",
                    },
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _scored(self):
        results = []
        for lead in _LEADS:
            icp = _icp_score(lead)
            bant = _bant_scores(lead)
            tier, combined = _tier_lead(icp, bant["composite"], lead["intent_score"])
            results.append({**lead, "icp_score": icp, "bant": bant, "tier": tier, "combined_score": combined})
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return results

    def _tiers(self):
        tiers = {t: [] for t in _TIERS}
        for s in self._scored():
            tiers[s["tier"]].append(s)
        return tiers

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "score_leads")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        tier_filter = kwargs.get("tier_filter")
        if tier_filter is not None and tier_filter not in _TIERS:
            return "**Error:** Unknown `tier_filter`. Valid: Hot, Warm, Nurture."
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
        output = handler(tier_filter)
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact names, lead counts, company attributes, "
            "scores, values, percentages, and timing are synthetic planning evidence. "
            "Outreach and routing are drafts for human review. No lead was assigned, no "
            "sequence or alert was activated, and no CRM or customer communication occurred."
        )

    # ── score_leads ───────────────────────────────────────────
    def _score_leads(self, tier_filter):
        scored = self._scored()
        tiers = self._tiers()
        bands = {"Hot": "Hot (80+)", "Warm": "Warm (60-79)", "Nurture": "Nurture (<60)"}
        summary = "| Tier | Leads | Recommended Action |\n|---|---|---|\n"
        for t in _TIERS:
            summary += f"| {bands[t]} | {len(tiers[t])} | {_SLA_RULES[t]['owner']} |\n"
        top_lines = ""
        for lead in tiers["Hot"][:3]:
            top_lines += f"- **{lead['company']}** ({lead['combined_score']}) - {_HOT_PLAYBOOK[lead['id']]['highlight']}\n"
        enrich = "| Company | Employees | Industry | Tech Stack | Intent |\n|---|---|---|---|---|\n"
        for lead in tiers["Hot"][:3]:
            enrich += (f"| {lead['company']} | {lead['employees']:,} | {lead['industry']} | "
                       f"{', '.join(lead['tech_stack'])} | {lead['intent_score']} |\n")
        filtered = ""
        if tier_filter:
            filtered = f"\n**{tier_filter} Leads Detail:**\n\n"
            filtered += "| Company | Contact | Score | Industry | Signals |\n|---|---|---|---|---|\n"
            for l in tiers[tier_filter]:
                sigs = ", ".join(l["engagement_signals"][:2])
                filtered += f"| {l['company']} | {l['contact_name']} | {l['combined_score']} | {l['industry']} | {sigs} |\n"
        w = _SCORE_WEIGHTS
        return (
            f"**Lead Qualification Summary — {len(scored)} Leads Scored**\n\n"
            f"Analyzed {len(scored)} leads with ICP scoring and BANT criteria plus intent data "
            f"(score = {w['icp']:.0%} ICP fit + {w['bant']:.0%} BANT + {w['intent']:.0%} intent).\n\n"
            f"{summary}\n"
            f"**Top 3 Hot Leads:**\n{top_lines}\n"
            f"**Enrichment (firmographic, technographic, intent):**\n\n{enrich}"
            f"{filtered}\n"
            "Next: BANT analysis on the hot leads.\n\n"
            "Source: [CRM + ZoomInfo + 6sense Intent Data]\n"
            "Agents: LeadEnrichmentAgent, ICPMatchingAgent"
        )

    # ── bant_analysis ─────────────────────────────────────────
    def _bant_analysis(self, tier_filter):
        targets = self._tiers()["Hot"][:5]
        table = "| Lead | Budget | Authority | Need | Timeline | BANT Score |\n|---|---|---|---|---|---|\n"
        for lead in targets:
            table += (f"| {lead['company']} | {_budget_label(lead)} | {_short_title(lead)} | {lead['need'][:45]} | "
                      f"{lead['timeline']} | {lead['bant']['composite']} |\n")
        signals = "\n**Strongest Engagement Signals:**\n"
        for lead in targets[:3]:
            signals += f"- **{lead['company']}**: {_HOT_PLAYBOOK[lead['id']]['signal']}\n"
        risks = "\n**Risk Flags:**\n"
        flagged = 0
        for lead in targets:
            if lead["budget"] == "tbd":
                risks += f"- {lead['company']}: Budget TBD\n"
                flagged += 1
            if lead["authority_level"] in ("Manager", "Individual"):
                risks += f"- {lead['company']}: Needs a decision maker ({lead['title']})\n"
                flagged += 1
        if not flagged:
            risks += "- No risk flags\n"
        return (
            f"**BANT Analysis — Top {len(targets)} Hot Leads**\n\n"
            f"{table}{signals}{risks}\n"
            "Source: [CRM + Booth Interactions + Intent Data]\n"
            "Agents: BANTScoringAgent"
        )

    # ── create_outreach ───────────────────────────────────────
    def _create_outreach(self, tier_filter):
        tier = tier_filter if tier_filter in ("Hot", "Warm") else "Hot"
        targets = self._tiers()[tier]
        rows = "| Lead | Contact | Personalized Hook | CTA |\n|---|---|---|---|\n"
        for lead in targets:
            o = _generate_outreach(lead, tier)
            rows += f"| {lead['company']} | {lead['contact_name']}, {lead['title']} | \"{o['hook']}\" | {o['cta']} |\n"
        steps = " > ".join(f"{what} {when.lower() if when != 'Today' else 'today'}" for when, what in _SEQUENCE)
        sequence = "\n**Draft Sequence Cadence (not activated):** " + steps + "\n"
        for when, what in _SEQUENCE:
            sequence += f"- {when}: {what}\n"
        return (
            f"**Personalized Outreach — {len(targets)} {tier} Leads**\n\n"
            f"Personalized outreach drafted for all {len(targets)} {tier.lower()} leads.\n\n"
            f"{rows}{sequence}\n"
            "Next: assign the leads to AEs.\n\n"
            "Source: [Content Library + Booth Notes + LinkedIn]\n"
            "Agents: PersonalizedOutreachAgent"
        )

    # ── assign_leads ──────────────────────────────────────────
    def _assign_leads(self, tier_filter):
        hot = self._tiers()["Hot"]
        assignments = {}
        for lead in hot:
            ae = _match_ae(lead)
            entry = assignments.setdefault(ae["name"], {"ae": ae, "leads": [], "value": 0})
            entry["leads"].append(lead)
            entry["value"] += lead["budget_usd"]
        table = "| AE | Leads | Pipeline | Specialty | Capacity |\n|---|---|---|---|---|\n"
        for name, d in assignments.items():
            table += (f"| {name} | {len(d['leads'])} | {_money_k(d['value'])} | {d['ae']['specialty']} | "
                      f"{d['ae']['current_capacity_pct']}% |\n")
        detail = "\n**Assignment Detail:**\n"
        for name, d in assignments.items():
            detail += f"- {name}: " + ", ".join(f"{l['company']} ({_money_k(l['budget_usd'])})" for l in d["leads"]) + "\n"
        under = all(d["ae"]["current_capacity_pct"] < 80 for d in assignments.values())
        capacity = "All AEs under 80% capacity." if under else "Capacity review needed: an AE is at 80% or more."
        return (
            f"**Recommended Lead Routing — {len(hot)} Hot Leads to {len(assignments)} AEs**\n\n"
            f"Leads routed by territory and expertise:\n\n{table}{detail}\n"
            f"{capacity} Handoff packages include BANT summary, booth notes, and email drafts.\n\n"
            "Next: set up SLA tracking.\n\n"
            "Source: [Territory Rules + Capacity Dashboard]\n"
            "Agents: LeadRoutingAgent"
        )

    # ── setup_tracking ────────────────────────────────────────
    def _setup_tracking(self, tier_filter):
        tiers = self._tiers()
        hot_pipeline = sum(l["budget_usd"] for l in tiers["Hot"])
        table = "| Tier | Leads | Response SLA | Escalation |\n|---|---|---|---|\n"
        for t in _TIERS:
            r = _SLA_RULES[t]
            table += f"| {t} | {len(tiers[t])} | {r['response_hours']} hours | {r['escalation']} |\n"
        tg = _TARGETS
        return (
            f"**Draft SLA Tracking Plan — {len(self._scored())} Synthetic Leads (ready to activate)**\n\n"
            f"{table}\n"
            f"**Automations to switch on (not activated):** Teams alerts at {tg['alert_hours_remaining']} hr "
            "remaining, manager notification if an SLA is missed, CRM stage update suggested when a meeting is "
            "booked.\n\n"
            f"**Targets:** {tg['hot_contact_rate']}% hot contact rate, {tg['meeting_conversion']}% meeting "
            f"conversion, {_money_k(hot_pipeline)} pipeline\n\n"
            "Next: generate the summary.\n\n"
            "Source: [SLA Engine + Notification System]\n"
            "Agents: SLAMonitoringAgent"
        )

    # ── qualification_report ──────────────────────────────────
    def _qualification_report(self, tier_filter):
        scored = self._scored()
        tiers = self._tiers()
        hot_value = sum(l["budget_usd"] for l in tiers["Hot"])
        warm_value = sum(l["budget_usd"] for l in tiers["Warm"])
        reps = len({_match_ae(l)["name"] for l in tiers["Hot"]})
        h, w, n = len(tiers["Hot"]), len(tiers["Warm"]), len(tiers["Nurture"])
        table = (
            "| Result | Value |\n|---|---|\n"
            f"| Leads analyzed | {len(scored)} |\n"
            f"| Hot leads | {h} ({_money_k(hot_value)}) |\n"
            f"| Outreach drafted | All {h} hot leads |\n"
            f"| AEs recommended | {reps} reps |\n"
            f"| SLA tracking | Plan ready to activate |\n"
        )
        return (
            "**Qualification Report — Lead qualification complete**\n\n"
            f"{table}\n"
            f"**Total pipeline:** {_money_k(hot_value + warm_value)} (Hot {_money_k(hot_value)} + Warm "
            f"{_money_k(warm_value)})\n\n"
            f"**Action plan:** {h} hot leads get AE outreach within {_SLA_RULES['Hot']['response_hours']} hours, "
            f"{w} warm get SDR calls, {n} nurture enter email sequences.\n\n"
            "**Draft Review Queue:** approve the hot-lead outreach drafts and AE routing, then activate the SLA plan.\n\n"
            "Source: [All Qualification Systems]\n"
            "Agents: QualificationReportAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = SalesQualificationAgent()
    for op in _OPERATIONS:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
