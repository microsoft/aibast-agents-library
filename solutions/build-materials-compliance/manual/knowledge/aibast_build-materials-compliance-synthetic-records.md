# Build Materials Compliance Agent — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Tailspin Civil Works, its three projects, the five vendors and their contacts, and every item, specification, price, certificate date, questionnaire answer and alternate are fictional. Never match them to a real organization, person or live system.

## Complete synthetic records

Each section below is the exact output of one operation over the fixed snapshot (demo defaults). Together they contain every record, figure and rule the pilot may cite.

### Weekly BOM change scan (`weekly_changes`)

**Approved BOM Changes: week of 2026-10-05 (vs scan of 2026-09-28)**

| Project | Item | Quantity | Vendor | Change |
|---|---|---|---|---|
| P-101 Riverside Main Replacement | DI-08 8-inch ductile iron pipe | 2,400 ft | Contoso Pipe & Valve | Quantity 2,000 -> 2,400 |
| P-101 Riverside Main Replacement | GV-08 8-inch resilient wedge gate valve | 12 ea | Fabrikam Castings | New this week |
| P-103 Lakeview Service Lines | CF-06 6-inch restraint coupling | 20 ea | Litware Fittings | Quantity 12 -> 20 |
| P-103 Lakeview Service Lines | MB-12 Polymer meter box | 150 ea | Wingtip Supply | New this week |

**Scan:** 3 projects, 8 BOM lines; 2 new lines and 2 quantity changes since last week.
**Next step:** check every covered item against the materials sourcing rule.

### Materials compliance check (`compliance_check`)

**Materials Compliance Check: 2026-10-05**

| Item | Status | Reason | Cited Evidence | Projects Affected |
|---|---|---|---|---|
| GV-08 8-inch resilient wedge gate valve | NEW Non-compliant | Vendor certificate expired 2026-09-30 | Fabrikam Castings certificate library entry | P-101, P-102 (18 ea) |
| CP-02 1-inch copper service tubing | NEW Non-compliant | Vendor questionnaire answer: final assembly moved to a non-qualifying plant | Litware Fittings questionnaire, answered Oct 2 | P-103 (3,000 ft) |
| CF-06 6-inch restraint coupling | Conflict | Master data says attestation on file; certificate letter lists a different part revision | Litware Fittings certificate letter vs product master data | P-102, P-103 (60 ea) |
| RB-04 No. 4 reinforcing bar | Evidence gap | Product data sheet missing | Product master data | P-101 (800 ft) |

**Result:** 5 covered items checked; 1 compliant, 2 newly non-compliant this week (GV-08, CP-02), 1 certificate conflict and 1 evidence gap. Non-compliant material on approved BOMs: $30,000.
**Next step:** review compliant alternates for GV-08 and CP-02 before ordering.

### Compliant alternates (`compliant_alternates`)

**Compliant Alternates: GV-08 8-inch resilient wedge gate valve (spec GV-8-RW)**

Current: Fabrikam Castings at $1,150/ea - Non-compliant: Vendor certificate expired 2026-09-30. On approved BOMs: P-101 (12), P-102 (6).

| Alternate | Vendor | Spec | Unit Price | Certificate To | Lead Time | Cost Impact | Evidence |
|---|---|---|---|---|---|---|---|
| GV-08B | Contoso Pipe & Valve | GV-8-RW | $1,210 | 2027-03-31 | 14 days | +$1,080 | Ready |
| GV-08C | Wingtip Supply | GV-8-RW | $1,185 | 2027-06-30 | 21 days | +$630 | Data sheet missing |

**Recommended:** GV-08B from Contoso Pipe & Valve: same spec, certificate current to 2027-03-31, cost impact +$1,080 across 18 ea.
**Next step:** approve the substitution so a change request draft can be prepared.

### Vendor certificate watch (`vendor_watch`)

**Vendor Certificate Watch: as of 2026-10-05 (window to 2027-01-03)**

| Vendor | Certificate Expires | Status | Covered Items | Contact |
|---|---|---|---|---|
| Fabrikam Castings | 2026-09-30 | Expired | GV-08 | Jamie Ortiz |
| Adatum Steel | 2026-11-15 | Expires within 90 days | RB-04 | Casey Morgan |
| Litware Fittings | 2026-12-01 | Expires within 90 days | CP-02, CF-06 | Riley Chen |

**Watch list:** 3 vendors need a certificate renewal; 1 questionnaire answer changed this week (CP-02).
**Next step:** request renewals before the next scan; expired certificates hold their items.

### Audit evidence readiness (`audit_evidence`)

**Audit Evidence Readiness: 2026-10-05**

