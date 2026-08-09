# Personalized Shopping Assistant — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Personal Shopper | occasion-ready options and transparent tradeoffs |
| Clienteling Specialist | opt-in preferences, continuity, and respectful follow-up drafts |
| Retail Manager | consistency, availability caveats, and service quality |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `PSA-01` | `product_recommendations` | Personal Shopper | `{"customer_id":"SHOP-001"}` | `Prepared for:** Personal Shopper`; `Draft Product Recommendations`; `no sensitive traits are inferred` |
| `PSA-02` | `style_profile` | Clienteling Specialist | `{"customer_id":"SHOP-002"}` | `Prepared for:** Clienteling Specialist`; `Opt-In Style Profile`; `Synthetic Shopper B` |
| `PSA-03` | `inventory_check` | Retail Manager | `{"sku":"SKU-1003"}` | `Prepared for:** Retail Manager`; `Inventory Snapshot`; `inventory is not reserved` |
| `PSA-04` | `outfit_builder` | Personal Shopper | `{"customer_id":"SHOP-001"}` | `Draft Outfit Builder`; `Business Casual`; `no return, refund, order, or purchase` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

Never infer body, health, identity, wealth, or another sensitive trait; reserve stock; apply a loyalty benefit or offer; process a return or refund; create an order; or complete a purchase.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `PSA-01` — `product_recommendations`

- Persona: **Personal Shopper**
- Prompt: As Personal Shopper, suggest transparent options for Synthetic Shopper A using only stated preferences.
- Exact arguments: `{"customer_id":"SHOP-001"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Personal Shopper
**Role focus:** occasion-ready options and transparent tradeoffs

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Draft Product Recommendations: Synthetic Shopper A

**Style:** classic, smart_casual
**Budget:** $50 - $250

| Rank | Product | Brand | Price | Match Score | Rating |
|---|---|---|---|---|---|
| 1 | Merino Wool Crew Sweater (SKU-1003) | Alpine Knits | $125.00 | 90% | 4.8 |
| 2 | Leather Chelsea Boots (SKU-1004) | Cobblestone | $195.00 | 55% | 4.6 |
| 3 | Linen Blazer — Unstructured (SKU-1008) | Riviera Style | $225.00 | 35% | 4.3 |
| 4 | Quilted Vest (SKU-1005) | Northfield | $110.00 | 25% | 4.4 |
| 5 | Performance Running Shoe (SKU-1007) | Stride Labs | $145.00 | 15% | 4.7 |
```

### `PSA-02` — `style_profile`

- Persona: **Clienteling Specialist**
- Prompt: As Clienteling Specialist, summarize Synthetic Shopper B's opt-in preferences without inferring anything else.
- Exact arguments: `{"customer_id":"SHOP-002"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Clienteling Specialist
**Role focus:** opt-in preferences, continuity, and respectful follow-up drafts

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Opt-In Style Profile: Synthetic Shopper B

## Sizing

- Top: S
- Bottom: 30
- Shoe: 8

## Style Preferences

- Casual
- Outdoor
- Athletic

## Brand Affinity

- Northfield
- Stride Labs

## Color Preference

- Olive
- Black
- White Grey

## Budget Range

$30 - $175

## Purchase History

- Quilted Vest — $110.00
- Performance Running Shoe — $145.00
```

### `PSA-03` — `inventory_check`

- Persona: **Retail Manager**
- Prompt: As Retail Manager, show the synthetic size-level availability and verification gate for SKU-1003.
- Exact arguments: `{"sku":"SKU-1003"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Retail Manager
**Role focus:** consistency, availability caveats, and service quality

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Inventory Snapshot: Merino Wool Crew Sweater (SKU-1003)

- **Price:** $125.00
- **Brand:** Alpine Knits
- **Rating:** 4.8

## Stock by Size

| Size | Stock | Status |
|---|---|---|
| S | 4 | Low Stock |
| M | 10 | In Stock |
| L | 8 | In Stock |
| XL | 3 | Low Stock |

**Total Units:** 25
```

### `PSA-04` — `outfit_builder`

- Persona: **Personal Shopper**
- Prompt: As Personal Shopper, draft coordinated outfit options and transparent totals without ordering anything.
- Exact arguments: `{"customer_id":"SHOP-001"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Personal Shopper
**Role focus:** occasion-ready options and transparent tradeoffs

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Draft Outfit Builder: Synthetic Shopper A

## Business Casual

- **Tops:** Classic Oxford Shirt — White — $68.00
- **Bottoms:** Slim Fit Chinos — Navy — $79.00
- **Footwear:** Leather Chelsea Boots — $195.00
- **Accessories:** Silk Pocket Square — $35.00

**Outfit Total:** $377.00

## Weekend Smart

- **Tops:** Merino Wool Crew Sweater — $125.00
- **Bottoms:** Slim Fit Chinos — Navy — $79.00
- **Footwear:** Leather Chelsea Boots — $195.00

**Outfit Total:** $399.00

## Active Weekend

- **Outerwear:** Quilted Vest — $110.00
- **Footwear:** Performance Running Shoe — $145.00

**Outfit Total:** $255.00

## Evening Out

- **Outerwear:** Linen Blazer — Unstructured — $225.00
- **Tops:** Classic Oxford Shirt — White — $68.00
- **Bottoms:** Slim Fit Chinos — Navy — $79.00
- **Footwear:** Leather Chelsea Boots — $195.00

**Outfit Total:** $567.00
```
