"""
Inventory Visibility Agent — Retail & CPG Stack

Provides real-time inventory visibility across stores, warehouses, in-transit
stock and the e-commerce reserve for a regional retailer. Detects critical
stockouts, locates the nearest available inventory, drafts phased transfer
plans, scores system-wide inventory health, and prepares automation and
investment proposals for authorized review.

Demo scenario (synthetic): a Pacific Northwest retailer with 51 locations.
The hero item, the Alpine Pro Winter Jacket, is sold out in Portland while the
Seattle stores hold excess stock.
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
    "name": "@aibast-agents-library/inventory-visibility",
    "version": "1.1.0",
    "display_name": "Inventory Visibility Agent",
    "description": (
        "Provide synthetic cross-channel inventory visibility and draft replenishment, transfer, and allocation recommendations for authorized review."
    ),
    "author": "AIBAST",
    "tags": [
        "inventory",
        "stock-management",
        "replenishment",
        "omni-channel",
        "retail",
    ],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic Data — Stores & Warehouses (detailed locations of a 51-location network)
# ---------------------------------------------------------------------------

STORES = {
    "STR-001": {"name": "Seattle Flagship", "city": "Seattle", "state": "WA", "region": "Seattle", "type": "flagship", "capacity_sqft": 42000},
    "STR-002": {"name": "Bellevue Store", "city": "Bellevue", "state": "WA", "region": "Seattle", "type": "suburban", "capacity_sqft": 18500},
    "STR-003": {"name": "Northgate Store", "city": "Seattle", "state": "WA", "region": "Seattle", "type": "suburban", "capacity_sqft": 12000},
    "STR-004": {"name": "Renton Store", "city": "Renton", "state": "WA", "region": "Seattle", "type": "suburban", "capacity_sqft": 9500},
    "STR-005": {"name": "Portland Flagship", "city": "Portland", "state": "OR", "region": "Portland", "type": "flagship", "capacity_sqft": 38000},
    "STR-006": {"name": "Portland Mall", "city": "Portland", "state": "OR", "region": "Portland", "type": "mall", "capacity_sqft": 16000},
}

WAREHOUSES = {
    "WH-CENTRAL": {"name": "Central Distribution Center", "city": "Kent", "state": "WA", "capacity_pallets": 22000},
    "WH-EAST": {"name": "East Regional Warehouse", "city": "Spokane", "state": "WA", "capacity_pallets": 14000},
    "WH-SOUTH": {"name": "South Regional Warehouse", "city": "Salem", "state": "OR", "capacity_pallets": 12000},
}

SKUS = {
    "SKU-2001": {"name": "Alpine Pro Winter Jacket", "category": "Outerwear", "unit_cost": 78.00, "retail_price": 170.00, "aliases": ["winter jacket", "alpine", "jacket"]},
    "SKU-1001": {"name": "Classic Denim Jacket", "category": "Apparel", "unit_cost": 34.50, "retail_price": 89.99, "aliases": ["denim"]},
    "SKU-1002": {"name": "Wireless Earbuds Pro", "category": "Electronics", "unit_cost": 18.75, "retail_price": 59.99, "aliases": ["earbuds"]},
    "SKU-1003": {"name": "Organic Cotton T-Shirt", "category": "Apparel", "unit_cost": 8.20, "retail_price": 29.99, "aliases": ["t-shirt", "tee"]},
    "SKU-1004": {"name": "Smart Fitness Tracker", "category": "Electronics", "unit_cost": 42.00, "retail_price": 129.99, "aliases": ["fitness tracker"]},
    "SKU-1005": {"name": "Premium Running Shoes", "category": "Footwear", "unit_cost": 55.00, "retail_price": 149.99, "aliases": ["running shoes", "shoes"]},
    "SKU-1006": {"name": "Stainless Water Bottle", "category": "Accessories", "unit_cost": 6.80, "retail_price": 24.99, "aliases": ["water bottle"]},
    "SKU-1007": {"name": "Leather Crossbody Bag", "category": "Accessories", "unit_cost": 27.50, "retail_price": 79.99, "aliases": ["crossbody", "bag"]},
    "SKU-1008": {"name": "UV Protection Sunglasses", "category": "Accessories", "unit_cost": 12.30, "retail_price": 44.99, "aliases": ["sunglasses"]},
}

# Current on-hand quantities per detailed location per SKU
INVENTORY = {
    "STR-001": {"SKU-2001": 97, "SKU-1001": 74, "SKU-1002": 132, "SKU-1003": 210, "SKU-1004": 45, "SKU-1005": 38, "SKU-1006": 195, "SKU-1007": 61, "SKU-1008": 88},
    "STR-002": {"SKU-2001": 52, "SKU-1001": 35, "SKU-1002": 67, "SKU-1003": 98, "SKU-1004": 22, "SKU-1005": 14, "SKU-1006": 110, "SKU-1007": 29, "SKU-1008": 53},
    "STR-003": {"SKU-2001": 50, "SKU-1001": 18, "SKU-1002": 41, "SKU-1003": 65, "SKU-1004": 9, "SKU-1005": 7, "SKU-1006": 72, "SKU-1007": 15, "SKU-1008": 30},
    "STR-004": {"SKU-2001": 48, "SKU-1001": 12, "SKU-1002": 28, "SKU-1003": 44, "SKU-1004": 6, "SKU-1005": 5, "SKU-1006": 55, "SKU-1007": 8, "SKU-1008": 19},
    "STR-005": {"SKU-2001": 0, "SKU-1001": 74, "SKU-1002": 132, "SKU-1003": 210, "SKU-1004": 45, "SKU-1005": 38, "SKU-1006": 195, "SKU-1007": 61, "SKU-1008": 88},
    "STR-006": {"SKU-2001": 3, "SKU-1001": 35, "SKU-1002": 67, "SKU-1003": 98, "SKU-1004": 22, "SKU-1005": 14, "SKU-1006": 110, "SKU-1007": 29, "SKU-1008": 53},
    "WH-CENTRAL": {"SKU-2001": 420, "SKU-1001": 1450, "SKU-1002": 2300, "SKU-1003": 3800, "SKU-1004": 780, "SKU-1005": 620, "SKU-1006": 4100, "SKU-1007": 950, "SKU-1008": 1700},
    "WH-EAST": {"SKU-2001": 310, "SKU-1001": 820, "SKU-1002": 1100, "SKU-1003": 2200, "SKU-1004": 410, "SKU-1005": 350, "SKU-1006": 2600, "SKU-1007": 530, "SKU-1008": 900},
    "WH-SOUTH": {"SKU-2001": 210, "SKU-1001": 560, "SKU-1002": 740, "SKU-1003": 1500, "SKU-1004": 280, "SKU-1005": 240, "SKU-1006": 1700, "SKU-1007": 360, "SKU-1008": 610},
}

SAFETY_STOCK = {
    "STR-001": {"SKU-2001": 12, "SKU-1001": 30, "SKU-1002": 50, "SKU-1003": 80, "SKU-1004": 20, "SKU-1005": 15, "SKU-1006": 70, "SKU-1007": 25, "SKU-1008": 35},
    "STR-002": {"SKU-2001": 6, "SKU-1001": 15, "SKU-1002": 30, "SKU-1003": 45, "SKU-1004": 10, "SKU-1005": 8, "SKU-1006": 40, "SKU-1007": 12, "SKU-1008": 20},
    "STR-003": {"SKU-2001": 6, "SKU-1001": 10, "SKU-1002": 20, "SKU-1003": 30, "SKU-1004": 5, "SKU-1005": 5, "SKU-1006": 25, "SKU-1007": 8, "SKU-1008": 12},
    "STR-004": {"SKU-2001": 6, "SKU-1001": 8, "SKU-1002": 15, "SKU-1003": 20, "SKU-1004": 4, "SKU-1005": 3, "SKU-1006": 20, "SKU-1007": 5, "SKU-1008": 10},
    "STR-005": {"SKU-2001": 24, "SKU-1001": 30, "SKU-1002": 50, "SKU-1003": 80, "SKU-1004": 20, "SKU-1005": 15, "SKU-1006": 70, "SKU-1007": 25, "SKU-1008": 35},
    "STR-006": {"SKU-2001": 24, "SKU-1001": 15, "SKU-1002": 30, "SKU-1003": 45, "SKU-1004": 10, "SKU-1005": 8, "SKU-1006": 40, "SKU-1007": 12, "SKU-1008": 20},
}

LEAD_TIMES_DAYS = {
    "WH-CENTRAL": {"STR-001": 1, "STR-002": 1, "STR-003": 1, "STR-004": 1, "STR-005": 2, "STR-006": 2},
    "WH-EAST": {"STR-001": 2, "STR-002": 2, "STR-003": 2, "STR-004": 2, "STR-005": 3, "STR-006": 3},
    "WH-SOUTH": {"STR-001": 2, "STR-002": 2, "STR-003": 2, "STR-004": 2, "STR-005": 1, "STR-006": 1},
}

CHANNEL_DEMAND = {
    "in_store": {"weight": 0.45, "daily_units_avg": 320},
    "online_ship": {"weight": 0.30, "daily_units_avg": 215},
    "bopis": {"weight": 0.15, "daily_units_avg": 108},
    "marketplace": {"weight": 0.10, "daily_units_avg": 72},
}

# Units sold per day at each detailed store (per-location rates, not network totals)
DAILY_SELL_THROUGH = {
    "STR-001": {"SKU-2001": 1.6, "SKU-1001": 6.0, "SKU-1002": 10.0, "SKU-1003": 16.0, "SKU-1004": 4.0, "SKU-1005": 3.0, "SKU-1006": 14.0, "SKU-1007": 5.0, "SKU-1008": 7.0},
    "STR-002": {"SKU-2001": 0.8, "SKU-1001": 3.0, "SKU-1002": 6.0, "SKU-1003": 9.0, "SKU-1004": 2.0, "SKU-1005": 1.6, "SKU-1006": 8.0, "SKU-1007": 2.4, "SKU-1008": 4.0},
    "STR-003": {"SKU-2001": 0.8, "SKU-1001": 2.0, "SKU-1002": 4.0, "SKU-1003": 6.0, "SKU-1004": 1.0, "SKU-1005": 1.0, "SKU-1006": 5.0, "SKU-1007": 1.6, "SKU-1008": 2.4},
    "STR-004": {"SKU-2001": 0.8, "SKU-1001": 1.6, "SKU-1002": 3.0, "SKU-1003": 4.0, "SKU-1004": 0.8, "SKU-1005": 0.6, "SKU-1006": 4.0, "SKU-1007": 1.0, "SKU-1008": 2.0},
    "STR-005": {"SKU-2001": 8.0, "SKU-1001": 6.0, "SKU-1002": 10.0, "SKU-1003": 16.0, "SKU-1004": 4.0, "SKU-1005": 3.0, "SKU-1006": 14.0, "SKU-1007": 5.0, "SKU-1008": 7.0},
    "STR-006": {"SKU-2001": 8.0, "SKU-1001": 3.0, "SKU-1002": 6.0, "SKU-1003": 9.0, "SKU-1004": 2.0, "SKU-1005": 1.6, "SKU-1006": 8.0, "SKU-1007": 2.4, "SKU-1008": 4.0},
}

# Network rollup for the hero item beyond the six detailed stores and three warehouses
NETWORK_ROLLUP = {
    "SKU-2001": {
        "other_stores": {"count": 41, "units": 1597},
        "in_transit": 285,
        "ecomm_reserve": 128,
        "ecomm_reserve_target": 200,
        "sold_out_days": {"STR-005": 3},
    },
}

# Nearest store holding excess stock for a stocked-out store, with road distance
NEAREST_SOURCE = {
    "STR-005": {"source": "STR-001", "miles": 174},
    "STR-006": {"source": "STR-001", "miles": 176},
}

# Phased Seattle -> Portland reallocation for the hero item
TRANSFER_PHASES = [
    {
        "phase": "Phase 1: Emergency (Next 12 Hours)",
        "moves": [{"from": "STR-001", "to": "STR-005", "units": 40}],
        "transport": "Overnight van",
        "cost": 340,
        "pickup": "6 PM tonight",
        "arrival": "Tomorrow 7 AM",
        "recovery": 6800,
        "window": "3-day window",
    },
    {
        "phase": "Phase 2: Strategic (24-48 Hours)",
        "moves": [
            {"from": "STR-002", "to": "STR-006", "units": 27},
            {"from": "STR-003", "to": "STR-006", "units": 27},
            {"from": "STR-004", "to": "STR-005", "units": 26},
        ],
        "transport": "Regular delivery truck",
        "cost": 180,
        "pickup": "Tomorrow morning route",
        "arrival": "Day after tomorrow",
        "recovery": 11600,
        "window": "week-long window",
    },
]

# System-wide health metrics across all 51 locations
NETWORK_HEALTH = {
    "locations": 51,
    "stock_balance_score": 72,
    "days_of_supply": 43,
    "stockout_incidents_per_month": 147,
    "overstock_by_category": {"Outerwear": 920000, "Apparel": 740000, "Electronics": 610000, "Footwear": 330000, "Accessories": 200000},
    "slow_movers": [
        {"sku": "SKU-1006", "weeks_of_supply": 19, "note": "summer item carried into winter"},
        {"sku": "SKU-1008", "weeks_of_supply": 17, "note": "seasonal demand down 40% since September"},
        {"sku": "SKU-1003", "weeks_of_supply": 14, "note": "base tee overbought for fall"},
    ],
    "seasonal_pattern": "Outerwear demand runs 2.1x the annual average from November to January; summer accessories run 0.4x.",
}

# The 8 additional SKUs with the same store-to-store imbalance pattern
IMBALANCES = [
    {"sku": "SKU-1001", "route": "Spokane -> Seattle", "units": 95, "routes": 2, "recovery": 11400, "transport": 460},
    {"sku": "SKU-1002", "route": "Seattle -> Portland", "units": 120, "routes": 2, "recovery": 14600, "transport": 520},
    {"sku": "SKU-1003", "route": "Portland -> Tacoma", "units": 140, "routes": 2, "recovery": 6300, "transport": 380},
    {"sku": "SKU-1004", "route": "Seattle -> Eugene", "units": 60, "routes": 2, "recovery": 13900, "transport": 410},
    {"sku": "SKU-1005", "route": "Bellevue -> Portland", "units": 55, "routes": 2, "recovery": 12500, "transport": 400},
    {"sku": "SKU-1006", "route": "Salem -> Seattle", "units": 90, "routes": 2, "recovery": 4100, "transport": 330},
    {"sku": "SKU-1007", "route": "Seattle -> Spokane", "units": 65, "routes": 2, "recovery": 10600, "transport": 450},
    {"sku": "SKU-1008", "route": "Portland -> Boise", "units": 55, "routes": 1, "recovery": 10800, "transport": 450},
]

# Warehouse automation options (investment and annual benefit in dollars)
AUTOMATION_OPTIONS = [
    {
        "priority": 1,
        "name": "RFID Tracking",
        "investment": 85000,
        "annual_benefit": 127000,
        "benefit_type": "Labor Savings",
        "benefit_label": "Annual labor savings",
        "highlights": ["Real-time location accuracy: 87% today, 99.8% with RFID", "Picking speed: +34%"],
    },
    {
        "priority": 2,
        "name": "Auto-Replenishment",
        "investment": 45000,
        "annual_benefit": 142000,
        "benefit_type": "Stockout Reduction",
        "benefit_label": "Annual savings",
        "highlights": ["Eliminate manual reorder points", "Stockouts: -62%"],
    },
    {
        "priority": 3,
        "name": "Predictive Allocation",
        "investment": 32000,
        "annual_benefit": 71000,
        "benefit_type": "Revenue Protection",
        "benefit_label": "Revenue protection",
        "highlights": ["AI-driven transfers (prevent imbalances)"],
    },
]

INVENTORY_ACCURACY = {"current_pct": 87, "target_pct": 99.8}

APPROVED_PERSONAS = {
    "Inventory Planner": "network balance, replenishment scenarios, and planning assumptions",
    "Store Manager": "store-level exceptions and practical review priorities",
    "Category Manager": "category health, availability patterns, and tradeoffs",
}

SAFETY_NOTICE = (
    "> Synthetic inventory snapshot. Read-only recommendations only; no stock is "
    "reserved, transferred, replenished, allocated, promised, or purchased. "
    "Verify all quantities in the system of record before action."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Inventory Planner"
    return [
        f"**Prepared for:** {role}",
        f"**Role focus:** {APPROVED_PERSONAS[role]}",
        "",
        SAFETY_NOTICE,
        "",
    ]


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _resolve_sku(query):
    """SKU id, product name or a simple alias ('winter jackets'); None when nothing matches."""
    if not query:
        return "SKU-2001"
    q = str(query).lower().strip()
    for sku_id, sku in SKUS.items():
        if q == sku_id.lower() or q in sku["name"].lower():
            return sku_id
        for alias in sku["aliases"]:
            if alias in q:
                return sku_id
    return None


def _resolve_location(query):
    """Location id or store/warehouse name; None when nothing matches."""
    q = str(query).lower().strip()
    for loc_id in INVENTORY:
        info = STORES.get(loc_id) or WAREHOUSES.get(loc_id)
        if q == loc_id.lower() or q in info["name"].lower():
            return loc_id
    return None


def _money(value):
    return f"${value:,.0f}"


def _total_network_inventory(sku_id):
    """Sum on-hand across all detailed locations for a given SKU."""
    return sum(loc.get(sku_id, 0) for loc in INVENTORY.values())


def _daily_rate(sku_id, location_id):
    return DAILY_SELL_THROUGH.get(location_id, {}).get(sku_id, 0)


def _days_of_supply(sku_id, location_id):
    """Days of supply at a store from that store's own daily sales."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    daily = _daily_rate(sku_id, location_id)
    return round(on_hand / daily, 1) if daily > 0 else 999.0


