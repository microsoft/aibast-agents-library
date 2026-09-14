# Cross-Selling Opportunities Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/cross-selling.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CS_01["CS-01: opportunity_scan<br/><small>Sales Operations Manager</small><br/><small>Analyze product usage trends and benchmarking gaps across accounts to …</small>"]
    n_CS_02["CS-02: product_affinity<br/><small>Enablement Manager</small><br/><small>Analyze product usage trends and benchmarking gaps across accounts to …</small>"]
    n_CS_03["CS-03: recommendation_engine<br/><small>Enablement Manager</small><br/><small>Generate prioritized opportunity lists and personalize outreach plans …</small>"]
    n_CS_04["CS-04: revenue_impact<br/><small>Sales Leader</small><br/><small>Generate prioritized opportunity lists and personalize outreach plans …</small>"]
    n_CS_01 --> n_CS_02
    n_CS_02 --> n_CS_03
    n_CS_03 --> n_CS_04
```
