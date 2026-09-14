# Deal Progression Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/deal-progression.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_DP_01["DP-01: pipeline_health<br/><small>Sales Director</small><br/><small>Perform proactive pipeline analysis to improve forecast confidence</small>"]
    n_DP_02["DP-02: stalled_deals<br/><small>Account Executive</small><br/><small>Detect stalled deals to reduce slippage and protect revenue commitment…</small>"]
    n_DP_03["DP-03: action_plans<br/><small>Account Executive</small><br/><small>Generate action plans that accelerate deal progress and improve close …</small>"]
    n_DP_04["DP-04: acceleration<br/><small>Sales Director</small><br/><small>Generate action plans that accelerate deal progress and improve close …</small>"]
    n_DP_05["DP-05: assign_tasks<br/><small>Sales Director</small><br/><small>Generate action plans that accelerate deal progress and improve close …</small>"]
    n_DP_06["DP-06: executive_summary<br/><small>Sales Director</small><br/><small>Perform proactive pipeline analysis to improve forecast confidence</small>"]
    n_DP_01 --> n_DP_02
    n_DP_02 --> n_DP_03
    n_DP_03 --> n_DP_04
    n_DP_04 --> n_DP_05
    n_DP_05 --> n_DP_06
```
