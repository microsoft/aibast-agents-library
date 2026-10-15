# Omnichannel Engagement Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/omnichannel-engagement.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_OCE_01["OCE-01: channel_performance<br/><small>Customer Experience Leader</small><br/><small>As Customer Experience Leader, compare the aggregate channel picture a…</small>"]
    n_OCE_02["OCE-02: journey_analysis<br/><small>Contact Center Supervisor</small><br/><small>As Contact Center Supervisor, identify handoff friction across the agg…</small>"]
    n_OCE_03["OCE-03: engagement_optimization<br/><small>Digital Engagement Manager</small><br/><small>As Digital Engagement Manager, propose consent-aware experiments with …</small>"]
    n_OCE_04["OCE-04: campaign_attribution<br/><small>Digital Engagement Manager</small><br/><small>As Digital Engagement Manager, summarize the synthetic attribution vie…</small>"]
    n_OCE_01 --> n_OCE_02
    n_OCE_02 --> n_OCE_03
    n_OCE_03 --> n_OCE_04
```
