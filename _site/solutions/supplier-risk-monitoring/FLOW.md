# Supply Risk Monitoring Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/supplier-risk-monitoring.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_SR_01["SR-01: risk_dashboard<br/><small>Supply Chain Director</small><br/><small>Where is supplier exposure concentrated, and which relationships shoul…</small>"]
    n_SR_02["SR-02: supplier_scorecard<br/><small>Procurement Manager</small><br/><small>Explain why TechnoCore is elevated and show me the evidence by risk di…</small>"]
    n_SR_03["SR-03: disruption_alerts<br/><small>Supply Chain Director</small><br/><small>Which recorded disruptions could threaten continuity, and what exposur…</small>"]
    n_SR_04["SR-04: alternative_sourcing<br/><small>Procurement Manager</small><br/><small>Compare backup sourcing options for review, but do not contact, qualif…</small>"]
    n_SR_01 --> n_SR_02
    n_SR_02 --> n_SR_03
    n_SR_03 --> n_SR_04
```
