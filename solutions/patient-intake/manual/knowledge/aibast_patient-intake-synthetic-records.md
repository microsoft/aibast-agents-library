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

## Synthetic patient record: SYN-PT-003 (demo default)

- **Display label:** Sarah Martinez (fictional) — new patient
- **Chief complaint:** Chronic migraines; requested provider Dr. James Anderson, MD (Neurology, Neurology Clinic - Suite 405)
- **Requested timeframe:** within 14 days of the 2024-01-23 call (fixed 2024 demo calendar)
- **Coverage payer recorded in synthetic source:** Blue Cross Blue Shield; state Active; evidence date 2024-01-23
- **Policy / group:** XXX-XX-7392 / 84721
- **Specialist copay:** $35; **deductible:** $450 met of $1,500; **prior auth required:** No (initial consult exempt); **network:** In-network, Tier 1
- **Coverage human follow-up:** Confirm active coverage and network status in the payer portal.
- **Intake status:** intake packet not yet completed
- **Requested visit:** New Patient Consultation with Dr. James Anderson on 2024-01-30 (60 minutes)

When no patient is named, the agent uses SYN-PT-003. A patient ID, label, or part of a label (for example `Alpha` or
`Sarah Martinez`) selects a record; anything else returns "No synthetic patient matched".

## Candidate source availability

These are candidate source slots only. Nothing is held, reserved, booked, rescheduled, or changed.

| Provider | Date | Time | Service |
| --- | --- | --- | --- |
| Clinician A | 2026-08-20 | 10:30 | new patient consultation |
| Clinician A | 2026-08-22 | 14:00 | follow-up consultation |
| Clinician B | 2026-08-21 | 09:00 | follow-up consultation |
| Dr. James Anderson | 2024-01-30 (Tuesday 2:30 PM) | 14:30 | new patient consultation |
| Dr. James Anderson | 2024-02-01 (Thursday 10:00 AM) | 10:00 | new patient consultation |

## Fixed source facts used by the locked cases

- PI-01 uses SYN-PT-001 and must preserve `emergency contact confirmation`.
- PI-02 uses SYN-PT-001 and must preserve `Synthetic Health Plan`, `source record received`, `2026-07-30`, and the exact payer-portal follow-up.
- PI-03 filters to Clinician A and must preserve both Clinician A slots and the statement that nothing has been reserved or booked.
- PI-04 uses SYN-PT-001 and must preserve the new patient consultation with Clinician A on 2026-08-15 plus the authorized patient-access reviewer.

## Intake packet, reminders and demo flow (video scenario)

- Neurology intake packet: Demographics Form: Name, DOB, contact info, emergency contact; Insurance Verification: Photo upload for card front/back; Medical History: Current medications, allergies, prior surgeries; Migraine Questionnaire: HIT-6 headache impact assessment; HIPAA Authorization: Digital signature required; Financial Policy: Payment terms and copay acknowledgment.
- Reminder protocol (40% no-show reduction protocol): 72-Hour Reminder SMS + Email (Saturday 2:30 PM for the Tuesday 2:30 PM visit); 24-Hour Reminder SMS + Voice call option (Monday 2:30 PM); 2-Hour Reminder Final SMS (Tuesday 12:30 PM); forms completion alert the day before (Monday); reply RESCHEDULE; waitlist auto-fill on >24hr cancellation notice; historical no-show rate 8% for new patients with this protocol. Times are computed from the chosen slot.
- Every registration, appointment, packet, confirmation and reminder is a draft for staff: nothing is registered, booked, sent, or activated by the agent.
- PI-05 (`new_patient_intake`, SYN-PT-003): New Patient Registration Draft; Dr. James Anderson, Neurology; Within 14 days.
- PI-06 (`appointment_hold_draft`, SYN-PT-003): Appointment Request Draft; Tuesday, January 30, 2024; 2:30 PM; Suite 405.
- PI-07 (`intake_packet`, SYN-PT-003): Digital Intake Packet Draft; HIT-6; HIPAA Authorization.
- PI-08 (`reminder_plan`, SYN-PT-003): 72-Hour Reminder; Saturday 2:30 PM; 8% for new patients.

## Exact source constants (JSON)

### `PATIENTS`

