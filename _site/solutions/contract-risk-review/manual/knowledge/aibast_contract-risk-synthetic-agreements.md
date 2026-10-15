# Contract Risk Review — Complete Synthetic Agreement Records

> SYNTHETIC PILOT DATA. Every client, agreement, clause, date, value, score,
> status, and recommendation is fictional. Fixed snapshot date: 2026-03-17.
> Do not recalculate `Days Out` from the current date.

## Portfolio summary

- Active contracts in the packaged portfolio: 4
- Total contract value: $49,700,000
- Value at elevated risk, defined as risk score at least 5.0: $37,000,000

| Contract | Client | Type | Value | Term | Governing law | Renewal | Risk | Pages | Status | HIGH issues |
|---|---|---|---:|---:|---|---|---:|---:|---|---:|
| CTR-5001 | NovaTech Systems | Master Services Agreement | $25,000,000 | 36 months | Delaware | 2028-06-30 | 6.5/10 | 47 | under_review | 4 |
| CTR-5002 | Meridian Healthcare | Statement of Work | $4,200,000 | 18 months | New York | 2027-09-15 | 3.8/10 | 22 | active | 0 documented |
| CTR-5003 | Atlas Financial Group | Master Services Agreement | $12,000,000 | 24 months | California | 2027-12-01 | 5.2/10 | 38 | active | 1 |
| CTR-5004 | Orion Defense Systems | IDIQ Task Order | $8,500,000 | 60 months | Federal (FAR) | 2030-03-31 | 4.1/10 | 64 | active | 0 documented |

## Complete documented clause evidence

### CTR-5001 — NovaTech Systems

| Section | Clause | Risk | Exact issue | Exact recommended review position |
|---|---|---|---|---|
| 7.1 | Liability Cap | HIGH | Cap limited to fees paid in preceding 12 months ($2-8M range); no carve-outs for IP or data breach | Increase cap to $10M with carve-outs (IP indemnity, data breach, gross negligence); fallback minimum $8.3M (annual contract value) |
| 8.2 | IP Ownership | HIGH | All work product assigned to client including improvements and derivatives; no pre-existing IP protection | Carve out pre-existing IP; add license-back for client-specific derivatives |
| 9.4 | Payment Terms | MEDIUM | Net 60 days vs company standard Net 30; creates $1.4M cash-flow delay | Change to Net 30 payment terms |
| 12.1 | Termination | HIGH | Client may terminate immediately for any breach with no cure period | Add 30-day cure period for termination |
| 14.3 | SLA Penalties | MEDIUM | Penalties uncapped; could exceed monthly fees in extreme scenarios | Cap SLA penalties at 10% of monthly fees |
| 15.2 | Change Orders | MEDIUM | Verbal change approvals accepted; creates scope-creep exposure | Require written change orders signed by authorized representatives |
| 7.3 | Indemnification | HIGH | One-sided: we indemnify the client, the client does not indemnify us | Add mutual indemnification |
| 16.1 | Dispute Resolution | MEDIUM | Litigation-first with no executive escalation or mediation step; high legal costs | Add escalation before litigation |
| 3.2 | Auto-Renewal | MEDIUM | Auto-renews with an unfavorable rate lock preventing price adjustments | Remove auto-renewal |
| 5.4 | Resource Replacement | MEDIUM | Client has unilateral right to replace our team members | Limit resource replacement rights |

Critical issues shown in the contract overview (the first six clauses):

- Liability exposure: Cap limited to prior 12 months fees ($2-8M)
- IP ownership: ALL work product assigned to client
- Payment terms: Net 60 vs standard Net 30
- Termination: No cure period, immediate for any breach
- SLA penalties: Uncapped, could exceed monthly fees
- Change orders: Verbal approval accepted (risky)

Canonical summary: 4 HIGH and 6 MEDIUM risk clauses.

### CTR-5003 — Atlas Financial Group

| Section | Clause | Risk | Exact issue | Exact recommended review position |
|---|---|---|---|---|
| 5.1 | Indemnification | HIGH | One-sided indemnification; we indemnify client but no reciprocal obligation | Add mutual indemnification clause |
| 6.3 | Data Handling | MEDIUM | No data destruction timeline after engagement ends; liability lingers | Add 90-day data destruction clause with certification |
| 11.2 | Non-Compete | MEDIUM | 12-month non-compete for similar engagements in financial services sector | Narrow scope to specific sub-sector or reduce to 6 months |

Canonical summary: 1 HIGH and 2 MEDIUM risk clauses.

## Evidence availability

- CTR-5001 and CTR-5003 have the complete clause findings available to this
  synthetic pilot.
- CTR-5002 and CTR-5004 have no packaged clause evidence. Their correct status
  in an internal-policy screen is `REVIEW REQUIRED`, never PASS.

## Upcoming Renewals

| Contract | Client | Renewal Date | Days Out | Exact action |
|---|---|---|---:|---|
| CTR-5002 | Meridian Healthcare | 2027-09-15 | 547 | Begin renewal discussions Q1 2027 |
| CTR-5003 | Atlas Financial Group | 2027-12-01 | 624 | Address risk clauses before renewal |
| CTR-5001 | NovaTech Systems | 2028-06-30 | 835 | Renegotiate critical terms at Year-2 review |
| CTR-5004 | Orion Defense Systems | 2030-03-31 | 1474 | Option-year review in 2028 |

## NovaTech MSA guided review (CTR-5001, the default agreement)

