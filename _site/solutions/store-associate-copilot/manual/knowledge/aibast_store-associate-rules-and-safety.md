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
| `SA-05` | `accessory_recommendations` | Store Associate | `{"sku_id":"SKU-1005"}` | `Recommended Add-Ons`; `Commission Calculator`; `$32.80` |
| `SA-06` | `product_compare` | Store Associate | `{"compare_with":"SoundMax Pro","sku_id":"SKU-1005"}` | `Head-to-Head Comparison`; `Best For`; `Your Recommendation` |
| `SA-07` | `prepare_transaction` | Store Associate | `{"addons":"warranty and cleaning kit","loyalty_tier":"Gold"}` | `Transaction Prepared (Not Rung Up)`; `$273.12`; `Payment Options Available` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.

Never promise or reserve inventory; apply a promotion or loyalty benefit; send a message; make an employment decision; process a return or refund; ring up a transaction (a prepared cart is a draft the associate rings up at the register); or complete a purchase.

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
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

# Product Lookup Snapshot

TechPro X-Series Wireless Headphones (`SKU-1005`) are in stock with 14 units available in your Bellevue store (synthetic on-hand snapshot; verify before advising).

**Product Details:**

| Feature | Specification |
|---|---|
| Battery life | 38 hours continuous |
| Noise cancellation | Active ANC, -42dB |
| Price | $199.99 (on sale) |
| Warranty | 2 years standard |
| Location | Aisle E1, Headphone wall |

**Key Selling Points:**
- Industry-leading 38hr battery (vs competitors 24-30hr)
- Multi-device pairing (3 devices simultaneously)
- Foldable design with premium case included

**Current Promotion:** Save $50 (regular $249.99), ends Sunday
**Customer Reviews:** 4.7/5.0 stars (847 reviews) - Praised for comfort and battery life
**Optional Complementary Ideas:** Extended Warranty, Premium Cleaning Kit, Travel Adapter, Replacement Cushions

Source: [Store POS + Product Database] (synthetic)

Want to see compatible accessories or alternative options?

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

# Accessory and Commission Snapshot

Compatible accessories for the TechPro X-Series and your commission breakdown for the full package.

**Recommended Add-Ons:**
- Extended Warranty ($39.99) - 3-year coverage, 87% attach rate
- Premium Cleaning Kit ($24.99) - Branded TechPro, high margin
- Travel Adapter ($19.99) - USB-C fast charging
- Replacement Cushions ($34.99) - Memory foam upgrade

**Commission Calculator (synthetic plan rates):**
- Product: $199.99 x 8% = $16.00
- Warranty: $39.99 x 18% = $7.20
- Accessories: $79.97 x 12% = $9.60
- **Bundle Total:** $319.95 | **Your Commission:** $32.80

**Tip:** Mention the cleaning kit extends cushion life - drives 65% conversion

Source: [Commission System + Sales Analytics] (synthetic)

Need help with a product comparison?

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-02` — `customer_assist`

- Persona: **Store Associate**
- Prompt: As Store Associate, draft respectful language for acknowledging a complaint while keeping the decision with an authorized reviewer.
- Exact arguments: `{"scenario":"complaint_handling"}`

```markdown
[store-associate-copilot-agent] Unknown scenario `Acknowledging a customer complaint respectfully while escalating the final decision to an authorized reviewer/manager, without promising a specific resolution`. Valid: greeting, upsell, complaint_handling, size_help, return_at_counter
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

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


> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-03` — `task_checklist`

- Persona: **Floor Specialist**
- Prompt: As Floor Specialist, turn the opening work into a prioritized planning checklist without claiming execution.
- Exact arguments: `{"shift":"opening"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Floor Specialist (location, availability, and task-planning detail)

# Daily Task Planning Checklist

## Opening Shift
**Estimated Time:** 57 min | **Status:** planned (0 of 6 tasks done)

| # | Task | Priority | Est. Time |
|---|------|----------|-----------|
| 1 | Unlock entrance doors and disable alarm | CRITICAL | 2 min |
| 2 | Power on POS terminals and verify connectivity | CRITICAL | 5 min |
| 3 | Walk floor to check overnight display condition | HIGH | 10 min |
| 4 | Restock fitting rooms with hangers | MEDIUM | 5 min |
| 5 | Review daily promotions and update signage | HIGH | 15 min |
| 6 | Check inventory alerts and pull items for floor replenishment | HIGH | 20 min |


> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-04` — `performance_dashboard`

- Persona: **Sales Manager**
- Prompt: As Sales Manager, summarize aggregate role-cohort coaching signals without ranking employees.
- Exact arguments: `{}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Sales Manager (aggregate coaching signals and operational review)

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

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-05` — `accessory_recommendations`

- Persona: **Store Associate**
- Prompt: What accessories go with the TechPro headphones, and what would I earn on the whole package?
- Exact arguments: `{"sku_id":"SKU-1005"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

# Accessory and Commission Snapshot

Compatible accessories for the TechPro X-Series and your commission breakdown for the full package.

**Recommended Add-Ons:**
- Extended Warranty ($39.99) - 3-year coverage, 87% attach rate
- Premium Cleaning Kit ($24.99) - Branded TechPro, high margin
- Travel Adapter ($19.99) - USB-C fast charging
- Replacement Cushions ($34.99) - Memory foam upgrade

**Commission Calculator (synthetic plan rates):**
- Product: $199.99 x 8% = $16.00
- Warranty: $39.99 x 18% = $7.20
- Accessories: $79.97 x 12% = $9.60
- **Bundle Total:** $319.95 | **Your Commission:** $32.80

**Tip:** Mention the cleaning kit extends cushion life - drives 65% conversion

Source: [Commission System + Sales Analytics] (synthetic)

Need help with a product comparison?

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-06` — `product_compare`

- Persona: **Store Associate**
- Prompt: The shopper is torn between the TechPro and the SoundMax Pro. How do they stack up?
- Exact arguments: `{"compare_with":"SoundMax Pro","sku_id":"SKU-1005"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

# Head-to-Head Comparison

Side-by-side comparison: TechPro has better battery, SoundMax has superior sound quality.

| Feature | TechPro X-Series | SoundMax Pro |
|---|---|---|
| Price | $199.99 (sale) | $229.99 |
| Battery | 38 hours | 30 hours |
| Sound quality | Premium | Audiophile |
| Noise cancel | -42dB | -48dB |
| Stock | 14 units | 3 units |

**Best For:**
- TechPro: Long flights, all-day use, budget-conscious
- SoundMax: Music enthusiasts, home listening, best audio

**Customer Reviews:**
- TechPro: 4.7/5 (847 reviews) - "Amazing battery"
- SoundMax: 4.8/5 (623 reviews) - "Best sound ever"

**Your Recommendation:** TechPro if travel/commute is priority, SoundMax if pure audio quality matters most

Source: [Product Specs + Reviews Database] (synthetic)

Ready to build the customer's cart?

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```

### `SA-07` — `prepare_transaction`

- Persona: **Store Associate**
- Prompt: My Gold member customer is taking the TechPro with the warranty and cleaning kit. Get the sale ready.
- Exact arguments: `{"addons":"warranty and cleaning kit","loyalty_tier":"Gold"}`

```markdown
[store-associate-copilot-agent] **Prepared for:** Store Associate (clear product facts and respectful customer-assistance drafts)

# Transaction Prepared (Not Rung Up)

Transaction prepared and additional savings found for your customer, ready for you to ring up at the register.

**Transaction Ready:**
- TechPro X-Series Headphones: $199.99
- Extended Warranty (3-year): $39.99
- Premium Cleaning Kit: $24.99

| Line | Amount |
|---|---|
| Subtotal | $264.97 |
| Loyalty Discount (Gold Member) | -$13.25 (5% off) |
| Sales Tax (8.5%) | $21.40 |
| **Total** | **$273.12** |

**Payment Options Available:**
- 0% APR financing (6 months, $45.52/month)
- Store credit card (earn 500 bonus points)
- Standard payment methods

**Your Commission:** $26.20 on this sale
**Customer Savings:** They saved $63.25 (sale + loyalty discount)

Source: [POS System + Loyalty Program] (synthetic)

Apply the loyalty discount and proceed to checkout? The sale, discount and payment are completed by you at the register.

> Synthetic planning snapshot. Recommendations and scripts are drafts only; availability is not guaranteed, inventory is not reserved, and no message, offer, return, refund, transaction, or purchase is completed.
```
