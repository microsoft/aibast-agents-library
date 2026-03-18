"""
Inventory Rebalancing Agent

Analyzes warehouse inventory levels across multiple facilities, identifies
imbalances relative to demand forecasts, and generates transfer plans with
cost-optimized rebalancing recommendations. Supports SKU-level snapshot
reporting, inter-warehouse transfer planning, and holding-cost analysis.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/inventory-rebalancing",
    "version": "1.0.0",
    "display_name": "Inventory Rebalancing Agent",
    "description": "Optimizes multi-warehouse inventory distribution by analyzing stock levels against demand forecasts and generating cost-effective transfer plans.",
    "author": "AIBAST",
    "tags": ["inventory", "warehouse", "supply-chain", "rebalancing", "manufacturing"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

WAREHOUSES = {
    "WH-ATL": {
        "name": "Atlanta Distribution Center",
        "region": "Southeast",
        "capacity_pallets": 12000,
        "used_pallets": 10450,
        "annual_holding_cost_per_pallet": 142.0,
    },
    "WH-ORD": {
        "name": "Chicago Regional Hub",
        "region": "Midwest",
        "capacity_pallets": 18000,
        "used_pallets": 9200,
        "annual_holding_cost_per_pallet": 158.0,
    },
    "WH-DFW": {
        "name": "Dallas Fulfillment Center",
        "region": "South Central",
        "capacity_pallets": 15000,
        "used_pallets": 14100,
        "annual_holding_cost_per_pallet": 135.0,
    },
    "WH-SEA": {
        "name": "Seattle West Coast Depot",
        "region": "Pacific Northwest",
        "capacity_pallets": 10000,
        "used_pallets": 4300,
        "annual_holding_cost_per_pallet": 172.0,
    },
}

SKU_INVENTORY = {
    "SKU-4401": {"description": "Brushless DC Motor 48V", "unit_cost": 87.50, "weight_kg": 3.2,
                  "levels": {"WH-ATL": 3200, "WH-ORD": 1800, "WH-DFW": 4100, "WH-SEA": 600}},
    "SKU-4402": {"description": "Planetary Gearbox PG-20", "unit_cost": 214.00, "weight_kg": 5.8,
                  "levels": {"WH-ATL": 750, "WH-ORD": 2400, "WH-DFW": 300, "WH-SEA": 1100}},
    "SKU-4403": {"description": "Linear Actuator LA-150", "unit_cost": 162.30, "weight_kg": 4.1,
                  "levels": {"WH-ATL": 1900, "WH-ORD": 500, "WH-DFW": 2600, "WH-SEA": 200}},
    "SKU-4404": {"description": "Servo Controller SC-800", "unit_cost": 345.00, "weight_kg": 1.4,
                  "levels": {"WH-ATL": 400, "WH-ORD": 1200, "WH-DFW": 950, "WH-SEA": 1800}},
    "SKU-4405": {"description": "Encoder Module EM-512", "unit_cost": 58.75, "weight_kg": 0.6,
                  "levels": {"WH-ATL": 5000, "WH-ORD": 3100, "WH-DFW": 4800, "WH-SEA": 900}},
    "SKU-4406": {"description": "Harmonic Drive HD-25", "unit_cost": 489.00, "weight_kg": 7.3,
                  "levels": {"WH-ATL": 180, "WH-ORD": 620, "WH-DFW": 90, "WH-SEA": 340}},
}

DEMAND_FORECASTS = {
    "SKU-4401": {"WH-ATL": 2800, "WH-ORD": 2600, "WH-DFW": 3000, "WH-SEA": 1500},
    "SKU-4402": {"WH-ATL": 1100, "WH-ORD": 900, "WH-DFW": 1200, "WH-SEA": 800},
    "SKU-4403": {"WH-ATL": 800, "WH-ORD": 1400, "WH-DFW": 1100, "WH-SEA": 900},
    "SKU-4404": {"WH-ATL": 700, "WH-ORD": 600, "WH-DFW": 800, "WH-SEA": 500},
    "SKU-4405": {"WH-ATL": 3500, "WH-ORD": 4200, "WH-DFW": 3800, "WH-SEA": 2300},
    "SKU-4406": {"WH-ATL": 300, "WH-ORD": 250, "WH-DFW": 400, "WH-SEA": 280},
}

REORDER_POINTS = {
    "SKU-4401": 1200, "SKU-4402": 500, "SKU-4403": 600,
    "SKU-4404": 350, "SKU-4405": 2000, "SKU-4406": 150,
}

TRANSFER_COSTS_PER_KG = {
    ("WH-ATL", "WH-ORD"): 0.28, ("WH-ATL", "WH-DFW"): 0.22,
    ("WH-ATL", "WH-SEA"): 0.41, ("WH-ORD", "WH-ATL"): 0.28,
    ("WH-ORD", "WH-DFW"): 0.25, ("WH-ORD", "WH-SEA"): 0.34,
    ("WH-DFW", "WH-ATL"): 0.22, ("WH-DFW", "WH-ORD"): 0.25,
    ("WH-DFW", "WH-SEA"): 0.38, ("WH-SEA", "WH-ATL"): 0.41,
    ("WH-SEA", "WH-ORD"): 0.34, ("WH-SEA", "WH-DFW"): 0.38,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _utilization_pct(wh_id):
    """Return warehouse utilization as a percentage."""
    wh = WAREHOUSES[wh_id]
    return round(wh["used_pallets"] / wh["capacity_pallets"] * 100, 1)


def _stock_vs_demand(sku, wh_id):
    """Return surplus (+) or deficit (-) for a SKU at a warehouse."""
    on_hand = SKU_INVENTORY[sku]["levels"].get(wh_id, 0)
    forecast = DEMAND_FORECASTS[sku].get(wh_id, 0)
    return on_hand - forecast


def _total_inventory_value(wh_id):
    """Sum the dollar value of all SKUs at a warehouse."""
    total = 0.0
    for sku, info in SKU_INVENTORY.items():
        qty = info["levels"].get(wh_id, 0)
        total += qty * info["unit_cost"]
    return round(total, 2)


def _build_imbalances():
    """Return list of (sku, wh_from, wh_to, qty, cost) transfer suggestions."""
    transfers = []
    for sku, info in SKU_INVENTORY.items():
        surpluses = []
        deficits = []
        for wh_id in WAREHOUSES:
            delta = _stock_vs_demand(sku, wh_id)
            if delta > 200:
                surpluses.append((wh_id, delta))
            elif delta < -200:
                deficits.append((wh_id, abs(delta)))
        surpluses.sort(key=lambda x: x[1], reverse=True)
        deficits.sort(key=lambda x: x[1], reverse=True)
        for src, s_qty in surpluses:
            for dst, d_qty in deficits:
                move_qty = min(s_qty, d_qty)
                if move_qty <= 0:
                    continue
                cost_per_unit = TRANSFER_COSTS_PER_KG.get(
                    (src, dst), 0.30) * info["weight_kg"]
                cost = round(move_qty * cost_per_unit, 2)
                transfers.append((sku, src, dst, move_qty, cost))
                s_qty -= move_qty
                d_qty -= move_qty
    return transfers


def _annual_holding_cost(wh_id):
    """Estimate total annual holding cost for a warehouse."""
    wh = WAREHOUSES[wh_id]
    return round(wh["used_pallets"] * wh["annual_holding_cost_per_pallet"], 2)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class InventoryRebalancingAgent(BasicAgent):
    """Optimizes multi-warehouse inventory distribution against demand forecasts."""

    def __init__(self):
        self.name = "InventoryRebalancingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "inventory_snapshot",
                "rebalance_recommendation",
                "transfer_plan",
                "cost_analysis",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "inventory_snapshot")
        dispatch = {
            "inventory_snapshot": self._inventory_snapshot,
            "rebalance_recommendation": self._rebalance_recommendation,
            "transfer_plan": self._transfer_plan,
            "cost_analysis": self._cost_analysis,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid operations: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _inventory_snapshot(self, **kwargs) -> str:
        lines = ["## Inventory Snapshot\n"]
        lines.append("| Warehouse | Region | Utilization | Pallets Used/Cap | Inventory Value |")
        lines.append("|-----------|--------|-------------|------------------|-----------------|")
        for wh_id, wh in WAREHOUSES.items():
            util = _utilization_pct(wh_id)
            val = _total_inventory_value(wh_id)
            flag = " :red_circle:" if util > 90 else ""
            lines.append(
                f"| {wh['name']} | {wh['region']} | {util}%{flag} | "
                f"{wh['used_pallets']:,}/{wh['capacity_pallets']:,} | ${val:,.2f} |"
            )

        lines.append("\n### SKU Levels by Warehouse\n")
        lines.append("| SKU | Description | ATL | ORD | DFW | SEA | Reorder Pt |")
        lines.append("|-----|-------------|-----|-----|-----|-----|------------|")
        for sku, info in SKU_INVENTORY.items():
            lvls = info["levels"]
            rp = REORDER_POINTS[sku]
            row_cells = [f"{lvls.get(wh, 0):,}" for wh in WAREHOUSES]
            flags = []
            for wh in WAREHOUSES:
                if lvls.get(wh, 0) < rp:
                    flags.append(wh)
            note = f" (below reorder at {', '.join(flags)})" if flags else ""
            lines.append(
                f"| {sku} | {info['description']} | {' | '.join(row_cells)} | {rp:,}{note} |"
            )
        return "\n".join(lines)

    def _rebalance_recommendation(self, **kwargs) -> str:
        lines = ["## Rebalance Recommendations\n"]
        lines.append("Analysis of stock-vs-demand across all facilities:\n")
        lines.append("| SKU | Warehouse | On-Hand | Forecast | Delta | Status |")
        lines.append("|-----|-----------|---------|----------|-------|--------|")
        critical_count = 0
        for sku in SKU_INVENTORY:
            for wh_id in WAREHOUSES:
                delta = _stock_vs_demand(sku, wh_id)
                on_hand = SKU_INVENTORY[sku]["levels"].get(wh_id, 0)
                forecast = DEMAND_FORECASTS[sku].get(wh_id, 0)
                if delta < -200:
                    status = "DEFICIT"
                    critical_count += 1
                elif delta > 500:
                    status = "SURPLUS"
                else:
                    status = "Balanced"
                if status != "Balanced":
                    lines.append(
                        f"| {sku} | {WAREHOUSES[wh_id]['name'][:20]} | "
                        f"{on_hand:,} | {forecast:,} | {delta:+,} | **{status}** |"
                    )
        lines.append(f"\n**Critical imbalances detected:** {critical_count}")
        lines.append("**Recommendation:** Execute transfer plan to redistribute surplus stock to deficit locations.")
        return "\n".join(lines)

    def _transfer_plan(self, **kwargs) -> str:
        transfers = _build_imbalances()
        lines = ["## Transfer Plan\n"]
        if not transfers:
            lines.append("No transfers required; inventory is balanced within tolerance.")
            return "\n".join(lines)

        lines.append("| SKU | From | To | Qty | Unit Wt (kg) | Transfer Cost |")
        lines.append("|-----|------|----|-----|--------------|---------------|")
        total_cost = 0.0
        total_units = 0
        for sku, src, dst, qty, cost in transfers:
            wt = SKU_INVENTORY[sku]["weight_kg"]
            lines.append(
                f"| {sku} | {src} | {dst} | {qty:,} | {wt} | ${cost:,.2f} |"
            )
            total_cost += cost
            total_units += qty

        lines.append(f"\n**Total units to transfer:** {total_units:,}")
        lines.append(f"**Total transfer cost:** ${total_cost:,.2f}")
        lines.append(f"**Estimated transit time:** 2-5 business days (ground freight)")
        lines.append(
            "\n### Expected Post-Transfer Utilization\n"
        )
        lines.append("| Warehouse | Current Util | Projected Util |")
        lines.append("|-----------|-------------|----------------|")
        for wh_id, wh in WAREHOUSES.items():
            cur = _utilization_pct(wh_id)
            # Rough projection: assume net transfer effect
            net = sum(q for s, _, d, q, _ in transfers if d == wh_id) - sum(
                q for s, _, d, q, _ in transfers if s == wh_id
            )
            # This is a simplified model
            proj_pallets = wh["used_pallets"] + int(net * 0.02)  # rough pallet factor
            proj = round(proj_pallets / wh["capacity_pallets"] * 100, 1)
            lines.append(f"| {wh['name']} | {cur}% | {proj}% |")
        return "\n".join(lines)

    def _cost_analysis(self, **kwargs) -> str:
        lines = ["## Inventory Holding & Transfer Cost Analysis\n"]

        lines.append("### Annual Holding Costs\n")
        lines.append("| Warehouse | Pallets | Cost/Pallet/Yr | Annual Holding Cost |")
        lines.append("|-----------|---------|----------------|---------------------|")
        total_holding = 0.0
        for wh_id, wh in WAREHOUSES.items():
            hc = _annual_holding_cost(wh_id)
            total_holding += hc
            lines.append(
                f"| {wh['name']} | {wh['used_pallets']:,} | "
                f"${wh['annual_holding_cost_per_pallet']:.2f} | ${hc:,.2f} |"
            )
        lines.append(f"\n**Total annual holding cost:** ${total_holding:,.2f}")

        lines.append("\n### Inventory Value at Risk (Below Reorder Point)\n")
        lines.append("| SKU | Warehouse | On-Hand | Reorder Pt | Shortfall | Value at Risk |")
        lines.append("|-----|-----------|---------|------------|-----------|---------------|")
        total_risk = 0.0
        for sku, info in SKU_INVENTORY.items():
            rp = REORDER_POINTS[sku]
            for wh_id in WAREHOUSES:
                qty = info["levels"].get(wh_id, 0)
                if qty < rp:
                    shortfall = rp - qty
                    val = round(shortfall * info["unit_cost"], 2)
                    total_risk += val
                    lines.append(
                        f"| {sku} | {wh_id} | {qty:,} | {rp:,} | {shortfall:,} | ${val:,.2f} |"
                    )
        lines.append(f"\n**Total value at risk from stockouts:** ${total_risk:,.2f}")

        transfers = _build_imbalances()
        transfer_cost = sum(c for _, _, _, _, c in transfers)
        lines.append(f"\n### Transfer vs. Holding Trade-off")
        lines.append(f"- One-time transfer cost: **${transfer_cost:,.2f}**")
        lines.append(f"- Avoided expedited-shipping premium (est.): **${transfer_cost * 3.2:,.2f}**")
        lines.append(f"- Net annual benefit from rebalancing: **${total_risk * 0.6 - transfer_cost:,.2f}**")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = InventoryRebalancingAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
