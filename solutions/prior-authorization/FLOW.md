# Prior Authorization Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/prior-authorization.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PA_01["PA-01: request_evidence<br/><small>Utilization Management Coordinator</small><br/><small>Compile the full clinical evidence packet needed for medical review</small>"]
    n_PA_02["PA-02: criteria_evidence<br/><small>Nurse Case Manager</small><br/><small>Pull payer-specific requirements and match them with EHR data</small>"]
    n_PA_03["PA-03: status_summary<br/><small>Radiology Scheduler</small><br/><small>Submit requests directly to payer portals and send real-time updates</small>"]
    n_PA_04["PA-04: appeal_evidence_packet<br/><small>Utilization Management Coordinator</small><br/><small>Prepare appeal materials proactively</small>"]
    n_PA_01 --> n_PA_02
    n_PA_02 --> n_PA_03
    n_PA_03 --> n_PA_04
```
