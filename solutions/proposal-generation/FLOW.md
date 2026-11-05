# Proposal Generation Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/proposal-generation.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PG_01["PG-01: analyze_rfp<br/><small>Bid Manager</small><br/><small>Perform rapid RFP analysis and requirement extraction to reduce risk a…</small>"]
    n_PG_02["PG-02: executive_summary<br/><small>Account Executive</small><br/><small>Assemble personalized proposal content and positioning to strengthen d…</small>"]
    n_PG_03["PG-03: solution_pricing<br/><small>Sales Leader</small><br/><small>Generate branded, professional proposal materials for same-day deliver…</small>"]
    n_PG_04["PG-04: references_positioning<br/><small>Bid Manager</small><br/><small>Assemble personalized proposal content and positioning to strengthen d…</small>"]
    n_PG_05["PG-05: compile_proposal<br/><small>Bid Manager</small><br/><small>Generate branded, professional proposal materials for same-day deliver…</small>"]
    n_PG_06["PG-06: delivery_summary<br/><small>Sales Leader</small><br/><small>Generate branded, professional proposal materials for same-day deliver…</small>"]
    n_PG_01 --> n_PG_02
    n_PG_02 --> n_PG_03
    n_PG_03 --> n_PG_04
    n_PG_04 --> n_PG_05
    n_PG_05 --> n_PG_06
```
