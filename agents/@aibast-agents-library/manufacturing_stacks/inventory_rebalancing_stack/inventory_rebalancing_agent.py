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
    "description": "Analyze a fixed synthetic inventory snapshot and recommend review-ready rebalancing options. Never claim that inventory was moved, reordered, returned, or liquidated.",
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

PORTFOLIO_CLASSIFICATIONS = {
    "SKU-4401": {"velocity": "MEDIUM", "strategic_value": "CORE", "lifecycle_risk": "LOW"},
    "SKU-4402": {"velocity": "SLOW-MOVING", "strategic_value": "HIGH", "lifecycle_risk": "LOW"},
    "SKU-4403": {"velocity": "SLOW-MOVING", "strategic_value": "STANDARD", "lifecycle_risk": "ELEVATED"},
    "SKU-4404": {"velocity": "MEDIUM", "strategic_value": "HIGH", "lifecycle_risk": "LOW"},
    "SKU-4405": {"velocity": "FAST", "strategic_value": "CORE", "lifecycle_risk": "LOW"},
    "SKU-4406": {"velocity": "SLOW-MOVING", "strategic_value": "CRITICAL", "lifecycle_risk": "ELEVATED"},
}

TRANSFER_COSTS_PER_KG = {
    ("WH-ATL", "WH-ORD"): 0.28, ("WH-ATL", "WH-DFW"): 0.22,
    ("WH-ATL", "WH-SEA"): 0.41, ("WH-ORD", "WH-ATL"): 0.28,
    ("WH-ORD", "WH-DFW"): 0.25, ("WH-ORD", "WH-SEA"): 0.34,
    ("WH-DFW", "WH-ATL"): 0.22, ("WH-DFW", "WH-ORD"): 0.25,
    ("WH-DFW", "WH-SEA"): 0.38, ("WH-SEA", "WH-ATL"): 0.41,
    ("WH-SEA", "WH-ORD"): 0.34, ("WH-SEA", "WH-DFW"): 0.38,
}


# Portfolio scenario (the demo default): one consumer-goods warehouse portfolio.
PORTFOLIO = {
    "total_value": 5_000_000,
    "slow_moving_pct": 30,
    "utilization_pct": 95,
    "holding_cost_rate_pct": 13.5,
    "cost_of_capital_pct": 8,
    "sku_count_reorder_review": 240,
}

# Slow-moving breakdown. The four disposition buckets total $1.25M; the remaining $250K of the
# $1.5M slow-moving value is "other slow movers" (the consignment candidates), so the table adds up.
SLOW_MOVING = [
    {"category": "Obsolete", "value": 450_000, "action": "liquidate immediately"},
    {"category": "Seasonal", "value": 300_000, "action": "store or pre-sell"},
    {"category": "Excess safety stock", "value": 375_000, "action": "right-size"},
    {"category": "Dead stock", "value": 125_000, "action": "write off"},
    {"category": "Other slow movers", "value": 250_000, "action": "consignment"},
]

# 90-day recovery plan: (phase, action, cash or working capital freed).
RECOVERY_PLAN = [
    {"phase": "Phase 1: Immediate Actions (Week 1-2)", "items": [
        ("Flash sale: 50% off obsolete items ($450K inventory)", "Expected recovery", 225_000),
        ("Vendor returns: $200K (restocking fees: $20K)", "Net credit", 180_000),
        ("Write-offs: $125K dead stock (tax benefit: $31K)", "Tax benefit", 31_000),
    ]},
    {"phase": "Phase 2: Strategic Moves (Week 3-6)", "items": [
        ("Pre-season sale: $300K seasonal (80% recovery)", "Expected recovery", 240_000),
        ("Consignment agreements: $180K slow movers", "Inventory moved off books", 180_000),
        ("Safety stock reduction: $375K -> $150K freed", "Working capital freed", 150_000),
    ]},
    {"phase": "Phase 3: Optimization (Week 7-12)", "items": [
        ("Reorder point adjustments across 240 SKUs", "Working capital freed", 194_000),
        ("JIT agreements with 3 key suppliers", "Enables lower reorder points", 0),
        ("ABC analysis implementation", "Keeps the portfolio classified", 0),
    ]},
]

