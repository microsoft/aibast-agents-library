# Win Loss Analysis Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/b2b_sales_stacks/win_loss_analysis_stack/win_loss_analysis_agent.py`
- Strict transcript evidence: `solutions/win-loss-analysis/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:43:36.334739+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_LOSS_REASONS` | 6 |
| `_COMPETITORS` | 3 |
| `_Q3_OPPORTUNITIES` | 127 |
| `_Q2_OPPORTUNITIES` | 118 |
| `_INTERVENTIONS` | 5 |

## Exact dataset `_LOSS_REASONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "security_certs",
  "enterprise_references",
  "pricing",
  "feature_gaps",
  "no_decision",
  "relationship"
]
```

## Exact dataset `_COMPETITORS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "CompetitorX": {
    "strength": "Enterprise security certs (FedRAMP, ISO 27001)",
    "weakness": "Poor UX, slow implementation"
  },
  "CompetitorY": {
    "strength": "Low price point, bundled analytics",
    "weakness": "Limited API, weak support"
  },
  "CompetitorZ": {
    "strength": "Industry-specific templates",
    "weakness": "No multi-cloud, small team"
  }
}
```

## Exact dataset `_Q3_OPPORTUNITIES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "account": "Apex Financial",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Apex Financial Platform",
    "outcome": "won",
    "segment": "enterprise",
    "value": 620000
  },
  {
    "account": "Pinnacle Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Pinnacle Data Migration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 540000
  },
  {
    "account": "Orion Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Orion Cloud Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 480000
  },
  {
    "account": "Atlas Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Atlas Infra Modernization",
    "outcome": "won",
    "segment": "enterprise",
    "value": 710000
  },
  {
    "account": "Summit Enterprises",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Summit ERP Integration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 390000
  },
  {
    "account": "Crestview Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Crestview Analytics",
    "outcome": "won",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "TechCorp Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "TechCorp Secure Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 890000
  },
  {
    "account": "Global Banking Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "GlobalBank Core Upgrade",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 780000
  },
  {
    "account": "SecureHealth Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "SecureHealth Compliance",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 650000
  },
  {
    "account": "FedFirst Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "FedFirst Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 720000
  },
  {
    "account": "Metro Government",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Metro Gov Modernization",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 580000
  },
  {
    "account": "NexGen Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "NexGen Data Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 510000
  },
  {
    "account": "PrimeCo",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "PrimeCo Digital Transform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 440000
  },
  {
    "account": "Vantage Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "enterprise_references",
    "name": "Vantage Cloud Migration",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 520000
  },
  {
    "account": "Beacon Systems",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Beacon ERP Overhaul",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 390000
  },
  {
    "account": "IronClad Defense",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "IronClad Security Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 670000
  },
  {
    "account": "Fortress Financial",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Fortress Data Vault",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 600000
  },
  {
    "account": "Titanium Holdings",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Titanium Platform Deal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 430000
  },
  {
    "account": "QuantumEdge",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "QuantumEdge Infra",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 350000
  },
  {
    "account": "Sterling Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Sterling Cloud Services",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 480000
  },
  {
    "account": "Nexus Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Nexus Analytics Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 290000
  },
  {
    "account": "OmniTech Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "OmniTech Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "CipherOne",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "CipherOne Security",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 550000
  },
  {
    "account": "AlphaWave",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "AlphaWave Data",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 420000
  },
  {
    "account": "SentinelOps",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "SentinelOps Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "BrightPath Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "BrightPath Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Cascade Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Cascade Data Services",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Evergreen LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Evergreen SaaS Upgrade",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "Clearwater Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Clearwater Cloud",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 230000
  },
  {
    "account": "StreamLine Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "StreamLine Ops",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "PeakView Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "PeakView Integration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 260000
  },
  {
    "account": "Horizon Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Horizon Data Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "Ridgeline Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Ridgeline Cloud Suite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 280000
  },
  {
    "account": "Trailhead Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Trailhead Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Summit Edge",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Summit Edge Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "NorthStar CRM Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 220000
  },
  {
    "account": "WildPine Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "WildPine Integration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "CoralReef Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "CoralReef Data Migration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "StoneArch Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "StoneArch Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 245000
  },
  {
    "account": "BlueSky Solutions",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "BlueSky SaaS Renewal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "GreenField Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "GreenField Ops",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "IronBridge LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "IronBridge Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "SilverLake Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "SilverLake Cloud",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Redwood Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Redwood Budget Freeze",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 320000
  },
  {
    "account": "Pinecrest Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Pinecrest Reorg",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Willow LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Willow Delayed Decision",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 250000
  },
  {
    "account": "Birchwood Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Birchwood Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "OakHill Partners",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "OakHill Budget Hold",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Cedarpoint Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Cedarpoint Priority Shift",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 270000
  },
  {
    "account": "Aspen Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Aspen Internal Conflict",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Maple Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Maple Reorg Delay",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 360000
  },
  {
    "account": "ElmGrove Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "ElmGrove Postponed",
    "outcome": "lost",
    "segment": "smb",
    "value": 135000
  },
  {
    "account": "Spruce Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Spruce Budget Cut",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Juniper Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Juniper Priority Shift",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "CypressWood Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "CypressWood Stall",
    "outcome": "lost",
    "segment": "smb",
    "value": 95000
  },
  {
    "account": "PolarStar Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "PolarStar Niche Fit",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "CoastalTech",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "CoastalTech Templates",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "TideLine Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "TideLine Industry Pack",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "HarborView LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "HarborView Vertical",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Anchor Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Anchor Relationship Play",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "LightHouse Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "LightHouse Legacy",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "Portside LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Portside Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 120000
  },
  {
    "account": "BreakWater Co",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "BreakWater Eval",
    "outcome": "lost",
    "segment": "smb",
    "value": 88000
  },
  {
    "account": "Velocity Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Velocity SaaS Upgrade",
    "outcome": "won",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Spark Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Spark Analytics Deal",
    "outcome": "won",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Pulse Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Pulse Data Services",
    "outcome": "won",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Drift Technologies",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Drift Cloud Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Zenith LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Zenith Integration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 120000
  },
  {
    "account": "Nimbus Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Nimbus Cloud Deal",
    "outcome": "won",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "Helix Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Helix SaaS Expansion",
    "outcome": "won",
    "segment": "mid-market",
    "value": 230000
  },
  {
    "account": "Prism Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Prism Data Migration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "Aether Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Aether Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Cirrus Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Cirrus Ops Tooling",
    "outcome": "won",
    "segment": "smb",
    "value": 92000
  },
  {
    "account": "Ember LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Ember Starter Pack",
    "outcome": "won",
    "segment": "smb",
    "value": 78000
  },
  {
    "account": "Flint Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Flint Quick Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Nova Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Nova Small Biz",
    "outcome": "won",
    "segment": "smb",
    "value": 65000
  },
  {
    "account": "Quasar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Quasar Rapid Start",
    "outcome": "won",
    "segment": "smb",
    "value": 72000
  },
  {
    "account": "Photon Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Photon Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 55000
  },
  {
    "account": "Echo Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Echo SMB Cloud",
    "outcome": "won",
    "segment": "smb",
    "value": 48000
  },
  {
    "account": "Stratos Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Stratos Integration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 260000
  },
  {
    "account": "Vortex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Vortex Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 240000
  },
  {
    "account": "Matrix LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Matrix Data Suite",
    "outcome": "won",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Dynamo Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Dynamo Cloud Ops",
    "outcome": "won",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "Warp Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Warp Speed Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Comet Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Comet Expansion",
    "outcome": "won",
    "segment": "mid-market",
    "value": 110000
  },
  {
    "account": "Orbit Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Orbit Analytics",
    "outcome": "won",
    "segment": "smb",
    "value": 98000
  },
  {
    "account": "Luna Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Luna Starter",
    "outcome": "won",
    "segment": "smb",
    "value": 42000
  },
  {
    "account": "Astro LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Astro Mini Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 58000
  },
  {
    "account": "Cosmic Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Cosmic Quick Start",
    "outcome": "won",
    "segment": "smb",
    "value": 35000
  },
  {
    "account": "Nebula Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Nebula Cloud",
    "outcome": "won",
    "segment": "smb",
    "value": 68000
  },
  {
    "account": "Pulsar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Pulsar SMB",
    "outcome": "won",
    "segment": "smb",
    "value": 46000
  },
  {
    "account": "Horizon Ent",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "relationship",
    "name": "Horizon Ent Relationship",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Meridian Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "relationship",
    "name": "Meridian Legacy Vendor",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 340000
  },
  {
    "account": "Zenon Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Zenon Pricing Squeeze",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 280000
  },
  {
    "account": "RapidScale Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "RapidScale Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Pixel Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Pixel Quick Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 52000
  },
  {
    "account": "Byte LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Byte Starter Pack",
    "outcome": "won",
    "segment": "smb",
    "value": 38000
  },
  {
    "account": "Atom Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Atom SMB Platform",
    "outcome": "won",
    "segment": "smb",
    "value": 44000
  },
  {
    "account": "Quark Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Quark Cloud Lite",
    "outcome": "won",
    "segment": "smb",
    "value": 62000
  },
  {
    "account": "Radiant Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Radiant Enterprise Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 560000
  },
  {
    "account": "Cobalt Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Cobalt Security Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 490000
  },
  {
    "account": "Sapphire Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "enterprise_references",
    "name": "Sapphire Data Vault",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 620000
  },
  {
    "account": "Topaz Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Topaz Cloud Migration",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 340000
  },
  {
    "account": "Jade Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Jade Analytics Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 275000
  },
  {
    "account": "Onyx Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Onyx Infra Deal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 385000
  },
  {
    "account": "Garnet Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Garnet Platform Upgrade",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 450000
  },
  {
    "account": "Pearl Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Pearl Managed Services",
    "outcome": "won",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "Opal Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Opal Cloud Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 420000
  },
  {
    "account": "Ruby Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Ruby Analytics Suite",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Amber Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Amber Data Connect",
    "outcome": "won",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Citrine LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Citrine SaaS Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 125000
  },
  {
    "account": "Agate Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Agate Cloud Ops",
    "outcome": "won",
    "segment": "smb",
    "value": 88000
  },
  {
    "account": "Beryl Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Beryl Quick Start",
    "outcome": "won",
    "segment": "smb",
    "value": 72000
  },
  {
    "account": "Coral Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Coral SMB Platform",
    "outcome": "won",
    "segment": "smb",
    "value": 55000
  },
  {
    "account": "Diamond Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Diamond Micro Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 42000
  },
  {
    "account": "FlintEdge Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "FlintEdge Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "Granite Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Granite Cloud Services",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Basalt Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Basalt Data Migration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 215000
  },
  {
    "account": "Slate LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "Slate Integration Pack",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Shale Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Shale Ops Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Pumice Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Pumice Cloud Suite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "Sandstone Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Sandstone Budget Freeze",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 285000
  },
  {
    "account": "Quartzite Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Quartzite Delay",
    "outcome": "lost",
    "segment": "smb",
    "value": 110000
  },
  {
    "account": "Feldspar Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Feldspar Reorg",
    "outcome": "lost",
    "segment": "smb",
    "value": 78000
  },
  {
    "account": "Mica LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Mica Postponement",
    "outcome": "lost",
    "segment": "smb",
    "value": 92000
  },
  {
    "account": "Calcite Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Calcite Quick Win",
    "outcome": "won",
    "segment": "smb",
    "value": 47000
  },
  {
    "account": "Dolomite Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Dolomite Starter",
    "outcome": "won",
    "segment": "smb",
    "value": 56000
  }
]
```

## Exact dataset `_Q2_OPPORTUNITIES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "account": "Apex Financial",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Apex Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 580000
  },
  {
    "account": "Pinnacle Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Pinnacle Phase2",
    "outcome": "won",
    "segment": "enterprise",
    "value": 490000
  },
  {
    "account": "Orion Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Orion Initial",
    "outcome": "won",
    "segment": "enterprise",
    "value": 520000
  },
  {
    "account": "Atlas Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Atlas Core",
    "outcome": "won",
    "segment": "enterprise",
    "value": 640000
  },
  {
    "account": "Summit Enterprises",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Summit Begin",
    "outcome": "won",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Crestview Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Crestview Start",
    "outcome": "won",
    "segment": "enterprise",
    "value": 350000
  },
  {
    "account": "Vertex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Vertex Platform",
    "outcome": "won",
    "segment": "enterprise",
    "value": 470000
  },
  {
    "account": "Keystone Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Keystone Migration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "Paradigm LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Paradigm Cloud",
    "outcome": "won",
    "segment": "enterprise",
    "value": 550000
  },
  {
    "account": "Milestone Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Milestone ERP",
    "outcome": "won",
    "segment": "enterprise",
    "value": 620000
  },
  {
    "account": "TechCorp Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-TechCorp Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 680000
  },
  {
    "account": "Global Banking Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-GlobalBank RFP",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 590000
  },
  {
    "account": "SecureHealth Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-SecureHealth Phase1",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 420000
  },
  {
    "account": "Vantage Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Vantage Initial",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "PrimeCo",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Q2-PrimeCo Start",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "NexGen Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-NexGen Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 290000
  },
  {
    "account": "Beacon Systems",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Beacon Proposal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 350000
  },
  {
    "account": "Velocity Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Velocity Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "Spark Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Spark Initial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Pulse Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Pulse Phase1",
    "outcome": "won",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Drift Technologies",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Drift Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "Zenith LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Zenith Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 110000
  },
  {
    "account": "Nimbus Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Nimbus Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Helix Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Helix Core",
    "outcome": "won",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Prism Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Prism Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Aether Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Aether Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Stratos Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Stratos Begin",
    "outcome": "won",
    "segment": "mid-market",
    "value": 250000
  },
  {
    "account": "Vortex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Vortex Initial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 220000
  },
  {
    "account": "Matrix LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Matrix Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Dynamo Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Dynamo Ops",
    "outcome": "won",
    "segment": "mid-market",
    "value": 260000
  },
  {
    "account": "BrightPath Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-BrightPath Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Cascade Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Cascade RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Evergreen LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Evergreen Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Clearwater Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Clearwater Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "StreamLine Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-StreamLine RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "PeakView Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-PeakView Proposal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 240000
  },
  {
    "account": "Horizon Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Horizon Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Ridgeline Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Ridgeline RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 255000
  },
  {
    "account": "Trailhead Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Trailhead Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "Summit Edge",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Q2-Summit Edge Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-NorthStar RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "Redwood Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Redwood Stall",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "Pinecrest Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Pinecrest Delay",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Willow LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Willow Hold",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 240000
  },
  {
    "account": "Birchwood Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Birchwood Pause",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "OakHill Partners",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-OakHill Delay",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 390000
  },
  {
    "account": "Cedarpoint Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Cedarpoint Freeze",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 260000
  },
  {
    "account": "Aspen Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Aspen Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Maple Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Maple Pause",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 340000
  },
  {
    "account": "ElmGrove Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-ElmGrove Freeze",
    "outcome": "lost",
    "segment": "smb",
    "value": 125000
  },
  {
    "account": "PolarStar Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-PolarStar Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "CoastalTech",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-CoastalTech RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "TideLine Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-TideLine Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "HarborView LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-HarborView Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "Anchor Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Q2-Anchor Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Cirrus Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Cirrus Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Ember LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Ember Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 72000
  },
  {
    "account": "Flint Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Flint Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Nova Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Nova Start",
    "outcome": "won",
    "segment": "smb",
    "value": 60000
  },
  {
    "account": "Quasar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Quasar Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 68000
  },
  {
    "account": "Photon Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Photon Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 50000
  },
  {
    "account": "Echo Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Echo Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 45000
  },
  {
    "account": "Orbit Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Orbit Start",
    "outcome": "won",
    "segment": "smb",
    "value": 90000
  },
  {
    "account": "Luna Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Luna Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 40000
  },
  {
    "account": "Astro LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Astro Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 55000
  },
  {
    "account": "Cosmic Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Cosmic Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 32000
  },
  {
    "account": "Nebula Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Nebula Start",
    "outcome": "won",
    "segment": "smb",
    "value": 62000
  },
  {
    "account": "Pulsar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Pulsar Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 42000
  },
  {
    "account": "Warp Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Warp Initial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "Comet Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Comet Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 105000
  },
  {
    "account": "Ruby Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Ruby Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Amber Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Amber Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Citrine LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Citrine Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 118000
  },
  {
    "account": "Agate Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Agate Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 82000
  },
  {
    "account": "Beryl Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Beryl Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 68000
  },
  {
    "account": "Coral Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Coral Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 52000
  },
  {
    "account": "Diamond Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Diamond Start",
    "outcome": "won",
    "segment": "smb",
    "value": 39000
  },
  {
    "account": "Pearl Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Pearl Initial",
    "outcome": "won",
    "segment": "enterprise",
    "value": 290000
  },
  {
    "account": "Opal Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Opal Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 400000
  },
  {
    "account": "Calcite Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Calcite Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 44000
  },
  {
    "account": "Dolomite Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Dolomite Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 52000
  },
  {
    "account": "Pixel Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Pixel Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 48000
  },
  {
    "account": "Byte LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Byte Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 35000
  },
  {
    "account": "Atom Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Atom Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 41000
  },
  {
    "account": "Quark Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Quark Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 58000
  },
  {
    "account": "Radiant Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-Radiant Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 520000
  },
  {
    "account": "Cobalt Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Cobalt RFP",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 450000
  },
  {
    "account": "Sapphire Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-Sapphire Bid",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 580000
  },
  {
    "account": "FlintEdge Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-FlintEdge Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Granite Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Granite RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Basalt Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Basalt Proposal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Shale Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Shale Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "LightHouse Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Q2-LightHouse Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Pumice Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Pumice Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 125000
  },
  {
    "account": "Sandstone Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Sandstone Pause",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 270000
  },
  {
    "account": "Quartzite Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Quartzite Hold",
    "outcome": "lost",
    "segment": "smb",
    "value": 100000
  },
  {
    "account": "Feldspar Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Feldspar Delay",
    "outcome": "lost",
    "segment": "smb",
    "value": 72000
  },
  {
    "account": "Mica LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Mica Freeze",
    "outcome": "lost",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Portside LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Portside RFP",
    "outcome": "lost",
    "segment": "smb",
    "value": 110000
  },
  {
    "account": "BreakWater Co",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-BreakWater Bid",
    "outcome": "lost",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Slate LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Slate Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "RapidScale Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-RapidScale RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "WildPine Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-WildPine Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "CoralReef Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-CoralReef Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "StoneArch Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-StoneArch Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 230000
  },
  {
    "account": "BlueSky Solutions",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "relationship",
    "name": "Q2-BlueSky RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 120000
  },
  {
    "account": "GreenField Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-GreenField Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "IronBridge LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-IronBridge RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "SilverLake Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "Q2-SilverLake Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-NorthStar Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Topaz Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Topaz Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 320000
  },
  {
    "account": "Jade Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Jade RFP",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 260000
  },
  {
    "account": "Onyx Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Onyx Proposal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 360000
  },
  {
    "account": "Garnet Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Garnet Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Meridian Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "relationship",
    "name": "Q2-Meridian Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "Spruce Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Spruce Freeze",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "Juniper Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Juniper Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "CypressWood Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-CypressWood Hold",
    "outcome": "lost",
    "segment": "smb",
    "value": 88000
  }
]
```

## Exact dataset `_INTERVENTIONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "fedramp_certification": {
    "actions": [
      "Engage FedRAMP 3PAO for readiness assessment",
      "Assign dedicated compliance engineering team",
      "Target FedRAMP Moderate authorization"
    ],
    "cost": 85000,
    "label": "FedRAMP Certification",
    "recovery_rate": 0.55,
    "timeline": "6 months"
  },
  "iso_certification": {
    "actions": [
      "Engage certification body for gap assessment",
      "Implement required ISMS controls",
      "Complete Stage 1 and Stage 2 audits"
    ],
    "cost": 25000,
    "label": "ISO 27001 Certification",
    "recovery_rate": 0.2,
    "timeline": "4 months"
  },
  "pricing_flexibility": {
    "actions": [
      "Enterprise tier: bundle security features at no extra cost",
      "Offer 90-day pilot with success-based conversion",
      "Match competitor payment terms flexibility",
      "Introduce volume discount for multi-year commits"
    ],
    "cost": 15000,
    "label": "Pricing & Packaging Adjustment",
    "recovery_rate": 0.3,
    "timeline": "Immediate"
  },
  "reference_program": {
    "actions": [
      "Activate 3 enterprise customers for reference calls",
      "Produce 2 video testimonials from Fortune 1000 logos",
      "Offer reference incentives (extended support, discounts)",
      "Build enterprise customer advisory board"
    ],
    "cost": 30000,
    "label": "Enterprise Reference Program",
    "recovery_rate": 0.4,
    "timeline": "30 days"
  },
  "security_positioning": {
    "actions": [
      "Lead with SOC 2 Type II (currently underutilized in sales materials)",
      "Create Security Architecture one-pager for enterprise buyers",
      "Offer security team direct access during evaluation period",
      "Bridge messaging: FedRAMP in progress, SOC 2 + ISO active now"
    ],
    "cost": 25000,
    "label": "Security Positioning Refresh",
    "recovery_rate": 0.35,
    "timeline": "Immediate"
  }
}
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
