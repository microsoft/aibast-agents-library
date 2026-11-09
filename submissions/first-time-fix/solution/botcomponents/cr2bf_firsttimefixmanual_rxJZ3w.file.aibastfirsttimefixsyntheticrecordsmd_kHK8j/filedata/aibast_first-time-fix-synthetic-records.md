# First-Time Fix — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The broadband provider and every service, plan, cabinet, case, network work record, visit, technician, slot, and booking draft are invented. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Services

```json
{
 "alder-grove": {
  "name": "Alder Grove Service",
  "plan": "Fibre 500",
  "area": "North service area",
  "cabinet": "Cabinet N-14",
  "status": "Active - intermittent connection",
  "drops_7_days": 6,
  "open_case": "CS-48211",
  "guided_fix": [
   "Restart the optical network terminal (ONT).",
   "Wait 2 minutes for it to reconnect.",
   "Confirm the broadband light is solid green."
  ],
  "visit_rule": "Book a technician if the broadband light stays red after the restart.",
  "flag": "Repeated drops after restart"
 },
 "cedar-reach": {
  "name": "Cedar Reach Service",
  "plan": "Fibre 300",
  "area": "East service area",
  "cabinet": "Cabinet E-03",
  "status": "Active - no fault detected",
  "drops_7_days": 1,
  "open_case": "CS-48207",
  "guided_fix": [
   "Check that the router power cable is secure.",
   "Restart the router.",
   "Test one wired device."
  ],
  "visit_rule": "No visit unless service is still unavailable after the planned maintenance.",
  "flag": "Maintenance window may affect connection"
 },
 "willow-park": {
  "name": "Willow Park Service",
  "plan": "Fibre 900",
  "area": "West service area",
  "cabinet": "Cabinet W-21",
  "status": "Active - connection restored",
  "drops_7_days": 0,
  "open_case": "CS-48190",
  "guided_fix": [
   "Confirm the router is powered on.",
   "Run a connection test before taking further action."
  ],
  "visit_rule": "No visit; no action is required if the connection test passes.",
  "flag": "None"
 },
 "harbour-view": {
  "name": "Harbour View Service",
  "plan": "Fibre 500",
  "area": "South service area",
  "cabinet": "Cabinet S-08",
  "status": "Active - intermittent connection",
  "drops_7_days": 4,
  "open_case": "CS-48215",
  "guided_fix": [
   "Check the router indicator lights.",
   "Reseat the broadband cable.",
   "Restart the router once."
  ],
  "visit_rule": "Book a technician if the broadband indicator stays off.",
  "flag": "Broadband indicator reported off"
 },
 "meadow-lane": {
  "name": "Meadow Lane Service",
  "plan": "Fibre 300",
  "area": "North service area",
  "cabinet": "Cabinet N-09",
  "status": "Active - unavailable",
  "drops_7_days": 9,
  "open_case": "CS-48219",
  "guided_fix": [
   "Verify the optical network terminal has power.",
   "Restart it.",
   "Check the broadband light."
  ],
  "visit_rule": "No premises visit while the emergency cable repair is in progress.",
  "flag": "Local repair expected to complete today"
 }
}
```

### Local Work

```json
[
 {
  "id": "NW-3301",
  "area": "East service area",
  "cabinet": "Cabinet E-03",
  "type": "Planned cabinet maintenance",
  "window": "Today 13:00-16:00",
  "status": "Scheduled",
  "affects": [
   "cedar-reach"
  ]
 },
 {
  "id": "NW-3307",
  "area": "North service area",
  "cabinet": "Cabinet N-09",
  "type": "Emergency cable repair",
  "window": "Started 07:40, expected complete 15:30 today",
  "status": "In progress",
  "affects": [
   "meadow-lane"
  ]
 }
]
```

### Visits

```json
[
 {
  "id": "FV-7710",
  "service": "alder-grove",
  "when": "22 days ago",
  "outcome": "Connection restored",
  "note": "Reseated fibre connector; investigate intermittent drops if they recur.",
  "technician": "Priya Nair"
 },
 {
  "id": "FV-7655",
  "service": "cedar-reach",
  "when": "40 days ago",
  "outcome": "No fault found",
  "note": "Service was stable on arrival; customer advised about planned cabinet maintenance.",
  "technician": "Daniel Okafor"
 },
 {
  "id": "FV-7702",
  "service": "willow-park",
  "when": "24 days ago",
  "outcome": "Router replaced",
  "note": "New router installed and connection test passed.",
  "technician": "Marta Lewis"
 },
 {
  "id": "FV-7719",
  "service": "meadow-lane",
  "when": "20 days ago",
  "outcome": "External network fault identified",
  "note": "Local cable repair required; no premises work completed.",
  "technician": "Owen Shah"
 }
]
```

### Technicians

```json
{
 "Priya Nair": {
  "skills": [
   "Fibre connectors",
   "ONT replacement"
  ],
  "area": "North service area",
  "next_slot": "Tomorrow 09:00-11:00"
 },
 "Daniel Okafor": {
  "skills": [
   "Cabinet work",
   "Router setup"
  ],
  "area": "East service area",
  "next_slot": "Tomorrow 13:00-15:00"
 },
 "Marta Lewis": {
  "skills": [
   "Router diagnostics",
   "In-home Wi-Fi"
  ],
  "area": "West service area",
  "next_slot": "Tomorrow 10:00-12:00"
 },
 "Owen Shah": {
  "skills": [
   "External cable",
   "ONT replacement"
  ],
  "area": "North service area",
  "next_slot": "Tomorrow 14:00-16:00"
 },
 "Sam Whitley": {
  "skills": [
   "Router diagnostics",
   "Fibre connectors"
  ],
  "area": "South service area",
  "next_slot": "Tomorrow 08:00-10:00"
 }
}
```