| Project | Covered Lines | Evidence Complete | Open Items | Package |
|---|---|---|---|---|
| P-101 Riverside Main Replacement | 3 | 1 | GV-08 (non-compliant), RB-04 (evidence gap) | Not ready |
| P-102 Hillcrest Pump Station | 2 | 0 | GV-08 (non-compliant), CF-06 (conflict) | Not ready |
| P-103 Lakeview Service Lines | 2 | 0 | CP-02 (non-compliant), CF-06 (conflict) | Not ready |

**Package:** evidence is complete for 1 of 7 covered BOM lines (current certificate, attestation and data sheet). Every open item cites the record it depends on.
**Next step:** close the open items before the evidence package goes to the program reviewer.

### Approved next-step drafts (`action_drafts`)

**Approved Next Steps: Drafts Ready for Review - Not Sent**

| # | Draft | To | Content |
|---|---|---|---|
| 1 | Hold notice | Project buyers, P-101 and P-102 | Hold GV-08 8-inch resilient wedge gate valve (18 ea): vendor certificate expired. |
| 2 | Certificate renewal request | Jamie Ortiz, Fabrikam Castings | Please send a renewed compliance certificate; GV-08 is on hold until it arrives. |
| 3 | Substitution change request | Engineering of record, P-101 and P-102 | Replace GV-08 with GV-08B (Contoso Pipe & Valve), same spec GV-8-RW. |
| 4 | Attestation follow-up | Riley Chen, Litware Fittings | Your Oct 2 answer moves CP-02 final assembly; please confirm the plant and send an updated attestation, and correct the part revision on the CF-06 certificate letter. |
| 5 | Data sheet request | Casey Morgan, Adatum Steel | Please send the product data sheet for RB-04 No. 4 reinforcing bar. |

**Status:** 5 drafts prepared. Nothing was sent, no order was placed, and master data is unchanged; a person sends each draft and records the change.

### `compliant_alternates` with item = CP-02

**Compliant Alternates: CP-02 1-inch copper service tubing (spec CU-1-K)**

Current: Litware Fittings at $3.10/ft - Non-compliant: Vendor questionnaire answer: final assembly moved to a non-qualifying plant. On approved BOMs: P-103 (3,000).

| Alternate | Vendor | Spec | Unit Price | Certificate To | Lead Time | Cost Impact | Evidence |
|---|---|---|---|---|---|---|---|
| CP-02B | Contoso Pipe & Valve | CU-1-K | $3.40 | 2027-03-31 | 10 days | +$900 | Ready |

**Recommended:** CP-02B from Contoso Pipe & Valve: same spec, certificate current to 2027-03-31, cost impact +$900 across 3,000 ft.
**Next step:** approve the substitution so a change request draft can be prepared.

### `compliant_alternates` with item = DI-08

**Compliant Alternates: DI-08 8-inch ductile iron pipe**

Status: Compliant (Certificate, attestation and data sheet current). No alternate is needed or none is listed in the approved catalog for spec DIP-8-C52.

## Record resolution rules

- The snapshot is the week of 2026-10-05 compared with the scan of 2026-09-28; the vendor watch window runs to 2027-01-03.
- `compliant_alternates` takes an optional `item`: an item code (GV-08, CP-02, DI-08, CF-06, RB-04, MB-12) or part of the item name, default GV-08. A value that matches nothing returns "No synthetic item matches".
- Finding order per covered item: expired vendor certificate, then a questionnaire answer that no longer qualifies, then a certificate letter that conflicts with master data, then a missing data sheet; otherwise compliant.
- Cost impact = (alternate unit price - current unit price) x quantity on the approved BOMs.

## Locked-case evidence contract

Each locked case below routes to one skill; a correct answer always contains every listed evidence string.

| Case | Persona | Prompt | Skill | Must include |
|---|---|---|---|---|
| BM-01 | Procurement Compliance Lead | What changed on our approved bills of materials this week? | `weekly-changes` | `2 new lines and 2 quantity changes`; `Riverside Main Replacement`; `New this week` |
| BM-02 | Procurement Compliance Lead | Is anything newly out of compliance, and why? | `compliance-check` | `2 newly non-compliant`; `Vendor certificate expired 2026-09-30`; `final assembly moved to a non-qualifying plant` |
| BM-03 | Buyer | Find me a compliant replacement for the gate valve with the same spec. | `compliant-alternates` | `GV-08B`; `Contoso Pipe & Valve`; `certificate current to 2027-03-31` |
| BM-04 | Supplier Quality Manager | Which vendor certificates have lapsed or are about to? | `vendor-watch` | `3 vendors need a certificate renewal`; `Adatum Steel`; `Expired` |
| BM-05 | Program Compliance Reviewer | Are we ready if the program auditor asks for our evidence package? | `audit-evidence` | `evidence is complete for 1 of 7`; `Not ready`; `Hillcrest Pump Station` |
| BM-06 | Procurement Compliance Lead | I approve the hold, the GV-08B substitution and the vendor follow-ups. Prepare the drafts. | `action-drafts` | `5 drafts prepared`; `Nothing was sent`; `Substitution change request` |
