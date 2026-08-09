# Cart Abandonment Recovery — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Marketing Manager | margin-aware recovery planning and approval gates |
| Digital Marketing Lead | channel sequencing, consent, and draft content |
| Growth Manager | aggregate conversion scenarios and experiment design |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `CAR-01` | `abandonment_analysis` | Marketing Manager | `{}` | `Prepared for:** Marketing Manager`; `Synthetic Cart Abandonment Analysis`; `no shopper is contacted` |
| `CAR-02` | `recovery_campaign` | Digital Marketing Lead | `{}` | `Prepared for:** Digital Marketing Lead`; `Draft Recovery Campaign Dashboard`; `not deployed` |
| `CAR-03` | `incentive_optimization` | Growth Manager | `{}` | `Prepared for:** Growth Manager`; `Draft Incentive Scenario Comparison`; `Scenario for approval` |
| `CAR-04` | `conversion_tracking` | Growth Manager | `{}` | `Synthetic Conversion Tracking`; `Recovery Rate`; `no cart or purchase is changed` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

Never identify or contact a shopper; send or schedule a message; create, issue, or apply an offer; change a cart; reserve an item; or complete a purchase.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `CAR-01` — `abandonment_analysis`

- Persona: **Marketing Manager**
- Prompt: As Marketing Manager, show where the anonymous synthetic cart journey is breaking down and what needs review.
- Exact arguments: `{}`

```markdown
[CartAbandonmentRecoveryAgent] **Prepared for:** Marketing Manager
**Role focus:** margin-aware recovery planning and approval gates

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

# Synthetic Cart Abandonment Analysis

**Abandoned Carts:** 4
**Total Abandoned Value:** $2,494.90
**Abandonment Rate:** 71.4%

## Abandoned Carts Detail

| Cart ID | Customer | Segment | Value | Exit Page | Device | Status |
|---|---|---|---|---|---|---|
| CART-20001 | Synthetic returning-shopper cart | Returning Shopper | $284.98 | Shipping Options | Mobile | Draft Stage 1 Ready |
| CART-20002 | Synthetic first-session cart | New Visitor | $299.97 | Account Creation | Desktop | Not Contacted |
| CART-20003 | Synthetic established-shopper cart | Established Shopper | $1,779.96 | Payment | Desktop | Not Contacted |
| CART-20004 | Synthetic guest cart | Guest | $129.99 | Cart Page | Mobile | Unrecoverable |

## Exit Page Breakdown

- Shipping Options: 1
- Account Creation: 1
- Payment: 1
- Cart Page: 1
```

### `CAR-02` — `recovery_campaign`

- Persona: **Digital Marketing Lead**
- Prompt: As Digital Marketing Lead, outline a consent-aware draft sequence without sending or scheduling anything.
- Exact arguments: `{}`

```markdown
[CartAbandonmentRecoveryAgent] **Prepared for:** Digital Marketing Lead
**Role focus:** channel sequencing, consent, and draft content

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

# Draft Recovery Campaign Dashboard

## Proposed Sequence (not deployed)

| Campaign | Delay | Subject | Incentive | Open Rate | Conversion |
|---|---|---|---|---|---|
| Draft Email Reminder | 1h | Draft: neutral cart reminder | None | 45.2% | 8.5% |
| Draft Follow-Up | 24h | Draft: availability-neutral follow-up | None | 38.1% | 5.2% |
| Draft Value Option | 72h | Draft: approved value option, if eligible | Optional incentive concept | 42.8% | 12.1% |
| Draft SMS Reminder | 2h | Draft: concise cart reminder | None | 98.0% | 4.8% |
| Draft Retargeting Concept | 6h | Draft: consented product reminder concept | None | 0% | 2.1% |

## Carts Pending Recovery

- **CART-20001** (Synthetic returning-shopper cart): $284.98 — Draft status: Draft Stage 1 Ready
- **CART-20002** (Synthetic first-session cart): $299.97 — Draft status: Not Contacted
- **CART-20003** (Synthetic established-shopper cart): $1,779.96 — Draft status: Not Contacted

**No consented contact path in synthetic record:** 1
```

### `CAR-03` — `incentive_optimization`

