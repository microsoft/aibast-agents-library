# Permit Management Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Facility filtering is case-insensitive substring matching against the exact synthetic facility name.
2. `permit_inventory` emits `# Permit & License Inventory` and counts active and expired records only within the selected facility set.
3. `renewal_calendar` emits `# Permit Renewal Calendar` and sorts by expiration date ascending; it is a planning reminder, not a renewal action.
4. `compliance_gaps` creates one CRITICAL `expired_permit` gap for every expired permit. An expired water-discharge permit also creates one HIGH `requirement_at_risk` gap for each listed regulatory requirement.
5. `application_status` emits `# Permit Application Status` from APPLICATIONS and may filter by facility substring.
6. No permit is submitted, renewed, amended, withdrawn, or represented as approved. Legal and permit owners validate obligations and authorize every external action.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### PERMIT_LICENSE_MANAGEMENT-01 — Facility Manager — `permit_inventory`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-01",
  "persona": "Facility Manager",
  "operation": "permit_inventory",
  "prompt": "Which Riverside permit is expired right now?",
  "canonical_kwargs": {
    "operation": "permit_inventory",
    "facility": "Riverside"
  },
  "must_include": [
    "PRM-6002",
    "EXPIRED",
    "Verify status"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Permit & License Inventory

**Total Permits:** 2 | **Active:** 1 | **Expired:** 1

| ID | Permit | Facility | Authority | Status | Expiration | Conditions |
|----|--------|----------|-----------|--------|-----------|-----------|
| PRM-6001 | Title V Air Operating Permit | Riverside Generating Station | CA Air Resources Board | ACTIVE | 2029-06-15 | 24 |
| PRM-6002 | NPDES Stormwater Discharge Permit | Riverside Generating Station | CA State Water Board | EXPIRED | 2026-03-01 | 18 |

> Synthetic register only. Verify status with the issuing authority before relying on it.
```

### PERMIT_LICENSE_MANAGEMENT-02 — Permit Coordinator — `renewal_calendar`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-02",
  "persona": "Permit Coordinator",
  "operation": "renewal_calendar",
  "prompt": "What is the next Riverside renewal deadline I need to prepare for?",
  "canonical_kwargs": {
    "operation": "renewal_calendar",
    "facility": "Riverside"
  },
  "must_include": [
    "NPDES Stormwater Discharge Permit",
    "2026-03-01",
    "No renewal"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Permit Renewal Calendar

| Permit | Facility | Expiration | Status | Lead Time |
|--------|----------|-----------|--------|-----------|
| NPDES Stormwater Discharge Permit | Riverside Generating Station | 2026-03-01 | EXPIRED | 180 days |
| Title V Air Operating Permit | Riverside Generating Station | 2029-06-15 | ACTIVE | 365 days |

> Planning reminders only. No renewal, notice, or authority submission has been initiated.
```

### PERMIT_LICENSE_MANAGEMENT-03 — Compliance Manager — `compliance_gaps`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-03",
  "persona": "Compliance Manager",
  "operation": "compliance_gaps",
  "prompt": "What permit evidence gap needs immediate authorized review at Riverside?",
  "canonical_kwargs": {
    "operation": "compliance_gaps",
    "facility": "Riverside"
  },
  "must_include": [
    "expired_permit",
    "CRITICAL",
    "not legal advice"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Compliance Gap Analysis

**Total Gaps:** 4 | **Critical:** 1

| Permit | Facility | Gap Type | Severity | Detail |
|--------|----------|----------|----------|--------|
| NPDES Stormwater Discharge Permit | Riverside Generating Station | expired_permit | CRITICAL | Permit NPDES-CA-0052841 expired on 2026-03-01 |
| NPDES Stormwater Discharge Permit | Riverside Generating Station | requirement_at_risk | HIGH | Requirement 'Monthly effluent sampling' at risk due to expired permit |
| NPDES Stormwater Discharge Permit | Riverside Generating Station | requirement_at_risk | HIGH | Requirement 'Annual DMR submission' at risk due to expired permit |
| NPDES Stormwater Discharge Permit | Riverside Generating Station | requirement_at_risk | HIGH | Requirement 'Stormwater pollution prevention plan' at risk due to expired permit |

> Triage evidence only, not legal advice. Authorized permit staff must validate obligations and approve remediation.
```

### PERMIT_LICENSE_MANAGEMENT-04 — Environmental Counsel — `application_status`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-04",
  "persona": "Environmental Counsel",
  "operation": "application_status",
  "prompt": "Where does the Riverside gas turbine permit application stand, and did we submit anything today?",
  "canonical_kwargs": {
    "operation": "application_status",
    "facility": "Riverside"
  },
  "must_include": [
    "APP-7002",
    "public_comment",
    "cannot submit"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Permit Application Status

**Active Applications:** 2

| ID | Application | Facility | Authority | Submitted | Status | Decision Date | Comments |
|----|-------------|----------|-----------|-----------|--------|--------------|----------|
| APP-7001 | NPDES Stormwater Discharge Permit Renewal | Riverside Generating Station | CA State Water Board | 2025-09-01 | under_review | 2026-04-15 | 3 |
| APP-7002 | New Source Review - Gas Turbine Expansion | Riverside Generating Station | CA Air Resources Board | 2026-01-20 | public_comment | 2026-06-30 | 12 |

> Read-only synthetic tracking. The agent cannot submit, amend, withdraw, or approve an application.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
