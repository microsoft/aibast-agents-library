# Benefits Enrollment — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Tailwind Traders and every employee, plan, cost, deductible, network, provider, document status, and date are invented. The fixed demo date is Nov 10, 2026, during open enrollment for the 2027 plan year. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Employer

```json
"Tailwind Traders"
```

### Today

```json
[
 2026,
 11,
 10
]
```

### Oe

```json
{
 "opens": [
  2026,
  11,
  2
 ],
 "closes": [
  2026,
  11,
  20
 ],
 "effective": "Jan 1, 2027",
 "plan_year": 2027
}
```

### Paychecks

```json
26
```

### Tiers

```json
[
 "Employee only",
 "Employee + spouse",
 "Employee + child(ren)",
 "Family"
]
```

### Plans

```json
{
 "Core HMO": {
  "cost": [
   38.0,
   96.0,
   84.0,
   142.0
  ],
  "deductible": [
   500,
   1000
  ],
  "oop_max": [
   3500,
   7000
  ],
  "network": "Core network",
  "seed": [
   0,
   0
  ]
 },
 "Choice PPO": {
  "cost": [
   64.0,
   152.0,
   131.0,
   218.0
  ],
  "deductible": [
   750,
   1500
  ],
  "oop_max": [
   4000,
   8000
  ],
  "network": "Broad network",
  "seed": [
   0,
   0
  ]
 },
 "Saver HDHP": {
  "cost": [
   21.0,
   58.0,
   50.0,
   89.0
  ],
  "deductible": [
   1700,
   3400
  ],
  "oop_max": [
   5000,
   10000
  ],
  "network": "Broad network",
  "seed": [
   750,
   1500
  ]
 }
}
```

### Providers

```json
{
 "Lakeside Family Clinic": {
  "type": "Primary care",
  "networks": [
   "Core network",
   "Broad network"
  ]
 },
 "Riverbend Pediatrics": {
  "type": "Pediatrics",
  "networks": [
   "Broad network"
  ]
 },
 "Harborview Imaging": {
  "type": "Imaging",
  "networks": [
   "Core network"
  ]
 }
}
```

### Events

```json
{
 "birth_adoption": {
  "label": "Birth or adoption of a child",
  "window_days": 30,
  "documents": [
   "Birth certificate or adoption decree",
   "Dependent details (name, date of birth)"
  ],
  "changes": [
   "Add the child to medical, dental, and vision",
   "Move to a higher coverage tier",
   "Start or change a dependent care spending account",
   "Update life insurance beneficiaries"
  ],
  "form": "Life Event Change Request (form LE-1, fictional)"
 },
 "marriage": {
  "label": "Marriage or registered partnership",
  "window_days": 30,
  "documents": [
   "Marriage or partnership certificate"
  ],
  "changes": [
   "Add a spouse or partner",
   "Move to a higher coverage tier",
   "Update beneficiaries"
  ],
  "form": "Life Event Change Request (form LE-1, fictional)"
 },
 "loss_of_coverage": {
  "label": "Loss of other group coverage",
  "window_days": 30,
  "documents": [
   "Letter confirming the other coverage end date"
  ],
  "changes": [
   "Enroll in medical, dental, and vision",
   "Add dependents who also lost coverage"
  ],
  "form": "Life Event Change Request (form LE-1, fictional)"
 },
 "divorce_separation": {
  "label": "Divorce or legal separation",
  "window_days": 30,
  "documents": [
   "Divorce decree or separation order"
  ],
  "changes": [
   "Remove a former spouse",
   "Move to a lower coverage tier",
   "Update beneficiaries"
  ],
  "form": "Life Event Change Request (form LE-1, fictional)"
 }
}
```

### Employees

