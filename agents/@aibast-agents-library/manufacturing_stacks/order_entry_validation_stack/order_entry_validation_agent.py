"""
Order Entry Validation Agent

Helps a sales operations specialist work the inbound purchase-order queue: read each
customer PO into structured fields, validate it against the accepted quote, check the
product configuration against the configuration rule book, classify the order, and
prepare a draft ERP sales order with every exception listed for a person to resolve.

Where a real deployment would read POs from a shared mailbox, quotes from the CRM and
rules from the product catalog, this agent uses a fixed synthetic snapshot so it runs
anywhere without credentials. It never submits, books or changes an order: the sales
order is a draft a person reviews and enters.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/order-entry-validation",
    "version": "1.0.0",
    "display_name": "Order Entry Validation Agent",
    "description": "Turn inbound customer purchase orders into validated draft sales orders: extract every PO field, check prices and terms against the accepted quote, catch invalid product configurations, classify the order, and hand a specialist a draft with each exception called out before entry.",
    "author": "AIBAST",
    "tags": ["manufacturing", "order-entry", "purchase-order", "quote-validation", "sales-operations", "erp"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot; every name and value is invented)
# ═══════════════════════════════════════════════════════════════

_ORG = "Proseware Instruments"
_AS_OF = "2026-10-05"
_PRICE_TOLERANCE = 0.01   # 1% per-line tolerance against the accepted quote

_PRODUCTS = {
    "PX-300": {"name": "PX-300 portable gas analyzer", "kind": "analyzer"},
    "PX-500": {"name": "PX-500 multi-gas analyzer", "kind": "analyzer"},
    "SH-CO": {"name": "Carbon monoxide sensor head", "kind": "sensor"},
    "SH-H2S": {"name": "Hydrogen sulfide sensor head", "kind": "sensor"},
    "SH-NH3": {"name": "Ammonia sensor head", "kind": "sensor"},
    "KIT-CAL": {"name": "Calibration kit", "kind": "kit"},
    "KIT-SAFE": {"name": "Intrinsic safety kit", "kind": "kit"},
}

# Configuration rule book.
_COMPATIBLE = {"PX-300": ["SH-CO", "SH-NH3"], "PX-500": ["SH-CO", "SH-H2S", "SH-NH3"]}
_MANDATORY_KITS = {"SH-H2S": "KIT-SAFE"}
_REGION_RESTRICTED = {"SH-NH3": "International"}   # sensor not released for that region

# Inbound purchase orders (key = PO number digits).
_POS = {
    "4471": {"po": "PO-4471", "customer": "Woodgrove Water Authority", "received": "2026-10-01",
             "quote": "Q-2210", "region": "Domestic", "channel": "Public sector", "order_class": "New",
             "ship_to": "1200 Reservoir Rd, Dock 3", "contact": "Hannah Cole", "payment": "Net 30",
             "freight": "FOB Origin", "buying_group": "",
             "lines": [("PX-300", 4, 6450.00), ("SH-CO", 4, 410.00), ("KIT-CAL", 2, 280.00)],
             "watch": "Sensor head price differs from the quote"},
    "4472": {"po": "PO-4472", "customer": "Coho Refining", "received": "2026-10-02",
             "quote": "Q-2214", "region": "Domestic", "channel": "Direct industrial", "order_class": "New",
             "ship_to": "88 Harbor Industrial Pkwy", "contact": "Luis Moreno", "payment": "Net 45",
             "freight": "FOB Destination", "buying_group": "",
             "lines": [("PX-500", 6, 8900.00), ("SH-H2S", 6, 520.00)],
             "watch": "Hydrogen sulfide heads ordered without the safety kit"},
    "4473": {"po": "PO-4473", "customer": "Tailwind Mining Co", "received": "2026-10-02",
             "quote": "Q-2219", "region": "International", "channel": "Distributor", "order_class": "Replacement",
             "ship_to": "Gate 7, Ridgeway Mine Site", "contact": "Ana Silva", "payment": "Net 60",
             "freight": "FOB Origin", "buying_group": "",
             "lines": [("PX-300", 10, 6200.00), ("SH-NH3", 10, 455.00)],
             "watch": "Payment terms and a region-restricted sensor"},
    "4474": {"po": "PO-4474", "customer": "Lucerne Labs", "received": "2026-10-03",
             "quote": "Q-2223", "region": "Domestic", "channel": "Direct industrial", "order_class": "Upgrade",
             "ship_to": "45 Science Park Dr, Bldg B", "contact": "Omar Haddad", "payment": "Net 30",
             "freight": "FOB Origin", "buying_group": "",
             "lines": [("PX-500", 2, 8900.00), ("SH-CO", 2, 395.00), ("KIT-CAL", 1, 280.00)],
             "watch": "None expected"},
    "4475": {"po": "PO-4475", "customer": "Relecloud Utilities", "received": "2026-10-04",
             "quote": "Q-2226", "region": "Domestic", "channel": "Public sector", "order_class": "New",
             "ship_to": "300 Grid Ave, Receiving", "contact": "Mei Tanaka", "payment": "Net 30",
             "freight": "FOB Origin", "buying_group": "",
             "lines": [("PX-300", 8, 6100.00), ("SH-CO", 8, 395.00)],
             "watch": "Buying group pricing on the quote"},
}

# Accepted quotes from the CRM snapshot.
_QUOTES = {
    "Q-2210": {"customer": "Woodgrove Water Authority", "contact": "Hannah Cole", "payment": "Net 30",
               "freight": "FOB Origin", "ship_to": "1200 Reservoir Rd, Dock 3", "buying_group": "",
               "prices": {"PX-300": 6450.00, "SH-CO": 395.00, "KIT-CAL": 280.00}},
    "Q-2214": {"customer": "Coho Refining", "contact": "Luis Moreno", "payment": "Net 45",
               "freight": "FOB Destination", "ship_to": "88 Harbor Industrial Pkwy", "buying_group": "",
               "prices": {"PX-500": 8900.00, "SH-H2S": 520.00, "KIT-SAFE": 340.00}},
    "Q-2219": {"customer": "Tailwind Mining Co", "contact": "Ana Silva", "payment": "Net 30",
               "freight": "FOB Origin", "ship_to": "Gate 7, Ridgeway Mine Site", "buying_group": "",
               "prices": {"PX-300": 6200.00, "SH-NH3": 455.00}},
    "Q-2223": {"customer": "Lucerne Labs", "contact": "Omar Haddad", "payment": "Net 30",
               "freight": "FOB Origin", "ship_to": "45 Science Park Dr, Bldg B", "buying_group": "",
               "prices": {"PX-500": 8900.00, "SH-CO": 395.00, "KIT-CAL": 280.00}},
    "Q-2226": {"customer": "Relecloud Utilities", "contact": "Mei Tanaka", "payment": "Net 30",
               "freight": "FOB Origin", "ship_to": "300 Grid Ave, Receiving", "buying_group": "Trey Purchasing Network",
               "prices": {"PX-300": 6100.00, "SH-CO": 395.00}},
}

_ORDER_TYPES = {"Domestic": "STD-DOM", "International": "STD-INTL"}

_GATE = (
    "Synthetic decision support only. This agent does not submit, book, release or change "
    "an order, and it does not contact the customer; a sales operations specialist reviews "
    "every draft and resolves every exception."
)
_SOURCE = "Source: [Synthetic PO Inbox + CRM Quote + Configuration Rule Snapshot]\nAgents: OrderEntryValidationAgent"


# ═══════════════════════════════════════════════════════════════
# HELPERS (plain dicts, lists and arithmetic)
# ═══════════════════════════════════════════════════════════════

def _money(v):
    v = round(v, 2)
    return f"${v:,.2f}" if v != int(v) else f"${v:,.0f}"


def _resolve_po(query):
    """PO number (with or without 'PO-') or part of the customer name; None when nothing matches."""
    if not query:
        return "4471"
    q = query.lower().strip()
    for key in _POS:
        if key in q or q in _POS[key]["customer"].lower():
            return key
    return None


def _quote_checks(key):
    """Field-by-field comparison with the accepted quote: list of (field, po value, quote value, result)."""
    po, qt = _POS[key], _QUOTES[_POS[key]["quote"]]
    checks = []
    for field, label in [("customer", "Customer account"), ("contact", "Ship-to contact"),
                         ("ship_to", "Ship-to address"), ("payment", "Payment terms"), ("freight", "Freight terms")]:
        checks.append((label, po[field], qt[field], "Match" if po[field] == qt[field] else "Mismatch"))
    for part, qty, price in po["lines"]:
        qp = qt["prices"].get(part)
        if qp is None:
            checks.append((f"Price {part}", _money(price), "Not on quote", "Mismatch"))
            continue
        diff = (price - qp) / qp
        result = "Match" if abs(diff) <= _PRICE_TOLERANCE else f"Mismatch ({diff * 100:+.1f}%)"
        checks.append((f"Price {part}", _money(price), _money(qp), result))
    if qt["buying_group"] and not po["buying_group"]:
        checks.append(("Buying group", "Not stated", qt["buying_group"], "Assign from quote"))
    return checks


def _config_checks(key):
    """Configuration rule results: list of (rule, result, detail)."""
    po = _POS[key]
    parts = [p for p, _, _ in po["lines"]]
    qty = {p: q for p, q, _ in po["lines"]}
    analyzers = [p for p in parts if _PRODUCTS[p]["kind"] == "analyzer"]
    sensors = [p for p in parts if _PRODUCTS[p]["kind"] == "sensor"]
    out = []
    for s in sensors:
        ok = all(s in _COMPATIBLE[a] for a in analyzers)
        out.append(("Compatible pairing", "Pass" if ok else "Fail",
                    f"{s} with {', '.join(analyzers)}" + ("" if ok else " is not a released pairing")))
        kit = _MANDATORY_KITS.get(s)
        if kit:
            have = qty.get(kit, 0)
            out.append(("Mandatory kit", "Pass" if have >= qty[s] else "Fail",
                        f"{s} needs {kit} ({have} of {qty[s]} ordered)"))
        region = _REGION_RESTRICTED.get(s)
        if region:
            ok = po["region"] != region
            out.append(("Region release", "Pass" if ok else "Fail",
                        f"{s} is not released for {region} orders" if not ok else f"{s} released for {po['region']}"))
    if not sensors:
        out.append(("Compatible pairing", "Pass", "No sensor heads on the order"))
    return out


def _exceptions(key):
    q = [f"{f}: PO {p} vs quote {v}" for f, p, v, r in _quote_checks(key) if r.startswith("Mismatch")]
    q += [f"{f}: assign {v} from the quote" for f, p, v, r in _quote_checks(key) if r == "Assign from quote"]
    c = [f"{rule}: {detail}" for rule, res, detail in _config_checks(key) if res == "Fail"]
    return q + c


def _total(key):
    return sum(q * p for _, q, p in _POS[key]["lines"])


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "order_queue", "extract_po", "quote_validation", "configuration_check",
    "order_classification", "draft_sales_order", "queue_review",
]


class OrderEntryValidationAgent(BasicAgent):
    """
    Sales operations order entry assistant.

    Operations:
        order_queue          - the pending purchase-order queue with what to watch for on each
        extract_po           - structured header and line fields read from one PO
        quote_validation     - PO vs accepted quote: customer, contact, terms, ship-to, prices (1% tolerance)
        configuration_check  - product configuration rules: pairings, mandatory kits, region release
        order_classification - region, order type, order class and sales channel
        draft_sales_order    - draft ERP sales order with every exception listed (never submitted)
        queue_review         - the whole queue: which POs are ready to enter and which need a fix
    """

    def __init__(self):
        self.name = "OrderEntryValidationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Order entry assistant for the Proseware Instruments sales operations team (fixed "
                "synthetic snapshot of five pending purchase orders, PO-4471 to PO-4475). Always use "
                "this tool, with its demo defaults, for: what is in my PO queue (order_queue); reading "
                "or extracting a PO's fields (extract_po); checking a PO against its quote, prices or "
                "terms (quote_validation); checking the product configuration, kits or pairings "
                "(configuration_check); which order type, class or channel applies "
                "(order_classification); preparing or drafting the sales order (draft_sales_order); and "
                "which orders are ready to enter or still need a fix (queue_review). Pass po as the PO "
                "number or customer name; the default is PO-4471. It never submits or books an order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "order_queue for the queue; extract_po to read a PO; quote_validation for "
                            "quote, price and terms checks; configuration_check for configuration rules; "
                            "order_classification for order type and channel; draft_sales_order for the "
                            "draft sales order; queue_review for what is ready across the queue."
                        ),
                    },
                    "po": {
                        "type": "string",
                        "description": "PO number or customer name, e.g. 'PO-4472' or 'Coho' (default PO-4471)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "order_queue"
        dispatch = {
            "order_queue": self._order_queue,
            "extract_po": self._extract_po,
            "quote_validation": self._quote_validation,
            "configuration_check": self._configuration_check,
            "order_classification": self._order_classification,
            "draft_sales_order": self._draft_sales_order,
            "queue_review": self._queue_review,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}. Available: {', '.join(_OPERATIONS)}.\n\n{_GATE}\n\n{_SOURCE}"
        if op in ("order_queue", "queue_review"):
            return handler()
        key = _resolve_po(kwargs.get("po", ""))
        if key is None:
            pos = ", ".join(f"{p['po']} {p['customer']}" for p in _POS.values())
            return f"No synthetic purchase order matches '{kwargs.get('po')}'. Queue: {pos}.\n\n{_GATE}\n\n{_SOURCE}"
        return handler(key)

    # ── order_queue ───────────────────────────────────────────
    def _order_queue(self):
        rows = "\n".join(
            f"| {p['po']} | {p['customer']} | {p['received']} | {p['quote']} | {_money(_total(k))} | {p['watch']} |"
            for k, p in _POS.items())
        total = sum(_total(k) for k in _POS)
        return (
            f"**Pending PO Queue: {_ORG} Sales Operations ({_AS_OF})**\n\n"
            f"| PO | Customer | Received | Quote | PO Value | Watch For |\n|---|---|---|---|---|---|\n{rows}\n\n"
            f"**Queue:** {len(_POS)} purchase orders worth {_money(total)}, each matched to an accepted quote.\n"
            f"**Next step:** start with PO-4471 (oldest): read it and check it against quote Q-2210.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── extract_po ────────────────────────────────────────────
    def _extract_po(self, key):
        p = _POS[key]
        lines = "\n".join(f"| {i} | {part} | {_PRODUCTS[part]['name']} | {q} | {_money(pr)} | {_money(q * pr)} |"
                          for i, (part, q, pr) in enumerate(p["lines"], 1))
        return (
            f"**Purchase Order Extract: {p['po']}**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Customer | {p['customer']} |\n| PO Number | {p['po']} |\n| Date Received | {p['received']} |\n"
            f"| Ship-To | {p['ship_to']} |\n| Ship-To Contact | {p['contact']} |\n"
            f"| Payment Terms | {p['payment']} |\n| Freight Terms | {p['freight']} |\n"
            f"| Referenced Quote | {p['quote']} |\n\n"
            f"| Line | Part | Description | Qty | Unit Price | Extended |\n|---|---|---|---|---|---|\n{lines}\n\n"
            f"**PO total:** {_money(_total(key))} across {len(p['lines'])} lines. Every field above was read "
            f"from the PO; nothing was inferred.\n**Next step:** validate it against quote {p['quote']}.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── quote_validation ──────────────────────────────────────
    def _quote_validation(self, key):
        p = _POS[key]
        checks = _quote_checks(key)
        rows = "\n".join(f"| {f} | {pv} | {qv} | {r} |" for f, pv, qv, r in checks)
        issues = [c for c in checks if c[3] != "Match"]
        if not issues:
            verdict, step = "All fields match the quote.", "check the product configuration"
        else:
            verdict = (f"{len(issues)} {'exception' if len(issues) == 1 else 'exceptions'}: "
                       + "; ".join(f"{f} is {pv} on the PO vs {qv} on the quote"
                                   + (f" ({r.split('(')[1]}" if "(" in r else "") for f, pv, qv, r in issues) + ".")
            step = "confirm " + " and ".join(f[0].lower() + f[1:] for f, _, _, _ in issues) + " with the account owner before entry"
        return (
            f"**Quote Validation: {p['po']} vs {p['quote']}**\n\n"
            f"| Check | PO | Quote | Result |\n|---|---|---|---|\n{rows}\n\n"
            f"**Result:** {verdict} Price tolerance is {_PRICE_TOLERANCE * 100:.0f}% per line.\n"
            f"**Next step:** {step}.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── configuration_check ───────────────────────────────────
    def _configuration_check(self, key):
        p = _POS[key]
        checks = _config_checks(key)
        rows = "\n".join(f"| {rule} | {res} | {detail} |" for rule, res, detail in checks)
        fails = [c for c in checks if c[1] == "Fail"]
        fix = ""
        if any(rule == "Mandatory kit" for rule, _, _ in fails):
            kit = [d.split(" needs ")[1].split(" ")[0] for r, _, d in fails if r == "Mandatory kit"][0]
            fix = f"add {kit} to the order (it is on quote {p['quote']}) and confirm with the customer"
        elif fails:
            fix = "ask the account owner for a released alternative before entry"
        return (
            f"**Configuration Check: {p['po']} ({p['customer']})**\n\n"
            f"| Rule | Result | Detail |\n|---|---|---|\n{rows}\n\n"
            f"**Result:** {len(checks) - len(fails)} of {len(checks)} configuration rules pass."
            + (f" Never enter this order with the wrong configuration: {fix}.\n" if fails else " Configuration is valid.\n")
            + f"\n{_GATE}\n\n{_SOURCE}"
        )

    # ── order_classification ──────────────────────────────────
    def _order_classification(self, key):
        p = _POS[key]
        return (
            f"**Order Classification: {p['po']} ({p['customer']})**\n\n"
            f"| Attribute | Value | Basis |\n|---|---|---|\n"
            f"| Region | {p['region']} | Ship-to address |\n"
            f"| Order Type | {_ORDER_TYPES[p['region']]} | Region rule |\n"
            f"| Order Class | {p['order_class']} | Quote opportunity |\n"
            f"| Sales Channel | {p['channel']} | Customer account |\n\n"
            f"**Next step:** use these values on the draft sales order header.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── draft_sales_order ─────────────────────────────────────
    def _draft_sales_order(self, key):
        p = _POS[key]
        qt = _QUOTES[p["quote"]]
        lines = "\n".join(
            f"| {i} | {part} | {q} | {_money(qt['prices'].get(part, pr))} | {_money(q * qt['prices'].get(part, pr))} |"
            for i, (part, q, pr) in enumerate(p["lines"], 1))
        total = sum(q * qt["prices"].get(part, pr) for part, q, pr in p["lines"])
        exc = _exceptions(key)
        status = "Draft - Not Submitted, on hold for exceptions" if exc else "Draft - Not Submitted, ready to enter"
        exc_txt = "\n".join(f"- {e}" for e in exc) if exc else "- None"
        return (
            f"**Draft Sales Order: {p['po']} - Not Submitted**\n\n"
            f"| Header | Value |\n|---|---|\n"
            f"| Customer | {p['customer']} |\n| Customer PO | {p['po']} |\n| Quote | {p['quote']} |\n"
            f"| Order Type | {_ORDER_TYPES[p['region']]} |\n| Order Class | {p['order_class']} |\n"
            f"| Sales Channel | {p['channel']} |\n| Payment Terms | {qt['payment']} (quote) |\n"
            f"| Freight Terms | {qt['freight']} (quote) |\n| Ship-To | {p['ship_to']} |\n"
            f"| Status | {status} |\n\n"
            f"| Line | Part | Qty | Unit Price (quote) | Extended |\n|---|---|---|---|---|\n{lines}\n\n"
            f"**Order total at quote prices:** {_money(total)} (PO states {_money(_total(key))}).\n"
            f"**Exceptions to resolve before entry:**\n{exc_txt}\n\n"
            f"A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── queue_review ──────────────────────────────────────────
    def _queue_review(self):
        rows, ready = [], 0
        for k, p in _POS.items():
            exc = _exceptions(k)
            if not exc:
                ready += 1
            rows.append(f"| {p['po']} | {p['customer']} | {'Ready to enter' if not exc else 'Needs fix'} | "
                        f"{'; '.join(exc) if exc else '-'} |")
        return (
            f"**Queue Review: {_AS_OF}**\n\n"
            f"| PO | Customer | Status | Exceptions |\n|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"**Result:** {ready} of {len(_POS)} purchase orders are ready to enter; "
            f"{len(_POS) - ready} need a fix first. Each exception names the field or rule behind it.\n"
            f"**Next step:** enter the ready orders and send the exceptions to their account owners as drafts.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = OrderEntryValidationAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
