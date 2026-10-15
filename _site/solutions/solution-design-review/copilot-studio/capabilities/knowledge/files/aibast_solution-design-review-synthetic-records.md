# Solution Design Review — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Northwind Traders and every name, identifier, date, amount and
> score below are invented for demonstration. Never match them to a real organization or
> person, and never treat them as live data.

## Complete synthetic records

The records below are the complete data the agent uses (one fictional initiative, its stakeholders, seven current-state components, eight non-functional requirements, the target design and the readiness checklist).

```json
{
 "INITIATIVE": {
  "id": "INIT-2026-031",
  "org": "Northwind Traders",
  "project": "Delivery Notifications Platform",
  "driver": "Customers ask where their order is; 38% of contact-center calls are delivery-status questions",
  "objective": "Send proactive, consent-aware delivery updates by text and email from one orchestration service",
  "sponsor": "Avery Lindqvist, VP Customer Operations",
  "business_owner": "Mara Okonjo, Director Customer Experience",
  "technical_owner": "Theo Brandt, Lead Solution Architect",
  "review_date": "2026-08-12"
 },
 "INPUTS": [
  {
   "input": "Solution design template",
   "detail": "4 sections to fill: Vision, Current State, Requirements, Target Design"
  },
  {
   "input": "Discovery session notes",
   "detail": "2 workshops, 41 captured statements"
  },
  {
   "input": "Initiative brief",
   "detail": "INIT-2026-031 Delivery Notifications Platform"
  }
 ],
 "SEQUENCE": [
  "Architecture vision (scope, stakeholders, impacted domains)",
  "Current-state baseline (components in scope)",
  "Non-functional requirements matrix (owners, gaps, variances)",
  "Target design (new, changed and retired components)",
  "Readiness check before the review board"
 ],
 "SCOPE_IN": [
  "Delivery status events from shipment tracking",
  "Text and email notifications",
  "Customer channel preferences and consent",
  "Retirement of the legacy text and batch email tools"
 ],
 "SCOPE_OUT": [
  "Marketing campaigns",
  "In-app push notifications (next phase)",
  "Carrier contract changes"
 ],
 "CONSTRAINTS": [
  "Consent must be checked before every send",
  "Launch before the peak season freeze on 2026-10-15",
  "Reuse the existing integration bus"
 ],
 "DOMAINS": {
  "Business": true,
  "Data": true,
  "Application": true,
  "Technology": true
 },
 "WORKGROUPS": [
  "Interfaces and APIs",
  "Information security",
  "Data protection"
 ],
 "COMPONENTS": [
  {
   "id": "CI-101",
   "name": "Order Management System",
   "domain": "Application",
   "owner": "Order Platform team",
   "status": "Supported"
  },
  {
   "id": "CI-102",
   "name": "Customer Profile Store",
   "domain": "Data",
   "owner": "Customer Data team",
   "status": "Supported"
  },
  {
   "id": "CI-103",
   "name": "Legacy Text Gateway",
   "domain": "Technology",
   "owner": "Messaging team",
   "status": "End of support 2026-12-31"
  },
  {
   "id": "CI-104",
   "name": "Shipment Tracking Service",
   "domain": "Application",
   "owner": "Logistics Apps team",
   "status": "Supported"
  },
  {
   "id": "CI-105",
   "name": "Batch Email Scheduler",
   "domain": "Application",
   "owner": "Messaging team",
   "status": "End of support 2026-09-30"
  },
  {
   "id": "CI-106",
   "name": "Integration Bus",
   "domain": "Technology",
   "owner": "Middleware team",
   "status": "Supported"
  },
  {
   "id": "CI-107",
   "name": "Consent Records Table",
   "domain": "Data",
   "owner": "Privacy and Compliance team",
   "status": "Supported"
  }
 ],
 "NFRS": [
  {
   "id": "NFR-01",
   "area": "Availability",
   "criterion": "99.9% monthly availability",
   "owner": "Operations Engineering",
   "status": "Met in design"
  },
  {
   "id": "NFR-02",
   "area": "Latency",
   "criterion": "Notification sent within 60 seconds of the event (p95)",
   "owner": "Messaging team",
   "status": "Met in design"
  },
  {
   "id": "NFR-03",
   "area": "Privacy",
   "criterion": "Consent checked before every send",
   "owner": "Privacy and Compliance team",
   "status": "Met in design"
  },
  {
   "id": "NFR-04",
   "area": "Retention",
   "criterion": "Message history kept 13 months, then purged",
   "owner": "",
   "status": "Gap"
  },
  {
   "id": "NFR-05",
   "area": "Security",
   "criterion": "Encryption in transit and at rest",
   "owner": "Information Security team",
   "status": "Met in design"
  },
  {
   "id": "NFR-06",
   "area": "Capacity",
   "criterion": "40 messages per second at peak",
   "owner": "Messaging team",
   "status": "Variance candidate",
   "note": "Launch design supports 25 per second; scale-out planned for phase 2"
  },
  {
   "id": "NFR-07",
   "area": "Auditability",
   "criterion": "Every send logged with the consent decision",
   "owner": "",
   "status": "Gap"
  },
  {
   "id": "NFR-08",
   "area": "Accessibility",
   "criterion": "Message templates meet the accessibility standard",
   "owner": "Customer Content team",
   "status": "Met in design"
  }
 ],
 "TARGET": {
  "new": [
   {
    "id": "CI-201",
    "name": "Notification Orchestrator",
    "domain": "Application"
   },
   {
    "id": "CI-202",
    "name": "Preference Center API",
    "domain": "Application"
   },
   {
    "id": "CI-203",
    "name": "Delivery Event Stream",
    "domain": "Technology"
   }
  ],
  "changed": [
   {
    "id": "CI-104",
    "name": "Shipment Tracking Service",
    "change": "Publishes delivery status events"
   },
   {
    "id": "CI-107",
    "name": "Consent Records Table",
    "change": "Adds per-channel preference fields"
   }
  ],
  "retired": [
   {
    "id": "CI-103",
    "name": "Legacy Text Gateway",
    "change": "Replaced by the orchestrator's text channel"
   },
   {
    "id": "CI-105",
    "name": "Batch Email Scheduler",
    "change": "Replaced by the orchestrator's email channel"
   }
  ],
  "domains": [
   "Business",
   "Data",
   "Application",
   "Technology"
  ],
  "diagrams": [
   "Business",
   "Data",
   "Application",
   "Technology"
  ]
 },
 "SEVERITY_ORDER": [
  "HIGH",
  "MED",
  "LOW"
 ]
}
```

