"""
Regulatory Compliance Agent — Financial Services Stack

Implements the published AIBAST one-pager "Regulatory Compliance Agent"
(advertised solution #40) and its demo session: a Chief Compliance Officer
reviews last quarter's 12,000 trades for MiFID II compliance, works the 24
transaction-report exceptions, stages the batch amendment, closes the algo
documentation gaps on Strategy #5, checks best execution by venue, tracks
trader certifications and ends with an executive report.

The one-pager promises:

  1. Scan all executed trades for reporting accuracy, required fields, and
     best-execution performance   -> "trade_surveillance", "best_execution_analysis"
  2. Flag missing or outdated documentation -> "documentation_review"
  3. Automate corrections and submissions to the regulatory portal
                                   -> "remediation_submission" (staged, never transmitted)
  4. Identify upcoming certification expirations and enroll traders
                                   -> "certification_tracker"

plus the roll-ups "compliance_dashboard" (the default) and "executive_summary".

Everything is a fixed synthetic quarter: no current-date dependence, no
connection to an order management system, ARM, FCA portal or LMS.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fs-regulatory-compliance",
    "version": "2.1.0",
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

# ---------------------------------------------------------------------------
# Synthetic domain data — one quarter on a trading desk
# ---------------------------------------------------------------------------

EXECUTING_ENTITY = {
    "name": "Northgate Asset Management LLP",
    "lei": "549300XKQZ2P4NLK7T18",
    "regulator": "FCA",
    "portal": "FCA transaction reporting via the firm's ARM",
}

DESK_SUMMARY = {
    "period": "last quarter",
    "trades": 12000,
    "client_trades": 8432,
    "traders": 12,
    "market_making_uptime_pct": 98.5,
    "market_making_obligation_pct": 95.0,
    "batch_minutes": 8,
    "penalty_exposure_avoided_gbp": 847000,
}

# Transaction-report exceptions by category: [issue, trades, auto_fix, priority]
ISSUE_CATEGORIES = [
    ["Venue ID mismatch", 11, True, "High"],
    ["Counterparty LEI", 8, True, "High"],
    ["Timestamp format", 4, True, "Medium"],
    ["Manual review needed", 1, False, "Critical"],
]

# Sample exceptions behind the categories (the full 24 live in the trade repository).
EXCEPTION_SAMPLES = [
    {"trade_id": "APX-2024-8847", "issue": "Manual review needed", "detail": "Counterparty LEI expired during settlement", "client": "Standard National Bank", "resolution": "Updated LEI required from client"},
    {"trade_id": "APX-2024-8812", "issue": "Venue ID mismatch", "detail": "Reported XPAR; instrument admitted on XLON", "client": "Meridian Pension Trustees", "resolution": "Correct venue to XLON"},
    {"trade_id": "APX-2024-8829", "issue": "Counterparty LEI", "detail": "Buyer LEI field empty", "client": "Halden Life Assurance", "resolution": "Populate LEI from client master"},
    {"trade_id": "APX-2024-8853", "issue": "Timestamp format", "detail": "Trading time not in UTC microseconds", "client": "Cavendish Multi-Asset Fund", "resolution": "Reformat to ISO 8601 UTC"},
]

ALGO_STRATEGIES = [
    {"number": 1, "id": "ALGO-VWAP-EU", "name": "VWAP Europe", "status": "live", "docs": ["pre_trade_testing", "stress_scenarios", "kill_switch_test", "audit_trail"]},
    {"number": 2, "id": "ALGO-IS-EU", "name": "Implementation Shortfall", "status": "live", "docs": ["pre_trade_testing", "stress_scenarios", "kill_switch_test", "audit_trail"]},
    {"number": 3, "id": "ALGO-POV-EU", "name": "Percentage of Volume", "status": "live", "docs": ["pre_trade_testing", "stress_scenarios", "kill_switch_test", "audit_trail"]},
    {"number": 4, "id": "ALGO-DARK-EU", "name": "Dark Aggregator", "status": "live", "docs": ["pre_trade_testing", "stress_scenarios", "kill_switch_test", "audit_trail"]},
    {"number": 5, "id": "ALGO-MOM-05", "name": "Momentum algo", "status": "pre-deployment", "docs": ["kill_switch_test", "audit_trail"],
     "deadline": "End of week", "revenue_at_risk_gbp": 2100000,
     "actions": ["Complete 12-month backtest with volatility scenarios",
                 "Document circuit breaker triggers (currently at 5% daily loss)",
                 "Obtain Quant team sign-off",
                 "File with compliance register"]},
]

REQUIRED_ALGO_DOCS = [
    ["pre_trade_testing", "Pre-trade testing"],
    ["stress_scenarios", "Stress scenarios"],
    ["kill_switch_test", "Kill switch test"],
    ["audit_trail", "Audit trail"],
]

# [metric, result, benchmark, unit, higher_is_better]
BEST_EX_METRICS = [
    ["Within best bid/offer", 97.0, 95.0, "%", True],
    ["Optimal venue selection", 94.0, 90.0, "%", True],
    ["Average slippage", 2.3, 3.0, " bps", False],
    ["Execution speed", 42.0, 100.0, " ms", False],
]

VENUE_PERFORMANCE = [
    ["LSE (London)", 4247, 98.2],
    ["BATS Europe", 2156, 96.8],
    ["Chi-X", 1589, 95.1],
    ["Turquoise", 440, 93.4],
]

TRADERS = [
    {"name": "James Morrison", "certification": "MiFID II Algo", "expires_in_days": 15, "action": "Enrollment in next week's recertification prepared"},
    {"name": "Sarah Chen", "certification": "Best Execution", "expires_in_days": 22, "action": "Reminder drafted, session proposed"},
    {"name": "Michael Torres", "certification": "Transaction Reporting", "expires_in_days": 28, "action": "Reminder drafted, session proposed"},
    {"name": "Lisa Wong", "certification": "Market Abuse", "expires_in_days": 180, "action": "None needed"},
]

TRAINING = {
    "fully_current": 11,
    "assessment_avg_pct": 94,
    "next_refresh_days": 45,
    "aml_current": 12,
    "penalty_per_uncertified_gbp": 50000,
}

CERT_WINDOW_DAYS = 30

_OPERATIONS = [
    "compliance_dashboard",
    "trade_surveillance",
    "documentation_review",
    "remediation_submission",
    "certification_tracker",
    "best_execution_analysis",
    "executive_summary",
]

_BOUNDARY = (
    "This synthetic pilot identifies at-risk areas and control gaps only. It cannot determine whether an "
    "audit will pass or fail and does not provide legal or regulatory advice."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exceptions():
    total = 0
    for row in ISSUE_CATEGORIES:
        total += row[1]
    return total


def _auto_fixable():
    total = 0
    for row in ISSUE_CATEGORIES:
        if row[2]:
            total += row[1]
    return total


def _reporting_pct():
    return round((DESK_SUMMARY["trades"] - _exceptions()) * 100 / DESK_SUMMARY["trades"], 1)


def _algo_complete():
    done = 0
    for s in ALGO_STRATEGIES:
        if len(s["docs"]) == len(REQUIRED_ALGO_DOCS):
            done += 1
    return done


def _gap_strategy():
    for s in ALGO_STRATEGIES:
        if len(s["docs"]) < len(REQUIRED_ALGO_DOCS):
            return s
    return None


def _cert_status(days):
    if days < 0:
        return "LAPSED"
    if days <= 15:
        return "Urgent"
    if days <= CERT_WINDOW_DAYS:
        return "Soon"
    return "Current"


def _expiry_text(days):
    if days >= 180:
        return f"{days // 30} months"
    return f"{days} days"


def _due_soon():
    return [t for t in TRADERS if t["expires_in_days"] <= CERT_WINDOW_DAYS]


def _lapsed():
    return [t for t in TRADERS if t["expires_in_days"] < 0]


def _team_pct():
    return round(TRAINING["fully_current"] * 100 / DESK_SUMMARY["traders"])


def _best_ex_status(result, benchmark, higher, unit):
    if higher:
        return "Exceeds" if result > benchmark else "Below"
    if result >= benchmark:
        return "Above limit"
    return "Met" if unit == " ms" else "Better"


def _fmt(value, unit):
    text = f"{value:g}"
    return f"{text}{unit}"


def _gbp(value):
    if value >= 1000000:
        return f"£{value / 1000000:.1f}M"
    return f"£{value // 1000}K"


def _risk(score):
    return "Low" if score >= 95 else "Medium"


def _algo_gap_table(strategy):
    lines = ["| Requirement | Status | Deadline |", "|---|---|---|"]
    for key, label in REQUIRED_ALGO_DOCS:
        if key in strategy["docs"]:
            lines.append(f"| {label} | Complete | - |")
        else:
            lines.append(f"| {label} | Missing | {strategy['deadline']} |")
    return lines


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
            "description": (
                "A synthetic trading-desk regulatory compliance pilot under MiFID II / MiFIR. "
                "Use this to review trading desk activities for MiFID II compliance (the demo quarter: "
                "12,000 trades with new algo strategies), the transaction reporting issues, executing "
                "or staging the batch fix, algo documentation gaps, best execution analysis by venue, "
                "trader certifications and training gaps, and the executive compliance report. Also "
                "use it for audit readiness, regulator validation or rejection issues, and whether an "
                "algorithm is about to go live. For audit questions, identify at-risk areas and control "
                "gaps only: never state that an audit will pass or fail, and never present the result as "
                "legal or regulatory advice. The remediation workflow prepares synthetic correction and "
                "submission payloads for authorized review; it never changes external records or "
                "transmits to an ARM portal. Route natural-language questions even when they do not name "
                "a regulation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Which compliance workflow to run. "
                            "compliance_dashboard: review trading desk activities for MiFID II compliance; "
                            "the whole-desk roll-up of at-risk areas and control gaps; never predict an audit "
                            "pass or failure. "
                            "trade_surveillance: the detailed breakdown of the transaction reporting issues "
                            "(venue, LEI, timestamp, manual review) or which trades the regulator would reject. "
                            "remediation_submission: execute or stage the batch fix / amendment, plus the algo "
                            "documentation gaps; prepare synthetic correction and submission payloads for "
                            "authorized compliance review; never file, transmit, or change an external ARM record. "
                            "documentation_review: algo or strategy documentation gaps, or whether anything is "
                            "about to go live that shouldn't. "
                            "best_execution_analysis: best execution results, venue ranking and the RTS 28 report. "
                            "certification_tracker: trader certifications, expirations and training gaps. "
                            "executive_summary: the executive compliance report and summary of what was accomplished."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "trade_ref": {"type": "string", "description": "Limit surveillance to one trade, e.g. APX-2024-8847."},
                    "trader_id": {"type": "string", "description": "Limit certification tracking to one trader name, e.g. James Morrison."},
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
            "best_execution_analysis": self._best_execution_analysis,
            "executive_summary": self._executive_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return (f"**Error:** Unknown operation `{operation}`. "
                    f"Available: {', '.join(dispatch)}.")
        return handler(**kwargs)

    # -- video turn 1 --------------------------------------------------------
    def _compliance_dashboard(self, **kwargs) -> str:
        d = DESK_SUMMARY
        gap = _gap_strategy()
        due = _due_soon()
        lapsed = _lapsed()
        risk = "LOW RISK - technical deficiencies only, no material violations" if not lapsed else "AT RISK - lapsed certifications"
        L = [f"# MiFID II Compliance Review — {d['trades']:,} trades ({d['period']})\n"]
        L.append(
            f"Analyzed all {d['trades']:,} trades against MiFID II requirements. Overall compliance is "
            f"{_reporting_pct()}% with {_exceptions()} trades requiring amendment.\n"
        )
        L.append("| Requirement | Status | Compliance |\n|---|---|---|")
        L.append(f"| Transaction Reporting | {d['trades'] - _exceptions():,} filed on time | {_reporting_pct()}% |")
        L.append(f"| Best Execution | {d['client_trades']:,} client trades | {BEST_EX_METRICS[0][1]:g}% within best bid/offer |")
        L.append(f"| Algo Testing Docs | {_algo_complete()} of {len(ALGO_STRATEGIES)} complete | {_algo_complete() * 100 // len(ALGO_STRATEGIES)}% |")
        L.append(f"| Market Making Uptime | {d['market_making_uptime_pct']}% achieved | obligation {d['market_making_obligation_pct']}% |")
        L.append("\n**Critical findings (control gaps):**\n")
        L.append(f"- {_exceptions()} transaction reports need amendment by end of day "
                 f"({_auto_fixable()} auto-fixable)")
        for s in EXCEPTION_SAMPLES:
            if s["issue"] == "Manual review needed":
                L.append(f"- 1 needs manual review: {s['trade_id']} ({s['client']}: {s['detail']})")
        if gap:
            L.append(f"- Strategy #{gap['number']} ({gap['name'].lower()}, {gap['id']}) missing testing documentation")
        L.append(f"- {len(due)} traders require updated certifications within {CERT_WINDOW_DAYS} days")
        L.append(f"\n**Audit-readiness assessment: {risk}.** The control gaps above require authorized review.\n")
        L.append(_BOUNDARY)
        L.append("\nSource: [GRC Platform + Compliance + Trade Surveillance] (synthetic)")
        L.append(f"\n**Next step:** see the detailed breakdown of the {_exceptions()} reporting issues?")
        return "\n".join(L)

    # -- video turn 2 --------------------------------------------------------
    def _trade_surveillance(self, **kwargs) -> str:
        ref = kwargs.get("trade_ref")
        if ref:
            hit = [s for s in EXCEPTION_SAMPLES if s["trade_id"].lower() == str(ref).lower().strip()]
            if not hit:
                return (f"**No exception found for trade `{ref}`;** no substitute record was used. "
                        f"Sample exceptions: {', '.join(s['trade_id'] for s in EXCEPTION_SAMPLES)}.")
            s = hit[0]
            return (f"# Trade {s['trade_id']}\n\n- Issue: {s['issue']} — {s['detail']}\n- Client: {s['client']}\n"
                    f"- Resolution: {s['resolution']}\n\nSynthetic record; no external record was changed.")
        L = [f"# Transaction Report Issues — {_exceptions()} trades\n"]
        L.append(
            f"The {_exceptions()} reporting issues are concentrated in cross-border trades with minor field "
            f"errors. Automated correction is available for {_auto_fixable()} of them.\n"
        )
        L.append("| Issue Type | Trades | Auto-Fix | Priority |\n|---|---|---|---|")
        for issue, count, auto, priority in ISSUE_CATEGORIES:
            L.append(f"| {issue} | {count} | {'Yes' if auto else 'No'} | {priority} |")
        for s in EXCEPTION_SAMPLES:
            if s["issue"] == "Manual review needed":
                L.append("\n**Critical Trade (Manual Review):**\n")
                L.append(f"- Trade ID: {s['trade_id']}")
                L.append(f"- Issue: {s['detail']}")
                L.append(f"- Client: {s['client']}")
                L.append(f"- Resolution: {s['resolution']}")
        L.append("\n**Sample corrections (from the trade repository):**\n")
        L.append("| Trade | Issue | Detail | Fix |\n|---|---|---|---|")
        for s in EXCEPTION_SAMPLES:
            if s["issue"] != "Manual review needed":
                L.append(f"| {s['trade_id']} | {s['issue']} | {s['detail']} | {s['resolution']} |")
        L.append("\n**Automated corrections ready:**\n")
        L.append(f"- {_auto_fixable()} trades can be amended in one batch")
        L.append(f"- Estimated processing: {DESK_SUMMARY['batch_minutes']} minutes")
        L.append(f"- Submission target: {EXECUTING_ENTITY['portal']}, after authorized approval")
        L.append("\nSource: [Trade Repository + LEI Database] (synthetic)")
        L.append("\n**Next step:** stage the batch amendment and show the algo strategy gaps?")
        return "\n".join(L)

    # -- video turn 3 --------------------------------------------------------
    def _remediation_submission(self, **kwargs) -> str:
        pending = [s for s in EXCEPTION_SAMPLES if s["issue"] == "Manual review needed"]
        L = ["# Batch Amendment — staged for approval\n"]
        L.append(
            "Synthetic dry run: correction and submission payloads are prepared for approval; no external "
            "record is changed and no filing is transmitted.\n"
        )
        L.append(f"**{_auto_fixable()} amendments staged** as correction reports for the {EXECUTING_ENTITY['regulator']} "
                 f"({EXECUTING_ENTITY['portal']}); reporting entity {EXECUTING_ENTITY['name']}, LEI "
                 f"`{EXECUTING_ENTITY['lei']}`.\n")
        L.append("| Issue Type | Trades | Payload |\n|---|---|---|")
        for issue, count, auto, _ in ISSUE_CATEGORIES:
            if auto:
                L.append(f"| {issue} | {count} | correction report |")
        for s in pending:
            L.append(f"\n**{len(pending)} trade pending:** {s['trade_id']} — {s['client']} must supply an updated "
                     f"LEI; it then goes as a new submission.")
        L.append(
            f"\n**Approval gate:** an authorized compliance reviewer approves the batch (about "
            f"{DESK_SUMMARY['batch_minutes']} minutes to process) before the ARM connector transmits it; the "
            "batch is ready for you to submit."
        )
        gap = _gap_strategy()
        if gap:
            L.append(f"\n## Algo Strategy #{gap['number']} Documentation Gaps ({gap['id']})\n")
            L.extend(_algo_gap_table(gap))
            L.append("\n**Required actions:**\n")
            for a in gap["actions"]:
                L.append(f"- {a}")
            L.append(
                f"\n**Risk if incomplete:** strategy cannot be deployed until documentation is filed. "
                f"Potential {_gbp(gap['revenue_at_risk_gbp'])} revenue impact."
            )
        L.append("\nSource: [Trade Repository + Algo Registry] (synthetic)")
        L.append("\n**Next step:** see the best execution analysis?")
        return "\n".join(L)

    # -- algo documentation --------------------------------------------------
    def _documentation_review(self, **kwargs) -> str:
        L = ["# Algorithm & Strategy Documentation Review\n"]
        L.append("MiFID II Art. 17 / RTS 6 requires each trading algorithm to hold a complete, "
                 "tested documentation pack before it runs.\n")
        L.append("| # | Strategy | Status | Docs complete |\n|---|---|---|---|")
        for s in ALGO_STRATEGIES:
            L.append(f"| {s['number']} | {s['id']} — {s['name']} | {s['status']} | "
                     f"{len(s['docs'])} of {len(REQUIRED_ALGO_DOCS)} |")
        gap = _gap_strategy()
        if gap:
            L.append(f"\n## Blocking go-live: Strategy #{gap['number']} ({gap['name'].lower()}, {gap['id']})\n")
            L.extend(_algo_gap_table(gap))
            L.append("\n**Required actions:**\n")
            for a in gap["actions"]:
                L.append(f"- {a}")
            L.append(
                f"\n**Risk if incomplete:** cannot deploy until documentation is filed; potential "
                f"{_gbp(gap['revenue_at_risk_gbp'])} revenue impact. Go-live needs Quant sign-off and authorized "
                "review; no deployment was changed or blocked by this pilot."
            )
        return "\n".join(L)

    # -- video turn 4 --------------------------------------------------------
    def _best_execution_analysis(self, **kwargs) -> str:
        top = BEST_EX_METRICS[0]
        L = [f"# Best Execution Summary ({DESK_SUMMARY['client_trades']:,} client trades)\n"]
        L.append(f"Best execution achieved {top[1]:g}% with {100 - top[1]:g}% of trades showing potential "
                 "execution quality issues.\n")
        L.append("| Metric | Result | Benchmark | Status |\n|---|---|---|---|")
        for metric, result, bench, unit, higher in BEST_EX_METRICS:
            mark = "" if higher else "<"
            L.append(f"| {metric} | {_fmt(result, unit)} | {mark}{_fmt(bench, unit)} | "
                     f"{_best_ex_status(result, bench, higher, unit)} |")
        L.append("\n**Venue Performance Ranking:**\n")
        n = 0
        total = 0
        for venue, trades, quality in VENUE_PERFORMANCE:
            n += 1
            total += trades
            L.append(f"{n}. {venue} - {trades:,} trades, {quality}% quality")
        L.append(f"\nVenue trades total {total:,}.")
        L.append(
            "\n**RTS 28 report:** quarterly report drafted with the top venue analysis, ready for your review "
            "before client distribution (not published)."
        )
        L.append("\nSource: [Execution Analytics + Venue Data] (synthetic)")
        L.append("\n**Next step:** show trader certification status and training requirements?")
        return "\n".join(L)

    # -- video turn 5 --------------------------------------------------------
    def _certification_tracker(self, **kwargs) -> str:
        only = kwargs.get("trader_id")
        rows = TRADERS
        if only:
            q = str(only).lower().strip()
            rows = [t for t in TRADERS if q in t["name"].lower()]
            if not rows:
                return (f"**No synthetic trader matches `{only}`;** no substitute record was used. "
                        f"Traders: {', '.join(t['name'] for t in TRADERS)}.")
        due = _due_soon()
        lapsed = _lapsed()
        L = ["# Trader Certification Status\n"]
        if lapsed:
            L.append(f"**{len(lapsed)} lapsed certification(s): those traders must stop trading pending authorized review.**\n")
        else:
            L.append(f"No trader is lapsed today; {len(due)} traders need certification renewal within "
                     f"{CERT_WINDOW_DAYS} days (by end of month).\n")
        L.append("| Trader | Certification | Expiry | Status |\n|---|---|---|---|")
        for t in rows:
            L.append(f"| {t['name']} | {t['certification']} | {_expiry_text(t['expires_in_days'])} | "
                     f"{_cert_status(t['expires_in_days'])} |")
        L.append("\n**Training actions (prepared for the desk supervisor to confirm):**\n")
        for t in rows:
            if t["expires_in_days"] <= CERT_WINDOW_DAYS:
                L.append(f"- {t['name']}: {t['action']}")
        L.append(f"- All {TRAINING['aml_current']} traders current on AML training")
        L.append("\n**Compliance Training Dashboard:**\n")
        L.append(f"- Team compliance rate: {_team_pct()}% ({TRAINING['fully_current']} of {DESK_SUMMARY['traders']} fully current; target 100%)")
        L.append(f"- Average score on assessments: {TRAINING['assessment_avg_pct']}%")
        L.append(f"- Next mandatory refresh: {TRAINING['next_refresh_days']} days")
        L.append(f"\n**Penalty risk:** {_gbp(TRAINING['penalty_per_uncertified_gbp'])}+ per uncertified trader operating.")
        L.append("\nNo enrollment was submitted and no message was sent; call the desk supervisor to confirm the sessions.")
        L.append("\nSource: [Learning Management + HR System] (synthetic)")
        L.append("\n**Next step:** generate the executive compliance report?")
        return "\n".join(L)

    # -- video turn 6 --------------------------------------------------------
    def _executive_summary(self, **kwargs) -> str:
        d = DESK_SUMMARY
        gap = _gap_strategy()
        algo_pct = _algo_complete() * 100 // len(ALGO_STRATEGIES)
        pending = [s for s in EXCEPTION_SAMPLES if s["issue"] == "Manual review needed"]
        L = ["# Executive Compliance Report (draft for leadership)\n"]
        L.append("**Session Summary:**\n")
        L.append(f"- Analyzed — {d['trades']:,} trades reviewed for MiFID II compliance ({_reporting_pct()}% compliant)")
        L.append(f"- Amended — {_auto_fixable()} transaction reports corrected and staged for {EXECUTING_ENTITY['regulator']} submission")
        if gap:
            L.append(f"- Identified — Strategy #{gap['number']} documentation gaps with resolution timeline ({gap['deadline'].lower()})")
        L.append(f"- Verified — best execution at {BEST_EX_METRICS[0][1]:g}% (exceeds {BEST_EX_METRICS[0][2]:g}% benchmark)")
        L.append(f"- Scheduled — {len(_due_soon())} trader recertifications with training sessions proposed")
        L.append("- Generated — RTS 28 quarterly report draft ready for review")
        L.append("\n**Compliance Scorecard:**\n")
        L.append("| Area | Score | Risk Level |\n|---|---|---|")
        L.append(f"| Transaction Reporting | {_reporting_pct()}% | {_risk(_reporting_pct())} |")
        L.append(f"| Best Execution | {BEST_EX_METRICS[0][1]:g}% | {_risk(BEST_EX_METRICS[0][1])} |")
        L.append(f"| Algo Compliance | {algo_pct}% | {_risk(algo_pct)} |")
        L.append(f"| Trader Certifications | {_team_pct()}% | {_risk(_team_pct())} |")
        L.append(f"\n**Remaining actions:** {len(pending)} trade pending LEI update, algo docs due end of week.")
        L.append(f"**Penalty exposure avoided (modeled):** {_gbp(d['penalty_exposure_avoided_gbp'])} in potential MiFID II fines.")
        L.append("\nThe report is a draft ready for you to share with leadership; nothing has been sent. " + _BOUNDARY)
        L.append("\nSource: [All connected systems] (synthetic)")
        return "\n".join(L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FSRegulatoryComplianceAgent()
    for op in ("compliance_dashboard", "trade_surveillance", "remediation_submission",
               "best_execution_analysis", "certification_tracker", "executive_summary"):
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
