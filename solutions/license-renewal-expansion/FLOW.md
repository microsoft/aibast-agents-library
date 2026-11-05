# License Renewal and Expansion Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/license-renewal-expansion.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_LRE_01["LRE-01: renewal_pipeline<br/><small>Sales Leadership</small><br/><small>Assess account health and usage signals for targeted, proactive renewa…</small>"]
    n_LRE_02["LRE-02: expansion_opportunities<br/><small>Account Executive</small><br/><small>Generate optimized renewal pricing and packaging so teams can close de…</small>"]
    n_LRE_03["LRE-03: churn_risk<br/><small>Customer Success Manager</small><br/><small>Identify competitive threats and switching costs to support negotiatio…</small>"]
    n_LRE_04["LRE-04: revenue_impact<br/><small>Sales Leadership</small><br/><small>Streamlines subscription renewal management and expansion planning, tu…</small>"]
    n_LRE_01 --> n_LRE_02
    n_LRE_02 --> n_LRE_03
    n_LRE_03 --> n_LRE_04
```
