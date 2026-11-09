# Field Permit to Work Agent — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT: Northwind Energy Networks permit snapshot, Tuesday 10 March 2026 at 06:30. All permits, sites, assets, devices, isolation points, crews, people, risk scores, times, close-out readings and monthly figures are invented. The names Dana Brooks, Lee Carter and the crew members listed below are fictional. Never match them to a real person, organization, site or record, and never use live data.

## Complete synthetic records

Each section below is the exact deterministic output of one packaged operation over one fictional record. Answer only from these sections; quote figures, identifiers and statuses exactly.

### permit_queue

**Permit Queue: Northwind Energy Networks** (snapshot Tue 10 Mar 2026 06:30)

| Permit | Site | Work | Start | Current stage | Risk | Blocker |
|---|---|---|---|---|---|---|
| PTW-4471 | Cedar Hill Substation | Tap-changer maintenance | 11:00 | Authorized person review | High | Live isolation not confirmed |
| PTW-4472 | Riverside Feeder 7 | Cable joint repair | 10:00 | Supervisor review | Medium | Isolation plan incomplete |
| PTW-4473 | Hilltop Line 3 | Insulator replacement | 13:00 | Supervisor review | Medium | None |

**Today:** 3 permits, 2 with a blocker before work can start.
**Recommended next:** PTW-4471 at Cedar Hill is the highest-risk job; draft its risk assessment and check its isolation first.



Source: [Synthetic Permit Snapshot]

### risk_assessment - PTW-4471

**Risk Assessment Draft: PTW-4471 Cedar Hill Substation Transformer T2**

| Hazard | Controls |
|---|---|
| Electric shock or arc flash | De-energize, lock out and tag, prove dead, arc-rated clothing |
| Hot oil contact | Cooling period, oil-handling gloves, drip tray |
| Manual handling of heavy components | Mechanical lift, two-person carry |

**PPE:** Arc-rated coveralls, insulated gloves, face shield

| Residual risk | Value |
|---|---|
| Base risk | 45 |
| Weather (wet) | +15 |
| Senior authorized crew | -0 |
| **Residual risk score** | **60 of 100 (High)** |

**Method steps:** toolbox talk and sign-in; confirm isolation and prove dead; barriers and signs; work to method statement; tidy site and clear the permit.

Risk bands: Low below 25, Medium 25-54, High 55 or more. Draft for the authorized person to review and sign.



Source: [Synthetic Hazard Library + Permit Snapshot]

### risk_assessment - PTW-4472

**Risk Assessment Draft: PTW-4472 Riverside Feeder 7 Cable joint J14**

| Hazard | Controls |
|---|---|
| Striking a live cable while digging | Cable-route plans, cable locator scan, hand dig near the route |
| Confined space in the joint pit | Gas monitor, top person, rescue plan |
| Heavy cable handling | Cable rollers, two-person lift |

**PPE:** Coveralls, cut-resistant gloves, gas monitor

| Residual risk | Value |
|---|---|
| Base risk | 45 |
| Weather (calm) | +0 |
| Senior authorized crew | -10 |
| **Residual risk score** | **35 of 100 (Medium)** |

**Method steps:** toolbox talk and sign-in; confirm isolation and prove dead; barriers and signs; work to method statement; tidy site and clear the permit.

Risk bands: Low below 25, Medium 25-54, High 55 or more. Draft for the authorized person to review and sign.



Source: [Synthetic Hazard Library + Permit Snapshot]

### risk_assessment - PTW-4473

**Risk Assessment Draft: PTW-4473 Hilltop Line 3 Span 3-14 to 3-15**

| Hazard | Controls |
|---|---|
| Working at height | Elevated work platform, fall arrest, exclusion zone |
| Adjacent live conductors | Safe approach distance, insulated tools, portable earths |
| Wind on the elevated platform | Wind check before lift, stop-work limit |

**PPE:** Fall-arrest harness, insulated gloves, high-visibility clothing

| Residual risk | Value |
|---|---|
| Base risk | 45 |
| Weather (windy) | +10 |
| Senior authorized crew | -10 |
| **Residual risk score** | **45 of 100 (Medium)** |

**Method steps:** toolbox talk and sign-in; confirm isolation and prove dead; barriers and signs; work to method statement; tidy site and clear the permit.

