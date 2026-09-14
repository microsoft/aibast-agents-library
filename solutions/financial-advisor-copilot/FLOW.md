# Financial Advisor Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/financial-advisor-copilot.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_FAC_01["FAC-01: service_intake<br/><small>Branch Banker</small><br/><small>Coordinate check-in, identity verification, and service routing</small>"]
    n_FAC_02["FAC-02: client_review<br/><small>Advisory Director</small><br/><small>Guide bankers through advisory, onboarding, and transaction workflows</small>"]
    n_FAC_03["FAC-03: portfolio_summary<br/><small>Financial Advisor</small><br/><small>Surface personalized financial insights, risk assessments, and researc…</small>"]
    n_FAC_04["FAC-04: recommendation_engine<br/><small>Financial Advisor</small><br/><small>Surface personalized financial insights, risk assessments, and researc…</small>"]
    n_FAC_05["FAC-05: compliance_check<br/><small>Compliance Officer</small><br/><small>Surface personalized financial insights, risk assessments, and researc…</small>"]
    n_FAC_06["FAC-06: advisor_handoff<br/><small>Branch Banker</small><br/><small>Guide bankers through advisory, onboarding, and transaction workflows</small>"]
    n_FAC_01 --> n_FAC_02
    n_FAC_02 --> n_FAC_03
    n_FAC_03 --> n_FAC_04
    n_FAC_04 --> n_FAC_05
    n_FAC_05 --> n_FAC_06
```
