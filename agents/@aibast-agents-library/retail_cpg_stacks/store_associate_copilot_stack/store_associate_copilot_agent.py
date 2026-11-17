"""
Store Associate Copilot Agent — Retail & CPG Stack

Empowers store associates with product lookup, customer assistance
scripts, daily task management, and performance dashboards.
"""

import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"),
)
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/store-associate-copilot",
    "version": "1.0.0",
    "display_name": "Retail Store Associate Copilot",
    "description": (
        "Provide synthetic product intelligence, customer-assistance drafts, task planning, and aggregate coaching insights for associate review."
    ),
    "author": "AIBAST",
    "tags": [
        "store-operations",
        "associate",
        "copilot",
        "product-lookup",
        "retail",
    ],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic Data — Product Catalog
# ---------------------------------------------------------------------------

PRODUCT_CATALOG = {
    "SKU-1005": {
        "key": "techpro",
        "name": "TechPro X-Series Wireless Headphones",
        "short_name": "TechPro X-Series",
        "category": "Headphones",
        "type": "product",
        "brand": "TechPro",
        "retail_price": 199.99,
        "regular_price": 249.99,
        "promotion": "Save $50 (regular $249.99), ends Sunday",
        "store": "Bellevue",
        "on_hand": 14,
        "battery_hours": 38,
        "battery_detail": "38 hours continuous",
        "anc_db": 42,
        "noise_cancellation": "Active ANC, -42dB",
        "sound_quality": "Premium",
        "warranty": "2 years standard",
        "colors": ["Matte Black", "Silver"],
        "location_aisle": "E1",
        "location_shelf": "Headphone wall",
        "upc": "0-12345-67890-5",
        "selling_points": [
            "Industry-leading 38hr battery (vs competitors 24-30hr)",
            "Multi-device pairing (3 devices simultaneously)",
            "Foldable design with premium case included",
        ],
        "rating": 4.7,
        "review_count": 847,
        "review_summary": "Praised for comfort and battery life",
        "review_quote": "Amazing battery",
        "best_for": ["Long flights", "all-day use", "budget-conscious"],
    },
    "SKU-1006": {
        "key": "soundmax",
        "name": "SoundMax Pro Wireless Headphones",
        "short_name": "SoundMax Pro",
        "category": "Headphones",
        "type": "product",
        "brand": "SoundMax",
        "retail_price": 229.99,
        "regular_price": 229.99,
        "promotion": "",
        "store": "Bellevue",
        "on_hand": 3,
        "battery_hours": 30,
        "battery_detail": "30 hours continuous",
        "anc_db": 48,
        "noise_cancellation": "Active ANC, -48dB",
        "sound_quality": "Audiophile",
        "warranty": "1 year standard",
        "colors": ["Graphite"],
        "location_aisle": "E1",
        "location_shelf": "Headphone wall",
        "upc": "0-12345-67890-6",
        "selling_points": [
            "Audiophile-grade drivers",
            "Strongest noise cancellation in the store (-48dB)",
        ],
        "rating": 4.8,
        "review_count": 623,
        "review_summary": "Praised for sound quality",
        "review_quote": "Best sound ever",
        "best_for": ["Music enthusiasts", "home listening", "best audio"],
    },
    "SKU-1002": {
        "key": "earbuds",
        "name": "SoundWave Wireless Earbuds Pro",
        "short_name": "Wireless Earbuds Pro",
        "category": "Earbuds",
        "type": "product",
        "brand": "SoundWave",
        "retail_price": 59.99,
        "regular_price": 59.99,
        "promotion": "",
        "store": "Bellevue",
        "on_hand": 132,
        "battery_hours": 8,
        "battery_detail": "8 hours (32 with case)",
        "anc_db": 30,
        "noise_cancellation": "Active ANC, -30dB",
        "sound_quality": "Standard",
        "warranty": "1 year standard",
        "colors": ["Matte Black", "Pearl White", "Navy"],
        "location_aisle": "E1",
        "location_shelf": "Locked case",
        "upc": "0-12345-67890-2",
        "selling_points": ["IPX4 water resistant", "Bluetooth 5.3"],
        "rating": 4.4,
        "review_count": 1210,
        "review_summary": "Praised for fit and value",
        "review_quote": "Great value",
        "best_for": ["Workouts", "commuting", "pocket size"],
    },
    "SKU-1011": {
        "key": "warranty",
        "name": "Extended Warranty (3-year)",
        "short_name": "Extended Warranty",
        "category": "Protection Plan",
        "type": "warranty",
        "brand": "TechPro",
        "retail_price": 39.99,
        "regular_price": 39.99,
        "note": "3-year coverage, 87% attach rate",
        "on_hand": 999,
        "location_aisle": "Register",
        "location_shelf": "Added at checkout",
        "upc": "0-12345-67891-1",
    },
    "SKU-1012": {
        "key": "cleaning",
        "name": "Premium Cleaning Kit",
        "short_name": "Premium Cleaning Kit",
        "category": "Accessories",
        "type": "accessory",
        "brand": "TechPro",
        "retail_price": 24.99,
        "regular_price": 24.99,
        "note": "Branded TechPro, high margin",
        "on_hand": 40,
        "location_aisle": "E2",
        "location_shelf": "Accessory pegs",
        "upc": "0-12345-67891-2",
    },
    "SKU-1013": {
        "key": "adapter",
        "name": "Travel Adapter",
        "short_name": "Travel Adapter",
        "category": "Accessories",
        "type": "accessory",
        "brand": "TechPro",
        "retail_price": 19.99,
        "regular_price": 19.99,
        "note": "USB-C fast charging",
        "on_hand": 55,
        "location_aisle": "E2",
        "location_shelf": "Accessory pegs",
        "upc": "0-12345-67891-3",
    },
    "SKU-1014": {
        "key": "cushion",
        "name": "Replacement Cushions",
        "short_name": "Replacement Cushions",
        "category": "Accessories",
        "type": "accessory",
        "brand": "TechPro",
        "retail_price": 34.99,
        "regular_price": 34.99,
        "note": "Memory foam upgrade",
        "on_hand": 22,
        "location_aisle": "E2",
        "location_shelf": "Accessory pegs",
        "upc": "0-12345-67891-4",
    },
}