Risk bands: Low below 25, Medium 25-54, High 55 or more. Draft for the authorized person to review and sign.



Source: [Synthetic Hazard Library + Permit Snapshot]

### isolation_check - PTW-4471

**Isolation Check: PTW-4471 Cedar Hill Substation** (live state as of Tue 10 Mar 2026 06:30)

**Plan vs required points: PASS (4 of 4)**

| Point | Type | Required state | Plan |
|---|---|---|---|
| ISO-T2-A | Primary disconnector | Open | In plan |
| ISO-T2-B | Earth switch | Closed | In plan |
| ISO-T2-C | Lockout padlock | Applied | In plan |
| ISO-T2-D | Voltage proving point | Tested | In plan |

**Live switching state:**

| Device | Type | State | Lockout |
|---|---|---|---|
| CB-CH-01 | Circuit breaker | Open | Applied |
| CB-CH-02 | Circuit breaker | Open | Not applied |
| DS-CH-01 | Disconnector | Open | Applied |
| ES-CH-01 | Earth switch | Closed | Applied |

**Result: Isolation NOT confirmed. Do not start work.** CB-CH-02 lockout not applied. Ask the control room to correct it and re-check before the crew briefing.

No device was operated or locked.



Source: [Synthetic Isolation Plan + Control Room Snapshot]

### isolation_check - PTW-4472

**Isolation Check: PTW-4472 Riverside Feeder 7** (live state as of Tue 10 Mar 2026 06:30)

**Plan vs required points: FAIL (3 of 4)**

| Point | Type | Required state | Plan |
|---|---|---|---|
| ISO-F7-A | Feeder breaker | Open | In plan |
| ISO-F7-B | Earth switch | Closed | MISSING from plan |
| ISO-F7-C | Lockout padlock | Applied | In plan |
| ISO-F7-D | Voltage proving point | Tested | In plan |

**Live switching state:**

| Device | Type | State | Lockout |
|---|---|---|---|
| CB-RV-07 | Circuit breaker | Open | Applied |
| ES-RV-07 | Earth switch | Closed | Applied |

**Result: Do not start work.** The isolation plan is missing ISO-F7-B earth switch; return it to the planner.

No device was operated or locked.



Source: [Synthetic Isolation Plan + Control Room Snapshot]

### isolation_check - PTW-4473

**Isolation Check: PTW-4473 Hilltop Line 3** (live state as of Tue 10 Mar 2026 06:30)

**Plan vs required points: PASS (3 of 3)**

| Point | Type | Required state | Plan |
|---|---|---|---|
| ISO-L3-A | Line recloser | Open | In plan |
| ISO-L3-B | Portable earths | Applied | In plan |
| ISO-L3-C | Lockout padlock | Applied | In plan |

**Live switching state:**

| Device | Type | State | Lockout |
|---|---|---|---|
| RC-HT-03 | Recloser | Open | Applied |
| DS-HT-03 | Disconnector | Open | Applied |

**Result: Isolation confirmed** against the plan and the live switching state.

No device was operated or locked.



Source: [Synthetic Isolation Plan + Control Room Snapshot]

### authorization_route - PTW-4471

**Sign-off Route: PTW-4471 Cedar Hill Substation** (from Tue 10 Mar 2026 06:30)

| Stage | Accountable | Target time | Due by |
|---|---|---|---|
| Authorized person review | Lee Carter, authorized person | 120 min | 08:30 |
| Site manager endorsement | Site manager | 90 min | 10:00 |
| Permit office issue | Permit office | 30 min | 10:30 |

**Next sign-off:** Lee Carter, authorized person (Authorized person review), priority P1 (High risk).
**Earliest issue:** 10:30. On track: ready 30 minutes before the 11:00 start.
**Condition:** the permit can only be issued once the live isolation is confirmed.

Routing note prepared for the permit office; no sign-off was given or requested.



Source: [Synthetic Permit Workflow]

### authorization_route - PTW-4472

**Sign-off Route: PTW-4472 (Blocked)**

The permit cannot enter sign-off: the isolation plan is incomplete. It returns to the planner, and the requested 10:00 start is at risk.



Source: [Synthetic Permit Workflow]

### authorization_route - PTW-4473

**Sign-off Route: PTW-4473 Hilltop Line 3** (from Tue 10 Mar 2026 06:30)

