# Fraud Detection and Alert Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/fraud-detection-alert.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_FDA_01["FDA-01: alert_triage<br/><small>Fraud Operations Manager</small><br/><small>Monitor transactions in real time to flag suspicious activity across a…</small>"]
    n_FDA_02["FDA-02: transaction_analysis<br/><small>Fraud Analyst</small><br/><small>Monitor transactions in real time to flag suspicious activity across a…</small>"]
    n_FDA_03["FDA-03: pattern_detection<br/><small>SIU Investigator</small><br/><small>Detect fraud patterns and rings to limit combined exposure and losses</small>"]
    n_FDA_04["FDA-04: investigation_summary<br/><small>Risk Leader</small><br/><small>Automate case creation and protective actions to accelerate investigat…</small>"]
    n_FDA_01 --> n_FDA_02
    n_FDA_02 --> n_FDA_03
    n_FDA_03 --> n_FDA_04
```
