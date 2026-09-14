# Portfolio Rebalancing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/portfolio-rebalancing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PRB_01["PRB-01: portfolio_analysis<br/><small>Portfolio Manager</small><br/><small>Detect portfolio drift and analyze risk to keep client portfolios alig…</small>"]
    n_PRB_02["PRB-02: rebalance_recommendation<br/><small>Financial Advisor</small><br/><small>Detect portfolio drift and analyze risk to keep client portfolios alig…</small>"]
    n_PRB_03["PRB-03: tax_impact<br/><small>Paraplanner</small><br/><small>Find tax-loss harvesting opportunities to maximize returns and minimiz…</small>"]
    n_PRB_04["PRB-04: tax_loss_harvest<br/><small>Tax-Aware Portfolio Manager</small><br/><small>Find tax-loss harvesting opportunities to maximize returns and minimiz…</small>"]
    n_PRB_05["PRB-05: retirement_scenario<br/><small>Retirement Planning Specialist</small><br/><small>Generate rebalancing plans and model retirement success outcomes</small>"]
    n_PRB_06["PRB-06: execution_plan<br/><small>Trading Supervisor</small><br/><small>Generate rebalancing plans and model retirement success outcomes</small>"]
    n_PRB_01 --> n_PRB_02
    n_PRB_02 --> n_PRB_03
    n_PRB_03 --> n_PRB_04
    n_PRB_04 --> n_PRB_05
    n_PRB_05 --> n_PRB_06
```