```json
{
  "SYN-PT-001": {
    "label": "Synthetic Patient Alpha",
    "language": "English",
    "forms": [
      "contact details",
      "consent acknowledgement",
      "medication list"
    ],
    "missing": [
      "emergency contact confirmation"
    ],
    "coverage": {
      "payer": "Synthetic Health Plan",
      "recorded_status": "source record received",
      "evidence_date": "2026-07-30",
      "follow_up": "Confirm active coverage and network status in the payer portal."
    },
    "visit": {
      "service": "new patient consultation",
      "provider": "Clinician A",
      "date": "2026-08-15"
    }
  },
  "SYN-PT-002": {
    "label": "Synthetic Patient Beta",
    "language": "Spanish",
    "forms": [
      "contact details",
      "consent acknowledgement"
    ],
    "missing": [
      "preferred-language packet",
      "medication list"
    ],
    "coverage": {
      "payer": "Synthetic Community Plan",
      "recorded_status": "referral evidence missing",
      "evidence_date": "2026-07-29",
      "follow_up": "Ask authorized staff to confirm referral and coverage evidence."
    },
    "visit": {
      "service": "follow-up consultation",
      "provider": "Clinician B",
      "date": "2026-08-18"
    }
  },
  "SYN-PT-003": {
    "label": "Sarah Martinez",
    "patient_type": "New Patient",
    "language": "English",
    "chief_complaint": "Chronic migraines",
    "timeframe_days": 14,
    "request_date": "2024-01-23",
    "forms": [],
    "missing": [
      "intake packet not yet completed"
    ],
    "coverage": {
      "payer": "Blue Cross Blue Shield",
      "recorded_status": "Active",
      "evidence_date": "2024-01-23",
      "follow_up": "Confirm active coverage and network status in the payer portal.",
      "policy_number": "XXX-XX-7392",
      "group_number": "84721",
      "specialist_copay": 35,
      "deductible_met": 450,
      "deductible": 1500,
      "prior_auth": "No (initial consult exempt)",
      "network": "In-network, Tier 1"
    },
    "visit": {
      "service": "New Patient Consultation",
      "provider": "Dr. James Anderson",
      "date": "2024-01-30"
    }
  }
}
```

### `PROVIDERS`

```json
{
  "Dr. James Anderson": {
    "credential": "MD",
    "specialty": "Neurology",
    "location": "Neurology Clinic - Suite 405"
  }
}
```

### `AVAILABILITY`

```json
{
  "Clinician A": [
    {
      "date": "2026-08-20",
      "time": "10:30",
      "service": "new patient consultation"
    },
    {
      "date": "2026-08-22",
      "time": "14:00",
      "service": "follow-up consultation"
    }
  ],
  "Clinician B": [
    {
      "date": "2026-08-21",
      "time": "09:00",
      "service": "follow-up consultation"
    }
  ],
  "Dr. James Anderson": [
    {
      "date": "2024-01-30",
      "time": "14:30",
      "service": "new patient consultation",
      "label": "Tuesday 2:30 PM"
    },
    {
      "date": "2024-02-01",
      "time": "10:00",
      "service": "new patient consultation",
      "label": "Thursday 10:00 AM"
    }
  ]
}
```

### `INTAKE_PACKETS`

```json
{
  "base": [
    "Demographics Form: Name, DOB, contact info, emergency contact",
    "Insurance Verification: Photo upload for card front/back",
    "Medical History: Current medications, allergies, prior surgeries",
    "HIPAA Authorization: Digital signature required",
    "Financial Policy: Payment terms and copay acknowledgment"
  ],
  "Neurology": [
    "Migraine Questionnaire: HIT-6 headache impact assessment"
  ]
}
```

### `REMINDER_PROTOCOL`

```json
{
  "touchpoints": [
    {
      "name": "72-Hour Reminder",
      "hours_before": 72,
      "channel": "SMS + Email"
    },
    {
      "name": "24-Hour Reminder",
      "hours_before": 24,
      "channel": "SMS + Voice call option"
    },
    {
      "name": "2-Hour Reminder",
      "hours_before": 2,
      "channel": "Final SMS"
    }
  ],
  "forms_alert_days_before": 1,
  "reschedule_keyword": "RESCHEDULE",
  "waitlist_rule": "Auto-fill the slot if she cancels with >24hr notice",
  "historical_no_show_rate": "8% for new patients with this protocol",
  "protocol_name": "40% no-show reduction protocol"
}
```
