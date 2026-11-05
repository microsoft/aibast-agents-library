# Returns and Complaints Resolution Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/returns-complaints-resolution.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_RCR_01["RCR-01: return_processing<br/><small>Customer Service Agent</small><br/><small>As Customer Service Agent, summarize the anonymous return review evide…</small>"]
    n_RCR_02["RCR-02: complaint_classification<br/><small>Customer Service Agent</small><br/><small>As Customer Service Agent, classify this product concern without echoi…</small>"]
    n_RCR_03["RCR-03: resolution_recommendation<br/><small>Customer Service Agent</small><br/><small>As Customer Service Agent, draft a policy-grounded option and keep all…</small>"]
    n_RCR_04["RCR-04: trend_analysis<br/><small>Quality Team</small><br/><small>As Quality Team, summarize aggregate defect and return patterns withou…</small>"]
    n_RCR_01 --> n_RCR_02
    n_RCR_02 --> n_RCR_03
    n_RCR_03 --> n_RCR_04
```