# When the recovery cash lands, by execution window (sums to the same $1.2M).
CASH_SCHEDULE = [
    {"window": "Week 1-2: Crisis Actions", "label": "Expected cash",
     "actions": ["Launch flash sale (marketing: email + web)", "Process vendor returns (3 suppliers)",
                 "Tag and segregate dead stock"],
     "cash": [("Flash sale proceeds", 225_000), ("First vendor-return credits", 82_000)]},
    {"window": "Week 3-6: Strategic Liquidation", "label": "Expected recovery",
     "actions": ["Pre-season promotional campaign", "Negotiate consignment deals", "Implement dynamic pricing"],
     "cash": [("Remaining vendor-return credits", 98_000), ("Pre-season sale", 240_000),
              ("First consignment settlements", 127_000)]},
    {"window": "Week 7-12: System Optimization", "label": "Expected working capital freed",
     "actions": ["Deploy AI-powered reorder points", "Establish JIT supplier agreements",
                 "ABC classification rollout", "Team training: 40 staff hours"],
     "cash": [("Remaining consignment settlements", 53_000), ("Dead-stock write-off tax benefit", 31_000),
              ("Safety stock right-sizing", 150_000), ("Reorder point adjustments", 194_000)]},
]

MILESTONES = [
    ("Day 14", "$300K cash recovered"),
    ("Day 45", "Warehouse at 75% utilization"),
    ("Day 90", "$1.2M working capital freed"),
]

# Share of warehouse space by category: (current %, after optimization %).
SPACE_BY_CATEGORY = [
    ("Obsolete items", 12, 1),
    ("Excess safety", 18, 8),
    ("Seasonal storage", 15, 11),
    ("Dead stock", 5, 0),
]

WAREHOUSE_BENEFITS = [
    "Improved picking efficiency: +35%",
    "Reduced handling damage: -40%",
    "Faster order fulfillment: -2 days avg",
    "Cycle count accuracy: 94% -> 98%",
    "Staff safety: Reduced congestion hazards",
]
GROWTH_CAPACITY = 2_800_000  # modeled room for additional inventory after optimization

ANNUAL_SAVINGS = [
    ("Holding costs reduced", 202_000),   # 13.5% x $1.5M slow-moving, rounded down
    ("Warehouse rent (avoid expansion)", 180_000),
    ("Obsolescence write-offs", 135_000),
    ("Handling efficiency", 78_000),
    ("Insurance premiums", 45_000),
]
IMPLEMENTATION_COST = 42_000

MONITORING_PLAN = {
    "Real-Time Dashboards": ["Inventory velocity by SKU", "Days-on-hand trending",
                             "Slow-moving item alerts (>90 days)", "Working capital efficiency"],
    "Automated Actions (proposed policy; each needs an approved tool and owner)": [
        "Auto-flag items at 60 days no movement", "Price optimization for aging inventory",
        "Reorder point adjustments weekly", "Excess stock alerts to procurement"],
    "Monthly Reviews": ["ABC analysis updates", "Obsolescence risk assessment",
                        "Supplier performance scoring", "Warehouse utilization trends"],
}
SUCCESS_METRICS = [
    ("Inventory turns", "4.2 -> 7.8 (target)"),
    ("Working capital ratio", "Improved 35%"),
    ("Obsolescence rate", "6% -> <2%"),
    ("Perfect order rate", "+12%"),
]

_GATE = ("Synthetic planning data. This agent recommends only: nothing is liquidated, returned, "
         "written off, repriced, moved, or reordered, and no message is sent.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _k(value):
    """$225K style."""
    return f"${value // 1000:,}K"


def _m(value):
    """$1.2M style."""
    return f"${value / 1_000_000:.1f}M"


def _recovery_total():
    return sum(amount for phase in RECOVERY_PLAN for _, _, amount in phase["items"])

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
    """Annual holding cost for a warehouse: inventory value x the portfolio holding-cost rate (13.5%)."""
    return round(_total_inventory_value(wh_id) * PORTFOLIO["holding_cost_rate_pct"] / 100, 2)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "inventory_snapshot", "rebalance_recommendation", "transfer_plan", "cost_analysis",
    "portfolio_analysis", "recovery_plan", "warehouse_impact", "financial_impact",
    "execution_timeline", "monitoring_plan",
]


