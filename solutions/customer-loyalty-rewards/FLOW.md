# Customer Loyalty and Rewards Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/customer-loyalty-rewards.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CLR_01["CLR-01: loyalty_dashboard<br/><small>Loyalty Program Director</small><br/><small>As Loyalty Program Director, summarize the synthetic program health an…</small>"]
    n_CLR_02["CLR-02: points_summary<br/><small>CRM Manager</small><br/><small>As CRM Manager, explain the synthetic Gold member balance without chan…</small>"]
    n_CLR_03["CLR-03: reward_recommendations<br/><small>Marketing Leader</small><br/><small>As Marketing Leader, show review-only reward options without creating …</small>"]
    n_CLR_04["CLR-04: tier_analysis<br/><small>Loyalty Program Director</small><br/><small>As Loyalty Program Director, review the synthetic tier structure witho…</small>"]
    n_CLR_01 --> n_CLR_02
    n_CLR_02 --> n_CLR_03
    n_CLR_03 --> n_CLR_04
```
