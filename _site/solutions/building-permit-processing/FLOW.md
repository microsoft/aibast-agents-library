# Building Permit Processing Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/building-permit-processing.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_BPP_01["BPP-01<br/><small>Development Services Director</small><br/><small>pain: long processing times and high citizen complaints</small>"]
    n_BPP_02["BPP-02<br/><small>Permit Technician</small><br/><small>Classify and validate permit applications at intake</small>"]
    n_BPP_03["BPP-03<br/><small>Permit Technician</small><br/><small>Route requests automatically to the correct review teams</small>"]
    n_BPP_04["BPP-04<br/><small>Customer Service Lead</small><br/><small>Centralize communication and provide instant updates to applicants</small>"]
    n_BPP_05["BPP-05<br/><small>Chief Building Inspector</small><br/><small>Provide inspectors with mobile access and real-time assignments</small>"]
    n_BPP_01 --> n_BPP_02
    n_BPP_02 --> n_BPP_03
    n_BPP_03 --> n_BPP_04
    n_BPP_04 --> n_BPP_05
```
