# Inventory Rebalancing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/inventory-rebalancing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_IR_01["IR-01: inventory_snapshot<br/><small>Supply Chain Manager</small><br/><small>Which distribution centers are tight on space, and which SKU positions…</small>"]
    n_IR_02["IR-02: rebalance_recommendation<br/><small>Inventory Manager</small><br/><small>Where do we have forecast-relative shortages or excess that deserve a …</small>"]
    n_IR_03["IR-03: transfer_plan<br/><small>Supply Chain Manager</small><br/><small>Show me the proposed warehouse moves, but do not move or reserve anyth…</small>"]
    n_IR_04["IR-04: cost_analysis<br/><small>Procurement Manager</small><br/><small>Where is inventory exposure concentrated, and what trade-offs should I…</small>"]
    n_IR_01 --> n_IR_02
    n_IR_02 --> n_IR_03
    n_IR_03 --> n_IR_04
```
