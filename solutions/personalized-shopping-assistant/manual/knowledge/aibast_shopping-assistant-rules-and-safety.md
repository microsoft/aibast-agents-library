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
| `PSA-01` | `product_recommendations` | Personal Shopper | `{"customer_id":"SHOP-001","occasion":"business dinner with clients"}` | `Prepared for:** Personal Shopper`; `Draft Product Recommendations`; `Wool crepe blazer` |
| `PSA-02` | `style_profile` | Clienteling Specialist | `{"customer_id":"SHOP-002"}` | `Prepared for:** Clienteling Specialist`; `Opt-In Style Profile`; `Synthetic Shopper B` |
| `PSA-03` | `inventory_check` | Retail Manager | `{"sku":"SKU-2003"}` | `Prepared for:** Retail Manager`; `Inventory Snapshot`; `inventory is not reserved` |
| `PSA-04` | `outfit_builder` | Personal Shopper | `{"customer_id":"SHOP-001"}` | `Draft Outfit Builder`; `Power Suiting`; `no return, refund, order, or purchase` |
| `PSA-05` | `pricing_offer` | Personal Shopper | `{"customer_id":"SHOP-001"}` | `$1,322`; `$273 (17%)`; `Bundle bonus` |
| `PSA-06` | `session_summary` | Clienteling Specialist | `{"customer_id":"SHOP-001"}` | `Business Dinner Look`; `Stuart Weitzman`; `not scheduled` |

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
- Prompt: As Personal Shopper, Jennifer needs an outfit for a business dinner with clients; suggest transparent options using only her stated preferences.
- Exact arguments: `{"customer_id":"SHOP-001","occasion":"business dinner with clients"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Personal Shopper
**Role focus:** occasion-ready options and transparent tradeoffs

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Draft Product Recommendations: Jennifer Hayes (Business dinner with clients)

**Occasion Analysis:**

| Requirement | Recommendation |
|---|---|
| Dress code | Business elegant |
| Impression | Polished, confident |
| Comfort level | Seated dining, standing cocktails |
| Her preference | Structured, not stuffy |

**Top Picks for Jennifer:**

| Item | Brand | Price | Match Score |
|---|---|---|---|
| Wool crepe blazer (SKU-2001) | Theory | $375 | 96% |
| Silk shell top (SKU-2002) | Vince | $195 | 94% |
| Tailored ankle pant (SKU-2003) | Equipment | $285 | 92% |
| Midi sheath dress (SKU-2004) | Theory | $345 | 91% |

**Why These Selections:**

- Blazer: Her favorite Theory brand, structured silhouette she loves
- Shell: Navy (her color), pairs with blazer
- Pants: High-rise she prefers, versatile neutral
- Dress option: One-piece alternative, midi length

**Not Recommended:**

- Prints (she avoids)
- Fitted dresses (prefers relaxed)
- Trendy pieces (wants investment value)

Source: [Recommendation Engine + Occasion Database] Agents: ProductRecommendationAgent, OccasionMatchingAgent

**Next step:** see complete outfit combinations?
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

**Customer Style Profile:**

| Attribute | Preference |
|---|---|
| Style archetype | Relaxed Minimal |
| Color palette | Black, white, camel |
| Fit preference | Easy, unstructured |
| Price range | $80-250 per piece |
| Preferred brands | Vince |

**Size Information:**

| Category | Size | Notes |
|---|---|---|
| Tops | 8 / Medium | Prefers easy fit |
| Bottoms | 29/8 | Mid-rise preferred |
| Dresses | 8 | Knee length |
| Shoes | 9 | Flats preferred |

**Recent Purchase Patterns:**

- Last purchase: 2 months ago (knit top)
- Avg items/visit: 1.6
- Return rate: 12%
- Total spend (YTD): $1,150

**Style Notes from Past Sessions:** "Prefers comfort and simple shapes"

These are stated, opt-in preferences; nothing else is inferred.

Source: [Purchase History + Style Profile + CRM Notes] Agents: StyleProfileAgent, OccasionMatchingAgent

**Next step:** what occasion is she shopping for?
```

### `PSA-03` — `inventory_check`

- Persona: **Retail Manager**
- Prompt: As Retail Manager, show the synthetic size-level availability and verification gate for SKU-2003.
- Exact arguments: `{"sku":"SKU-2003"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Retail Manager
**Role focus:** consistency, availability caveats, and service quality

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Inventory Snapshot: Equipment Tailored ankle pant (SKU-2003)

- **Price:** $285
- **Her size:** 28

| Location | Size | Stock | Status |
|---|---|---|---|
| Store | 27 | 2 | In stock |
| Store | 28 | 1 | Low stock (1 left) |
| Store | 29 | 2 | In stock |
| Warehouse | 28 | 0 | Out of stock here |
| Downtown | 28 | 0 | Out of stock here |
```

### `PSA-04` — `outfit_builder`