- Persona: **Growth Manager**
- Prompt: As Growth Manager, compare margin-aware value scenarios and keep every concept behind approval.
- Exact arguments: `{}`

```markdown
[CartAbandonmentRecoveryAgent] **Prepared for:** Growth Manager
**Role focus:** aggregate conversion scenarios and experiment design

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

# Draft Incentive Scenario Comparison

## Available Incentives

| Incentive | Description | Margin Impact | Conversion Lift |
|---|---|---|---|
| Percent Off 10 | 10% off cart total | 10.0% | +35.0% |
| Percent Off 15 | 15% off cart total | 15.0% | +48.0% |
| Free Shipping | Free standard shipping | 5.5% | +28.0% |
| Dollar Off 20 | $20 off orders over $150 | 8.0% | +22.0% |
| Gift With Purchase | Free accessory with order | 6.0% | +18.0% |

## Recommended Incentives by Cart

### CART-20001: Synthetic returning-shopper cart ($284.98)

- **Segment:** Returning Shopper
- **Scenario for approval:** Free standard shipping
- **Expected Lift:** +28.0%
- **Net Recovery Value:** $269.31

### CART-20002: Synthetic first-session cart ($299.97)

- **Segment:** New Visitor
- **Scenario for approval:** 15% off cart total
- **Expected Lift:** +48.0%
- **Net Recovery Value:** $254.97

### CART-20003: Synthetic established-shopper cart ($1,779.96)

- **Segment:** Established Shopper
- **Scenario for approval:** 10% off cart total
- **Expected Lift:** +35.0%
- **Net Recovery Value:** $1,601.96
```

### `CAR-04` — `conversion_tracking`

- Persona: **Growth Manager**
- Prompt: As Growth Manager, summarize the fixed recovery metrics and separate benchmarks from planning estimates.
- Exact arguments: `{}`

```markdown
[CartAbandonmentRecoveryAgent] **Prepared for:** Growth Manager
**Role focus:** aggregate conversion scenarios and experiment design

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

# Synthetic Cart Abandonment Analysis

**Abandoned Carts:** 4
**Total Abandoned Value:** $2,494.90
**Abandonment Rate:** 71.4%

## Abandoned Carts Detail

| Cart ID | Customer | Segment | Value | Exit Page | Device | Status |
|---|---|---|---|---|---|---|
| CART-20001 | Synthetic returning-shopper cart | Returning Shopper | $284.98 | Shipping Options | Mobile | Draft Stage 1 Ready |
| CART-20002 | Synthetic first-session cart | New Visitor | $299.97 | Account Creation | Desktop | Not Contacted |
| CART-20003 | Synthetic established-shopper cart | Established Shopper | $1,779.96 | Payment | Desktop | Not Contacted |
| CART-20004 | Synthetic guest cart | Guest | $129.99 | Cart Page | Mobile | Unrecoverable |

## Exit Page Breakdown

- Shipping Options: 1
- Account Creation: 1
- Payment: 1
- Cart Page: 1
[CartAbandonmentRecoveryAgent] **Prepared for:** Growth Manager
**Role focus:** aggregate conversion scenarios and experiment design

> Synthetic aggregate planning data. Drafts and scenarios only; no shopper is contacted, no message or offer is sent, and no cart or purchase is changed.

# Synthetic Conversion Tracking (30-Day)

- **Abandonment Rate:** 71.4%
- **Recovery Rate:** 12.8%
- **Avg Recovered Order Value:** $187.50
- **Total Abandoned Carts:** 4,250
- **Total Recovered:** 544
- **Recovered Revenue:** $102,000

## Campaign Performance

| Campaign | Open Rate | Conversion | Est. Recovered |
|---|---|---|---|
| Draft Email Reminder | 45.2% | 8.5% | $67,734 |
| Draft Follow-Up | 38.1% | 5.2% | $41,438 |
| Draft Value Option | 42.8% | 12.1% | $96,422 |
| Draft SMS Reminder | 98.0% | 4.8% | $38,250 |
| Draft Retargeting Concept | 0% | 2.1% | $16,734 |

**Current Active Cart Value at Risk:** $2,494.90
```
