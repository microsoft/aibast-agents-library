# Maintenance Scheduling Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/maintenance-scheduling.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_MS_01["MS-01: schedule_overview<br/><small>Maintenance Manager</small><br/><small>Give me the equipment and technician-capacity picture I should review …</small>"]
    n_MS_02["MS-02: predictive_alerts<br/><small>Production Supervisor</small><br/><small>Which asset signals deserve immediate human review before the next pro…</small>"]
    n_MS_03["MS-03: work_order_plan<br/><small>Maintenance Manager</small><br/><small>Draft the maintenance candidates with crew, parts, and backup checks, …</small>"]
    n_MS_04["MS-04: downtime_analysis<br/><small>Operations Leader</small><br/><small>What synthetic downtime exposure and preventive trade-offs should lead…</small>"]
    n_MS_01 --> n_MS_02
    n_MS_02 --> n_MS_03
    n_MS_03 --> n_MS_04
```