- Persona: **Personal Shopper**
- Prompt: As Personal Shopper, draft coordinated outfit options and transparent totals without ordering anything.
- Exact arguments: `{"customer_id":"SHOP-001"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Personal Shopper
**Role focus:** occasion-ready options and transparent tradeoffs

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Draft Outfit Builder: Jennifer Hayes (Business dinner with clients)

## Outfit 1: Power Suiting (recommended)

| Piece | Item | Price |
|---|---|---|
| Blazer | Theory Wool crepe blazer | $375 |
| Top | Vince Silk shell top | $195 |
| Pants | Equipment Tailored ankle pant | $285 |
| Shoes | Store label Classic leather pump | $295 |
| Bag | Store label Leather tote | $425 |
| **Total** | | **$1,575** |

## Outfit 2: Elegant Simplicity

| Piece | Item | Price |
|---|---|---|
| Dress | Theory Midi sheath dress | $345 |
| Blazer | Theory Wool crepe blazer | $375 |
| Shoes | Store label Pointed kitten heel | $265 |
| Jewelry | Store label Gold bar necklace | $125 |
| **Total** | | **$1,110** |

## Outfit 3: Modern Edge

| Piece | Item | Price |
|---|---|---|
| Jumpsuit | Vince Tailored jumpsuit | $395 |
| Belt | Store label Leather waist belt | $145 |
| Earrings | Store label Statement gold earrings | $85 |
| Clutch | Store label Evening leather clutch | $295 |
| **Total** | | **$920** |

**Stylist Recommendation:** Outfit 1 (Power Suiting) - most aligned with her established style.

Source: [Outfit Coordination Engine + Style Rules] Agents: OutfitCoordinationAgent, ProductRecommendationAgent

**Next step:** check availability for her sizes?
```

### `PSA-05` — `pricing_offer`

- Persona: **Personal Shopper**
- Prompt: As Personal Shopper, what is the best offer I can give Jennifer with her loyalty benefits?
- Exact arguments: `{"customer_id":"SHOP-001"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Personal Shopper
**Role focus:** occasion-ready options and transparent tradeoffs

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Loyalty Pricing: Outfit 1 Power Suiting for Jennifer Hayes

**Tier:** Platinum (10% member pricing)

| Item | Price | Her Price | Benefit |
|---|---|---|---|
| Theory wool crepe blazer | $375 | $337 | 10% Platinum |
| Vince silk shell top | $195 | $175 | 10% Platinum |
| Equipment tailored ankle pant | $285 | $256 | 10% Platinum |
| Stuart Weitzman block heel | $315 | $283 | 10% Platinum |
| Store label leather tote | $425 | $382 | 10% Platinum |

**Additional Offers:**

| Offer | Value | Conditions |
|---|---|---|
| Bundle bonus | Extra 5% | 3+ pieces |
| Points redemption | -$42 | Use balance |
| Free alterations | $35 value | Platinum perk |

**Best Deal Package:**

| | Amount |
|---|---|
| Original total | $1,595 |
| Platinum discount (10%) | -$159 |
| Bundle bonus (5%) | -$72 |
| Points applied | -$42 |
| **Final price** | **$1,322** |
| Total savings | $273 (17%) |

Calculated for the stylist to present; the member discount applies to the order total and the bundle bonus to the discounted total. Nothing is charged, and the benefits are applied only when you ring up the order.

Source: [Pricing Engine + Loyalty System + Promotions] Agents: PricingOptimizationAgent, InventoryAvailabilityAgent

**Next step:** generate the session summary?
```

### `PSA-06` — `session_summary`

- Persona: **Clienteling Specialist**
- Prompt: As Clienteling Specialist, wrap up Jennifer's styling session and prepare the updates for her profile.
- Exact arguments: `{"customer_id":"SHOP-001"}`

```markdown
[PersonalizedShoppingAssistantAgent] **Prepared for:** Clienteling Specialist
**Role focus:** opt-in preferences, continuity, and respectful follow-up drafts

> Synthetic opt-in preferences and inventory snapshots. Recommendations only; no sensitive traits are inferred, inventory is not reserved, benefits are not applied, and no return, refund, order, or purchase is completed.

# Session Summary: Jennifer Hayes (Business dinner with clients)

| Accomplishment | Result |
|---|---|
| Style profile applied | 5 preferences matched |
| Outfits created | 3 complete looks |
| Recommended outfit | Power Suiting (#1) |
| Availability confirmed | 4 of 5 in store |
| Savings delivered | $273 (17%) on $1,322 |

**Profile updates, ready for you to save:**

- Outfit 1: save as "Business Dinner Look"
- Outfits 2 & 3: add to wishlist
- Size preferences: confirmed accurate
- Brand note: Stuart Weitzman added

**Proposed follow-ups (not scheduled):**

| Trigger | Action | Timing |
|---|---|---|
| New Theory arrivals | Notification | Automatic |
| Pants low stock | Alert | If not purchased |
| Wishlist items on sale | Email | When discounted |

Nothing was written to her profile and no message was sent; confirm these updates in the clienteling system.
```