| Stage | Accountable | Target time | Due by |
|---|---|---|---|
| Supervisor review | Shift supervisor | 60 min | 07:30 |
| Authorized person review | Lee Carter, authorized person | 120 min | 09:30 |
| Site manager endorsement | Site manager | 90 min | 11:00 |
| Permit office issue | Permit office | 30 min | 11:30 |

**Next sign-off:** Shift supervisor (Supervisor review), priority P2 (Medium risk).
**Earliest issue:** 11:30. On track: ready 90 minutes before the 13:00 start.
**Condition:** the permit can only be issued once the live isolation is confirmed.

Routing note prepared for the permit office; no sign-off was given or requested.



Source: [Synthetic Permit Workflow]

### crew_briefing - PTW-4471

**Crew Briefing: PTW-4471 crew CR-12**

**Briefing topics:** isolation points and lockouts, PPE check, emergency contacts and muster point, site hazards (Electric shock or arc flash, Hot oil contact, Manual handling of heavy components).

| Crew member | Role | Acknowledgement |
|---|---|---|
| Morgan Hayes | Crew lead | Acknowledged |
| Ravi Kumar | Electrician | Acknowledged |
| Elena Novak | Electrician | Acknowledged |
| Chris Dale | Apprentice | Not yet |

**Status:** Incomplete: 3 of 4 acknowledged. Work cannot start until Chris Dale acknowledges.

Briefing sheet prepared for the crew lead; no one was messaged.



Source: [Synthetic Crew Briefing Records]

### crew_briefing - PTW-4472

**Crew Briefing: PTW-4472 crew CR-07**

**Briefing topics:** isolation points and lockouts, PPE check, emergency contacts and muster point, site hazards (Striking a live cable while digging, Confined space in the joint pit, Heavy cable handling).

| Crew member | Role | Acknowledgement |
|---|---|---|
| Jordan Wells | Crew lead | Not yet |
| Aisha Bello | Cable jointer | Not yet |
| Tom Reyes | Cable jointer | Not yet |

**Status:** Incomplete: 0 of 3 acknowledged. Work cannot start until Jordan Wells, Aisha Bello, Tom Reyes acknowledge.

Briefing sheet prepared for the crew lead; no one was messaged.



Source: [Synthetic Crew Briefing Records]

### crew_briefing - PTW-4473

**Crew Briefing: PTW-4473 crew CR-21**

**Briefing topics:** isolation points and lockouts, PPE check, emergency contacts and muster point, site hazards (Working at height, Adjacent live conductors, Wind on the elevated platform).

| Crew member | Role | Acknowledgement |
|---|---|---|
| Priya Raman | Crew lead | Acknowledged |
| Leo Grant | Line worker | Acknowledged |
| Nina Holt | Line worker | Acknowledged |

**Status:** Complete: every crew member has acknowledged.

Briefing sheet prepared for the crew lead; no one was messaged.



Source: [Synthetic Crew Briefing Records]

### clearance_check - PTW-4471

**Permit Clearance Check: PTW-4471 Cedar Hill Substation**

| Check | Start | Close |
|---|---|---|
| People on site | 4 | 4 |
| Tools | 18 issued | 17 returned |
| Area safe | | Yes |
| Work complete | | Yes |

**Close-out entered:** 16:40 by Morgan Hayes
**Clearance status:** Held for review

**Issues:**
- Tools: 18 issued, 17 returned (1 unaccounted for)

**Next step:** the crew lead resolves each issue (for a tool shortfall, finds the missing tool) before the authorized person clears the permit and the control room restores supply.

The permit was not closed.



Source: [Synthetic Close-out Records]

### clearance_check - PTW-4472

**Permit Clearance Check: PTW-4472 Riverside Feeder 7**

| Check | Start | Close |
|---|---|---|
| People on site | 3 | 3 |
| Tools | 12 issued | 12 returned |
| Area safe | | Yes |
| Work complete | | No |

**Close-out entered:** Not yet entered
**Clearance status:** Held for review

**Issues:**
- Work not marked complete

**Next step:** the crew lead resolves each issue (for a tool shortfall, finds the missing tool) before the authorized person clears the permit and the control room restores supply.

The permit was not closed.



Source: [Synthetic Close-out Records]

### clearance_check - PTW-4473

**Permit Clearance Check: PTW-4473 Hilltop Line 3**

