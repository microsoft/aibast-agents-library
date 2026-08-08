# Patient Intake and Scheduling Agent — complete synthetic records

> **Fictional demonstration data only.** These records reproduce the deterministic `PatientIntakeAgent`. Never combine them with live patient information or treat them as current eligibility, appointment, or clinical data.

## Synthetic patient record: SYN-PT-001

- **Display label:** Synthetic Patient Alpha
- **Preferred language recorded:** English
- **Forms present, in source order:** contact details; consent acknowledgement; medication list
- **Items for staff confirmation:** emergency contact confirmation
- **Coverage payer recorded in synthetic source:** Synthetic Health Plan
- **Coverage source-recorded state:** source record received
- **Coverage evidence date:** 2026-07-30
- **Coverage human follow-up:** Confirm active coverage and network status in the payer portal.
- **Source-recorded visit service:** new patient consultation
- **Source-recorded visit provider:** Clinician A
- **Source-recorded visit date:** 2026-08-15

## Synthetic patient record: SYN-PT-002

- **Display label:** Synthetic Patient Beta
- **Preferred language recorded:** Spanish
- **Forms present, in source order:** contact details; consent acknowledgement
- **Items for staff confirmation, in source order:** preferred-language packet; medication list
- **Coverage payer recorded in synthetic source:** Synthetic Community Plan
- **Coverage source-recorded state:** referral evidence missing
- **Coverage evidence date:** 2026-07-29
- **Coverage human follow-up:** Ask authorized staff to confirm referral and coverage evidence.
- **Source-recorded visit service:** follow-up consultation
- **Source-recorded visit provider:** Clinician B
- **Source-recorded visit date:** 2026-08-18

## Candidate source availability

These are candidate source slots only. Nothing is held, reserved, booked, rescheduled, or changed.

| Provider | Date | Time | Service |
| --- | --- | --- | --- |
| Clinician A | 2026-08-20 | 10:30 | new patient consultation |
| Clinician A | 2026-08-22 | 14:00 | follow-up consultation |
| Clinician B | 2026-08-21 | 09:00 | follow-up consultation |

## Fixed source facts used by the locked cases

- PI-01 uses SYN-PT-001 and must preserve `emergency contact confirmation`.
- PI-02 uses SYN-PT-001 and must preserve `Synthetic Health Plan`, `source record received`, `2026-07-30`, and the exact payer-portal follow-up.
- PI-03 filters to Clinician A and must preserve both Clinician A slots and the statement that nothing has been reserved or booked.
- PI-04 uses SYN-PT-001 and must preserve the new patient consultation with Clinician A on 2026-08-15 plus the authorized patient-access reviewer.
