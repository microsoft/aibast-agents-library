# Time Entry and Billing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/time-entry-billing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_TEB_01["TEB-01: unbilled_report<br/><small>Billing Manager</small><br/><small>Process time entries intelligently to enforce billing rules and accele…</small>"]
    n_TEB_02["TEB-02: billing_summary<br/><small>Finance Vice President</small><br/><small>Generate CFO-ready revenue recognition reports and audit trails</small>"]
    n_TEB_03["TEB-03: time_entry_audit<br/><small>Billing Compliance Lead</small><br/><small>Automate risk and compliance checks to reduce errors and maintain audi…</small>"]
    n_TEB_04["TEB-04: invoice_preparation<br/><small>Billing Manager</small><br/><small>Validate time entries and billing rules and generate invoices</small>"]
    n_TEB_05["TEB-05: dispute_resolution<br/><small>Client Finance Partner</small><br/><small>Provide dispute resolution intelligence to help protect revenue and pr…</small>"]
    n_TEB_01 --> n_TEB_02
    n_TEB_02 --> n_TEB_03
    n_TEB_03 --> n_TEB_04
    n_TEB_04 --> n_TEB_05
```
