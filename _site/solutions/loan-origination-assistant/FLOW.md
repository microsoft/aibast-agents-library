# Loan Origination Assistant — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/loan-origination-assistant.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_LOA_01["LOA-01: application_review<br/><small>Loan Officer</small><br/><small>Automate intake to standardize process and reduce manual processing</small>"]
    n_LOA_02["LOA-02: credit_analysis<br/><small>Underwriter</small><br/><small>Assess program eligibility to accelerate and support better borrowing …</small>"]
    n_LOA_03["LOA-03: document_verification<br/><small>Processor</small><br/><small>Automate intake to standardize process and reduce manual processing</small>"]
    n_LOA_04["LOA-04: decision_recommendation<br/><small>Senior Underwriter</small><br/><small>Assess program eligibility to accelerate and support better borrowing …</small>"]
    n_LOA_05["LOA-05: condition_tracking<br/><small>Closing Coordinator</small><br/><small>Track conditions and timelines to speed closing and minimize delays</small>"]
    n_LOA_01 --> n_LOA_02
    n_LOA_02 --> n_LOA_03
    n_LOA_03 --> n_LOA_04
    n_LOA_04 --> n_LOA_05
```
