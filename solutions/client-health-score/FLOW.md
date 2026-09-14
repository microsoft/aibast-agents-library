# Client Health Score Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/client-health-score.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CHS_01["CHS-01: health_dashboard<br/><small>Client Success Leader</small><br/><small>Perform predictive health scoring to identify risks early and enable p…</small>"]
    n_CHS_02["CHS-02: engagement_analysis<br/><small>Account Manager</small><br/><small>Detect at-risk accounts to prevent churn and protect high-value client…</small>"]
    n_CHS_03["CHS-03: satisfaction_trend<br/><small>Client Experience Director</small><br/><small>Identify relationship opportunities and improve client satisfaction</small>"]
    n_CHS_04["CHS-04: at_risk_clients<br/><small>Client Success Leader</small><br/><small>Detect at-risk accounts to prevent churn and protect high-value client…</small>"]
    n_CHS_05["CHS-05: retention_plan<br/><small>Account Manager</small><br/><small>Automate retention planning to restore satisfaction and strengthen exe…</small>"]
    n_CHS_01 --> n_CHS_02
    n_CHS_02 --> n_CHS_03
    n_CHS_03 --> n_CHS_04
    n_CHS_04 --> n_CHS_05
```
