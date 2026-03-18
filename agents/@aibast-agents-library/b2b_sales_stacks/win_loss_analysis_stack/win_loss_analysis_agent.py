"""
Win/Loss Analysis Agent

Analyzes closed opportunities to surface win-rate trends, root-cause loss
patterns, competitor-specific insights, counter-strategies, revenue recovery
projections, and board-ready presentation frameworks.

Where a real deployment would pull from Salesforce, Gong, win/loss survey
platforms, etc., this agent uses a synthetic data layer so it runs anywhere
without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/win-loss-analysis",
    "version": "1.0.0",
    "display_name": "Win/Loss Analysis",
    "description": "AI-powered win/loss analysis with pattern recognition, competitive insights, revenue recovery modeling, and board-ready presentations.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "win-loss", "competitive-intel", "revenue-recovery"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# Stands in for CRM, Gong, Win/Loss Survey System, etc.
# ═══════════════════════════════════════════════════════════════

_LOSS_REASONS = [
    "security_certs", "enterprise_references", "pricing",
    "feature_gaps", "no_decision", "relationship",
]

_COMPETITORS = {
    "CompetitorX": {"strength": "Enterprise security certs (FedRAMP, ISO 27001)", "weakness": "Poor UX, slow implementation"},
    "CompetitorY": {"strength": "Low price point, bundled analytics",            "weakness": "Limited API, weak support"},
    "CompetitorZ": {"strength": "Industry-specific templates",                    "weakness": "No multi-cloud, small team"},
}

# Q3: 127 closed opportunities
_Q3_OPPORTUNITIES = [
    # ── Enterprise Won ──
    {"name": "Apex Financial Platform",   "account": "Apex Financial",      "value": 620000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Pinnacle Data Migration",   "account": "Pinnacle Corp",       "value": 540000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Orion Cloud Expansion",     "account": "Orion Industries",    "value": 480000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Atlas Infra Modernization", "account": "Atlas Group",         "value": 710000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Summit ERP Integration",    "account": "Summit Enterprises",  "value": 390000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Crestview Analytics",       "account": "Crestview Inc",       "value": 310000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    # ── Enterprise Lost to CompetitorX ──
    {"name": "TechCorp Secure Platform",  "account": "TechCorp Industries", "value": 890000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "GlobalBank Core Upgrade",   "account": "Global Banking Corp", "value": 780000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "SecureHealth Compliance",   "account": "SecureHealth Inc",    "value": 650000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "FedFirst Platform",         "account": "FedFirst Solutions",  "value": 720000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Metro Gov Modernization",   "account": "Metro Government",    "value": 580000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "NexGen Data Suite",         "account": "NexGen Corp",         "value": 510000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "PrimeCo Digital Transform", "account": "PrimeCo",             "value": 440000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Vantage Cloud Migration",   "account": "Vantage Ltd",         "value": 520000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Beacon ERP Overhaul",       "account": "Beacon Systems",      "value": 390000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "IronClad Security Suite",   "account": "IronClad Defense",    "value": 670000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Fortress Data Vault",       "account": "Fortress Financial",  "value": 600000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Titanium Platform Deal",    "account": "Titanium Holdings",   "value": 430000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "QuantumEdge Infra",         "account": "QuantumEdge",         "value": 350000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Sterling Cloud Services",   "account": "Sterling Group",      "value": 480000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Nexus Analytics Platform",  "account": "Nexus Corp",          "value": 290000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "OmniTech Suite",            "account": "OmniTech Inc",        "value": 380000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "CipherOne Security",        "account": "CipherOne",           "value": 550000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "AlphaWave Data",            "account": "AlphaWave",           "value": 420000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "SentinelOps Platform",      "account": "SentinelOps",         "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    # ── Lost to CompetitorY ──
    {"name": "BrightPath Analytics",      "account": "BrightPath Co",       "value": 185000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Cascade Data Services",     "account": "Cascade Inc",         "value": 210000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Evergreen SaaS Upgrade",    "account": "Evergreen LLC",       "value": 175000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Clearwater Cloud",          "account": "Clearwater Inc",      "value": 230000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "StreamLine Ops",            "account": "StreamLine Co",       "value": 195000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "PeakView Integration",      "account": "PeakView Inc",       "value": 260000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Horizon Data Platform",     "account": "Horizon Ltd",         "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Ridgeline Cloud Suite",     "account": "Ridgeline Corp",      "value": 280000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Trailhead Analytics",       "account": "Trailhead Inc",       "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Summit Edge Platform",      "account": "Summit Edge",         "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "NorthStar CRM Deal",        "account": "NorthStar Co",        "value": 220000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "WildPine Integration",      "account": "WildPine Ltd",        "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "CoralReef Data Migration",  "account": "CoralReef Inc",       "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "StoneArch Platform",        "account": "StoneArch Corp",      "value": 245000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "BlueSky SaaS Renewal",      "account": "BlueSky Solutions",   "value": 130000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "GreenField Ops",            "account": "GreenField Inc",      "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "IronBridge Analytics",      "account": "IronBridge LLC",      "value": 200000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "SilverLake Cloud",          "account": "SilverLake Co",       "value": 225000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    # ── No Decision ──
    {"name": "Redwood Budget Freeze",     "account": "Redwood Corp",        "value": 320000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Pinecrest Reorg",           "account": "Pinecrest Inc",       "value": 180000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Willow Delayed Decision",   "account": "Willow LLC",          "value": 250000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Birchwood Stall",           "account": "Birchwood Co",        "value": 145000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "OakHill Budget Hold",       "account": "OakHill Partners",    "value": 410000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Cedarpoint Priority Shift", "account": "Cedarpoint Inc",      "value": 270000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Aspen Internal Conflict",   "account": "Aspen Group",         "value": 190000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Maple Reorg Delay",         "account": "Maple Industries",    "value": 360000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "ElmGrove Postponed",        "account": "ElmGrove Ltd",        "value": 135000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Spruce Budget Cut",         "account": "Spruce Systems",      "value": 160000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Juniper Priority Shift",    "account": "Juniper Corp",        "value": 200000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "CypressWood Stall",         "account": "CypressWood Inc",     "value": 95000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    # ── Other Losses (CompetitorZ / relationship) ──
    {"name": "PolarStar Niche Fit",       "account": "PolarStar Inc",       "value": 175000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "CoastalTech Templates",     "account": "CoastalTech",         "value": 210000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "TideLine Industry Pack",    "account": "TideLine Corp",       "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "HarborView Vertical",       "account": "HarborView LLC",      "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Anchor Relationship Play",  "account": "Anchor Corp",         "value": 195000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "LightHouse Legacy",         "account": "LightHouse Inc",      "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Portside Deal",             "account": "Portside LLC",        "value": 120000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing",            "segment": "smb",        "deal_size_bucket": "100K-250K"},
    {"name": "BreakWater Eval",           "account": "BreakWater Co",       "value": 88000,  "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing",            "segment": "smb",        "deal_size_bucket": "<100K"},
    # ── Mid-Market & SMB Won ──
    {"name": "Velocity SaaS Upgrade",     "account": "Velocity Co",         "value": 185000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Spark Analytics Deal",      "account": "Spark Corp",          "value": 210000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Pulse Data Services",       "account": "Pulse Inc",           "value": 165000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Drift Cloud Platform",      "account": "Drift Technologies",  "value": 140000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Zenith Integration",        "account": "Zenith LLC",          "value": 120000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Nimbus Cloud Deal",         "account": "Nimbus Corp",         "value": 195000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Helix SaaS Expansion",      "account": "Helix Inc",           "value": 230000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Prism Data Migration",      "account": "Prism Ltd",           "value": 175000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Aether Platform",           "account": "Aether Solutions",    "value": 155000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Cirrus Ops Tooling",        "account": "Cirrus Co",           "value": 92000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Ember Starter Pack",        "account": "Ember LLC",           "value": 78000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Flint Quick Deploy",        "account": "Flint Corp",          "value": 85000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Nova Small Biz",            "account": "Nova Inc",            "value": 65000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Quasar Rapid Start",        "account": "Quasar Ltd",          "value": 72000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Photon Pilot",              "account": "Photon Co",           "value": 55000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Echo SMB Cloud",            "account": "Echo Systems",        "value": 48000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Stratos Integration",       "account": "Stratos Inc",         "value": 260000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Vortex Platform",           "account": "Vortex Corp",         "value": 240000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Matrix Data Suite",         "account": "Matrix LLC",          "value": 190000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Dynamo Cloud Ops",          "account": "Dynamo Co",           "value": 275000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Warp Speed Deploy",         "account": "Warp Inc",            "value": 145000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Comet Expansion",           "account": "Comet Solutions",     "value": 110000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Orbit Analytics",           "account": "Orbit Ltd",           "value": 98000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Luna Starter",              "account": "Luna Corp",           "value": 42000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Astro Mini Deploy",         "account": "Astro LLC",           "value": 58000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Cosmic Quick Start",        "account": "Cosmic Inc",          "value": 35000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Nebula Cloud",              "account": "Nebula Co",           "value": 68000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Pulsar SMB",               "account": "Pulsar Ltd",          "value": 46000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    # ── Additional Enterprise Lost (relationship / misc) ──
    {"name": "Horizon Ent Relationship",  "account": "Horizon Ent",         "value": 410000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "relationship",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Meridian Legacy Vendor",    "account": "Meridian Corp",       "value": 340000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "relationship",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Zenon Pricing Squeeze",     "account": "Zenon Inc",           "value": 280000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    # ── Additional Mid-Market Lost ──
    {"name": "RapidScale Eval",           "account": "RapidScale Co",       "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    # ── Additional SMB Won ──
    {"name": "Pixel Quick Deploy",        "account": "Pixel Corp",          "value": 52000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Byte Starter Pack",         "account": "Byte LLC",            "value": 38000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Atom SMB Platform",         "account": "Atom Inc",            "value": 44000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Quark Cloud Lite",          "account": "Quark Co",            "value": 62000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    # ── Additional Q3 deals to reach ~127 total ──
    {"name": "Radiant Enterprise Suite",  "account": "Radiant Corp",        "value": 560000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Cobalt Security Platform",  "account": "Cobalt Inc",          "value": 490000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Sapphire Data Vault",       "account": "Sapphire Ltd",        "value": 620000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Topaz Cloud Migration",     "account": "Topaz Group",         "value": 340000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Jade Analytics Platform",   "account": "Jade Corp",           "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Onyx Infra Deal",           "account": "Onyx Industries",     "value": 385000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Garnet Platform Upgrade",   "account": "Garnet Solutions",    "value": 450000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Pearl Managed Services",    "account": "Pearl Inc",           "value": 310000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Opal Cloud Expansion",      "account": "Opal Ltd",            "value": 420000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Ruby Analytics Suite",      "account": "Ruby Corp",           "value": 180000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Amber Data Connect",        "account": "Amber Inc",           "value": 155000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Citrine SaaS Deploy",       "account": "Citrine LLC",         "value": 125000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Agate Cloud Ops",           "account": "Agate Co",            "value": 88000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Beryl Quick Start",         "account": "Beryl Ltd",           "value": 72000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Coral SMB Platform",        "account": "Coral Corp",          "value": 55000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Diamond Micro Deploy",      "account": "Diamond Inc",         "value": 42000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "FlintEdge Analytics",       "account": "FlintEdge Co",        "value": 195000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Granite Cloud Services",    "account": "Granite Inc",         "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Basalt Data Migration",     "account": "Basalt Corp",         "value": 215000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Slate Integration Pack",    "account": "Slate LLC",           "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Shale Ops Platform",        "account": "Shale Inc",           "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Pumice Cloud Suite",        "account": "Pumice Co",           "value": 135000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Sandstone Budget Freeze",   "account": "Sandstone Ltd",       "value": 285000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Quartzite Delay",           "account": "Quartzite Corp",      "value": 110000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "100K-250K"},
    {"name": "Feldspar Reorg",            "account": "Feldspar Inc",        "value": 78000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Mica Postponement",         "account": "Mica LLC",            "value": 92000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Calcite Quick Win",         "account": "Calcite Co",          "value": 47000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Dolomite Starter",          "account": "Dolomite Inc",        "value": 56000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
]

# Q2: 118 closed opportunities (prior quarter baseline)
_Q2_OPPORTUNITIES = [
    # ── Enterprise Won (higher win rate in Q2) ──
    {"name": "Q2-Apex Expansion",        "account": "Apex Financial",     "value": 580000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Pinnacle Phase2",       "account": "Pinnacle Corp",      "value": 490000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Orion Initial",         "account": "Orion Industries",   "value": 520000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Atlas Core",            "account": "Atlas Group",        "value": 640000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Summit Begin",          "account": "Summit Enterprises", "value": 410000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Crestview Start",       "account": "Crestview Inc",      "value": 350000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Vertex Platform",       "account": "Vertex Corp",        "value": 470000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Keystone Migration",    "account": "Keystone Inc",       "value": 380000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Paradigm Cloud",        "account": "Paradigm LLC",       "value": 550000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Milestone ERP",         "account": "Milestone Corp",     "value": 620000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "500K+"},
    # ── Enterprise Lost Q2 (fewer losses) ──
    {"name": "Q2-TechCorp Eval",         "account": "TechCorp Industries","value": 680000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-GlobalBank RFP",        "account": "Global Banking Corp","value": 590000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-SecureHealth Phase1",   "account": "SecureHealth Inc",   "value": 420000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Vantage Initial",       "account": "Vantage Ltd",        "value": 380000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-PrimeCo Start",         "account": "PrimeCo",            "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-NexGen Eval",           "account": "NexGen Corp",        "value": 290000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Beacon Proposal",       "account": "Beacon Systems",     "value": 350000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    # ── Q2 Mid-Market Won ──
    {"name": "Q2-Velocity Start",        "account": "Velocity Co",        "value": 175000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Spark Initial",         "account": "Spark Corp",         "value": 190000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pulse Phase1",          "account": "Pulse Inc",          "value": 155000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Drift Deploy",          "account": "Drift Technologies", "value": 130000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Zenith Pilot",          "account": "Zenith LLC",         "value": 110000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Nimbus Start",          "account": "Nimbus Corp",        "value": 180000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Helix Core",            "account": "Helix Inc",          "value": 210000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Prism Start",           "account": "Prism Ltd",          "value": 165000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Aether Pilot",          "account": "Aether Solutions",   "value": 140000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Stratos Begin",         "account": "Stratos Inc",        "value": 250000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Vortex Initial",        "account": "Vortex Corp",        "value": 220000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Matrix Deploy",         "account": "Matrix LLC",         "value": 185000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Dynamo Ops",            "account": "Dynamo Co",          "value": 260000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    # ── Q2 Mid-Market Lost ──
    {"name": "Q2-BrightPath Eval",       "account": "BrightPath Co",      "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Cascade RFP",           "account": "Cascade Inc",        "value": 200000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Evergreen Bid",         "account": "Evergreen LLC",      "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Clearwater Eval",       "account": "Clearwater Inc",     "value": 210000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-StreamLine RFP",        "account": "StreamLine Co",      "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-PeakView Proposal",     "account": "PeakView Inc",       "value": 240000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Horizon Eval",          "account": "Horizon Ltd",        "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Ridgeline RFP",         "account": "Ridgeline Corp",     "value": 255000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Trailhead Bid",         "account": "Trailhead Inc",      "value": 130000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Summit Edge Eval",      "account": "Summit Edge",        "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-NorthStar RFP",         "account": "NorthStar Co",       "value": 195000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    # ── Q2 No Decision ──
    {"name": "Q2-Redwood Stall",         "account": "Redwood Corp",       "value": 310000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Pinecrest Delay",       "account": "Pinecrest Inc",      "value": 170000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Willow Hold",           "account": "Willow LLC",         "value": 240000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Birchwood Pause",       "account": "Birchwood Co",       "value": 135000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-OakHill Delay",         "account": "OakHill Partners",   "value": 390000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Cedarpoint Freeze",     "account": "Cedarpoint Inc",     "value": 260000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Aspen Stall",           "account": "Aspen Group",        "value": 185000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Maple Pause",           "account": "Maple Industries",   "value": 340000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-ElmGrove Freeze",       "account": "ElmGrove Ltd",       "value": 125000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "100K-250K"},
    # ── Q2 CompetitorZ / Other ──
    {"name": "Q2-PolarStar Eval",        "account": "PolarStar Inc",      "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-CoastalTech RFP",       "account": "CoastalTech",        "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-TideLine Eval",         "account": "TideLine Corp",      "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-HarborView Bid",        "account": "HarborView LLC",     "value": 130000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Anchor Deal",           "account": "Anchor Corp",        "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    # ── Q2 SMB Won ──
    {"name": "Q2-Cirrus Pilot",          "account": "Cirrus Co",          "value": 85000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Ember Quick",           "account": "Ember LLC",          "value": 72000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Flint Deploy",          "account": "Flint Corp",         "value": 80000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Nova Start",            "account": "Nova Inc",           "value": 60000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Quasar Pilot",          "account": "Quasar Ltd",         "value": 68000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Photon Trial",          "account": "Photon Co",          "value": 50000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Echo Quick",            "account": "Echo Systems",       "value": 45000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Orbit Start",           "account": "Orbit Ltd",          "value": 90000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Luna Trial",            "account": "Luna Corp",          "value": 40000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Astro Pilot",           "account": "Astro LLC",          "value": 55000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Cosmic Trial",          "account": "Cosmic Inc",         "value": 32000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Nebula Start",          "account": "Nebula Co",          "value": 62000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Pulsar Quick",          "account": "Pulsar Ltd",         "value": 42000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    # ── Additional Q2 deals to reach ~118 total ──
    {"name": "Q2-Warp Initial",          "account": "Warp Inc",           "value": 135000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Comet Start",           "account": "Comet Solutions",    "value": 105000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Ruby Start",            "account": "Ruby Corp",          "value": 170000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Amber Deploy",          "account": "Amber Inc",          "value": 145000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Citrine Pilot",         "account": "Citrine LLC",        "value": 118000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Agate Quick",           "account": "Agate Co",           "value": 82000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Beryl Trial",           "account": "Beryl Ltd",          "value": 68000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Coral Deploy",          "account": "Coral Corp",         "value": 52000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Diamond Start",         "account": "Diamond Inc",        "value": 39000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Pearl Initial",         "account": "Pearl Inc",          "value": 290000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Opal Expansion",        "account": "Opal Ltd",           "value": 400000, "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Calcite Trial",         "account": "Calcite Co",         "value": 44000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Dolomite Quick",        "account": "Dolomite Inc",       "value": 52000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Pixel Pilot",           "account": "Pixel Corp",         "value": 48000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Byte Quick",            "account": "Byte LLC",           "value": 35000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Atom Deploy",           "account": "Atom Inc",           "value": 41000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Quark Trial",           "account": "Quark Co",           "value": 58000,  "outcome": "won",  "competitor_lost_to": None,          "loss_reason": None,                 "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Radiant Eval",          "account": "Radiant Corp",       "value": 520000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Cobalt RFP",            "account": "Cobalt Inc",         "value": 450000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Sapphire Bid",          "account": "Sapphire Ltd",       "value": 580000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs",     "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-FlintEdge Eval",        "account": "FlintEdge Co",       "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Granite RFP",           "account": "Granite Inc",        "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Basalt Proposal",       "account": "Basalt Corp",        "value": 200000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Shale Eval",            "account": "Shale Inc",          "value": 175000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-LightHouse Bid",        "account": "LightHouse Inc",     "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pumice Stall",          "account": "Pumice Co",          "value": 125000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Sandstone Pause",       "account": "Sandstone Ltd",      "value": 270000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Quartzite Hold",        "account": "Quartzite Corp",     "value": 100000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Feldspar Delay",        "account": "Feldspar Inc",       "value": 72000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Mica Freeze",           "account": "Mica LLC",           "value": 85000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Portside RFP",          "account": "Portside LLC",       "value": 110000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing",            "segment": "smb",        "deal_size_bucket": "100K-250K"},
    {"name": "Q2-BreakWater Bid",        "account": "BreakWater Co",      "value": 80000,  "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing",            "segment": "smb",        "deal_size_bucket": "<100K"},
    {"name": "Q2-Slate Eval",            "account": "Slate LLC",          "value": 135000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-RapidScale RFP",        "account": "RapidScale Co",      "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-WildPine Eval",         "account": "WildPine Ltd",       "value": 175000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-CoralReef Bid",         "account": "CoralReef Inc",      "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-StoneArch Eval",        "account": "StoneArch Corp",     "value": 230000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-BlueSky RFP",           "account": "BlueSky Solutions",  "value": 120000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "relationship",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-GreenField Bid",        "account": "GreenField Inc",     "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps",       "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-IronBridge RFP",        "account": "IronBridge LLC",     "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-SilverLake Eval",       "account": "SilverLake Co",      "value": 210000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-NorthStar Bid",         "account": "NorthStar Co",       "value": 185000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing",            "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Topaz Eval",            "account": "Topaz Group",        "value": 320000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Jade RFP",              "account": "Jade Corp",          "value": 260000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Onyx Proposal",         "account": "Onyx Industries",    "value": 360000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Garnet Eval",           "account": "Garnet Solutions",   "value": 410000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing",            "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Meridian Eval",         "account": "Meridian Corp",      "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "relationship",       "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Spruce Freeze",         "account": "Spruce Systems",     "value": 150000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Juniper Stall",         "account": "Juniper Corp",       "value": 190000, "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-CypressWood Hold",      "account": "CypressWood Inc",    "value": 88000,  "outcome": "lost", "competitor_lost_to": None,          "loss_reason": "no_decision",        "segment": "smb",        "deal_size_bucket": "<100K"},
]

# Intervention costs and expected recovery rates
_INTERVENTIONS = {
    "security_positioning": {
        "label": "Security Positioning Refresh",
        "cost": 25000,
        "recovery_rate": 0.35,
        "timeline": "Immediate",
        "actions": [
            "Lead with SOC 2 Type II (currently underutilized in sales materials)",
            "Create Security Architecture one-pager for enterprise buyers",
            "Offer security team direct access during evaluation period",
            "Bridge messaging: FedRAMP in progress, SOC 2 + ISO active now",
        ],
    },
    "fedramp_certification": {
        "label": "FedRAMP Certification",
        "cost": 85000,
        "recovery_rate": 0.55,
        "timeline": "6 months",
        "actions": [
            "Engage FedRAMP 3PAO for readiness assessment",
            "Assign dedicated compliance engineering team",
            "Target FedRAMP Moderate authorization",
        ],
    },
    "reference_program": {
        "label": "Enterprise Reference Program",
        "cost": 30000,
        "recovery_rate": 0.40,
        "timeline": "30 days",
        "actions": [
            "Activate 3 enterprise customers for reference calls",
            "Produce 2 video testimonials from Fortune 1000 logos",
            "Offer reference incentives (extended support, discounts)",
            "Build enterprise customer advisory board",
        ],
    },
    "pricing_flexibility": {
        "label": "Pricing & Packaging Adjustment",
        "cost": 15000,
        "recovery_rate": 0.30,
        "timeline": "Immediate",
        "actions": [
            "Enterprise tier: bundle security features at no extra cost",
            "Offer 90-day pilot with success-based conversion",
            "Match competitor payment terms flexibility",
            "Introduce volume discount for multi-year commits",
        ],
    },
    "iso_certification": {
        "label": "ISO 27001 Certification",
        "cost": 25000,
        "recovery_rate": 0.20,
        "timeline": "4 months",
        "actions": [
            "Engage certification body for gap assessment",
            "Implement required ISMS controls",
            "Complete Stage 1 and Stage 2 audits",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS -- real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _quarter_stats(opps):
    """Compute aggregate stats for a list of opportunities."""
    total = len(opps)
    won = [o for o in opps if o["outcome"] == "won"]
    lost = [o for o in opps if o["outcome"] == "lost"]
    win_rate = round(len(won) / max(total, 1) * 100, 1)
    avg_won_value = int(sum(o["value"] for o in won) / max(len(won), 1))
    total_won_value = sum(o["value"] for o in won)
    total_lost_value = sum(o["value"] for o in lost)

    # Segment breakdown
    segments = {}
    for seg in ("enterprise", "mid-market", "smb"):
        seg_opps = [o for o in opps if o["segment"] == seg]
        seg_won = [o for o in seg_opps if o["outcome"] == "won"]
        segments[seg] = {
            "total": len(seg_opps),
            "won": len(seg_won),
            "lost": len(seg_opps) - len(seg_won),
            "win_rate": round(len(seg_won) / max(len(seg_opps), 1) * 100, 1),
        }

    return {
        "total": total, "won": len(won), "lost": len(lost),
        "win_rate": win_rate, "avg_won_value": avg_won_value,
        "total_won_value": total_won_value,
        "total_lost_value": total_lost_value,
        "segments": segments,
    }


def _competitor_breakdown(opps):
    """Break down losses by competitor with counts and values."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    competitors = {}
    no_decision_count = 0
    no_decision_value = 0
    for o in lost:
        comp = o["competitor_lost_to"]
        if comp is None:
            no_decision_count += 1
            no_decision_value += o["value"]
        else:
            if comp not in competitors:
                competitors[comp] = {"count": 0, "value": 0, "reasons": {}}
            competitors[comp]["count"] += 1
            competitors[comp]["value"] += o["value"]
            reason = o["loss_reason"] or "unknown"
            competitors[comp]["reasons"][reason] = competitors[comp]["reasons"].get(reason, 0) + 1

    competitors["No Decision"] = {"count": no_decision_count, "value": no_decision_value, "reasons": {"no_decision": no_decision_count}}
    total_lost = len(lost)
    for comp in competitors:
        competitors[comp]["pct_of_losses"] = round(competitors[comp]["count"] / max(total_lost, 1) * 100, 1)
    return competitors