## Locked-case evidence contract

Each locked case is one natural-language prompt routed to one operation. The answer must
contain every listed evidence value exactly as recorded.

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| SDR-01 | Solution Architect | I have the design template, the discovery notes and the initiative brief for the delivery notifications project. Walk me through where to start. | `design_intake` | INIT-2026-031; 3 inputs received; Recommended fill sequence |
| SDR-02 | Solution Architect | Draft the vision: scope, stakeholders and which architecture domains are impacted. | `architecture_vision` | Avery Lindqvist; 4 of 4; Data protection |
| SDR-03 | Solution Architect | What does the current state look like for the systems in scope? | `current_state` | CI-103; End of support; no current-state baseline for the Business domain |
| SDR-04 | Enterprise Architecture Lead | Which non-functional requirements apply, and who owns each one? | `requirements_matrix` | NFR-04; MISSING OWNER; 1 variance candidate |
| SDR-05 | Solution Architect | Draft the target design and list what changes in the inventory. | `target_design` | Notification Orchestrator; 3 new, 2 changed, 2 retired; not registered by this agent |
| SDR-06 | Review Board Coordinator | Is this design ready for the review board? | `readiness_check` | 70%; Revise before the review board; Not submitted to the review board |

## Complete operation outputs

The deterministic output of every operation on the fixed snapshot follows. Answers must
keep these identifiers, figures and tables.

### SDR-01 — Design intake and plan (`design_intake`)

# Design Intake - INIT-2026-031 Delivery Notifications Platform

**Organization:** Northwind Traders | **Review board date:** 2026-08-12

| Input received | Detail |
|----------------|--------|
| Solution design template | 4 sections to fill: Vision, Current State, Requirements, Target Design |
| Discovery session notes | 2 workshops, 41 captured statements |
| Initiative brief | INIT-2026-031 Delivery Notifications Platform |

**Recommended fill sequence:**
1. Architecture vision (scope, stakeholders, impacted domains)
2. Current-state baseline (components in scope)
3. Non-functional requirements matrix (owners, gaps, variances)
4. Target design (new, changed and retired components)
5. Readiness check before the review board

3 inputs received; 5 steps from intake to readiness. Start with the vision.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.

### SDR-02 — Architecture vision draft (`architecture_vision`)

# Architecture Vision - DRAFT (INIT-2026-031)

**Business driver:** Customers ask where their order is; 38% of contact-center calls are delivery-status questions.
**Objective:** Send proactive, consent-aware delivery updates by text and email from one orchestration service.

| Stakeholder | Role |
|-------------|------|
| Avery Lindqvist, VP Customer Operations | Executive sponsor |
| Mara Okonjo, Director Customer Experience | Business owner |
| Theo Brandt, Lead Solution Architect | Technical owner |

**In scope:** Delivery status events from shipment tracking; Text and email notifications; Customer channel preferences and consent; Retirement of the legacy text and batch email tools.
**Out of scope:** Marketing campaigns; In-app push notifications (next phase); Carrier contract changes.

