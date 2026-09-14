# Win/Loss Analysis Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/win-loss-analysis.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_WL_01["WL-01: win_loss_overview<br/><small>Sales Operations Manager</small><br/><small>Perform pattern recognition and trend analysis to identify actionable …</small>"]
    n_WL_02["WL-02: root_cause_analysis<br/><small>Enablement Manager</small><br/><small>Analyze buyer feedback and loss reasons to prioritize addressable gaps…</small>"]
    n_WL_03["WL-03: counter_strategies<br/><small>Enablement Manager</small><br/><small>Generate targeted strategies and enablement content to equip teams for…</small>"]
    n_WL_04["WL-04: revenue_impact<br/><small>Sales Leader</small><br/><small>Generate targeted strategies and enablement content to equip teams for…</small>"]
    n_WL_05["WL-05: board_presentation<br/><small>Sales Leader</small><br/><small>Perform pattern recognition and trend analysis to identify actionable …</small>"]
    n_WL_06["WL-06: action_summary<br/><small>Sales Operations Manager</small><br/><small>Generate targeted strategies and enablement content to equip teams for…</small>"]
    n_WL_01 --> n_WL_02
    n_WL_02 --> n_WL_03
    n_WL_03 --> n_WL_04
    n_WL_04 --> n_WL_05
    n_WL_05 --> n_WL_06
```
