# Discount Finder Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/procurement-support.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_DISC_01["DISC-01: savings_scan<br/><small>Procurement Manager</small><br/><small>Track discounts across vendors and promotions to reveal savings opport…</small>"]
    n_DISC_02["DISC-02: time_sensitive_deals<br/><small>Category Buyer</small><br/><small>Flag time-sensitive deals and price increases to help teams capture sa…</small>"]
    n_DISC_03["DISC-03: consolidation_analysis<br/><small>Finance Director</small><br/><small>Analyze purchase timing and vendor incentives to secure favorable pric…</small>"]
    n_DISC_04["DISC-04: purchase_timing<br/><small>Category Buyer</small><br/><small>Analyze purchase timing and vendor incentives to secure favorable pric…</small>"]
    n_DISC_01 --> n_DISC_02
    n_DISC_02 --> n_DISC_03
    n_DISC_03 --> n_DISC_04
```
