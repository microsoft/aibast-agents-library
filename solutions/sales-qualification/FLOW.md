# Sales Qualification Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/sales-qualification.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_SQ_01["SQ-01: score_leads<br/><small>Sales Manager</small><br/><small>Perform intelligent lead enrichment to prioritize high-potential oppor…</small>"]
    n_SQ_02["SQ-02: bant_analysis<br/><small>Business Development Rep.</small><br/><small>Automate qualification scoring to identify conversion-ready prospects</small>"]
    n_SQ_03["SQ-03: create_outreach<br/><small>Business Development Rep.</small><br/><small>Generate personalized outreach sequences to boost engagement</small>"]
    n_SQ_04["SQ-04: assign_leads<br/><small>Sales Manager</small><br/><small>Coordinate SLA-based assignments and tracking to drive timely engageme…</small>"]
    n_SQ_05["SQ-05: setup_tracking<br/><small>Sales Manager</small><br/><small>Coordinate SLA-based assignments and tracking to drive timely engageme…</small>"]
    n_SQ_06["SQ-06: qualification_report<br/><small>Account Executive</small><br/><small>Automate qualification scoring to identify conversion-ready prospects</small>"]
    n_SQ_01 --> n_SQ_02
    n_SQ_02 --> n_SQ_03
    n_SQ_03 --> n_SQ_04
    n_SQ_04 --> n_SQ_05
    n_SQ_05 --> n_SQ_06
```