### Bookings

```json
{
 "alder-grove": {
  "technician": "Priya Nair",
  "status": "Ready to book",
  "preparation": [
   "Add the repeated-drop history (6 drops in 7 days).",
   "Include the previous fibre-connector visit note (FV-7710).",
   "Test the optical network terminal and fibre connector on arrival."
  ]
 },
 "cedar-reach": {
  "technician": "Daniel Okafor",
  "status": "Not required",
  "preparation": [
   "Hold the visit until planned cabinet maintenance NW-3301 completes.",
   "Include the maintenance reference if service remains unavailable."
  ]
 },
 "willow-park": {
  "technician": "Marta Lewis",
  "status": "No booking needed",
  "preparation": [
   "Bring the router diagnostics kit only if a later test fails.",
   "Confirm connection test results before any travel."
  ]
 },
 "harbour-view": {
  "technician": "Sam Whitley",
  "status": "Ready to book if the indicator stays off",
  "preparation": [
   "Note that the broadband indicator was reported off.",
   "Bring a replacement broadband cable and router diagnostics kit."
  ]
 },
 "meadow-lane": {
  "technician": "Owen Shah",
  "status": "Pending local repair",
  "preparation": [
   "Do not book a premises visit while emergency cable repair NW-3307 is open.",
   "Review repair completion first."
  ]
 }
}
```

## Exact responses for every locked case

### FTF-01 — Guided connection fix

Prompt: "The customer on Alder Grove Service keeps dropping. What guided fix should I walk them through right now?"

Operation: `guided_fix`; arguments: `{"operation": "guided_fix", "service": "Alder Grove Service"}`

**Guided Connection Fix - Alder Grove Service**

**Plan:** Fibre 500 | **Status:** Active - intermittent connection | **Drops in 7 days:** 6 | **Open case:** CS-48211

**Steps to use now**
1. Restart the optical network terminal (ONT).
2. Wait 2 minutes for it to reconnect.
3. Confirm the broadband light is solid green.

**When to book a visit:** Book a technician if the broadband light stays red after the restart.
**Local work:** No confirmed local work
**Flag:** Repeated drops after restart

> Read-only synthetic snapshot. No visit, service, customer contact, case or technician schedule was changed; every booking is a draft for the agent to confirm.

Source: [Synthetic Broadband Service Snapshot]
Agents: FirstTimeFixAgent

### FTF-02 — Local work check

Prompt: "Is there any network work near Meadow Lane that could explain the outage?"

Operation: `local_work_check`; arguments: `{"operation": "local_work_check", "service": "Meadow Lane Service"}`

**Local Work Check - Meadow Lane Service**

**Area:** North service area | **Cabinet:** Cabinet N-09

| Work | Type | Window | Status |
|------|------|--------|--------|
| NW-3307 | Emergency cable repair | Started 07:40, expected complete 15:30 today | In progress |

**Flag for the agent:** Local repair expected to complete today

> Read-only synthetic snapshot. No visit, service, customer contact, case or technician schedule was changed; every booking is a draft for the agent to confirm.

Source: [Synthetic Broadband Service Snapshot]
Agents: FirstTimeFixAgent

### FTF-03 — Previous visit review

Prompt: "What did the last technician find at Alder Grove Service?"

Operation: `visit_history`; arguments: `{"operation": "visit_history", "service": "Alder Grove Service"}`

**Previous Visits - Alder Grove Service**

| Visit | When | Outcome | Technician | Note |
|-------|------|---------|------------|------|
| FV-7710 | 22 days ago | Connection restored | Priya Nair | Reseated fibre connector; investigate intermittent drops if they recur. |

> Read-only synthetic snapshot. No visit, service, customer contact, case or technician schedule was changed; every booking is a draft for the agent to confirm.

Source: [Synthetic Broadband Service Snapshot]
Agents: FirstTimeFixAgent

### FTF-04 — Technician booking draft

Prompt: "If the light stays red, which technician should go to Alder Grove and what should they prepare? Don't book it yet."

Operation: `technician_booking`; arguments: `{"operation": "technician_booking", "service": "Alder Grove Service"}`

**Technician Booking - Alder Grove Service**

**Recommended technician:** Priya Nair (Fibre connectors, ONT replacement; North service area)
**Next slot:** Tomorrow 09:00-11:00 | **Booking status:** Ready to book

**Job preparation**
- Add the repeated-drop history (6 drops in 7 days).
- Include the previous fibre-connector visit note (FV-7710).
- Test the optical network terminal and fibre connector on arrival.

> Draft only: no visit was booked. Read-only synthetic snapshot. No visit, service, customer contact, case or technician schedule was changed; every booking is a draft for the agent to confirm.

Source: [Synthetic Broadband Service Snapshot]
Agents: FirstTimeFixAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| FTF-01 | Contact Center Agent | The customer on Alder Grove Service keeps dropping. What guided fix should I walk them through right now? | `guided_fix` | Guided Connection Fix; optical network terminal; solid green |
| FTF-02 | Contact Center Agent | Is there any network work near Meadow Lane that could explain the outage? | `local_work_check` | Local Work Check; NW-3307; Emergency cable repair |
| FTF-03 | Field Service Dispatcher | What did the last technician find at Alder Grove Service? | `visit_history` | FV-7710; Connection restored; fibre connector |
| FTF-04 | Field Service Dispatcher | If the light stays red, which technician should go to Alder Grove and what should they prepare? Don't book it yet. | `technician_booking` | Technician Booking; Priya Nair; Draft only |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
