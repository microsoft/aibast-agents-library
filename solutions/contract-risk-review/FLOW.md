# Contract Risk Review Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/contract-risk-review.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CRR_01["CRR-01: risk_scan<br/><small>Legal Operations Director</small><br/><small>Perform comprehensive contract analysis to accelerate reviews and high…</small>"]
    n_CRR_02["CRR-02: clause_analysis<br/><small>Commercial Attorney</small><br/><small>Evaluate liability exposure and IP provisions to identify gaps and ens…</small>"]
    n_CRR_03["CRR-03: compliance_check<br/><small>Legal Operations Manager</small><br/><small>Evaluate liability exposure and IP provisions to identify gaps and ens…</small>"]
    n_CRR_04["CRR-04: renegotiation_brief<br/><small>General Counsel</small><br/><small>Recommend amendments and negotiation strategies to strengthen contract…</small>"]
    n_CRR_01 --> n_CRR_02
    n_CRR_02 --> n_CRR_03
    n_CRR_03 --> n_CRR_04
```
