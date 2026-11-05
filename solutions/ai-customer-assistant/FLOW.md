# Customer Escalations Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/ai-customer-assistant.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CES_01["CES-01: handle_inquiry<br/><small>Back-Office Agent</small><br/><small>Perform real-time inquiry analysis from full customer context to speed…</small>"]
    n_CES_02["CES-02: knowledge_search<br/><small>Back-Office Agent</small><br/><small>Recommend resolutions aligned to policies, case studies, and playbooks…</small>"]
    n_CES_03["CES-03: escalation_routing<br/><small>Escalation Manager</small><br/><small>Recommend resolutions aligned to policies, case studies, and playbooks…</small>"]
    n_CES_04["CES-04: satisfaction_survey<br/><small>Quality Analyst</small><br/><small>Perform real-time inquiry analysis from full customer context to speed…</small>"]
    n_CES_01 --> n_CES_02
    n_CES_02 --> n_CES_03
    n_CES_03 --> n_CES_04
```