def _loss_reason_analysis(opps, competitor=None):
    """Analyze loss reasons, optionally filtered to a specific competitor."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    if competitor:
        lost = [o for o in lost if o["competitor_lost_to"] == competitor]

    reasons = {}
    for o in lost:
        r = o["loss_reason"] or "unknown"
        if r not in reasons:
            reasons[r] = {"count": 0, "value": 0}
        reasons[r]["count"] += 1
        reasons[r]["value"] += o["value"]

    total_lost = len(lost)
    for r in reasons:
        reasons[r]["frequency_pct"] = round(reasons[r]["count"] / max(total_lost, 1) * 100, 1)

    # Impact scoring: high if frequency > 25%, medium 10-25%, low < 10%
    for r in reasons:
        pct = reasons[r]["frequency_pct"]
        if pct >= 25:
            reasons[r]["impact"] = "High"
        elif pct >= 10:
            reasons[r]["impact"] = "Medium"
        else:
            reasons[r]["impact"] = "Low"

        # Addressable assessment
        addressable_map = {
            "security_certs": "Yes (6 months)",
            "enterprise_references": "Yes (3 months)",
            "pricing": "Yes (immediate)",
            "feature_gaps": "Roadmap item",
            "no_decision": "Partially (nurture)",
            "relationship": "Yes (engagement plan)",
        }
        reasons[r]["addressable"] = addressable_map.get(r, "Unknown")

    return reasons


def _revenue_recovery_model(opps):
    """Model recoverable revenue per intervention based on loss data."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    projections = {}
    total_recoverable = 0

    reason_to_intervention = {
        "security_certs": ["security_positioning", "fedramp_certification"],
        "enterprise_references": ["reference_program"],
        "pricing": ["pricing_flexibility"],
        "feature_gaps": [],
        "no_decision": [],
        "relationship": ["reference_program"],
    }

    for intv_key, intv in _INTERVENTIONS.items():
        # Find deals that map to this intervention
        applicable_reasons = [r for r, ivs in reason_to_intervention.items() if intv_key in ivs]
        applicable_deals = [o for o in lost if o.get("loss_reason") in applicable_reasons]

        total_pipeline = sum(o["value"] for o in applicable_deals)
        recoverable_value = int(total_pipeline * intv["recovery_rate"])
        deal_count_low = max(1, int(len(applicable_deals) * intv["recovery_rate"] * 0.7))
        deal_count_high = max(deal_count_low, int(len(applicable_deals) * intv["recovery_rate"] * 1.1))

        projections[intv_key] = {
            "label": intv["label"],
            "applicable_deals": len(applicable_deals),
            "total_pipeline": total_pipeline,
            "recoverable_value": recoverable_value,
            "deals_recoverable": f"{deal_count_low}-{deal_count_high}",
            "cost": intv["cost"],
            "timeline": intv["timeline"],
            "roi": round(recoverable_value / max(intv["cost"], 1), 1),
        }
        total_recoverable += recoverable_value

    total_cost = sum(intv["cost"] for intv in _INTERVENTIONS.values())
    return projections, total_recoverable, total_cost


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class WinLossAnalysisAgent(BasicAgent):
    """
    Analyzes closed opportunities to surface win-rate trends, loss patterns,
    and revenue recovery opportunities.

    Operations:
        win_loss_overview   - Quarter comparison, win rates, competitor breakdown
        root_cause_analysis - Loss pattern identification with frequency/impact scoring
        counter_strategies  - Specific strategies per loss driver (immediate + long-term)
        revenue_impact      - Financial modeling of interventions with ROI
        board_presentation  - Slide-by-slide board presentation framework
        action_summary      - Complete findings and next steps
    """

    def __init__(self):
        self.name = "WinLossAnalysisAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "win_loss_overview", "root_cause_analysis",
                            "counter_strategies", "revenue_impact",
                            "board_presentation", "action_summary",
                        ],
                        "description": "The analysis to perform",
                    },
                    "quarter": {
                        "type": "string",
                        "description": "Quarter to analyze (default: Q3 current)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "win_loss_overview")
        dispatch = {
            "win_loss_overview": self._win_loss_overview,
            "root_cause_analysis": self._root_cause_analysis,
            "counter_strategies": self._counter_strategies,
            "revenue_impact": self._revenue_impact,
            "board_presentation": self._board_presentation,
            "action_summary": self._action_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return json.dumps({"status": "error", "message": f"Unknown operation: {op}"})
        return handler()

    # ── win_loss_overview ──────────────────────────────────────
    def _win_loss_overview(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        wr_delta = round(q3["win_rate"] - q2["win_rate"], 1)
        ent_delta = round(q3["segments"]["enterprise"]["win_rate"] - q2["segments"]["enterprise"]["win_rate"], 1)
        opp_delta = round((q3["total"] - q2["total"]) / max(q2["total"], 1) * 100)
        avg_delta = round((q3["avg_won_value"] - q2["avg_won_value"]) / max(q2["avg_won_value"], 1) * 100)

        comp_q3 = _competitor_breakdown(_Q3_OPPORTUNITIES)
        comp_q2 = _competitor_breakdown(_Q2_OPPORTUNITIES)

        # Build competitor table sorted by loss count descending
        comp_rows = ""
        for comp in sorted(comp_q3, key=lambda c: comp_q3[c]["count"], reverse=True):
            c3 = comp_q3[comp]
            c2 = comp_q2.get(comp, {"pct_of_losses": 0})
            trend_val = round(c3["pct_of_losses"] - c2["pct_of_losses"], 1)
            trend = f"Up {trend_val}%" if trend_val > 1 else ("Down {:.0f}%".format(abs(trend_val)) if trend_val < -1 else "Flat")
            comp_rows += f"| {comp} | {c3['count']} | {c3['pct_of_losses']}% | {trend} |\n"

        # Identify top competitor
        top_comp = max((c for c in comp_q3 if c != "No Decision"), key=lambda c: comp_q3[c]["count"], default="CompetitorX")

        seg_table = ""
        for seg in ("enterprise", "mid-market", "smb"):
            s3 = q3["segments"][seg]
            s2 = q2["segments"][seg]
            delta = round(s3["win_rate"] - s2["win_rate"], 1)
            seg_table += f"| {seg.title()} | {s3['win_rate']}% | {s2['win_rate']}% | {delta:+.1f} pts |\n"

        return (
            f"**Q3 Win/Loss Overview** ({q3['total']} closed opportunities analyzed)\n\n"
            f"| Metric | Q3 | Q2 | Change |\n|---|---|---|---|\n"
            f"| Total opportunities | {q3['total']} | {q2['total']} | {opp_delta:+d}% |\n"
            f"| Win rate | {q3['win_rate']}% | {q2['win_rate']}% | {wr_delta:+.1f} pts |\n"
            f"| Enterprise win rate | {q3['segments']['enterprise']['win_rate']}% | {q2['segments']['enterprise']['win_rate']}% | {ent_delta:+.1f} pts |\n"
            f"| Avg deal size (won) | ${q3['avg_won_value']:,} | ${q2['avg_won_value']:,} | {avg_delta:+d}% |\n\n"
            f"**Win Rate by Segment:**\n\n"
            f"| Segment | Q3 | Q2 | Change |\n|---|---|---|---|\n{seg_table}\n"
            f"**Loss Analysis by Competitor:**\n\n"
            f"| Competitor | Losses | % of Total | Trend |\n|---|---|---|---|\n{comp_rows}\n"
            f"**Initial Pattern:** {top_comp} wins are concentrated in enterprise ($500K+) deals with security-conscious buyers.\n\n"
            f"Source: [CRM + Win/Loss Interviews + Competitive Intel]\n"
            f"Agents: WinLossDataAgent, PatternRecognitionAgent"
        )

    # ── root_cause_analysis ────────────────────────────────────
    def _root_cause_analysis(self):
        # Focus on top competitor
        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"], default="CompetitorX")
        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)

        # Sort by frequency
        sorted_reasons = sorted(reasons.items(), key=lambda kv: kv[1]["count"], reverse=True)

        reason_labels = {
            "security_certs": "Security certifications",
            "enterprise_references": "Enterprise references",
            "pricing": "Pricing/packaging",
            "feature_gaps": "Feature gaps",
            "no_decision": "No decision",
            "relationship": "Relationship/trust",
        }

        table = ""
        for r, data in sorted_reasons:
            label = reason_labels.get(r, r)
            table += f"| {label} | {data['frequency_pct']}% | {data['impact']} | {data['addressable']} |\n"

        # Deep dives for top 2 reasons
        top_two = sorted_reasons[:2]
        deep_dives = ""
        buyer_quotes = {
            "security_certs": "We loved the product but couldn't get past security review",
            "enterprise_references": "We need peer validation from companies our size before we commit",
            "pricing": "The total cost was above our budget threshold for this category",
            "feature_gaps": "Missing capabilities we consider table-stakes for our use case",
            "relationship": "We had stronger rapport and trust with the competing vendor team",
        }

        sec_deals = [o for o in _Q3_OPPORTUNITIES if o["outcome"] == "lost" and o["competitor_lost_to"] == top_comp and o["loss_reason"] == "security_certs"]
        ref_deals = [o for o in _Q3_OPPORTUNITIES if o["outcome"] == "lost" and o["competitor_lost_to"] == top_comp and o["loss_reason"] == "enterprise_references"]

        if sec_deals:
            deep_dives += (
                f"\n**Deep Dive - Security ({len(sec_deals)} deals, ${sum(d['value'] for d in sec_deals):,} pipeline):**\n"
                f"- {top_comp} has FedRAMP certification (we do not)\n"
                f"- They lead with SOC 2 Type II + ISO 27001 in every proposal\n"
                f"- Enterprise buyers require these for procurement approval\n"
                f'- Quote: "{buyer_quotes["security_certs"]}"\n'
            )
        if ref_deals:
            deep_dives += (
                f"\n**Deep Dive - References ({len(ref_deals)} deals, ${sum(d['value'] for d in ref_deals):,} pipeline):**\n"
                f"- {top_comp} has 12 Fortune 500 logos available for reference\n"
                f"- We have 3 enterprise references currently available\n"
                f"- Buyers want peer validation at their scale before committing\n"
                f'- Quote: "{buyer_quotes["enterprise_references"]}"\n'
            )

        # Win/loss interview insight
        preferred_ux_count = len(sec_deals) + len(ref_deals)
        interview_note = ""
        if preferred_ux_count > 0:
            surveyed = min(preferred_ux_count, 10)
            preferred = int(surveyed * 0.8)
            interview_note = f"\n**Win/Loss Interview Insight:** {preferred} of {surveyed} lost buyers said they preferred our UX but couldn't justify the security/reference risk.\n"

        return (
            f"**Root Cause Analysis - Losses to {top_comp}:**\n\n"
            f"| Reason | Frequency | Impact | Addressable? |\n|---|---|---|---|\n{table}"
            f"{deep_dives}{interview_note}\n"
            f"Source: [Win/Loss Surveys + Gong Calls + Competitive Intel]\n"
            f"Agents: RootCauseAnalysisAgent, PatternRecognitionAgent"
        )

    # ── counter_strategies ─────────────────────────────────────
    def _counter_strategies(self):
        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES)
        sorted_reasons = sorted(reasons.items(), key=lambda kv: kv[1]["count"], reverse=True)

        immediate = []
        long_term = []
        for intv_key, intv in _INTERVENTIONS.items():
            if intv["timeline"] in ("Immediate", "30 days"):
                immediate.append((intv_key, intv))
            else:
                long_term.append((intv_key, intv))

        imm_section = "**Immediate Actions (This Quarter):**\n\n"
        for i, (key, intv) in enumerate(immediate, 1):
            imm_section += f"**{i}. {intv['label']}**\n"
            for action in intv["actions"]:
                imm_section += f"- {action}\n"
            imm_section += "\n"

        lt_section = "**Longer-Term (Next 2 Quarters):**\n\n"
        for key, intv in long_term:
            lt_section += f"- {intv['label']} ({intv['timeline']} timeline, ${intv['cost']:,} investment)\n"
            for action in intv["actions"]:
                lt_section += f"  - {action}\n"
        lt_section += "\n"

        talk_track = (
            "**Updated Talk Track:**\n"
            '"We\'re the secure choice for enterprises who want modern UX. '
            "Here's our SOC 2 Type II, and our FedRAMP is in progress. "
            'Let us connect you with 3 enterprise references in your industry."\n'
        )

        return (
            f"**Counter-Strategies for Win Rate Recovery:**\n\n"
            f"{imm_section}{lt_section}{talk_track}\n"
            f"Source: [Competitive Playbook + Product Roadmap]\n"
            f"Agents: CompetitiveStrategyAgent"
        )

    # ── revenue_impact ─────────────────────────────────────────
    def _revenue_impact(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        projections, total_recoverable, total_cost = _revenue_recovery_model(_Q3_OPPORTUNITIES)

        # Revenue recovery table
        table = ""
        for key in sorted(projections, key=lambda k: projections[k]["recoverable_value"], reverse=True):
            p = projections[key]
            table += f"| {p['label']} | {p['deals_recoverable']} deals | ${p['recoverable_value']:,} | {p['timeline']} |\n"

        overall_roi = round(total_recoverable / max(total_cost, 1), 1)

        # Forecast impact modeling
        current_won = q3["total_won_value"]
        # Project Q4 based on current trajectory vs intervention
        q4_current_trajectory = int(current_won * 1.0)  # Flat from Q3
        intervention_lift = int(total_recoverable * 0.62)  # 62% realizable in Q4
        q4_with_intervention = q4_current_trajectory + intervention_lift

        current_wr = q3["win_rate"]
        q4_wr = round(current_wr + (total_recoverable / max(q3["total_lost_value"], 1)) * 100 * 0.15, 1)
        q1_wr = round(q4_wr + 4.0, 1)
        q2_wr = round(q1_wr + 4.0, 1)

        return (
            f"**Revenue Impact Model:**\n\n"
            f"| Intervention | Deals Recoverable | Pipeline Value | Timeline |\n|---|---|---|---|\n{table}\n"
            f"**Q4 Forecast Impact:**\n"
            f"- Current trajectory: ${q4_current_trajectory:,} ({current_wr}% win rate)\n"
            f"- With interventions: ${q4_with_intervention:,} ({q4_wr}% win rate)\n"
            f"- **Incremental revenue: ${intervention_lift:,}**\n\n"
            f"**Win Rate Recovery Path:**\n\n"
            f"| Quarter | Projected Win Rate | Key Driver |\n|---|---|---|\n"
            f"| Q4 | {q4_wr}% | Positioning + pricing |\n"
            f"| Q1 | {q1_wr}% | References + certifications |\n"
            f"| Q2 | {q2_wr}% | Full program maturity |\n\n"
            f"**ROI Calculation:**\n"
            f"- Investment: ${total_cost:,} (certifications, content, incentives)\n"
            f"- Return: ${total_recoverable:,} recovered pipeline\n"
            f"- ROI: {overall_roi}:1\n\n"
            f"Source: [Revenue Analytics + Forecast Models]\n"
            f"Agents: RevenueImpactAgent"
        )

    # ── board_presentation ─────────────────────────────────────
    def _board_presentation(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        wr_delta = round(q3["win_rate"] - q2["win_rate"], 1)
        ent_delta = round(q3["segments"]["enterprise"]["win_rate"] - q2["segments"]["enterprise"]["win_rate"], 1)

        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"], default="CompetitorX")
        top_comp_pct = comp[top_comp]["pct_of_losses"]

        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)
        sorted_reasons = sorted(reasons.items(), key=lambda kv: kv[1]["count"], reverse=True)

        reason_labels = {
            "security_certs": "Security certs",
            "enterprise_references": "Enterprise refs",
            "pricing": "Pricing",
            "feature_gaps": "Feature gaps",
            "relationship": "Relationship",
        }

        projections, total_recoverable, total_cost = _revenue_recovery_model(_Q3_OPPORTUNITIES)
        overall_roi = round(total_recoverable / max(total_cost, 1), 1)

        current_wr = q3["win_rate"]
        q4_wr = round(current_wr + (total_recoverable / max(q3["total_lost_value"], 1)) * 100 * 0.15, 1)

        evidence_table = ""
        for r, data in sorted_reasons[:3]:
            label = reason_labels.get(r, r)
            evidence_table += f"| {label} | {data['frequency_pct']}% of losses | Buyer feedback, lost deal analysis |\n"

        return (
            f"**Board Presentation: Q3 Win/Loss Analysis**\n\n"
            f"**Slide 1: The Challenge**\n"
            f"- Win rate declined to {q3['win_rate']}% (from {q2['win_rate']}%)\n"
            f"- Enterprise segment hit hardest ({ent_delta:+.1f} pts)\n"
            f"- {top_comp} captured {top_comp_pct}% of our losses\n"
            f"- Root cause: Security positioning and references gap\n\n"
            f"**Slide 2: Why We're Losing**\n\n"
            f"| Factor | Impact | Evidence |\n|---|---|---|\n{evidence_table}\n"
            f"**Slide 3: The Plan**\n"
            f"- Immediate: Security messaging refresh, pricing flexibility\n"
            f"- 30 days: Enterprise reference program launch\n"
            f"- 6 months: FedRAMP + ISO 27001 certification\n\n"
            f"**Slide 4: Expected Outcomes**\n"
            f"- Q4 win rate target: {q4_wr}% ({q4_wr - current_wr:+.1f} pts)\n"
            f"- Pipeline recovery: ${total_recoverable:,}\n"
            f"- Investment required: ${total_cost:,}\n"
            f"- ROI: {overall_roi}:1\n\n"
            f"**Ask:** Approve ${total_cost:,} for certification and reference program.\n\n"
            f"Source: [All Analysis Systems]\n"
            f"Agents: ExecutivePresentationAgent"
        )

    # ── action_summary ─────────────────────────────────────────
    def _action_summary(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        wr_delta = round(q3["win_rate"] - q2["win_rate"], 1)

        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"], default="CompetitorX")
        top_comp_pct = comp[top_comp]["pct_of_losses"]

        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)
        sorted_reasons = sorted(reasons.items(), key=lambda kv: kv[1]["count"], reverse=True)
        top_reason = sorted_reasons[0] if sorted_reasons else ("unknown", {"frequency_pct": 0})
        second_reason = sorted_reasons[1] if len(sorted_reasons) > 1 else ("unknown", {"frequency_pct": 0})

        reason_labels = {
            "security_certs": "Security certifications",
            "enterprise_references": "Enterprise references",
            "pricing": "Pricing/packaging",
            "feature_gaps": "Feature gaps",
            "no_decision": "No decision",
            "relationship": "Relationship/trust",
        }

        projections, total_recoverable, total_cost = _revenue_recovery_model(_Q3_OPPORTUNITIES)
        overall_roi = round(total_recoverable / max(total_cost, 1), 1)
        num_root_causes = len([r for r in reasons if reasons[r]["frequency_pct"] >= 10])

        current_wr = q3["win_rate"]
        q4_wr = round(current_wr + (total_recoverable / max(q3["total_lost_value"], 1)) * 100 * 0.15, 1)
        recovery_quarters = 2

        return (
            f"**Win/Loss Analysis - Complete Summary**\n\n"
            f"| Insight | Finding |\n|---|---|\n"
            f"| Q3 win rate | {q3['win_rate']}% ({wr_delta:+.1f} pts from Q2) |\n"
            f"| Primary competitor | {top_comp} ({top_comp_pct}% of losses) |\n"
            f"| Biggest gap | {reason_labels.get(top_reason[0], top_reason[0])} ({top_reason[1]['frequency_pct']}%) |\n"
            f"| Second gap | {reason_labels.get(second_reason[0], second_reason[0])} ({second_reason[1]['frequency_pct']}%) |\n"
            f"| Recoverable pipeline | ${total_recoverable:,} |\n\n"
            f"**Session Accomplishments:**\n"
            f"- Analyzed {q3['total']} Q3 opportunities\n"
            f"- Identified {num_root_causes} root causes for losses\n"
            f"- Developed counter-strategies for each driver\n"
            f"- Modeled ${total_recoverable:,} revenue recovery\n"
            f"- Created board presentation framework\n\n"
            f"**Immediate Actions (This Week):**\n"
            f"1. Update security positioning materials\n"
            f"2. Launch pricing flexibility program\n"
            f"3. Activate enterprise reference calls\n"
            f"4. Train sales team on updated talk tracks\n\n"
            f"**30-Day Milestones:**\n"
            f"- Reference video testimonials live\n"
            f"- FedRAMP readiness assessment initiated\n"
            f"- Win rate tracking dashboard active\n\n"
            f"**Expected Outcome:** Win rate recovery from {current_wr}% to {q4_wr}% within {recovery_quarters} quarters, "
            f"${total_recoverable:,} pipeline recovery, {overall_roi}:1 ROI on ${total_cost:,} investment.\n\n"
            f"Source: [All Win/Loss Systems]\n"
            f"Agents: ExecutivePresentationAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = WinLossAnalysisAgent()
    for op in ["win_loss_overview", "root_cause_analysis", "counter_strategies",
                "revenue_impact", "board_presentation", "action_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
