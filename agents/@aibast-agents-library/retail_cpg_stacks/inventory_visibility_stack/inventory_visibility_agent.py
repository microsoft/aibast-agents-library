"""
Inventory Visibility Agent — Retail & CPG Stack

Provides real-time inventory visibility across stores, warehouses, and channels.
Surfaces stock alerts, generates replenishment plans, and optimizes channel
allocation for omni-channel retail operations.
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
    "version": "1.0.0",
    "display_name": "Inventory Visibility Agent",
    "description": (
        "Delivers real-time inventory dashboards, stock-out alerts, "
        "replenishment planning, and channel allocation optimization "
        "for omni-channel retail and CPG operations."
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
# Synthetic Data — Stores & Warehouses
# ---------------------------------------------------------------------------

STORES = {
    "STR-001": {
        "name": "Downtown Flagship",
        "city": "Chicago",
        "state": "IL",
        "type": "flagship",
        "capacity_sqft": 42000,
    },
    "STR-002": {
        "name": "Northshore Mall",
        "city": "Evanston",
        "state": "IL",
        "type": "mall",
        "capacity_sqft": 18500,
    },
    "STR-003": {
        "name": "Oakbrook Center",
        "city": "Oak Brook",
        "state": "IL",
        "type": "outlet",
        "capacity_sqft": 12000,
    },
    "STR-004": {
        "name": "Michigan Ave Express",
        "city": "Chicago",
        "state": "IL",
        "type": "express",
        "capacity_sqft": 6500,
    },
}

WAREHOUSES = {
    "WH-CENTRAL": {
        "name": "Central Distribution Center",
        "city": "Romeoville",
        "state": "IL",
        "capacity_pallets": 22000,
    },
    "WH-EAST": {
        "name": "East Regional Warehouse",
        "city": "Indianapolis",
        "state": "IN",
        "capacity_pallets": 14000,
    },
}

SKUS = {
    "SKU-1001": {"name": "Classic Denim Jacket", "category": "Apparel", "unit_cost": 34.50, "retail_price": 89.99},
    "SKU-1002": {"name": "Wireless Earbuds Pro", "category": "Electronics", "unit_cost": 18.75, "retail_price": 59.99},
    "SKU-1003": {"name": "Organic Cotton T-Shirt", "category": "Apparel", "unit_cost": 8.20, "retail_price": 29.99},
    "SKU-1004": {"name": "Smart Fitness Tracker", "category": "Electronics", "unit_cost": 42.00, "retail_price": 129.99},
    "SKU-1005": {"name": "Premium Running Shoes", "category": "Footwear", "unit_cost": 55.00, "retail_price": 149.99},
    "SKU-1006": {"name": "Stainless Water Bottle", "category": "Accessories", "unit_cost": 6.80, "retail_price": 24.99},
    "SKU-1007": {"name": "Leather Crossbody Bag", "category": "Accessories", "unit_cost": 27.50, "retail_price": 79.99},
    "SKU-1008": {"name": "UV Protection Sunglasses", "category": "Accessories", "unit_cost": 12.30, "retail_price": 44.99},
}

# Current on-hand quantities per location per SKU
INVENTORY = {
    "STR-001": {"SKU-1001": 74, "SKU-1002": 132, "SKU-1003": 210, "SKU-1004": 45, "SKU-1005": 38, "SKU-1006": 195, "SKU-1007": 61, "SKU-1008": 88},
    "STR-002": {"SKU-1001": 35, "SKU-1002": 67, "SKU-1003": 98, "SKU-1004": 22, "SKU-1005": 14, "SKU-1006": 110, "SKU-1007": 29, "SKU-1008": 53},
    "STR-003": {"SKU-1001": 18, "SKU-1002": 41, "SKU-1003": 65, "SKU-1004": 9, "SKU-1005": 7, "SKU-1006": 72, "SKU-1007": 15, "SKU-1008": 30},
    "STR-004": {"SKU-1001": 12, "SKU-1002": 28, "SKU-1003": 44, "SKU-1004": 6, "SKU-1005": 5, "SKU-1006": 55, "SKU-1007": 8, "SKU-1008": 19},
    "WH-CENTRAL": {"SKU-1001": 1450, "SKU-1002": 2300, "SKU-1003": 3800, "SKU-1004": 780, "SKU-1005": 620, "SKU-1006": 4100, "SKU-1007": 950, "SKU-1008": 1700},
    "WH-EAST": {"SKU-1001": 820, "SKU-1002": 1100, "SKU-1003": 2200, "SKU-1004": 410, "SKU-1005": 350, "SKU-1006": 2600, "SKU-1007": 530, "SKU-1008": 900},
}

SAFETY_STOCK = {
    "STR-001": {"SKU-1001": 30, "SKU-1002": 50, "SKU-1003": 80, "SKU-1004": 20, "SKU-1005": 15, "SKU-1006": 70, "SKU-1007": 25, "SKU-1008": 35},
    "STR-002": {"SKU-1001": 15, "SKU-1002": 30, "SKU-1003": 45, "SKU-1004": 10, "SKU-1005": 8, "SKU-1006": 40, "SKU-1007": 12, "SKU-1008": 20},
    "STR-003": {"SKU-1001": 10, "SKU-1002": 20, "SKU-1003": 30, "SKU-1004": 5, "SKU-1005": 5, "SKU-1006": 25, "SKU-1007": 8, "SKU-1008": 12},
    "STR-004": {"SKU-1001": 8, "SKU-1002": 15, "SKU-1003": 20, "SKU-1004": 4, "SKU-1005": 3, "SKU-1006": 20, "SKU-1007": 5, "SKU-1008": 10},
}

LEAD_TIMES_DAYS = {
    "WH-CENTRAL": {"STR-001": 1, "STR-002": 1, "STR-003": 2, "STR-004": 1},
    "WH-EAST": {"STR-001": 2, "STR-002": 2, "STR-003": 3, "STR-004": 2},
}

CHANNEL_DEMAND = {
    "in_store": {"weight": 0.45, "daily_units_avg": 320},
    "online_ship": {"weight": 0.30, "daily_units_avg": 215},
    "bopis": {"weight": 0.15, "daily_units_avg": 108},
    "marketplace": {"weight": 0.10, "daily_units_avg": 72},
}

DAILY_SELL_THROUGH = {
    "SKU-1001": 6.2, "SKU-1002": 9.8, "SKU-1003": 14.5, "SKU-1004": 3.1,
    "SKU-1005": 2.7, "SKU-1006": 12.0, "SKU-1007": 4.4, "SKU-1008": 7.3,
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _total_network_inventory(sku_id):
    """Sum on-hand across all locations for a given SKU."""
    return sum(loc.get(sku_id, 0) for loc in INVENTORY.values())


def _days_of_supply(sku_id, location_id):
    """Estimate days-of-supply at a location."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    daily = DAILY_SELL_THROUGH.get(sku_id, 1.0)
    return round(on_hand / daily, 1) if daily > 0 else 999.0


