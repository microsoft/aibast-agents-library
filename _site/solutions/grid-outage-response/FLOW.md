# Grid Outage Response Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/grid-outage-response.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_GOR_01["GOR-01<br/><small>Control Room Operator</small><br/><small>Detect and rank active outages by customer impact and vulnerability</small>"]
    n_GOR_02["GOR-02<br/><small>Field Dispatch Supervisor</small><br/><small>Dispatch the right crew to the highest-impact circuit first</small>"]
    n_GOR_03["GOR-03<br/><small>Control Room Operator</small><br/><small>Give every affected customer an accurate restoration estimate</small>"]
    n_GOR_04["GOR-04<br/><small>Regulatory Reporting Manager</small><br/><small>Track reliability minutes against the regulator's thresholds continuou…</small>"]
    n_GOR_01 --> n_GOR_02
    n_GOR_02 --> n_GOR_03
    n_GOR_03 --> n_GOR_04
```