HERO_SKU = "SKU-1005"

# Add-on bundles a customer can choose at checkout.
ADDON_BUNDLES = {
    "warranty and cleaning kit": ["SKU-1011", "SKU-1012"],
    "warranty": ["SKU-1011"],
    "cleaning kit": ["SKU-1012"],
    "all add-ons": ["SKU-1011", "SKU-1012", "SKU-1013", "SKU-1014"],
    "none": [],
}

# Commission and checkout terms in basis points (800 = 8%).
COMMISSION_RATES_BP = {"product": 800, "warranty": 1800, "accessory": 1200}

CHECKOUT_TERMS = {
    "loyalty_discount_bp": {"Gold": 500, "Silver": 300, "Bronze": 0},
    "sales_tax_bp": 850,
    "financing_months": 6,
    "financing_apr": "0% APR",
    "store_card_bonus_points": 500,
    "default_loyalty_tier": "Gold",
    "conversion_tip": "Mention the cleaning kit extends cushion life - drives 65% conversion",
}

CUSTOMER_INTERACTION_SCRIPTS = {
    "greeting": {
        "scenario": "Customer enters the store",
        "script": "Draft: Welcome the shopper and ask what category they would like help finding.",
        "follow_up": "If they mention a product category, guide them to the correct aisle.",
        "tips": ["Make eye contact", "Smile genuinely", "Keep a comfortable distance"],
    },
    "upsell": {
        "scenario": "Customer is ready to purchase a single item",
        "script": "Draft: If useful, mention one relevant complementary item without pressure.",
        "follow_up": "If interested, walk them to the complementary item. If not, respect their decision.",
        "tips": ["Suggest only relevant items", "Limit to one upsell attempt", "Focus on value not price"],
    },
    "complaint_handling": {
        "scenario": "Customer has a complaint or issue",
        "script": "Draft: Acknowledge the concern, restate it, and explain that an authorized associate will review options.",
        "follow_up": "Listen fully, repeat back the issue, offer a concrete solution within your authority.",
        "tips": ["Never argue", "Acknowledge their frustration", "Offer alternatives if first solution is declined"],
    },
    "size_help": {
        "scenario": "Customer needs sizing assistance",
        "script": "Draft: Ask which size the shopper would like checked; do not infer body characteristics.",
        "follow_up": "Check fitting room availability. Bring two sizes if customer is between sizes.",
        "tips": ["Be sensitive about sizing", "Suggest trying multiple sizes", "Check stock for requested size first"],
    },
    "return_at_counter": {
        "scenario": "Customer wants to make a return at the register",
        "script": "Draft: Ask whether proof of purchase is available and explain that return eligibility requires authorized review.",
        "follow_up": "Verify return eligibility per policy. Process efficiently and offer exchange if applicable.",
        "tips": ["Stay positive and empathetic", "Explain policy clearly", "Thank them regardless of outcome"],
    },
}

