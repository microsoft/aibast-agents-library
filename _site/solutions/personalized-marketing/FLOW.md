# Personalized Marketing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/personalized-marketing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PM_01["PM-01: customer_segmentation<br/><small>Marketing Director</small><br/><small>As Marketing Director, summarize the aggregate customer groups without…</small>"]
    n_PM_02["PM-02: campaign_design<br/><small>Campaign Manager</small><br/><small>As Campaign Manager, outline the review-only win-back sequence, assump…</small>"]
    n_PM_03["PM-03: content_personalization<br/><small>Campaign Manager</small><br/><small>As Campaign Manager, draft neutral content ideas for New Explorers and…</small>"]
    n_PM_04["PM-04: performance_analysis<br/><small>Marketing Director</small><br/><small>As Marketing Director, compare the synthetic tests and call out measur…</small>"]
    n_PM_01 --> n_PM_02
    n_PM_02 --> n_PM_03
    n_PM_03 --> n_PM_04
```
