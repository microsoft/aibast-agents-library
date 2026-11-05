# Tiered Huddle Board — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Cedarline Community Hospital and every unit, issue, tier target, clock, person, role, ticket, escalation draft and decision on this board are invented. Never match them to a real organization, person, patient, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source. `hours_in_tier` is how long the issue has been in its current tier; the clock is the tier target minus that value. A mitigated item runs a hold clock instead and is never counted as past target.

### Hospital

```json
{
 "name": "Cedarline Community Hospital",
 "default_viewer": "Elena Brooks"
}
```

### Tiers

```json
[
 {
  "key": "unit",
  "name": "Tier 1",
  "scope": "Unit",
  "huddle": "08:30",
  "target_hours": 8
 },
 {
  "key": "department",
  "name": "Tier 2",
  "scope": "Department",
  "huddle": "09:15",
  "target_hours": 24
 },
 {
  "key": "operations",
  "name": "Tier 3",
  "scope": "Hospital operations",
  "huddle": "09:45",
  "target_hours": 48
 },
 {
  "key": "executive",
  "name": "Executive",
  "scope": "Leadership",
  "huddle": "10:30",
  "target_hours": 72
 }
]
```

### Issues

```json
[
 {
  "id": "HB-2041",
  "tier": "unit",
  "unit": "4 West Med-Surg",
  "category": "Equipment",
  "title": "Two IV infusion pumps out of service; three scheduled infusions this shift at risk",
  "status": "Open - unit cannot fix",
  "owner": "Elena Brooks",
  "originator": "Jordan Pike",
  "waiting_on": "Elena Brooks",
  "hours_in_tier": 10,
  "hours_open": 10,
  "unit_tried": "Borrowed one pump from 4 East overnight (returned at 07:00) and opened biomedical ticket BME-5531.",
  "impact": "Three scheduled infusions this shift have no pump; one antibiotic dose is due at 14:00."
 },
 {
  "id": "HB-2043",
  "tier": "unit",
  "unit": "4 West Med-Surg",
  "category": "Staffing",
  "title": "Night shift short one registered nurse tonight",
  "status": "In progress",
  "owner": "Elena Brooks",
  "originator": "Elena Brooks",
  "waiting_on": "Lena Ford",
  "hours_in_tier": 3,
  "hours_open": 3,
  "unit_tried": "Offered the open shift to the unit float list.",
  "impact": "Ratio rises to 1:6 on nights if the shift stays open."
 },
 {
  "id": "HB-2038",
  "tier": "unit",
  "unit": "4 West Med-Surg",
  "category": "Safety",
  "title": "Bed exit alarm in room 412 failing intermittently",
  "status": "Mitigated - awaiting originator confirmation",
  "owner": "Elena Brooks",
  "originator": "Jordan Pike",
  "waiting_on": "Jordan Pike",
  "hours_in_tier": 18,
  "hours_open": 18,
  "mitigation": "Biomedical engineering replaced the sensor pad; the fall-risk patient stays in room 409 until the alarm holds for 24 hours (two full shifts).",
  "hold_hours_required": 24,
  "hold_hours_done": 16,
  "unit_tried": "Moved the fall-risk patient to room 409.",
  "impact": "A fall-risk patient cannot use room 412 until the alarm is proven."
 },
 {
  "id": "HB-2033",
  "tier": "department",
  "unit": "2 North Surgical",
  "category": "Safety",
  "title": "Call light system dropped calls from four rooms",
  "status": "Mitigated - awaiting originator confirmation",
  "owner": "Rachel Ng",
  "originator": "Amir Sadeghi",
  "waiting_on": "Amir Sadeghi",
  "hours_in_tier": 14,
  "hours_open": 21,
  "mitigation": "The vendor reset the room controllers; hourly rounding stays in place until the system holds for a full 12-hour shift.",
  "hold_hours_required": 12,
  "hold_hours_done": 12,
  "unit_tried": "Started hourly rounding on the four rooms.",
  "impact": "Four rooms depend on hourly rounding instead of call lights."
 },
 {
  "id": "HB-2035",
  "tier": "department",
  "unit": "3 East Telemetry",
  "category": "Patient flow",
  "title": "Four telemetry beds held by patients waiting for step-down placement",
  "status": "In progress",
  "owner": "Rachel Ng",
  "originator": "Tessa Morgan",
  "waiting_on": "Case management",
  "hours_in_tier": 20,
  "hours_open": 26,
  "unit_tried": "Placed step-down requests for all four patients.",
  "impact": "Telemetry admissions from the emergency department wait for a bed."
 },
 {
  "id": "HB-2029",
  "tier": "department",
  "unit": "Intensive Care Unit",
  "category": "Quality",
  "title": "Central line bundle audit at 82% against a 95% goal",
  "status": "In progress",
  "owner": "Owen Price",
  "originator": "Owen Price",
  "waiting_on": "Owen Price",
  "hours_in_tier": 6,
  "hours_open": 6,
  "unit_tried": "Added a second check at the dressing change.",
  "impact": "Infection-prevention risk on lines placed this week."
 },
 {
  "id": "HB-2031",
  "tier": "operations",
  "unit": "Emergency Department",
  "category": "Patient flow",
  "title": "Five admitted patients boarding in the emergency department for more than 6 hours",
  "status": "Decision needed",
  "owner": "Victor Hale",
  "originator": "Sofia Grant",
  "waiting_on": "Leadership huddle",
  "hours_in_tier": 52,
  "hours_open": 70,
  "escalation_reason": "Opening the six-bed surge unit on 5 South needs house-wide staffing and overtime that exceed hospital operations authority.",
  "decision": "Approve opening the six-bed surge unit on 5 South for 72 hours with agency staffing.",
  "unit_tried": "Expedited discharges before 11:00 on three units.",
  "impact": "Admitted patients wait in emergency bays; ambulance diversion risk rises after 18:00."
 },
 {
  "id": "HB-2027",
  "tier": "executive",
  "unit": "Pharmacy",
  "category": "Supplies",
  "title": "Heparin flush supplier backorder; nine days of stock on hand",
  "status": "Decision needed",
  "owner": "Naomi Carter",
  "originator": "Felix Osei",
  "waiting_on": "Leadership huddle",
  "hours_in_tier": 30,
  "hours_open": 96,
  "escalation_reason": "Switching to the alternate supplier changes a contract at a higher unit cost, which needs executive approval.",
  "decision": "Approve the alternate heparin flush supplier at the higher unit cost for 60 days.",
  "unit_tried": "Moved to conservation dosing and pooled stock across units.",
  "impact": "Stock runs out in nine days at current use."
 },
 {
  "id": "HB-2019",
  "tier": "department",
  "unit": "4 West Med-Surg",
  "category": "Supplies",
  "title": "Wound-care dressing par levels too low on weekends",
  "status": "Closed - originator confirmed the fix held",
  "owner": "Rachel Ng",
  "originator": "Jordan Pike",
  "waiting_on": "",
  "hours_in_tier": 40,
  "hours_open": 120,
  "mitigation": "Supply chain raised weekend par levels by 30%.",
  "hold_hours_required": 48,
  "hold_hours_done": 48,
  "unit_tried": "Borrowed dressings from 4 East on weekends.",
  "impact": "None after the change."
 }
]
```