| Check | Start | Close |
|---|---|---|
| People on site | 3 | 3 |
| Tools | 15 issued | 15 returned |
| Area safe | | Yes |
| Work complete | | Yes |

**Close-out entered:** 17:10 by Priya Raman
**Clearance status:** Ready to clear

**Issues:**
- None

**Next step:** the authorized person reviews and clears the permit.

The permit was not closed.



Source: [Synthetic Close-out Records]

### safety_kpis

**Permit Safety Roll-up: Northwind Energy Networks** (30 days to Tue 10 Mar 2026)

| Measure | Value |
|---|---|
| Permits issued | 212 |
| Closed on time | 196 (92%) |
| Near misses reported | 5 |
| Average permit cycle | 18.4 hours |
| Lockout gaps caught before work | 7 |
| Isolation plans returned to planner | 4 |

**Top hazards this month:**
1. Electric shock or arc flash
2. Working at height
3. Striking a live cable while digging
4. Confined space

**Focus:** lockout gaps are the most frequent pre-start finding; keep the live isolation check before every crew briefing.



Source: [Synthetic Permit Analytics Snapshot]

### work_request_check - WR-9081

**Work Request Check: WR-9081** (raised by Jordan Wells, crew lead CR-07, planned Thu 12 Mar 2026 09:00)

| Required field | Entered | Check |
|---|---|---|
| Work type | Cable fault location and repair | Complete |
| Location | Riverside Feeder 9 | Complete |
| Asset | Cable section RV9-03 | Complete |
| Isolation points | ISO-F9-A, ISO-F9-B, ISO-F9-C, ISO-F9-D | Complete |
| Crew and competencies | Jordan Wells (authorized person), Aisha Bello, Tom Reyes (cable jointers) | Complete |
| Method statement | MS-UG-12 Cable joint repair | Complete |

**Result: Complete.** Every required field is filled; the permit coordinator can raise the permit and start the risk assessment.

No permit was raised and the request was not returned; the permit coordinator decides.



Source: [Synthetic Work Requests]

### work_request_check - WR-9083

**Work Request Check: WR-9083** (raised by Priya Raman, crew lead CR-21, planned Thu 12 Mar 2026 08:00)

| Required field | Entered | Check |
|---|---|---|
| Work type | Pole replacement | Complete |
| Location | Hilltop Line 3, pole 3-22 | Complete |
| Asset | Pole 3-22 and stay | Complete |
| Isolation points | (blank) | MISSING: No isolation points listed for an overhead line job |
| Crew and competencies | Priya Raman, Leo Grant, Nina Holt (competencies not listed) | MISSING: Competencies not listed for any crew member |
| Method statement | MS-OH-04 Pole replacement | Complete |

**Result: Not ready to raise a permit.** 2 of 6 required fields need work. Return it to Priya Raman, crew lead CR-21 with the gaps above.

No permit was raised and the request was not returned; the permit coordinator decides.



Source: [Synthetic Work Requests]

### isolation_confirmation - PTW-4471

**Isolation Confirmation: PTW-4471 Cedar Hill Substation**

**Status: Not confirmed.** CB-CH-02 lockout not applied.

The permit stays at its current stage and the crew (Morgan Hayes, Ravi Kumar, Elena Novak, Chris Dale) must not be told the isolation is in place. Ask the control room to correct the isolation and record the confirmation in the distribution management system.

No device was operated, the permit status was not changed and no one was notified.



Source: [Synthetic Control Room Confirmations]

### isolation_confirmation - PTW-4472

**Isolation Confirmation: PTW-4472 Riverside Feeder 7**

**Status: Not confirmed.** ISO-F7-B earth switch missing from the isolation plan.

The permit stays at its current stage and the crew (Jordan Wells, Aisha Bello, Tom Reyes) must not be told the isolation is in place. Ask the control room to correct the isolation and record the confirmation in the distribution management system.

No device was operated, the permit status was not changed and no one was notified.



Source: [Synthetic Control Room Confirmations]

### isolation_confirmation - PTW-4473

**Isolation Confirmation: PTW-4473 Hilltop Line 3**

**Status: Confirmed by the control room.** Sam Ortiz, control engineer at 06:20, switching log DMS-SW-55102.

- RC-HT-03 recloser open and locked
- DS-HT-03 disconnector open and locked

