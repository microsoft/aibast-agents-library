# Order Status Communications Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/order-status-communication.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_OS_01["OS-01: order_lookup<br/><small>Customer Service Representative</small><br/><small>Which orders are on track or delayed, and where should customer servic…</small>"]
    n_OS_02["OS-02: shipment_tracking<br/><small>Account Manager</small><br/><small>What shipment evidence is recorded for the shipped order, and what sti…</small>"]
    n_OS_03["OS-03: delay_notification<br/><small>Operations Leader</small><br/><small>Prepare the internal delay and recovery review for the at-risk custome…</small>"]
    n_OS_04["OS-04: customer_update<br/><small>Account Manager</small><br/><small>Draft the customer updates for approval, but do not send an email, por…</small>"]
    n_OS_01 --> n_OS_02
    n_OS_02 --> n_OS_03
    n_OS_03 --> n_OS_04
```