### Paging roster (Microsoft Teams, by tier and category)

```json
{
 "unit": {
  "default": [
   {
    "name": "Elena Brooks",
    "role": "Nurse Manager, 4 West"
   },
   {
    "name": "Jordan Pike",
    "role": "Charge Nurse, 4 West"
   }
  ]
 },
 "department": {
  "Equipment": [
   {
    "name": "Rachel Ng",
    "role": "Director of Medical-Surgical Nursing"
   },
   {
    "name": "Marcus Bell",
    "role": "Biomedical Engineering Supervisor"
   }
  ],
  "Staffing": [
   {
    "name": "Rachel Ng",
    "role": "Director of Medical-Surgical Nursing"
   },
   {
    "name": "Lena Ford",
    "role": "Staffing Office Manager"
   }
  ],
  "default": [
   {
    "name": "Rachel Ng",
    "role": "Director of Medical-Surgical Nursing"
   }
  ]
 },
 "operations": {
  "Equipment": [
   {
    "name": "Victor Hale",
    "role": "Director of Hospital Operations"
   },
   {
    "name": "Grace Holloway",
    "role": "Administrator on Duty"
   }
  ],
  "default": [
   {
    "name": "Victor Hale",
    "role": "Director of Hospital Operations"
   },
   {
    "name": "Grace Holloway",
    "role": "Administrator on Duty"
   }
  ]
 },
 "executive": {
  "default": [
   {
    "name": "Naomi Carter",
    "role": "Chief Nursing Officer"
   },
   {
    "name": "Daniel Reyes",
    "role": "Chief Operating Officer"
   }
  ]
 }
}
```