**Draft permit status update:** Isolation confirmed (DMS-SW-55102); ready for crew acceptance at the 13:00 start once sign-offs are complete.

**Draft crew notification (crew CR-21: Priya Raman, Leo Grant, Nina Holt):** "The isolation for PTW-4473 Hilltop Line 3 Span 3-14 to 3-15 is confirmed by the control room (DMS-SW-55102). Do not start until your crew lead has accepted the permit on site and the safety brief is done."

Drafts for the permit coordinator to send; the permit status was not changed and no one was notified.



Source: [Synthetic Control Room Confirmations]

### acceptance_readiness - PTW-4471

**Permit Acceptance Readiness: PTW-4471 Cedar Hill Substation** (crew lead Morgan Hayes)

| Before the crew lead accepts | Met |
|---|---|
| Isolation confirmed by the control room | No |
| All sign-offs complete (permit issued) | No |
| Safety brief acknowledged by every crew member | No |

**Crew log to record on acceptance (crew CR-12):**

| Crew member | Role | Briefing |
|---|---|---|
| Morgan Hayes | Crew lead | Acknowledged |
| Ravi Kumar | Electrician | Acknowledged |
| Elena Novak | Electrician | Acknowledged |
| Chris Dale | Apprentice | Not yet |

**Result:** Not ready to accept. Outstanding: Isolation confirmed by the control room; All sign-offs complete (permit issued); Safety brief not acknowledged by Chris Dale. Morgan Hayes accepts on the mobile app only when every item is met, then logs every crew member on the live work.

The permit was not accepted and no one was messaged.



Source: [Synthetic Permit Snapshot + Crew Briefing Records]

### acceptance_readiness - PTW-4472

**Permit Acceptance Readiness: PTW-4472 Riverside Feeder 7** (crew lead Jordan Wells)

| Before the crew lead accepts | Met |
|---|---|
| Isolation confirmed by the control room | No |
| All sign-offs complete (permit issued) | No |
| Safety brief acknowledged by every crew member | No |

**Crew log to record on acceptance (crew CR-07):**

| Crew member | Role | Briefing |
|---|---|---|
| Jordan Wells | Crew lead | Not yet |
| Aisha Bello | Cable jointer | Not yet |
| Tom Reyes | Cable jointer | Not yet |

**Result:** Not ready to accept. Outstanding: Isolation confirmed by the control room; All sign-offs complete (permit issued); Safety brief not acknowledged by Jordan Wells, Aisha Bello, Tom Reyes. Jordan Wells accepts on the mobile app only when every item is met, then logs every crew member on the live work.

The permit was not accepted and no one was messaged.



Source: [Synthetic Permit Snapshot + Crew Briefing Records]

### acceptance_readiness - PTW-4473

**Permit Acceptance Readiness: PTW-4473 Hilltop Line 3** (crew lead Priya Raman)

| Before the crew lead accepts | Met |
|---|---|
| Isolation confirmed by the control room | Yes |
| All sign-offs complete (permit issued) | No |
| Safety brief acknowledged by every crew member | Yes |

**Crew log to record on acceptance (crew CR-21):**

| Crew member | Role | Briefing |
|---|---|---|
| Priya Raman | Crew lead | Acknowledged |
| Leo Grant | Line worker | Acknowledged |
| Nina Holt | Line worker | Acknowledged |

**Result:** Not ready to accept. Outstanding: All sign-offs complete (permit issued). Priya Raman accepts on the mobile app only when every item is met, then logs every crew member on the live work.

The permit was not accepted and no one was messaged.



Source: [Synthetic Permit Snapshot + Crew Briefing Records]

### audit_trail - PTW-4459

**Permit Audit Trail: PTW-4459 Cedar Hill Substation** (Busbar inspection; record PR-2026-0311)

| Step | Event | Time | Signed by |
|---|---|---|---|
| 1 | Work request | Mon 9 Mar 07:10 | Morgan Hayes |
| 2 | Risk assessment | Mon 9 Mar 07:40 | Dana Brooks |
| 3 | Isolation validated | Mon 9 Mar 08:05 | Lee Carter |
| 4 | Sign-offs complete | Mon 9 Mar 09:20 | Permit office |
| 5 | Isolation confirmed by control room | Mon 9 Mar 09:35 | Sam Ortiz |
| 6 | Crew accepted permit | Mon 9 Mar 09:50 | Morgan Hayes |
| 7 | Permit cleared | Mon 9 Mar 15:30 | Lee Carter |
| 8 | Archived | Mon 9 Mar 15:45 | Permit office |