def _stock_status(sku_id, location_id):
    """Return stock status label for a SKU at a location."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    safety = SAFETY_STOCK.get(location_id, {}).get(sku_id, 0)
    if on_hand == 0:
        return "OUT_OF_STOCK"
    if on_hand <= safety:
        return "CRITICAL"
    if on_hand <= safety * 1.5:
        return "LOW"
    return "HEALTHY"


def _replenishment_qty(sku_id, location_id, target_days=14):
    """Calculate replenishment quantity targeting N days of supply."""
    on_hand = INVENTORY.get(location_id, {}).get(sku_id, 0)
    daily = DAILY_SELL_THROUGH.get(sku_id, 1.0)
    target_qty = int(daily * target_days)
    needed = max(0, target_qty - on_hand)
    return needed


def _channel_allocation_units(sku_id, total_available):
    """Allocate available inventory across channels by demand weight."""
    allocations = {}
    for channel, info in CHANNEL_DEMAND.items():
        allocations[channel] = int(total_available * info["weight"])
    remainder = total_available - sum(allocations.values())
    allocations["in_store"] += remainder
    return allocations


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

class InventoryVisibilityAgent(BasicAgent):
    """Agent providing omni-channel inventory visibility and planning."""

    def __init__(self):
        self.name = "inventory-visibility-agent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "inventory_dashboard",
                            "stock_alerts",
                            "replenishment_plan",
                            "channel_allocation",
                        ],
                    },
                    "sku_id": {"type": "string"},
                    "location_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    # ---- operations -------------------------------------------------------

    def _inventory_dashboard(self, **kwargs):
        location_id = kwargs.get("location_id")
        locations = [location_id] if location_id and location_id in INVENTORY else list(STORES.keys())
        lines = ["# Inventory Dashboard", ""]
        for loc_id in locations:
            loc_info = STORES.get(loc_id, WAREHOUSES.get(loc_id, {}))
            lines.append(f"## {loc_info.get('name', loc_id)} (`{loc_id}`)")
            lines.append("")
            lines.append("| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |")
            lines.append("|-----|---------|---------|--------------|--------|----------------|")
            for sku_id in sorted(SKUS.keys()):
                sku = SKUS[sku_id]
                on_hand = INVENTORY[loc_id].get(sku_id, 0)
                safety = SAFETY_STOCK.get(loc_id, {}).get(sku_id, "N/A")
                status = _stock_status(sku_id, loc_id)
                dos = _days_of_supply(sku_id, loc_id)
                lines.append(f"| {sku_id} | {sku['name']} | {on_hand} | {safety} | {status} | {dos} |")
            lines.append("")
        total_units = sum(sum(v.values()) for v in INVENTORY.values())
        lines.append(f"**Total Network Inventory:** {total_units:,} units across {len(INVENTORY)} locations")
        return "\n".join(lines)

    def _stock_alerts(self, **kwargs):
        lines = ["# Stock Alerts", "", "## Critical & Out-of-Stock Items", ""]
        lines.append("| Location | SKU | Product | On-Hand | Safety Stock | Status | Action Required |")
        lines.append("|----------|-----|---------|---------|--------------|--------|-----------------|")
        alert_count = 0
        for loc_id in sorted(STORES.keys()):
            for sku_id in sorted(SKUS.keys()):
                status = _stock_status(sku_id, loc_id)
                if status in ("CRITICAL", "OUT_OF_STOCK"):
                    sku = SKUS[sku_id]
                    on_hand = INVENTORY[loc_id].get(sku_id, 0)
                    safety = SAFETY_STOCK[loc_id].get(sku_id, 0)
                    action = "Emergency replenish" if status == "OUT_OF_STOCK" else "Expedite transfer"
                    loc_name = STORES[loc_id]["name"]
                    lines.append(
                        f"| {loc_name} | {sku_id} | {sku['name']} | {on_hand} | {safety} | {status} | {action} |"
                    )
                    alert_count += 1
        lines.append("")
        lines.append(f"**Total Alerts:** {alert_count}")
        lines.append("")
        lines.append("## Low-Stock Warnings")
        lines.append("")
        low_count = 0
        for loc_id in sorted(STORES.keys()):
            for sku_id in sorted(SKUS.keys()):
                status = _stock_status(sku_id, loc_id)
                if status == "LOW":
                    dos = _days_of_supply(sku_id, loc_id)
                    lines.append(f"- **{STORES[loc_id]['name']}** / {SKUS[sku_id]['name']}: {dos} days remaining")
                    low_count += 1
        lines.append(f"\n**Low-Stock Warnings:** {low_count}")
        return "\n".join(lines)

    def _replenishment_plan(self, **kwargs):
        target_days = 14
        lines = [
            "# Replenishment Plan",
            "",
            f"**Target:** {target_days}-day supply at each store",
            "",
        ]
        total_cost = 0.0
        for loc_id in sorted(STORES.keys()):
            store = STORES[loc_id]
            lines.append(f"## {store['name']} (`{loc_id}`)")
            lines.append("")
            lines.append("| SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |")
            lines.append("|-----|---------|---------|--------|---------------|--------|-----------|-----------|")
            for sku_id in sorted(SKUS.keys()):
                qty = _replenishment_qty(sku_id, loc_id, target_days)
                if qty > 0:
                    sku = SKUS[sku_id]
                    on_hand = INVENTORY[loc_id][sku_id]
                    target_qty = on_hand + qty
                    wh_central = INVENTORY["WH-CENTRAL"].get(sku_id, 0)
                    source = "WH-CENTRAL" if wh_central >= qty else "WH-EAST"
                    lt = LEAD_TIMES_DAYS.get(source, {}).get(loc_id, 3)
                    cost = round(qty * sku["unit_cost"], 2)
                    total_cost += cost
                    lines.append(
                        f"| {sku_id} | {sku['name']} | {on_hand} | {target_qty} | {qty} | {source} | {lt}d | ${cost:,.2f} |"
                    )
            lines.append("")
        lines.append(f"**Estimated Total Replenishment Cost:** ${total_cost:,.2f}")
        return "\n".join(lines)

    def _channel_allocation(self, **kwargs):
        sku_id = kwargs.get("sku_id", "SKU-1001")
        sku = SKUS.get(sku_id, SKUS["SKU-1001"])
        total = _total_network_inventory(sku_id)
        allocations = _channel_allocation_units(sku_id, total)
        lines = [
            "# Channel Allocation",
            "",
            f"**SKU:** {sku_id} — {sku['name']}",
            f"**Total Network Inventory:** {total:,} units",
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
        lines.append("- **In-Store Priority:** Flagship and mall locations receive 60% of in-store allocation")
        lines.append("- **Online Buffer:** Maintain 3-day safety stock for e-commerce fulfillment")
        lines.append("- **BOPIS Reserve:** Hold 10% buffer for same-day pickup surges")
        lines.append("- **Marketplace Cap:** Limit marketplace allocation to prevent channel conflict")
        return "\n".join(lines)

    # ---- dispatch ----------------------------------------------------------

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "inventory_dashboard")
        dispatch = {
            "inventory_dashboard": self._inventory_dashboard,
            "stock_alerts": self._stock_alerts,
            "replenishment_plan": self._replenishment_plan,
            "channel_allocation": self._channel_allocation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = InventoryVisibilityAgent()
    print("=" * 80)
    print(agent.perform(operation="inventory_dashboard", location_id="STR-001"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="stock_alerts"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="replenishment_plan"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="channel_allocation", sku_id="SKU-1003"))
    print("=" * 80)
