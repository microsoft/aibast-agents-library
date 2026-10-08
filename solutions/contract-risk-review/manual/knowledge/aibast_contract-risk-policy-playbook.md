# Contract Risk Review — Complete Synthetic Policy and Negotiation Rules

> SYNTHETIC INTERNAL POLICY. This is not legal advice, an industry standard, or
> a compliance determination.

## Internal Policy Requirements

| Requirement key | Display name | Exact synthetic standard |
|---|---|---|
| liability_cap_minimum | Liability Cap Minimum | $8,300,000 (annual contract value) |
| payment_terms_max_days | Payment Terms Max Days | Net 30 (30 days) |
| ip_preexisting_protection | IP Preexisting Protection | Required |
| mutual_indemnification | Mutual Indemnification | Required |
| cure_period_days | Cure Period Days | 30 days |
| data_destruction_clause | Data Destruction Clause | Required with certification |
| change_order_written | Change Order Written | Required |
| sla_penalty_cap_pct | SLA Penalty Cap Pct | 10% of monthly fees |

## Deterministic policy-screen rules

1. For each documented HIGH or MEDIUM clause, report a gap with clause title,
   section, severity, and the exact recommended review position.
2. CTR-5001 must return `GAPS FOUND (10)`.
3. CTR-5003 must return `GAPS FOUND (3)`.
4. CTR-5002 and CTR-5004 have no clause evidence and must return
   `REVIEW REQUIRED` with: `No clause evidence is packaged for this contract;
   no compliance conclusion can be made.`
5. Never convert absent evidence into PASS.

## Deterministic negotiation rules

### CTR-5001 — NovaTech Systems

- Value: $25,000,000 over 36 months
- Risk score: 6.5/10
- Governing law: Delaware
- Renewal: 2028-06-30
- 14 critical amendments required before signing (see the 14-amendment table
  in the agreement records). Top 6 are non-negotiable: increase cap to $10M;
  add mutual indemnification; carve-outs (IP, data breach, gross negligence);
  protect pre-existing methodologies; license-back for client-specific work;
  restrict client resale rights.
- **Non-Negotiable Amendments (must resolve):** the six above.
- Fallback Position: minimum $8.3M liability (annual value) with mutual
  indemnification and critical carve-outs. Alternative: tiered caps by
  violation type.
- Escalation path: General Counsel review if there is an impasse on the
  liability cap.

### CTR-5003 — Atlas Financial Group

- Value: $12,000,000 over 24 months
- Risk score: 5.2/10
- Governing law: California
- Renewal: 2027-12-01
- **Non-Negotiable Amendments:** Indemnification.
- **Preferred Amendments:** Data Handling and Non-Compete.
- Fallback: accept the current value on MEDIUM items only if every HIGH item is
  resolved.
- Escalation path: General Counsel review if the non-negotiable position cannot
  be resolved.

Total contract value requiring renegotiation (both agreements, on request for the whole portfolio): $37,000,000. By default the brief covers the NovaTech MSA.

## Required response headings and decision boundaries

- `Contract Risk Scan`
- `Upcoming Renewals`
- `Clause-Level Risk Analysis`
- `Internal Policy Requirements`
- `Contract Compliance Status`
- `REVIEW REQUIRED`
- `Renegotiation Brief`
- `Non-Negotiable Amendments (must resolve)`
- `Preferred Amendments`
- `Negotiation strategy`

Always state `Review support only` for portfolio triage and `Draft positions
for authorized counsel review` for negotiation output. Never edit, approve,
sign, send, accept, renew, or transmit a contract.