## Exact responses for every locked case

### THB-01 — Whole board view

Prompt: "I'm between patients. Show me the huddle board: what's past target and what's waiting on me?"

Operation: `board_view`; arguments: `{"operation": "board_view"}`

**Huddle Board - Cedarline Community Hospital**

**As of:** today's huddle snapshot | **Open items:** 8 | **Past target:** 2 | **Waiting on Elena Brooks:** 1

**Act first:** HB-2031 (Emergency Department) is 4 h past target at Tier 3: Five admitted patients boarding in the emergency department for more than 6 hours.

| Lane | Item | Unit | Issue | Clock | Status | Waiting on |
|------|------|------|-------|-------|--------|------------|
| Tier 1 (8 h) | HB-2041 | 4 West Med-Surg | Two IV infusion pumps out of service; three scheduled infusions this shift at risk | 2 h past target | Open - unit cannot fix | Elena Brooks |
| Tier 1 (8 h) | HB-2043 | 4 West Med-Surg | Night shift short one registered nurse tonight | 5 h left | In progress | Lena Ford |
| Tier 1 (8 h) | HB-2038 | 4 West Med-Surg | Bed exit alarm in room 412 failing intermittently | Hold 16 of 24 h | Mitigated - awaiting originator confirmation | Jordan Pike |
| Tier 2 (24 h) | HB-2033 | 2 North Surgical | Call light system dropped calls from four rooms | Hold 12 of 12 h | Mitigated - awaiting originator confirmation | Amir Sadeghi |
| Tier 2 (24 h) | HB-2035 | 3 East Telemetry | Four telemetry beds held by patients waiting for step-down placement | 4 h left | In progress | Case management |
| Tier 2 (24 h) | HB-2029 | Intensive Care Unit | Central line bundle audit at 82% against a 95% goal | 18 h left | In progress | Owen Price |
| Tier 3 (48 h) | HB-2031 | Emergency Department | Five admitted patients boarding in the emergency department for more than 6 hours | 4 h past target | Decision needed | Leadership huddle |
| Executive (72 h) | HB-2027 | Pharmacy | Heparin flush supplier backorder; nine days of stock on hand | 42 h left | Decision needed | Leadership huddle |

**Waiting on Elena Brooks**
- HB-2041: Two IV infusion pumps out of service; three scheduled infusions this shift at risk (2 h past target)

> Read-only synthetic snapshot of a fictional hospital. No issue was escalated, closed or changed and no one was paged; an authorized person confirms every step.

Source: [Synthetic Tiered Huddle Board Snapshot]
Agents: TieredHuddleBoardAgent

### THB-02 — Escalation draft

Prompt: "4 West can't fix the IV pump problem at our level. Get the escalation ready for the next tier, but don't page anyone until I confirm."

Operation: `escalation_draft`; arguments: `{"operation": "escalation_draft", "issue": "IV pumps"}`

**Escalation Draft - HB-2041: Tier 1 to Tier 2**

**Issue:** Two IV infusion pumps out of service; three scheduled infusions this shift at risk (4 West Med-Surg, Equipment)
**Current clock:** 2 h past target at Tier 1 (target 8 h)
**New clock:** restarts at the Tier 2 target of 24 h, due 24 h after confirmation; reviewed at the 09:15 department huddle

**Reason the next tier reads first**
4 West Med-Surg cannot resolve this at Tier 1. Impact: Three scheduled infusions this shift have no pump; one antibiotic dose is due at 14:00. Already tried: Borrowed one pump from 4 East overnight (returned at 07:00) and opened biomedical ticket BME-5531.

