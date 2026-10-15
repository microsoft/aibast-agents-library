# Permit Management Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Days left = expiration date - the fixed snapshot date 2026-03-02 (never the current date). Critical means fewer than 30 days left.
2. `permit_inventory` reports the portfolio (240 active permits, 63 expiring in 120 days, $2.34M renewal investment, $47M production at risk) and lists the 8 critical permits by days left: Imperial Valley Solar Air Quality 18, Reno Wind Farm Environmental 22, Phoenix Solar Water Use 26, Bakersfield Solar Hazmat 28, then four at 29.
3. `renewal_calendar` marks a lead time MISSED when days left are below the permit's renewal lead time.
4. `compliance_gaps` emits one `renewal_lead_time_missed` gap per missed lead time, CRITICAL below 30 days, with the obligations at risk for that permit type.
5. `application_status` lists already-submitted applications, optionally filtered by facility substring; it never submits or amends.
6. `renewal_plan` lists the prepared action and renewal cost for every critical permit; investment = sum of renewal costs ($685,000); production protected = sum of production at risk ($13.8M); stakeholder alerts are drafts only.
7. A filter that matches no facility returns no invented record.

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
  "prompt": "Show me our permit status and any expiring soon",
  "canonical_kwargs": {
    "operation": "permit_inventory"
  },
  "must_include": [
    "240 active permits",
    "Imperial Valley Solar",
    "$47M"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Permit & License Inventory

I've analyzed all 240 active permits across your facilities. You have 63 permits expiring in the next 120 days, including 8 critical ones needing immediate attention.

## Critical Permits (<30 Days) as of 2026-03-02

| ID | Facility | Permit Type | Days Left | Risk |
|----|----------|-------------|-----------|------|
| PRM-8101 | Imperial Valley Solar | Air Quality | 18 | CRITICAL |
| PRM-8102 | Reno Wind Farm | Environmental | 22 | CRITICAL |
| PRM-8103 | Phoenix Solar | Water Use | 26 | CRITICAL |
| PRM-8104 | Bakersfield Solar | Hazmat | 28 | CRITICAL |
| PRM-8105 | Tehachapi Wind | Avian Protection | 29 | CRITICAL |
| PRM-8106 | Palm Springs Wind | Noise Variance | 29 | CRITICAL |
| PRM-8107 | Yuma Solar | Grading | 29 | CRITICAL |
| PRM-8108 | Mojave Storage | Fire Code | 29 | CRITICAL |

**Total Renewal Investment:** $2.34M across 63 permits
**Production at Risk:** $47M if permits lapse

Source: [Synthetic D365 + SharePoint permit register]

**Next step:** Should I prepare the emergency renewal package for the critical permits?

> Synthetic register only. Verify status with the issuing authority before relying on it.
```

### PERMIT_LICENSE_MANAGEMENT-02 — Permit Coordinator — `renewal_calendar`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-02",
  "persona": "Permit Coordinator",
  "operation": "renewal_calendar",
  "prompt": "Which permit renewals have already missed their lead time, and how many days are left?",
  "canonical_kwargs": {
    "operation": "renewal_calendar"
  },
  "must_include": [
    "Reno Wind Farm",
    "MISSED",
    "No renewal"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Compliance Gap Analysis

**Total Gaps:** 8 | **Critical:** 8

| Permit | Facility | Gap Type | Severity | Detail |
|--------|----------|----------|----------|--------|
| PRM-8101 Air Quality | Imperial Valley Solar | renewal_lead_time_missed | CRITICAL | 18 days left vs 90-day lead time; at risk: Dust control plan, Annual emissions inventory, Quarterly compliance reports |
| PRM-8102 Environmental | Reno Wind Farm | renewal_lead_time_missed | CRITICAL | 22 days left vs 120-day lead time; at risk: Habitat monitoring, Annual environmental report, Mitigation plan updates |
| PRM-8103 Water Use | Phoenix Solar | renewal_lead_time_missed | CRITICAL | 26 days left vs 60-day lead time; at risk: Monthly water use reporting, Annual allocation review, Conservation plan |
| PRM-8104 Hazmat | Bakersfield Solar | renewal_lead_time_missed | CRITICAL | 28 days left vs 60-day lead time; at risk: Hazardous materials business plan, Annual inventory certification, Emergency response plan |
| PRM-8105 Avian Protection | Tehachapi Wind | renewal_lead_time_missed | CRITICAL | 29 days left vs 90-day lead time; at risk: Post-construction fatality monitoring, Annual avian report, Adaptive management plan |
| PRM-8106 Noise Variance | Palm Springs Wind | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Quarterly noise monitoring, Community complaint log |
| PRM-8107 Grading | Yuma Solar | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Erosion control inspection, Grading completion certification |
| PRM-8108 Fire Code | Mojave Storage | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Annual fire inspection, Battery hazard mitigation analysis |

> Triage evidence only, not legal advice. Authorized permit staff must validate obligations and approve remediation.
[PermitLicenseManagementAgent] # Permit Renewal Calendar

Days left are computed from the snapshot date 2026-03-02.

| Permit | Facility | Expiration | Days Left | Lead Time | Lead Time Status |
|--------|----------|-----------|-----------|-----------|------------------|
| PRM-8101 Air Quality | Imperial Valley Solar | 2026-03-20 | 18 | 90 days | MISSED |
| PRM-8102 Environmental | Reno Wind Farm | 2026-03-24 | 22 | 120 days | MISSED |
| PRM-8103 Water Use | Phoenix Solar | 2026-03-28 | 26 | 60 days | MISSED |
| PRM-8104 Hazmat | Bakersfield Solar | 2026-03-30 | 28 | 60 days | MISSED |
| PRM-8105 Avian Protection | Tehachapi Wind | 2026-03-31 | 29 | 90 days | MISSED |
| PRM-8106 Noise Variance | Palm Springs Wind | 2026-03-31 | 29 | 45 days | MISSED |
| PRM-8107 Grading | Yuma Solar | 2026-03-31 | 29 | 45 days | MISSED |
| PRM-8108 Fire Code | Mojave Storage | 2026-03-31 | 29 | 45 days | MISSED |

> Planning reminders only. No renewal, notice, or authority submission has been initiated.
```

### PERMIT_LICENSE_MANAGEMENT-03 — Compliance Manager — `compliance_gaps`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-03",
  "persona": "Compliance Manager",
  "operation": "compliance_gaps",
  "prompt": "What permit evidence gap needs immediate authorized review?",
  "canonical_kwargs": {
    "operation": "compliance_gaps"
  },
  "must_include": [
    "renewal_lead_time_missed",
    "CRITICAL",
    "not legal advice"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Compliance Gap Analysis

**Total Gaps:** 8 | **Critical:** 8

| Permit | Facility | Gap Type | Severity | Detail |
|--------|----------|----------|----------|--------|
| PRM-8101 Air Quality | Imperial Valley Solar | renewal_lead_time_missed | CRITICAL | 18 days left vs 90-day lead time; at risk: Dust control plan, Annual emissions inventory, Quarterly compliance reports |
| PRM-8102 Environmental | Reno Wind Farm | renewal_lead_time_missed | CRITICAL | 22 days left vs 120-day lead time; at risk: Habitat monitoring, Annual environmental report, Mitigation plan updates |
| PRM-8103 Water Use | Phoenix Solar | renewal_lead_time_missed | CRITICAL | 26 days left vs 60-day lead time; at risk: Monthly water use reporting, Annual allocation review, Conservation plan |
| PRM-8104 Hazmat | Bakersfield Solar | renewal_lead_time_missed | CRITICAL | 28 days left vs 60-day lead time; at risk: Hazardous materials business plan, Annual inventory certification, Emergency response plan |
| PRM-8105 Avian Protection | Tehachapi Wind | renewal_lead_time_missed | CRITICAL | 29 days left vs 90-day lead time; at risk: Post-construction fatality monitoring, Annual avian report, Adaptive management plan |
| PRM-8106 Noise Variance | Palm Springs Wind | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Quarterly noise monitoring, Community complaint log |
| PRM-8107 Grading | Yuma Solar | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Erosion control inspection, Grading completion certification |
| PRM-8108 Fire Code | Mojave Storage | renewal_lead_time_missed | CRITICAL | 29 days left vs 45-day lead time; at risk: Annual fire inspection, Battery hazard mitigation analysis |

> Triage evidence only, not legal advice. Authorized permit staff must validate obligations and approve remediation.
```

### PERMIT_LICENSE_MANAGEMENT-04 — Environmental Counsel — `application_status`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-04",
  "persona": "Environmental Counsel",
  "operation": "application_status",
  "prompt": "Where does the Imperial Valley Solar Phase 2 application stand, and did we submit anything today?",
  "canonical_kwargs": {
    "operation": "application_status",
    "facility": "Imperial Valley"
  },
  "must_include": [
    "APP-7102",
    "public_comment",
    "cannot submit"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] # Permit Application Status

**Active Applications:** 1

| ID | Application | Facility | Authority | Submitted | Status | Decision Date | Comments |
|----|-------------|----------|-----------|-----------|--------|--------------|----------|
| APP-7102 | Imperial Valley Solar Phase 2 Conditional Use Permit | Imperial Valley Solar | County planning commission | 2026-01-20 | public_comment | 2026-06-30 | 12 |

> Read-only synthetic tracking. The agent cannot submit, amend, withdraw, or approve an application.
```

### PERMIT_LICENSE_MANAGEMENT-05 — Operations Director — `renewal_plan`

```json
{
  "case_id": "PERMIT_LICENSE_MANAGEMENT-05",
  "persona": "Operations Director",
  "operation": "renewal_plan",
  "prompt": "Start emergency renewals for the critical permits.",
  "canonical_kwargs": {
    "operation": "renewal_plan"
  },
  "must_include": [
    "$685,000",
    "$13.8M",
    "No application was submitted"
  ],
  "expected_agent": "PermitLicenseManagementAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[PermitLicenseManagementAgent] Emergency renewal package prepared for all 8 critical permits, ready for your approval. Expedited processing requests and stakeholder alerts are drafted, not sent.

# Emergency Renewal Plan

| ID | Facility | Permit Type | Days Left | Prepared Action | Renewal Cost |
|----|----------|-------------|-----------|-----------------|--------------|
| PRM-8101 | Imperial Valley Solar | Air Quality | 18 | Expedited air quality renewal application prepared, ready for you to submit | $185,000 |
| PRM-8102 | Reno Wind Farm | Environmental | 22 | Environmental permit vendor shortlisted (2-week turnaround); engagement request drafted | $140,000 |
| PRM-8103 | Phoenix Solar | Water Use | 26 | County approval fast-track request drafted | $95,000 |
| PRM-8104 | Bakersfield Solar | Hazmat | 28 | Hazmat documentation compiled, ready to submit | $80,000 |
| PRM-8105 | Tehachapi Wind | Avian Protection | 29 | Monitoring report assembled for the renewal filing | $60,000 |
| PRM-8106 | Palm Springs Wind | Noise Variance | 29 | Variance renewal letter drafted | $45,000 |
| PRM-8107 | Yuma Solar | Grading | 29 | Grading plan resubmittal package prepared | $40,000 |
| PRM-8108 | Mojave Storage | Fire Code | 29 | Fire code inspection request drafted | $40,000 |

**Investment Required:** $685,000 for critical renewals
**Production Protected:** $13.8M (combined facility capacity)
**Stakeholder Alerts (drafts for Teams and Outlook):** Facility managers, Legal

Draft alert: "Critical permit renewals: 8 permits expire within 30 days. The renewal package is ready for approval; please confirm owners today."

**Monitoring:** daily status review with executive escalation if a renewal slips (recommended cadence).

Source: [Synthetic D365 vendor management + SharePoint]

**Next step:** Would you like me to analyze the Reno Wind Farm permit to see what's needed?

> Prepared for approval only. No application was submitted, no vendor was engaged, and no Teams or Outlook message was sent.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
