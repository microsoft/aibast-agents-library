# Procurement Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/procurement-agent.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PROC_01["PROC-01: purchase_request<br/><small>Procurement Manager</small><br/><small>Automate purchase order creation and approval workflows to reduce cycl…</small>"]
    n_PROC_02["PROC-02: vendor_comparison<br/><small>Category Buyer</small><br/><small>Perform intelligent vendor analysis to optimize supplier selection, co…</small>"]
    n_PROC_03["PROC-03: approval_routing<br/><small>Department Approver</small><br/><small>Automate purchase order creation and approval workflows to reduce cycl…</small>"]
    n_PROC_04["PROC-04: spend_analysis<br/><small>Finance Director</small><br/><small>Deliver real-time spend analytics to identify savings opportunities an…</small>"]
    n_PROC_01 --> n_PROC_02
    n_PROC_02 --> n_PROC_03
    n_PROC_03 --> n_PROC_04
```
