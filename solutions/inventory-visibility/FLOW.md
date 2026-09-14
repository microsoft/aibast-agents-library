# Inventory Visibility Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/inventory-visibility.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_IV_01["IV-01: inventory_dashboard<br/><small>Inventory Planner</small><br/><small>As Inventory Planner, summarize the store snapshot and verification bo…</small>"]
    n_IV_02["IV-02: stock_alerts<br/><small>Store Manager</small><br/><small>As Store Manager, identify urgent review candidates without issuing tr…</small>"]
    n_IV_03["IV-03: replenishment_plan<br/><small>Inventory Planner</small><br/><small>As Inventory Planner, show the fourteen-day replenishment scenario and…</small>"]
    n_IV_04["IV-04: channel_allocation<br/><small>Category Manager</small><br/><small>As Category Manager, compare the channel planning scenario without res…</small>"]
    n_IV_01 --> n_IV_02
    n_IV_02 --> n_IV_03
    n_IV_03 --> n_IV_04
```
