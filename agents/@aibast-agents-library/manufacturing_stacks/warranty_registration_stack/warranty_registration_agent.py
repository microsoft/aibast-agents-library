"""
Warranty and Registration Agent

Dealer-facing assistant for equipment warranty coverage, claim pre-checks,
serial validation, registration drafts and extended-coverage offers.

Where a real deployment would call an ERP warranty module, a product catalog
and a dealer registration service, this agent uses a fixed synthetic snapshot
so it runs anywhere without credentials. It never files a claim, submits a
registration, sells an extension or contacts a customer: it returns drafts and
pre-checks for an authorized person to act on.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/warranty-registration",
    "version": "1.0.0",
    "display_name": "Warranty and Registration Agent",
    "description": "Give equipment dealers one place to check warranty coverage, pre-check claims, validate serials and prepare product registrations, so covered repairs move faster and no unit misses its registration window.",
    "author": "AIBAST",
    "tags": ["manufacturing", "warranty", "product-registration", "dealer-service", "aftermarket"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot, as of 2026-03-02)
# ═══════════════════════════════════════════════════════════════

_AS_OF = "2026-03-02"
_AS_OF_ORDINAL = 739677          # date(2026, 3, 2).toordinal(), fixed so no clock is read

_DEALER = {
    "name": "Fabrikam Tool Supply (Riverside branch)",
    "account": "DLR-4100",
    "manufacturer": "Northwind Equipment",
    "service_manager": "Priya Raman",
    "warranty_desk": "Northwind warranty desk",
}

_COVERAGE = {
    "full": {"label": "Full parts and labor", "parts": "Yes", "labor": "Yes", "on_site": "Yes"},
    "parts_only": {"label": "Parts only", "parts": "Yes", "labor": "No", "on_site": "No"},
    "limited": {"label": "Limited (wear items excluded)", "parts": "Yes", "labor": "No", "on_site": "No"},
}

# Registered units. Day counts are precomputed against the snapshot date.
_UNITS = {
    "HP-40-1182": {
        "product": "Hydraulic Press HP-40", "family": "Shop presses",
        "purchased": "2024-04-10", "registered": "2024-04-12", "warranty_end": "2027-04-10",
        "end_ordinal": 740081, "coverage": "full", "extension_price": 420.00,
        "claims": [],
    },
    "WS-25-4471": {
        "product": "Welding Station WS-250", "family": "Welding",
        "purchased": "2025-01-22", "registered": "2025-01-24", "warranty_end": "2027-01-22",
        "end_ordinal": 740003, "coverage": "full", "extension_price": 260.00,
        "claims": [
            {"claim": "CLM-25-0318", "date": "2025-08-14", "issue": "Torch cable replaced", "status": "Resolved"},
        ],
    },
    "BG-08-2290": {
        "product": "Bench Grinder BG-8", "family": "Grinding",
        "purchased": "2024-03-28", "registered": "2024-04-02", "warranty_end": "2026-03-28",
        "end_ordinal": 739703, "coverage": "parts_only", "extension_price": 85.00,
        "claims": [],
    },
    "PW-30-0615": {
        "product": "Parts Washer PW-30", "family": "Cleaning",
        "purchased": "2024-05-05", "registered": "2024-05-07", "warranty_end": "2026-05-05",
        "end_ordinal": 739741, "coverage": "full", "extension_price": 140.00,
        "claims": [],
    },
    "TC-90-3307": {
        "product": "Tire Changer TC-900", "family": "Tire service",
        "purchased": "2023-02-14", "registered": "2023-02-15", "warranty_end": "2026-02-14",
        "end_ordinal": 739661, "coverage": "full", "extension_price": 0.00,
        "claims": [
            {"claim": "CLM-24-0127", "date": "2024-06-03", "issue": "Bead breaker cylinder resealed", "status": "Resolved"},
            {"claim": "CLM-25-0044", "date": "2025-02-11", "issue": "Turntable motor replaced", "status": "Resolved"},
        ],
    },
    "CR-12-0950": {
        "product": "Coolant Recovery Unit CR-12", "family": "Fluid service",
        "purchased": "2025-06-30", "registered": "2025-07-01", "warranty_end": "2027-06-30",
        "end_ordinal": 740162, "coverage": "limited", "extension_price": 110.00,
        "claims": [],
    },
}

# Units sold but not yet registered (shipment snapshot). Registration window: 30 days from sale.
_PENDING = {
    "WS-25-4520": {
        "product": "Welding Station WS-250", "sold": "2026-02-20", "registration_due": "2026-03-22",
        "due_ordinal": 739697, "term_months": 24, "warranty_end": "2028-02-20", "coverage": "full",
        "buyer": "Contoso Fleet Services (shop account C-2207)",
    },
    "HP-40-1207": {
        "product": "Hydraulic Press HP-40", "sold": "2026-02-26", "registration_due": "2026-03-28",
        "due_ordinal": 739703, "term_months": 36, "warranty_end": "2029-02-26", "coverage": "full",
        "buyer": "Adatum Auto Body (shop account C-2241)",
    },
}

_SERIALS = list(_UNITS) + list(_PENDING)
_EXTENSION_WINDOW_DAYS = 90
_EXTENSION_DISCOUNT = 0.15

_GATE = (
    "Synthetic dealer snapshot only. This agent does not file a claim, submit a "
    "registration, sell an extension, contact a customer or change a warranty record; "
    "it prepares drafts and pre-checks for an authorized person to act on."
)
_SOURCE = "Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]\nAgents: WarrantyRegistrationAgent"


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _days_left(unit):
    return unit["end_ordinal"] - _AS_OF_ORDINAL


def _status(unit):
    d = _days_left(unit)
    if d < 0:
        return "Expired"
    if d <= _EXTENSION_WINDOW_DAYS:
        return "Expiring soon"
    return "Active"


def _money(x):
    return f"${x:,.2f}"


def _resolve_serial(serial, default):
    """Exact serial (case-insensitive) or a serial contained in the text; None when nothing matches."""
    if not serial:
        return default
    q = str(serial).strip().upper()
    for s in _SERIALS:
        if s == q or s in q:
            return s
    return None


def _miss(serial):
    return (
        f"No unit with serial '{serial}' is in the synthetic snapshot. "
        f"Known serials: {', '.join(_SERIALS)}.\n\n{_GATE}\n\n{_SOURCE}"
    )


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "coverage_overview", "claim_precheck", "unit_record",
    "validate_serial", "registration_draft", "extension_offers",
]


class WarrantyRegistrationAgent(BasicAgent):
    """
    Dealer warranty and registration assistant.

    Operations:
        coverage_overview  - dealer-wide coverage: active, expiring, expired, awaiting registration
        claim_precheck     - is a repair on this unit covered? (pre-check, never files a claim)
        unit_record        - full warranty record and claim history for one serial
        validate_serial    - catalog, format and duplicate check before registering
        registration_draft - Not Submitted registration draft for a sold unit
        extension_offers   - extended-coverage offers for units expiring within 90 days
    """

    def __init__(self):
        self.name = "WarrantyRegistrationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Dealer warranty desk for the fictional Fabrikam Tool Supply branch and its "
                "Northwind Equipment units. Always use this tool for warranty coverage, repair "
                "coverage questions, unit warranty records, serial checks, product registrations "
                "and extended-coverage offers. Routing: how coverage looks overall -> "
                "coverage_overview; 'is this repair covered' or 'can we claim' for a serial -> "
                "claim_precheck; 'full record' or claim history for a serial -> unit_record; "
                "'check the serial' before registering a sold unit -> validate_serial; "
                "'prepare/draft the registration' -> registration_draft (never submitted); "
                "'who should we offer extended coverage to' -> extension_offers. Serial numbers "
                "look like WS-25-4471. Every operation has a demo default, so call it right away. "
                "Never files a claim, submits a registration, sells an extension or contacts a "
                "customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "coverage_overview for the dealer-wide picture; claim_precheck for "
                            "whether a repair is covered; unit_record for one unit's full record; "
                            "validate_serial before registering; registration_draft to prepare a "
                            "registration; extension_offers for extended-coverage candidates."
                        ),
                    },
                    "serial_number": {
                        "type": "string",
                        "enum": list(_SERIALS),
                        "description": "Unit serial, e.g. 'WS-25-4471' (claim_precheck, unit_record, validate_serial, registration_draft)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "coverage_overview"
        serial = kwargs.get("serial_number") or ""
        if op == "coverage_overview":
            return self._coverage_overview()
        if op == "extension_offers":
            return self._extension_offers()
        defaults = {
            "claim_precheck": "WS-25-4471", "unit_record": "TC-90-3307",
            "validate_serial": "WS-25-4520", "registration_draft": "WS-25-4520",
        }
        if op not in defaults:
            return f"Unknown operation: {op}. Available: {', '.join(_OPERATIONS)}."
        key = _resolve_serial(serial, defaults[op])
        if key is None:
            return _miss(serial)
        if op == "claim_precheck":
            return self._claim_precheck(key)
        if op == "unit_record":
            return self._unit_record(key)
        if op == "validate_serial":
            return self._validate_serial(key)
        return self._registration_draft(key)

    # ── coverage_overview ─────────────────────────────────────
    def _coverage_overview(self):
        rows, active, expiring, expired = [], 0, 0, 0
        for serial, u in _UNITS.items():
            st = _status(u)
            if st == "Active":
                active += 1
            elif st == "Expiring soon":
                expiring += 1
            else:
                expired += 1
            d = _days_left(u)
            left = f"{d} days" if d >= 0 else f"ended {-d} days ago"
            rows.append(f"| {serial} | {u['product']} | {_COVERAGE[u['coverage']]['label']} | {u['warranty_end']} | {left} | {st} |")
        pending = "\n".join(
            f"| {s} | {p['product']} | sold {p['sold']} | due {p['registration_due']} ({p['due_ordinal'] - _AS_OF_ORDINAL} days) |"
            for s, p in _PENDING.items()
        )
        return (
            f"**Warranty Coverage Overview: {_DEALER['name']}**\n\n"
            f"Dealer account {_DEALER['account']} | Manufacturer {_DEALER['manufacturer']} | As of {_AS_OF}\n\n"
            f"| Measure | Count |\n|---|---|\n"
            f"| Registered units | {len(_UNITS)} |\n"
            f"| Active | {active} |\n"
            f"| Expiring within {_EXTENSION_WINDOW_DAYS} days | {expiring} |\n"
            f"| Expired | {expired} |\n"
            f"| Sold, awaiting registration | {len(_PENDING)} |\n\n"
            f"| Serial | Product | Coverage | Ends | Remaining | Status |\n|---|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"**Awaiting registration (30-day window):**\n\n"
            f"| Serial | Product | Sale | Registration |\n|---|---|---|---|\n{pending}\n\n"
            f"**Next step:** register the 2 sold units before their windows close and review "
            f"extended-coverage offers for the {expiring} expiring units.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── claim_precheck ────────────────────────────────────────
    def _claim_precheck(self, serial):
        if serial in _PENDING:
            p = _PENDING[serial]
            return (
                f"**Claim Pre-Check: {serial} ({p['product']})**\n\n"
                f"Result: **Not ready for claim review** - this unit is not registered yet "
                f"(registration due {p['registration_due']}). Register it first; coverage starts from the "
                f"sale date {p['sold']} once registration is confirmed.\n\n{_GATE}\n\n{_SOURCE}"
            )
        u = _UNITS[serial]
        cov = _COVERAGE[u["coverage"]]
        d = _days_left(u)
        active = d >= 0
        if not active:
            result = "Not eligible - warranty ended"
            path = (f"Coverage ended {u['warranty_end']} ({-d} days ago). Offer the customer a paid "
                    f"repair quote; an exception request goes to the {_DEALER['warranty_desk']}.")
        elif cov["labor"] == "No":
            result = "Eligible for parts only"
            path = "Parts are covered; labor is billable to the customer. Quote labor before the repair."
        else:
            result = "Eligible for claim review"
            path = (f"Parts and labor are covered. Prepare the claim with the failure description, "
                    f"photos and hours for the {_DEALER['warranty_desk']} to approve.")
        claims = len(u["claims"])
        return (
            f"**Claim Pre-Check: {serial} ({u['product']})**\n\n"
            f"| Check | Result |\n|---|---|\n"
            f"| Registration | Confirmed {u['registered']} |\n"
            f"| Warranty active | {'Yes' if active else 'No'} (ends {u['warranty_end']}) |\n"
            f"| Days remaining | {d if active else 0} |\n"
            f"| Coverage | {cov['label']} |\n"
            f"| Parts covered | {cov['parts'] if active else 'No'} |\n"
            f"| Labor covered | {cov['labor'] if active else 'No'} |\n"
            f"| Prior claims | {claims} |\n\n"
            f"**Pre-check result: {result}**\n\n"
            f"**Next step:** {path}\n\n"
            f"No claim was filed. The {_DEALER['warranty_desk']} makes the coverage decision.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── unit_record ───────────────────────────────────────────
    def _unit_record(self, serial):
        if serial in _PENDING:
            p = _PENDING[serial]
            return (
                f"**Warranty Record: {serial} ({p['product']})**\n\n"
                f"No warranty record yet - sold {p['sold']} to {p['buyer']}, registration due "
                f"{p['registration_due']}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        u = _UNITS[serial]
        cov = _COVERAGE[u["coverage"]]
        d = _days_left(u)
        claims = "\n".join(
            f"| {c['claim']} | {c['date']} | {c['issue']} | {c['status']} |" for c in u["claims"]
        ) or "| - | - | No claims on record | - |"
        if d < 0:
            nxt = (f"Warranty ended {-d} days ago. Repairs are customer-paid; quote the repair and, if "
                   f"the customer asks, route an exception request to the {_DEALER['warranty_desk']}.")
        elif d <= _EXTENSION_WINDOW_DAYS:
            nxt = f"Coverage ends in {d} days; this unit qualifies for an extended-coverage offer."
        else:
            nxt = "Coverage is active; no action needed."
        status = f"{_status(u)} ({d} days remaining)" if d >= 0 else f"Expired (ended {-d} days ago)"
        return (
            f"**Warranty Record: {serial} ({u['product']})**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Product family | {u['family']} |\n"
            f"| Purchased | {u['purchased']} |\n"
            f"| Registered | {u['registered']} |\n"
            f"| Warranty ends | {u['warranty_end']} |\n"
            f"| Status | {status} |\n"
            f"| Coverage | {cov['label']} |\n"
            f"| Parts / Labor / On-site | {cov['parts']} / {cov['labor']} / {cov['on_site']} |\n\n"
            f"**Claim history ({len(u['claims'])}):**\n\n"
            f"| Claim | Date | Issue | Status |\n|---|---|---|---|\n{claims}\n\n"
            f"**Next step:** {nxt}\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── validate_serial ───────────────────────────────────────
    def _validate_serial(self, serial):
        if serial in _UNITS:
            u = _UNITS[serial]
            return (
                f"**Serial Check: {serial}**\n\n"
                f"| Check | Result |\n|---|---|\n"
                f"| Format | Valid |\n"
                f"| In catalog | Yes - {u['product']} |\n"
                f"| Already registered | Yes - registered {u['registered']} |\n\n"
                f"**Result: Duplicate - do not register again.** This serial already has a warranty "
                f"record ending {u['warranty_end']}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        p = _PENDING[serial]
        days = p["due_ordinal"] - _AS_OF_ORDINAL
        return (
            f"**Serial Check: {serial}**\n\n"
            f"| Check | Result |\n|---|---|\n"
            f"| Format | Valid |\n"
            f"| In catalog | Yes - {p['product']} |\n"
            f"| Already registered | No |\n"
            f"| Sold | {p['sold']} to {p['buyer']} |\n"
            f"| Registration window | Due {p['registration_due']} ({days} days left) |\n\n"
            f"**Result: Ready to register.** Ask me to prepare the registration draft.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── registration_draft ────────────────────────────────────
    def _registration_draft(self, serial):
        if serial in _UNITS:
            u = _UNITS[serial]
            return (
                f"**Registration Draft: {serial}**\n\n"
                f"No draft prepared - {u['product']} {serial} is already registered "
                f"({u['registered']}). Registering it again would create a duplicate.\n\n{_GATE}\n\n{_SOURCE}"
            )
        p = _PENDING[serial]
        cov = _COVERAGE[p["coverage"]]
        days = p["due_ordinal"] - _AS_OF_ORDINAL
        return (
            f"**Product Registration Draft - Not Submitted**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Draft ID | REG-DRAFT-{serial} |\n"
            f"| Serial | {serial} |\n"
            f"| Product | {p['product']} |\n"
            f"| Dealer | {_DEALER['name']} ({_DEALER['account']}) |\n"
            f"| End customer | {p['buyer']} |\n"
            f"| Sale date (warranty start) | {p['sold']} |\n"
            f"| Warranty term | {p['term_months']} months |\n"
            f"| Warranty would end | {p['warranty_end']} |\n"
            f"| Coverage | {cov['label']} |\n"
            f"| Registration due | {p['registration_due']} ({days} days left) |\n"
            f"| Status | Draft for dealer review |\n\n"
            f"**Before submitting:** confirm the sale date on the invoice and the end customer's "
            f"contact with {_DEALER['service_manager']}, then submit it in the manufacturer's "
            f"registration portal. Nothing was submitted and no warranty was activated.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── extension_offers ──────────────────────────────────────
    def _extension_offers(self):
        rows, total, count = [], 0.0, 0
        for serial, u in _UNITS.items():
            d = _days_left(u)
            if 0 <= d <= _EXTENSION_WINDOW_DAYS:
                net = round(u["extension_price"] * (1 - _EXTENSION_DISCOUNT), 2)
                total += net
                count += 1
                rows.append(
                    f"| {serial} | {u['product']} | {u['warranty_end']} | {d} days | "
                    f"{_money(u['extension_price'])} | {_money(net)} |"
                )
        lapsed = [s for s, u in _UNITS.items() if _days_left(u) < 0]
        return (
            f"**Extended-Coverage Offers: {count} units ending within {_EXTENSION_WINDOW_DAYS} days**\n\n"
            f"| Serial | Product | Coverage ends | Remaining | List price | Offer (15% off list) |\n"
            f"|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"**Offer total:** {_money(total)} across {count} units.\n"
            f"**Not offered:** {', '.join(lapsed)} - coverage already ended; extensions must start "
            f"before the warranty ends.\n\n"
            f"**Next step:** review the offer drafts and send them to the customers yourself. "
            f"No offer was sent and nothing was sold.\n\n{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = WarrantyRegistrationAgent()
    story = [
        {"operation": "coverage_overview"},
        {"operation": "claim_precheck", "serial_number": "WS-25-4471"},
        {"operation": "unit_record", "serial_number": "TC-90-3307"},
        {"operation": "validate_serial", "serial_number": "WS-25-4520"},
        {"operation": "registration_draft", "serial_number": "WS-25-4520"},
        {"operation": "extension_offers"},
    ]
    for kw in story:
        print("=" * 60)
        print(agent.perform(**kw))
        print()
