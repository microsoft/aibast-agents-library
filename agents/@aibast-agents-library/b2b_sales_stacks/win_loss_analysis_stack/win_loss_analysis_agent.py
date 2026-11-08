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
    "display_name": "Win Loss Analysis Agent",
    "description": "Automates competitive deal analysis to uncover root causes, improve win rates, and guide strategic sales enablement.",
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

# Q3: 127 closed opportunities - 36 won (28%), 91 lost: CompetitorX 43, CompetitorY 23, no decision 15, CompetitorZ 10.
# secondary_reason = a second loss reason the buyer cited in the win/loss interview (counted as a mention).
_Q3_OPPORTUNITIES = [
    {"name": "Apex Financial Platform", "account": "Apex Financial", "value": 330000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Pinnacle Data Migration", "account": "Pinnacle Corp", "value": 355000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Orion Cloud Expansion", "account": "Orion Industries", "value": 380000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Atlas Infra Modernization", "account": "Atlas Group", "value": 405000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Summit ERP Integration", "account": "Summit Enterprises", "value": 435000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Crestview Analytics", "account": "Crestview Inc", "value": 460000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Velocity SaaS Upgrade", "account": "Velocity Co", "value": 485000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Spark Analytics Deal", "account": "Spark Corp", "value": 510000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Pulse Data Services", "account": "Pulse Inc", "value": 540000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Drift Cloud Platform", "account": "Drift Technologies", "value": 145000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Zenith Integration", "account": "Zenith LLC", "value": 160000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Nimbus Cloud Deal", "account": "Nimbus Corp", "value": 170000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Helix SaaS Expansion", "account": "Helix Inc", "value": 180000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Prism Data Migration", "account": "Prism Ltd", "value": 195000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Aether Platform", "account": "Aether Solutions", "value": 205000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Cirrus Ops Tooling", "account": "Cirrus Co", "value": 215000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Ember Starter Pack", "account": "Ember LLC", "value": 230000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Flint Quick Deploy", "account": "Flint Corp", "value": 240000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Nova Small Biz", "account": "Nova Inc", "value": 145000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Quasar Rapid Start", "account": "Quasar Ltd", "value": 160000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Photon Pilot", "account": "Photon Co", "value": 170000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Echo SMB Cloud", "account": "Echo Systems", "value": 180000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Stratos Integration", "account": "Stratos Inc", "value": 195000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Vortex Platform", "account": "Vortex Corp", "value": 310000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Matrix Data Suite", "account": "Matrix LLC", "value": 90000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Dynamo Cloud Ops", "account": "Dynamo Co", "value": 95000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Warp Speed Deploy", "account": "Warp Inc", "value": 105000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Comet Expansion", "account": "Comet Solutions", "value": 110000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Orbit Analytics", "account": "Orbit Ltd", "value": 115000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Luna Starter", "account": "Luna Corp", "value": 125000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Astro Mini Deploy", "account": "Astro LLC", "value": 130000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Cosmic Quick Start", "account": "Cosmic Inc", "value": 140000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Nebula Cloud", "account": "Nebula Co", "value": 145000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Pulsar SMB", "account": "Pulsar Ltd", "value": 90000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Pixel Quick Deploy", "account": "Pixel Corp", "value": 95000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Byte Starter Pack", "account": "Byte LLC", "value": 160000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "TechCorp Secure Platform", "account": "TechCorp Industries", "value": 365000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "secondary_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "GlobalBank Core Upgrade", "account": "Global Banking Corp", "value": 395000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "SecureHealth Compliance", "account": "SecureHealth Inc", "value": 420000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "FedFirst Platform", "account": "FedFirst Solutions", "value": 450000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Metro Gov Modernization", "account": "Metro Government", "value": 480000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "NexGen Data Suite", "account": "NexGen Corp", "value": 510000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "IronClad Security Suite", "account": "IronClad Defense", "value": 540000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Fortress Data Vault", "account": "Fortress Financial", "value": 565000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "CipherOne Security", "account": "CipherOne", "value": 595000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Radiant Enterprise Suite", "account": "Radiant Corp", "value": 365000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Cobalt Security Platform", "account": "Cobalt Inc", "value": 395000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Garnet Platform Upgrade", "account": "Garnet Solutions", "value": 420000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "PrimeCo Digital Transform", "account": "PrimeCo", "value": 450000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Vantage Cloud Migration", "account": "Vantage Ltd", "value": 770000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Beacon ERP Overhaul", "account": "Beacon Systems", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Titanium Platform Deal", "account": "Titanium Holdings", "value": 300000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "AlphaWave Data", "account": "AlphaWave", "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "secondary_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Sapphire Data Vault", "account": "Sapphire Ltd", "value": 295000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Onyx Infra Deal", "account": "Onyx Industries", "value": 315000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "QuantumEdge Infra", "account": "QuantumEdge", "value": 340000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Sterling Cloud Services", "account": "Sterling Group", "value": 360000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Nexus Analytics Platform", "account": "Nexus Corp", "value": 380000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "OmniTech Suite", "account": "OmniTech Inc", "value": 405000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "SentinelOps Platform", "account": "SentinelOps", "value": 510000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "BrightPath Analytics", "account": "BrightPath Co", "value": 120000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Cascade Data Services", "account": "Cascade Inc", "value": 130000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Evergreen SaaS Upgrade", "account": "Evergreen LLC", "value": 230000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Zenon Pricing Squeeze", "account": "Zenon Inc", "value": 645000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "secondary_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Topaz Cloud Migration", "account": "Topaz Group", "value": 695000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "secondary_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Clearwater Cloud", "account": "Clearwater Inc", "value": 750000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "StreamLine Ops", "account": "StreamLine Co", "value": 1310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "PeakView Integration", "account": "PeakView Inc", "value": 290000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Horizon Data Platform", "account": "Horizon Ltd", "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Ridgeline Cloud Suite", "account": "Ridgeline Corp", "value": 335000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Trailhead Analytics", "account": "Trailhead Inc", "value": 355000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Summit Edge Platform", "account": "Summit Edge", "value": 610000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "500K+"},
    {"name": "Jade Analytics Platform", "account": "Jade Corp", "value": 305000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "NorthStar CRM Deal", "account": "NorthStar Co", "value": 495000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "WildPine Integration", "account": "WildPine Ltd", "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "CoralReef Data Migration", "account": "CoralReef Inc", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "StoneArch Platform", "account": "StoneArch Corp", "value": 195000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "BlueSky SaaS Renewal", "account": "BlueSky Solutions", "value": 205000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "GreenField Ops", "account": "GreenField Inc", "value": 355000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "IronBridge Analytics", "account": "IronBridge LLC", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "RapidScale Eval", "account": "RapidScale Co", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "FlintEdge Analytics", "account": "FlintEdge Co", "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Basalt Data Migration", "account": "Basalt Corp", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "SilverLake Cloud", "account": "SilverLake Co", "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Portside Deal", "account": "Portside LLC", "value": 200000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Atom SMB Platform", "account": "Atom Inc", "value": 215000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Quark Cloud Lite", "account": "Quark Co", "value": 225000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Pearl Managed Services", "account": "Pearl Inc", "value": 235000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Opal Cloud Expansion", "account": "Opal Ltd", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Ruby Analytics Suite", "account": "Ruby Corp", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Amber Data Connect", "account": "Amber Inc", "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Citrine SaaS Deploy", "account": "Citrine LLC", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Agate Cloud Ops", "account": "Agate Co", "value": 305000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Granite Cloud Services", "account": "Granite Inc", "value": 130000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Beryl Quick Start", "account": "Beryl Ltd", "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Coral SMB Platform", "account": "Coral Corp", "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Diamond Micro Deploy", "account": "Diamond Inc", "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Slate Integration Pack", "account": "Slate LLC", "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Shale Ops Platform", "account": "Shale Inc", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Pumice Cloud Suite", "account": "Pumice Co", "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Calcite Quick Win", "account": "Calcite Co", "value": 200000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Dolomite Starter", "account": "Dolomite Inc", "value": 210000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Redwood Budget Freeze", "account": "Redwood Corp", "value": 265000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Pinecrest Reorg", "account": "Pinecrest Inc", "value": 285000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Willow Delayed Decision", "account": "Willow LLC", "value": 310000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Birchwood Stall", "account": "Birchwood Co", "value": 540000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "OakHill Budget Hold", "account": "OakHill Partners", "value": 135000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Cedarpoint Priority Shift", "account": "Cedarpoint Inc", "value": 150000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Aspen Internal Conflict", "account": "Aspen Group", "value": 160000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Maple Reorg Delay", "account": "Maple Industries", "value": 170000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "ElmGrove Postponed", "account": "ElmGrove Ltd", "value": 180000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Spruce Budget Cut", "account": "Spruce Systems", "value": 190000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Juniper Priority Shift", "account": "Juniper Corp", "value": 275000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "CypressWood Stall", "account": "CypressWood Inc", "value": 65000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Sandstone Budget Freeze", "account": "Sandstone Ltd", "value": 70000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Quartzite Delay", "account": "Quartzite Corp", "value": 75000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Feldspar Reorg", "account": "Feldspar Inc", "value": 130000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "PolarStar Niche Fit", "account": "PolarStar Inc", "value": 135000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "CoastalTech Templates", "account": "CoastalTech", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "TideLine Industry Pack", "account": "TideLine Corp", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "HarborView Vertical", "account": "HarborView LLC", "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Arden Platform Deal", "account": "Arden Group", "value": 175000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Bexley Platform Deal", "account": "Bexley Group", "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "BreakWater Eval", "account": "BreakWater Co", "value": 70000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Calder Platform Deal", "account": "Calder Group", "value": 75000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Dunmore Platform Deal", "account": "Dunmore Group", "value": 80000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Eastvale Platform Deal", "account": "Eastvale Group", "value": 135000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "100K-250K"},
]

# Q2: 120 closed opportunities (prior quarter baseline) - 42 won (35%), CompetitorX 27 of 78 losses.
_Q2_OPPORTUNITIES = [
    {"name": "Q2-Apex Expansion", "account": "Apex Financial", "value": 350000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Pinnacle Phase2", "account": "Pinnacle Corp", "value": 380000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Orion Initial", "account": "Orion Industries", "value": 410000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Atlas Core", "account": "Atlas Group", "value": 435000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Summit Begin", "account": "Summit Enterprises", "value": 465000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Crestview Start", "account": "Crestview Inc", "value": 490000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Vertex Platform", "account": "Vertex Corp", "value": 520000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Keystone Migration", "account": "Keystone Inc", "value": 545000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Paradigm Cloud", "account": "Paradigm LLC", "value": 575000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Milestone ERP", "account": "Milestone Corp", "value": 350000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Velocity Start", "account": "Velocity Co", "value": 580000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Spark Initial", "account": "Spark Corp", "value": 145000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pulse Phase1", "account": "Pulse Inc", "value": 155000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Drift Deploy", "account": "Drift Technologies", "value": 165000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Zenith Pilot", "account": "Zenith LLC", "value": 180000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Nimbus Start", "account": "Nimbus Corp", "value": 190000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Helix Core", "account": "Helix Inc", "value": 200000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Prism Start", "account": "Prism Ltd", "value": 210000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Aether Pilot", "account": "Aether Solutions", "value": 225000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Stratos Begin", "account": "Stratos Inc", "value": 235000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Vortex Initial", "account": "Vortex Corp", "value": 145000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Matrix Deploy", "account": "Matrix LLC", "value": 155000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Dynamo Ops", "account": "Dynamo Co", "value": 165000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Cirrus Pilot", "account": "Cirrus Co", "value": 180000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Ember Quick", "account": "Ember LLC", "value": 190000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Flint Deploy", "account": "Flint Corp", "value": 200000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Nova Start", "account": "Nova Inc", "value": 210000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Quasar Pilot", "account": "Quasar Ltd", "value": 225000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Photon Trial", "account": "Photon Co", "value": 225000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Echo Quick", "account": "Echo Systems", "value": 60000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Orbit Start", "account": "Orbit Ltd", "value": 65000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Luna Trial", "account": "Luna Corp", "value": 70000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Astro Pilot", "account": "Astro LLC", "value": 70000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Cosmic Trial", "account": "Cosmic Inc", "value": 75000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Nebula Start", "account": "Nebula Co", "value": 80000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Pulsar Quick", "account": "Pulsar Ltd", "value": 85000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Warp Initial", "account": "Warp Inc", "value": 90000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Comet Start", "account": "Comet Solutions", "value": 95000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Ruby Start", "account": "Ruby Corp", "value": 60000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Amber Deploy", "account": "Amber Inc", "value": 65000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Citrine Pilot", "account": "Citrine LLC", "value": 70000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Agate Quick", "account": "Agate Co", "value": 115000, "outcome": "won", "competitor_lost_to": None, "loss_reason": None, "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-TechCorp Eval", "account": "TechCorp Industries", "value": 380000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-GlobalBank RFP", "account": "Global Banking Corp", "value": 410000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Radiant Eval", "account": "Radiant Corp", "value": 440000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Sapphire Bid", "account": "Sapphire Ltd", "value": 470000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Vantage Initial", "account": "Vantage Ltd", "value": 500000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-PrimeCo Start", "account": "PrimeCo", "value": 800000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "security_certs", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-SecureHealth Phase1", "account": "SecureHealth Inc", "value": 290000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Beacon Proposal", "account": "Beacon Systems", "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Cobalt RFP", "account": "Cobalt Inc", "value": 335000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Onyx Proposal", "account": "Onyx Industries", "value": 355000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Anchor Deal", "account": "Anchor Corp", "value": 610000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "enterprise_references", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-NexGen Eval", "account": "NexGen Corp", "value": 285000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Topaz Eval", "account": "Topaz Group", "value": 310000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Garnet Eval", "account": "Garnet Solutions", "value": 330000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Beryl Trial", "account": "Beryl Ltd", "value": 575000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Coral Deploy", "account": "Coral Corp", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Diamond Start", "account": "Diamond Inc", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pearl Initial", "account": "Pearl Inc", "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Opal Expansion", "account": "Opal Ltd", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Calcite Trial", "account": "Calcite Co", "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Dolomite Quick", "account": "Dolomite Inc", "value": 205000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pixel Pilot", "account": "Pixel Corp", "value": 215000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Byte Quick", "account": "Byte LLC", "value": 225000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Atom Deploy", "account": "Atom Inc", "value": 240000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Quark Trial", "account": "Quark Co", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Arden Platform Deal", "account": "Arden Group", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Bexley Platform Deal", "account": "Bexley Group", "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorX", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-BrightPath Eval", "account": "BrightPath Co", "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Cascade RFP", "account": "Cascade Inc", "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Evergreen Bid", "account": "Evergreen LLC", "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-PeakView Proposal", "account": "PeakView Inc", "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Horizon Eval", "account": "Horizon Ltd", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Trailhead Bid", "account": "Trailhead Inc", "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-NorthStar RFP", "account": "NorthStar Co", "value": 205000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-FlintEdge Eval", "account": "FlintEdge Co", "value": 215000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Basalt Proposal", "account": "Basalt Corp", "value": 225000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-RapidScale RFP", "account": "RapidScale Co", "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-CoralReef Bid", "account": "CoralReef Inc", "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-StoneArch Eval", "account": "StoneArch Corp", "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-IronBridge RFP", "account": "IronBridge LLC", "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-NorthStar Bid", "account": "NorthStar Co", "value": 180000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Calder Platform Deal", "account": "Calder Group", "value": 190000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Dunmore Platform Deal", "account": "Dunmore Group", "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "pricing", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Clearwater Eval", "account": "Clearwater Inc", "value": 140000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-StreamLine RFP", "account": "StreamLine Co", "value": 150000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Granite RFP", "account": "Granite Inc", "value": 160000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-WildPine Eval", "account": "WildPine Ltd", "value": 170000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-GreenField Bid", "account": "GreenField Inc", "value": 185000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Eastvale Platform Deal", "account": "Eastvale Group", "value": 295000, "outcome": "lost", "competitor_lost_to": "CompetitorY", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Redwood Stall", "account": "Redwood Corp", "value": 265000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Pinecrest Delay", "account": "Pinecrest Inc", "value": 285000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Willow Hold", "account": "Willow LLC", "value": 500000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "enterprise", "deal_size_bucket": "500K+"},
    {"name": "Q2-Birchwood Pause", "account": "Birchwood Co", "value": 140000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-OakHill Delay", "account": "OakHill Partners", "value": 155000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Cedarpoint Freeze", "account": "Cedarpoint Inc", "value": 165000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Aspen Stall", "account": "Aspen Group", "value": 175000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Maple Pause", "account": "Maple Industries", "value": 190000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-ElmGrove Freeze", "account": "ElmGrove Ltd", "value": 200000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Pumice Stall", "account": "Pumice Co", "value": 210000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Sandstone Pause", "account": "Sandstone Ltd", "value": 265000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Quartzite Hold", "account": "Quartzite Corp", "value": 70000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Feldspar Delay", "account": "Feldspar Inc", "value": 75000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Mica Freeze", "account": "Mica LLC", "value": 80000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Spruce Freeze", "account": "Spruce Systems", "value": 85000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Juniper Stall", "account": "Juniper Corp", "value": 140000, "outcome": "lost", "competitor_lost_to": None, "loss_reason": "no_decision", "segment": "smb", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-PolarStar Eval", "account": "PolarStar Inc", "value": 125000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-CoastalTech RFP", "account": "CoastalTech", "value": 135000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-TideLine Eval", "account": "TideLine Corp", "value": 145000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-HarborView Bid", "account": "HarborView LLC", "value": 155000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Shale Eval", "account": "Shale Inc", "value": 165000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "100K-250K"},
    {"name": "Q2-Fairmont Platform Deal", "account": "Fairmont Group", "value": 275000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "feature_gaps", "segment": "mid-market", "deal_size_bucket": "250K-500K"},
    {"name": "Q2-Portside RFP", "account": "Portside LLC", "value": 65000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-BreakWater Bid", "account": "BreakWater Co", "value": 70000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Glenrock Platform Deal", "account": "Glenrock Group", "value": 75000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Halston Platform Deal", "account": "Halston Group", "value": 80000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Ivybridge Platform Deal", "account": "Ivybridge Group", "value": 85000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Kestrel Platform Deal", "account": "Kestrel Group", "value": 90000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "<100K"},
    {"name": "Q2-Larkspur Platform Deal", "account": "Larkspur Group", "value": 135000, "outcome": "lost", "competitor_lost_to": "CompetitorZ", "loss_reason": "pricing", "segment": "smb", "deal_size_bucket": "100K-250K"},
]

# Intervention costs and expected recovery rates
_INTERVENTIONS = {
    "security_positioning": {
        "label": "Security positioning",
        "cost": 25000,
        "recovery_rate": 0.25,
        "timeline": "Immediate",
        "actions": [
            "Lead with SOC 2 Type II (currently underutilized in sales materials)",
            "Bridge message: \"FedRAMP in progress\" with the readiness timeline",
            "Create a Security Architecture one-pager for enterprise buyers",
            "Offer the buyer's security team direct access during evaluation",
        ],
    },
    "reference_program": {
        "label": "Reference program",
        "cost": 30000,
        "recovery_rate": 0.35,
        "timeline": "30 days",
        "actions": [
            "Activate 3 enterprise customers for reference calls",
            "Produce video testimonials from enterprise logos",
            "Offer reference incentives (extended support, discounts)",
        ],
    },
    "pricing_flexibility": {
        "label": "Pricing flexibility",
        "cost": 15000,
        "recovery_rate": 0.15,
        "timeline": "Immediate",
        "actions": [
            "Enterprise tier: bundle security features at no extra cost",
            "Offer a 90-day pilot option with success-based conversion",
            "Match competitor payment-terms flexibility",
        ],
    },
    "roadmap_commitments": {
        "label": "Roadmap commitments",
        "cost": 0,
        "recovery_rate": 0.20,
        "timeline": "Next quarter",
        "actions": [
            "Share dated roadmap commitments for the top feature gaps",
            "Offer design-partner access for the missing capabilities",
        ],
    },
    "fedramp_certification": {
        "label": "FedRAMP certification",
        "cost": 85000,
        "recovery_rate": 0.0,
        "timeline": "6 months",
        "actions": [
            "Engage a FedRAMP 3PAO for the readiness assessment",
            "Target FedRAMP Moderate authorization",
        ],
    },
    "iso_certification": {
        "label": "ISO 27001",
        "cost": 25000,
        "recovery_rate": 0.0,
        "timeline": "4 months",
        "actions": [
            "Engage a certification body for the gap assessment",
            "Complete Stage 1 and Stage 2 audits",
        ],
    },
}

# Which intervention recovers which primary loss reason (one each, so no deal is counted twice).
_REASON_TO_INTERVENTION = {
    "security_certs": "security_positioning",
    "enterprise_references": "reference_program",
    "pricing": "pricing_flexibility",
    "feature_gaps": "roadmap_commitments",
}

_REASON_LABELS = {
    "security_certs": "Security certs",
    "enterprise_references": "Enterprise refs",
    "pricing": "Pricing",
    "feature_gaps": "Features",
    "no_decision": "No decision",
    "relationship": "Relationship",
}

_ADDRESSABLE = {
    "security_certs": "6 months",
    "enterprise_references": "3 months",
    "pricing": "Immediate",
    "feature_gaps": "Roadmap",
    "no_decision": "Partially (nurture)",
    "relationship": "Engagement plan",
}

_COMPETITIVE_GAP = {
    "CompetitorX": {"they_have": "FedRAMP + 12 Fortune 500 logos", "we_have": "SOC 2 + 3 refs"},
}

_FORECAST = {"q4_realization": 0.62, "focus_competitor": "CompetitorX"}


# ═══════════════════════════════════════════════════════════════
# HELPERS -- real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _whole(value):
    """Round half away from zero (16.5 -> 17), unlike Python's banker's rounding."""
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)


def _pct(value):
    """Whole-percent display, e.g. 28.3 -> '28%'."""
    return f"{_whole(value)}%"


def _millions(value):
    return f"${value / 1000000:.1f}M"


def _quarter_stats(opps):
    """Compute aggregate stats for a list of opportunities."""
    total = len(opps)
    won = [o for o in opps if o["outcome"] == "won"]
    lost = [o for o in opps if o["outcome"] == "lost"]
    win_rate = round(len(won) / max(total, 1) * 100, 1)
    avg_won_value = int(sum(o["value"] for o in won) / max(len(won), 1))
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
        "total_won_value": sum(o["value"] for o in won),
        "total_lost_value": sum(o["value"] for o in lost),
        "segments": segments,
    }


def _competitor_breakdown(opps):
    """Break down losses by competitor with counts, values and share of losses."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    competitors = {}
    for o in lost:
        comp = o["competitor_lost_to"] or "No Decision"
        if comp not in competitors:
            competitors[comp] = {"count": 0, "value": 0}
        competitors[comp]["count"] += 1
        competitors[comp]["value"] += o["value"]
    for comp in competitors:
        competitors[comp]["pct_of_losses"] = round(competitors[comp]["count"] / max(len(lost), 1) * 100, 1)
    return competitors


def _loss_reason_analysis(opps, competitor=None):
    """Loss reasons by buyer mentions (primary + secondary reason cited in the win/loss interview)."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    if competitor:
        lost = [o for o in lost if o["competitor_lost_to"] == competitor]
    reasons = {}
    for o in lost:
        cited = [o["loss_reason"]] + ([o["secondary_reason"]] if o.get("secondary_reason") else [])
        for r in cited:
            if r not in reasons:
                reasons[r] = {"mentions": 0, "deals": 0, "value": 0}
            reasons[r]["mentions"] += 1
        reasons[o["loss_reason"]]["deals"] += 1
        reasons[o["loss_reason"]]["value"] += o["value"]
    total = sum(r["mentions"] for r in reasons.values())
    for r in reasons:
        pct = round(reasons[r]["mentions"] / max(total, 1) * 100, 1)
        reasons[r]["frequency_pct"] = pct
        reasons[r]["impact"] = "High" if pct >= 25 else "Medium" if pct >= 10 else "Low"
        reasons[r]["addressable"] = _ADDRESSABLE.get(r, "Unknown")
    return reasons


def _revenue_recovery_model(opps, competitor="CompetitorX"):
    """Recoverable pipeline per intervention over the competitor's losses; one intervention per primary reason."""
    lost = [o for o in opps if o["outcome"] == "lost" and o["competitor_lost_to"] == competitor]
    projections = {}
    for reason, key in _REASON_TO_INTERVENTION.items():
        intv = _INTERVENTIONS[key]
        deals = [o for o in lost if o["loss_reason"] == reason]
        pipeline = sum(o["value"] for o in deals)
        value = int(round(pipeline * intv["recovery_rate"] / 100000.0)) * 100000
        projections[key] = {
            "label": intv["label"],
            "applicable_deals": len(deals),
            "total_pipeline": pipeline,
            "recoverable_value": value,
            "deals_recoverable": int(round(len(deals) * intv["recovery_rate"])),
            "timeline": intv["timeline"],
        }
    total_recoverable = sum(p["recoverable_value"] for p in projections.values())
    total_cost = sum(intv["cost"] for intv in _INTERVENTIONS.values())
    return projections, total_recoverable, total_cost


def _forecast(opps):
    """Q4 scenario: flat Q3 bookings plus the realizable share of the recovery; win rates from recovered deals."""
    q3 = _quarter_stats(opps)
    projections, total_recoverable, total_cost = _revenue_recovery_model(opps, _FORECAST["focus_competitor"])
    lift = int(round(total_recoverable * _FORECAST["q4_realization"] / 100000.0)) * 100000
    immediate = sum(p["deals_recoverable"] for p in projections.values() if p["timeline"] == "Immediate")
    all_deals = sum(p["deals_recoverable"] for p in projections.values())
    return {
        "current": q3["total_won_value"],
        "lift": lift,
        "with": q3["total_won_value"] + lift,
        "current_wr": q3["win_rate"],
        "q4_wr": round((q3["won"] + immediate) / q3["total"] * 100, 1),
        "q1_wr": round((q3["won"] + all_deals) / q3["total"] * 100, 1),
        "recoverable": total_recoverable,
        "cost": total_cost,
        "roi": int(total_recoverable / max(total_cost, 1)),
        "projections": projections,
    }


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
            "description": (
                f"{__manifest__['description']} Uses bundled synthetic closed-deal evidence "
                "and returns read-only analysis, draft enablement, and scenario models only. "
                "It does not change forecasts, approve investments, or claim realized revenue. "
                "Always call this tool when a sales leader asks to analyze Q3 win/loss data or why we are "
                "losing to CompetitorX, the main reasons we lose, strategies to counter CompetitorX, the revenue "
                "impact of fixing the issues, or an executive summary for a board presentation; short "
                "follow-ups ('yes, ...') continue the same analysis. "
                "Route requests to summarize all findings, session accomplishments, or candidate "
                "next steps to `action_summary`; that operation returns `Complete Summary` and "
                "`Draft Next-Step Options`."
            ),
            "operations": [
                "win_loss_overview", "root_cause_analysis", "counter_strategies",
                "revenue_impact", "board_presentation", "action_summary",
            ],
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
                        "description": (
                            "Select the requested win/loss deliverable. win_loss_overview: analyze the Q3 win/loss "
                            "data, win-rate trend and why we lose to a competitor in a segment. root_cause_analysis: "
                            "the main reasons we lose (loss drivers, buyer feedback). counter_strategies: strategies "
                            "to counter the competitor, talk track. revenue_impact: revenue impact if we fix the "
                            "issues (recoverable pipeline, ROI). board_presentation: executive summary for a board "
                            "presentation. "
                            "action_summary: REQUIRED for a complete findings summary, session "
                            "accomplishments, candidate next steps, or non-activated action recap; "
                            "returns Complete Summary and Draft Next-Step Options."
                        ),
                    },
                    "quarter": {
                        "type": "string",
                        "enum": ["Q3"],
                        "description": "Synthetic quarter to analyze. Only Q3 is supported.",
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

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "win_loss_overview")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        if kwargs.get("quarter", "Q3") != "Q3":
            return "**Error:** `quarter` must be `Q3` for the bundled synthetic evidence."
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
        output = handler()
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact deal values, counts, interview statements, "
            "rates, costs, ROI, and recovery figures are synthetic scenario evidence, not "
            "measured business results or commitments. This read-only output did not change "
            "a forecast, approve spend, publish enablement, or contact a buyer."
        )

    # ── win_loss_overview ──────────────────────────────────────
    def _win_loss_overview(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        ent3, ent2 = q3["segments"]["enterprise"]["win_rate"], q2["segments"]["enterprise"]["win_rate"]
        wr_delta = int(round(q3["win_rate"] - q2["win_rate"]))
        ent_delta = int(round(ent3 - ent2))
        comp_q3 = _competitor_breakdown(_Q3_OPPORTUNITIES)
        comp_q2 = _competitor_breakdown(_Q2_OPPORTUNITIES)
        comp_rows = ""
        for comp in sorted(comp_q3, key=lambda c: comp_q3[c]["count"], reverse=True):
            c3 = comp_q3[comp]
            c2 = comp_q2.get(comp, {"pct_of_losses": 0})
            trend_val = _whole(c3["pct_of_losses"]) - _whole(c2["pct_of_losses"])
            trend = f"Up {trend_val}%" if trend_val > 1 else (f"Down {abs(trend_val)}%" if trend_val < -1 else "Flat")
            comp_rows += f"| {comp} | {c3['count']} | {_pct(c3['pct_of_losses'])} | {trend} |\n"
        top_comp = max((c for c in comp_q3 if c != "No Decision"), key=lambda c: comp_q3[c]["count"])
        x = comp_q3[top_comp]
        x_trend = _whole(x["pct_of_losses"]) - _whole(comp_q2[top_comp]["pct_of_losses"])
        seg_table = ""
        for seg in ("enterprise", "mid-market", "smb"):
            s3, s2 = q3["segments"][seg], q2["segments"][seg]
            seg_table += f"| {seg.upper() if seg == 'smb' else seg.title()} | {_pct(s3['win_rate'])} | {_pct(s2['win_rate'])} | {int(round(s3['win_rate'] - s2['win_rate'])):+d} pts |\n"
        return (
            f"**Q3 Win/Loss Overview** - analyzed {q3['total']} Q3 opportunities: win rate dropped "
            f"{abs(wr_delta)} pts, enterprise hit hardest.\n\n"
            f"| Metric | Q3 | Q2 | Change |\n|---|---|---|---|\n"
            f"| Win rate | {_pct(q3['win_rate'])} | {_pct(q2['win_rate'])} | {wr_delta:+d} pts |\n"
            f"| Enterprise win rate | {_pct(ent3)} | {_pct(ent2)} | {ent_delta:+d} pts |\n"
            f"| Closed opportunities | {q3['total']} | {q2['total']} | {q3['total'] - q2['total']:+d} |\n\n"
            f"**Win Rate by Segment:**\n\n"
            f"| Segment | Q3 | Q2 | Change |\n|---|---|---|---|\n{seg_table}\n"
            f"**Loss by Competitor:** {top_comp} {_pct(x['pct_of_losses'])} (up {x_trend}%), "
            + ", ".join(f"{c} {_pct(comp_q3[c]['pct_of_losses'])}" for c in sorted(comp_q3, key=lambda c: comp_q3[c]["count"], reverse=True)[1:3])
            + "\n\n"
            f"| Competitor | Losses | % of Total | Trend |\n|---|---|---|---|\n{comp_rows}\n"
            f"**Pattern:** {top_comp} is winning enterprise deals with security-conscious buyers.\n\n"
            f"Next: see the root cause analysis.\n\n"
            f"Source: [CRM + Win/Loss Interviews + Competitive Intel]\n"
            f"Agents: WinLossDataAgent, PatternRecognitionAgent"
        )

    # ── root_cause_analysis ────────────────────────────────────
    def _root_cause_analysis(self):
        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"])
        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)
        ranked = sorted(reasons.items(), key=lambda kv: kv[1]["mentions"], reverse=True)
        table = ""
        for r, data in ranked:
            table += (f"| {_REASON_LABELS.get(r, r)} | {_pct(data['frequency_pct'])} | {data['impact']} | "
                      f"{data['addressable']} |\n")
        sec = [o for o in _Q3_OPPORTUNITIES if o["outcome"] == "lost" and o["competitor_lost_to"] == top_comp
               and o["loss_reason"] == "security_certs"]
        ref = [o for o in _Q3_OPPORTUNITIES if o["outcome"] == "lost" and o["competitor_lost_to"] == top_comp
               and o["loss_reason"] == "enterprise_references"]
        surveyed = min(len(sec) + len(ref), 10)
        preferred = int(surveyed * 0.8)
        gap = _COMPETITIVE_GAP.get(top_comp, {"they_have": "-", "we_have": "-"})
        return (
            f"**Root Cause Analysis - Losses to {top_comp}:** {len(ranked)} loss drivers identified - "
            f"security is the biggest gap.\n\n"
            f"| Reason | Frequency | Impact | Addressable |\n|---|---|---|---|\n{table}\n"
            f"Frequency = share of buyer-cited loss reasons in {comp[top_comp]['count']} lost deals "
            f"({sum(d['mentions'] for d in reasons.values())} reasons cited).\n\n"
            f"**Buyer Key Insight:** \"We loved the product but couldn't get past security review\" "
            f"({preferred} of {surveyed} lost buyers)\n\n"
            f"**Gap:** They have {gap['they_have']}; we have {gap['we_have']}.\n\n"
            f"- Security: {len(sec)} deals, ${sum(d['value'] for d in sec):,} pipeline\n"
            f"- References: {len(ref)} deals, ${sum(d['value'] for d in ref):,} pipeline\n\n"
            f"Next: counter-strategies.\n\n"
            f"Source: [Win/Loss Surveys + Gong Calls + Competitive Intel]\n"
            f"Agents: RootCauseAnalysisAgent, PatternRecognitionAgent"
        )

    # ── counter_strategies ─────────────────────────────────────
    def _counter_strategies(self):
        immediate = [(k, v) for k, v in _INTERVENTIONS.items() if v["timeline"] in ("Immediate", "30 days")]
        long_term = [(k, v) for k, v in _INTERVENTIONS.items() if v["timeline"] not in ("Immediate", "30 days")]
        imm = "**Immediate (This Quarter):**\n\n"
        for key, intv in immediate:
            imm += f"- **{intv['label']}** ({intv['timeline']}): " + "; ".join(intv["actions"]) + "\n"
        lt = "\n**Longer-Term:**\n\n"
        for key, intv in long_term:
            cost = f"${intv['cost']:,} investment" if intv["cost"] else "within the existing roadmap budget"
            lt += f"- {intv['label']} ({intv['timeline']}, {cost})\n"
        talk_track = (
            "\n**Talk Track:** \"Secure choice with modern UX. SOC 2 active, FedRAMP in progress. "
            "Let us connect you with 3 enterprise references.\"\n"
        )
        return (
            f"**Counter-Strategies by Driver (vs {_FORECAST['focus_competitor']}):**\n\n"
            f"{imm}{lt}{talk_track}\n"
            f"Next: see the revenue impact.\n\n"
            f"Source: [Competitive Playbook + Product Roadmap]\n"
            f"Agents: CompetitiveStrategyAgent"
        )

    # ── revenue_impact ─────────────────────────────────────────
    def _revenue_impact(self):
        f = _forecast(_Q3_OPPORTUNITIES)
        rows = ""
        for key in sorted(f["projections"], key=lambda k: f["projections"][k]["recoverable_value"], reverse=True):
            p = f["projections"][key]
            rows += (f"| {p['label']} | {_millions(p['recoverable_value'])} | {p['timeline']} | "
                     f"{p['deals_recoverable']} of {p['applicable_deals']} deals |\n")
        return (
            f"**Synthetic Revenue Scenario Model:** {_millions(f['recoverable'])} recoverable pipeline with "
            f"interventions.\n\n"
            f"| Action | Value | Timeline | Deals Recoverable |\n|---|---|---|---|\n{rows}\n"
            f"**Q4 Impact:** {_millions(f['current'])} -> {_millions(f['with'])} (+{_millions(f['lift'])}); "
            f"win rate {_pct(f['current_wr'])} -> {_pct(f['q4_wr'])} in Q4 and {_pct(f['q1_wr'])} by Q1 as the "
            f"reference program lands.\n\n"
            f"**Investment:** ${f['cost'] // 1000}K | **ROI:** {f['roi']}:1\n\n"
            f"Q4 assumes flat Q3 bookings plus {int(_FORECAST['q4_realization'] * 100)}% of the recoverable "
            f"pipeline; FedRAMP and ISO 27001 are enablers with cost only, so no deal is counted twice.\n\n"
            f"Next: build the board executive summary.\n\n"
            f"Source: [Revenue Analytics + Forecast Models]\n"
            f"Agents: RevenueImpactAgent"
        )

    # ── board_presentation ─────────────────────────────────────
    def _board_presentation(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"])
        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)
        ranked = sorted(reasons.items(), key=lambda kv: kv[1]["mentions"], reverse=True)[:3]
        f = _forecast(_Q3_OPPORTUNITIES)
        causes = ", ".join(f"{_REASON_LABELS[r]} ({_pct(d['frequency_pct'])})" for r, d in ranked)
        return (
            f"**Board Presentation: Q3 Win/Loss - Executive Summary**\n\n"
            f"| Slide | Content |\n|---|---|\n"
            f"| Challenge | Win rate {_pct(q3['win_rate'])} (down {abs(int(round(q3['win_rate'] - q2['win_rate'])))}), "
            f"{top_comp} taking {_pct(comp[top_comp]['pct_of_losses'])} of losses |\n"
            f"| Root Causes | {causes} |\n"
            f"| Plan | Security messaging now -> References in 30 days -> FedRAMP in 6 months |\n"
            f"| Ask | ${f['cost'] // 1000}K for certification + reference program |\n"
            f"| Expected | {_pct(f['q4_wr'])} Q4 win rate, {_millions(f['recoverable'])} pipeline recovery, "
            f"{f['roi']}:1 ROI |\n\n"
            f"**Decision for authorized leaders:** evaluate the synthetic ${f['cost']:,} investment scenario and "
            f"require normal approvals before any action. The summary is ready for you to share in Teams.\n\n"
            f"Source: [All Analysis Systems]\n"
            f"Agents: ExecutivePresentationAgent"
        )

    # ── action_summary ─────────────────────────────────────────
    def _action_summary(self):
        q3 = _quarter_stats(_Q3_OPPORTUNITIES)
        q2 = _quarter_stats(_Q2_OPPORTUNITIES)
        comp = _competitor_breakdown(_Q3_OPPORTUNITIES)
        top_comp = max((c for c in comp if c != "No Decision"), key=lambda c: comp[c]["count"])
        reasons = _loss_reason_analysis(_Q3_OPPORTUNITIES, competitor=top_comp)
        ranked = sorted(reasons.items(), key=lambda kv: kv[1]["mentions"], reverse=True)
        f = _forecast(_Q3_OPPORTUNITIES)
        return (
            f"**Win/Loss Analysis - Complete Summary**\n\n"
            f"| Insight | Finding |\n|---|---|\n"
            f"| Q3 win rate | {_pct(q3['win_rate'])} ({int(round(q3['win_rate'] - q2['win_rate'])):+d} pts from Q2) |\n"
            f"| Primary competitor | {top_comp} ({_pct(comp[top_comp]['pct_of_losses'])} of losses) |\n"
            f"| Biggest gap | {_REASON_LABELS[ranked[0][0]]} ({_pct(ranked[0][1]['frequency_pct'])}) |\n"
            f"| Second gap | {_REASON_LABELS[ranked[1][0]]} ({_pct(ranked[1][1]['frequency_pct'])}) |\n"
            f"| Recoverable pipeline | {_millions(f['recoverable'])} |\n\n"
            f"**Session Accomplishments:**\n"
            f"- Analyzed {q3['total']} Q3 opportunities\n"
            f"- Identified {len(ranked)} loss drivers\n"
            f"- Developed counter-strategies for each driver\n"
            f"- Modeled a {_millions(f['recoverable'])} synthetic recovery scenario\n"
            f"- Created the board executive summary\n\n"
            f"**Draft Next-Step Options:**\n"
            f"1. Review security positioning materials\n"
            f"2. Evaluate a pricing-flexibility policy with authorized approvers\n"
            f"3. Validate reference availability before any buyer contact\n"
            f"4. Review draft talk tracks with enablement leaders\n\n"
            f"**Synthetic Scenario:** the model illustrates movement from {_pct(f['current_wr'])} to "
            f"{_pct(f['q4_wr'])} in Q4 and {_pct(f['q1_wr'])} by Q1; it is not a conversion, revenue, ROI, or "
            f"forecast commitment.\n\n"
            f"Source: [All Win/Loss Systems]\n"
            f"Agents: ExecutivePresentationAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = WinLossAnalysisAgent()
    for op in agent.metadata["operations"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
