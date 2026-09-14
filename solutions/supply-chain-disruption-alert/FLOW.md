# Supply Chain Disruption Alert Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/supply-chain-disruption-alert.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_01["SUPPLY_CHAIN_DISRUPTION_ALERT-01: disruption_dashboard<br/><small>Customer Fulfillment Lead</small><br/><small>Which active disruption has the largest modeled impact and what is aff…</small>"]
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_02["SUPPLY_CHAIN_DISRUPTION_ALERT-02: risk_assessment<br/><small>Supply Chain Planner</small><br/><small>Why is RT-APAC-01 high risk?</small>"]
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_03["SUPPLY_CHAIN_DISRUPTION_ALERT-03: mitigation_plan<br/><small>Operations Leader</small><br/><small>Draft a DISR-002 mitigation scenario without rerouting or moving inven…</small>"]
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_04["SUPPLY_CHAIN_DISRUPTION_ALERT-04: supplier_alternatives<br/><small>Procurement Manager</small><br/><small>Show Electronics alternatives without activating a supplier.</small>"]
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_01 --> n_SUPPLY_CHAIN_DISRUPTION_ALERT_02
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_02 --> n_SUPPLY_CHAIN_DISRUPTION_ALERT_03
    n_SUPPLY_CHAIN_DISRUPTION_ALERT_03 --> n_SUPPLY_CHAIN_DISRUPTION_ALERT_04
```
