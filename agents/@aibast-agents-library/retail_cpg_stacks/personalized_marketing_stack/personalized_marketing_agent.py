"""
Personalized Marketing Agent — Retail & CPG Stack

Drives customer segmentation, campaign design, content personalization,
and performance analysis for targeted retail marketing programs.
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
    "name": "@aibast-agents-library/personalized-marketing",
    "version": "1.0.0",
    "display_name": "Personalized Marketing Agent",
    "description": (
        "Enables customer segmentation, personalized campaign design, "
        "dynamic content personalization, and marketing performance "
        "analysis for retail and CPG brands."
    ),
    "author": "AIBAST",
    "tags": [
        "marketing",
        "personalization",
        "segmentation",
        "campaigns",
        "retail",
    ],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic Data — Customer Segments
# ---------------------------------------------------------------------------

CUSTOMER_SEGMENTS = {
    "SEG-LOYAL": {
        "name": "Loyal Advocates",
        "size": 42850,
        "avg_age": 38,
        "gender_split": {"female": 0.56, "male": 0.42, "other": 0.02},
        "avg_annual_spend": 1875.00,
        "avg_orders_per_year": 18.3,
        "avg_basket_size": 102.46,
        "preferred_channels": ["in_store", "mobile_app"],
        "top_categories": ["Apparel", "Footwear", "Accessories"],
        "churn_risk": 0.04,
        "lifetime_value": 11250.00,
        "engagement_score": 92,
    },
    "SEG-ATRISK": {
        "name": "At-Risk Churners",
        "size": 18420,
        "avg_age": 44,
        "gender_split": {"female": 0.48, "male": 0.50, "other": 0.02},
        "avg_annual_spend": 620.00,
        "avg_orders_per_year": 5.1,
        "avg_basket_size": 121.57,
        "preferred_channels": ["email", "desktop_web"],
        "top_categories": ["Electronics", "Home"],
        "churn_risk": 0.38,
        "lifetime_value": 3720.00,
        "engagement_score": 31,
    },
    "SEG-NEW": {
        "name": "New Explorers",
        "size": 27600,
        "avg_age": 26,
        "gender_split": {"female": 0.51, "male": 0.45, "other": 0.04},
        "avg_annual_spend": 340.00,
        "avg_orders_per_year": 3.8,
        "avg_basket_size": 89.47,
        "preferred_channels": ["social_media", "mobile_app"],
        "top_categories": ["Apparel", "Beauty", "Accessories"],
        "churn_risk": 0.22,
        "lifetime_value": 2040.00,
        "engagement_score": 58,
    },
    "SEG-HIGHVAL": {
        "name": "High-Value VIPs",
        "size": 8750,
        "avg_age": 47,
        "gender_split": {"female": 0.60, "male": 0.38, "other": 0.02},
        "avg_annual_spend": 4200.00,
        "avg_orders_per_year": 24.6,
        "avg_basket_size": 170.73,
        "preferred_channels": ["in_store", "mobile_app", "email"],
        "top_categories": ["Premium Apparel", "Footwear", "Jewelry"],
        "churn_risk": 0.06,
        "lifetime_value": 33600.00,
        "engagement_score": 97,
    },
    "SEG-DORMANT": {
        "name": "Dormant Lapsed",
        "size": 34200,
        "avg_age": 41,
        "gender_split": {"female": 0.47, "male": 0.51, "other": 0.02},
        "avg_annual_spend": 85.00,
        "avg_orders_per_year": 0.8,
        "avg_basket_size": 106.25,
        "preferred_channels": ["email"],
        "top_categories": ["Home", "Electronics"],
        "churn_risk": 0.72,
        "lifetime_value": 510.00,
        "engagement_score": 9,
    },
}

CAMPAIGN_TEMPLATES = {
    "CAMP-WINBACK": {
        "name": "Win-Back Journey",
        "type": "automated_email",
        "target_segment": "SEG-DORMANT",
        "stages": 4,
        "duration_days": 28,
        "discount_offer": "20% off next purchase",
        "subject_lines": [
            "We miss you — here is 20% off",
            "Your favorites are waiting",
            "Last chance: exclusive offer inside",
            "Final reminder: your 20% expires tomorrow",
        ],
        "historical_open_rate": 0.18,
        "historical_click_rate": 0.04,
        "historical_conversion_rate": 0.012,
    },
    "CAMP-LOYALTY": {
        "name": "Loyalty Tier Upgrade",
        "type": "multi_channel",
        "target_segment": "SEG-LOYAL",
        "stages": 3,
        "duration_days": 14,
        "discount_offer": "Early access + double points",
        "subject_lines": [
            "You are almost Gold status!",
            "Earn double points this weekend",
            "Congratulations on your tier upgrade",
        ],
        "historical_open_rate": 0.42,
        "historical_click_rate": 0.15,
        "historical_conversion_rate": 0.08,
    },
    "CAMP-NEWWELCOME": {
        "name": "New Customer Welcome",
        "type": "automated_email",
        "target_segment": "SEG-NEW",
        "stages": 5,
        "duration_days": 30,
        "discount_offer": "15% off first order over $50",
        "subject_lines": [
            "Welcome! Here is 15% off your first order",
            "Discover our best sellers",
            "Complete your look — curated picks",
            "Your style profile is ready",
            "Join our rewards program today",
        ],
        "historical_open_rate": 0.35,
        "historical_click_rate": 0.11,
        "historical_conversion_rate": 0.055,
    },
    "CAMP-VIP": {
        "name": "VIP Exclusive Preview",
        "type": "multi_channel",
        "target_segment": "SEG-HIGHVAL",
        "stages": 2,
        "duration_days": 7,
        "discount_offer": "Private sale — 30% off new collection",
        "subject_lines": [
            "VIP Only: private sale starts now",
            "Your exclusive early access ends tonight",
        ],
        "historical_open_rate": 0.58,
        "historical_click_rate": 0.24,
        "historical_conversion_rate": 0.14,
    },
}

AB_TEST_RESULTS = {
    "ABT-001": {
        "campaign": "CAMP-WINBACK",
        "variant_a": {"subject": "We miss you — here is 20% off", "open_rate": 0.18, "click_rate": 0.04, "conversions": 82},
        "variant_b": {"subject": "Come back for something special", "open_rate": 0.21, "click_rate": 0.05, "conversions": 107},
        "winner": "B",
        "confidence": 0.94,
        "sample_size": 8500,
    },
    "ABT-002": {
        "campaign": "CAMP-LOYALTY",
        "variant_a": {"subject": "You are almost Gold status!", "open_rate": 0.42, "click_rate": 0.15, "conversions": 341},
        "variant_b": {"subject": "Unlock Gold rewards today", "open_rate": 0.39, "click_rate": 0.13, "conversions": 298},
        "winner": "A",
        "confidence": 0.91,
        "sample_size": 6200,
    },
    "ABT-003": {
        "campaign": "CAMP-VIP",
        "variant_a": {"subject": "VIP Only: private sale starts now", "open_rate": 0.58, "click_rate": 0.24, "conversions": 215},
        "variant_b": {"subject": "Your private collection awaits", "open_rate": 0.61, "click_rate": 0.27, "conversions": 248},
        "winner": "B",
        "confidence": 0.88,
        "sample_size": 3400,
    },
}

CONTENT_BLOCKS = {
    "hero_banner": {
        "SEG-LOYAL": {"headline": "Thank You for Being a Loyal Customer", "cta": "Shop Your Rewards"},
        "SEG-ATRISK": {"headline": "We Have Something Special for You", "cta": "Rediscover Your Favorites"},
        "SEG-NEW": {"headline": "Welcome to the Family", "cta": "Start Shopping"},
        "SEG-HIGHVAL": {"headline": "Exclusive Access Just for You", "cta": "View Private Collection"},
        "SEG-DORMANT": {"headline": "It Has Been a While — Come Back", "cta": "See What Is New"},
    },
    "product_recs": {
        "SEG-LOYAL": ["Classic Denim Jacket", "Premium Running Shoes", "Leather Crossbody Bag"],
        "SEG-ATRISK": ["Wireless Earbuds Pro", "Smart Fitness Tracker"],
        "SEG-NEW": ["Organic Cotton T-Shirt", "Stainless Water Bottle", "UV Protection Sunglasses"],
        "SEG-HIGHVAL": ["Limited Edition Blazer", "Designer Handbag", "Artisan Watch"],
        "SEG-DORMANT": ["Best Sellers Bundle", "Gift Card"],
    },
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _total_addressable_customers():
    return sum(seg["size"] for seg in CUSTOMER_SEGMENTS.values())


def _weighted_avg_ltv():
    total_size = _total_addressable_customers()
    weighted = sum(seg["size"] * seg["lifetime_value"] for seg in CUSTOMER_SEGMENTS.values())
    return round(weighted / total_size, 2) if total_size > 0 else 0


def _segment_revenue_contribution(seg_id):
    seg = CUSTOMER_SEGMENTS.get(seg_id, {})
    return round(seg.get("size", 0) * seg.get("avg_annual_spend", 0), 2)


def _campaign_projected_revenue(camp_id):
    camp = CAMPAIGN_TEMPLATES.get(camp_id, {})
    seg = CUSTOMER_SEGMENTS.get(camp.get("target_segment", ""), {})
    audience = seg.get("size", 0)
    conv_rate = camp.get("historical_conversion_rate", 0)
    basket = seg.get("avg_basket_size", 0)
    return round(audience * conv_rate * basket, 2)


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

class PersonalizedMarketingAgent(BasicAgent):
    """Agent for personalized retail marketing orchestration."""

    def __init__(self):
        self.name = "personalized-marketing-agent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "customer_segmentation",
                            "campaign_design",
                            "content_personalization",
                            "performance_analysis",
                        ],
                    },
                    "segment_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _customer_segmentation(self, **kwargs):
        lines = [
            "# Customer Segmentation Overview",
            "",
            f"**Total Addressable Customers:** {_total_addressable_customers():,}",
            f"**Weighted Average LTV:** ${_weighted_avg_ltv():,.2f}",
            "",
            "| Segment | Size | Avg Spend | Orders/Yr | LTV | Churn Risk | Engagement |",
            "|---------|------|-----------|-----------|-----|------------|------------|",
        ]
        for seg_id, seg in CUSTOMER_SEGMENTS.items():
            lines.append(
                f"| {seg['name']} | {seg['size']:,} | ${seg['avg_annual_spend']:,.2f} "
                f"| {seg['avg_orders_per_year']} | ${seg['lifetime_value']:,.2f} "
                f"| {seg['churn_risk']*100:.0f}% | {seg['engagement_score']}/100 |"
            )
        lines.append("")
        lines.append("## Revenue Contribution by Segment")
        lines.append("")
        for seg_id, seg in CUSTOMER_SEGMENTS.items():
            rev = _segment_revenue_contribution(seg_id)
            lines.append(f"- **{seg['name']}:** ${rev:,.2f}")
        return "\n".join(lines)

    def _campaign_design(self, **kwargs):
        campaign_id = kwargs.get("campaign_id")
        if campaign_id and campaign_id in CAMPAIGN_TEMPLATES:
            camps = {campaign_id: CAMPAIGN_TEMPLATES[campaign_id]}
        else:
            camps = CAMPAIGN_TEMPLATES
        lines = ["# Campaign Design Portfolio", ""]
        for cid, camp in camps.items():
            seg = CUSTOMER_SEGMENTS.get(camp["target_segment"], {})
            proj_rev = _campaign_projected_revenue(cid)
            lines.append(f"## {camp['name']} (`{cid}`)")
            lines.append("")
            lines.append(f"- **Type:** {camp['type']}")
            lines.append(f"- **Target Segment:** {seg.get('name', 'Unknown')} ({camp['target_segment']})")
            lines.append(f"- **Audience Size:** {seg.get('size', 0):,}")
            lines.append(f"- **Duration:** {camp['duration_days']} days, {camp['stages']} stages")
            lines.append(f"- **Offer:** {camp['discount_offer']}")
            lines.append(f"- **Projected Revenue:** ${proj_rev:,.2f}")
            lines.append("")
            lines.append("**Email Sequence:**")
            for i, subj in enumerate(camp["subject_lines"], 1):
                lines.append(f"  {i}. {subj}")
            lines.append("")
            lines.append(f"**Historical Benchmarks:** Open {camp['historical_open_rate']*100:.0f}% | "
                         f"Click {camp['historical_click_rate']*100:.0f}% | "
                         f"Convert {camp['historical_conversion_rate']*100:.1f}%")
            lines.append("")
        return "\n".join(lines)

    def _content_personalization(self, **kwargs):
        segment_id = kwargs.get("segment_id")
        if segment_id and segment_id in CUSTOMER_SEGMENTS:
            segs = {segment_id: CUSTOMER_SEGMENTS[segment_id]}
        else:
            segs = CUSTOMER_SEGMENTS
        lines = ["# Content Personalization Matrix", ""]
        for seg_id, seg in segs.items():
            hero = CONTENT_BLOCKS["hero_banner"].get(seg_id, {})
            recs = CONTENT_BLOCKS["product_recs"].get(seg_id, [])
            lines.append(f"## {seg['name']} (`{seg_id}`)")
            lines.append("")
            lines.append("**Hero Banner:**")
            lines.append(f"- Headline: \"{hero.get('headline', '')}\"")
            lines.append(f"- CTA: \"{hero.get('cta', '')}\"")
            lines.append("")
            lines.append("**Product Recommendations:**")
            for prod in recs:
                lines.append(f"- {prod}")
            lines.append("")
            lines.append(f"**Preferred Channels:** {', '.join(seg['preferred_channels'])}")
            lines.append(f"**Top Categories:** {', '.join(seg['top_categories'])}")
            lines.append("")
        return "\n".join(lines)

    def _performance_analysis(self, **kwargs):
        lines = [
            "# Marketing Performance Analysis",
            "",
            "## A/B Test Results",
            "",
            "| Test | Campaign | Winner | Confidence | Sample | Lift |",
            "|------|----------|--------|------------|--------|------|",
        ]
        for test_id, test in AB_TEST_RESULTS.items():
            camp_name = CAMPAIGN_TEMPLATES.get(test["campaign"], {}).get("name", test["campaign"])
            a_conv = test["variant_a"]["conversions"]
            b_conv = test["variant_b"]["conversions"]
            lift = round(((max(a_conv, b_conv) - min(a_conv, b_conv)) / min(a_conv, b_conv)) * 100, 1)
            lines.append(
                f"| {test_id} | {camp_name} | Variant {test['winner']} "
                f"| {test['confidence']*100:.0f}% | {test['sample_size']:,} | +{lift}% |"
            )
        lines.append("")
        lines.append("## Campaign ROI Summary")
        lines.append("")
        lines.append("| Campaign | Audience | Proj. Revenue | Conv. Rate | Est. ROAS |")
        lines.append("|----------|----------|---------------|------------|-----------|")
        for cid, camp in CAMPAIGN_TEMPLATES.items():
            seg = CUSTOMER_SEGMENTS.get(camp["target_segment"], {})
            rev = _campaign_projected_revenue(cid)
            cost_estimate = seg.get("size", 0) * 0.35  # $0.35 per contact
            roas = round(rev / cost_estimate, 2) if cost_estimate > 0 else 0
            lines.append(
                f"| {camp['name']} | {seg.get('size', 0):,} | ${rev:,.2f} "
                f"| {camp['historical_conversion_rate']*100:.1f}% | {roas}x |"
            )
        lines.append("")
        total_rev = sum(_campaign_projected_revenue(c) for c in CAMPAIGN_TEMPLATES)
        lines.append(f"**Total Projected Campaign Revenue:** ${total_rev:,.2f}")
        return "\n".join(lines)

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "customer_segmentation")
        dispatch = {
            "customer_segmentation": self._customer_segmentation,
            "campaign_design": self._campaign_design,
            "content_personalization": self._content_personalization,
            "performance_analysis": self._performance_analysis,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = PersonalizedMarketingAgent()
    print("=" * 80)
    print(agent.perform(operation="customer_segmentation"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="campaign_design", campaign_id="CAMP-VIP"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="content_personalization", segment_id="SEG-LOYAL"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="performance_analysis"))
    print("=" * 80)
