# Emissions Tracking Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/emission-tracking.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_EMISSION_TRACKING_01["EMISSION_TRACKING-01: emissions_dashboard<br/><small>Emissions Data Analyst</small><br/><small>Consolidate the Ridgeline scope totals and state the evidence limitati…</small>"]
    n_EMISSION_TRACKING_02["EMISSION_TRACKING-02: compliance_status<br/><small>Environmental Compliance Manager</small><br/><small>Screen FAC-E03 against its threshold without making a legal compliance…</small>"]
    n_EMISSION_TRACKING_03["EMISSION_TRACKING-03: reduction_plan<br/><small>Decarbonization Program Lead</small><br/><small>What reduction scenarios exist for Ridgeline and who must review them?</small>"]
    n_EMISSION_TRACKING_04["EMISSION_TRACKING-04: carbon_offset_analysis<br/><small>Sustainability Lead</small><br/><small>Show offset candidates for the Ridgeline gap, but do not buy or claim …</small>"]
    n_EMISSION_TRACKING_01 --> n_EMISSION_TRACKING_02
    n_EMISSION_TRACKING_02 --> n_EMISSION_TRACKING_03
    n_EMISSION_TRACKING_03 --> n_EMISSION_TRACKING_04
```
