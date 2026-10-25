"""
Staffing Territory Planning Agent

Territory planning assistant for a staffing firm's regional sales leader:
territory snapshot, market sizing, coverage gaps, competitive position, labor
trends and a draft quarterly territory plan.

Where a real deployment would read CRM accounts, placement history and labor
market feeds, this agent uses a fixed synthetic snapshot so it runs anywhere
without credentials. It never changes headcount, quotas, account assignments or
CRM records: it returns analysis and a draft plan for sales leadership to decide.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/staffing-territory-planning",
    "version": "1.0.0",
    "display_name": "Staffing Territory Planning Agent",
    "description": "Help staffing sales leaders size their territory, find where demand outruns recruiter coverage, read the competition and labor trends, and walk into the quarter with a draft plan grounded in the numbers.",
    "author": "AIBAST",
    "tags": ["professional-services", "staffing", "territory-planning", "market-sizing", "sales-planning"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot, Q3 planning cycle)
# ═══════════════════════════════════════════════════════════════

_FIRM = "Contoso Staffing"
_TERRITORY = "North Valley territory"
_LEADER = "Dana Whitfield, regional sales director"
_SNAPSHOT = "trailing 12 months to June 30"

_LINES = ["Light Industrial", "Office and Admin", "IT and Engineering", "Healthcare Support"]

# Annual addressable temporary-labor spend and our revenue, in $ millions, per metro and service line.
_METROS = {
    "Harbor City": {
        "addressable": [48.0, 22.0, 31.0, 14.0], "ours": [6.2, 2.9, 1.1, 0.4],
        "recruiters": 9, "clients": 64,
    },
    "Millbrook": {
        "addressable": [26.0, 9.0, 6.0, 11.0], "ours": [4.1, 1.2, 0.0, 0.9],
        "recruiters": 5, "clients": 38,
    },
    "Granite Ridge": {
        "addressable": [18.0, 7.0, 12.0, 9.0], "ours": [0.8, 0.6, 0.0, 0.0],
        "recruiters": 1, "clients": 9,
    },
    "Ashford Junction": {
        "addressable": [14.0, 5.0, 3.0, 6.0], "ours": [2.0, 0.7, 0.0, 0.5],
        "recruiters": 2, "clients": 17,
    },
}

# Competitor share of addressable spend, per metro (fictional firms).
_COMPETITORS = {
    "Fabrikam Workforce": {"Harbor City": 0.18, "Millbrook": 0.12, "Granite Ridge": 0.21, "Ashford Junction": 0.09},
    "Northwind Staffing": {"Harbor City": 0.11, "Millbrook": 0.15, "Granite Ridge": 0.06, "Ashford Junction": 0.14},
    "Litware Talent": {"Harbor City": 0.07, "Millbrook": 0.04, "Granite Ridge": 0.17, "Ashford Junction": 0.03},
}

# Labor trends per service line (synthetic market feed).
_TRENDS = {
    "Light Industrial": {"postings_yoy": 6, "wage_yoy": 4.2, "time_to_fill": 9},
    "Office and Admin": {"postings_yoy": -3, "wage_yoy": 2.1, "time_to_fill": 12},
    "IT and Engineering": {"postings_yoy": 11, "wage_yoy": 5.8, "time_to_fill": 31},
    "Healthcare Support": {"postings_yoy": 8, "wage_yoy": 4.9, "time_to_fill": 18},
}

_GAP_SHARE = 0.05          # a line is a coverage gap when our share is under 5%...
_GAP_MIN_SPEND = 9.0       # ...of at least $9.0M addressable spend
_METRO_KEYS = ["all"] + list(_METROS)

_GATE = (
    "Synthetic planning snapshot only. This agent does not change headcount, quotas, "
    "account assignments or CRM records; the plan is a draft for sales leadership to decide."
)
_SOURCE = "Source: [Synthetic Territory + Labor Market Snapshot]\nAgents: StaffingTerritoryPlanningAgent"


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _m(x):
    return f"${x:,.1f}M"


def _pct(x):
    return f"{x * 100:.1f}%"


def _metro_totals(name):
    m = _METROS[name]
    return round(sum(m["addressable"]), 1), round(sum(m["ours"]), 1)


def _territory_totals():
    addr = round(sum(sum(m["addressable"]) for m in _METROS.values()), 1)
    ours = round(sum(sum(m["ours"]) for m in _METROS.values()), 1)
    recruiters = sum(m["recruiters"] for m in _METROS.values())
    clients = sum(m["clients"] for m in _METROS.values())
    return addr, ours, recruiters, clients


def _gaps():
    """(metro, line, addressable, ours, share, open_spend) for every gap, largest open spend first."""
    out = []
    for name, m in _METROS.items():
        for i, line in enumerate(_LINES):
            a, o = m["addressable"][i], m["ours"][i]
            share = o / a
            if a >= _GAP_MIN_SPEND and share < _GAP_SHARE:
                out.append((name, line, a, o, share, round(a - o, 1)))
    out.sort(key=lambda g: -g[5])
    return out


def _resolve_metro(metro):
    if not metro:
        return "all"
    q = str(metro).strip().lower()
    if q in ("all", "territory", "north valley", "north valley territory"):
        return "all"
    for name in _METROS:
        if name.lower() in q or q in name.lower():
            return name
    return None


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "territory_snapshot", "market_sizing", "coverage_gaps",
    "competitive_landscape", "labor_trends", "territory_plan",
]


class StaffingTerritoryPlanningAgent(BasicAgent):
    """
    Staffing territory planning assistant.

    Operations:
        territory_snapshot     - territory at a glance: spend, revenue, share, recruiters, clients per metro
        market_sizing          - addressable spend by service line for the territory or one metro
        coverage_gaps          - lines where demand outruns our share and recruiter coverage
        competitive_landscape  - fictional competitor share and our rank per metro
        labor_trends           - postings, wage and time-to-fill trends by service line
        territory_plan         - draft quarterly plan: opportunities, risks, recommendations, priority action
    """

    def __init__(self):
        self.name = "StaffingTerritoryPlanningAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Territory planning desk for the fictional Contoso Staffing North Valley territory "
                "(metros Harbor City, Millbrook, Granite Ridge, Ashford Junction). Always use this tool "
                "for territory, market, coverage, competitor, labor-trend and territory-plan questions. "
                "Routing: snapshot or 'how does my territory look' -> territory_snapshot; 'how big is "
                "the market' (optionally for one metro) -> market_sizing; 'where are our gaps' -> "
                "coverage_gaps; 'who are we up against' -> competitive_landscape; labor or hiring "
                "trends -> labor_trends; 'draft my quarterly/territory plan' -> territory_plan. Every "
                "operation has a demo default, so call it right away. Never changes headcount, quotas, "
                "account assignments or CRM records."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "territory_snapshot for the overview; market_sizing for addressable "
                            "spend; coverage_gaps for under-served lines; competitive_landscape for "
                            "competitors; labor_trends for market trends; territory_plan for the "
                            "draft quarterly plan."
                        ),
                    },
                    "metro": {
                        "type": "string",
                        "enum": list(_METRO_KEYS),
                        "description": "Metro for market_sizing: 'all' (default) or one of Harbor City, Millbrook, Granite Ridge, Ashford Junction",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "territory_snapshot"
        dispatch = {
            "territory_snapshot": self._territory_snapshot,
            "coverage_gaps": self._coverage_gaps,
            "competitive_landscape": self._competitive_landscape,
            "labor_trends": self._labor_trends,
            "territory_plan": self._territory_plan,
        }
        if op == "market_sizing":
            metro = _resolve_metro(kwargs.get("metro"))
            if metro is None:
                return (
                    f"No metro named '{kwargs.get('metro')}' is in the {_TERRITORY}. "
                    f"Metros: {', '.join(_METROS)}.\n\n{_GATE}\n\n{_SOURCE}"
                )
            return self._market_sizing(metro)
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}. Available: {', '.join(_OPERATIONS)}."
        return handler()

    # ── territory_snapshot ────────────────────────────────────
    def _territory_snapshot(self):
        addr, ours, rec, cli = _territory_totals()
        rows = []
        for name, m in _METROS.items():
            a, o = _metro_totals(name)
            rows.append(
                f"| {name} | {_m(a)} | {_m(o)} | {_pct(o / a)} | {m['recruiters']} | "
                f"{_m(round(a / m['recruiters'], 1))} | {m['clients']} |"
            )
        return (
            f"**Territory Snapshot: {_FIRM} {_TERRITORY}**\n\n"
            f"Prepared for {_LEADER} | Data: {_SNAPSHOT}\n\n"
            f"| Metro | Addressable spend | Our revenue | Our share | Recruiters | Spend per recruiter | Active clients |\n"
            f"|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n"
            f"| **Territory** | **{_m(addr)}** | **{_m(ours)}** | **{_pct(ours / addr)}** | **{rec}** | "
            f"**{_m(round(addr / rec, 1))}** | **{cli}** |\n\n"
            f"**Read:** Granite Ridge carries {_m(46.0)} of spend with 1 recruiter, more than three times "
            f"the territory's spend per recruiter.\n\n"
            f"**Next step:** size the Granite Ridge market, then review coverage gaps.\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── market_sizing ─────────────────────────────────────────
    def _market_sizing(self, metro):
        if metro == "all":
            addr_by_line = [round(sum(m["addressable"][i] for m in _METROS.values()), 1) for i in range(4)]
            ours_by_line = [round(sum(m["ours"][i] for m in _METROS.values()), 1) for i in range(4)]
            title = _TERRITORY
        else:
            addr_by_line, ours_by_line = _METROS[metro]["addressable"], _METROS[metro]["ours"]
            title = metro
        a_tot, o_tot = round(sum(addr_by_line), 1), round(sum(ours_by_line), 1)
        rows = "\n".join(
            f"| {line} | {_m(addr_by_line[i])} | {_m(ours_by_line[i])} | {_pct(ours_by_line[i] / addr_by_line[i])} | "
            f"{_m(round(addr_by_line[i] - ours_by_line[i], 1))} |"
            for i, line in enumerate(_LINES)
        )
        big = max(range(4), key=lambda i: addr_by_line[i] - ours_by_line[i])
        return (
            f"**Market Sizing: {title}**\n\n"
            f"| Service line | Addressable spend | Our revenue | Our share | Open spend |\n|---|---|---|---|---|\n"
            f"{rows}\n"
            f"| **Total** | **{_m(a_tot)}** | **{_m(o_tot)}** | **{_pct(o_tot / a_tot)}** | **{_m(round(a_tot - o_tot, 1))}** |\n\n"
            f"**Largest open spend:** {_LINES[big]} ({_m(round(addr_by_line[big] - ours_by_line[big], 1))}).\n\n"
            f"Addressable spend is the synthetic annual temporary-labor spend; open spend is addressable "
            f"spend not yet won by {_FIRM}.\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── coverage_gaps ─────────────────────────────────────────
    def _coverage_gaps(self):
        gaps = _gaps()
        rows = "\n".join(
            f"| {i + 1} | {g[0]} | {g[1]} | {_m(g[2])} | {_m(g[3])} | {_pct(g[4])} | {_m(g[5])} |"
            for i, g in enumerate(gaps)
        )
        open_total = round(sum(g[5] for g in gaps), 1)
        return (
            f"**Coverage Gaps: {_TERRITORY}**\n\n"
            f"Rule: a service line with at least {_m(_GAP_MIN_SPEND)} addressable spend where our share is under 5%.\n\n"
            f"| Rank | Metro | Service line | Addressable | Our revenue | Our share | Open spend |\n"
            f"|---|---|---|---|---|---|---|\n{rows}\n\n"
            f"**{len(gaps)} gaps, {_m(open_total)} open spend.** The two largest are IT and Engineering in "
            f"Harbor City and Light Industrial in Granite Ridge.\n\n"
            f"**Next step:** check who holds these markets today before deciding where to add recruiters.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── competitive_landscape ─────────────────────────────────
    def _competitive_landscape(self):
        rows = []
        for name in _METROS:
            a, o = _metro_totals(name)
            shares = [(c, s[name]) for c, s in _COMPETITORS.items()] + [(_FIRM, round(o / a, 3))]
            shares.sort(key=lambda x: -x[1])
            rank = [c for c, _ in shares].index(_FIRM) + 1
            leader = shares[0]
            rows.append(
                f"| {name} | {leader[0]} ({_pct(leader[1])}) | {_pct(o / a)} | {rank} of {len(shares)} |"
            )
        return (
            f"**Competitive Landscape: {_TERRITORY}**\n\n"
            f"| Metro | Share leader | {_FIRM} share | Our rank |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"**Competitor profiles (synthetic):**\n"
            f"- Fabrikam Workforce: volume light-industrial player; leads Harbor City and Granite Ridge.\n"
            f"- Northwind Staffing: strongest in Millbrook and Ashford Junction office and admin.\n"
            f"- Litware Talent: IT and engineering specialist; 17.0% of Granite Ridge.\n\n"
            f"**Read:** we rank last in Granite Ridge, where Litware Talent's IT focus meets our zero IT revenue.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── labor_trends ──────────────────────────────────────────
    def _labor_trends(self):
        rows = "\n".join(
            f"| {line} | {t['postings_yoy']:+d}% | {t['wage_yoy']:+.1f}% | {t['time_to_fill']} days |"
            for line, t in _TRENDS.items()
        )
        return (
            f"**Labor Trends: {_TERRITORY}**\n\n"
            f"| Service line | Job postings (YoY) | Median wage (YoY) | Time to fill |\n|---|---|---|---|\n"
            f"{rows}\n\n"
            f"**Read:** IT and Engineering postings are up 11% with a 31-day time to fill, the slowest "
            f"fill and fastest growth; Office and Admin postings are down 3%.\n\n"
            f"**Planning implication:** recruiter capacity for IT and Engineering is the constraint; "
            f"bill rates should reflect the 5.8% wage movement.\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── territory_plan ────────────────────────────────────────
    def _territory_plan(self):
        gaps = _gaps()[:3]
        addr, ours, rec, _cli = _territory_totals()
        opps = "\n".join(
            f"{i + 1}. {g[0]} {g[1]}: {_m(g[5])} open spend at {_pct(g[4])} share." for i, g in enumerate(gaps)
        )
        return (
            f"**Draft Quarterly Territory Plan: {_TERRITORY}** (draft for sales leadership review)\n\n"
            f"**Territory snapshot:** {_m(addr)} addressable spend, {_m(ours)} our revenue "
            f"({_pct(ours / addr)} share), {rec} recruiters.\n\n"
            f"**Top 3 opportunities:**\n{opps}\n\n"
            f"**Top 2 risks:**\n"
            f"1. Granite Ridge has 1 recruiter for {_m(46.0)} of spend; Fabrikam Workforce and Litware Talent hold 38.0% of it.\n"
            f"2. Office and Admin postings are down 3%; Harbor City office revenue ({_m(2.9)}) is exposed.\n\n"
            f"**3 recommendations:**\n"
            f"1. Add 2 IT and Engineering recruiters split across Harbor City and Granite Ridge (31-day time to fill).\n"
            f"2. Move 1 light-industrial recruiter from Harbor City to Granite Ridge to work its {_m(17.2)} open spend.\n"
            f"3. Re-price IT and Engineering bill rates for the 5.8% wage movement before Q3 renewals.\n\n"
            f"**Priority action:** approve the 2 IT and Engineering recruiter requisitions this quarter.\n\n"
            f"Status: Draft - no headcount, quota or account change was made.\n\n{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = StaffingTerritoryPlanningAgent()
    story = [
        {"operation": "territory_snapshot"},
        {"operation": "market_sizing", "metro": "Granite Ridge"},
        {"operation": "coverage_gaps"},
        {"operation": "competitive_landscape"},
        {"operation": "labor_trends"},
        {"operation": "territory_plan"},
    ]
    for kw in story:
        print("=" * 60)
        print(agent.perform(**kw))
        print()