**Chain of custody: Complete.** Every step from request to archive is signed and time-stamped.

Read-only view of the archived record; nothing was changed.



Source: [Synthetic Permit Records Library]

### audit_trail - PTW-4462

**Permit Audit Trail: PTW-4462 Riverside Feeder 7** (Link box inspection; record PR-2026-0314)

| Step | Event | Time | Signed by |
|---|---|---|---|
| 1 | Work request | Mon 9 Mar 08:00 | Jordan Wells |
| 2 | Risk assessment | Mon 9 Mar 08:25 | Dana Brooks |
| 3 | Isolation validated | Mon 9 Mar 08:50 | Lee Carter |
| 4 | Sign-offs complete | Mon 9 Mar 10:05 | Permit office |
| 5 | Isolation confirmed by control room | Mon 9 Mar 10:15 | Sam Ortiz |
| 6 | Crew accepted permit | Mon 9 Mar 10:30 | Jordan Wells |
| 7 | Permit cleared | Mon 9 Mar 14:10 | MISSING signature |
| 8 | Archived | Mon 9 Mar 14:20 | Permit office |

**Chain of custody: Incomplete.** Permit cleared has no signature; flag it to the permit office for correction and include it in the monthly assurance review.

Read-only view of the archived record; nothing was changed.



Source: [Synthetic Permit Records Library]

## Record matching

A permit is selected by its ID, case-insensitive (PTW-4471 Cedar Hill Substation, PTW-4472 Riverside Feeder 7, PTW-4473 Hilltop Line 3). With no permit named, the default is `PTW-4471`. A value that matches no record returns a not-found message listing the fictional records and never falls back to another record.

A work request is selected by its ID, case-insensitive (WR-9081 Riverside Feeder 9, WR-9083 Hilltop Line 3); with none named, the default is `WR-9083`. An archived permit for the audit trail is selected by its ID (PTW-4459 Cedar Hill Substation, PTW-4462 Riverside Feeder 7); with none named, the default is `PTW-4459`. Isolation confirmation and acceptance readiness use the live permits above, default `PTW-4471`.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| PTW-01 | Permit Coordinator | permit_queue | Which work permits are waiting for today? | PTW-4471; 2 with a blocker; Live isolation not confirmed |
| PTW-02 | Permit Coordinator | risk_assessment | Draft the risk assessment for the Cedar Hill transformer job. | 60 of 100; Arc-rated coveralls; Draft for the authorized person |
| PTW-03 | Authorized Person | isolation_check | Is the isolation for the Cedar Hill job actually in place? | CB-CH-02 lockout not applied; Do not start work; No device was operated |
| PTW-04 | Permit Coordinator | authorization_route | Where is the Cedar Hill permit in the sign-off chain, and will it be ready for the 11:00 start? | Lee Carter; Earliest issue; 10:30 |
| PTW-05 | Crew Lead | crew_briefing | Has the Cedar Hill crew acknowledged the briefing? | 3 of 4 acknowledged; Chris Dale; no one was messaged |
| PTW-06 | Authorized Person | clearance_check | The Cedar Hill crew has finished. Can we close the permit? | Held for review; 1 unaccounted for; The permit was not closed |
| PTW-07 | Operations Manager | safety_kpis | How are we doing on permit safety this month? | 212; Lockout gaps caught before work; Near misses |
| PTW-08 | Crew Lead | work_request_check | Is the Hilltop pole replacement request ready to raise a permit? | WR-9083; Not ready to raise a permit; No isolation points listed |
| PTW-09 | Permit Coordinator | isolation_confirmation | Has the control room confirmed the isolation for the Hilltop Line 3 job? Draft the crew notice. | Sam Ortiz; DMS-SW-55102; Draft crew notification |
| PTW-10 | Crew Lead | acceptance_readiness | Can my crew accept the Cedar Hill permit on site yet? | Not ready to accept; Chris Dale; Isolation confirmed by the control room |
| PTW-11 | Safety Auditor | audit_trail | Pull the audit trail for the archived Riverside link box permit. Is anything missing? | PTW-4462; Permit cleared; MISSING |
