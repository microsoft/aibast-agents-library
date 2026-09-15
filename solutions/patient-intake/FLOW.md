# Patient Intake and Scheduling Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/patient-intake.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PI_01["PI-01: intake_readiness<br/><small>Front Desk Staff</small><br/><small>Deliver tailored digital packets with all required pre-visit forms</small>"]
    n_PI_02["PI-02: coverage_evidence<br/><small>Patient Access Representative</small><br/><small>Verify insurance, referrals, and network status during patient intake</small>"]
    n_PI_03["PI-03: appointment_availability<br/><small>Scheduling Coordinator</small><br/><small>Ensure clinicians’ availability and readiness through up-to-date sched…</small>"]
    n_PI_04["PI-04: pre_visit_summary<br/><small>Front Desk Staff</small><br/><small>Automate intake checks and coordination to ensure patients are fully p…</small>"]
    n_PI_01 --> n_PI_02
    n_PI_02 --> n_PI_03
    n_PI_03 --> n_PI_04
```
