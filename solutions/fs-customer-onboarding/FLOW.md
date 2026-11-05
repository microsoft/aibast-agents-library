# Customer Onboarding Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/fs-customer-onboarding.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_FCO_01["FCO-01: kyc_verification<br/><small>Compliance Officer</small><br/><small>Automate identity verification, document collection, and analysis</small>"]
    n_FCO_02["FCO-02: account_setup<br/><small>Onboarding Specialist</small><br/><small>Configure accounts, treasury services, and credit facilities</small>"]
    n_FCO_03["FCO-03: document_checklist<br/><small>Relationship Manager</small><br/><small>Automate identity verification, document collection, and analysis</small>"]
    n_FCO_04["FCO-04: onboarding_status<br/><small>Head of Onboarding</small><br/><small>Gain real-time updates on client profiles and KYC processes</small>"]
    n_FCO_01 --> n_FCO_02
    n_FCO_02 --> n_FCO_03
    n_FCO_03 --> n_FCO_04
```
