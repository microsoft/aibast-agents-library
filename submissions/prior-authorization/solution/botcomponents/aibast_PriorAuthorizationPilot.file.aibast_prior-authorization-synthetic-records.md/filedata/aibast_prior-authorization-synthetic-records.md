# Prior Authorization Agent — complete synthetic records

> **Fictional demonstration data only.** These records reproduce the deterministic `PriorAuthorizationAgent`. They are not real payer policy, eligibility, medical-necessity, or authorization evidence.

## Synthetic request: SYN-AUTH-001

- **Service:** synthetic knee imaging request
- **Payer in synthetic source:** Synthetic Health Plan
- **Source-recorded workflow state:** additional evidence requested
- **Source date:** 2026-07-30
- **Workflow-state rationale:** not stated in synthetic source
- **Referenced policy:** SYN-POL-IMG-01
- **Evidence — encounter note:** present
- **Evidence — prior imaging report:** present
- **Evidence — conservative-care duration:** not found in synthetic source

## Synthetic request: SYN-AUTH-002

- **Service:** synthetic outpatient procedure request
- **Payer in synthetic source:** Synthetic Community Plan
- **Source-recorded workflow state:** payer response recorded
- **Source date:** 2026-07-31
- **Workflow-state rationale:** not stated in synthetic source
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

- PA-01 must preserve SYN-AUTH-001, `additional evidence requested`, 2026-07-30, SYN-POL-IMG-01, both present items, and `conservative-care duration: not found in synthetic source`.
- PA-02 must preserve `Synthetic Imaging Evidence Checklist`, 2026-07-01, all three reviewer checks, and `Checklist only; presence does not establish medical necessity or authorization.`
- PA-03 must preserve `additional evidence requested as recorded on 2026-07-30` and `This is a source transcription, not an agent determination.`
- PA-04 must preserve SYN-POL-IMG-01, `Include only authorized, minimum-necessary evidence.`, and human utilization-review ownership.

## Demo authorization portfolio (video walkthrough)

All patients, identifiers and values below are fictional.

| Auth # | Patient | Listed as | Procedure | Payer | Recorded status |
|---|---|---|---|---|---|
| PA-2024-892741 | Robert Chen | Chen, Robert | Lumbar MRI | Insurance | Ready to submit |
| PA-2024-892655 | Ana Martinez | Martinez, Ana | Knee arthroscopy | Insurance | Approved |
| PA-2024-892698 | David Thompson | Thompson, David | Cervical MRI | Insurance | Pending |
| PA-2024-892712 | Sarah Williams | Williams, Sarah | PT (20 visits) | Insurance | Under review |
| PA-2024-891977 | Michael Johnson | Johnson, Michael | Sleep study | Medicare | Denied (appealing) |

Open statuses counted as pending: Ready to submit, Pending, Under review (3 authorizations). Portfolio metrics: average approval time 2.4 days; approval rate 91% this month; historical approval rate 94% for similar cases.

### Robert Chen request (PA-2024-892741)

| Field | Value |
|---|---|
| auth_id | PA-2024-892741 |
| patient | Robert Chen |
| dob | 05/22/1965 |
| mrn | MR-489327 |
| insurance | Insurance PPO #XY4829103 |
| cpt | 72148 - Lumbar MRI w/o contrast |
| provider | Dr. James Thompson (Orthopedics) |
| diagnosis | M54.5 - Chronic low back pain |
| indication | Failed 6 weeks conservative therapy |
| payer_reference | Case #4729183 |
| prepared_at | Today at 3:47 PM |
| review_type | Standard (non-urgent) |
| expected_decision | Within 2 business days |
| reviewer | Automated criteria screening |

### Payer requirements for CPT 72148

| Requirement | Evidence found | Status |
|---|---|---|
| Clinical notes | Last 3 office visits attached | Met |
| Conservative therapy | PT x6 weeks, NSAIDs documented | Met |
| Symptom duration | 8 weeks, no improvement | Met |
| Red flag screening | Negative (no fever/trauma/cancer) | Met |
| Provider NPI | Dr. Thompson #1234567890 | Met |
| Prior imaging | None on file (first lumbar study) | Met |

Documentation strengths: Conservative therapy well-documented (PT, NSAIDs); Symptom duration >6 weeks; Clinical notes support medical necessity criteria; No inappropriate imaging red flags; Complete documentation package.

Appeal strategy if denied: Peer-to-peer review with radiologist; Additional functional impact documentation; Imaging guidelines citation.

Drafted notifications (sent only by the coordinator): Patient: SMS with tracking link; Dr. Thompson: Inbox message; Radiology: Pending alert for scheduling.

Proposed tracking plan: Status checks: every 4 hours via portal; Patient notification: SMS when approved (includes auth #); Radiology alert: scheduling team notified to book slot; Provider update: Dr. Thompson via secure message; Escalation: auto-trigger if no decision in 48 hours; Appeal workflow: ready if denied.

### Michael Johnson denial (PA-2024-891977)

- Reason: Insufficient clinical documentation of daytime symptoms
- Missing elements: Epworth Sleepiness Scale not in records; Work/driving impairment not documented; Failed CPAP trial not clearly stated
- Appeal actions recorded: Peer-to-peer review scheduled - tomorrow 2 PM; Additional symptom questionnaire completed; Employer letter documenting work issues; Prior CPAP compliance data retrieved
- Timeline: Decision expected within 5 business days