**Page in Microsoft Teams on confirmation**
- Rachel Ng, Director of Medical-Surgical Nursing
- Marcus Bell, Biomedical Engineering Supervisor
- Copy: Jordan Pike (raised the issue)

**Status:** Draft - waiting for one confirmation from the issue owner (Elena Brooks) on the huddle board. This agent cannot send it: the board's authorized escalation step moves the tier and sends the Teams pages. Nothing has moved tiers and no one has been paged.

> Read-only synthetic snapshot of a fictional hospital. No issue was escalated, closed or changed and no one was paged; an authorized person confirms every step.

Source: [Synthetic Tiered Huddle Board Snapshot]
Agents: TieredHuddleBoardAgent

### THB-03 — Closure check

Prompt: "Biomed fixed the bed alarm in room 412 yesterday. Can we take it off the board?"

Operation: `closure_check`; arguments: `{"operation": "closure_check", "issue": "bed alarm in 412"}`

**Closure Check - HB-2038**

**Issue:** Bed exit alarm in room 412 failing intermittently (4 West Med-Surg)
**Raised by:** Jordan Pike | **Owner:** Elena Brooks | **Status:** Mitigated - awaiting originator confirmation

**Can it close now? No. Mitigated is not closed.**
Only Jordan Pike, who raised it, can confirm the fix held.

**Mitigation:** Biomedical engineering replaced the sensor pad; the fall-risk patient stays in room 409 until the alarm holds for 24 hours (two full shifts).
**Hold period:** 16 of 24 h done; 8 h to go before Jordan Pike is asked to confirm.

**Other mitigated items waiting on their originator:** HB-2033 (Amir Sadeghi)

> Read-only synthetic snapshot of a fictional hospital. No issue was escalated, closed or changed and no one was paged; an authorized person confirms every step.

Source: [Synthetic Tiered Huddle Board Snapshot]
Agents: TieredHuddleBoardAgent

### THB-04 — Leadership huddle decisions

Prompt: "For the 10:30 leadership huddle, what needs a decision from us today?"

Operation: `leadership_decisions`; arguments: `{"operation": "leadership_decisions"}`

**Leadership Huddle - 10:30 today**

**2 decisions needed today**, most urgent first.

| Item | Lane | Decision needed | Reason | Clock | Owner |
|------|------|-----------------|--------|-------|-------|
| HB-2031 | Tier 3 | Approve opening the six-bed surge unit on 5 South for 72 hours with agency staffing. | Opening the six-bed surge unit on 5 South needs house-wide staffing and overtime that exceed hospital operations authority. | 4 h past target | Victor Hale |
| HB-2027 | Executive | Approve the alternate heparin flush supplier at the higher unit cost for 60 days. | Switching to the alternate supplier changes a contract at a higher unit cost, which needs executive approval. | 42 h left | Naomi Carter |

**Past target below this huddle (for awareness):** HB-2041 4 West Med-Surg (2 h past target at Tier 1)

> Recommendation only: leadership records each decision on the board. Read-only synthetic snapshot of a fictional hospital. No issue was escalated, closed or changed and no one was paged; an authorized person confirms every step.

Source: [Synthetic Tiered Huddle Board Snapshot]
Agents: TieredHuddleBoardAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| THB-01 | Nurse Manager | I'm between patients. Show me the huddle board: what's past target and what's waiting on me? | `board_view` | Huddle Board; HB-2041; past target |
| THB-02 | Nurse Manager | 4 West can't fix the IV pump problem at our level. Get the escalation ready for the next tier, but don't page anyone until I confirm. | `escalation_draft` | Escalation Draft; Tier 2; Marcus Bell |
| THB-03 | Nurse Manager | Biomed fixed the bed alarm in room 412 yesterday. Can we take it off the board? | `closure_check` | Closure Check; HB-2038; Jordan Pike |
| THB-04 | Chief Nursing Officer | For the 10:30 leadership huddle, what needs a decision from us today? | `leadership_decisions` | Leadership Huddle; HB-2027; HB-2031 |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
