# Content Launch Clearance — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The media company and every title, territory, contract document, clause, window, holdback, reviewer, and approval draft are invented. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Titles

```json
{
 "silver-harbor": {
  "name": "Silver Harbor",
  "territory": "UK",
  "platform": "Owned streaming service",
  "requested_launch": "Not yet confirmed",
  "contract": "UK Rights Agreement SH-UK-2026",
  "clause": "3.1",
  "contract_status": "Approved",
  "clause_text": "Exclusive UK subscription streaming rights are granted for 24 months from the end of the theatrical holdback.",
  "clearance": "Cleared from the end of the theatrical holdback (in 24 days)"
 },
 "paper-lantern": {
  "name": "Paper Lantern",
  "territory": "Canada",
  "platform": "Owned streaming service",
  "requested_launch": "In 33 days",
  "contract": "Canada Rights Agreement PL-CA-2026",
  "clause": "2.4",
  "contract_status": "Approved",
  "clause_text": "Canadian subscription streaming rights commence at the start of the window; no earlier digital launch is permitted.",
  "clearance": "Not cleared until the window opens (in 40 days)"
 },
 "meadow-current": {
  "name": "Meadow Current",
  "territory": "Australia",
  "platform": "Owned streaming service",
  "requested_launch": "In 21 days",
  "contract": "ANZ Rights Agreement MC-ANZ-2026",
  "clause": "4.2",
  "contract_status": "Approved",
  "clause_text": "Non-exclusive subscription streaming rights in Australia commence at the start of the window.",
  "clearance": "Cleared from the window opening (in 14 days)"
 },
 "northern-signal": {
  "name": "Northern Signal",
  "territory": "UK",
  "platform": "Owned streaming service",
  "requested_launch": "Not yet confirmed",
  "contract": "UK Rights Agreement NS-UK-2026",
  "clause": "3.1",
  "contract_status": "Pending review",
  "clause_text": "UK subscription streaming rights are subject to an unsigned amendment.",
  "clearance": "Clearance unavailable"
 },
 "driftwood-lane": {
  "name": "Driftwood Lane",
  "territory": "UK",
  "platform": "Owned streaming service",
  "requested_launch": "Not yet confirmed",
  "contract": "UK Rights Agreement DL-UK-2026",
  "clause": "6.1",
  "contract_status": "Pending review",
  "clause_text": "The licensed territory list excludes the UK until a territory amendment is signed.",
  "clearance": "Clearance unavailable"
 }
}
```

### Windows

```json
{
 "silver-harbor": {
  "window": "Exclusive subscription streaming",
  "opens": "In 24 days",
  "runs": "24 months",
  "holdback": "Theatrical holdback",
  "restriction": "UK launch must not occur before the theatrical holdback ends in 24 days.",
  "earliest_launch": "In 24 days"
 },
 "paper-lantern": {
  "window": "Subscription streaming",
  "opens": "In 40 days",
  "runs": "Not stated in the clause",
  "holdback": "No earlier digital launch",
  "restriction": "Canadian launch must not occur before the window opens in 40 days.",
  "earliest_launch": "In 40 days"
 },
 "meadow-current": {
  "window": "Non-exclusive subscription streaming",
  "opens": "In 14 days",
  "runs": "Not stated in the clause",
  "holdback": "None",
  "restriction": "No scheduling restriction after the window opens in 14 days.",
  "earliest_launch": "In 14 days"
 },
 "northern-signal": {
  "window": "Subscription streaming (subject to amendment)",
  "opens": "Not set",
  "runs": "Not set",
  "holdback": "Unsigned contract amendment",
  "restriction": "Launch blocked while contract amendment is unsigned.",
  "earliest_launch": "None until the amendment is signed"
 },
 "driftwood-lane": {
  "window": "Subscription streaming (territory pending)",
  "opens": "Not set",
  "runs": "Not set",
  "holdback": "Territory amendment",
  "restriction": "Launch is blocked pending a territory amendment.",
  "earliest_launch": "None until the territory amendment is signed"
 }
}
```

### Readiness