def _stock_status(sku_id, location_id):
    """Return stock status label for a SKU at a store."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    safety = SAFETY_STOCK.get(location_id, {}).get(sku_id, 0)
    if on_hand == 0:
        return "OUT_OF_STOCK"
    if on_hand <= safety:
        return "CRITICAL"
    if on_hand <= safety * 1.5:
        return "LOW"
    if _days_of_supply(sku_id, location_id) > 30:
        return "OVERSTOCK"
    return "HEALTHY"


def _replenishment_qty(sku_id, location_id, target_days=14):
    """Units needed to reach N days of supply at the store's own sales rate."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    target_qty = int(_daily_rate(sku_id, location_id) * target_days)
    return max(0, target_qty - on_hand)


def _channel_allocation_units(sku_id, total_available):
    """Allocate available inventory across channels by demand weight."""
    allocations = {}
    for channel, info in CHANNEL_DEMAND.items():
        allocations[channel] = int(total_available * info["weight"])
    remainder = total_available - sum(allocations.values())
    allocations["in_store"] += remainder
    return allocations


def _region_units(sku_id, region):
    return sum(INVENTORY[s].get(sku_id, 0) for s in STORES if STORES[s]["region"] == region)


def _region_rate(sku_id, region):
    return round(sum(_daily_rate(sku_id, s) for s in STORES if STORES[s]["region"] == region), 1)


