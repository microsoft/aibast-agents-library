# Store Associate Copilot — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Store Associate | clear product facts and respectful customer-assistance drafts |
| Sales Manager | aggregate coaching signals and operational review |
| Floor Specialist | location, availability, and task-planning detail |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `SA-01` | `product_lookup` | Store Associate | `{"sku_id":"SKU-1005"}` | `Prepared for:** Store Associate`; `Product Lookup Snapshot`; `verify before advising` |
| `SA-02` | `customer_assist` | Store Associate | `{"scenario":"complaint_handling"}` | `Draft Customer Assistance Guide`; `Suggested Draft Language`; `authorized associate` |
| `SA-03` | `task_checklist` | Floor Specialist | `{"shift":"opening"}` | `Prepared for:** Floor Specialist`; `Daily Task Planning Checklist`; `Opening Shift` |
| `SA-04` | `performance_dashboard` | Sales Manager | `{}` | `Prepared for:** Sales Manager`; `Synthetic Role-Cohort Performance Dashboard`; `Aggregate Coaching Signals` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

Never promise or reserve inventory; apply a promotion or loyalty benefit; send a message; make an employment decision; process a return or refund; prepare a transaction; or complete a purchase.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `SA-01` — `product_lookup`

- Persona: **Store Associate**
- Prompt: As Store Associate, give me the product facts, floor location, optional complements, and availability caveat for SKU-1005.
- Exact arguments: `{"sku_id":"SKU-1005"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Store Associate
**Role focus:** clear product facts and respectful customer-assistance drafts

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

# Product Lookup Snapshot

## Premium Running Shoes (`SKU-1005`)

- **Brand:** StrideMax
- **Category:** Footwear
- **Price:** $149.99
- **Sizes:** 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 12, 13
- **Colors:** Cloud White/Grey, Black/Volt, Navy/Orange
- **Materials:** Engineered mesh upper, EVA foam midsole, rubber outsole
- **Care:** Spot clean with damp cloth. Air dry only.
- **Location:** Aisle F1, Wall display
- **Synthetic On-Hand Snapshot:** 38 units (verify before advising)
- **UPC:** 0-12345-67890-5

**Key Features:**
  - Responsive cushioning
  - Breathable knit upper
  - Reflective accents
  - Carbon fiber plate

**Optional Complementary Ideas:** Stainless Water Bottle, Performance Yoga Mat
```

### `SA-02` — `customer_assist`

- Persona: **Store Associate**
- Prompt: As Store Associate, draft respectful language for acknowledging a complaint while keeping the decision with an authorized reviewer.
- Exact arguments: `{"scenario":"complaint_handling"}`

```markdown
[store-associate-copilot-agent] Unknown scenario `customer complaint acknowledgment with escalation to authorized reviewer`. Valid: greeting, upsell, complaint_handling, size_help, return_at_counter
[store-associate-copilot-agent] **Prepared for:** Store Associate
**Role focus:** clear product facts and respectful customer-assistance drafts

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

# Draft Customer Assistance Guide

## Complaint Handling

**Scenario:** Customer has a complaint or issue

**Suggested Draft Language:**
> Draft: Acknowledge the concern, restate it, and explain that an authorized associate will review options.

**Follow-Up:** Listen fully, repeat back the issue, offer a concrete solution within your authority.

**Tips:**
- Never argue
- Acknowledge their frustration
- Offer alternatives if first solution is declined
```

### `SA-03` — `task_checklist`

- Persona: **Floor Specialist**
- Prompt: As Floor Specialist, turn the opening work into a prioritized planning checklist without claiming execution.
- Exact arguments: `{"shift":"opening"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Floor Specialist
**Role focus:** location, availability, and task-planning detail

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

# Daily Task Planning Checklist

## Opening Shift
**Estimated Time:** 57 min | **Completion:** 83.3%

| # | Task | Priority | Est. Time |
|---|------|----------|-----------|
| 1 | Unlock entrance doors and disable alarm | CRITICAL | 2 min |
| 2 | Power on POS terminals and verify connectivity | CRITICAL | 5 min |
| 3 | Walk floor to check overnight display condition | HIGH | 10 min |
| 4 | Restock fitting rooms with hangers | MEDIUM | 5 min |
| 5 | Review daily promotions and update signage | HIGH | 15 min |
| 6 | Check inventory alerts and pull items for floor replenishment | HIGH | 20 min |
```

### `SA-04` — `performance_dashboard`

- Persona: **Sales Manager**
- Prompt: As Sales Manager, summarize aggregate role-cohort coaching signals without ranking employees.
- Exact arguments: `{}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Sales Manager
**Role focus:** aggregate coaching signals and operational review

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

# Synthetic Role-Cohort Performance Dashboard

**Store Total Revenue Today:** $6,539.00
**Store Total Transactions:** 52
**Store Avg Basket:** $125.75

| Associate | Role | Shift | Revenue | Units | Txns | Basket | Upsell | CSAT | Tasks |
|-----------|------|-------|---------|-------|------|--------|--------|------|-------|
| Opening Senior Associate Cohort | Senior Associate | opening | $1,847.50 | 23 | 14 | $131.96 | 35% | 4.8/5.0 | 11/12 (92%) |
| Midday Associate Cohort | Associate | midday | $1,295.80 | 17 | 11 | $117.80 | 22% | 4.5/5.0 | 8/10 (80%) |
| Closing Associate Cohort | Associate | closing | $985.40 | 12 | 9 | $109.49 | 18% | 4.3/5.0 | 7/9 (78%) |
| Opening Lead Associate Cohort | Lead Associate | opening | $2,410.30 | 29 | 18 | $133.91 | 40% | 4.9/5.0 | 12/12 (100%) |

## Aggregate Coaching Signals

- **Revenue reference cohort:** Opening Lead Associate Cohort — use for workflow review, not personnel decisions
- **Service reference cohort:** Opening Lead Associate Cohort — inspect practices, not individuals
- **Attach-rate reference cohort:** Opening Lead Associate Cohort — avoid pressure-based selling
```
