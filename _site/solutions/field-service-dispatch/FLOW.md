# Field Service Dispatch Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/field-service-dispatch.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_FIELD_SERVICE_DISPATCH_01["FIELD_SERVICE_DISPATCH-01: dispatch_dashboard<br/><small>Field Operations Manager</small><br/><small>What critical Central request is unassigned right now?</small>"]
    n_FIELD_SERVICE_DISPATCH_02["FIELD_SERVICE_DISPATCH-02: route_optimization<br/><small>Service Director</small><br/><small>Compare Central zone load and capacity before anyone is rerouted.</small>"]
    n_FIELD_SERVICE_DISPATCH_03["FIELD_SERVICE_DISPATCH-03: technician_assignment<br/><small>Dispatch Coordinator</small><br/><small>Who is the best certified candidate for SR-4005? Do not assign them.</small>"]
    n_FIELD_SERVICE_DISPATCH_04["FIELD_SERVICE_DISPATCH-04: emergency_response<br/><small>Emergency Duty Manager</small><br/><small>Draft the SR-4005 response view without dispatching or notifying anyon…</small>"]
    n_FIELD_SERVICE_DISPATCH_01 --> n_FIELD_SERVICE_DISPATCH_02
    n_FIELD_SERVICE_DISPATCH_02 --> n_FIELD_SERVICE_DISPATCH_03
    n_FIELD_SERVICE_DISPATCH_03 --> n_FIELD_SERVICE_DISPATCH_04
```