DAILY_TASK_LIST = {
    "opening": [
        {"task": "Unlock entrance doors and disable alarm", "priority": "critical", "est_minutes": 2},
        {"task": "Power on POS terminals and verify connectivity", "priority": "critical", "est_minutes": 5},
        {"task": "Walk floor to check overnight display condition", "priority": "high", "est_minutes": 10},
        {"task": "Restock fitting rooms with hangers", "priority": "medium", "est_minutes": 5},
        {"task": "Review daily promotions and update signage", "priority": "high", "est_minutes": 15},
        {"task": "Check inventory alerts and pull items for floor replenishment", "priority": "high", "est_minutes": 20},
    ],
    "midday": [
        {"task": "Restock high-traffic areas and end caps", "priority": "high", "est_minutes": 20},
        {"task": "Process online pickup orders (BOPIS)", "priority": "critical", "est_minutes": 15},
        {"task": "Clean fitting rooms and return abandoned items", "priority": "medium", "est_minutes": 10},
        {"task": "Rotate break schedule for floor coverage", "priority": "high", "est_minutes": 5},
        {"task": "Check and respond to customer service queue", "priority": "high", "est_minutes": 10},
    ],
    "closing": [
        {"task": "Process remaining BOPIS orders for next-day pickup", "priority": "critical", "est_minutes": 15},
        {"task": "Reconcile POS drawers and prepare deposit", "priority": "critical", "est_minutes": 20},
        {"task": "Tidy all displays and return misplaced merchandise", "priority": "high", "est_minutes": 25},
        {"task": "Vacuum high-traffic aisles", "priority": "medium", "est_minutes": 15},
        {"task": "Set alarm and lock all entrances", "priority": "critical", "est_minutes": 3},
    ],
}

ASSOCIATE_PERFORMANCE = {
    "ASC-101": {
        "name": "Opening Senior Associate Cohort",
        "role": "Senior Associate",
        "shift": "opening",
        "units_sold_today": 23,
        "revenue_today": 1847.50,
        "transactions_today": 14,
        "avg_basket": 131.96,
        "upsell_rate": 0.35,
        "csat_score": 4.8,
        "tasks_completed": 11,
        "tasks_total": 12,
        "hours_this_week": 32.5,
    },
    "ASC-102": {
        "name": "Midday Associate Cohort",
        "role": "Associate",
        "shift": "midday",
        "units_sold_today": 17,
        "revenue_today": 1295.80,
        "transactions_today": 11,
        "avg_basket": 117.80,
        "upsell_rate": 0.22,
        "csat_score": 4.5,
        "tasks_completed": 8,
        "tasks_total": 10,
        "hours_this_week": 28.0,
    },
    "ASC-103": {
        "name": "Closing Associate Cohort",
        "role": "Associate",
        "shift": "closing",
        "units_sold_today": 12,
        "revenue_today": 985.40,
        "transactions_today": 9,
        "avg_basket": 109.49,
        "upsell_rate": 0.18,
        "csat_score": 4.3,
        "tasks_completed": 7,
        "tasks_total": 9,
        "hours_this_week": 24.0,
    },
    "ASC-104": {
        "name": "Opening Lead Associate Cohort",
        "role": "Lead Associate",
        "shift": "opening",
        "units_sold_today": 29,
        "revenue_today": 2410.30,
        "transactions_today": 18,
        "avg_basket": 133.91,
        "upsell_rate": 0.40,
        "csat_score": 4.9,
        "tasks_completed": 12,
        "tasks_total": 12,
        "hours_this_week": 36.0,
    },
}

COMPLEMENTARY_PRODUCTS = {
    "SKU-1005": ["SKU-1011", "SKU-1012", "SKU-1013", "SKU-1014"],
    "SKU-1006": ["SKU-1011", "SKU-1013"],
    "SKU-1002": ["SKU-1011"],
}

