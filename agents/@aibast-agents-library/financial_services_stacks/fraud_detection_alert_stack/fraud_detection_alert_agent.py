"""
Fraud Detection & Alert Agent — Financial Services Stack

Provides alert triage, transaction analysis, pattern detection, and
investigation summaries for financial fraud operations teams.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fraud-detection-alert",
    "version": "1.0.0",
    "display_name": "Fraud Detection & Alert Agent",
    "description": "Financial fraud detection with alert triage, transaction analysis, pattern recognition, and investigation case management.",
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
        "notes": "Cardholder confirmed they are not traveling. Card blocked. Replacement issued.",
    },
    "INV-2025-302": {
        "alert_txns": ["TXN-90006"],
        "rules_triggered": ["RULE-004"],
        "pattern": "account_takeover",
        "status": "escalated",
        "analyst": "David Chen",
        "opened": "2025-03-05",
        "priority": "critical",
        "notes": "Wire to Nigeria following password reset 90 minutes prior. SAR filing initiated.",
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
# Helper functions
# ---------------------------------------------------------------------------

def _alert_metrics():
    """Compute alert and investigation metrics."""
    high_risk_txns = sum(1 for t in TRANSACTIONS.values() if t["risk_score"] >= 70)
    total_flagged_amount = sum(t["amount"] for t in TRANSACTIONS.values() if t["risk_score"] >= 70)
    open_cases = sum(1 for c in INVESTIGATION_CASES.values() if c["status"] in ("open", "under_review", "escalated"))
    return {"high_risk_txns": high_risk_txns, "flagged_amount": total_flagged_amount, "open_cases": open_cases}


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
        self.name = "@aibast-agents-library/fraud-detection-alert"
        self.metadata = {
            "name": self.name,
            "display_name": "Fraud Detection & Alert Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "alert_triage",
                            "transaction_analysis",
                            "pattern_detection",
                            "investigation_summary",
                        ],
                    },
                    "case_id": {"type": "string"},
                    "account": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "alert_triage")
        dispatch = {
            "alert_triage": self._alert_triage,
            "transaction_analysis": self._transaction_analysis,
            "pattern_detection": self._pattern_detection,
            "investigation_summary": self._investigation_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _alert_triage(self, **kwargs) -> str:
        metrics = _alert_metrics()
        lines = ["# Fraud Alert Triage\n"]
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
        for rule_id, rule in ALERT_RULES.items():
            lines.append(f"- **{rule_id} ({rule['name']}):** {rule['description']} [{rule['severity'].upper()}]")
        return "\n".join(lines)

    def _transaction_analysis(self, **kwargs) -> str:
        lines = ["# Transaction Analysis\n"]
        lines.append("## All Monitored Transactions\n")
        lines.append("| TXN ID | Cardholder | Amount | Merchant | Category | Country | Channel | Risk |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for tid, t in TRANSACTIONS.items():
            lines.append(
                f"| {tid} | {t['cardholder']} | ${t['amount']:,.2f} | {t['merchant']} "
                f"| {t['category']} | {t['country']} | {t['channel']} | {t['risk_score']} |"
            )
        accounts = {}
        for t in TRANSACTIONS.values():
            acct = t["account"]
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
            return "\n".join(lines)

        lines = ["# Investigation Case Summary\n"]
        lines.append("| Case ID | Pattern | Status | Priority | Analyst | Opened |")
        lines.append("|---|---|---|---|---|---|")
        for cid, case in INVESTIGATION_CASES.items():
            pattern = case["pattern"].replace("_", " ").title() if case["pattern"] else "TBD"
            lines.append(
                f"| {cid} | {pattern} | {case['status'].replace('_', ' ').title()} "
                f"| {case['priority'].title()} | {case['analyst']} | {case['opened']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FraudDetectionAlertAgent()
    print(agent.perform(operation="alert_triage"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="transaction_analysis"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="pattern_detection"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="investigation_summary", case_id="INV-2025-302"))
