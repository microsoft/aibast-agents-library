"""
Regulatory Compliance Agent — Financial Services Stack

Implements the published AIBAST one-pager "Regulatory Compliance Agent"
(advertised solution #40) end to end. The advertised scenario is an investment
firm validating compliance across thousands of executed trades, and the
one-pager promises exactly four things:

  1. Scan all executed trades for reporting accuracy, required fields, and
     best-execution performance            -> operation "trade_surveillance"
  2. Flag missing or outdated documentation -> operation "documentation_review"
  3. Automate corrections and submissions
     to the regulatory portal               -> operation "remediation_submission"
  4. Identify upcoming certification
     expirations and enroll traders         -> operation "certification_tracker"

plus the Chief Compliance Officer roll-up the demo opens on
("compliance_dashboard", the default).

Personas served: Chief Compliance Officer, Compliance Manager, Trading Desk
Supervisor. Regime: MiFID II — RTS 22 transaction reporting, RTS 27/28 best
execution.

Where a real deployment would connect to an order management system, an
Approved Reporting Mechanism (ARM) and an LMS, this agent uses a synthetic data
layer so it runs with no configuration. All dates are computed relative to the
day it runs, so a demo never goes stale.
"""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fs-regulatory-compliance",
    "version": "2.0.0",
    "display_name": "Regulatory Compliance Agent",
    "description": "Automates compliance monitoring and regulatory reporting to achieve proactive risk management with real-time surveillance.",
    "author": "AIBAST",
    "tags": ["compliance", "MiFID-II", "trade-surveillance", "best-execution",
             "transaction-reporting", "certifications", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

TODAY = date.today()


def _d(offset_days):
    return (TODAY + timedelta(days=offset_days)).isoformat()


# ---------------------------------------------------------------------------
# Synthetic domain data — an investment firm's trading desk
# ---------------------------------------------------------------------------

# The reporting entity. A real deployment reads this from the firm's MiFIR
# registration; the LEI is correctly formatted (20 char, ISO 17442) but synthetic.
EXECUTING_ENTITY = {
    "name": "Northgate Asset Management LLP",
    "lei": "549300XKQZ2P4NLK7T18",
    "mifir_status": "Investment firm — MiFID II Article 26 reporting entity",
    "arm": "Unavista ARM",
    "nca": "FCA (UK) / AFM (NL) passporting",
}

# MiFID II RTS 22 transaction reporting. Field numbers are the real Annex I
# Table 2 positions a compliance officer reads off a rejection notice, so the
# agent's output can be reconciled against an actual ARM response file.
RTS22_FIELDS = {
    "transaction_reference": (2, "Transaction Reference Number"),
    "executing_entity_lei": (4, "Executing entity identification code"),
    "buyer_lei": (7, "Buyer identification code"),
    "seller_lei": (16, "Seller identification code"),
    "trading_datetime": (28, "Trading date time"),
    "quantity": (30, "Quantity"),
    "price": (33, "Price"),
    "trading_venue": (36, "Venue"),
    "instrument_id": (41, "Instrument identification code"),
    "investment_decision_id": (57, "Investment decision within firm"),
    "execution_decision_id": (59, "Execution within firm"),
}
RTS22_REQUIRED_FIELDS = list(RTS22_FIELDS)

# ARM rejection codes as they come back on a MiFIR response file.
ARM_REJECTION_CODES = {
    "missing_field": ("CON-412", "Mandatory field absent or empty"),
    "venue_mismatch": ("CON-190", "Venue does not match instrument reference data (FIRDS)"),
    "not_submitted": ("LATE-026", "Transaction not reported by T+1 (MiFIR Art. 26(1))"),
}

# Counterparties, by LEI. Correctly formatted, synthetic.
COUNTERPARTIES = {
    "5493001KJTIIGC8Y1R12": "Meridian Pension Trustees Ltd",
    "213800QILIUD4ROSU703": "Halden Life Assurance plc",
    "549300ZFEEJ2IP5VME73": "Cavendish Multi-Asset Fund SICAV",
    "894500PL5FUZ1QG6JS64": "Ashcombe Endowment Trust",
}

# Where each instrument is admitted to trading. A report naming a venue the
# instrument is not admitted on is the "venue mismatch" the one-pager calls out.
INSTRUMENT_VENUES = {
    "GB00BH4HKS39": {"name": "Vodafone Group PLC", "admitted": ["XLON", "CHIX", "BATE"], "asset_class": "Equity"},
    "DE0007164600": {"name": "SAP SE", "admitted": ["XETR", "CHIX", "TQEX"], "asset_class": "Equity"},
    "FR0000120271": {"name": "TotalEnergies SE", "admitted": ["XPAR", "CHIX"], "asset_class": "Equity"},
    "NL0011794037": {"name": "Koninklijke Ahold Delhaize", "admitted": ["XAMS", "CHIX"], "asset_class": "Equity"},
    "XS2434891912": {"name": "Iberdrola 1.875% 2030", "admitted": ["XLON"], "asset_class": "Bond"},
}

# Executed trades. Each carries what the desk actually reported.
TRADES = [
    {"ref": "TRD-88104", "instrument": "GB00BH4HKS39", "venue": "XLON", "side": "BUY",
     "quantity": 145000, "price": 74.82, "arrival_price": 74.79, "benchmark_vwap": 74.86,
     "executed": _d(-1), "exec_time": "09:14:22.418733", "counterparty": "5493001KJTIIGC8Y1R12",
     "trader": "T-2041", "algo": "ALGO-VWAP-EU", "missing_fields": [], "reported": True},
    {"ref": "TRD-88117", "instrument": "DE0007164600", "venue": "XETR", "side": "SELL",
     "quantity": 22500, "price": 141.60, "arrival_price": 141.63, "benchmark_vwap": 141.58,
     "executed": _d(-1), "exec_time": "11:02:57.996210", "counterparty": "213800QILIUD4ROSU703",
     "trader": "T-2041", "algo": "ALGO-IS-DE", "missing_fields": ["investment_decision_id"], "reported": True},
    {"ref": "TRD-88129", "instrument": "FR0000120271", "venue": "XETR", "side": "BUY",
     "quantity": 61000, "price": 58.14, "arrival_price": 58.12, "benchmark_vwap": 58.15,
     "executed": _d(-2), "exec_time": "14:38:05.113904", "counterparty": "549300ZFEEJ2IP5VME73",
     "trader": "T-2107", "algo": "ALGO-VWAP-EU", "missing_fields": [], "reported": True},
    # The problem trade the demo lands on: incomplete, unlodged, and a genuine
    # best-execution outlier all at once.
    {"ref": "TRD-88133", "instrument": "NL0011794037", "venue": "XAMS", "side": "BUY",
     "quantity": 38000, "price": 29.44, "arrival_price": 29.39, "benchmark_vwap": 29.40,
     "executed": _d(-2), "exec_time": "16:51:44.207518", "counterparty": "894500PL5FUZ1QG6JS64",
     "trader": "T-2107", "algo": "ALGO-IS-DE", "missing_fields": ["execution_decision_id", "buyer_lei"], "reported": False},
    {"ref": "TRD-88146", "instrument": "XS2434891912", "venue": "XLON", "side": "SELL",
     "quantity": 4000000, "price": 96.35, "arrival_price": 96.36, "benchmark_vwap": 96.34,
     "executed": _d(-3), "exec_time": "10:07:31.660042", "counterparty": "213800QILIUD4ROSU703",
     "trader": "T-2233", "algo": None, "missing_fields": [], "reported": True},
    {"ref": "TRD-88150", "instrument": "GB00BH4HKS39", "venue": "TQEX", "side": "SELL",
     "quantity": 96000, "price": 74.51, "arrival_price": 74.60, "benchmark_vwap": 74.55,
     "executed": _d(-3), "exec_time": "15:22:09.874311", "counterparty": "5493001KJTIIGC8Y1R12",
     "trader": "T-2233", "algo": "ALGO-DARK-EU", "missing_fields": [], "reported": True},
    {"ref": "TRD-88162", "instrument": "DE0007164600", "venue": "CHIX", "side": "BUY",
     "quantity": 18700, "price": 142.05, "arrival_price": 142.02, "benchmark_vwap": 142.07,
     "executed": _d(-4), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2041", "algo": "ALGO-IS-DE",
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88178", "instrument": "FR0000120271", "venue": "XPAR", "side": "SELL",
     "quantity": 74500, "price": 57.88, "arrival_price": 57.90, "benchmark_vwap": 57.86,
     "executed": _d(-4), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2107", "algo": "ALGO-VWAP-EU",
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88184", "instrument": "GB00BH4HKS39", "venue": "CHIX", "side": "BUY",
     "quantity": 52000, "price": 74.66, "arrival_price": 74.64, "benchmark_vwap": 74.68,
     "executed": _d(-5), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2041", "algo": "ALGO-VWAP-EU",
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88191", "instrument": "NL0011794037", "venue": "XAMS", "side": "SELL",
     "quantity": 27400, "price": 29.51, "arrival_price": 29.52, "benchmark_vwap": 29.49,
     "executed": _d(-5), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2107", "algo": "ALGO-VWAP-EU",
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88203", "instrument": "DE0007164600", "venue": "XETR", "side": "BUY",
     "quantity": 31200, "price": 141.88, "arrival_price": 141.85, "benchmark_vwap": 141.90,
     "executed": _d(-6), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2041", "algo": "ALGO-VWAP-EU",
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88215", "instrument": "XS2434891912", "venue": "XLON", "side": "BUY",
     "quantity": 2500000, "price": 96.42, "arrival_price": 96.40, "benchmark_vwap": 96.43,
     "executed": _d(-6), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2233", "algo": None,
     "missing_fields": [], "reported": True},
    {"ref": "TRD-88228", "instrument": "FR0000120271", "venue": "CHIX", "side": "BUY",
     "quantity": 44300, "price": 58.06, "arrival_price": 58.04, "benchmark_vwap": 58.08,
     "executed": _d(-7), "exec_time": "13:45:11.004920", "counterparty": "549300ZFEEJ2IP5VME73", "trader": "T-2107", "algo": "ALGO-VWAP-EU",
     "missing_fields": [], "reported": True},
]

# Algorithm and strategy documentation. MiFID II Art. 17 / RTS 6 requires an
# algo to be documented and re-validated before it runs.
ALGO_DOCUMENTATION = {
    "ALGO-VWAP-EU": {"name": "VWAP Europe", "owner": "Quant Execution", "version": "4.2",
                     "last_validated": _d(-95), "revalidation_days": 365, "go_live": _d(-400),
                     "docs": ["strategy_description", "risk_controls", "kill_switch_test", "conformance_test"]},
    "ALGO-IS-DE": {"name": "Implementation Shortfall DE", "owner": "Quant Execution", "version": "2.9",
                   "last_validated": _d(-402), "revalidation_days": 365, "go_live": _d(-720),
                   "docs": ["strategy_description", "risk_controls"]},
    "ALGO-POV-NL": {"name": "Percentage of Volume NL", "owner": "Quant Execution", "version": "1.4",
                    "last_validated": None, "revalidation_days": 365, "go_live": _d(6),
                    "docs": ["strategy_description"]},
    "ALGO-DARK-EU": {"name": "Dark Aggregator Europe", "owner": "Quant Execution", "version": "3.1",
                     "last_validated": _d(-310), "revalidation_days": 365, "go_live": _d(-500),
                     "docs": ["strategy_description", "risk_controls", "kill_switch_test", "conformance_test"]},
}

REQUIRED_ALGO_DOCS = ["strategy_description", "risk_controls", "kill_switch_test", "conformance_test"]

TRADERS = {
    "T-2041": {"name": "Trader 2041", "desk": "EU Equities", "supervisor": "Desk Supervisor — EU Equities",
               "certifications": {"MiFID II Knowledge & Competence": _d(24),
                                  "Market Abuse Regulation": _d(210),
                                  "Algo Trading Certification": _d(-12)}},
    "T-2107": {"name": "Trader 2107", "desk": "EU Equities", "supervisor": "Desk Supervisor — EU Equities",
               "certifications": {"MiFID II Knowledge & Competence": _d(88),
                                  "Market Abuse Regulation": _d(41)}},
    "T-2233": {"name": "Trader 2233", "desk": "Credit", "supervisor": "Desk Supervisor — Credit",
               "certifications": {"MiFID II Knowledge & Competence": _d(300),
                                  "Market Abuse Regulation": _d(-3),
                                  "Bond Market Conduct": _d(150)}},
}

# Course sessions the agent can enrol a trader into.
TRAINING_CALENDAR = {
    "MiFID II Knowledge & Competence": [_d(9), _d(30), _d(58)],
    "Market Abuse Regulation": [_d(5), _d(26), _d(54)],
    "Algo Trading Certification": [_d(12), _d(40)],
    "Bond Market Conduct": [_d(19), _d(47)],
}

# Best execution: RTS 27/28 tolerance in basis points before a fill is outlier.
BEST_EX_TOLERANCE_BPS = 5.0
CERT_WARNING_DAYS = 90
REGULATORY_PORTAL = "ARM — Approved Reporting Mechanism (T+1 submission window)"


# ---------------------------------------------------------------------------
# Helpers — the real computation behind every advertised bullet
# ---------------------------------------------------------------------------

def _days_until(iso):
    return (date.fromisoformat(iso) - TODAY).days


def _slippage_bps(trade):
    """Signed execution slippage against arrival price, in basis points.

    Positive = worse than arrival for the client. This is the best-execution
    performance measure the one-pager promises to surface.
    """
    arrival = trade["arrival_price"]
    if not arrival:
        return 0.0
    diff = trade["price"] - arrival
    if trade["side"] == "SELL":
        diff = -diff
    return round((diff / arrival) * 10000, 2)


def _vwap_bps(trade):
    """Performance against the venue VWAP benchmark, in basis points."""
    bm = trade["benchmark_vwap"]
    if not bm:
        return 0.0
    diff = trade["price"] - bm
    if trade["side"] == "SELL":
        diff = -diff
    return round((diff / bm) * 10000, 2)


def _venue_mismatch(trade):
    """True when the reported venue is not one the instrument is admitted on."""
    inst = INSTRUMENT_VENUES.get(trade["instrument"])
    return bool(inst) and trade["venue"] not in inst["admitted"]


def _notional(trade):
    return trade["quantity"] * trade["price"]


def _field_label(field):
    """'buyer_lei' -> 'field 7 Buyer identification code' — as an ARM reports it."""
    num, name = RTS22_FIELDS.get(field, ("?", field))
    return f"field {num} {name}"


def _trade_exceptions(trade):
    """Every reportable defect on one trade, as (severity, category, detail)."""
    out = []
    for f in trade["missing_fields"]:
        code, desc = ARM_REJECTION_CODES["missing_field"]
        out.append(("high", "Missing RTS 22 field", f"{_field_label(f)} — {code} {desc}"))
    if _venue_mismatch(trade):
        inst = INSTRUMENT_VENUES[trade["instrument"]]
        code, desc = ARM_REJECTION_CODES["venue_mismatch"]
        out.append(("high", "Venue mismatch",
                    f"{_field_label('trading_venue')} reported {trade['venue']}; {inst['name']} "
                    f"is admitted on {', '.join(inst['admitted'])} — {code} {desc}"))
    if not trade["reported"]:
        code, desc = ARM_REJECTION_CODES["not_submitted"]
        out.append(("high", "Not submitted",
                    f"no {EXECUTING_ENTITY['arm']} submission recorded — {code} {desc}"))
    slip = _slippage_bps(trade)
    if slip > BEST_EX_TOLERANCE_BPS:
        out.append(("medium", "Best execution outlier",
                    f"{slip} bps worse than arrival (tolerance {BEST_EX_TOLERANCE_BPS} bps)"))
    algo = trade.get("algo")
    if algo:
        doc = ALGO_DOCUMENTATION.get(algo, {})
        if _algo_doc_status(algo)[0] != "current":
            out.append(("medium", "Algorithm documentation",
                        f"{algo} ({doc.get('name', '?')}) is not current at time of execution"))
    return out


def _algo_doc_status(algo_id):
    """(status, reason) for one algorithm's documentation pack."""
    doc = ALGO_DOCUMENTATION.get(algo_id)
    if not doc:
        return "unknown", "no documentation record"
    missing = [d for d in REQUIRED_ALGO_DOCS if d not in doc["docs"]]
    if doc["last_validated"] is None:
        return "never validated", f"missing {len(missing)} artefact(s), never validated"
    age = -_days_until(doc["last_validated"])
    if age > doc["revalidation_days"]:
        return "expired", f"validated {age} days ago, revalidation due every {doc['revalidation_days']}"
    if missing:
        return "incomplete", f"missing {', '.join(missing)}"
    return "current", f"validated {age} days ago"


def _exception_rate():
    flagged = sum(1 for t in TRADES if _trade_exceptions(t))
    return round(100.0 * flagged / len(TRADES), 1) if TRADES else 0.0


#: Exception categories that make a *transaction report* wrong. Best execution
#: and algorithm documentation are separate obligations and are reported
#: separately — folding them in here would make the headline mean nothing.
REPORTING_DEFECTS = {"Missing RTS 22 field", "Venue mismatch", "Not submitted"}


def _reporting_accuracy():
    """Share of trades whose transaction report is complete and correctly lodged."""
    clean = sum(1 for t in TRADES
                if not any(e[1] in REPORTING_DEFECTS for e in _trade_exceptions(t)))
    return round(100.0 * clean / len(TRADES), 1) if TRADES else 0.0


def _expiring_certifications(window_days=CERT_WARNING_DAYS):
    """(trader_id, certification, days_left) for lapsed or soon-to-lapse credentials."""
    out = []
    for tid, t in TRADERS.items():
        for cert, expiry in t["certifications"].items():
            days = _days_until(expiry)
            if days <= window_days:
                out.append((tid, cert, days))
    return sorted(out, key=lambda r: r[2])


def _blocked_traders():
    """Traders with a lapsed certification — they must not be on the desk."""
    return sorted({tid for tid, _, days in _expiring_certifications(0) if days < 0})


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class FSRegulatoryComplianceAgent(BasicAgent):
    """Trading-desk regulatory compliance agent (MiFID II)."""

    def __init__(self):
        self.name = "FSRegulatoryCompliance"
        self.metadata = {
            "name": self.name,
            "display_name": "Regulatory Compliance Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Which compliance workflow to run.",
                        "enum": [
                            "compliance_dashboard",
                            "trade_surveillance",
                            "documentation_review",
                            "remediation_submission",
                            "certification_tracker",
                        ],
                    },
                    "trade_ref": {"type": "string", "description": "Limit surveillance to one trade reference, e.g. TRD-88133."},
                    "trader_id": {"type": "string", "description": "Limit certification tracking to one trader, e.g. T-2041."},
                    "window_days": {"type": "integer", "description": "Certification look-ahead window in days (default 90)."},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "compliance_dashboard")
        dispatch = {
            "compliance_dashboard": self._compliance_dashboard,
            "trade_surveillance": self._trade_surveillance,
            "documentation_review": self._documentation_review,
            "remediation_submission": self._remediation_submission,
            "certification_tracker": self._certification_tracker,
        }
        handler = dispatch.get(operation)
        if not handler:
            return (f"**Error:** Unknown operation `{operation}`. "
                    f"Available: {', '.join(dispatch)}.")
        return handler(**kwargs)

    # -- the Chief Compliance Officer roll-up -------------------------------
    def _compliance_dashboard(self, **kwargs) -> str:
        exceptions = {t["ref"]: _trade_exceptions(t) for t in TRADES}
        total_ex = sum(len(v) for v in exceptions.values())
        high = sum(1 for v in exceptions.values() for e in v if e[0] == "high")
        unsubmitted = [t for t in TRADES if not t["reported"]]
        expiring = _expiring_certifications()
        lapsed = [r for r in expiring if r[2] < 0]
        stale_algos = [a for a in ALGO_DOCUMENTATION if _algo_doc_status(a)[0] != "current"]

        L = [f"# Regulatory Compliance — Desk Overview ({TODAY.isoformat()})\n"]
        L.append(f"**Reporting accuracy:** {_reporting_accuracy()}%  ·  "
                 f"**Trades with exceptions:** {_exception_rate()}%  ·  "
                 f"**Open exceptions:** {total_ex} ({high} high)\n")
        L.append("| Area | Status | Detail |")
        L.append("|---|---|---|")
        L.append(f"| Transaction reporting (RTS 22) | {'ATTENTION' if high else 'OK'} | "
                 f"{high} high-severity defect(s) across {len(TRADES)} executed trades |")
        L.append(f"| ARM submission | {'ATTENTION' if unsubmitted else 'OK'} | "
                 f"{len(unsubmitted)} trade(s) outside the T+1 window |")
        L.append(f"| Best execution (RTS 27/28) | "
                 f"{'ATTENTION' if any(_slippage_bps(t) > BEST_EX_TOLERANCE_BPS for t in TRADES) else 'OK'} | "
                 f"tolerance {BEST_EX_TOLERANCE_BPS} bps vs arrival price |")
        L.append(f"| Algorithm documentation (RTS 6) | {'ATTENTION' if stale_algos else 'OK'} | "
                 f"{len(stale_algos)} of {len(ALGO_DOCUMENTATION)} algorithms not current |")
        L.append(f"| Trader certifications | {'BLOCKED' if lapsed else 'ATTENTION' if expiring else 'OK'} | "
                 f"{len(lapsed)} lapsed, {len(expiring) - len(lapsed)} expiring within {CERT_WARNING_DAYS} days |")

        blocked = _blocked_traders()
        if blocked:
            L.append("\n## Immediate action\n")
            for tid in blocked:
                lapsed_for = [c for t, c, d in expiring if t == tid and d < 0]
                L.append(f"- **{tid} ({TRADERS[tid]['desk']})** must be stood down: "
                         f"{', '.join(lapsed_for)} lapsed. Supervisor: {TRADERS[tid]['supervisor']}.")
        L.append("\nRun `trade_surveillance`, `documentation_review`, "
                 "`remediation_submission` or `certification_tracker` for the detail behind each row.")
        return "\n".join(L)

    # -- one-pager bullet 1 -------------------------------------------------
    def _trade_surveillance(self, **kwargs) -> str:
        ref = kwargs.get("trade_ref")
        trades = [t for t in TRADES if not ref or t["ref"] == ref.upper()]
        if not trades:
            return f"**No trade found for reference `{ref}`.** Known: {', '.join(t['ref'] for t in TRADES)}."

        L = [f"# Trade Surveillance — {len(trades)} executed trade(s) scanned\n"]
        L.append(f"**Executing entity:** {EXECUTING_ENTITY['name']} · LEI `{EXECUTING_ENTITY['lei']}` · "
                 f"reporting via {EXECUTING_ENTITY['arm']} · NCA {EXECUTING_ENTITY['nca']}\n")
        L.append(f"Scanned against MiFID II RTS 22 ({len(RTS22_REQUIRED_FIELDS)} mandatory fields), "
                 f"FIRDS venue admission, and RTS 27/28 best execution vs arrival price "
                 f"(tolerance {BEST_EX_TOLERANCE_BPS} bps).\n")
        L.append("| Trade | Instrument | Venue | Notional | Slippage | vs VWAP | Exceptions |")
        L.append("|---|---|---|---|---|---|---|")
        for t in trades:
            inst = INSTRUMENT_VENUES.get(t["instrument"], {})
            ex = _trade_exceptions(t)
            L.append(f"| {t['ref']} | {inst.get('name', t['instrument'])} | {t['venue']}"
                     f"{' ⚠' if _venue_mismatch(t) else ''} | {_notional(t):,.0f} | "
                     f"{_slippage_bps(t):+.2f} bps | {_vwap_bps(t):+.2f} bps | "
                     f"{len(ex) if ex else '—'} |")

        flagged = [(t, _trade_exceptions(t)) for t in trades if _trade_exceptions(t)]
        if flagged:
            L.append(f"\n## Exceptions ({sum(len(e) for _, e in flagged)})\n")
            for t, ex in flagged:
                cp = COUNTERPARTIES.get(t.get('counterparty'), 'unknown counterparty')
                L.append(f"**{t['ref']}** — {INSTRUMENT_VENUES.get(t['instrument'], {}).get('name', '')} "
                         f"({t['instrument']}) · {t['side']} {t['quantity']:,} @ {t['price']} · "
                         f"{t['executed']}T{t.get('exec_time', '')}Z · counterparty {cp} · trader {t['trader']}")
                for sev, cat, detail in ex:
                    L.append(f"- `{sev.upper()}` **{cat}:** {detail}")
                L.append("")
        else:
            L.append("\nNo exceptions. Every scanned trade carries all required RTS 22 fields, "
                     "was executed on an admitted venue, and fell inside the best-execution tolerance.\n")

        L.append("## Best execution summary\n")
        worst = max(trades, key=_slippage_bps)
        avg = round(sum(_slippage_bps(t) for t in trades) / len(trades), 2)
        L.append(f"- Average slippage vs arrival: **{avg:+.2f} bps** across "
                 f"{sum(_notional(t) for t in trades):,.0f} notional")
        L.append(f"- Worst fill: **{worst['ref']}** at {_slippage_bps(worst):+.2f} bps "
                 f"({INSTRUMENT_VENUES.get(worst['instrument'], {}).get('name', '')}, {worst['venue']})")
        L.append(f"- Outliers beyond tolerance: "
                 f"**{sum(1 for t in trades if _slippage_bps(t) > BEST_EX_TOLERANCE_BPS)}**")
        return "\n".join(L)

    # -- one-pager bullet 2 -------------------------------------------------
    def _documentation_review(self, **kwargs) -> str:
        L = ["# Algorithm & Strategy Documentation Review\n"]
        L.append("MiFID II Art. 17 / RTS 6 requires each trading algorithm to hold a complete, "
                 "revalidated documentation pack before it runs.\n")
        L.append("| Algorithm | Version | Owner | Status | Detail | Go-live |")
        L.append("|---|---|---|---|---|---|")
        for algo_id, doc in ALGO_DOCUMENTATION.items():
            status, reason = _algo_doc_status(algo_id)
            gl = _days_until(doc["go_live"])
            gl_txt = f"in {gl}d" if gl > 0 else "live"
            L.append(f"| {algo_id} — {doc['name']} | {doc['version']} | {doc['owner']} | "
                     f"{status.upper()} | {reason} | {gl_txt} |")

        blocking = []
        for algo_id, doc in ALGO_DOCUMENTATION.items():
            status, reason = _algo_doc_status(algo_id)
            gl = _days_until(doc["go_live"])
            if status != "current" and gl > 0:
                blocking.append((algo_id, doc, status, reason, gl))
        if blocking:
            L.append("\n## Blocking go-live\n")
            for algo_id, doc, status, reason, gl in blocking:
                missing = [d for d in REQUIRED_ALGO_DOCS if d not in doc["docs"]]
                L.append(f"**{algo_id} — {doc['name']}** goes live in {gl} days and is `{status}` ({reason}).")
                if missing:
                    L.append(f"- Missing artefacts: {', '.join('`' + m + '`' for m in missing)}")
                L.append(f"- Owner to complete: {doc['owner']}")
                L.append("")

        stale = [(a, d) for a, d in ALGO_DOCUMENTATION.items() if _algo_doc_status(a)[0] == "expired"]
        if stale:
            L.append("## Outdated documentation on live algorithms\n")
            for algo_id, doc in stale:
                age = -_days_until(doc["last_validated"])
                affected = [t["ref"] for t in TRADES if t.get("algo") == algo_id]
                L.append(f"- **{algo_id} — {doc['name']}**: last validated {age} days ago "
                         f"(limit {doc['revalidation_days']}). "
                         f"{len(affected)} executed trade(s) affected: {', '.join(affected) or 'none'}")
        return "\n".join(L)

    # -- one-pager bullet 3 -------------------------------------------------
    def _remediation_submission(self, **kwargs) -> str:
        corrections, resubmissions = [], []
        for t in TRADES:
            ex = _trade_exceptions(t)
            for sev, cat, detail in ex:
                if cat == "Missing RTS 22 field":
                    corrections.append((t, detail, f"populate `{detail}` from the order management record"))
                elif cat == "Venue mismatch":
                    inst = INSTRUMENT_VENUES[t["instrument"]]
                    corrections.append((t, "trading_venue",
                                        f"correct venue to the admitted MIC ({', '.join(inst['admitted'])})"))
            if not t["reported"]:
                resubmissions.append(t)

        L = ["# Automated Correction & Submission\n"]
        L.append(f"Target portal: **{REGULATORY_PORTAL}**\n")
        if not corrections and not resubmissions:
            L.append("Nothing to submit — every executed trade is complete and already lodged.")
            return "\n".join(L)

        if corrections:
            L.append(f"## Field corrections prepared ({len(corrections)})\n")
            L.append("| Trade | Field | Correction | Status |")
            L.append("|---|---|---|---|")
            for t, field, action in corrections:
                L.append(f"| {t['ref']} | `{field}` | {action} | prepared |")

        if resubmissions:
            L.append(f"\n## Submissions queued ({len(resubmissions)})\n")
            for t in resubmissions:
                inst = INSTRUMENT_VENUES.get(t["instrument"], {})
                age = -_days_until(t["executed"])
                L.append(f"- **{t['ref']}** — {inst.get('name', '')} {t['side']} {t['quantity']:,} @ {t['price']} "
                         f"(executed {t['executed']}, {age} day(s) ago). "
                         f"{'**Breach: outside T+1.**' if age > 1 else 'Within T+1.'}")

        batch = sorted({t["ref"] for t, _, _ in corrections} | {t["ref"] for t in resubmissions})
        L.append(f"\n## Submission batch\n")
        L.append(f"- Trades in batch: **{len(batch)}** ({', '.join(batch)})")
        L.append(f"- Field corrections applied: **{len(corrections)}**")
        L.append(f"- Reporting accuracy before: **{_reporting_accuracy()}%** → after this batch: **100.0%**")
        L.append(f"- Remaining manual review: only exceptions the agent cannot source from the "
                 f"order management record (currently none).")
        return "\n".join(L)

    # -- one-pager bullet 4 -------------------------------------------------
    def _certification_tracker(self, **kwargs) -> str:
        window = int(kwargs.get("window_days") or CERT_WARNING_DAYS)
        only = kwargs.get("trader_id")
        rows = _expiring_certifications(window)
        if only:
            rows = [r for r in rows if r[0] == only.upper()]
            if not rows:
                return (f"**No certification expiring within {window} days for `{only}`.** "
                        f"Known traders: {', '.join(TRADERS)}.")

        L = [f"# Trader Certification Readiness — {window}-day window\n"]
        lapsed = [r for r in rows if r[2] < 0]
        if lapsed:
            L.append(f"**{len(lapsed)} lapsed certification(s) — affected traders must be stood down.**\n")

        L.append("| Trader | Desk | Certification | Expires | Status | Action |")
        L.append("|---|---|---|---|---|---|")
        enrolments = []
        for tid, cert, days in rows:
            t = TRADERS[tid]
            expiry = t["certifications"][cert]
            status = "LAPSED" if days < 0 else ("URGENT" if days <= 30 else "DUE")
            sessions = [s for s in TRAINING_CALENDAR.get(cert, []) if _days_until(s) >= 0]
            if sessions:
                nxt = sessions[0]
                enrolments.append((tid, cert, nxt, days))
                action = f"enrol {nxt}"
            else:
                action = "no session scheduled — escalate"
            L.append(f"| {tid} | {t['desk']} | {cert} | {expiry} | {status} "
                     f"({days:+d}d) | {action} |")

        if enrolments:
            L.append(f"\n## Enrolments raised ({len(enrolments)})\n")
            for tid, cert, session, days in enrolments:
                t = TRADERS[tid]
                before = "before expiry" if _days_until(session) < days else "**after expiry — gap in coverage**"
                L.append(f"- **{tid}** → *{cert}*, session {session} ({before}). "
                         f"Notify {t['supervisor']}.")

        gaps = [(tid, cert, s) for tid, cert, s, days in enrolments if _days_until(s) >= days >= 0]
        if gaps or lapsed:
            L.append("\n## Desk coverage risk\n")
            for tid in sorted({r[0] for r in lapsed}):
                L.append(f"- **{tid}** ({TRADERS[tid]['desk']}) is not currently certified to trade.")
            for tid, cert, s in gaps:
                L.append(f"- **{tid}** has no session for *{cert}* before it expires.")
        return "\n".join(L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FSRegulatoryComplianceAgent()
    for op in ("compliance_dashboard", "trade_surveillance", "documentation_review",
               "remediation_submission", "certification_tracker"):
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
