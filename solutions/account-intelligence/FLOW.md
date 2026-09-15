# Account Intelligence Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/account-intelligence.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_AI_01["AI-01: account_overview<br/><small>Account Executive</small><br/><small>Aggregate business intelligence to uncover sales opportunities in minu…</small>"]
    n_AI_02["AI-02: stakeholder_map<br/><small>Account Executive</small><br/><small>Perform stakeholder mapping for visibility into purchasing paths and e…</small>"]
    n_AI_03["AI-03: competitive_intel<br/><small>Sales Director</small><br/><small>Deliver competitive analysis and positioning recommendations to help s…</small>"]
    n_AI_04["AI-04: value_messaging<br/><small>Account Executive</small><br/><small>Create personalized engagement strategies to empower sellers for every…</small>"]
    n_AI_05["AI-05: risk_assessment<br/><small>Sales Director</small><br/><small>Deliver competitive analysis and positioning recommendations to help s…</small>"]
    n_AI_06["AI-06: executive_briefing<br/><small>Customer Success Manager</small><br/><small>Create personalized engagement strategies to empower sellers for every…</small>"]
    n_AI_01 --> n_AI_02
    n_AI_02 --> n_AI_03
    n_AI_03 --> n_AI_04
    n_AI_04 --> n_AI_05
    n_AI_05 --> n_AI_06
```
