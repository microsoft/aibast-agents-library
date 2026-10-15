# Resource Utilization Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/resource-utilization.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_RU_01["RU-01: utilization_dashboard<br/><small>Operations Leader</small><br/><small>Implement real-time utilization tracking and capacity analysis</small>"]
    n_RU_02["RU-02: capacity_forecast<br/><small>Resource Manager</small><br/><small>Analyze workforce skills and availability to identify deployment gaps …</small>"]
    n_RU_03["RU-03: bench_analysis<br/><small>Finance Director</small><br/><small>Analyze workforce skills and availability to identify deployment gaps …</small>"]
    n_RU_04["RU-04: staffing_recommendation<br/><small>Resource Manager</small><br/><small>Match consultants to pipeline projects and innovation initiatives for …</small>"]
    n_RU_05["RU-05: workforce_plan<br/><small>Operations Leader</small><br/><small>Model upskilling ROI and implement strategic workforce planning to ali…</small>"]
    n_RU_01 --> n_RU_02
    n_RU_02 --> n_RU_03
    n_RU_03 --> n_RU_04
    n_RU_04 --> n_RU_05
```
