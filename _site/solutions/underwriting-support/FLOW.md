# Underwriting Support Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/underwriting-support.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_UWS_01["UWS-01: risk_evaluation<br/><small>Underwriter</small><br/><small>Analyze applications, documents, and loss history to identify key risk…</small>"]
    n_UWS_02["UWS-02: pricing_recommendation<br/><small>Pricing Analyst</small><br/><small>Generate standardized risk assessments, scoring, and pricing recommend…</small>"]
    n_UWS_03["UWS-03: guideline_check<br/><small>Risk Analyst</small><br/><small>Analyze applications, documents, and loss history to identify key risk…</small>"]
    n_UWS_04["UWS-04: exception_review<br/><small>Senior Underwriter</small><br/><small>Validate coverage structure and compliance requirements</small>"]
    n_UWS_01 --> n_UWS_02
    n_UWS_02 --> n_UWS_03
    n_UWS_03 --> n_UWS_04
```
