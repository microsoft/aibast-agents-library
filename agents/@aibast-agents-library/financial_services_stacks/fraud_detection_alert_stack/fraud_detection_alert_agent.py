"""
Fraud Detection & Alert Agent — Financial Services Stack

Provides alert triage, transaction analysis, pattern detection, and
investigation summaries for financial fraud operations teams.

Demo scenario (synthetic): a bank's 1,247-alert overnight queue. The agent
triages the queue, detects three organized rings, investigates the 12-account
takeover ring, prepares cases FRD-2024-1847..1849 with a proposed protective
action plan, reports prevention performance and trends, and summarizes the
morning with action items. Protective actions are proposals awaiting
authorized execution; nothing is blocked, sent or filed by the agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fraud-detection-alert",
    "version": "1.0.0",
    "display_name": "Fraud Detection and Alert Agent",
    "description": "Deploy AI-driven fraud monitoring and identification to accelerate investigations, enhance detection rates, and improve prevention.",
    "author": "AIBAST",
    "tags": ["fraud", "detection", "alerts", "transactions", "investigation", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

TRANSACTIONS = {
    "TXN-90001": {"account": "4532-XXXX-8891", "cardholder": "James Peterson", "amount": 4850.00, "merchant": "ElectroMax Dubai", "category": "electronics", "country": "AE", "timestamp": "2025-03-05T02:15:00", "channel": "card_present", "risk_score": 88},
    "TXN-90002": {"account": "4532-XXXX-8891", "cardholder": "James Peterson", "amount": 2100.00, "merchant": "Gold Souq Trading", "category": "jewelry", "country": "AE", "timestamp": "2025-03-05T02:42:00", "channel": "card_present", "risk_score": 92},
    "TXN-90003": {"account": "4716-XXXX-3304", "cardholder": "Lisa Wang", "amount": 12500.00, "merchant": "CryptoSwap Exchange", "category": "crypto", "country": "US", "timestamp": "2025-03-04T18:30:00", "channel": "online", "risk_score": 75},
    "TXN-90004": {"account": "4716-XXXX-3304", "cardholder": "Lisa Wang", "amount": 9800.00, "merchant": "CryptoSwap Exchange", "category": "crypto", "country": "US", "timestamp": "2025-03-04T18:35:00", "channel": "online", "risk_score": 82},
    "TXN-90005": {"account": "5412-XXXX-6678", "cardholder": "Robert Miles", "amount": 189.99, "merchant": "Amazon.com", "category": "retail", "country": "US", "timestamp": "2025-03-05T10:20:00", "channel": "online", "risk_score": 12},
    "TXN-90006": {"account": "5412-XXXX-6678", "cardholder": "Robert Miles", "amount": 3200.00, "merchant": "WireTransfer-NG", "category": "wire_transfer", "country": "NG", "timestamp": "2025-03-05T11:05:00", "channel": "online", "risk_score": 95},
    "TXN-90007": {"account": "4024-XXXX-1190", "cardholder": "Elena Vasquez", "amount": 67.50, "merchant": "Whole Foods Market", "category": "grocery", "country": "US", "timestamp": "2025-03-05T09:15:00", "channel": "contactless", "risk_score": 5},
}

ALERT_RULES = {
    "RULE-001": {"name": "Velocity Check", "description": "Multiple high-value transactions within 1 hour", "threshold": "2+ transactions over $1,000 within 60 minutes", "severity": "high"},
    "RULE-002": {"name": "Geographic Anomaly", "description": "Transaction in country with no prior history", "threshold": "First transaction in high-risk country", "severity": "high"},
    "RULE-003": {"name": "Crypto Purchase Spike", "description": "Unusual crypto exchange activity", "threshold": "Crypto transactions exceeding 3x normal volume", "severity": "medium"},
    "RULE-004": {"name": "Wire to High-Risk Country", "description": "Wire transfer to FATF grey/black list country", "threshold": "Any wire to listed jurisdiction", "severity": "critical"},
    "RULE-005": {"name": "Card-Not-Present Velocity", "description": "Rapid online purchases across merchants", "threshold": "5+ online transactions within 30 minutes", "severity": "medium"},
    "RULE-006": {"name": "Account Takeover Pattern", "description": "Password change followed by high-value transaction", "threshold": "Transaction within 2 hours of credential change", "severity": "critical"},
}

FRAUD_PATTERNS = {
    "card_cloning": {"description": "Physical card duplicated; used at multiple locations simultaneously", "indicators": ["Transactions in geographically distant locations within short timeframe", "Card-present transactions after reported card-not-present use"], "frequency": "common"},
    "account_takeover": {"description": "Unauthorized access to account via compromised credentials", "indicators": ["Login from new device/IP", "Immediate password and contact info change", "Large transfer or purchase within hours"], "frequency": "increasing"},
    "bust_out": {"description": "Deliberate credit line exhaustion before default", "indicators": ["Rapid utilization increase to near-limit", "Cash advance activity", "Payments stop after utilization spike"], "frequency": "moderate"},
    "synthetic_identity": {"description": "Fictitious identity created using mixed real and fake data", "indicators": ["SSN with no credit history prior to 2 years ago", "Authorized user on multiple unrelated accounts", "Address inconsistencies"], "frequency": "increasing"},
}

INVESTIGATION_CASES = {
    "INV-2025-301": {
        "alert_txns": ["TXN-90001", "TXN-90002"],
        "rules_triggered": ["RULE-001", "RULE-002"],
        "pattern": "card_cloning",
        "status": "open",
        "analyst": "Karen Wright",
        "opened": "2025-03-05",
        "priority": "high",
        "notes": "Synthetic contact evidence indicates no travel. Card block and replacement are proposed protective actions pending authorization.",
    },
    "INV-2025-302": {
        "alert_txns": ["TXN-90006"],
        "rules_triggered": ["RULE-004", "RULE-006"],
        "pattern": "account_takeover",
        "status": "escalated",
        "analyst": "David Chen",
        "opened": "2025-03-05",
        "priority": "critical",
        "notes": "Synthetic wire followed a password reset by 90 minutes. Escalation and SAR review are proposed; no filing or account action occurred.",
    },
    "INV-2025-303": {
        "alert_txns": ["TXN-90003", "TXN-90004"],
        "rules_triggered": ["RULE-003"],
        "pattern": None,
        "status": "under_review",
        "analyst": "Karen Wright",
        "opened": "2025-03-04",
        "priority": "medium",
        "notes": "Customer confirmed crypto purchases. Monitoring for additional activity.",
    },
}


# ---------------------------------------------------------------------------
# Synthetic overnight queue and ring investigation (the demo walkthrough)
# ---------------------------------------------------------------------------

OVERNIGHT_QUEUE = [
    {"priority": "Critical", "alerts": 23, "value": 892000, "action": "Immediate review"},
    {"priority": "High", "alerts": 67, "value": 1400000, "action": "Today"},
    {"priority": "Medium", "alerts": 234, "value": 2100000, "action": "48-hour queue"},
    {"priority": "Low", "alerts": 923, "value": 3200000, "action": "Auto-disposition"},
]

CRITICAL_BREAKDOWN = [
    {"type": "Account takeover", "alerts": 8, "avg_value": 34000, "trigger": "Credential change + transfer"},
    {"type": "Card fraud ring", "alerts": 6, "avg_value": 28000, "trigger": "Multi-location velocity"},
    {"type": "Wire fraud", "alerts": 5, "avg_value": 67000, "trigger": "First-time international"},
    {"type": "Check fraud", "alerts": 4, "avg_value": 42000, "trigger": "Duplicate deposit"},
]

IMMEDIATE_ALERTS = [
    {"alert": "F-78234", "summary": "$127K wire to high-risk jurisdiction", "team": "Wire Team"},
    {"alert": "F-78156", "summary": "takeover in progress", "team": "Senior Analyst (SIU)"},
    {"alert": "F-78089", "summary": "card testing", "team": "Card Team"},
]

FRAUD_RINGS = [
    {
        "ring": "Ring 1 - Account Takeover Network",
        "short": "ATO Ring",
        "alert": "F-78156",
        "accounts": 12,
        "exposure": 340000,
        "evidence": ["Alert #F-78156, 12 connected accounts, $340K exposure",
                     "Pattern: Same device fingerprint, 8 password resets in 2 hours"],
        "confidence_pct": 94,
        "case_id": "FRD-2024-1847",
        "team": "Senior Analyst",
        "priority": "critical",
    },
    {
        "ring": "Ring 2 - Card Testing",
        "short": "Card Testing",
        "alert": "F-78089",
        "accounts": 18,
        "exposure": 127000,
        "evidence": ["47 cards tested in 4 hours", "Pattern: Gas stations (small amounts), 3 states",
                     "Success rate: 23% (stolen batch indicator)"],
        "confidence_pct": 87,
        "case_id": "FRD-2024-1848",
        "team": "Card Team",
        "priority": "high",
    },
    {
        "ring": "Ring 3 - Wire Fraud",
        "short": "Wire Fraud",
        "alert": "F-78234",
        "accounts": 5,
        "exposure": 224000,
        "evidence": ["5 accounts opened in the last 30 days", "Similar deposits, attempting international wires",
                     "Destination: Known mule accounts"],
        "confidence_pct": 91,
        "case_id": "FRD-2024-1849",
        "team": "Wire Team",
        "priority": "high",
    },
]

ATO_RING_ACCOUNTS = [
    {"account": "***4521", "customer": "J. Morrison", "balance": 89000, "status": "Compromised"},
    {"account": "***7834", "customer": "S. Chen", "balance": 67000, "status": "Compromised"},
    {"account": "***2156", "customer": "M. Williams", "balance": 54000, "status": "Attempted"},
    {"account": "***3390", "customer": "A. Patel", "balance": 22000, "status": "Linked (same device)"},
    {"account": "***6612", "customer": "R. Okafor", "balance": 18000, "status": "Linked (same device)"},
    {"account": "***1478", "customer": "L. Brooks", "balance": 16000, "status": "Linked (same device)"},
    {"account": "***9025", "customer": "T. Nguyen", "balance": 15000, "status": "Linked (same device)"},
    {"account": "***5307", "customer": "K. Alvarez", "balance": 14000, "status": "Linked (same device)"},
    {"account": "***8841", "customer": "D. Fischer", "balance": 13000, "status": "Linked (same device)"},
    {"account": "***2763", "customer": "E. Rossi", "balance": 12000, "status": "Linked (same device)"},
    {"account": "***4419", "customer": "P. Kim", "balance": 11000, "status": "Linked (same device)"},
    {"account": "***7150", "customer": "G. Hart", "balance": 9000, "status": "Linked (same device)"},
]

ACCOUNT_EVENTS = {
    "***4521": [
        {"time": "2:14 AM", "event": "Password reset (new IP)"},
        {"time": "2:18 AM", "event": "Email changed"},
        {"time": "2:22 AM", "event": "Phone changed"},
        {"time": "2:34 AM", "event": "$15K wire initiated"},
        {"time": "2:35 AM", "event": "Transfer held by the AI risk model"},
    ],
}

ATO_INDICATORS = (
    "Foreign IP, new device, unusual navigation, all changes in 20 minutes. Customer verified no activity "
    "(contacted 6 AM)."
)

PROTECTIVE_ACTIONS = [
    {"action": "Account freeze", "count": "12", "status": "Ready for authorized execution"},
    {"action": "Cards blocked", "count": "18", "status": "Ready for authorized execution"},
    {"action": "Wires held", "count": "5 pending", "status": "Ready for authorized execution"},
    {"action": "Password reset", "count": "12", "status": "Queued for approval"},
]

CASE_EVIDENCE = "Device fingerprints, IPs, timeline, customer statements collected. SAR draft prepared for review."
CASE_COMMUNICATIONS = "12 customer alerts drafted, 4 high-value customers flagged for a personal call, new credentials to schedule."

PERFORMANCE_METRICS = [
    {"metric": "Detection rate", "current": "94.2%", "target": "90%", "current_value": 94.2, "target_value": 90, "higher_is_better": True},
    {"metric": "False positive", "current": "2.8%", "target": "5%", "current_value": 2.8, "target_value": 5, "higher_is_better": False},
    {"metric": "Detection time", "current": "4.2 sec", "target": "10 sec", "current_value": 4.2, "target_value": 10, "higher_is_better": False},
    {"metric": "Losses prevented", "current": "$4.8M", "target": "$4M", "current_value": 4.8, "target_value": 4, "higher_is_better": True},
]

FRAUD_TRENDS = [
    {"type": "Account takeover", "change": "+34%", "concern": "High concern - correlates with dark web dump"},
    {"type": "Card present", "change": "-12%", "concern": "Low"},
    {"type": "Wire fraud", "change": "+2%", "concern": "Medium"},
]

ATO_ANALYSIS = "Specific segment targeted (high-balance), bypassing 2FA, increasing sophistication."
RECOMMENDED_CONTROLS = [
    "Deploy adaptive authentication",
    "Pilot behavioral biometrics",
    "Increase monitoring for credential changes",
]

SUMMARY_ACTIONS = {
    "immediate": [
        "SAR filing for ATO (48-hour deadline) - draft ready for the BSA officer",
        "Customer outreach (4 high-value accounts)",
        "Coordinate card team on testing pattern",
    ],
    "strategic": "Address 34% ATO increase, pilot behavioral biometrics, review credential monitoring",
}


SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — INVESTIGATOR REVIEW REQUIRED.** Fictional alerts and accounts only. "
    "A score or pattern is not proof of fraud. No card, account, payment, wire, report, or filing has been "
    "blocked, changed, submitted, or completed.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _alert_metrics():
    """Compute alert and investigation metrics."""
    high_risk_txns = sum(1 for t in TRANSACTIONS.values() if t["risk_score"] >= 70)
    total_flagged_amount = sum(t["amount"] for t in TRANSACTIONS.values() if t["risk_score"] >= 70)
    open_cases = sum(1 for c in INVESTIGATION_CASES.values() if c["status"] in ("open", "under_review", "escalated"))
    return {"high_risk_txns": high_risk_txns, "flagged_amount": total_flagged_amount, "open_cases": open_cases}


def _money_k(value):
    if value >= 1000000:
        return f"${value / 1000000:.1f}M"
    return f"${value / 1000:g}K"


def _queue_total():
    return sum(t["alerts"] for t in OVERNIGHT_QUEUE)


def _meets_target(m):
    if m["higher_is_better"]:
        return m["current_value"] >= m["target_value"]
    return m["current_value"] <= m["target_value"]


def _ring_case(case_id):
    for ring in FRAUD_RINGS:
        if ring["case_id"] == case_id:
            return ring
    return None


def _ring_account(account):
    q = str(account).replace("*", "").strip()
    for a in ATO_RING_ACCOUNTS:
        if q and q in a["account"]:
            return a
    return None


def _risk_level(score):
    """Map numeric risk score to level."""
    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class FraudDetectionAlertAgent(BasicAgent):
    """Fraud detection and alert management agent."""

    def __init__(self):
        self.name = "FraudDetectionAlertAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Fraud Detection & Alert Agent",
            "description": (
                "Always call this tool for fraud-analyst, SIU, or risk-leader requests about overnight fraud "
                "activity and the most urgent alert, pattern analysis and connected rings, investigating the "
                "account takeover ring, account activity behind the Dubai alert, creating investigation cases "
                "and protective actions, fraud prevention performance and trends, or the morning summary and "
                "action items. Every operation has demo defaults, so call it right away. Do not answer those requests "
                "from general knowledge. Uses fictional records only; a flag is not proof of fraud and the "
                "tool never blocks funds, changes an account, contacts a customer, files a SAR, or performs "
                "another protective action. Human investigation and authorized human review and approval "
                "are mandatory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose alert_triage to review overnight activity, the overnight queue, the most "
                            "urgent alert, severity, or why an alert is urgent. Choose pattern_detection for "
                            "pattern analysis and connected activity, coordinated fraud rings, known patterns, "
                            "or why a match is only a hypothesis. Choose transaction_analysis to investigate the "
                            "account takeover ring and its accounts (default), or for account activity behind "
                            "the Dubai alert (account 4532-XXXX-8891), merchant sequence, or transactions. Choose "
                            "investigation_summary to create investigation cases and take protective action "
                            "(returns proposed actions awaiting authorized execution), for a named case, the "
                            "critical wire case, SIU preparation, or what protective actions actually occurred. "
                            "Choose prevention_metrics for fraud prevention performance and concerning trends. "
                            "Choose morning_summary to summarize everything and give the action items."
                        ),
                        "enum": [
                            "alert_triage",
                            "transaction_analysis",
                            "pattern_detection",
                            "investigation_summary",
                            "prevention_metrics",
                            "morning_summary",
                        ],
                    },
                    "case_id": {
                        "type": "string",
                        "description": (
                            "Synthetic case mapping: the Dubai/card-cloning case is INV-2025-301; the "
                            "critical wire case is INV-2025-302; the crypto case is INV-2025-303; the ATO ring "
                            "case is FRD-2024-1847, card testing FRD-2024-1848, wire fraud ring FRD-2024-1849. "
                            "Omit to prepare the three ring cases."
                        ),
                    },
                    "account": {
                        "type": "string",
                        "description": (
                            "Synthetic account mapping: the Dubai alert or James Peterson is "
                            "4532-XXXX-8891; Lisa Wang/crypto is 4716-XXXX-3304; Robert Miles/critical wire "
                            "is 5412-XXXX-6678; Elena Vasquez is 4024-XXXX-1190. Takeover-ring accounts: J. "
                            "Morrison ***4521, S. Chen ***7834, M. Williams ***2156. Omit for the takeover ring."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("case_id")
        if record_id and record_id not in INVESTIGATION_CASES and _ring_case(record_id) is None:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        account = kwargs.get("account")
        known_accounts = {txn["account"] for txn in TRANSACTIONS.values()}
        if account and account not in known_accounts and _ring_account(account) is None:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{account}` exists; no substitute record was used."
        operation = kwargs.get("operation", "alert_triage")
        dispatch = {
            "alert_triage": self._alert_triage,
            "transaction_analysis": self._transaction_analysis,
            "pattern_detection": self._pattern_detection,
            "investigation_summary": self._investigation_summary,
            "prevention_metrics": self._prevention_metrics,
            "morning_summary": self._morning_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    def _alert_triage(self, **kwargs) -> str:
        metrics = _alert_metrics()
        lines = ["# Fraud Alert Triage\n"]
        critical = OVERNIGHT_QUEUE[0]
        lines.append(f"{_queue_total():,} overnight alerts analyzed. {critical['alerts']} critical requiring immediate action.\n")
        lines.append("| Priority | Alerts | Value | Action |")
        lines.append("|---|---|---|---|")
        for t in OVERNIGHT_QUEUE:
            lines.append(f"| {t['priority']} | {t['alerts']:,} | {_money_k(t['value'])} | {t['action']} |")
        lines.append("\n## Critical Breakdown\n")
        for b in CRITICAL_BREAKDOWN:
            lines.append(f"- {b['type']}: {b['alerts']} ({_money_k(b['avg_value'])} avg) - {b['trigger']}")
        lines.append(
            "\n**Immediate:** "
            + ", ".join(f"Alert #{a['alert']} ({a['summary']})" for a in IMMEDIATE_ALERTS)
            + f". Most urgent: #{IMMEDIATE_ALERTS[0]['alert']} - route to the {IMMEDIATE_ALERTS[0]['team']}.\n"
        )
        lines.append("## Monitored Card Transactions (sample)\n")
        lines.append(f"**High-Risk Transactions:** {metrics['high_risk_txns']}")
        lines.append(f"**Flagged Amount:** ${metrics['flagged_amount']:,.2f}")
        lines.append(f"**Open Cases:** {metrics['open_cases']}\n")
        flagged = {k: v for k, v in TRANSACTIONS.items() if v["risk_score"] >= 70}
        lines.append("## Flagged Transactions\n")
        lines.append("| TXN ID | Account | Amount | Merchant | Country | Risk | Level |")
        lines.append("|---|---|---|---|---|---|---|")
        for tid, t in flagged.items():
            level = _risk_level(t["risk_score"])
            lines.append(
                f"| {tid} | {t['account']} | ${t['amount']:,.2f} | {t['merchant']} "
                f"| {t['country']} | {t['risk_score']} | {level} |"
            )
        lines.append("\n## Alert Rules Triggered\n")
        triggered = []
        for case in INVESTIGATION_CASES.values():
            for rule_id in case["rules_triggered"]:
                if rule_id not in triggered:
                    triggered.append(rule_id)
        for rule_id in triggered:
            rule = ALERT_RULES[rule_id]
            lines.append(f"- **{rule_id} ({rule['name']}):** {rule['description']} [{rule['severity'].upper()}]")
        lines.append("\nNext step: see the pattern analysis?")
        return "\n".join(lines)

    def _ring_investigation(self, focus):
        ring = FRAUD_RINGS[0]
        lines = ["# Transaction Analysis: Account Takeover Ring\n"]
        lines.append(f"{ring['accounts']}-account takeover ring investigated. {_money_k(ring['exposure'])} at immediate risk.\n")
        lines.append("| Account | Customer | Balance | Status |")
        lines.append("|---|---|---|---|")
        for a in ATO_RING_ACCOUNTS:
            lines.append(f"| {a['account']} | {a['customer']} | {_money_k(a['balance'])} | {a['status']} |")
        total = sum(a["balance"] for a in ATO_RING_ACCOUNTS)
        lines.append(f"| **Total** | {len(ATO_RING_ACCOUNTS)} accounts | **{_money_k(total)}** | |")
        primary = focus or ATO_RING_ACCOUNTS[0]
        events = ACCOUNT_EVENTS.get(primary["account"], [])
        lines.append(f"\n## Primary - {primary['customer']} ({primary['account']}) Timeline\n")
        if events:
            for e in events:
                lines.append(f"- {e['time']}: {e['event']}")
            lines.append(f"\n**Indicators:** {ATO_INDICATORS}")
        else:
            lines.append("- No credential-event timeline is recorded for this account in the synthetic snapshot.")
        lines.append("\nNext step: create investigation cases and propose protective actions?")
        return "\n".join(lines)

    def _transaction_analysis(self, **kwargs) -> str:
        account = kwargs.get("account")
        known_accounts = [txn["account"] for txn in TRANSACTIONS.values()]
        if not account or account not in known_accounts:
            return self._ring_investigation(_ring_account(account) if account else None)
        lines = ["# Transaction Analysis\n"]
        lines.append(f"## Monitored Transactions for {account}\n")
        lines.append("| TXN ID | Cardholder | Amount | Merchant | Category | Country | Channel | Risk |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for tid, t in TRANSACTIONS.items():
            if t["account"] != account:
                continue
            lines.append(
                f"| {tid} | {t['cardholder']} | ${t['amount']:,.2f} | {t['merchant']} "
                f"| {t['category']} | {t['country']} | {t['channel']} | {t['risk_score']} |"
            )
        accounts = {}
        for t in TRANSACTIONS.values():
            acct = t["account"]
            if acct != account:
                continue
            if acct not in accounts:
                accounts[acct] = {"total": 0, "count": 0, "max_risk": 0}
            accounts[acct]["total"] += t["amount"]
            accounts[acct]["count"] += 1
            accounts[acct]["max_risk"] = max(accounts[acct]["max_risk"], t["risk_score"])
        lines.append("\n## Account-Level Summary\n")
        lines.append("| Account | Transactions | Total Amount | Max Risk |")
        lines.append("|---|---|---|---|")
        for acct, data in accounts.items():
            lines.append(f"| {acct} | {data['count']} | ${data['total']:,.2f} | {data['max_risk']} |")
        return "\n".join(lines)

    def _pattern_detection(self, **kwargs) -> str:
        lines = ["# Fraud Pattern Detection\n"]
        ato = FRAUD_RINGS[0]
        lines.append(
            f"{len(FRAUD_RINGS)} organized fraud rings detected (hypotheses for investigator review, not proof). "
            f"Alert #{ato['alert']} connects to {ato['accounts']} accounts.\n"
        )
        for ring in FRAUD_RINGS:
            lines.append(f"### {ring['ring']}\n")
            for ev in ring["evidence"]:
                lines.append(f"- {ev}")
            lines.append(f"- Confidence: {ring['confidence_pct']}%")
            lines.append("")
        lines.append("Next step: investigate the takeover ring first?\n")
        lines.append("## Known Fraud Patterns\n")
        for pid, pattern in FRAUD_PATTERNS.items():
            lines.append(f"### {pid.replace('_', ' ').title()}\n")
            lines.append(f"**Description:** {pattern['description']}")
            lines.append(f"**Frequency:** {pattern['frequency'].title()}\n")
            lines.append("**Indicators:**\n")
            for ind in pattern["indicators"]:
                lines.append(f"- {ind}")
            lines.append("")
        lines.append("## Pattern Matches in Active Cases\n")
        for case_id, case in INVESTIGATION_CASES.items():
            if case["pattern"]:
                pattern = FRAUD_PATTERNS.get(case["pattern"], {})
                lines.append(f"- **{case_id}:** {case['pattern'].replace('_', ' ').title()} — {pattern.get('description', 'N/A')}")
        return "\n".join(lines)

    def _investigation_summary(self, **kwargs) -> str:
        case_id = kwargs.get("case_id")
        if case_id and case_id in INVESTIGATION_CASES:
            case = INVESTIGATION_CASES[case_id]
            lines = [f"# Investigation: {case_id}\n"]
            lines.append(f"- **Status:** {case['status'].replace('_', ' ').title()}")
            lines.append(f"- **Priority:** {case['priority'].title()}")
            lines.append(f"- **Analyst:** {case['analyst']}")
            lines.append(f"- **Opened:** {case['opened']}")
            lines.append(f"- **Pattern:** {case['pattern'].replace('_', ' ').title() if case['pattern'] else 'Under Analysis'}")
            lines.append(f"- **Notes:** {case['notes']}\n")
            lines.append("## Associated Transactions\n")
            for txn_id in case["alert_txns"]:
                t = TRANSACTIONS.get(txn_id, {})
                if t:
                    lines.append(f"- **{txn_id}:** ${t['amount']:,.2f} at {t['merchant']} ({t['country']}) — Risk: {t['risk_score']}")
            lines.append("\n## Rules Triggered\n")
            for rule_id in case["rules_triggered"]:
                rule = ALERT_RULES.get(rule_id, {})
                lines.append(f"- **{rule_id}:** {rule.get('name', 'Unknown')} [{rule.get('severity', 'N/A').upper()}]")
            route = "SIU" if case["priority"] in ("critical", "high") else "Fraud Operations"
            lines.append(f"\n## Proposed Routing\n\n- Queue: {route}")
            lines.append("- Status: Prepared for authorized investigator review; no external action taken")
            return "\n".join(lines)

        if case_id and _ring_case(case_id):
            ring = _ring_case(case_id)
            lines = [f"# Investigation: {case_id} (draft case)\n"]
            lines.append(f"- **Ring:** {ring['short']} ({ring['ring']})")
            lines.append(f"- **Exposure:** {_money_k(ring['exposure'])}")
            lines.append(f"- **Priority:** {ring['priority'].title()}")
            lines.append(f"- **Proposed routing:** {ring['team']}")
            lines.append(f"- **Confidence:** {ring['confidence_pct']}%\n")
            lines.append("## Evidence\n")
            for ev in ring["evidence"]:
                lines.append(f"- {ev}")
            lines.append("\n- Status: Prepared for authorized investigator review; no external action taken")
            return "\n".join(lines)

        lines = ["# Investigation Cases and Proposed Protective Actions\n"]
        ato = FRAUD_RINGS[0]
        lines.append(
            f"Draft cases prepared and protective actions staged for authorized execution: {ato['accounts']} "
            f"accounts, {_money_k(ato['exposure'])} to protect. Nothing has been blocked, frozen or sent.\n"
        )
        lines.append("| Proposed Action | Accounts | Status |")
        lines.append("|---|---|---|")
        for a in PROTECTIVE_ACTIONS:
            lines.append(f"| {a['action']} | {a['count']} | {a['status']} |")
        lines.append("\n## Draft Cases (proposed routing)\n")
        for ring in FRAUD_RINGS:
            lines.append(f"- {ring['case_id']}: {ring['short']}, {_money_k(ring['exposure'])} ({ring['team']})")
        lines.append(f"\n**Evidence:** {CASE_EVIDENCE}")
        lines.append(f"\n**Communications (drafts, not sent):** {CASE_COMMUNICATIONS}")
        lines.append("\n## Existing Investigation Queue\n")
        lines.append("| Case ID | Pattern | Status | Priority | Analyst | Opened |")
        lines.append("|---|---|---|---|---|---|")
        for cid, case in INVESTIGATION_CASES.items():
            pattern = case["pattern"].replace("_", " ").title() if case["pattern"] else "TBD"
            lines.append(
                f"| {cid} | {pattern} | {case['status'].replace('_', ' ').title()} "
                f"| {case['priority'].title()} | {case['analyst']} | {case['opened']} |"
            )
        lines.append("\nStatus: prepared for authorized investigator review; no external action taken.")
        lines.append("\nNext step: show fraud metrics and trends?")
        return "\n".join(lines)

    def _prevention_metrics(self, **kwargs) -> str:
        lines = ["# Fraud Prevention Performance\n"]
        lines.append("Strong prevention but an emerging ATO trend requires attention.\n")
        lines.append("| Metric | Current | Target | Status |")
        lines.append("|---|---|---|---|")
        for m in PERFORMANCE_METRICS:
            status = "Exceeding" if _meets_target(m) else "Below target"
            lines.append(f"| {m['metric']} | {m['current']} | {m['target']} | {status} |")
        lines.append("\n## Trends (30-Day)\n")
        for t in FRAUD_TRENDS:
            lines.append(f"- {t['type']}: {t['change']} ({t['concern']})")
        lines.append(f"\n**ATO Analysis:** {ATO_ANALYSIS}")
        lines.append("\n**Recommended controls (for approval):** " + "; ".join(RECOMMENDED_CONTROLS) + ".")
        lines.append("\nNext step: generate the summary and action items?")
        return "\n".join(lines)

    def _morning_summary(self, **kwargs) -> str:
        critical = OVERNIGHT_QUEUE[0]
        ato = FRAUD_RINGS[0]
        other = sum(r["exposure"] for r in FRAUD_RINGS[1:])
        lines = ["# Morning Fraud Review Summary\n"]
        lines.append("| Accomplishment | Result |")
        lines.append("|---|---|")
        lines.append(f"| Alerts reviewed | {_queue_total():,} overnight |")
        lines.append(f"| Critical identified | {critical['alerts']} requiring action |")
        lines.append(f"| Rings detected | {len(FRAUD_RINGS)} organized schemes |")
        lines.append(f"| Accounts to secure | {ato['accounts']} compromised or linked (actions staged for authorized execution) |")
        lines.append(f"| Value protected (on execution) | {_money_k(ato['exposure'] + other)} ({_money_k(ato['exposure'])} ATO + {_money_k(other)} other) |")
        lines.append("\n## Cases Prepared\n")
        for ring in FRAUD_RINGS:
            lines.append(f"- {ring['case_id']}: {ring['short']} ({_money_k(ring['exposure'])}, {ring['priority']})")
        lines.append("\n## Immediate Actions\n")
        for i, a in enumerate(SUMMARY_ACTIONS["immediate"], 1):
            lines.append(f"{i}. {a}")
        lines.append(f"\n**Strategic:** {SUMMARY_ACTIONS['strategic']}")
        lines.append("\nNo SAR has been filed and no customer has been contacted; each action needs its authorized owner.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FraudDetectionAlertAgent()
    for op in ["alert_triage", "pattern_detection", "transaction_analysis", "investigation_summary",
               "prevention_metrics", "morning_summary"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
