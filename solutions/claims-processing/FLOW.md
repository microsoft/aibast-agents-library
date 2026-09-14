# Claims Processing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/claims-processing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CLP_01["CLP-01: claim_intake<br/><small>Claims Operations Leader</small><br/><small>Triage claims instantly to accelerate routing and reduce adjuster work…</small>"]
    n_CLP_02["CLP-02: adjudication_review<br/><small>Claims Adjuster</small><br/><small>Pre-prepare complex claim files to give adjusters ready-to-review summ…</small>"]
    n_CLP_03["CLP-03: fraud_flag<br/><small>SIU Investigator</small><br/><small>Spot fraud indicators early to prevent exposure and protect claim payo…</small>"]
    n_CLP_04["CLP-04: settlement_recommendation<br/><small>Claims Manager</small><br/><small>Auto-adjudicate simple claims to shorten cycle times and improve consi…</small>"]
    n_CLP_01 --> n_CLP_02
    n_CLP_02 --> n_CLP_03
    n_CLP_03 --> n_CLP_04
```
