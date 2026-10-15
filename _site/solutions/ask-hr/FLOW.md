# Ask HR Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/ask-hr.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_HR_01["HR-01: leave_balance<br/><small>Employee</small><br/><small>Provides personalized, policy-based answers to reduce inquiry volume v…</small>"]
    n_HR_02["HR-02: submit_time_off<br/><small>Employee</small><br/><small>Automates core HR transactions like time-off requests to reduce operat…</small>"]
    n_HR_03["HR-03: parental_leave<br/><small>Employee</small><br/><small>Provides personalized, policy-based answers to reduce inquiry volume v…</small>"]
    n_HR_04["HR-04: health_insurance<br/><small>Employee</small><br/><small>Provides personalized, policy-based answers to reduce inquiry volume v…</small>"]
    n_HR_05["HR-05: remote_work<br/><small>Manager</small><br/><small>Provides personalized, policy-based answers to reduce inquiry volume v…</small>"]
    n_HR_06["HR-06: benefits_summary<br/><small>HR Operations Specialist</small><br/><small>Provides personalized, policy-based answers to reduce inquiry volume v…</small>"]
    n_HR_01 --> n_HR_02
    n_HR_02 --> n_HR_03
    n_HR_03 --> n_HR_04
    n_HR_04 --> n_HR_05
    n_HR_05 --> n_HR_06
```