def _transfer_totals():
    units = sum(m["units"] for p in TRANSFER_PHASES for m in p["moves"])
    cost = sum(p["cost"] for p in TRANSFER_PHASES)
    recovery = sum(p["recovery"] for p in TRANSFER_PHASES)
    return units, cost, recovery


def _ratio(numerator, denominator):
    return f"{round(numerator / denominator)}:1" if denominator else "n/a"


def _imbalance_totals():
    return (
        sum(i["units"] for i in IMBALANCES),
        sum(i["routes"] for i in IMBALANCES),
        sum(i["recovery"] for i in IMBALANCES),
        sum(i["transport"] for i in IMBALANCES),
    )


def _payback_months(investment, annual):
    return round(investment / annual * 12, 1)


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

OPERATIONS = [
    "inventory_dashboard",
    "stock_alerts",
    "replenishment_plan",
    "channel_allocation",
    "transfer_plan",
    "network_health",
    "automation_recommendations",
    "investment_proposal",
]


class InventoryVisibilityAgent(BasicAgent):
    """Agent providing omni-channel inventory visibility and planning."""

    def __init__(self):
        self.name = "inventory-visibility-agent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"]
                + " Always use this tool for inventory status, stockouts, transfers or reallocation, "
                "inventory health, warehouse automation and inventory investment proposals. The demo "
                "hero item is the Alpine Pro Winter Jacket (SKU-2001): sold out in Portland, excess in "
                "Seattle. Every operation has demo defaults, so call it right away without asking for "
                "SKUs or locations. Approvals such as 'execute both phases' or 'optimize all 8' never "
                "move stock: the tool returns a release-ready packet for an authorized planner."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "inventory_dashboard for real-time inventory status of top sellers or "
                            "winter jackets across all locations (or one store with location_id); "
                            "stock_alerts for critical stockouts and the nearest available stock; "
                            "replenishment_plan for warehouse replenishment to a 14-day supply; "
                            "channel_allocation for splitting stock across sales channels; "
                            "transfer_plan for 'create the reallocation plan' with cost and timing; "
                            "network_health for 'approved, execute both phases' and system-wide "
                            "inventory health, overstock and slow movers; automation_recommendations "
                            "for 'optimize all 8' and warehouse automation recommendations; "
                            "investment_proposal for the investment proposal with 3-year financial "
                            "projections."
                        ),
                    },
                    "sku_id": {"type": "string", "description": "SKU id or product name (default SKU-2001 Alpine Pro Winter Jacket)"},
                    "location_id": {"type": "string", "description": "Store or warehouse id or name, only to view one location"},
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

    # ---- operations -------------------------------------------------------

    def _location_snapshot(self, loc_id, persona):
        loc_info = STORES.get(loc_id) or WAREHOUSES.get(loc_id)
        lines = _response_header(persona) + ["# Inventory Visibility Snapshot", ""]
        lines.append(f"## {loc_info['name']} (`{loc_id}`)")
        lines.append("")
        lines.append("| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |")
        lines.append("|-----|---------|---------|--------------|--------|----------------|")
        for sku_id in SKUS:
            on_hand = INVENTORY[loc_id].get(sku_id, 0)
            if loc_id in STORES:
                safety = SAFETY_STOCK[loc_id].get(sku_id, 0)
                status = _stock_status(sku_id, loc_id)
                dos = _days_of_supply(sku_id, loc_id)
            else:
                safety, status, dos = "N/A", "WAREHOUSE", "N/A"
            lines.append(f"| {sku_id} | {SKUS[sku_id]['name']} | {on_hand} | {safety} | {status} | {dos} |")
        lines.append("")
        total_units = sum(INVENTORY[loc_id].values())
        lines.append(f"**Total Units at {loc_info['name']}:** {total_units:,}")
        return "\n".join(lines)

    def _inventory_dashboard(self, **kwargs):
        persona = kwargs.get("persona")
        if kwargs.get("location_id"):
            return self._location_snapshot(kwargs["location_id"], persona)
        sku_id = kwargs.get("sku_id") or "SKU-2001"
        sku = SKUS[sku_id]
        roll = NETWORK_ROLLUP.get(sku_id, {"other_stores": {"count": 0, "units": 0}, "in_transit": 0, "ecomm_reserve": 0, "ecomm_reserve_target": 0, "sold_out_days": {}})
        store_count = len(STORES) + roll["other_stores"]["count"]
        store_units = sum(INVENTORY[s].get(sku_id, 0) for s in STORES) + roll["other_stores"]["units"]
        wh_units = sum(INVENTORY[w].get(sku_id, 0) for w in WAREHOUSES)
        rows = [
            (f"Stores ({store_count})", store_units),
            (f"Warehouses ({len(WAREHOUSES)})", wh_units),
            ("In-transit", roll["in_transit"]),
            ("E-comm reserve", roll["ecomm_reserve"]),
        ]
        total = sum(units for _, units in rows)
        locations = store_count + len(WAREHOUSES) + (1 if roll["ecomm_reserve_target"] else 0)
        statuses = [_stock_status(sku_id, s) for s in STORES]
        store_status = "Unbalanced" if ("OVERSTOCK" in statuses and ("OUT_OF_STOCK" in statuses or "CRITICAL" in statuses)) else "Healthy"
        labels = [store_status, "Healthy", "Active", "Low" if roll["ecomm_reserve"] < roll["ecomm_reserve_target"] else "Healthy"]
        lines = _response_header(persona) + [
            "# Inventory Visibility Snapshot",
            "",
            f"Real-time inventory analyzed across all {locations} locations. Critical allocation imbalance "
            "detected - Seattle overstock while Portland is out of stock.",
            "",
            f"**{sku['name']} ({sku_id}) - All Locations:**",
            "",
            "| Location Type | Units | % Total | Status |",
            "|---|---|---|---|",
        ]
        for (label, units), status in zip(rows, labels):
            lines.append(f"| {label} | {units:,} | {round(units * 100 / total)}% | {status} |")
        lines.append(f"| **Total** | **{total:,}** | 100% | |")
        lines.append("")
        lines.append("**Critical Issues:**")
        for s in STORES:
            if STORES[s]["region"] != "Portland":
                continue
            on_hand = INVENTORY[s].get(sku_id, 0)
            if on_hand == 0:
                days = roll["sold_out_days"].get(s)
                lines.append(f"- {STORES[s]['name']} - 0 units (sold out {days} days ago)")
            else:
                lines.append(f"- {STORES[s]['name']} - {on_hand} units (selling {_daily_rate(sku_id, s):g}/day)")
        lines.append(
            f"- Seattle stores - {_region_units(sku_id, 'Seattle')} units excess "
            f"(selling {_region_rate(sku_id, 'Seattle'):g}/day)"
        )
        units, _, recovery = _transfer_totals()
        lines.append("")
        lines.append(f"**Opportunity:** Transfer {units} units Seattle -> Portland = {_money(recovery)} recovered sales")
        lines.append("")
        lines.append("Source: [Real-Time Inventory + POS Data + Demand Forecast]")
        lines.append("")
        lines.append("Next step: should I create the reallocation plan?")
        return "\n".join(lines)

    def _stock_alerts(self, **kwargs):
        lines = _response_header(kwargs.get("persona")) + ["# Draft Stock Review", "", "## Critical & Out-of-Stock Candidates", ""]
        lines.append("| Location | SKU | Product | On-Hand | Safety Stock | Daily Sales | Status | Nearest Available | Action Required |")
        lines.append("|----------|-----|---------|---------|--------------|-------------|--------|-------------------|-----------------|")
        alert_count = 0
        for loc_id in STORES:
            for sku_id in SKUS:
                status = _stock_status(sku_id, loc_id)
                if status in ("CRITICAL", "OUT_OF_STOCK"):
                    near = NEAREST_SOURCE.get(loc_id)
                    if near:
                        src = near["source"]
                        nearest = f"{STORES[src]['name']} ({INVENTORY[src].get(sku_id, 0)} units, {near['miles']} mi)"
                    else:
                        nearest = "Nearest warehouse"
                    action = "Review replenishment candidate" if status == "OUT_OF_STOCK" else "Review transfer candidate"
                    lines.append(
                        f"| {STORES[loc_id]['name']} | {sku_id} | {SKUS[sku_id]['name']} | "
                        f"{INVENTORY[loc_id].get(sku_id, 0)} | {SAFETY_STOCK[loc_id].get(sku_id, 0)} | "
                        f"{_daily_rate(sku_id, loc_id):g}/day | {status} | {nearest} | {action} |"
                    )
                    alert_count += 1
        lines.append("")
        lines.append(f"**Total Alerts:** {alert_count}")
        lines.append(
            "**Review guidance:** Use `Review replenishment candidate` for an "
            "out-of-stock item and `Review transfer candidate` for a critical "
            "item; neither phrase executes an inventory change. Same-day transfers "
            "from the nearest available store are drafted with the reallocation plan."
        )
        lines.append("")
        lines.append("## Overstock Sources")
        lines.append("")
        for loc_id in STORES:
            for sku_id in SKUS:
                if _stock_status(sku_id, loc_id) == "OVERSTOCK":
                    lines.append(
                        f"- **{STORES[loc_id]['name']}** / {SKUS[sku_id]['name']}: "
                        f"{INVENTORY[loc_id][sku_id]} units, {_days_of_supply(sku_id, loc_id)} days of supply"
                    )
        lines.append("")
        lines.append("## Low-Stock Warnings")
        lines.append("")
        low_count = 0
        for loc_id in STORES:
            for sku_id in SKUS:
                if _stock_status(sku_id, loc_id) == "LOW":
                    lines.append(f"- **{STORES[loc_id]['name']}** / {SKUS[sku_id]['name']}: {_days_of_supply(sku_id, loc_id)} days remaining")
                    low_count += 1
        lines.append(f"\n**Low-Stock Warnings:** {low_count}")
        return "\n".join(lines)

    def _replenishment_plan(self, **kwargs):
        target_days = 14
        lines = _response_header(kwargs.get("persona")) + [
            "# Draft Replenishment Plan",
            "",
            f"**Target:** {target_days}-day supply at each store (each store's own daily sales)",
            "",
            "| Store | SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |",
            "|-------|-----|---------|---------|--------|---------------|--------|-----------|-----------|",
        ]
        total_cost = 0.0
        for loc_id in STORES:
            for sku_id in SKUS:
                qty = _replenishment_qty(sku_id, loc_id, target_days)
                if qty > 0:
                    sku = SKUS[sku_id]
                    on_hand = INVENTORY[loc_id][sku_id]
                    source = "WH-SOUTH" if STORES[loc_id]["region"] == "Portland" else "WH-CENTRAL"
                    if INVENTORY[source].get(sku_id, 0) < qty:
                        source = "WH-EAST"
                    lt = LEAD_TIMES_DAYS[source][loc_id]
                    cost = round(qty * sku["unit_cost"], 2)
                    total_cost += cost
                    lines.append(
                        f"| {STORES[loc_id]['name']} | {sku_id} | {sku['name']} | {on_hand} | {on_hand + qty} | {qty} | {source} | {lt}d | ${cost:,.2f} |"
                    )
        lines.append("")
        lines.append(f"**Estimated Total Replenishment Cost:** ${total_cost:,.2f}")
        lines.append("Scheduled replenishment is a draft for planner approval; no purchase or transfer order is created.")
        return "\n".join(lines)

    def _channel_allocation(self, **kwargs):
        sku_id = kwargs.get("sku_id") or "SKU-2001"
        sku = SKUS[sku_id]
        total = _total_network_inventory(sku_id)
        allocations = _channel_allocation_units(sku_id, total)
        lines = _response_header(kwargs.get("persona")) + [
            "# Channel Allocation Scenario",
            "",
            f"**SKU:** {sku_id} — {sku['name']}",
            f"**Total Network Inventory:** {total:,} units (detailed stores and warehouses)",
            "",
            "| Channel | Weight | Allocated Units | Daily Demand Avg | Days Coverage |",
            "|---------|--------|-----------------|------------------|---------------|",
        ]
        for channel, units in allocations.items():
            info = CHANNEL_DEMAND[channel]
            daily = info["daily_units_avg"]
            coverage = round(units / daily, 1) if daily > 0 else 0
            lines.append(
                f"| {channel.replace('_', ' ').title()} | {info['weight']*100:.0f}% | {units:,} | {daily} | {coverage} |"
            )
        lines.append("")
        lines.append("## Allocation Recommendations")
        lines.append("")
        lines.append("- **In-Store Scenario:** Model a larger share for flagship and mall demand")
        lines.append("- **Online Buffer:** Model a three-day planning buffer for e-commerce")
        lines.append("- **BOPIS Buffer:** Model a pickup buffer; do not reserve units")
        lines.append("- **Marketplace Review:** Model a cap to reduce channel conflict")
        return "\n".join(lines)

    def _transfer_plan(self, **kwargs):
        sku_id = "SKU-2001"
        units, cost, recovery = _transfer_totals()
        seattle_after = _region_units(sku_id, "Seattle") - units
        rate = _region_rate(sku_id, "Seattle")
        days_left = int(seattle_after / rate)
        lines = _response_header(kwargs.get("persona")) + [
            "# Draft Reallocation Plan: Seattle -> Portland",
            "",
            f"Reallocation plan for the {SKUS[sku_id]['name']}, optimized for 36-hour execution with minimal "
            "disruption and strong ROI.",
            "",
        ]
        for p in TRANSFER_PHASES:
            p_units = sum(m["units"] for m in p["moves"])
            lines.append(f"## {p['phase']}")
            lines.append("")
            sources = []
            for m in p["moves"]:
                if m["from"] not in sources:
                    sources.append(m["from"])
            if len(sources) == 1:
                lines.append(f"- Move {p_units} units from {STORES[sources[0]]['name']} to {STORES[p['moves'][0]['to']]['name']}")
            else:
                lines.append(f"- Move {p_units} units from {len(sources)} Seattle suburban stores")
                for m in p["moves"]:
                    lines.append(f"  - {STORES[m['from']]['name']} -> {STORES[m['to']]['name']}: {m['units']} units")
            lines.append(f"- Transport: {p['transport']} ({_money(p['cost'])})")
            lines.append(f"- Pickup: {p['pickup']}; Arrival: {p['arrival']}")
            lines.append(f"- Revenue recovery: {_money(p['recovery'])} ({p['window']})")
            lines.append("")
        lines += [
            "## Total Plan",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Units transferred | {units} |",
            f"| Transportation cost | {_money(cost)} |",
            f"| Revenue recovered | {_money(recovery)} |",
            f"| ROI | {_ratio(recovery, cost)} |",
            "",
            f"**Impact on Seattle:** still leaves {seattle_after} units ({days_left} days of supply at the "
            f"current {rate:g}/day rate).",
            "",
            "Source: [Logistics Network + Cost Calculator + Demand Model]",
            "",
            "This is a draft plan: nothing has moved and no van or truck is booked. Next step: approve it "
            "so an authorized planner can release both phases.",
        ]
        return "\n".join(lines)

    def _network_health(self, **kwargs):
        units, cost, recovery = _transfer_totals()
        h = NETWORK_HEALTH
        overstock = sum(h["overstock_by_category"].values())
        n = len(IMBALANCES)
        i_units, i_routes, i_recovery, i_transport = _imbalance_totals()
        p1 = TRANSFER_PHASES[0]
        lines = _response_header(kwargs.get("persona")) + [
            "# Transfer Release Packet and System-Wide Inventory Health",
            "",
            f"Transfer packet ready for release: the Seattle van pickup slot is {p1['pickup']}. "
            f"System-wide analysis shows {n} more allocation opportunities.",
            "",
            "## Transfer Status (ready for you to release; nothing has moved yet)",
            "",
        ]
        for p in TRANSFER_PHASES:
            p_units = sum(m["units"] for m in p["moves"])
            lines.append(f"- {p['phase'].split(':')[0]}: {p['transport']}, pickup {p['pickup']}, "
                         f"{p_units} units, arrival {p['arrival']} - Ready for release")
        lines += [
            f"- Store systems: new quantities staged for {units} units (applied on release)",
            "- E-commerce: Portland inventory becomes visible online once the transfer is received",
            "",
            "## System-Wide Inventory Health",
            "",
            "| Metric | Current |",
            "|---|---|",
            f"| Stock balance score | {h['stock_balance_score']}/100 |",
            f"| Days of supply | {h['days_of_supply']} days |",
            f"| Overstock value | ${overstock / 1000000:.1f}M |",
            f"| Stockout incidents | {h['stockout_incidents_per_month']}/month |",
            "",
            "**Overstock by category:** " + "; ".join(f"{c} {_money(v)}" for c, v in h["overstock_by_category"].items()),
            "",
            "**Slow movers:** " + "; ".join(
                f"{SKUS[s['sku']]['name']} ({s['weeks_of_supply']} weeks of supply, {s['note']})" for s in h["slow_movers"]
            ),
            "",
            f"**Seasonal demand:** {h['seasonal_pattern']}",
            "",
            "## Additional Opportunities",
            "",
            f"- {n} SKUs with similar imbalances",
            f"- Combined recovery potential: {_money(i_recovery)}",
            f"- Transport investment: {_money(i_transport)}",
            f"- Total ROI: {_ratio(i_recovery, i_transport)}",
            "",
            "Source: [Inventory Optimization Engine + All Locations]",
            "",
            f"Next step: optimize all {n} opportunities?",
        ]
        return "\n".join(lines)

    def _automation_recommendations(self, **kwargs):
        n = len(IMBALANCES)
        i_units, i_routes, i_recovery, i_transport = _imbalance_totals()
        annual = sum(o["annual_benefit"] for o in AUTOMATION_OPTIONS)
        lines = _response_header(kwargs.get("persona")) + [
            "# Optimization Queue and Warehouse Automation Recommendations",
            "",
            f"All {n} SKU reallocations drafted for the next 72 hours. Warehouse automation analysis reveals "
            f"{_money(annual / 1000)}K annual savings opportunity.",
            "",
            "## Optimization Queue (draft for release)",
            "",
            "| SKU | Product | Route | Units | Recovery | Transport |",
            "|---|---|---|---|---|---|",
        ]
        for i in IMBALANCES:
            lines.append(f"| {i['sku']} | {SKUS[i['sku']]['name']} | {i['route']} | {i['units']} | {_money(i['recovery'])} | {_money(i['transport'])} |")
        lines += [
            "",
            f"- {n} SKU transfers drafted across a 3-day window",
            f"- Total units moving: {i_units} across {i_routes} routes",
            f"- Combined revenue recovery: {_money(i_recovery)}",
            f"- Transport investment: {_money(i_transport)}",
            "- Store notifications drafted for release by the planner; none sent",
            "",
            "## Warehouse Automation Recommendations",
            "",
        ]
        for o in AUTOMATION_OPTIONS:
            lines.append(f"**Priority {o['priority']}: {o['name']} ({_money(o['investment'] / 1000)}K investment)**")
            for hl in o["highlights"]:
                lines.append(f"- {hl}")
            lines.append(f"- {o['benefit_label']}: {_money(o['annual_benefit'])}/year")
            lines.append(f"- Payback: {_payback_months(o['investment'], o['annual_benefit']):g} months")
            lines.append("")
        lines += [
            f"**Total annual savings opportunity:** {_money(annual)}",
            "",
            "Source: [Warehouse Operations + Technology Assessment]",
            "",
            "Next step: generate the investment proposal?",
        ]
        return "\n".join(lines)

    def _investment_proposal(self, **kwargs):
        invest = sum(o["investment"] for o in AUTOMATION_OPTIONS)
        annual = sum(o["annual_benefit"] for o in AUTOMATION_OPTIONS)
        years = 3
        cumulative = annual * years
        net = cumulative - invest
        acc = INVENTORY_ACCURACY
        stockout_cut = AUTOMATION_OPTIONS[1]["highlights"][1].split(": ")[1]
        lines = _response_header(kwargs.get("persona")) + [
            "# Draft Investment Proposal: Inventory Automation",
            "",
            "## Investment Required",
            "",
        ]
        for o in AUTOMATION_OPTIONS:
            lines.append(f"- {o['name']}: {_money(o['investment'] / 1000)}K")
        lines.append(f"- **Total: {_money(invest / 1000)}K**")
        lines += [
            "",
            "## Annual Benefits",
            "",
            "| Year | " + " | ".join(o["benefit_type"] for o in AUTOMATION_OPTIONS) + " | Total |",
            "|---|" + "---|" * (len(AUTOMATION_OPTIONS) + 1),
        ]
        for y in range(1, years + 1):
            lines.append(f"| Year {y} | " + " | ".join(f"{_money(o['annual_benefit'] / 1000)}K" for o in AUTOMATION_OPTIONS) + f" | {_money(annual / 1000)}K |")
        lines += [
            "",
            "## 3-Year Summary",
            "",
            f"- Cumulative benefits: {_money(cumulative)}",
            f"- Net value: {_money(net)}",
            f"- ROI: {round(net * 100 / invest)}%",
            f"- Payback: {_payback_months(invest, annual):g} months",
            "",
            "## Operational Improvements",
            "",
            f"- Inventory accuracy: {acc['current_pct']}% -> {acc['target_pct']}%",
            f"- Stockouts: {stockout_cut}",
            "- Manual reorders: Eliminated",
            "",
            "Source: [Financial Planning + Technology ROI Models]",
            "",
            "Draft ready for you to share with the CFO and operations team in Microsoft Teams; nothing has been sent.",
        ]
        return "\n".join(lines)

    # ---- dispatch ----------------------------------------------------------

    def perform(self, **kwargs):
        if kwargs.get("data_source", "synthetic") != "synthetic":
            return "data_source must be `synthetic` for this package."
        sku_query = kwargs.get("sku_id")
        location_query = kwargs.get("location_id")
        if sku_query:
            sku_id = _resolve_sku(sku_query)
            if sku_id is None:
                return f"Unknown sku_id `{sku_query}`. Valid: {', '.join(SKUS)}"
            kwargs["sku_id"] = sku_id
        if location_query:
            location_id = _resolve_location(location_query)
            if location_id is None:
                return f"Unknown location_id `{location_query}`. Valid: {', '.join(INVENTORY)}"
            kwargs["location_id"] = location_id
        operation = kwargs.get("operation", "inventory_dashboard")
        dispatch = {
            "inventory_dashboard": self._inventory_dashboard,
            "stock_alerts": self._stock_alerts,
            "replenishment_plan": self._replenishment_plan,
            "channel_allocation": self._channel_allocation,
            "transfer_plan": self._transfer_plan,
            "network_health": self._network_health,
            "automation_recommendations": self._automation_recommendations,
            "investment_proposal": self._investment_proposal,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — the demo video's turns in order
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = InventoryVisibilityAgent()
    for op in ["inventory_dashboard", "transfer_plan", "network_health", "automation_recommendations", "investment_proposal"]:
        print("=" * 80)
        print(agent.perform(operation=op))
    print("=" * 80)
