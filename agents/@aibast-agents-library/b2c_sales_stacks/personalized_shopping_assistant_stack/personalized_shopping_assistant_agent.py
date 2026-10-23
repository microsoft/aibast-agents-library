"""
Personalized Shopping Assistant Agent — B2C Sales Stack

Builds a client style profile, occasion-matched picks, complete outfits,
size-level availability with alternatives, a loyalty-priced offer and a session
summary for a personal-styling session. The default client is the synthetic
Jennifer Hayes profile shopping for a business dinner (the demo session).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/personalized-shopping-assistant",
    "version": "1.1.0",
    "display_name": "Personalized Shopping Agent",
    "description": "Draft opt-in product, style, availability, and outfit recommendations using synthetic non-sensitive preferences for human review.",
    "author": "AIBAST",
    "tags": ["shopping", "personalization", "recommendations", "style", "inventory", "b2c"],
    "category": "b2c_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PRODUCT_CATALOG = {
    "SKU-2001": {"name": "Wool crepe blazer", "brand": "Theory", "piece": "Blazer", "price": 375, "size_type": "numeric", "color": "navy", "stock": {"store": {"4": 2, "6": 3, "8": 2}, "warehouse": {"6": 5}, "downtown": {"6": 1}}},
    "SKU-2002": {"name": "Silk shell top", "brand": "Vince", "piece": "Top", "price": 195, "size_type": "top", "color": "navy", "stock": {"store": {"XS": 1, "S": 4, "M": 3}, "warehouse": {"S": 6}, "downtown": {"S": 2}}},
    "SKU-2003": {"name": "Tailored ankle pant", "brand": "Equipment", "piece": "Pants", "price": 285, "size_type": "bottom", "color": "black", "stock": {"store": {"27": 2, "28": 1, "29": 2}, "warehouse": {"28": 0}, "downtown": {"28": 0}}},
    "SKU-2004": {"name": "Midi sheath dress", "brand": "Theory", "piece": "Dress", "price": 345, "size_type": "numeric", "color": "burgundy", "stock": {"store": {"4": 1, "6": 2, "8": 1}, "warehouse": {"6": 3}, "downtown": {"6": 1}}},
    "SKU-2005": {"name": "Classic leather pump", "brand": "Store label", "piece": "Shoes", "price": 295, "size_type": "shoe", "color": "black", "stock": {"store": {"7": 2, "8": 0, "9": 1}, "warehouse": {"8": 0}, "downtown": {"8": 0}}, "alternative": "SKU-2006"},
    "SKU-2006": {"name": "Block heel", "brand": "Stuart Weitzman", "piece": "Shoes", "price": 315, "size_type": "shoe", "color": "black", "stock": {"store": {"8": 2}, "warehouse": {"8": 4}, "downtown": {"8": 1}}, "note": "Same height, similar style"},
    "SKU-2007": {"name": "Leather tote", "brand": "Store label", "piece": "Bag", "price": 425, "size_type": "one_size", "color": "cognac", "stock": {"store": {"One size": 3}, "warehouse": {"One size": 4}, "downtown": {"One size": 1}}},
    "SKU-2008": {"name": "Pointed kitten heel", "brand": "Store label", "piece": "Shoes", "price": 265, "size_type": "shoe", "color": "nude", "stock": {"store": {"8": 3}, "warehouse": {"8": 2}, "downtown": {"8": 1}}},
    "SKU-2009": {"name": "Gold bar necklace", "brand": "Store label", "piece": "Jewelry", "price": 125, "size_type": "one_size", "color": "gold", "stock": {"store": {"One size": 5}, "warehouse": {"One size": 6}, "downtown": {"One size": 2}}},
    "SKU-2010": {"name": "Tailored jumpsuit", "brand": "Vince", "piece": "Jumpsuit", "price": 395, "size_type": "numeric", "color": "black", "stock": {"store": {"4": 1, "6": 0}, "warehouse": {"6": 3}, "downtown": {"6": 1}}},
    "SKU-2011": {"name": "Leather waist belt", "brand": "Store label", "piece": "Belt", "price": 145, "size_type": "one_size", "color": "black", "stock": {"store": {"One size": 4}, "warehouse": {"One size": 3}, "downtown": {"One size": 1}}},
    "SKU-2012": {"name": "Statement gold earrings", "brand": "Store label", "piece": "Earrings", "price": 85, "size_type": "one_size", "color": "gold", "stock": {"store": {"One size": 6}, "warehouse": {"One size": 4}, "downtown": {"One size": 2}}},
    "SKU-2013": {"name": "Evening leather clutch", "brand": "Store label", "piece": "Clutch", "price": 295, "size_type": "one_size", "color": "black", "stock": {"store": {"One size": 2}, "warehouse": {"One size": 2}, "downtown": {"One size": 1}}},
}

CUSTOMER_PREFERENCES = {
    "SHOP-001": {
        "name": "Jennifer Hayes",
        "alias": "jennifer",
        "profile": [
            ["Style archetype", "Modern Classic"],
            ["Color palette", "Neutrals, navy, burgundy"],
            ["Fit preference", "Tailored, not tight"],
            ["Price range", "$150-400 per piece"],
            ["Preferred brands", "Theory, Vince, Equipment"],
        ],
        "sizes": {"top": "S", "numeric": "6", "bottom": "28", "shoe": "8"},
        "size_rows": [
            ["Tops", "6 / Small", "Prefers relaxed fit"],
            ["Bottoms", "28/6", "High-rise preferred"],
            ["Dresses", "6", "Midi length"],
            ["Shoes", "8", "Comfortable heels only"],
        ],
        "purchase_patterns": [
            ["Last purchase", "3 weeks ago (silk blouse)"],
            ["Avg items/visit", "2.4"],
            ["Return rate", "8% (well below average)"],
            ["Total spend (YTD)", "$4,200"],
        ],
        "purchase_brands": ["Vince", "Theory", "Stuart Weitzman"],
        "style_notes": "Loves structured pieces, avoids prints, prefers investment pieces over trends",
        "loyalty_tier": "Platinum",
        "points_balance_value": 42,
    },
    "SHOP-002": {
        "name": "Synthetic Shopper B",
        "alias": "shopper b",
        "profile": [
            ["Style archetype", "Relaxed Minimal"],
            ["Color palette", "Black, white, camel"],
            ["Fit preference", "Easy, unstructured"],
            ["Price range", "$80-250 per piece"],
            ["Preferred brands", "Vince"],
        ],
        "sizes": {"top": "M", "numeric": "8", "bottom": "29", "shoe": "9"},
        "size_rows": [
            ["Tops", "8 / Medium", "Prefers easy fit"],
            ["Bottoms", "29/8", "Mid-rise preferred"],
            ["Dresses", "8", "Knee length"],
            ["Shoes", "9", "Flats preferred"],
        ],
        "purchase_patterns": [
            ["Last purchase", "2 months ago (knit top)"],
            ["Avg items/visit", "1.6"],
            ["Return rate", "12%"],
            ["Total spend (YTD)", "$1,150"],
        ],
        "purchase_brands": ["Vince"],
        "style_notes": "Prefers comfort and simple shapes",
        "loyalty_tier": "Gold",
        "points_balance_value": 15,
    },
}

OCCASIONS = {
    "business_dinner": {
        "label": "Business dinner with clients",
        "requirements": [
            ["Dress code", "Business elegant"],
            ["Impression", "Polished, confident"],
            ["Comfort level", "Seated dining, standing cocktails"],
            ["Her preference", "Structured, not stuffy"],
        ],
        "picks": [
            ["SKU-2001", 96, "Blazer: Her favorite Theory brand, structured silhouette she loves"],
            ["SKU-2002", 94, "Shell: Navy (her color), pairs with blazer"],
            ["SKU-2003", 92, "Pants: High-rise she prefers, versatile neutral"],
            ["SKU-2004", 91, "Dress option: One-piece alternative, midi length"],
        ],
        "avoid": ["Prints (she avoids)", "Fitted dresses (prefers relaxed)", "Trendy pieces (wants investment value)"],
    },
}

OUTFIT_TEMPLATES = {
    "business_dinner": [
        {"number": 1, "name": "Power Suiting", "pieces": [["Blazer", "SKU-2001"], ["Top", "SKU-2002"], ["Pants", "SKU-2003"], ["Shoes", "SKU-2005"], ["Bag", "SKU-2007"]], "recommended": True},
        {"number": 2, "name": "Elegant Simplicity", "pieces": [["Dress", "SKU-2004"], ["Blazer", "SKU-2001"], ["Shoes", "SKU-2008"], ["Jewelry", "SKU-2009"]], "recommended": False},
        {"number": 3, "name": "Modern Edge", "pieces": [["Jumpsuit", "SKU-2010"], ["Belt", "SKU-2011"], ["Earrings", "SKU-2012"], ["Clutch", "SKU-2013"]], "recommended": False},
    ],
}

LOYALTY_PROGRAM = {
    "Platinum": {"discount_pct": 10, "bundle_pct": 5, "bundle_min_pieces": 3, "free_alterations_value": 35},
    "Gold": {"discount_pct": 5, "bundle_pct": 5, "bundle_min_pieces": 3, "free_alterations_value": 0},
}

FOLLOW_UP_TRIGGERS = [
    ["New Theory arrivals", "Notification", "Automatic"],
    ["Pants low stock", "Alert", "If not purchased"],
    ["Wishlist items on sale", "Email", "When discounted"],
]

APPROVED_PERSONAS = {
    "Personal Shopper": "occasion-ready options and transparent tradeoffs",
    "Clienteling Specialist": "opt-in preferences, continuity, and respectful follow-up drafts",
    "Retail Manager": "consistency, availability caveats, and service quality",
}

SAFETY_NOTICE = (
    "> Synthetic opt-in preferences and inventory snapshots. Recommendations only; "
    "no sensitive traits are inferred, inventory is not reserved, benefits are not "
    "applied, and no return, refund, order, or purchase is completed."
)

_OPERATIONS = [
    "product_recommendations",
    "style_profile",
    "inventory_check",
    "outfit_builder",
    "pricing_offer",
    "session_summary",
]


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Personal Shopper"
    return [
        f"**Prepared for:** {role}",
        f"**Role focus:** {APPROVED_PERSONAS[role]}",
        "",
        SAFETY_NOTICE,
        "",
    ]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_customer(query):
    """Customer ID, full name or first name; SHOP-001 when empty; None when nothing matches."""
    if not query:
        return "SHOP-001"
    q = str(query).lower().strip()
    for cid, prefs in CUSTOMER_PREFERENCES.items():
        if cid.lower() in q or prefs["alias"] in q or q in prefs["name"].lower():
            return cid
    return None


def _resolve_occasion(query):
    """The packaged occasion; business_dinner is the only synthetic occasion, so any wording maps to it."""
    return "business_dinner"


def _size_for(product, prefs):
    if product["size_type"] == "one_size":
        return "One size"
    return prefs["sizes"][product["size_type"]]


def _store_qty(product, prefs, location):
    return product["stock"].get(location, {}).get(_size_for(product, prefs), 0)


def _status(qty):
    if qty >= 2:
        return "In stock"
    if qty == 1:
        return "Low stock (1 left)"
    return "Out of stock here"


def _outfit_items(outfit, prefs, swap):
    """(piece, sku) pairs; with swap, an out-of-stock piece is replaced by its in-stock alternative."""
    items = []
    for piece, sku in outfit["pieces"]:
        product = PRODUCT_CATALOG[sku]
        if swap and _store_qty(product, prefs, "store") == 0 and product.get("alternative"):
            alt = PRODUCT_CATALOG[product["alternative"]]
            if _store_qty(alt, prefs, "store") > 0:
                sku = product["alternative"]
        items.append([piece, sku])
    return items


def _recommended(occasion):
    for outfit in OUTFIT_TEMPLATES[occasion]:
        if outfit["recommended"]:
            return outfit
    return OUTFIT_TEMPLATES[occasion][0]


def _offer(items, prefs):
    """Loyalty pricing in whole dollars: tier discount on the total, bundle bonus on the rest, then points."""
    tier = LOYALTY_PROGRAM[prefs["loyalty_tier"]]
    original = 0
    for _, sku in items:
        original += PRODUCT_CATALOG[sku]["price"]
    tier_off = original * tier["discount_pct"] // 100
    bundle_off = 0
    if len(items) >= tier["bundle_min_pieces"]:
        bundle_off = ((original - tier_off) * tier["bundle_pct"] + 50) // 100
    points = prefs["points_balance_value"]
    final = original - tier_off - bundle_off - points
    savings = original - final
    return {"original": original, "tier_off": tier_off, "bundle_off": bundle_off, "points": points,
            "final": final, "savings": savings, "savings_pct": savings * 100 // original}


def _in_store_count(items, prefs):
    count = 0
    for _, sku in items:
        if _store_qty(PRODUCT_CATALOG[sku], prefs, "store") > 0:
            count += 1
    return count


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class PersonalizedShoppingAssistantAgent(BasicAgent):
    """Personalized shopping assistant agent."""

    def __init__(self):
        self.name = "PersonalizedShoppingAssistantAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Personalized Shopping Assistant Agent",
            "description": (
                f"{__manifest__['description']} Always call this tool for a personal-styling session: "
                "finding the perfect outfit for a customer from her style preferences and purchase history "
                "(`style_profile`), an occasion such as a business dinner with clients "
                "(`product_recommendations`), complete outfit options with accessories (`outfit_builder`), "
                "inventory and what is in stock for her size (`inventory_check`), the best offer or loyalty "
                "pricing (`pricing_offer`), and wrapping up or saving the session to her profile "
                "(`session_summary`). The demo client is Jennifer Hayes (SHOP-001) shopping for a business "
                "dinner; when no customer or occasion is named, omit them and the agent uses that session. "
                "Never ask which shopper or occasion to use."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Required routing key. style_profile to find the perfect outfit for a customer "
                            "based on style preferences and purchase history (her profile); "
                            "product_recommendations when an occasion is named (e.g. 'she needs an outfit for "
                            "a business dinner with clients'); outfit_builder for complete outfit options, "
                            "looks, accessories or outfit totals; inventory_check for inventory, availability "
                            "or what is in stock for her size; pricing_offer for the best offer, price or "
                            "loyalty benefits; session_summary to wrap up, summarize or save everything to "
                            "her profile. Do not ask a follow-up or substitute another operation."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "customer_id": {
                        "type": "string",
                        "description": (
                            "Synthetic client: Jennifer Hayes or Jennifer is SHOP-001 (the default); Synthetic "
                            "Shopper B is SHOP-002. Omit when the prompt names no customer; the agent uses "
                            "SHOP-001 and must not ask for clarification."
                        ),
                    },
                    "occasion": {
                        "type": "string",
                        "description": "Occasion in the user's words; the packaged occasion is a business dinner with clients (default).",
                    },
                    "sku": {
                        "type": "string",
                        "description": "Synthetic SKU (SKU-2001 to SKU-2013) for a single-item inventory_check.",
                    },
                    "persona": {
                        "type": "string",
                        "enum": list(APPROVED_PERSONAS),
                        "description": "Copy the role stated in the request.",
                    },
                    "data_source": {"type": "string", "enum": ["synthetic"]},
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        if kwargs.get("data_source", "synthetic") != "synthetic":
            return "data_source must be `synthetic` for this package."
        customer_id = _resolve_customer(kwargs.get("customer_id"))
        if customer_id is None:
            return (
                f"Unknown customer_id `{kwargs.get('customer_id')}`. Valid synthetic IDs: "
                f"{', '.join(CUSTOMER_PREFERENCES)}"
            )
        sku = kwargs.get("sku")
        if sku and sku not in PRODUCT_CATALOG:
            return f"Unknown sku `{sku}`. Valid: {', '.join(PRODUCT_CATALOG)}"
        occasion = _resolve_occasion(kwargs.get("occasion"))
        operation = kwargs.get("operation", "style_profile")
        dispatch = {
            "product_recommendations": self._product_recommendations,
            "style_profile": self._style_profile,
            "inventory_check": self._inventory_check,
            "outfit_builder": self._outfit_builder,
            "pricing_offer": self._pricing_offer,
            "session_summary": self._session_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        header = _response_header(kwargs.get("persona"))
        return "\n".join(header) + "\n" + handler(customer_id, occasion, kwargs)

    # -- style_profile: video turn 1 ------------------------------------------
    def _style_profile(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        lines = [f"# Opt-In Style Profile: {prefs['name']}\n"]
        lines.append("**Customer Style Profile:**\n")
        lines.append("| Attribute | Preference |\n|---|---|")
        for attr, value in prefs["profile"]:
            lines.append(f"| {attr} | {value} |")
        lines.append("\n**Size Information:**\n")
        lines.append("| Category | Size | Notes |\n|---|---|---|")
        for cat, size, note in prefs["size_rows"]:
            lines.append(f"| {cat} | {size} | {note} |")
        lines.append("\n**Recent Purchase Patterns:**\n")
        for label, value in prefs["purchase_patterns"]:
            lines.append(f"- {label}: {value}")
        lines.append(f"\n**Style Notes from Past Sessions:** \"{prefs['style_notes']}\"")
        lines.append("\nThese are stated, opt-in preferences; nothing else is inferred.")
        lines.append("\nSource: [Purchase History + Style Profile + CRM Notes] Agents: StyleProfileAgent, OccasionMatchingAgent")
        lines.append("\n**Next step:** what occasion is she shopping for?")
        return "\n".join(lines)

    # -- product_recommendations: video turn 2 --------------------------------
    def _product_recommendations(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        occ = OCCASIONS[occasion]
        first = prefs["name"].split(" ")[0]
        lines = [f"# Draft Product Recommendations: {prefs['name']} ({occ['label']})\n"]
        lines.append("**Occasion Analysis:**\n")
        lines.append("| Requirement | Recommendation |\n|---|---|")
        for req, rec in occ["requirements"]:
            lines.append(f"| {req} | {rec} |")
        lines.append(f"\n**Top Picks for {first}:**\n")
        lines.append("| Item | Brand | Price | Match Score |\n|---|---|---|---|")
        for sku, score, _ in occ["picks"]:
            p = PRODUCT_CATALOG[sku]
            lines.append(f"| {p['name']} ({sku}) | {p['brand']} | ${p['price']:,} | {score}% |")
        lines.append("\n**Why These Selections:**\n")
        for _, _, why in occ["picks"]:
            lines.append(f"- {why}")
        lines.append("\n**Not Recommended:**\n")
        for item in occ["avoid"]:
            lines.append(f"- {item}")
        lines.append("\nSource: [Recommendation Engine + Occasion Database] Agents: ProductRecommendationAgent, OccasionMatchingAgent")
        lines.append("\n**Next step:** see complete outfit combinations?")
        return "\n".join(lines)

    # -- outfit_builder: video turn 3 -----------------------------------------
    def _outfit_builder(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        lines = [f"# Draft Outfit Builder: {prefs['name']} ({OCCASIONS[occasion]['label']})\n"]
        for outfit in OUTFIT_TEMPLATES[occasion]:
            tag = " (recommended)" if outfit["recommended"] else ""
            lines.append(f"## Outfit {outfit['number']}: {outfit['name']}{tag}\n")
            lines.append("| Piece | Item | Price |\n|---|---|---|")
            total = 0
            for piece, sku in outfit["pieces"]:
                p = PRODUCT_CATALOG[sku]
                total += p["price"]
                lines.append(f"| {piece} | {p['brand']} {p['name']} | ${p['price']:,} |")
            lines.append(f"| **Total** | | **${total:,}** |\n")
        rec = _recommended(occasion)
        lines.append(f"**Stylist Recommendation:** Outfit {rec['number']} ({rec['name']}) - most aligned with her established style.")
        lines.append("\nSource: [Outfit Coordination Engine + Style Rules] Agents: OutfitCoordinationAgent, ProductRecommendationAgent")
        lines.append("\n**Next step:** check availability for her sizes?")
        return "\n".join(lines)

    # -- inventory_check: video turn 4 ----------------------------------------
    def _inventory_check(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        sku = kwargs.get("sku")
        if sku:
            product = PRODUCT_CATALOG[sku]
            lines = [f"# Inventory Snapshot: {product['brand']} {product['name']} ({sku})\n"]
            lines.append(f"- **Price:** ${product['price']:,}")
            lines.append(f"- **Her size:** {_size_for(product, prefs)}\n")
            lines.append("| Location | Size | Stock | Status |\n|---|---|---|---|")
            for location, sizes in product["stock"].items():
                for size, qty in sizes.items():
                    lines.append(f"| {location.title()} | {size} | {qty} | {_status(qty)} |")
            return "\n".join(lines)
        lines = [f"# Inventory Snapshot: {prefs['name']}'s sizes ({OCCASIONS[occasion]['label']})\n"]
        rec = _recommended(occasion)
        for outfit in OUTFIT_TEMPLATES[occasion]:
            lines.append(f"## Outfit {outfit['number']} Availability: {outfit['name']}\n")
            lines.append("| Item | Size | Status |\n|---|---|---|")
            notes = []
            for piece, sku_ in outfit["pieces"]:
                p = PRODUCT_CATALOG[sku_]
                size = _size_for(p, prefs)
                qty = _store_qty(p, prefs, "store")
                lines.append(f"| {p['brand']} {p['name'].lower()} | {size} | {_status(qty)} |")
                if qty == 0:
                    alt_sku = p.get("alternative")
                    if alt_sku and _store_qty(PRODUCT_CATALOG[alt_sku], prefs, "store") > 0:
                        alt = PRODUCT_CATALOG[alt_sku]
                        diff = alt["price"] - p["price"]
                        known = "Customer has purchased this brand before (good fit)" if alt["brand"] in prefs["purchase_brands"] else "New brand for her"
                        notes.append(
                            f"**{piece} Alternative:** {alt['brand']} {alt['name'].lower()} - Size {_size_for(alt, prefs)} in stock; "
                            f"{alt.get('note', 'similar style')}, ${alt['price']:,} (+${diff:,}). {known}."
                        )
                    else:
                        here = [s for s, n in p["stock"]["store"].items() if n > 0]
                        if here:
                            notes.append(f"- {p['piece']} only in size {', '.join(here)} here")
                        if _store_qty(p, prefs, "warehouse") > 0:
                            notes.append("- Can ship from warehouse (2 days)")
                        if _store_qty(p, prefs, "downtown") > 0:
                            notes.append("- Or available at downtown location")
            if notes:
                lines.append("")
                lines.extend(notes)
            lines.append("")
        items = _outfit_items(rec, prefs, True)
        lines.append(
            f"**Recommendation:** Outfit {rec['number']} fully available today with shoe swap "
            f"({_in_store_count(rec['pieces'], prefs)} of {len(rec['pieces'])} original pieces in store; "
            f"{_in_store_count(items, prefs)} of {len(items)} with the swap). Nothing is held or reserved."
        )
        lines.append("\nSource: [Inventory System + Store Network] Agents: InventoryAvailabilityAgent, ProductRecommendationAgent")
        lines.append("\n**Next step:** see pricing with her loyalty benefits?")
        return "\n".join(lines)

    # -- pricing_offer: video turn 5 ------------------------------------------
    def _pricing_offer(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        outfit = _recommended(occasion)
        items = _outfit_items(outfit, prefs, True)
        tier = LOYALTY_PROGRAM[prefs["loyalty_tier"]]
        offer = _offer(items, prefs)
        lines = [f"# Loyalty Pricing: Outfit {outfit['number']} {outfit['name']} for {prefs['name']}\n"]
        lines.append(f"**Tier:** {prefs['loyalty_tier']} ({tier['discount_pct']}% member pricing)\n")
        lines.append("| Item | Price | Her Price | Benefit |\n|---|---|---|---|")
        for _, sku in items:
            p = PRODUCT_CATALOG[sku]
            lines.append(
                f"| {p['brand']} {p['name'].lower()} | ${p['price']:,} | ${p['price'] * (100 - tier['discount_pct']) // 100:,} "
                f"| {tier['discount_pct']}% {prefs['loyalty_tier']} |"
            )
        lines.append("\n**Additional Offers:**\n")
        lines.append("| Offer | Value | Conditions |\n|---|---|---|")
        lines.append(f"| Bundle bonus | Extra {tier['bundle_pct']}% | {tier['bundle_min_pieces']}+ pieces |")
        lines.append(f"| Points redemption | -${offer['points']} | Use balance |")
        if tier["free_alterations_value"]:
            lines.append(f"| Free alterations | ${tier['free_alterations_value']} value | {prefs['loyalty_tier']} perk |")
        lines.append("\n**Best Deal Package:**\n")
        lines.append("| | Amount |\n|---|---|")
        lines.append(f"| Original total | ${offer['original']:,} |")
        lines.append(f"| {prefs['loyalty_tier']} discount ({tier['discount_pct']}%) | -${offer['tier_off']:,} |")
        lines.append(f"| Bundle bonus ({tier['bundle_pct']}%) | -${offer['bundle_off']:,} |")
        lines.append(f"| Points applied | -${offer['points']:,} |")
        lines.append(f"| **Final price** | **${offer['final']:,}** |")
        lines.append(f"| Total savings | ${offer['savings']:,} ({offer['savings_pct']}%) |")
        lines.append(
            "\nCalculated for the stylist to present; the member discount applies to the order total and the "
            "bundle bonus to the discounted total. Nothing is charged, and the benefits are applied only when "
            "you ring up the order."
        )
        lines.append("\nSource: [Pricing Engine + Loyalty System + Promotions] Agents: PricingOptimizationAgent, InventoryAvailabilityAgent")
        lines.append("\n**Next step:** generate the session summary?")
        return "\n".join(lines)

    # -- session_summary: video turn 6 ----------------------------------------
    def _session_summary(self, customer_id, occasion, kwargs) -> str:
        prefs = CUSTOMER_PREFERENCES[customer_id]
        rec = _recommended(occasion)
        items = _outfit_items(rec, prefs, True)
        offer = _offer(items, prefs)
        outfits = OUTFIT_TEMPLATES[occasion]
        others = " & ".join(str(o["number"]) for o in outfits if not o["recommended"])
        swapped = []
        for piece, sku in items:
            brand = PRODUCT_CATALOG[sku]["brand"]
            if sku not in [s for _, s in rec["pieces"]]:
                swapped.append(brand)
        lines = [f"# Session Summary: {prefs['name']} ({OCCASIONS[occasion]['label']})\n"]
        lines.append("| Accomplishment | Result |\n|---|---|")
        lines.append(f"| Style profile applied | {len(prefs['profile'])} preferences matched |")
        lines.append(f"| Outfits created | {len(outfits)} complete looks |")
        lines.append(f"| Recommended outfit | {rec['name']} (#{rec['number']}) |")
        lines.append(f"| Availability confirmed | {_in_store_count(rec['pieces'], prefs)} of {len(rec['pieces'])} in store |")
        lines.append(f"| Savings delivered | ${offer['savings']:,} ({offer['savings_pct']}%) on ${offer['final']:,} |")
        lines.append("\n**Profile updates, ready for you to save:**\n")
        lines.append(f"- Outfit {rec['number']}: save as \"Business Dinner Look\"")
        lines.append(f"- Outfits {others}: add to wishlist")
        lines.append("- Size preferences: confirmed accurate")
        for brand in swapped:
            lines.append(f"- Brand note: {brand} added")
        lines.append("\n**Proposed follow-ups (not scheduled):**\n")
        lines.append("| Trigger | Action | Timing |\n|---|---|---|")
        for trigger, action, timing in FOLLOW_UP_TRIGGERS:
            lines.append(f"| {trigger} | {action} | {timing} |")
        lines.append(
            "\nNothing was written to her profile and no message was sent; confirm these updates in the "
            "clienteling system."
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = PersonalizedShoppingAssistantAgent()
    for op in ["style_profile", "product_recommendations", "outfit_builder", "inventory_check", "pricing_offer", "session_summary"]:
        print("=" * 80)
        print(agent.perform(operation=op))
        print()
