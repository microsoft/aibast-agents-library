# Care Gap Closure Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/care-gap-closure.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CG_01["CG-01: gap_analysis<br/><small>Quality Manager</small><br/><small>Analyze quality measures and surface high-priority gaps</small>"]
    n_CG_02["CG-02: cohort_review<br/><small>Care Coordinator</small><br/><small>Stratify outreach based on risk, condition severity, and engagement</small>"]
    n_CG_03["CG-03: outreach_draft<br/><small>Care Coordinator</small><br/><small>Launch targeted multi-channel outreach campaigns with real-time progre…</small>"]
    n_CG_04["CG-04: quality_dashboard<br/><small>Clinical Operations Lead</small><br/><small>Analyze care gaps to surface priority measures</small>"]
    n_CG_01 --> n_CG_02
    n_CG_02 --> n_CG_03
    n_CG_03 --> n_CG_04
```
