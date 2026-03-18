"""
Personalized Shopping Assistant Agent — B2C Sales Stack

Delivers product recommendations, style profiles, inventory checks,
and outfit building for personalized retail experiences.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/personalized-shopping-assistant",
    "version": "1.0.0",
    "display_name": "Personalized Shopping Assistant Agent",
    "description": "Personalized retail shopping with product recommendations, style profiling, inventory checks, and outfit building.",
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
    "SKU-1001": {"name": "Classic Oxford Shirt — White", "category": "tops", "subcategory": "shirts", "price": 68.00, "brand": "Heritage Co.", "sizes": ["S", "M", "L", "XL"], "colors": ["white", "blue", "pink"], "style_tags": ["classic", "business", "smart_casual"], "rating": 4.7, "stock": {"S": 12, "M": 25, "L": 18, "XL": 8}},
    "SKU-1002": {"name": "Slim Fit Chinos — Navy", "category": "bottoms", "subcategory": "pants", "price": 79.00, "brand": "Heritage Co.", "sizes": ["30", "32", "34", "36"], "colors": ["navy", "khaki", "olive"], "style_tags": ["classic", "smart_casual", "weekend"], "rating": 4.5, "stock": {"30": 6, "32": 15, "34": 20, "36": 10}},
    "SKU-1003": {"name": "Merino Wool Crew Sweater", "category": "tops", "subcategory": "sweaters", "price": 125.00, "brand": "Alpine Knits", "sizes": ["S", "M", "L", "XL"], "colors": ["charcoal", "burgundy", "forest"], "style_tags": ["classic", "smart_casual", "layering"], "rating": 4.8, "stock": {"S": 4, "M": 10, "L": 8, "XL": 3}},
    "SKU-1004": {"name": "Leather Chelsea Boots", "category": "footwear", "subcategory": "boots", "price": 195.00, "brand": "Cobblestone", "sizes": ["8", "9", "10", "11", "12"], "colors": ["brown", "black"], "style_tags": ["classic", "smart_casual", "evening"], "rating": 4.6, "stock": {"8": 5, "9": 8, "10": 12, "11": 7, "12": 3}},
    "SKU-1005": {"name": "Quilted Vest", "category": "outerwear", "subcategory": "vests", "price": 110.00, "brand": "Northfield", "sizes": ["S", "M", "L", "XL"], "colors": ["navy", "olive", "black"], "style_tags": ["casual", "outdoor", "layering"], "rating": 4.4, "stock": {"S": 2, "M": 7, "L": 5, "XL": 9}},
    "SKU-1006": {"name": "Silk Pocket Square", "category": "accessories", "subcategory": "pocket_squares", "price": 35.00, "brand": "Heritage Co.", "sizes": ["OS"], "colors": ["navy_paisley", "burgundy_dot", "green_stripe"], "style_tags": ["classic", "business", "evening"], "rating": 4.9, "stock": {"OS": 30}},
    "SKU-1007": {"name": "Performance Running Shoe", "category": "footwear", "subcategory": "athletic", "price": 145.00, "brand": "Stride Labs", "sizes": ["8", "9", "10", "11", "12"], "colors": ["white_grey", "black_red"], "style_tags": ["athletic", "casual", "performance"], "rating": 4.7, "stock": {"8": 10, "9": 15, "10": 20, "11": 12, "12": 6}},
    "SKU-1008": {"name": "Linen Blazer — Unstructured", "category": "outerwear", "subcategory": "blazers", "price": 225.00, "brand": "Riviera Style", "sizes": ["S", "M", "L", "XL"], "colors": ["tan", "light_blue"], "style_tags": ["smart_casual", "evening", "summer"], "rating": 4.3, "stock": {"S": 3, "M": 6, "L": 4, "XL": 2}},
}

CUSTOMER_PREFERENCES = {
    "SHOP-001": {
        "name": "Daniel Reeves",
        "size_top": "L",
        "size_bottom": "34",
        "size_shoe": "10",
        "style_preference": ["classic", "smart_casual"],
        "brand_affinity": ["Heritage Co.", "Alpine Knits"],
        "color_preference": ["navy", "charcoal", "white"],
        "budget_range": {"min": 50, "max": 250},
        "purchase_history": ["SKU-1001", "SKU-1002", "SKU-1006"],
    },
    "SHOP-002": {
        "name": "Olivia Chen",
        "size_top": "S",
        "size_bottom": "30",
        "size_shoe": "8",
        "style_preference": ["casual", "outdoor", "athletic"],
        "brand_affinity": ["Northfield", "Stride Labs"],
        "color_preference": ["olive", "black", "white_grey"],
        "budget_range": {"min": 30, "max": 175},
        "purchase_history": ["SKU-1005", "SKU-1007"],
    },
}

OUTFIT_TEMPLATES = {
    "business_casual": {"name": "Business Casual", "pieces": ["tops:shirts", "bottoms:pants", "footwear:boots", "accessories:pocket_squares"]},
    "weekend_smart": {"name": "Weekend Smart", "pieces": ["tops:sweaters", "bottoms:pants", "footwear:boots"]},
    "active_weekend": {"name": "Active Weekend", "pieces": ["outerwear:vests", "footwear:athletic"]},
    "evening_out": {"name": "Evening Out", "pieces": ["outerwear:blazers", "tops:shirts", "bottoms:pants", "footwear:boots"]},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _match_score(product, preferences):
    """Calculate match score between product and customer preferences."""
    score = 0
    style_overlap = set(product["style_tags"]) & set(preferences["style_preference"])
    score += len(style_overlap) * 20
    if product["brand"] in preferences["brand_affinity"]:
        score += 25
    color_overlap = set(product["colors"]) & set(preferences["color_preference"])
    score += len(color_overlap) * 10
    if preferences["budget_range"]["min"] <= product["price"] <= preferences["budget_range"]["max"]:
        score += 15
    return min(100, score)


def _check_stock(product, size):
    """Check stock availability for a product and size."""
    return product["stock"].get(size, 0)


def _get_recommendations(customer_id, limit=5):
    """Get top product recommendations for a customer."""
    prefs = CUSTOMER_PREFERENCES.get(customer_id, {})
    if not prefs:
        return []
    scored = []
    for sku, product in PRODUCT_CATALOG.items():
        if sku in prefs.get("purchase_history", []):
            continue
        score = _match_score(product, prefs)
        scored.append((sku, product, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:limit]


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class PersonalizedShoppingAssistantAgent(BasicAgent):
    """Personalized shopping assistant agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/personalized-shopping-assistant"
        self.metadata = {
            "name": self.name,
            "display_name": "Personalized Shopping Assistant Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "product_recommendations",
                            "style_profile",
                            "inventory_check",
                            "outfit_builder",
                        ],
                    },
                    "customer_id": {"type": "string"},
                    "sku": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "product_recommendations")
        dispatch = {
            "product_recommendations": self._product_recommendations,
            "style_profile": self._style_profile,
            "inventory_check": self._inventory_check,
            "outfit_builder": self._outfit_builder,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _product_recommendations(self, **kwargs) -> str:
        customer_id = kwargs.get("customer_id", "SHOP-001")
        prefs = CUSTOMER_PREFERENCES.get(customer_id, {})
        recs = _get_recommendations(customer_id)
        lines = [f"# Product Recommendations: {prefs.get('name', 'Customer')}\n"]
        lines.append(f"**Style:** {', '.join(prefs.get('style_preference', []))}")
        lines.append(f"**Budget:** ${prefs.get('budget_range', {}).get('min', 0)} - ${prefs.get('budget_range', {}).get('max', 0)}\n")
        if recs:
            lines.append("| Rank | Product | Brand | Price | Match Score | Rating |")
            lines.append("|---|---|---|---|---|---|")
            for i, (sku, product, score) in enumerate(recs, 1):
                lines.append(
                    f"| {i} | {product['name']} ({sku}) | {product['brand']} "
                    f"| ${product['price']:,.2f} | {score}% | {product['rating']} |"
                )
        else:
            lines.append("No recommendations available.")
        return "\n".join(lines)

    def _style_profile(self, **kwargs) -> str:
        customer_id = kwargs.get("customer_id", "SHOP-001")
        prefs = CUSTOMER_PREFERENCES.get(customer_id, {})
        lines = [f"# Style Profile: {prefs.get('name', 'Unknown')}\n"]
        lines.append(f"## Sizing\n")
        lines.append(f"- Top: {prefs.get('size_top', 'N/A')}")
        lines.append(f"- Bottom: {prefs.get('size_bottom', 'N/A')}")
        lines.append(f"- Shoe: {prefs.get('size_shoe', 'N/A')}\n")
        lines.append("## Style Preferences\n")
        for style in prefs.get("style_preference", []):
            lines.append(f"- {style.replace('_', ' ').title()}")
        lines.append("\n## Brand Affinity\n")
        for brand in prefs.get("brand_affinity", []):
            lines.append(f"- {brand}")
        lines.append("\n## Color Preference\n")
        for color in prefs.get("color_preference", []):
            lines.append(f"- {color.replace('_', ' ').title()}")
        lines.append(f"\n## Budget Range\n")
        br = prefs.get("budget_range", {})
        lines.append(f"${br.get('min', 0)} - ${br.get('max', 0)}")
        lines.append("\n## Purchase History\n")
        for sku in prefs.get("purchase_history", []):
            product = PRODUCT_CATALOG.get(sku, {})
            lines.append(f"- {product.get('name', sku)} — ${product.get('price', 0):,.2f}")
        return "\n".join(lines)

    def _inventory_check(self, **kwargs) -> str:
        sku = kwargs.get("sku")
        if sku and sku in PRODUCT_CATALOG:
            product = PRODUCT_CATALOG[sku]
            lines = [f"# Inventory Check: {product['name']} ({sku})\n"]
            lines.append(f"- **Price:** ${product['price']:,.2f}")
            lines.append(f"- **Brand:** {product['brand']}")
            lines.append(f"- **Rating:** {product['rating']}\n")
            lines.append("## Stock by Size\n")
            lines.append("| Size | Stock | Status |")
            lines.append("|---|---|---|")
            for size, qty in product["stock"].items():
                status = "In Stock" if qty > 5 else "Low Stock" if qty > 0 else "Out of Stock"
                lines.append(f"| {size} | {qty} | {status} |")
            total = sum(product["stock"].values())
            lines.append(f"\n**Total Units:** {total}")
            return "\n".join(lines)

        lines = ["# Inventory Overview\n"]
        lines.append("| SKU | Product | Price | Total Stock | Status |")
        lines.append("|---|---|---|---|---|")
        for sku, p in PRODUCT_CATALOG.items():
            total = sum(p["stock"].values())
            status = "In Stock" if total > 10 else "Low Stock" if total > 0 else "Out of Stock"
            lines.append(f"| {sku} | {p['name']} | ${p['price']:,.2f} | {total} | {status} |")
        return "\n".join(lines)

    def _outfit_builder(self, **kwargs) -> str:
        customer_id = kwargs.get("customer_id", "SHOP-001")
        prefs = CUSTOMER_PREFERENCES.get(customer_id, {})
        lines = [f"# Outfit Builder: {prefs.get('name', 'Customer')}\n"]
        for template_id, template in OUTFIT_TEMPLATES.items():
            lines.append(f"## {template['name']}\n")
            total_price = 0
            for piece_spec in template["pieces"]:
                cat, subcat = piece_spec.split(":")
                matches = [(sku, p) for sku, p in PRODUCT_CATALOG.items() if p["category"] == cat and p["subcategory"] == subcat]
                if matches:
                    best = max(matches, key=lambda x: _match_score(x[1], prefs) if prefs else x[1]["rating"])
                    sku, product = best
                    total_price += product["price"]
                    lines.append(f"- **{cat.replace('_', ' ').title()}:** {product['name']} — ${product['price']:,.2f}")
                else:
                    lines.append(f"- **{cat.replace('_', ' ').title()}:** No matching item found")
            lines.append(f"\n**Outfit Total:** ${total_price:,.2f}\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = PersonalizedShoppingAssistantAgent()
    print(agent.perform(operation="product_recommendations", customer_id="SHOP-001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="style_profile", customer_id="SHOP-002"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="inventory_check", sku="SKU-1003"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="outfit_builder", customer_id="SHOP-001"))
