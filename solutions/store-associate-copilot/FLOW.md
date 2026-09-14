# Retail Store Associate Copilot — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/store-associate-copilot.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_SA_01["SA-01: product_lookup<br/><small>Store Associate</small><br/><small>As Store Associate, give me the product facts, floor location, optiona…</small>"]
    n_SA_02["SA-02: customer_assist<br/><small>Store Associate</small><br/><small>As Store Associate, draft respectful language for acknowledging a comp…</small>"]
    n_SA_03["SA-03: task_checklist<br/><small>Floor Specialist</small><br/><small>As Floor Specialist, turn the opening work into a prioritized planning…</small>"]
    n_SA_04["SA-04: performance_dashboard<br/><small>Sales Manager</small><br/><small>As Sales Manager, summarize aggregate role-cohort coaching signals wit…</small>"]
    n_SA_01 --> n_SA_02
    n_SA_02 --> n_SA_03
    n_SA_03 --> n_SA_04
```
