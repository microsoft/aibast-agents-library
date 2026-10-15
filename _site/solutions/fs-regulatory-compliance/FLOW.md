# Regulatory Compliance Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/fs-regulatory-compliance.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_RC_01["RC-01<br/><small>Chief Compliance Officer</small><br/><small>pain: manual review created delays and increased audit risk</small>"]
    n_RC_02["RC-02<br/><small>Trading Desk Supervisor</small><br/><small>Identify upcoming certification expirations and enroll traders</small>"]
    n_RC_03["RC-03<br/><small>Compliance Manager</small><br/><small>Scan all executed trades for reporting accuracy, required fields, and …</small>"]
    n_RC_04["RC-04<br/><small>Head of Quant Execution</small><br/><small>Flag missing or outdated documentation</small>"]
    n_RC_05["RC-05<br/><small>Chief Risk Officer</small><br/><small>Automate corrections and submissions to the regulatory portal</small>"]
    n_RC_01 --> n_RC_02
    n_RC_02 --> n_RC_03
    n_RC_03 --> n_RC_04
    n_RC_04 --> n_RC_05
```