**Impacted domains (4 of 4):** Business, Data, Application, Technology.
**Constraints:** Consent must be checked before every send; Launch before the peak season freeze on 2026-10-15; Reuse the existing integration bus.
**Review workgroups:** Interfaces and APIs, Information security, Data protection.

Draft for the architect to edit. Next: the current-state baseline.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.

### SDR-03 — Current-state baseline (`current_state`)

# Current-State Baseline - 7 Components in Scope

| Component | Name | Domain | Owner | Lifecycle |
|-----------|------|--------|-------|-----------|
| CI-101 | Order Management System | Application | Order Platform team | Supported |
| CI-102 | Customer Profile Store | Data | Customer Data team | Supported |
| CI-103 | Legacy Text Gateway | Technology | Messaging team | End of support 2026-12-31 |
| CI-104 | Shipment Tracking Service | Application | Logistics Apps team | Supported |
| CI-105 | Batch Email Scheduler | Application | Messaging team | End of support 2026-09-30 |
| CI-106 | Integration Bus | Technology | Middleware team | Supported |
| CI-107 | Consent Records Table | Data | Privacy and Compliance team | Supported |

**End of support:** 2 components - CI-103 Legacy Text Gateway, CI-105 Batch Email Scheduler.
**Domains with a baseline:** Application, Data, Technology.
**Gap:** no current-state baseline for the Business domain (process and capability view); add it before the review.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.

### SDR-04 — Non-functional requirements matrix (`requirements_matrix`)

# Non-Functional Requirements Matrix - 8 Requirements

| ID | Area | Acceptance criterion | Owner | Status |
|----|------|----------------------|-------|--------|
| NFR-01 | Availability | 99.9% monthly availability | Operations Engineering | Met in design |
| NFR-02 | Latency | Notification sent within 60 seconds of the event (p95) | Messaging team | Met in design |
| NFR-03 | Privacy | Consent checked before every send | Privacy and Compliance team | Met in design |
| NFR-04 | Retention | Message history kept 13 months, then purged | MISSING OWNER | Gap |
| NFR-05 | Security | Encryption in transit and at rest | Information Security team | Met in design |
| NFR-06 | Capacity | 40 messages per second at peak | Messaging team | Variance candidate - Launch design supports 25 per second; scale-out planned for phase 2 |
| NFR-07 | Auditability | Every send logged with the consent decision | MISSING OWNER | Gap |
| NFR-08 | Accessibility | Message templates meet the accessibility standard | Customer Content team | Met in design |

**Summary:** 5 met in design, 2 missing owners (NFR-04, NFR-07), 1 variance candidate (NFR-06).
Next: name owners for the gaps and write the architect response for the variance.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.

### SDR-05 — Target design and inventory delta (`target_design`)

# Target Design - DRAFT (Delivery Notifications Platform)

One notification orchestrator consumes delivery events from the integration bus, checks consent and channel preference, and sends by text or email; the two legacy senders are retired.

| Change | Component | Name | Detail |
|--------|-----------|------|--------|
| New | CI-201 | Notification Orchestrator | Application |
| New | CI-202 | Preference Center API | Application |
| New | CI-203 | Delivery Event Stream | Technology |
| Changed | CI-104 | Shipment Tracking Service | Publishes delivery status events |
| Changed | CI-107 | Consent Records Table | Adds per-channel preference fields |
| Retired | CI-103 | Legacy Text Gateway | Replaced by the orchestrator's text channel |
| Retired | CI-105 | Batch Email Scheduler | Replaced by the orchestrator's email channel |

**Inventory delta:** 3 new, 2 changed, 2 retired = 7 inventory updates to register after build (not registered by this agent).
**Target domains drafted:** Business, Data, Application, Technology; a diagram reference is included for each.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.

### SDR-06 — Review-board readiness check (`readiness_check`)

# Review-Board Readiness - INIT-2026-031

**Confidence: 70%** (7 of 10 checks pass) | **Gaps:** 2 HIGH, 1 MED, 0 LOW | **Recommendation:** Revise before the review board

| Severity | Gap | Evidence |
|----------|-----|----------|
| HIGH | Every impacted domain has a current-state baseline | Missing: Business |
| HIGH | Every non-functional requirement has a named owner | No owner: NFR-04, NFR-07 |
| MED | Every variance has a documented architect response | Open: NFR-06 |

**To close before the review:** add the Business baseline; name owners for NFR-04 and NFR-07; write the architect response for NFR-06.
Closing all 3 gaps takes the checklist to 10 of 10.

Status: self-check for the architect. Not submitted to the review board.

> Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the review board, no inventory record was changed, and no design decision was made; the architect owns every section.