class InventoryRebalancingAgent(BasicAgent):
    """Optimizes multi-warehouse inventory distribution against demand forecasts."""

    def __init__(self):
        self.name = "InventoryRebalancingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always use this tool for inventory optimization: the "
                "demo portfolio ($5M inventory, 30% slow-moving, warehouse 95% full) and its recovery "
                "plan, warehouse impact, financial impact, execution timeline and monitoring plan, plus "
                "per-distribution-center rebalancing. Call it first; every operation has demo defaults."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "portfolio_analysis: the default and the first step only for the portfolio story 'we have $5M inventory, "
                            "30% slow-moving, warehouse 95% full, need an optimization plan' (current state "
                            "and slow-moving breakdown). recovery_plan: 'show the recovery plan' (90-day "
                            "phased plan). warehouse_impact: 'show warehouse impact' or space/utilization. "
                            "financial_impact: 'show the financial impact', ROI or savings. "
                            "execution_timeline: 'show the execution timeline' or implementation steps. "
                            "monitoring_plan: 'show the monitoring approach', ongoing optimization, alerts "
                            "or success metrics. The four distribution-center operations below cover the "
                            "Atlanta/Chicago/Dallas/Seattle network: "
                            "inventory_snapshot: summarize per-distribution-center utilization and SKU levels. "
                            "rebalance_recommendation: identify forecast-relative excess and shortage. "
                            "transfer_plan: prepare proposed inter-warehouse moves for approval; never "
                            "move inventory. cost_analysis: where inventory exposure is concentrated, total "
                            "annual holding cost, value at risk and trade-offs for a planning meeting; "
                            "compare synthetic holding, shortage, and transfer-cost estimates."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation") or "portfolio_analysis"
        dispatch = {
            "portfolio_analysis": self._portfolio_analysis,
            "recovery_plan": self._recovery_plan,
            "warehouse_impact": self._warehouse_impact,
            "financial_impact": self._financial_impact,
            "execution_timeline": self._execution_timeline,
            "monitoring_plan": self._monitoring_plan,
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
        lines = ["## Inventory Snapshot\n", "> Synthetic pilot snapshot; no live warehouse or ERP data was queried.\n"]
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
        lines = ["## Rebalance Recommendations\n", "> Fixed synthetic snapshot and recommendation only; no inventory movement, reorder, return, or liquidation has occurred.\n"]
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
        lines.append("\n### Portfolio Classification\n")
        lines.append("| SKU | Velocity | Strategic Value | Lifecycle Risk | Review Option |")
        lines.append("|-----|----------|-----------------|----------------|---------------|")
        for sku, profile in PORTFOLIO_CLASSIFICATIONS.items():
            if profile["velocity"] == "SLOW-MOVING" and profile["lifecycle_risk"] == "ELEVATED":
                option = "Validate demand; review vendor-return or controlled disposition eligibility"
            elif profile["velocity"] == "SLOW-MOVING":
                option = "Review transfer, reorder pause, and safety-stock settings"
            else:
                option = "Monitor against forecast and fixed reorder policy"
            lines.append(
                f"| {sku} | {profile['velocity']} | {profile['strategic_value']} | "
                f"{profile['lifecycle_risk']} | {option} |"
            )
        lines.append("**Recommendation:** Review the proposed transfer plan with inventory and warehouse owners before any movement.")
        lines.append("No SKU is declared obsolete without an authorized lifecycle decision and source-system evidence.")
        return "\n".join(lines)

    def _transfer_plan(self, **kwargs) -> str:
        transfers = _build_imbalances()
        lines = ["## Proposed Transfer Plan\n", "> Synthetic planning output only. No inventory has been reserved, picked, shipped, or moved.\n"]
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
        lines.append(f"**Synthetic planning assumption:** 2-5 business days (ground freight)")
        lines.append(
            "\n### Expected Post-Transfer Utilization\n"
        )
        lines.append("| Warehouse | Current Util | Projected Util |")
        lines.append("|-----------|-------------|----------------|")
        for wh_id, wh in WAREHOUSES.items():
            cur = _utilization_pct(wh_id)
            # Rough projection: assume net transfer effect
            net = sum(q for _, src, dst, q, _ in transfers if dst == wh_id) - sum(
                q for _, src, dst, q, _ in transfers if src == wh_id
            )
            # This is a simplified model
            proj_pallets = wh["used_pallets"] + int(net * 0.02)  # rough pallet factor
            proj = round(proj_pallets / wh["capacity_pallets"] * 100, 1)
            lines.append(f"| {wh['name']} | {cur}% | {proj}% |")
        return "\n".join(lines)

    def _cost_analysis(self, **kwargs) -> str:
        lines = ["## Inventory Holding & Transfer Cost Analysis\n", "> All figures are synthetic planning estimates, not customer outcomes.\n"]

        lines.append("### Annual Holding Costs\n")
        lines.append(f"Holding cost = inventory value x {PORTFOLIO['holding_cost_rate_pct']}% per year.\n")
        lines.append("| Warehouse | Inventory Value | Annual Holding Cost |")
        lines.append("|-----------|-----------------|---------------------|")
        total_holding = 0.0
        for wh_id, wh in WAREHOUSES.items():
            hc = _annual_holding_cost(wh_id)
            total_holding += hc
            lines.append(
                f"| {wh['name']} | ${_total_inventory_value(wh_id):,.2f} | ${hc:,.2f} |"
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
        lines.append(f"- Value at risk below reorder point: **${total_risk:,.2f}**")
        lines.append(f"- Total annual holding cost: **${total_holding:,.2f}**")
        lines.append("- Trade-off: a one-time transfer cost far below the value at risk favors reviewing the transfers first.")
        lines.append("\nNo reorder, transfer, vendor return, liquidation, or inventory-policy change is executed by this agent.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Portfolio optimization story (the demo path)
    # ------------------------------------------------------------------
    def _portfolio_analysis(self, **kwargs) -> str:
        p = PORTFOLIO
        slow = p["total_value"] * p["slow_moving_pct"] // 100
        holding = p["total_value"] * p["holding_cost_rate_pct"] / 100
        rows = "\n".join(f"| {b['category']} | {_k(b['value'])} | {b['action']} |" for b in SLOW_MOVING)
        return (
            "## Inventory Optimization: Current State Analysis\n\n"
            f"Analyzing ${p['total_value'] / 1_000_000:.1f}M across all SKUs for movement velocity and strategic value.\n\n"
            "| Measure | Value |\n|---|---|\n"
            f"| Total inventory | ${p['total_value'] / 1_000_000:.1f}M |\n"
            f"| Slow-moving ({p['slow_moving_pct']}%) | ${slow / 1_000_000:.1f}M tied up |\n"
            f"| Warehouse utilization | {p['utilization_pct']}% (critical) |\n"
            f"| Annual holding cost | {_k(int(holding))} ({p['holding_cost_rate_pct']}%) |\n\n"
            "### Slow-Moving Breakdown\n\n"
            f"| Category | Value | Recommended action |\n|---|---|---|\n{rows}\n"
            f"| **Total slow-moving** | **{_m(sum(b['value'] for b in SLOW_MOVING))}** | |\n\n"
            "Source: [Synthetic D365 Inventory + WMS snapshot]\n\n"
            "**Next step:** Shall I create the recovery plan?\n\n"
            f"{_GATE}"
        )

    def _recovery_plan(self, **kwargs) -> str:
        parts = ["## Inventory Recovery Plan - 90 Days\n"]
        for phase in RECOVERY_PLAN:
            parts.append(f"### {phase['phase']}\n")
            parts.append("| Action | Effect | Cash / Capital |\n|---|---|---|")
            for action, effect, amount in phase["items"]:
                parts.append(f"| {action} | {effect} | {_k(amount) if amount else '-'} |")
            subtotal = sum(a for _, _, a in phase["items"])
            parts.append(f"| **Phase total** | | **{_k(subtotal)}** |\n")
        total = _recovery_total()
        parts.append(f"**Total Cash Recovery: ${total / 1_000_000:.1f}M in 90 days** "
                     f"(working capital freed across {len(RECOVERY_PLAN)} phases).\n")
        parts.append("Source: [Synthetic historical sales + D365 snapshot]\n")
        parts.append("This is a recommended plan for your review; every sale, return and write-off needs an authorized owner.\n")
        parts.append("**Next step:** Want to see the warehouse impact?\n")
        parts.append(_GATE)
        return "\n".join(parts)

    def _warehouse_impact(self, **kwargs) -> str:
        current = PORTFOLIO["utilization_pct"]
        freed = sum(c - a for _, c, a in SPACE_BY_CATEGORY)
        new = current - freed
        rows = "\n".join(f"| {name} | {c}% | {a}% | {c - a}% |" for name, c, a in SPACE_BY_CATEGORY)
        benefits = "\n".join(f"- {b}" for b in WAREHOUSE_BENEFITS)
        return (
            "## Warehouse Space Recovery\n\n"
            f"**Current Utilization:** {current}% (Critical - operations impaired)\n\n"
            "### Space by Category\n\n"
            "| Category | Current | After Optimization | Freed |\n|---|---|---|---|\n"
            f"{rows}\n| **Total** | | | **{freed}%** |\n\n"
            f"**New Utilization:** {new}% (Optimal operational range)\n\n"
            f"### Benefits\n\n{benefits}\n\n"
            f"**Capacity for Growth:** Room for ${GROWTH_CAPACITY / 1_000_000:.1f}M additional inventory\n\n"
            "Source: [Synthetic WMS + Facility Management snapshot]\n\n"
            "**Next step:** Shall I show the financial impact?\n\n"
            f"{_GATE}"
        )

    def _financial_impact(self, **kwargs) -> str:
        p = PORTFOLIO
        freed = _recovery_total()
        pct = freed * 100 // p["total_value"]
        capital_benefit = freed * p["cost_of_capital_pct"] // 100
        annual = sum(v for _, v in ANNUAL_SAVINGS)
        three_year = annual * 3
        value = three_year + freed
        roi = round((value - IMPLEMENTATION_COST) * 100 / IMPLEMENTATION_COST)
        rows = "\n".join(f"| {name} | {_k(v)} |" for name, v in ANNUAL_SAVINGS)
        return (
            "## Financial Impact Analysis\n\n"
            "### Working Capital Recovery\n\n"
            f"- Cash freed: ${freed / 1_000_000:.1f}M ({pct}% of total inventory)\n"
            "- Available for: Operations, growth, debt reduction\n"
            f"- Cost of capital: {p['cost_of_capital_pct']}% = {_k(capital_benefit)} annual benefit\n\n"
            "### Annual Cost Savings\n\n"
            f"| Category | Annual Savings |\n|---|---|\n{rows}\n"
            f"| **Total Annual Savings** | **{_k(annual)}** |\n\n"
            f"**3-Year Value:** ${three_year / 1_000_000:.2f}M + ${freed / 1_000_000:.1f}M working capital = "
            f"${value / 1_000_000:.2f}M\n\n"
            f"**Implementation Cost:** {_k(IMPLEMENTATION_COST)} (software + consulting)  "
            f"**Net ROI:** {roi:,}% over 3 years\n\n"
            "Source: [Synthetic financial analysis + industry benchmarks]; planning estimates, not customer outcomes.\n\n"
            "**Next step:** Ready to see the execution timeline?\n\n"
            f"{_GATE}"
        )

    def _execution_timeline(self, **kwargs) -> str:
        parts = ["## 90-Day Execution Timeline\n"]
        running = 0
        for w in CASH_SCHEDULE:
            amount = sum(v for _, v in w["cash"])
            running += amount
            parts.append(f"### {w['window']}\n")
            parts.extend(f"- {a}" for a in w["actions"])
            parts.append(f"- **{w['label']}: {_k(amount)}** ("
                         + "; ".join(f"{n} {_k(v)}" for n, v in w["cash"]) + ")\n")
        parts.append("### Milestones\n")
        parts.extend(f"- {day}: {goal}" for day, goal in MILESTONES)
        parts.append(f"\nCumulative by Day 90: {_m(running)}.\n")
        parts.append("Source: [Synthetic project plan + D365 snapshot]\n")
        parts.append("Ready for you to share with stakeholders in Microsoft Teams; the agent does not post it.\n")
        parts.append("**Next step:** Want to see ongoing monitoring?\n")
        parts.append(_GATE)
        return "\n".join(parts)

    def _monitoring_plan(self, **kwargs) -> str:
        parts = ["## Continuous Inventory Optimization\n"]
        for section, items in MONITORING_PLAN.items():
            parts.append(f"### {section}\n")
            parts.extend(f"- {i}" for i in items)
            parts.append("")
        parts.append("### Success Metrics\n")
        parts.append("| Metric | Target |\n|---|---|")
        parts.extend(f"| {m} | {t} |" for m, t in SUCCESS_METRICS)
        parts.append("\nSource: [Synthetic Power BI + D365 + Azure AI design]\n")
        parts.append(_GATE)
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = InventoryRebalancingAgent()
    for op in ["portfolio_analysis", "recovery_plan", "warehouse_impact", "financial_impact",
               "execution_timeline", "monitoring_plan"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
