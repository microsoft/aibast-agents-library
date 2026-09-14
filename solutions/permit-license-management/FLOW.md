# Permit Management Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/permit-license-management.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PERMIT_LICENSE_MANAGEMENT_01["PERMIT_LICENSE_MANAGEMENT-01: permit_inventory<br/><small>Facility Manager</small><br/><small>Which Riverside permit is expired right now?</small>"]
    n_PERMIT_LICENSE_MANAGEMENT_02["PERMIT_LICENSE_MANAGEMENT-02: renewal_calendar<br/><small>Permit Coordinator</small><br/><small>What is the next Riverside renewal deadline I need to prepare for?</small>"]
    n_PERMIT_LICENSE_MANAGEMENT_03["PERMIT_LICENSE_MANAGEMENT-03: compliance_gaps<br/><small>Compliance Manager</small><br/><small>What permit evidence gap needs immediate authorized review at Riversid…</small>"]
    n_PERMIT_LICENSE_MANAGEMENT_04["PERMIT_LICENSE_MANAGEMENT-04: application_status<br/><small>Environmental Counsel</small><br/><small>Where does the Riverside gas turbine permit application stand, and did…</small>"]
    n_PERMIT_LICENSE_MANAGEMENT_01 --> n_PERMIT_LICENSE_MANAGEMENT_02
    n_PERMIT_LICENSE_MANAGEMENT_02 --> n_PERMIT_LICENSE_MANAGEMENT_03
    n_PERMIT_LICENSE_MANAGEMENT_03 --> n_PERMIT_LICENSE_MANAGEMENT_04
```