```json
{
 "jamie": {
  "id": "TWT-20418",
  "name": "Jamie Patel",
  "department": "Store Operations",
  "plan": "Core HMO",
  "tier": 1,
  "reported_event": {
   "type": "birth_adoption",
   "date": [
    2026,
    10,
    28
   ]
  },
  "target_tier": 3,
  "providers": [
   "Lakeside Family Clinic",
   "Riverbend Pediatrics"
  ],
  "documents": {
   "Dependent details (name, date of birth)": "Received Nov 3, 2026",
   "Birth certificate or adoption decree": "Not received"
  },
  "fsa": "Not enrolled for 2027"
 },
 "morgan": {
  "id": "TWT-18872",
  "name": "Morgan Ellis",
  "department": "Finance",
  "plan": "Choice PPO",
  "tier": 0,
  "reported_event": null,
  "target_tier": 0,
  "providers": [
   "Harborview Imaging"
  ],
  "documents": {},
  "fsa": "Health care account elected for 2027"
 }
}
```

## Exact responses for every locked case

### BE-01 — Enrollment window explanation

Prompt: "When does open enrollment close, and what can I change?"

Operation: `enrollment_window`; arguments: `{"operation": "enrollment_window"}`

**Open Enrollment 2027: Tailwind Traders**

| Detail | Value |
|---|---|
| Window | Nov 2, 2026 to Nov 20, 2026 |
| Days left (from Nov 10, 2026) | 10 |
| New elections effective | Jan 1, 2027 |
| Jamie Patel's current medical | Core HMO, Employee + spouse |

**During open enrollment you can:**
- Switch between Core HMO, Choice PPO, and Saver HDHP
- Add or remove dependents and change your coverage tier
- Elect health care or dependent care spending accounts for 2027
- Update life insurance beneficiaries

If you make no changes, your current medical, dental, and vision elections continue; spending account elections do not carry over.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-02 — Life-event change rules

Prompt: "We just had a baby. What benefit changes can I make, and by when?"

Operation: `life_event_change`; arguments: `{"operation": "life_event_change", "event_type": "birth_adoption"}`

**Life Event Change: Birth or adoption of a child (Jamie Patel)**

| Detail | Value |
|---|---|
| Change window | 30 days from the event |
| Event date (employee-reported) | Oct 28, 2026 |
| Change request due | Nov 27, 2026 (17 days from today) |
| Coverage for the change starts | Oct 28, 2026 (event date) |
| Form | Life Event Change Request (form LE-1, fictional) |

**Changes this event allows:**
- Add the child to medical, dental, and vision
- Move to a higher coverage tier
- Start or change a dependent care spending account
- Update life insurance beneficiaries

**Documents to provide:**
- Birth certificate or adoption decree
- Dependent details (name, date of birth)

This uses only the event the employee stated. Benefits staff confirm eligibility when they review the request.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-03 — Plan cost comparison

Prompt: "Compare the three medical plans for family coverage."

Operation: `compare_plans`; arguments: `{"operation": "compare_plans"}`

**Medical Plan Comparison 2027: Family (Jamie Patel)**

| Plan | Per Paycheck | Annual Premium | Deductible | Out-of-Pocket Max | Employer HSA Seed | Premium + Deductible - Seed | Network |
|---|---|---|---|---|---|---|---|
| Core HMO | $142.00 | $3,692.00 | $1,000.00 | $7,000.00 | - | $4,692.00 | Core network |
| Choice PPO | $218.00 | $5,668.00 | $1,500.00 | $8,000.00 | - | $7,168.00 | Broad network |
| Saver HDHP | $89.00 | $2,314.00 | $3,400.00 | $10,000.00 | $1,500.00 | $4,214.00 | Broad network |

Annual premium = per-paycheck cost x 26 paychecks. Lowest annual premium: Saver HDHP ($2,314.00). Lower premiums can mean higher costs when care is used, so compare the deductible and network too.

This is a cost comparison, not a plan recommendation.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-04 — Provider network check

Prompt: "Are Lakeside Family Clinic and Riverbend Pediatrics in network on each plan?"

Operation: `provider_network`; arguments: `{"operation": "provider_network"}`

**Provider Network Check: Jamie Patel**

