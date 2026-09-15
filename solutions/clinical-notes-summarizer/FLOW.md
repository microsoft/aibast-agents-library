# Clinical Notes Summarizer Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/clinical-notes-summarizer.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CN_01["CN-01: encounter_summary<br/><small>Primary Care Physician</small><br/><small>Automatically generate concise, clinically relevant patient summaries</small>"]
    n_CN_02["CN-02: medication_inventory<br/><small>Anesthesia Clinician</small><br/><small>Surface key risks, comorbidities, and medication considerations</small>"]
    n_CN_03["CN-03: problem_list_extract<br/><small>Surgeon</small><br/><small>Standardize documentation to support smoother surgical and anesthesia …</small>"]
    n_CN_04["CN-04: referral_context<br/><small>Primary Care Physician</small><br/><small>Send summaries through EHR and secure messaging systems</small>"]
    n_CN_01 --> n_CN_02
    n_CN_02 --> n_CN_03
    n_CN_03 --> n_CN_04
```
