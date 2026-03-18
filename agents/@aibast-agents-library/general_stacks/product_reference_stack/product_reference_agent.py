"""
Product Reference Agent

Product catalog lookup with feature comparison, pricing information,
and compatibility checking across the product portfolio.

Where a real deployment would connect to PIM and pricing systems, this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/product-reference",
    "version": "1.0.0",
    "display_name": "Product Reference",
    "description": "Product catalog with feature comparison, pricing tiers, and compatibility checking.",
    "author": "AIBAST",
    "tags": ["product", "catalog", "pricing", "features", "compatibility"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_PRODUCTS = {
    "CORE": {"id": "CORE", "name": "Core Platform", "category": "Platform", "description": "Essential CRM and workflow automation for growing teams", "features": ["Contact Management", "Deal Pipeline", "Task Automation", "Basic Reporting", "Email Integration", "Mobile App"], "max_users": 100, "storage_gb": 50, "api_calls_monthly": 10000, "support_level": "Standard"},
    "ENT": {"id": "ENT", "name": "Enterprise Platform", "category": "Platform", "description": "Full-featured platform with advanced analytics and enterprise controls", "features": ["Everything in Core", "Advanced Analytics", "Custom Dashboards", "Role-Based Access", "Audit Logging", "SSO/SAML", "API Unlimited", "Custom Objects", "Workflow Builder"], "max_users": 10000, "storage_gb": 500, "api_calls_monthly": -1, "support_level": "Premium"},
    "ANLYT-STD": {"id": "ANLYT-STD", "name": "Analytics Standard", "category": "Analytics", "description": "Business intelligence and reporting for data-driven decisions", "features": ["Pre-built Reports", "Dashboard Builder", "Data Export (CSV/PDF)", "Scheduled Reports", "Basic Visualizations"], "max_users": 50, "storage_gb": 25, "api_calls_monthly": 5000, "support_level": "Standard"},
    "ANLYT-PRO": {"id": "ANLYT-PRO", "name": "Analytics Pro", "category": "Analytics", "description": "Advanced analytics with predictive insights and custom models", "features": ["Everything in Standard", "Predictive Analytics", "Custom Models", "Data Warehouse Connect", "Real-time Dashboards", "Embedded Analytics", "AI-Powered Insights"], "max_users": 500, "storage_gb": 200, "api_calls_monthly": 50000, "support_level": "Premium"},
    "INTGR": {"id": "INTGR", "name": "Integration Hub", "category": "Integration", "description": "Connect your tech stack with pre-built and custom integrations", "features": ["200+ Pre-built Connectors", "Custom API Builder", "Webhook Support", "Data Sync Engine", "Transformation Rules", "Error Handling & Retry"], "max_users": -1, "storage_gb": 100, "api_calls_monthly": 100000, "support_level": "Standard"},
    "SECUR": {"id": "SECUR", "name": "Security Suite", "category": "Security", "description": "Enterprise-grade security, compliance, and data protection", "features": ["Data Encryption (AES-256)", "IP Allowlisting", "MFA Enforcement", "DLP Policies", "Compliance Reports (SOC2, HIPAA)", "Threat Detection", "Backup & Recovery"], "max_users": -1, "storage_gb": 50, "api_calls_monthly": -1, "support_level": "Premium"},
}

_PRICING_TIERS = {
    "CORE": {"monthly_per_user": 29, "annual_per_user": 24, "annual_savings_pct": 17},
    "ENT": {"monthly_per_user": 79, "annual_per_user": 65, "annual_savings_pct": 18},
    "ANLYT-STD": {"monthly_per_user": 19, "annual_per_user": 15, "annual_savings_pct": 21},
    "ANLYT-PRO": {"monthly_per_user": 49, "annual_per_user": 40, "annual_savings_pct": 18},
    "INTGR": {"monthly_flat": 1500, "annual_flat": 15000, "annual_savings_pct": 17},
    "SECUR": {"monthly_flat": 1250, "annual_flat": 12500, "annual_savings_pct": 17},
}

_COMPATIBILITY_MATRIX = {
    "CORE": {"requires": [], "recommended": ["ANLYT-STD", "INTGR"], "incompatible": []},
    "ENT": {"requires": [], "recommended": ["ANLYT-PRO", "INTGR", "SECUR"], "incompatible": []},
    "ANLYT-STD": {"requires": ["CORE"], "recommended": ["INTGR"], "incompatible": ["ANLYT-PRO"]},
    "ANLYT-PRO": {"requires": ["ENT"], "recommended": ["INTGR", "SECUR"], "incompatible": ["ANLYT-STD"]},
    "INTGR": {"requires": ["CORE"], "recommended": ["SECUR"], "incompatible": []},
    "SECUR": {"requires": ["ENT"], "recommended": ["INTGR"], "incompatible": []},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_product(query):
    if not query:
        return "CORE"
    q = query.upper().strip()
    if q in _PRODUCTS:
        return q
    for pid, prod in _PRODUCTS.items():
        if q in prod["name"].upper():
            return pid
    return "CORE"


def _calculate_bundle_price(product_ids, num_users=100, billing="annual"):
    total = 0
    for pid in product_ids:
        pricing = _PRICING_TIERS.get(pid, {})
        if billing == "annual":
            if "annual_per_user" in pricing:
                total += pricing["annual_per_user"] * num_users * 12
            elif "annual_flat" in pricing:
                total += pricing["annual_flat"]
        else:
            if "monthly_per_user" in pricing:
                total += pricing["monthly_per_user"] * num_users * 12
            elif "monthly_flat" in pricing:
                total += pricing["monthly_flat"] * 12
    return total


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ProductReferenceAgent(BasicAgent):
    """
    Product reference and catalog agent.

    Operations:
        product_lookup       - look up product details
        feature_comparison   - compare features across products
        pricing_info         - view pricing tiers and calculate costs
        compatibility_check  - check product compatibility and dependencies
    """

    def __init__(self):
        self.name = "ProductReferenceAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "product_lookup", "feature_comparison",
                            "pricing_info", "compatibility_check",
                        ],
                        "description": "The product reference operation to perform",
                    },
                    "product_id": {
                        "type": "string",
                        "description": "Product ID (e.g. 'CORE', 'ENT')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "product_lookup")
        dispatch = {
            "product_lookup": self._product_lookup,
            "feature_comparison": self._feature_comparison,
            "pricing_info": self._pricing_info,
            "compatibility_check": self._compatibility_check,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── product_lookup ─────────────────────────────────────────
    def _product_lookup(self, params):
        pid = _resolve_product(params.get("product_id", ""))
        prod = _PRODUCTS[pid]
        features = "\n".join(f"- {f}" for f in prod["features"])
        users = f"{prod['max_users']:,}" if prod["max_users"] > 0 else "Unlimited"
        api = f"{prod['api_calls_monthly']:,}" if prod["api_calls_monthly"] > 0 else "Unlimited"
        pricing = _PRICING_TIERS.get(pid, {})
        if "monthly_per_user" in pricing:
            price_line = f"${pricing['monthly_per_user']}/user/month (${pricing['annual_per_user']}/user/month annual)"
        else:
            price_line = f"${pricing.get('monthly_flat', 0):,}/month (${pricing.get('annual_flat', 0):,}/year)"
        return (
            f"**Product: {prod['name']}** ({prod['id']})\n\n"
            f"**Category:** {prod['category']} | **Support:** {prod['support_level']}\n\n"
            f"**Description:** {prod['description']}\n\n"
            f"| Spec | Value |\n|---|---|\n"
            f"| Max Users | {users} |\n"
            f"| Storage | {prod['storage_gb']} GB |\n"
            f"| API Calls | {api}/month |\n"
            f"| Pricing | {price_line} |\n\n"
            f"**Features:**\n{features}\n\n"
            f"Source: [Product Catalog]\nAgents: ProductReferenceAgent"
        )

    # ── feature_comparison ─────────────────────────────────────
    def _feature_comparison(self, params):
        categories = {}
        for pid, prod in _PRODUCTS.items():
            categories.setdefault(prod["category"], []).append(prod)
        comparison = ""
        for cat, products in categories.items():
            if len(products) < 2:
                continue
            comparison += f"**{cat}:**\n\n"
            all_features = set()
            for p in products:
                all_features.update(f for f in p["features"] if not f.startswith("Everything"))
            header = "| Feature | " + " | ".join(p["name"] for p in products) + " |\n"
            sep = "|---|" + "|".join(["---"] * len(products)) + "|\n"
            rows = ""
            for feat in sorted(all_features):
                cells = []
                for p in products:
                    cells.append("Yes" if feat in p["features"] else "No")
                rows += f"| {feat} | " + " | ".join(cells) + " |\n"
            comparison += header + sep + rows + "\n"
        return (
            f"**Feature Comparison**\n\n"
            f"{comparison}"
            f"Source: [Product Catalog]\nAgents: ProductReferenceAgent"
        )

    # ── pricing_info ───────────────────────────────────────────
    def _pricing_info(self, params):
        rows = ""
        for pid, pricing in _PRICING_TIERS.items():
            name = _PRODUCTS[pid]["name"]
            if "monthly_per_user" in pricing:
                monthly = f"${pricing['monthly_per_user']}/user"
                annual = f"${pricing['annual_per_user']}/user"
            else:
                monthly = f"${pricing.get('monthly_flat', 0):,} flat"
                annual = f"${pricing.get('annual_flat', 0):,} flat"
            rows += f"| {name} | {monthly} | {annual} | {pricing.get('annual_savings_pct', 0)}% |\n"
        example_100 = _calculate_bundle_price(["ENT", "ANLYT-PRO", "INTGR", "SECUR"], 100, "annual")
        example_500 = _calculate_bundle_price(["ENT", "ANLYT-PRO", "INTGR", "SECUR"], 500, "annual")
        return (
            f"**Pricing Information**\n\n"
            f"| Product | Monthly | Annual | Savings |\n|---|---|---|---|\n"
            f"{rows}\n"
            f"**Bundle Examples (Annual Billing):**\n"
            f"- Enterprise Full Suite (100 users): ${example_100:,}/year\n"
            f"- Enterprise Full Suite (500 users): ${example_500:,}/year\n\n"
            f"**Notes:**\n"
            f"- Volume discounts available for 50+ users\n"
            f"- Multi-year commitments receive additional 10-20% discount\n"
            f"- Non-profit and education pricing available\n\n"
            f"Source: [Pricing Engine]\nAgents: ProductReferenceAgent"
        )

    # ── compatibility_check ────────────────────────────────────
    def _compatibility_check(self, params):
        pid = _resolve_product(params.get("product_id", ""))
        compat = _COMPATIBILITY_MATRIX.get(pid, {})
        prod = _PRODUCTS[pid]
        requires = ", ".join(_PRODUCTS[r]["name"] for r in compat.get("requires", [])) or "None (standalone)"
        recommended = ", ".join(_PRODUCTS[r]["name"] for r in compat.get("recommended", [])) or "None"
        incompatible = ", ".join(_PRODUCTS[r]["name"] for r in compat.get("incompatible", [])) or "None"
        matrix_rows = ""
        for p_id, c in _COMPATIBILITY_MATRIX.items():
            reqs = ", ".join(c["requires"]) or "-"
            recs = ", ".join(c["recommended"]) or "-"
            incompat = ", ".join(c["incompatible"]) or "-"
            matrix_rows += f"| {_PRODUCTS[p_id]['name']} | {reqs} | {recs} | {incompat} |\n"
        return (
            f"**Compatibility Check: {prod['name']}**\n\n"
            f"| Relationship | Products |\n|---|---|\n"
            f"| Requires | {requires} |\n"
            f"| Recommended With | {recommended} |\n"
            f"| Incompatible With | {incompatible} |\n\n"
            f"**Full Compatibility Matrix:**\n\n"
            f"| Product | Requires | Recommended | Incompatible |\n|---|---|---|---|\n"
            f"{matrix_rows}\n\n"
            f"Source: [Product Catalog + Compatibility Engine]\nAgents: ProductReferenceAgent"
        )


if __name__ == "__main__":
    agent = ProductReferenceAgent()
    for op in ["product_lookup", "feature_comparison", "pricing_info", "compatibility_check"]:
        print("=" * 60)
        print(agent.perform(operation=op, product_id="ENT"))
        print()