```json
{
 "silver-harbor": {
  "missing": [
   "Confirmed requested UK launch date"
  ],
  "rights_status": "Pending submission",
  "reviewer": "Helena Brooks",
  "next_step": "Programming confirms the UK launch date on or after the holdback end, then the request goes to the rights team."
 },
 "paper-lantern": {
  "missing": [],
  "rights_status": "Pending rights approval",
  "reviewer": "Tomas Reyes",
  "next_step": "Move the requested launch from 33 days out to the window opening in 40 days before the rights team approves."
 },
 "meadow-current": {
  "missing": [],
  "rights_status": "Approved",
  "reviewer": "Tomas Reyes",
  "next_step": "No rights action needed; programming may schedule from the window opening."
 },
 "northern-signal": {
  "missing": [
   "Approved contract amendment",
   "Requested launch date"
  ],
  "rights_status": "On hold",
  "reviewer": "Helena Brooks",
  "next_step": "Rights team obtains the signed amendment before any launch date is set."
 },
 "driftwood-lane": {
  "missing": [
   "Signed territory amendment",
   "Requested launch date"
  ],
  "rights_status": "On hold",
  "reviewer": "Helena Brooks",
  "next_step": "Rights team obtains the signed territory amendment before any launch date is set."
 }
}
```

## Exact responses for every locked case

### CLC-01 — Launch clearance

Prompt: "Can we put Silver Harbor on our streaming service in the UK, and which contract clause says so?"

Operation: `launch_clearance`; arguments: `{"operation": "launch_clearance", "title": "Silver Harbor"}`

**Launch Clearance - Silver Harbor**

**Territory:** UK | **Platform:** Owned streaming service | **Requested launch:** Not yet confirmed

**Clearance:** Cleared from the end of the theatrical holdback (in 24 days)

**Contract term cited**
- **Document:** UK Rights Agreement SH-UK-2026 (contract status: Approved)
- **Clause 3.1:** "Exclusive UK subscription streaming rights are granted for 24 months from the end of the theatrical holdback."

**Restriction:** UK launch must not occur before the theatrical holdback ends in 24 days.

> Read-only synthetic snapshot. No title was scheduled or published, no contract was changed and no approval was submitted; every approval request is a draft for the rights team to review.

Source: [Synthetic Content Rights Snapshot]
Agents: ContentLaunchClearanceAgent

### CLC-02 — Distribution window and holdback

Prompt: "Programming wants Paper Lantern live in Canada in about a month. Is there a holdback that blocks that date?"

Operation: `distribution_window`; arguments: `{"operation": "distribution_window", "title": "Paper Lantern"}`

**Distribution Window - Paper Lantern**

**Territory:** Canada | **Platform:** Owned streaming service

| Window | Opens | Runs | Holdback | Earliest launch |
|--------|-------|------|----------|-----------------|
| Subscription streaming | In 40 days | Not stated in the clause | No earlier digital launch | In 40 days |

**Restriction:** Canadian launch must not occur before the window opens in 40 days.
**Source:** Canada Rights Agreement PL-CA-2026, clause 2.4

> Read-only synthetic snapshot. No title was scheduled or published, no contract was changed and no approval was submitted; every approval request is a draft for the rights team to review.

Source: [Synthetic Content Rights Snapshot]
Agents: ContentLaunchClearanceAgent

### CLC-03 — Approval readiness draft

Prompt: "Is Northern Signal ready to come to the rights team for sign-off? What is still missing?"

Operation: `approval_readiness`; arguments: `{"operation": "approval_readiness", "title": "Northern Signal"}`

**Approval Readiness - Northern Signal**

**Rights approval status:** On hold | **Rights reviewer:** Helena Brooks (Rights & Clearances Lead)
**Ready for rights-team approval:** No

**Still missing**
- Approved contract amendment
- Requested launch date

**Draft approval request**
- Title: Northern Signal | Territory: UK | Platform: Owned streaming service
- Clearance: Clearance unavailable (UK Rights Agreement NS-UK-2026, clause 3.1)
- Next step: Rights team obtains the signed amendment before any launch date is set.

> Draft only: no approval was submitted. Read-only synthetic snapshot. No title was scheduled or published, no contract was changed and no approval was submitted; every approval request is a draft for the rights team to review.

Source: [Synthetic Content Rights Snapshot]
Agents: ContentLaunchClearanceAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| CLC-01 | Programming Manager | Can we put Silver Harbor on our streaming service in the UK, and which contract clause says so? | `launch_clearance` | Launch Clearance; UK Rights Agreement SH-UK-2026; theatrical holdback |
| CLC-02 | Distribution Lead | Programming wants Paper Lantern live in Canada in about a month. Is there a holdback that blocks that date? | `distribution_window` | Distribution Window; In 40 days; Canada Rights Agreement PL-CA-2026 |
| CLC-03 | Rights & Clearances Lead | Is Northern Signal ready to come to the rights team for sign-off? What is still missing? | `approval_readiness` | Approval Readiness; Approved contract amendment; Draft only |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
