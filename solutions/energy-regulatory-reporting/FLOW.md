# Regulatory Reporting Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/energy-regulatory-reporting.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_ENERGY_REGULATORY_REPORTING_01["ENERGY_REGULATORY_REPORTING-01: report_status<br/><small>Regulatory Reporting Lead</small><br/><small>Which filing is overdue and who owns it?</small>"]
    n_ENERGY_REGULATORY_REPORTING_02["ENERGY_REGULATORY_REPORTING-02: data_validation<br/><small>Data Analyst</small><br/><small>Which report data is incomplete or below quality threshold?</small>"]
    n_ENERGY_REGULATORY_REPORTING_03["ENERGY_REGULATORY_REPORTING-03: submission_tracker<br/><small>Compliance Manager</small><br/><small>Show filing state and confirm you did not transmit anything.</small>"]
    n_ENERGY_REGULATORY_REPORTING_04["ENERGY_REGULATORY_REPORTING-04: audit_readiness<br/><small>Internal Auditor</small><br/><small>What high-severity reporting evidence is still open?</small>"]
    n_ENERGY_REGULATORY_REPORTING_01 --> n_ENERGY_REGULATORY_REPORTING_02
    n_ENERGY_REGULATORY_REPORTING_02 --> n_ENERGY_REGULATORY_REPORTING_03
    n_ENERGY_REGULATORY_REPORTING_03 --> n_ENERGY_REGULATORY_REPORTING_04
```
