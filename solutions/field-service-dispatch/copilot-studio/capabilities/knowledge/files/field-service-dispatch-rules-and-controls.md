# Field Service Dispatch Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Request filtering accepts case-insensitive exact zone and exact synthetic service-request ID. Unknown filters return no invented request.
2. `dispatch_dashboard` emits `# Field Service Dispatch Dashboard` and orders priority CRITICAL, HIGH, MEDIUM, then LOW.
3. `route_optimization` emits `# Route Optimization by Zone`. Remaining capacity is the sum of `max_jobs - jobs_today`; utilization is `1 - remaining capacity / (technician count * 4)`, rounded to one decimal place.
4. `technician_assignment` requires every requested certification and remaining capacity. Candidate score is efficiency + 10 when in-zone + 5 when status is available or on_break. Highest score wins the review recommendation.
5. For SR-4005, Marcus Thompson is the only qualifying candidate: SCADA systems plus high-voltage certification, Central zone, on_break, efficiency 92, score 107.
6. `emergency_response` emits `# Emergency Response Draft` for emergency or CRITICAL requests and lists certification-eligible responders.
7. No technician is assigned, notified, rerouted, or dispatched. No job, route, customer message, inventory record, or field action is changed.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### FIELD_SERVICE_DISPATCH-01 — Field Operations Manager — `dispatch_dashboard`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-01",
  "persona": "Field Operations Manager",
  "operation": "dispatch_dashboard",
  "prompt": "What critical Central request is unassigned right now?",
  "canonical_kwargs": {
    "operation": "dispatch_dashboard",
    "zone": "Central",
    "service_request_id": "SR-4005"
  },
  "must_include": [
    "Emergency: SCADA communication failure",
    "CRITICAL",
    "No job"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Field Service Dispatch Dashboard

**Total Requests:** 3 | **Unassigned:** 2 | **Available Techs:** 0

| Priority | Request | Type | Zone | Location | Hours | Status |
|----------|---------|------|------|----------|-------|--------|
| CRITICAL | Emergency: SCADA communication failure | emergency | Central | Denver, CO | 3h | unassigned |
| HIGH | Transformer oil leak - Ridgeline Substation | corrective | Central | Moffat County, CO | 6h | unassigned |
| MEDIUM | Quarterly turbine blade inspection - Sweetwater | preventive | Central | Nolan County, TX | 4h | assigned |

> Read-only synthetic dashboard. No job, crew, route, customer message, or inventory record was changed.
```

### FIELD_SERVICE_DISPATCH-02 — Service Director — `route_optimization`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-02",
  "persona": "Service Director",
  "operation": "route_optimization",
  "prompt": "Compare Central zone load and capacity before anyone is rerouted.",
  "canonical_kwargs": {
    "operation": "route_optimization",
    "zone": "Central"
  },
  "must_include": [
    "Central",
    "3",
    "dispatcher must validate"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Route Optimization by Zone

| Zone | States | Technicians | Open Requests | Total Hours | Capacity | Utilization |
|------|--------|------------|---------------|-------------|----------|-------------|
| Central | TX, CO, OK, KS, NM | 2 | 3 | 13h | 4 slots | 50.0% |

> Capacity comparison only. A dispatcher must validate travel, safety, labor, and SLA constraints before rerouting.
```

### FIELD_SERVICE_DISPATCH-03 — Dispatch Coordinator — `technician_assignment`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-03",
  "persona": "Dispatch Coordinator",
  "operation": "technician_assignment",
  "prompt": "Who is the best certified candidate for SR-4005? Do not assign them.",
  "canonical_kwargs": {
    "operation": "technician_assignment",
    "service_request_id": "SR-4005"
  },
  "must_include": [
    "Marcus Thompson",
    "Candidate for dispatcher review",
    "No technician has been assigned"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Technician Assignment Recommendations

## SR-4005: Emergency: SCADA communication failure
Priority: CRITICAL | Required Certs: scada_systems, electrical_high_voltage
Candidates: 1
**Candidate for dispatcher review:** Marcus Thompson (score: 107, efficiency: 92%, in-zone: True)

> Recommendation only. No technician has been assigned, notified, or dispatched.
```

### FIELD_SERVICE_DISPATCH-04 — Emergency Duty Manager — `emergency_response`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-04",
  "persona": "Emergency Duty Manager",
  "operation": "emergency_response",
  "prompt": "Draft the SR-4005 response view without dispatching or notifying anyone.",
  "canonical_kwargs": {
    "operation": "emergency_response",
    "service_request_id": "SR-4005"
  },
  "must_include": [
    "Emergency Response Draft",
    "Marcus Thompson",
    "No field action"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Emergency Response Draft

**Active Emergencies:** 1

## Emergency: SCADA communication failure
- Priority: CRITICAL
- Location: Denver, CO
- Equipment: Ridgeline Substation SCADA
- Estimated Hours: 3

**Eligible Responders:**

| Technician | Status | Current Location |
|-----------|--------|-----------------|
| Marcus Thompson | on_break | Denver, CO |

> Dispatcher approval and established emergency procedures are mandatory. No field action or customer notification has occurred.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