The NovaTech Systems MSA is already on file; no upload is needed. The guided
review answers, in order: "Legal just sent over a master services agreement
from NovaTech Systems. $25M over 3 years ... can you review it before our
signing meeting tomorrow" (also asked as "Legal just sent over the NovaTech
Systems master services agreement. Can you review it before our signing
meeting tomorrow?"), "What specifically is wrong with the liability provisions
in the NovaTech agreement?", "Show me the IP ownership problems in the NovaTech
agreement.", "What other risk factors did you find beyond liability and IP?",
"Give me the full amendment list with priorities", and "Generate the redline
and an executive summary for our legal team."

### Contract Overview

| Element | Details |
|---|---|
| Agreement type | Master Services Agreement |
| Total value | $25M over 36 months (3 years) |
| Client | NovaTech Systems Inc |
| Governing law | Delaware |
| Pages analyzed | 47 |
| Risk score | 6.5/10 (Medium-High) |

The 47-page MSA requires 14 amendments before signing; 6 critical issues
(listed above).

### Liability Problems (Section 7.1)

- Current cap: "Fees paid in preceding 12 months"
- Minimum exposure: $2M (early project); maximum exposure: $8M (later stages)
- Potential damages $10-20M, so the gap to damages could be a $2-18M shortfall
  ($10M - $8M = $2M; $20M - $2M = $18M)
- Industry standards: minimum = annual contract value ($8.3M = $25M x 12 / 36);
  preferred = greater of annual value or $10M
- Our recommendation: $10M with carve-outs
- Missing protections: no carve-outs for IP indemnity, data breach or gross
  negligence; one-sided indemnification (Section 7.3: we indemnify them, they
  don't indemnify us)
- Insurance Gap: Current E&O coverage insufficient for $10M+ exposure

### IP Ownership Issues (Section 8.2)

- Current language: ALL work product assigned to client; includes improvements
  and derivatives; no distinction for pre-existing IP; no license-back
  provision; no restrictions on client use
- Risk Scenario: we develop valuable accelerator during engagement; client owns
  it completely; client can use it with our competitors; client can sell it in
  the market; we can't reuse our own innovation
- Required protections: carve-out for pre-existing methodologies; License-back
  for client-specific work; restriction: client use only, no resale; define
  "work product" narrowly

### Additional Risks

| Risk | Current Terms | Impact |
|---|---|---|
| Payment | Net 60 days | $1.4M delayed cash flow |
| Termination | Immediate, no cure | Loss of $25M revenue |
| SLA penalties | Uncapped | Could exceed monthly fees |
| Change orders | Verbal OK | Scope creep exposure |
| Disputes | Litigation-first | High legal costs |

- Cash flow: monthly fees $694,444 ($25M / 36); Net 60 keeps two months of
  fees outstanding = $1.4M on average vs Net 30 standard
- Termination risk: no 30-day cure period means instant contract loss for a
  minor breach
- Auto-Renewal: yes, with an unfavorable rate lock preventing price adjustments
- Resource control: client has unilateral right to replace our team members

### 14 amendments (top 6 non-negotiable)

| # | Group | Amendment | Original | Proposed | Non-negotiable |
|---|---|---|---|---|---|
| 1 | Liability Protection | Increase cap to $10M | Cap = fees paid in preceding 12 months | Cap = $10,000,000 per claim | Yes |
| 2 | Liability Protection | Add mutual indemnification | Provider indemnifies client only | Each party indemnifies the other | Yes |
| 3 | Liability Protection | Carve-outs: IP, data breach, gross negligence | No carve-outs | IP indemnity, data breach and gross negligence sit outside the cap | Yes |
| 4 | IP Protection | Protect pre-existing methodologies | ALL work product assigned to client | Pre-existing IP and methodologies remain with provider | Yes |
| 5 | IP Protection | License-back for client-specific work | No license-back | Provider receives a license-back to client-specific derivatives | Yes |
| 6 | IP Protection | Restrict client resale rights | No restrictions on client use | Client use only; no resale or transfer to third parties | Yes |
| 7 | IP Protection | Define "work product" narrowly | Work product includes improvements and derivatives | Work product = deliverables named in each SOW | No |
| 8 | Payment & Termination | Change to Net 30 payment terms | Net 60 | Net 30 | No |
| 9 | Payment & Termination | Add 30-day cure period for termination | Immediate termination for any breach | 30-day written cure period before termination | No |
| 10 | Payment & Termination | Cap SLA penalties at 10% of monthly fees | Uncapped SLA penalties | SLA penalties capped at 10% of monthly fees | No |
| 11 | Additional Amendments | Require written change orders | Verbal approval accepted | Signed written change orders only | No |
| 12 | Additional Amendments | Escalation before litigation | Litigation-first | Executive escalation, then mediation, before litigation | No |
| 13 | Additional Amendments | Remove auto-renewal | Auto-renewal with rate lock | Renewal by mutual written agreement with rate review | No |
| 14 | Additional Amendments | Limit resource replacement rights | Client may replace team members unilaterally | Replacement for documented cause with 15 days notice | No |

- Fallback Position: minimum $8.3M liability (annual value) with mutual
  indemnification and critical carve-outs
- Alternative: Tiered caps by violation type

### Redline and executive summary (drafts only)

- Deliverables (drafts): Redlined MSA with 14 tracked changes (the table
  above, ready for Word); executive memo, 3-page risk summary with rationale;
  fallback positions (tiered negotiation strategy); comparable terms (industry
  contract references); insurance review ($10M E&O coverage to raise with your
  broker).
- Key talking points: risk score 6.5/10 requires amendments; liability
  exposure $2-18M gap; IP risk: complete ownership transfer; cash flow impact
  $1.4M delayed; termination: no cure period.
- Negotiation strategy: target $10M liability cap with carve-outs; minimum
  $8.3M with mutual indemnification; alternative: Tiered caps by violation
  type.
- Nothing has been uploaded, sent or flagged: the user uploads the drafts to
  the contract workspace and contacts the broker.