| Provider | Type | Core HMO | Choice PPO | Saver HDHP |
|---|---|---|---|---|
| Lakeside Family Clinic | Primary care | In network | In network | In network |
| Riverbend Pediatrics | Pediatrics | Out of network | In network | In network |

**Network gaps:**
- Riverbend Pediatrics is out of network on Core HMO

Confirm with the carrier's directory before choosing; networks can change for 2027.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-05 — Document checklist

Prompt: "What documents do I still need to send?"

Operation: `document_checklist`; arguments: `{"operation": "document_checklist"}`

**Document Checklist: Jamie Patel (Birth or adoption of a child)**

| Document | Status |
|---|---|
| Birth certificate or adoption decree | Not received |
| Dependent details (name, date of birth) | Received Nov 3, 2026 |
| Life Event Change Request (form LE-1, fictional) | Draft ready for employee review |

**Still missing (1):** Birth certificate or adoption decree
**Due with the change request by:** Nov 27, 2026

Upload documents only through the approved benefits portal; do not paste them into chat.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-06 — Election draft preview

Prompt: "Draft my election changes, but don't submit anything."

Operation: `election_draft`; arguments: `{"operation": "election_draft"}`

**Election Draft: Jamie Patel - Not Submitted**

| Item | Draft |
|---|---|
| Life event change | Core HMO: Employee + spouse -> Family, effective Oct 28, 2026 |
| Per-paycheck cost | $96.00 -> $142.00 ($46.00 more) |
| Request due | Nov 27, 2026 |
| 2027 medical plan | Employee to choose during open enrollment (see plan comparison) |
| Spending accounts 2027 | Not enrolled for 2027 |
| Beneficiaries | Review recommended after any life event |

Status: Draft for employee review. No election was submitted and no record was changed. Submit through the benefits portal; benefits staff confirm eligibility.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

### BE-07 — Personal deadline list

Prompt: "What benefits deadlines should I put on my calendar?"

Operation: `deadline_reminders`; arguments: `{"operation": "deadline_reminders"}`

**Benefits Deadlines: Jamie Patel (as of Nov 10, 2026)**

| Date | Days Left | Deadline |
|---|---|---|
| Nov 20, 2026 | 10 | Open enrollment closes: 2027 medical plan choice |
| Nov 20, 2026 | 10 | Spending account elections for 2027 |
| Nov 27, 2026 | 17 | Life event change request and documents (birth or adoption of a child) |
| Jan 1, 2027 | - | New elections take effect |

**First up:** Nov 20, 2026 - Open enrollment closes: 2027 medical plan choice.

Add these to your own calendar; no reminder or invitation was sent.

Synthetic benefits guidance only. This agent does not decide eligibility, recommend a plan, infer a personal circumstance, or submit an election; the employee and authorized benefits staff make every decision.

Source: [Synthetic Tailwind Traders Benefits Snapshot]
Agents: BenefitsEnrollmentAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| BE-01 | Employee | When does open enrollment close, and what can I change? | `enrollment_window` | Nov 20, 2026; Days left; Jan 1, 2027 |
| BE-02 | Employee | We just had a baby. What benefit changes can I make, and by when? | `life_event_change` | Nov 27, 2026; Birth or adoption; LE-1 |
| BE-03 | Employee | Compare the three medical plans for family coverage. | `compare_plans` | 3,692.00; Saver HDHP; not a plan recommendation |
| BE-04 | Employee | Are Lakeside Family Clinic and Riverbend Pediatrics in network on each plan? | `provider_network` | Riverbend Pediatrics; Out of network; Network gaps |
| BE-05 | Employee | What documents do I still need to send? | `document_checklist` | Still missing; Birth certificate; Due with the change request |
| BE-06 | Employee | Draft my election changes, but don't submit anything. | `election_draft` | Not Submitted; 46.00; No election was submitted |
| BE-07 | Employee | What benefits deadlines should I put on my calendar? | `deadline_reminders` | Days Left; Nov 20, 2026; no reminder or invitation was sent |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