APPROVED_PERSONAS = {
    "Store Associate": "clear product facts and respectful customer-assistance drafts",
    "Sales Manager": "aggregate coaching signals and operational review",
    "Floor Specialist": "location, availability, and task-planning detail",
}

SAFETY_NOTICE = (
    "> Synthetic planning snapshot. Recommendations and scripts are drafts only; "
    "availability is not guaranteed, inventory is not reserved, and no message, "
    "offer, return, refund, transaction, or purchase is completed."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Store Associate"
    return [f"**Prepared for:** {role} ({APPROVED_PERSONAS[role]})", ""]


def _footer():
    return ["", SAFETY_NOTICE]


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

_PRODUCT_NAMES = ["TechPro X-Series", "SoundMax Pro", "Wireless Earbuds Pro"]

def _by_name(name):
    """SKU whose short name or SKU id equals the given value; None when no product matches."""
    for sku_id, prod in PRODUCT_CATALOG.items():
        if prod["short_name"] == name or sku_id == name:
            return sku_id
    return None


def _cents(price):
    return int(round(price * 100))


def _pct_of(cents, bp):
    """Basis-point share of an amount in cents, rounded half up to the cent."""
    return (cents * bp + 5000) // 10000


def _money(cents):
    return f"${cents // 100:,}.{cents % 100:02d}"


def _store_total_revenue():
    return sum(a["revenue_today"] for a in ASSOCIATE_PERFORMANCE.values())


def _store_total_transactions():
    return sum(a["transactions_today"] for a in ASSOCIATE_PERFORMANCE.values())


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "product_lookup",
    "customer_assist",
    "task_checklist",
    "performance_dashboard",
    "accessory_recommendations",
    "product_compare",
    "prepare_transaction",
]


