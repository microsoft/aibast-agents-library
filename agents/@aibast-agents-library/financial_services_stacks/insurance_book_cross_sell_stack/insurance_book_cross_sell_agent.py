"""
Book of Business Cross-Sell Agent

Turns a broker's book of business (an expiration list) into a routed cross-sell
plan for a multi-unit commercial insurer: profile the book, classify every line,
match each line to the underwriting units with appetite, draft the unit and broker
confirmations, and lay out the routing plan with renewal follow-up dates.

Where a real deployment would read the broker's emailed expiration list, the
carrier's appetite guide and a CRM pipeline, this agent uses a fixed synthetic
snapshot so it runs anywhere without credentials. It never sends, routes, quotes
or binds anything: every outreach and routing step is a draft for a person.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/insurance-book-cross-sell",
    "version": "1.0.0",
    "display_name": "Book of Business Cross-Sell Agent",
    "description": "Turn a broker's book of business into a confirmed, routed cross-sell plan: classify every line, match it to the underwriting units with appetite, find the white space, and draft the unit and broker confirmations before anything reaches a seller's pipeline.",
    "author": "AIBAST",
    "tags": ["insurance", "cross-sell", "book-of-business", "appetite", "broker", "commercial-lines"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot; every name and value is invented)
# ═══════════════════════════════════════════════════════════════

_CARRIER = "Northwind Mutual"
_BROKER = "Fabrikam Insurance Brokers"
_BROKER_CONTACT = "Priya Natarajan"
_AS_OF = "2026-10-05"
_FOLLOW_UP_LEAD_DAYS = 60

# Underwriting units: the lines each unit writes and the states where the unit is unavailable.
_UNITS = {
    "property": {"name": "Northwind Property", "contact": "Marcus Lee",
                 "lines": ["Property"], "unavailable": []},
    "casualty": {"name": "Northwind Casualty", "contact": "Elena Ruiz",
                 "lines": ["General Liability", "Workers Compensation", "Commercial Auto"], "unavailable": []},
    "surety": {"name": "Northwind Surety", "contact": "Tom Becker",
               "lines": ["Surety Bond"], "unavailable": []},
    "professional": {"name": "Northwind Professional", "contact": "Grace Okafor",
                     "lines": ["Professional Liability"], "unavailable": []},
    "marine": {"name": "Northwind Inland Marine", "contact": "Sam Patel",
               "lines": ["Inland Marine"], "unavailable": ["AZ"]},
}
_UNIT_ORDER = ["property", "casualty", "surety", "professional", "marine"]

_CLASSES = {
    "IC-2381": "Framing and structural contractors",
    "IC-2373": "Paving and road contractors",
    "IC-3118": "Commercial bakeries",
    "IC-4841": "General freight trucking",
    "IC-4931": "Warehousing and storage",
    "IC-6212": "Dental practices",
}
# Appetite guide: the lines of business the carrier wants for each industry class.
_APPETITE = {
    "IC-2381": ["General Liability", "Workers Compensation", "Surety Bond"],
    "IC-2373": ["General Liability", "Workers Compensation", "Surety Bond", "Inland Marine"],
    "IC-3118": ["Property", "General Liability"],
    "IC-4841": ["Commercial Auto", "Inland Marine"],
    "IC-4931": ["Property", "General Liability"],
    "IC-6212": ["Professional Liability", "Property"],
}
# Legacy class codes that some agency systems still export, and keyword rules for free-text descriptions.
_LEGACY_CROSSWALK = {"L-2051": "IC-3118", "L-4225": "IC-4931"}
_KEYWORDS = [("trucking", "IC-4841"), ("paving", "IC-2373")]

# The broker's book of business: one row per policy line.
_BOOK = [
    {"line_id": "BK-01", "account": "Alder Creek Framing", "state": "CO", "class_code": "IC-2381", "legacy_code": "", "description": "Framing contractor",
     "line": "General Liability", "carrier": "Other market", "expires": "2026-12-15", "premium": 48000},
    {"line_id": "BK-02", "account": "Alder Creek Framing", "state": "CO", "class_code": "IC-2381", "legacy_code": "", "description": "Framing contractor",
     "line": "Workers Compensation", "carrier": "Other market", "expires": "2026-12-15", "premium": 62000},
    {"line_id": "BK-03", "account": "Bluebird Bakery Co", "state": "OR", "class_code": "", "legacy_code": "L-2051", "description": "Wholesale bakery",
     "line": "Property", "carrier": "Northwind Mutual", "expires": "2027-01-10", "premium": 21000},
    {"line_id": "BK-04", "account": "Cedar Point Logistics", "state": "TX", "class_code": "", "legacy_code": "", "description": "Regional trucking fleet",
     "line": "Commercial Auto", "carrier": "Other market", "expires": "2026-11-30", "premium": 95000},
    {"line_id": "BK-05", "account": "Cedar Point Logistics", "state": "TX", "class_code": "", "legacy_code": "", "description": "Regional trucking fleet",
     "line": "Inland Marine", "carrier": "Other market", "expires": "2026-11-30", "premium": 18000},
    {"line_id": "BK-06", "account": "Driftwood Dental Group", "state": "WA", "class_code": "IC-6212", "legacy_code": "", "description": "Dental group practice",
     "line": "Professional Liability", "carrier": "Other market", "expires": "2027-02-01", "premium": 14000},
    {"line_id": "BK-07", "account": "Elmstone Paving", "state": "AZ", "class_code": "", "legacy_code": "", "description": "Asphalt paving contractor",
     "line": "General Liability", "carrier": "Northwind Mutual", "expires": "2026-12-31", "premium": 41000},
    {"line_id": "BK-08", "account": "Elmstone Paving", "state": "AZ", "class_code": "", "legacy_code": "", "description": "Asphalt paving contractor",
     "line": "Surety Bond", "carrier": "Other market", "expires": "2026-12-31", "premium": 30000},
    {"line_id": "BK-09", "account": "Foxglove Studio", "state": "CA", "class_code": "", "legacy_code": "", "description": "Creative services",
     "line": "General Liability", "carrier": "Other market", "expires": "2027-01-15", "premium": 7000},
    {"line_id": "BK-10", "account": "Granite Ridge Storage", "state": "NV", "class_code": "", "legacy_code": "L-4225", "description": "Self storage facilities",
     "line": "Property", "carrier": "Other market", "expires": "2027-01-20", "premium": 27000},
]

# Replies recorded in the fixed snapshot after the confirmation drafts went out (used by routing_plan).
_UNIT_PASSES = [("surety", "Elmstone Paving", "bond capacity for paving is full this quarter")]
_BROKER_DROPS = [("Granite Ridge Storage", "renewed early with its current market")]

_GATE = (
    "Synthetic decision support only. This agent does not send outreach, route records "
    "into a pipeline, quote, bind, or make an underwriting decision; every draft waits "
    "for a person to review and send it."
)
_SOURCE = "Source: [Synthetic Book of Business + Appetite Guide Snapshot]\nAgents: BookCrossSellAgent"


# ═══════════════════════════════════════════════════════════════
# HELPERS (plain dicts, lists and arithmetic)
# ═══════════════════════════════════════════════════════════════

def _money(v):
    return f"${v:,.0f}"


def _classify(row):
    """Explicit class wins, then the legacy crosswalk, then a keyword rule; otherwise unresolved."""
    if row["class_code"]:
        return row["class_code"], "Explicit class on the book"
    if row["legacy_code"] in _LEGACY_CROSSWALK:
        return _LEGACY_CROSSWALK[row["legacy_code"]], f"Legacy code {row['legacy_code']} crosswalk"
    text = row["description"].lower()
    for word, code in _KEYWORDS:
        if word in text:
            return code, f"Keyword '{word}' in description"
    return "", "Unresolved: ask the broker"


def _accounts():
    out = []
    for row in _BOOK:
        if row["account"] not in out:
            out.append(row["account"])
    return out


def _unit_for_line(line):
    for key in _UNIT_ORDER:
        if line in _UNITS[key]["lines"]:
            return key
    return None


def _follow_up(expires):
    """Follow-up date = expiration minus the lead days; inside the window already means 'Now'."""
    import datetime
    y, m, d = (int(p) for p in expires.split("-"))
    f = datetime.date(y, m, d) - datetime.timedelta(days=_FOLLOW_UP_LEAD_DAYS)
    return f.isoformat() if f.isoformat() > _AS_OF else f"Now (window opened {f.isoformat()})"


def _match():
    """Per account: incumbent lines, competing-market lines (rewrite at renewal), white space, state blocks, holds."""
    results = []
    for account in _accounts():
        rows = [r for r in _BOOK if r["account"] == account]
        code, basis = _classify(rows[0])
        state = rows[0]["state"]
        entry = {"account": account, "state": state, "class": code, "basis": basis,
                 "competing": [], "incumbent": [], "white_space": [], "blocked": [], "held": ""}
        if not code:
            entry["held"] = "Needs class from broker"
            results.append(entry)
            continue
        on_book = [r["line"] for r in rows]
        for r in rows:
            key = _unit_for_line(r["line"])
            if r["carrier"] == _CARRIER:
                entry["incumbent"].append(r)
            elif r["line"] in _APPETITE[code] and state not in _UNITS[key]["unavailable"]:
                entry["competing"].append(dict(r, unit=key))
        for line in _APPETITE[code]:
            if line in on_book:
                continue
            key = _unit_for_line(line)
            if state in _UNITS[key]["unavailable"]:
                entry["blocked"].append(f"{line} ({_UNITS[key]['name']} unavailable in {state})")
            else:
                entry["white_space"].append({"unit": key, "line": line, "expires": rows[0]["expires"]})
        results.append(entry)
    return results


def _shortlist():
    """Per unit: (account, opportunity, expires, premium-or-blank)."""
    by_unit = {k: [] for k in _UNIT_ORDER}
    for e in _match():
        for r in e["competing"]:
            by_unit[r["unit"]].append((e["account"], f"{r['line']} at renewal", r["expires"], r["premium"]))
        for w in e["white_space"]:
            by_unit[w["unit"]].append((e["account"], f"{w['line']} (new line)", w["expires"], 0))
    return by_unit


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "book_summary", "classify_lines", "appetite_match",
    "unit_confirmation", "broker_confirmation", "routing_plan",
]
_UNIT_CHOICES = ["all"] + _UNIT_ORDER


class BookCrossSellAgent(BasicAgent):
    """
    Broker book-of-business cross-sell assistant.

    Operations:
        book_summary        - profile the broker's book: accounts, lines, premium, renewal window
        classify_lines      - resolve an industry class for every line; flag what needs the broker
        appetite_match      - match lines to units with appetite: competing, incumbent, white space
        unit_confirmation   - per-unit shortlist and a draft appetite-confirmation note (never sent)
        broker_confirmation - draft note asking the broker to confirm the shortlist (never sent)
        routing_plan        - routing plan with renewal follow-up dates after recorded replies (draft)
    """

    def __init__(self):
        self.name = "BookCrossSellAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Cross-sell assistant for a commercial insurer reviewing a broker's book of business "
                "(the Fabrikam Insurance Brokers expiration list in a fixed synthetic snapshot). Always "
                "use this tool, with its demo defaults, for: what is in the book or broker's expiration "
                "list (book_summary); finding or fixing industry classes for the lines (classify_lines); "
                "which accounts fit our appetite, where the white space is, or what we can cross-sell "
                "(appetite_match); asking the underwriting units to confirm appetite or showing a unit's "
                "shortlist (unit_confirmation, optional unit); going back to the broker to confirm the "
                "shortlist (broker_confirmation); and routing the opportunities to sellers with follow-up "
                "dates (routing_plan). It returns drafts only; it never sends, routes, quotes or binds."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "book_summary for the book or expiration list overview; classify_lines for "
                            "industry classes; appetite_match for appetite fit, white space or cross-sell; "
                            "unit_confirmation to ask the underwriting units; broker_confirmation to go "
                            "back to the broker; routing_plan to route opportunities and set follow-ups."
                        ),
                    },
                    "unit": {
                        "type": "string",
                        "enum": list(_UNIT_CHOICES),
                        "description": "unit_confirmation only: one underwriting unit, or 'all' (default)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "book_summary"
        dispatch = {
            "book_summary": self._book_summary,
            "classify_lines": self._classify_lines,
            "appetite_match": self._appetite_match,
            "unit_confirmation": self._unit_confirmation,
            "broker_confirmation": self._broker_confirmation,
            "routing_plan": self._routing_plan,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}. Available: {', '.join(_OPERATIONS)}.\n\n{_GATE}\n\n{_SOURCE}"
        if op == "unit_confirmation":
            unit = kwargs.get("unit") or "all"
            if unit not in _UNIT_CHOICES:
                return (f"No synthetic underwriting unit matches '{unit}'. Units: "
                        f"{', '.join(_UNIT_CHOICES)}.\n\n{_GATE}\n\n{_SOURCE}")
            return handler(unit)
        return handler()

    # ── book_summary ──────────────────────────────────────────
    def _book_summary(self):
        accounts = _accounts()
        total = sum(r["premium"] for r in _BOOK)
        ours = [r for r in _BOOK if r["carrier"] == _CARRIER]
        rows = "\n".join(
            f"| {r['line_id']} | {r['account']} | {r['state']} | {r['line']} | {r['carrier']} | "
            f"{r['expires']} | {_money(r['premium'])} |" for r in _BOOK)
        return (
            f"**Book of Business: {_BROKER} (as of {_AS_OF})**\n\n"
            f"| Line | Account | State | Line of Business | Current Carrier | Expires | Premium |\n"
            f"|---|---|---|---|---|---|---|\n{rows}\n\n"
            f"**Book at a glance:** {len(accounts)} accounts, {len(_BOOK)} policy lines, "
            f"{_money(total)} total premium. {len(ours)} lines are already with {_CARRIER}; "
            f"{len(_BOOK) - len(ours)} lines ({_money(total - sum(r['premium'] for r in ours))}) "
            f"sit with other markets.\n\n"
            f"**Next step:** classify every line so it can be checked against unit appetite.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── classify_lines ────────────────────────────────────────
    def _classify_lines(self):
        rows, unresolved, counts = [], [], {}
        for account in _accounts():
            first = [r for r in _BOOK if r["account"] == account][0]
            code, basis = _classify(first)
            label = f"{code} {_CLASSES[code]}" if code else "Unresolved"
            rows.append(f"| {account} | {first['description']} | {label} | {basis} |")
            kind = basis.split(" ")[0]
            counts[kind] = counts.get(kind, 0) + 1
            if not code:
                unresolved.append(account)
        resolved = len(rows) - len(unresolved)
        return (
            f"**Industry Class Resolution: {len(rows)} accounts**\n\n"
            f"| Account | Description on Book | Industry Class | Basis |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"**Resolved {resolved} of {len(rows)} accounts:** {counts.get('Explicit', 0)} explicit, "
            f"{counts.get('Legacy', 0)} by legacy crosswalk, {counts.get('Keyword', 0)} by keyword rule.\n"
            f"**Needs the broker:** {', '.join(unresolved)} (class not guessed; held from matching).\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── appetite_match ────────────────────────────────────────
    def _appetite_match(self):
        rows, comp_n, comp_p, ws_n, inc_n = [], 0, 0, 0, 0
        for e in _match():
            if e["held"]:
                rows.append(f"| {e['account']} | Unresolved | - | - | Held: {e['held']} |")
                continue
            comp = "; ".join(f"{r['line']} -> {_UNITS[r['unit']]['name']}" for r in e["competing"]) or "-"
            inc = "; ".join(r["line"] for r in e["incumbent"]) or "-"
            ws = "; ".join(f"{w['line']} -> {_UNITS[w['unit']]['name']}" for w in e["white_space"]) or "-"
            rows.append(f"| {e['account']} | {e['class']} | {inc} | {comp} | {ws} |")
            comp_n += len(e["competing"])
            comp_p += sum(r["premium"] for r in e["competing"])
            ws_n += len(e["white_space"])
            inc_n += len(e["incumbent"])
        blocked = [f"{e['account']}: {b}" for e in _match() for b in e["blocked"]]
        blocked_note = f"**State filter:** {'; '.join(blocked)}.\n" if blocked else ""
        return (
            f"**Appetite Match: {_BROKER} book**\n\n"
            f"| Account | Class | Already With Us | Competing-Market Lines | White Space (new lines) |\n"
            f"|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"**Opportunity:** {comp_n} competing-market lines worth {_money(comp_p)} at renewal, plus "
            f"{ws_n} white-space lines with no current policy; {inc_n} lines are already with us.\n"
            f"{blocked_note}"
            f"**Next step:** ask each underwriting unit to confirm appetite before anything is routed.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── unit_confirmation ─────────────────────────────────────
    def _unit_confirmation(self, unit):
        keys = _UNIT_ORDER if unit == "all" else [unit]
        lists = _shortlist()
        parts, total = [], 0
        for key in keys:
            items = lists[key]
            if not items:
                parts.append(f"**{_UNITS[key]['name']}:** no accounts on this book's shortlist.")
                continue
            total += len(items)
            table = "\n".join(f"| {a} | {o} | {x} | {_money(p) if p else 'New line'} |" for a, o, x, p in items)
            names = ", ".join(sorted(set(a for a, _, _, _ in items)))
            parts.append(
                f"**{_UNITS[key]['name']}** ({len(items)} {'opportunity' if len(items) == 1 else 'opportunities'}, contact {_UNITS[key]['contact']})\n\n"
                f"| Account | Opportunity | Expires | Premium |\n|---|---|---|---|\n{table}\n\n"
                f"> Draft note to {_UNITS[key]['contact']}: \"From the {_BROKER} book, these accounts look "
                f"like a fit for {_UNITS[key]['name']}: {names}. Can you confirm appetite, or tell us which "
                f"to pass on, by Oct 12?\""
            )
        return (
            f"**Unit Appetite Confirmation Drafts - Not Sent**\n\n"
            + "\n\n".join(parts) + "\n\n"
            f"**Shortlist:** {total} opportunities across {len([k for k in keys if lists[k]])} units. "
            f"Status: Draft for your review; nothing is routed until the units reply.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── broker_confirmation ───────────────────────────────────
    def _broker_confirmation(self):
        accounts = [e["account"] for e in _match() if not e["held"] and (e["competing"] or e["white_space"])]
        held = [e["account"] for e in _match() if e["held"]]
        lines = "\n".join(f"| {a} | {', '.join(sorted(set(r['line'] for r in _BOOK if r['account'] == a)))} |" for a in accounts)
        return (
            f"**Broker Confirmation Draft - Not Sent**\n\n"
            f"| Shortlisted Account | Lines on the Book |\n|---|---|\n{lines}\n\n"
            f"> To {_BROKER_CONTACT}, {_BROKER}: \"We reviewed your book and found {len(accounts)} accounts "
            f"we believe {_CARRIER} can help with. Before we involve our units, can you confirm none of "
            f"them are out of business or already placed elsewhere? For {', '.join(held)}, can you tell "
            f"us the type of business so we can classify it?\"\n\n"
            f"**Status:** Draft for your review. Broker replies remove accounts before routing.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── routing_plan ──────────────────────────────────────────
    def _routing_plan(self):
        passes = {(u, a) for u, a, _ in _UNIT_PASSES}
        drops = {a for a, _ in _BROKER_DROPS}
        routed, removed = [], []
        for key in _UNIT_ORDER:
            for a, o, x, p in _shortlist()[key]:
                if a in drops:
                    removed.append(f"| {a} | {o} | Broker: {[r for n, r in _BROKER_DROPS if n == a][0]} |")
                elif (key, a) in passes:
                    removed.append(f"| {a} | {o} | {_UNITS[key]['name']} passed: "
                                   f"{[r for u, n, r in _UNIT_PASSES if (u, n) == (key, a)][0]} |")
                else:
                    routed.append((a, o, _UNITS[key]["name"], _UNITS[key]["contact"], x, _follow_up(x), p))
        routed.sort(key=lambda t: t[4])
        rows = "\n".join(f"| {a} | {o} | {u} | {c} | {x} | {f} |" for a, o, u, c, x, f in [t[:6] for t in routed])
        premium = sum(t[6] for t in routed)
        held = [e["account"] for e in _match() if e["held"]]
        return (
            f"**Cross-Sell Routing Plan - Draft, Not Routed**\n\n"
            f"| Account | Opportunity | Unit | Seller | Expires | Follow-Up By |\n|---|---|---|---|---|---|\n"
            f"{rows}\n\n"
            f"**Removed after replies:**\n\n| Account | Opportunity | Reason |\n|---|---|---|\n"
            + "\n".join(removed) + "\n\n"
            f"**Plan:** {len(routed)} opportunities ready to route ({_money(premium)} competing-market "
            f"premium plus new lines); follow-up is set {_FOLLOW_UP_LEAD_DAYS} days before each "
            f"expiration. Still held: {', '.join(held)} (needs class from broker).\n"
            f"**Next step:** a person approves the plan and creates the pipeline records.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = BookCrossSellAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
