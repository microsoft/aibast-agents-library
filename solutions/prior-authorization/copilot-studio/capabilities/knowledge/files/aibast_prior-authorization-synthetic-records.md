# Prior Authorization Agent — complete synthetic records

> **Fictional demonstration data only.** These records reproduce the deterministic `PriorAuthorizationAgent`. They are not real payer policy, eligibility, medical-necessity, or authorization evidence.

## Synthetic request: SYN-AUTH-001

- **Service:** synthetic knee imaging request
- **Payer in synthetic source:** Synthetic Health Plan
- **Source-recorded workflow state:** additional evidence requested
- **Source date:** 2026-07-30
- **Referenced policy:** SYN-POL-IMG-01
- **Evidence — encounter note:** present
- **Evidence — prior imaging report:** present
- **Evidence — conservative-care duration:** not found in synthetic source

## Synthetic request: SYN-AUTH-002

- **Service:** synthetic outpatient procedure request
- **Payer in synthetic source:** Synthetic Community Plan
- **Source-recorded workflow state:** payer response recorded
- **Source date:** 2026-07-31
- **Referenced policy:** SYN-POL-PROC-02
- **Evidence — encounter note:** present
- **Evidence — specialist note:** present
- **Evidence — current payer policy confirmation:** requires human review

## Fictional policy: SYN-POL-IMG-01

- **Title:** Synthetic Imaging Evidence Checklist
- **Synthetic effective date:** 2026-07-01
- **Reviewer checks, in order:** relevant encounter note; prior imaging evidence; documented duration fields

## Fictional policy: SYN-POL-PROC-02

- **Title:** Synthetic Procedure Evidence Checklist
- **Synthetic effective date:** 2026-07-01
- **Reviewer checks, in order:** relevant encounter note; specialist documentation; current policy version

These are fictional checklists. Presence of a listed item does not establish medical necessity, eligibility, authorization, or policy compliance.

## Fixed source facts used by the locked cases

- PA-01 must preserve SYN-AUTH-001, `additional evidence requested`, 2026-07-30, SYN-POL-IMG-01, both present items, and `conservative-care duration: not found in synthetic source`. The captured agentic loop also followed the inventory with the SYN-POL-IMG-01 criteria crosswalk.
- PA-02 must preserve `Synthetic Imaging Evidence Checklist`, 2026-07-01, all three reviewer checks, and `Checklist only; presence does not establish medical necessity or authorization.`
- PA-03 must preserve `additional evidence requested as recorded on 2026-07-30` and `This is a source transcription, not an agent determination.`
- PA-04 must preserve SYN-POL-IMG-01, `Include only authorized, minimum-necessary evidence.`, and human utilization-review ownership.