class StoreAssociateCopilotAgent(BasicAgent):
    """Copilot agent assisting store associates with daily operations."""

    def __init__(self):
        self.name = "store-associate-copilot-agent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always use this tool when a store associate asks about a "
                "product on the floor (the demo product is the TechPro X-Series wireless headphones in the "
                "Bellevue store), its accessories and commission, a comparison with another model (SoundMax "
                "Pro), or getting a sale ready. Never completes a sale, charge, or discount: the transaction "
                "is prepared for the associate to ring up."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "product_lookup: is a product in stock and what are its key features, price and "
                            "promotion (e.g. 'TechPro wireless headphones'). accessory_recommendations: "
                            "compatible accessories, warranty add-ons and the associate's commission. "
                            "product_compare: compare the product with another model (e.g. SoundMax Pro) or "
                            "find alternatives. prepare_transaction: the customer chose items - start / prepare "
                            "the transaction with loyalty discount, tax and payment options. customer_assist: "
                            "draft language for greeting, upsell, complaint, sizing or return conversations. "
                            "task_checklist: shift task planning. performance_dashboard: aggregate cohort "
                            "coaching signals."
                        ),
                    },
                    "sku_id": {
                        "type": "string",
                        "enum": list(PRODUCT_CATALOG),
                        "description": "Catalog SKU: SKU-1005 TechPro X-Series headphones (default), SKU-1006 SoundMax Pro, SKU-1002 Wireless Earbuds Pro, SKU-1011 Extended Warranty, SKU-1012 Premium Cleaning Kit, SKU-1013 Travel Adapter, SKU-1014 Replacement Cushions",
                    },
                    "product": {
                        "type": "string",
                        "enum": _PRODUCT_NAMES,
                        "description": "Product the customer asks about, by name (alternative to sku_id), e.g. 'TechPro X-Series'",
                    },
                    "compare_with": {
                        "type": "string",
                        "enum": _PRODUCT_NAMES,
                        "description": "product_compare: the second product by name or SKU, e.g. 'SoundMax Pro' or 'SKU-1006' (default SoundMax Pro)",
                    },
                    "addons": {
                        "type": "string",
                        "enum": list(ADDON_BUNDLES),
                        "description": "prepare_transaction: one of the listed add-on bundles, exactly as written (warranty plus cleaning kit = 'warranty and cleaning kit', the default)",
                    },
                    "loyalty_tier": {"type": "string", "enum": ["Gold", "Silver", "Bronze"], "description": "Customer loyalty tier (default Gold)"},
                    "scenario": {"type": "string"},
                    "shift": {"type": "string"},
                    "persona": {
                        "type": "string",
                        "enum": list(APPROVED_PERSONAS),
                    },
                    "data_source": {"type": "string", "enum": ["synthetic"]},
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _resolve(self, kwargs):
        """(sku_id, product) from sku_id or product name; the hero product when neither is given; (None, msg) on a miss."""
        sku_id = kwargs.get("sku_id", "")
        product = kwargs.get("product", "")
        if sku_id:
            if sku_id not in PRODUCT_CATALOG:
                return None, f"Unknown sku_id `{sku_id}`. Valid: {', '.join(PRODUCT_CATALOG)}"
            return sku_id, PRODUCT_CATALOG[sku_id]
        if product:
            found = _by_name(product)
            if found is None:
                return None, f"No products found for: \"{product}\""
            return found, PRODUCT_CATALOG[found]
        return HERO_SKU, PRODUCT_CATALOG[HERO_SKU]

    def _product_lookup(self, **kwargs):
        sid, prod = self._resolve(kwargs)
        lines = _response_header(kwargs.get("persona")) + ["# Product Lookup Snapshot", ""]
        if sid is None:
            return "\n".join(lines + [prod] + _footer())
        stock = "in stock" if prod["on_hand"] > 0 else "out of stock"
        lines.append(
            f"{prod['name']} (`{sid}`) are {stock} with {prod['on_hand']} units available in your "
            f"{prod.get('store', 'local')} store (synthetic on-hand snapshot; verify before advising)."
        )
        lines.append("")
        if prod["type"] != "product":
            lines.append(f"- **Price:** ${prod['retail_price']:.2f} — {prod['note']}")
            lines.append(f"- **Location:** Aisle {prod['location_aisle']}, {prod['location_shelf']}")
            return "\n".join(lines + _footer())
        sale = " (on sale)" if prod["promotion"] else ""
        lines += [
            "**Product Details:**",
            "",
            "| Feature | Specification |",
            "|---|---|",
            f"| Battery life | {prod['battery_detail']} |",
            f"| Noise cancellation | {prod['noise_cancellation']} |",
            f"| Price | ${prod['retail_price']:.2f}{sale} |",
            f"| Warranty | {prod['warranty']} |",
            f"| Location | Aisle {prod['location_aisle']}, {prod['location_shelf']} |",
            "",
            "**Key Selling Points:**",
        ]
        for point in prod["selling_points"]:
            lines.append(f"- {point}")
        lines.append("")
        if prod["promotion"]:
            lines.append(f"**Current Promotion:** {prod['promotion']}")
        lines.append(
            f"**Customer Reviews:** {prod['rating']}/5.0 stars ({prod['review_count']} reviews) - {prod['review_summary']}"
        )
        comp = [PRODUCT_CATALOG[c]["short_name"] for c in COMPLEMENTARY_PRODUCTS.get(sid, [])]
        if comp:
            lines.append(f"**Optional Complementary Ideas:** {', '.join(comp)}")
        if prod["on_hand"] <= 3:
            alts = [p["short_name"] + f" ({p['on_hand']} units)" for k, p in PRODUCT_CATALOG.items()
                    if k != sid and p["category"] == prod["category"] and p["on_hand"] > 3]
            if alts:
                lines.append(f"**Low stock - in-stock alternatives:** {', '.join(alts)}")
        lines += ["", "Source: [Store POS + Product Database] (synthetic)", "",
                  "Want to see compatible accessories or alternative options?"]
        return "\n".join(lines + _footer())

    def _accessory_recommendations(self, **kwargs):
        sid, prod = self._resolve(kwargs)
        lines = _response_header(kwargs.get("persona")) + ["# Accessory and Commission Snapshot", ""]
        if sid is None:
            return "\n".join(lines + [prod] + _footer())
        addons = [(k, PRODUCT_CATALOG[k]) for k in COMPLEMENTARY_PRODUCTS.get(sid, [])]
        lines.append(f"Compatible accessories for the {prod['short_name']} and your commission breakdown for the full package.")
        lines += ["", "**Recommended Add-Ons:**"]
        for _, a in addons:
            lines.append(f"- {a['name'].replace(' (3-year)', '')} (${a['retail_price']:.2f}) - {a['note']}")
        product_c = _cents(prod["retail_price"])
        warranty_c = sum(_cents(a["retail_price"]) for _, a in addons if a["type"] == "warranty")
        accessory_c = sum(_cents(a["retail_price"]) for _, a in addons if a["type"] == "accessory")
        rates = COMMISSION_RATES_BP
        com_p = _pct_of(product_c, rates["product"])
        com_w = _pct_of(warranty_c, rates["warranty"])
        com_a = _pct_of(accessory_c, rates["accessory"])
        lines += [
            "",
            "**Commission Calculator (synthetic plan rates):**",
            f"- Product: {_money(product_c)} x {rates['product'] // 100}% = {_money(com_p)}",
            f"- Warranty: {_money(warranty_c)} x {rates['warranty'] // 100}% = {_money(com_w)}",
            f"- Accessories: {_money(accessory_c)} x {rates['accessory'] // 100}% = {_money(com_a)}",
            f"- **Bundle Total:** {_money(product_c + warranty_c + accessory_c)} | **Your Commission:** {_money(com_p + com_w + com_a)}",
            "",
            f"**Tip:** {CHECKOUT_TERMS['conversion_tip']}",
            "",
            "Source: [Commission System + Sales Analytics] (synthetic)",
            "",
            "Need help with a product comparison?",
        ]
        return "\n".join(lines + _footer())

    def _product_compare(self, **kwargs):
        sid, prod = self._resolve(kwargs)
        lines = _response_header(kwargs.get("persona")) + ["# Head-to-Head Comparison", ""]
        if sid is None:
            return "\n".join(lines + [prod] + _footer())
        other_name = kwargs.get("compare_with", "") or "SoundMax Pro"
        oid = _by_name(other_name)
        if oid is None or oid == sid:
            return "\n".join(lines + [f"No second product found for compare_with: \"{other_name}\""] + _footer())
        other = PRODUCT_CATALOG[oid]
        a, b = prod, other
        better_battery = a["short_name"].split(" ")[0] if a["battery_hours"] >= b["battery_hours"] else b["short_name"].split(" ")[0]
        better_sound = b["short_name"].split(" ")[0] if b["anc_db"] >= a["anc_db"] else a["short_name"].split(" ")[0]
        sale_a = " (sale)" if a["promotion"] else ""
        sale_b = " (sale)" if b["promotion"] else ""
        lines += [
            f"Side-by-side comparison: {better_battery} has better battery, {better_sound} has superior sound quality.",
            "",
            f"| Feature | {a['short_name']} | {b['short_name']} |",
            "|---|---|---|",
            f"| Price | ${a['retail_price']:.2f}{sale_a} | ${b['retail_price']:.2f}{sale_b} |",
            f"| Battery | {a['battery_hours']} hours | {b['battery_hours']} hours |",
            f"| Sound quality | {a['sound_quality']} | {b['sound_quality']} |",
            f"| Noise cancel | -{a['anc_db']}dB | -{b['anc_db']}dB |",
            f"| Stock | {a['on_hand']} units | {b['on_hand']} units |",
            "",
            "**Best For:**",
            f"- {a['short_name'].split(' ')[0]}: {', '.join(a['best_for'])}",
            f"- {b['short_name'].split(' ')[0]}: {', '.join(b['best_for'])}",
            "",
            "**Customer Reviews:**",
            f"- {a['short_name'].split(' ')[0]}: {a['rating']}/5 ({a['review_count']} reviews) - \"{a['review_quote']}\"",
            f"- {b['short_name'].split(' ')[0]}: {b['rating']}/5 ({b['review_count']} reviews) - \"{b['review_quote']}\"",
            "",
            f"**Your Recommendation:** {a['short_name'].split(' ')[0]} if travel/commute is priority, "
            f"{b['short_name'].split(' ')[0]} if pure audio quality matters most",
            "",
            "Source: [Product Specs + Reviews Database] (synthetic)",
            "",
            "Ready to build the customer's cart?",
        ]
        return "\n".join(lines + _footer())

    def _prepare_transaction(self, **kwargs):
        terms = CHECKOUT_TERMS
        product = kwargs.get("product", "") or PRODUCT_CATALOG[HERO_SKU]["short_name"]
        sid = _by_name(product)
        if sid is None:
            return "\n".join(_response_header(kwargs.get("persona")) + [f"No products found for: \"{product}\""] + _footer())
        bundle = kwargs.get("addons", "") or "warranty and cleaning kit"
        if bundle not in ADDON_BUNDLES:
            bundle = "warranty and cleaning kit"
        cart = [sid] + ADDON_BUNDLES[bundle]
        tier = kwargs.get("loyalty_tier", "") or terms["default_loyalty_tier"]
        tier = tier.strip().title()
        if tier not in terms["loyalty_discount_bp"]:
            tier = terms["default_loyalty_tier"]
        lines = _response_header(kwargs.get("persona")) + ["# Transaction Prepared (Not Rung Up)", ""]
        subtotal = sum(_cents(PRODUCT_CATALOG[k]["retail_price"]) for k in cart)
        disc_bp = terms["loyalty_discount_bp"][tier]
        discount = _pct_of(subtotal, disc_bp)
        tax = _pct_of(subtotal - discount, terms["sales_tax_bp"])
        total = subtotal - discount + tax
        monthly = (total + terms["financing_months"] - 1) // terms["financing_months"]
        promo_savings = sum(_cents(PRODUCT_CATALOG[k]["regular_price"]) - _cents(PRODUCT_CATALOG[k]["retail_price"]) for k in cart)
        commission = sum(_pct_of(_cents(PRODUCT_CATALOG[k]["retail_price"]), COMMISSION_RATES_BP[PRODUCT_CATALOG[k]["type"]]) for k in cart)
        lines.append("Transaction prepared and additional savings found for your customer, ready for you to ring up at the register.")
        lines += ["", "**Transaction Ready:**"]
        for k in cart:
            lines.append(f"- {PRODUCT_CATALOG[k]['name'].replace(' Wireless Headphones', ' Headphones')}: ${PRODUCT_CATALOG[k]['retail_price']:.2f}")
        lines += [
            "",
            "| Line | Amount |",
            "|---|---|",
            f"| Subtotal | {_money(subtotal)} |",
            f"| Loyalty Discount ({tier} Member) | -{_money(discount)} ({disc_bp // 100}% off) |",
            f"| Sales Tax ({terms['sales_tax_bp'] / 100:g}%) | {_money(tax)} |",
            f"| **Total** | **{_money(total)}** |",
            "",
            "**Payment Options Available:**",
            f"- {terms['financing_apr']} financing ({terms['financing_months']} months, {_money(monthly)}/month)",
            f"- Store credit card (earn {terms['store_card_bonus_points']} bonus points)",
            "- Standard payment methods",
            "",
            f"**Your Commission:** {_money(commission)} on this sale",
            f"**Customer Savings:** They saved {_money(promo_savings + discount)} (sale + loyalty discount)",
            "",
            "Source: [POS System + Loyalty Program] (synthetic)",
            "",
            "Apply the loyalty discount and proceed to checkout? The sale, discount and payment are completed by you at the register.",
        ]
        return "\n".join(lines + _footer())

    def _customer_assist(self, **kwargs):
        scenario = kwargs.get("scenario", "")
        if scenario and scenario not in CUSTOMER_INTERACTION_SCRIPTS:
            return (
                f"Unknown scenario `{scenario}`. Valid: "
                f"{', '.join(CUSTOMER_INTERACTION_SCRIPTS)}"
            )
        if scenario and scenario in CUSTOMER_INTERACTION_SCRIPTS:
            scripts = {scenario: CUSTOMER_INTERACTION_SCRIPTS[scenario]}
        else:
            scripts = CUSTOMER_INTERACTION_SCRIPTS
        lines = _response_header(kwargs.get("persona")) + ["# Draft Customer Assistance Guide", ""]
        for scen_id, scr in scripts.items():
            lines.append(f"## {scen_id.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"**Scenario:** {scr['scenario']}")
            lines.append("")
            lines.append("**Suggested Draft Language:**")
            lines.append(f"> {scr['script']}")
            lines.append("")
            lines.append(f"**Follow-Up:** {scr['follow_up']}")
            lines.append("")
            lines.append("**Tips:**")
            for tip in scr["tips"]:
                lines.append(f"- {tip}")
            lines.append("")
        return "\n".join(lines + _footer())

    def _task_checklist(self, **kwargs):
        shift = kwargs.get("shift", "")
        if shift and shift not in DAILY_TASK_LIST:
            return f"Unknown shift `{shift}`. Valid: {', '.join(DAILY_TASK_LIST)}"
        if shift and shift in DAILY_TASK_LIST:
            shifts = {shift: DAILY_TASK_LIST[shift]}
        else:
            shifts = DAILY_TASK_LIST
        lines = _response_header(kwargs.get("persona")) + ["# Daily Task Planning Checklist", ""]
        for shift_name, tasks in shifts.items():
            total_minutes = sum(t["est_minutes"] for t in tasks)
            lines.append(f"## {shift_name.title()} Shift")
            lines.append(f"**Estimated Time:** {total_minutes} min | **Status:** planned (0 of {len(tasks)} tasks done)")
            lines.append("")
            lines.append("| # | Task | Priority | Est. Time |")
            lines.append("|---|------|----------|-----------|")
            for i, task in enumerate(tasks, 1):
                lines.append(f"| {i} | {task['task']} | {task['priority'].upper()} | {task['est_minutes']} min |")
            lines.append("")
        return "\n".join(lines + _footer())

    def _performance_dashboard(self, **kwargs):
        total_rev = _store_total_revenue()
        total_txn = _store_total_transactions()
        lines = _response_header(kwargs.get("persona")) + [
            "# Synthetic Role-Cohort Performance Dashboard",
            "",
            f"**Store Total Revenue Today:** ${total_rev:,.2f}",
            f"**Store Total Transactions:** {total_txn}",
            f"**Store Avg Basket:** ${total_rev / total_txn:.2f}" if total_txn > 0 else "",
            "",
            "| Associate | Role | Shift | Revenue | Units | Txns | Basket | Upsell | CSAT | Tasks |",
            "|-----------|------|-------|---------|-------|------|--------|--------|------|-------|",
        ]
        for asc_id, asc in ASSOCIATE_PERFORMANCE.items():
            task_pct = round(asc["tasks_completed"] / asc["tasks_total"] * 100) if asc["tasks_total"] > 0 else 0
            lines.append(
                f"| {asc['name']} | {asc['role']} | {asc['shift']} "
                f"| ${asc['revenue_today']:,.2f} | {asc['units_sold_today']} "
                f"| {asc['transactions_today']} | ${asc['avg_basket']:.2f} "
                f"| {asc['upsell_rate']*100:.0f}% | {asc['csat_score']}/5.0 "
                f"| {asc['tasks_completed']}/{asc['tasks_total']} ({task_pct}%) |"
            )
        lines.append("")
        lines.append("## Aggregate Coaching Signals")
        lines.append("")
        best_rev = max(ASSOCIATE_PERFORMANCE.values(), key=lambda a: a["revenue_today"])
        best_csat = max(ASSOCIATE_PERFORMANCE.values(), key=lambda a: a["csat_score"])
        best_upsell = max(ASSOCIATE_PERFORMANCE.values(), key=lambda a: a["upsell_rate"])
        lines.append(f"- **Revenue reference cohort:** {best_rev['name']} — use for workflow review, not personnel decisions")
        lines.append(f"- **Service reference cohort:** {best_csat['name']} — inspect practices, not individuals")
        lines.append(f"- **Attach-rate reference cohort:** {best_upsell['name']} — avoid pressure-based selling")
        return "\n".join(lines + _footer())

    def perform(self, **kwargs):
        if kwargs.get("data_source", "synthetic") != "synthetic":
            return "data_source must be `synthetic` for this package."
        operation = kwargs.get("operation", "product_lookup")
        dispatch = {
            "product_lookup": self._product_lookup,
            "customer_assist": self._customer_assist,
            "task_checklist": self._task_checklist,
            "performance_dashboard": self._performance_dashboard,
            "accessory_recommendations": self._accessory_recommendations,
            "product_compare": self._product_compare,
            "prepare_transaction": self._prepare_transaction,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — the demo video's four turns, then the remaining operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = StoreAssociateCopilotAgent()
    for kw in [
        {"operation": "product_lookup", "product": "TechPro X-Series"},
        {"operation": "accessory_recommendations"},
        {"operation": "product_compare", "compare_with": "SoundMax Pro"},
        {"operation": "prepare_transaction", "addons": "warranty and cleaning kit"},
        {"operation": "customer_assist", "scenario": "upsell"},
        {"operation": "task_checklist", "shift": "opening"},
        {"operation": "performance_dashboard"},
    ]:
        print("=" * 80)
        print(agent.perform(**kw))
