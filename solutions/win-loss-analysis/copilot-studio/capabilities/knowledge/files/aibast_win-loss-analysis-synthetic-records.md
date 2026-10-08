# Win Loss Analysis Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/b2b_sales_stacks/win_loss_analysis_stack/win_loss_analysis_agent.py`
- Strict transcript evidence: `solutions/win-loss-analysis/evals/transcripts.json`
- Transcript captured at: `2026-10-07T01:30:51.992697+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_LOSS_REASONS` | 6 |
| `_COMPETITORS` | 3 |
| `_Q3_OPPORTUNITIES` | 127 |
| `_Q2_OPPORTUNITIES` | 120 |
| `_INTERVENTIONS` | 6 |
| `_REASON_TO_INTERVENTION` | 4 |
| `_REASON_LABELS` | 6 |
| `_ADDRESSABLE` | 6 |
| `_COMPETITIVE_GAP` | 1 |
| `_FORECAST` | 2 |

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
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Apex Financial Platform",
    "outcome": "won",
    "segment": "enterprise",
    "value": 330000
  },
  {
    "account": "Pinnacle Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Pinnacle Data Migration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 355000
  },
  {
    "account": "Orion Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Orion Cloud Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "Atlas Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Atlas Infra Modernization",
    "outcome": "won",
    "segment": "enterprise",
    "value": 405000
  },
  {
    "account": "Summit Enterprises",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Summit ERP Integration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 435000
  },
  {
    "account": "Crestview Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Crestview Analytics",
    "outcome": "won",
    "segment": "enterprise",
    "value": 460000
  },
  {
    "account": "Velocity Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Velocity SaaS Upgrade",
    "outcome": "won",
    "segment": "enterprise",
    "value": 485000
  },
  {
    "account": "Spark Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Spark Analytics Deal",
    "outcome": "won",
    "segment": "enterprise",
    "value": 510000
  },
  {
    "account": "Pulse Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Pulse Data Services",
    "outcome": "won",
    "segment": "enterprise",
    "value": 540000
  },
  {
    "account": "Drift Technologies",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Drift Cloud Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Zenith LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Zenith Integration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Nimbus Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Nimbus Cloud Deal",
    "outcome": "won",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Helix Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Helix SaaS Expansion",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Prism Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Prism Data Migration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "Aether Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Aether Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 205000
  },
  {
    "account": "Cirrus Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Cirrus Ops Tooling",
    "outcome": "won",
    "segment": "mid-market",
    "value": 215000
  },
  {
    "account": "Ember LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Ember Starter Pack",
    "outcome": "won",
    "segment": "mid-market",
    "value": 230000
  },
  {
    "account": "Flint Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Flint Quick Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 240000
  },
  {
    "account": "Nova Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Nova Small Biz",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Quasar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Quasar Rapid Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Photon Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Photon Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Echo Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Echo SMB Cloud",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Stratos Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Stratos Integration",
    "outcome": "won",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "Vortex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Vortex Platform",
    "outcome": "won",
    "segment": "mid-market",
    "value": 310000
  },
  {
    "account": "Matrix LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Matrix Data Suite",
    "outcome": "won",
    "segment": "smb",
    "value": 90000
  },
  {
    "account": "Dynamo Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Dynamo Cloud Ops",
    "outcome": "won",
    "segment": "smb",
    "value": 95000
  },
  {
    "account": "Warp Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Warp Speed Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 105000
  },
  {
    "account": "Comet Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Comet Expansion",
    "outcome": "won",
    "segment": "smb",
    "value": 110000
  },
  {
    "account": "Orbit Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Orbit Analytics",
    "outcome": "won",
    "segment": "smb",
    "value": 115000
  },
  {
    "account": "Luna Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Luna Starter",
    "outcome": "won",
    "segment": "smb",
    "value": 125000
  },
  {
    "account": "Astro LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Astro Mini Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 130000
  },
  {
    "account": "Cosmic Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Cosmic Quick Start",
    "outcome": "won",
    "segment": "smb",
    "value": 140000
  },
  {
    "account": "Nebula Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Nebula Cloud",
    "outcome": "won",
    "segment": "smb",
    "value": 145000
  },
  {
    "account": "Pulsar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Pulsar SMB",
    "outcome": "won",
    "segment": "smb",
    "value": 90000
  },
  {
    "account": "Pixel Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Pixel Quick Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 95000
  },
  {
    "account": "Byte LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Byte Starter Pack",
    "outcome": "won",
    "segment": "smb",
    "value": 160000
  },
  {
    "account": "TechCorp Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "TechCorp Secure Platform",
    "outcome": "lost",
    "secondary_reason": "enterprise_references",
    "segment": "enterprise",
    "value": 365000
  },
  {
    "account": "Global Banking Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "GlobalBank Core Upgrade",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 395000
  },
  {
    "account": "SecureHealth Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "SecureHealth Compliance",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 420000
  },
  {
    "account": "FedFirst Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "FedFirst Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 450000
  },
  {
    "account": "Metro Government",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Metro Gov Modernization",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 480000
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
    "account": "IronClad Defense",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "IronClad Security Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 540000
  },
  {
    "account": "Fortress Financial",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Fortress Data Vault",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 565000
  },
  {
    "account": "CipherOne",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "CipherOne Security",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 595000
  },
  {
    "account": "Radiant Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Radiant Enterprise Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 365000
  },
  {
    "account": "Cobalt Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Cobalt Security Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 395000
  },
  {
    "account": "Garnet Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Garnet Platform Upgrade",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 420000
  },
  {
    "account": "PrimeCo",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "PrimeCo Digital Transform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 450000
  },
  {
    "account": "Vantage Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Vantage Cloud Migration",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 770000
  },
  {
    "account": "Beacon Systems",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "security_certs",
    "name": "Beacon ERP Overhaul",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Titanium Holdings",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Titanium Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 300000
  },
  {
    "account": "AlphaWave",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "AlphaWave Data",
    "outcome": "lost",
    "secondary_reason": "pricing",
    "segment": "enterprise",
    "value": 275000
  },
  {
    "account": "Sapphire Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Sapphire Data Vault",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 295000
  },
  {
    "account": "Onyx Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Onyx Infra Deal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 315000
  },
  {
    "account": "QuantumEdge",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "QuantumEdge Infra",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 340000
  },
  {
    "account": "Sterling Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Sterling Cloud Services",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 360000
  },
  {
    "account": "Nexus Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Nexus Analytics Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "OmniTech Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "OmniTech Suite",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 405000
  },
  {
    "account": "SentinelOps",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "enterprise_references",
    "name": "SentinelOps Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 510000
  },
  {
    "account": "BrightPath Co",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "BrightPath Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 120000
  },
  {
    "account": "Cascade Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "Cascade Data Services",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "Evergreen LLC",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "enterprise_references",
    "name": "Evergreen SaaS Upgrade",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 230000
  },
  {
    "account": "Zenon Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "Zenon Pricing Squeeze",
    "outcome": "lost",
    "secondary_reason": "security_certs",
    "segment": "enterprise",
    "value": 645000
  },
  {
    "account": "Topaz Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "Topaz Cloud Migration",
    "outcome": "lost",
    "secondary_reason": "security_certs",
    "segment": "enterprise",
    "value": 695000
  },
  {
    "account": "Clearwater Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "Clearwater Cloud",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 750000
  },
  {
    "account": "StreamLine Co",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "StreamLine Ops",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 1310000
  },
  {
    "account": "PeakView Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "PeakView Integration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 290000
  },
  {
    "account": "Horizon Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Horizon Data Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 310000
  },
  {
    "account": "Ridgeline Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Ridgeline Cloud Suite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 335000
  },
  {
    "account": "Trailhead Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Trailhead Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 355000
  },
  {
    "account": "Summit Edge",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "Summit Edge Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 610000
  },
  {
    "account": "Jade Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Jade Analytics Platform",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 305000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "NorthStar CRM Deal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 495000
  },
  {
    "account": "WildPine Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "WildPine Integration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "CoralReef Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "CoralReef Data Migration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "StoneArch Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "StoneArch Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 195000
  },
  {
    "account": "BlueSky Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "BlueSky SaaS Renewal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 205000
  },
  {
    "account": "GreenField Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "GreenField Ops",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 355000
  },
  {
    "account": "IronBridge LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "IronBridge Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "RapidScale Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "RapidScale Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "FlintEdge Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "FlintEdge Analytics",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Basalt Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Basalt Data Migration",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "SilverLake Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "SilverLake Cloud",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Portside LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Portside Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Atom Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Atom SMB Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 215000
  },
  {
    "account": "Quark Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Quark Cloud Lite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Pearl Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Pearl Managed Services",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 235000
  },
  {
    "account": "Opal Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Opal Cloud Expansion",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Ruby Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Ruby Analytics Suite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Amber Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Amber Data Connect",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Citrine LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Citrine SaaS Deploy",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Agate Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Agate Cloud Ops",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 305000
  },
  {
    "account": "Granite Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Granite Cloud Services",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 130000
  },
  {
    "account": "Beryl Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Beryl Quick Start",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Coral Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Coral SMB Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "Diamond Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Diamond Micro Deploy",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Slate LLC",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Slate Integration Pack",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Shale Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Shale Ops Platform",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Pumice Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Pumice Cloud Suite",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Calcite Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Calcite Quick Win",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Dolomite Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Dolomite Starter",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Redwood Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Redwood Budget Freeze",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 265000
  },
  {
    "account": "Pinecrest Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Pinecrest Reorg",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 285000
  },
  {
    "account": "Willow LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Willow Delayed Decision",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "Birchwood Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": "no_decision",
    "name": "Birchwood Stall",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 540000
  },
  {
    "account": "OakHill Partners",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "OakHill Budget Hold",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "Cedarpoint Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Cedarpoint Priority Shift",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "Aspen Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Aspen Internal Conflict",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 160000
  },
  {
    "account": "Maple Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Maple Reorg Delay",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "ElmGrove Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "ElmGrove Postponed",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Spruce Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Spruce Budget Cut",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Juniper Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Juniper Priority Shift",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "CypressWood Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "CypressWood Stall",
    "outcome": "lost",
    "segment": "smb",
    "value": 65000
  },
  {
    "account": "Sandstone Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Sandstone Budget Freeze",
    "outcome": "lost",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Quartzite Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Quartzite Delay",
    "outcome": "lost",
    "segment": "smb",
    "value": 75000
  },
  {
    "account": "Feldspar Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Feldspar Reorg",
    "outcome": "lost",
    "segment": "smb",
    "value": 130000
  },
  {
    "account": "PolarStar Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "PolarStar Niche Fit",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "CoastalTech",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "CoastalTech Templates",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "TideLine Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "TideLine Industry Pack",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "HarborView LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "HarborView Vertical",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Arden Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Arden Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "Bexley Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Bexley Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "BreakWater Co",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "BreakWater Eval",
    "outcome": "lost",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Calder Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Calder Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 75000
  },
  {
    "account": "Dunmore Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Dunmore Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Eastvale Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Eastvale Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 135000
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
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Apex Expansion",
    "outcome": "won",
    "segment": "enterprise",
    "value": 350000
  },
  {
    "account": "Pinnacle Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Pinnacle Phase2",
    "outcome": "won",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "Orion Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Orion Initial",
    "outcome": "won",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Atlas Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Atlas Core",
    "outcome": "won",
    "segment": "enterprise",
    "value": 435000
  },
  {
    "account": "Summit Enterprises",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Summit Begin",
    "outcome": "won",
    "segment": "enterprise",
    "value": 465000
  },
  {
    "account": "Crestview Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Crestview Start",
    "outcome": "won",
    "segment": "enterprise",
    "value": 490000
  },
  {
    "account": "Vertex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Vertex Platform",
    "outcome": "won",
    "segment": "enterprise",
    "value": 520000
  },
  {
    "account": "Keystone Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Keystone Migration",
    "outcome": "won",
    "segment": "enterprise",
    "value": 545000
  },
  {
    "account": "Paradigm LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Paradigm Cloud",
    "outcome": "won",
    "segment": "enterprise",
    "value": 575000
  },
  {
    "account": "Milestone Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": null,
    "name": "Q2-Milestone ERP",
    "outcome": "won",
    "segment": "enterprise",
    "value": 350000
  },
  {
    "account": "Velocity Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": null,
    "name": "Q2-Velocity Start",
    "outcome": "won",
    "segment": "enterprise",
    "value": 580000
  },
  {
    "account": "Spark Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Spark Initial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
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
    "value": 165000
  },
  {
    "account": "Zenith LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Zenith Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Nimbus Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Nimbus Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Helix Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Helix Core",
    "outcome": "won",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Prism Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Prism Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Aether Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Aether Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Stratos Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Stratos Begin",
    "outcome": "won",
    "segment": "mid-market",
    "value": 235000
  },
  {
    "account": "Vortex Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Vortex Initial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Matrix LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Matrix Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Dynamo Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Dynamo Ops",
    "outcome": "won",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Cirrus Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Cirrus Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Ember LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Ember Quick",
    "outcome": "won",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Flint Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Flint Deploy",
    "outcome": "won",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Nova Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Nova Start",
    "outcome": "won",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Quasar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Quasar Pilot",
    "outcome": "won",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Photon Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Photon Trial",
    "outcome": "won",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Echo Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Echo Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 60000
  },
  {
    "account": "Orbit Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Orbit Start",
    "outcome": "won",
    "segment": "smb",
    "value": 65000
  },
  {
    "account": "Luna Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Luna Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Astro LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Astro Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Cosmic Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Cosmic Trial",
    "outcome": "won",
    "segment": "smb",
    "value": 75000
  },
  {
    "account": "Nebula Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Nebula Start",
    "outcome": "won",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Pulsar Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Pulsar Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Warp Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Warp Initial",
    "outcome": "won",
    "segment": "smb",
    "value": 90000
  },
  {
    "account": "Comet Solutions",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Comet Start",
    "outcome": "won",
    "segment": "smb",
    "value": 95000
  },
  {
    "account": "Ruby Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Ruby Start",
    "outcome": "won",
    "segment": "smb",
    "value": 60000
  },
  {
    "account": "Amber Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Amber Deploy",
    "outcome": "won",
    "segment": "smb",
    "value": 65000
  },
  {
    "account": "Citrine LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": null,
    "name": "Q2-Citrine Pilot",
    "outcome": "won",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Agate Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": null,
    "name": "Q2-Agate Quick",
    "outcome": "won",
    "segment": "smb",
    "value": 115000
  },
  {
    "account": "TechCorp Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Q2-TechCorp Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 380000
  },
  {
    "account": "Global Banking Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Q2-GlobalBank RFP",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 410000
  },
  {
    "account": "Radiant Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Q2-Radiant Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 440000
  },
  {
    "account": "Sapphire Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "security_certs",
    "name": "Q2-Sapphire Bid",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 470000
  },
  {
    "account": "Vantage Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-Vantage Initial",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 500000
  },
  {
    "account": "PrimeCo",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "security_certs",
    "name": "Q2-PrimeCo Start",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 800000
  },
  {
    "account": "SecureHealth Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-SecureHealth Phase1",
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
    "value": 310000
  },
  {
    "account": "Cobalt Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Cobalt RFP",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 335000
  },
  {
    "account": "Onyx Industries",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "enterprise_references",
    "name": "Q2-Onyx Proposal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 355000
  },
  {
    "account": "Anchor Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "enterprise_references",
    "name": "Q2-Anchor Deal",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 610000
  },
  {
    "account": "NexGen Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-NexGen Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 285000
  },
  {
    "account": "Topaz Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Topaz Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 310000
  },
  {
    "account": "Garnet Solutions",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Garnet Eval",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 330000
  },
  {
    "account": "Beryl Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "500K+",
    "loss_reason": "pricing",
    "name": "Q2-Beryl Trial",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 575000
  },
  {
    "account": "Coral Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Coral Deploy",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Diamond Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Diamond Start",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Pearl Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Pearl Initial",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Opal Ltd",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Opal Expansion",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Calcite Co",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Calcite Trial",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Dolomite Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Dolomite Quick",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 205000
  },
  {
    "account": "Pixel Corp",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Pixel Pilot",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 215000
  },
  {
    "account": "Byte LLC",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Byte Quick",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "Atom Inc",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Atom Deploy",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 240000
  },
  {
    "account": "Quark Co",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Quark Trial",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "Arden Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Arden Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Bexley Group",
    "competitor_lost_to": "CompetitorX",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Bexley Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "BrightPath Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-BrightPath Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "Cascade Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Cascade RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
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
    "account": "PeakView Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-PeakView Proposal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "Horizon Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Horizon Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Trailhead Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Trailhead Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-NorthStar RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 205000
  },
  {
    "account": "FlintEdge Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-FlintEdge Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 215000
  },
  {
    "account": "Basalt Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Basalt Proposal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 225000
  },
  {
    "account": "RapidScale Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-RapidScale RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "CoralReef Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-CoralReef Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
  },
  {
    "account": "StoneArch Corp",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-StoneArch Eval",
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
    "value": 170000
  },
  {
    "account": "NorthStar Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-NorthStar Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 180000
  },
  {
    "account": "Calder Group",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Calder Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "Dunmore Group",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "pricing",
    "name": "Q2-Dunmore Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "Clearwater Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Clearwater Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "StreamLine Co",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-StreamLine RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 150000
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
    "account": "WildPine Ltd",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-WildPine Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 170000
  },
  {
    "account": "GreenField Inc",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-GreenField Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 185000
  },
  {
    "account": "Eastvale Group",
    "competitor_lost_to": "CompetitorY",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Eastvale Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 295000
  },
  {
    "account": "Redwood Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Redwood Stall",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 265000
  },
  {
    "account": "Pinecrest Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Pinecrest Delay",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 285000
  },
  {
    "account": "Willow LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "500K+",
    "loss_reason": "no_decision",
    "name": "Q2-Willow Hold",
    "outcome": "lost",
    "segment": "enterprise",
    "value": 500000
  },
  {
    "account": "Birchwood Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Birchwood Pause",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 140000
  },
  {
    "account": "OakHill Partners",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-OakHill Delay",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Cedarpoint Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Cedarpoint Freeze",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Aspen Group",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Aspen Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 175000
  },
  {
    "account": "Maple Industries",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Maple Pause",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 190000
  },
  {
    "account": "ElmGrove Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-ElmGrove Freeze",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 200000
  },
  {
    "account": "Pumice Co",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Pumice Stall",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 210000
  },
  {
    "account": "Sandstone Ltd",
    "competitor_lost_to": null,
    "deal_size_bucket": "250K-500K",
    "loss_reason": "no_decision",
    "name": "Q2-Sandstone Pause",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 265000
  },
  {
    "account": "Quartzite Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Quartzite Hold",
    "outcome": "lost",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Feldspar Inc",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Feldspar Delay",
    "outcome": "lost",
    "segment": "smb",
    "value": 75000
  },
  {
    "account": "Mica LLC",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Mica Freeze",
    "outcome": "lost",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Spruce Systems",
    "competitor_lost_to": null,
    "deal_size_bucket": "<100K",
    "loss_reason": "no_decision",
    "name": "Q2-Spruce Freeze",
    "outcome": "lost",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Juniper Corp",
    "competitor_lost_to": null,
    "deal_size_bucket": "100K-250K",
    "loss_reason": "no_decision",
    "name": "Q2-Juniper Stall",
    "outcome": "lost",
    "segment": "smb",
    "value": 140000
  },
  {
    "account": "PolarStar Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-PolarStar Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 125000
  },
  {
    "account": "CoastalTech",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-CoastalTech RFP",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 135000
  },
  {
    "account": "TideLine Corp",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-TideLine Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 145000
  },
  {
    "account": "HarborView LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-HarborView Bid",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 155000
  },
  {
    "account": "Shale Inc",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Shale Eval",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 165000
  },
  {
    "account": "Fairmont Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "250K-500K",
    "loss_reason": "feature_gaps",
    "name": "Q2-Fairmont Platform Deal",
    "outcome": "lost",
    "segment": "mid-market",
    "value": 275000
  },
  {
    "account": "Portside LLC",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-Portside RFP",
    "outcome": "lost",
    "segment": "smb",
    "value": 65000
  },
  {
    "account": "BreakWater Co",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-BreakWater Bid",
    "outcome": "lost",
    "segment": "smb",
    "value": 70000
  },
  {
    "account": "Glenrock Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-Glenrock Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 75000
  },
  {
    "account": "Halston Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-Halston Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 80000
  },
  {
    "account": "Ivybridge Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-Ivybridge Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 85000
  },
  {
    "account": "Kestrel Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "<100K",
    "loss_reason": "pricing",
    "name": "Q2-Kestrel Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 90000
  },
  {
    "account": "Larkspur Group",
    "competitor_lost_to": "CompetitorZ",
    "deal_size_bucket": "100K-250K",
    "loss_reason": "pricing",
    "name": "Q2-Larkspur Platform Deal",
    "outcome": "lost",
    "segment": "smb",
    "value": 135000
  }
]
```

## Exact dataset `_INTERVENTIONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "fedramp_certification": {
    "actions": [
      "Engage a FedRAMP 3PAO for the readiness assessment",
      "Target FedRAMP Moderate authorization"
    ],
    "cost": 85000,
    "label": "FedRAMP certification",
    "recovery_rate": 0.0,
    "timeline": "6 months"
  },
  "iso_certification": {
    "actions": [
      "Engage a certification body for the gap assessment",
      "Complete Stage 1 and Stage 2 audits"
    ],
    "cost": 25000,
    "label": "ISO 27001",
    "recovery_rate": 0.0,
    "timeline": "4 months"
  },
  "pricing_flexibility": {
    "actions": [
      "Enterprise tier: bundle security features at no extra cost",
      "Offer a 90-day pilot option with success-based conversion",
      "Match competitor payment-terms flexibility"
    ],
    "cost": 15000,
    "label": "Pricing flexibility",
    "recovery_rate": 0.15,
    "timeline": "Immediate"
  },
  "reference_program": {
    "actions": [
      "Activate 3 enterprise customers for reference calls",
      "Produce video testimonials from enterprise logos",
      "Offer reference incentives (extended support, discounts)"
    ],
    "cost": 30000,
    "label": "Reference program",
    "recovery_rate": 0.35,
    "timeline": "30 days"
  },
  "roadmap_commitments": {
    "actions": [
      "Share dated roadmap commitments for the top feature gaps",
      "Offer design-partner access for the missing capabilities"
    ],
    "cost": 0,
    "label": "Roadmap commitments",
    "recovery_rate": 0.2,
    "timeline": "Next quarter"
  },
  "security_positioning": {
    "actions": [
      "Lead with SOC 2 Type II (currently underutilized in sales materials)",
      "Bridge message: \"FedRAMP in progress\" with the readiness timeline",
      "Create a Security Architecture one-pager for enterprise buyers",
      "Offer the buyer's security team direct access during evaluation"
    ],
    "cost": 25000,
    "label": "Security positioning",
    "recovery_rate": 0.25,
    "timeline": "Immediate"
  }
}
```

## Exact dataset `_REASON_TO_INTERVENTION`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "enterprise_references": "reference_program",
  "feature_gaps": "roadmap_commitments",
  "pricing": "pricing_flexibility",
  "security_certs": "security_positioning"
}
```

## Exact dataset `_REASON_LABELS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "enterprise_references": "Enterprise refs",
  "feature_gaps": "Features",
  "no_decision": "No decision",
  "pricing": "Pricing",
  "relationship": "Relationship",
  "security_certs": "Security certs"
}
```

## Exact dataset `_ADDRESSABLE`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "enterprise_references": "3 months",
  "feature_gaps": "Roadmap",
  "no_decision": "Partially (nurture)",
  "pricing": "Immediate",
  "relationship": "Engagement plan",
  "security_certs": "6 months"
}
```

## Exact dataset `_COMPETITIVE_GAP`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "CompetitorX": {
    "they_have": "FedRAMP + 12 Fortune 500 logos",
    "we_have": "SOC 2 + 3 refs"
  }
}
```

## Exact dataset `_FORECAST`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "focus_competitor": "CompetitorX",
  "q4_realization": 0.62
}
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
