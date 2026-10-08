"""
Utility Billing Assistance Agent — SLG Government Stack

Provides utility billing support including account inquiries, usage
analysis, payment plan management, and assistance program eligibility
for municipal utility departments.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/utility-billing-assistance",
    "version": "1.1.0",
    "display_name": "Utility Billing and Assistance Agent",
    "description": "Review synthetic municipal utility accounts for billing questions, smart-meter usage anomalies, draft payment-plan options, and preliminary assistance-program screening. The agent never adjusts a bill, enrolls a resident, starts a payment plan, schedules a repair, or changes an account; authorized utility staff must approve actions through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["utility", "billing", "water", "payment", "assistance", "municipal"],
    "category": "slg_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

UTILITY_ACCOUNTS = {
    "RES-782MD": {
        "customer": "782 Maple Drive household",
        "address": "782 Maple Drive",
        "property": "single-family residence",
        "account_type": "residential",
        "services": ["water", "sewer", "stormwater"],
        "status": "current",
        "balance_current": 184.50,
        "balance_past_due": 0.00,
        "autopay": False,
        "last_payment": {"date": "2024-02-20", "amount": 48.20},
        "meter": "Smart meter - hourly data available",
        "tenure_years": 8,
        "billing_period": "Feb 24 - Mar 28",
        "current_gallons": 22000,
        "typical_gallons": 4500,
        "typical_bill": 48.20,
        "prior_leak_adjustments": 0,
        "resident_age": 42,
        "household_income_estimate": 32400,
        "income_source": "estimated from property tax records",
    },
    "ACCT-90001": {
        "customer": "Patricia Hernandez",
        "address": "1245 Cedar Lane",
        "account_type": "residential",
        "services": ["water", "sewer", "stormwater"],
        "status": "active",
        "balance_current": 127.45,
        "balance_past_due": 0.00,
        "autopay": True,
        "last_payment": {"date": "2025-02-15", "amount": 118.90},
    },
    "ACCT-90002": {
        "customer": "Green Valley Shopping Center",
        "address": "5600 Commerce Blvd",
        "account_type": "commercial",
        "services": ["water", "sewer", "stormwater", "fire_line"],
        "status": "active",
        "balance_current": 2845.60,
        "balance_past_due": 1420.30,
        "autopay": False,
        "last_payment": {"date": "2025-01-20", "amount": 2650.00},
    },
    "ACCT-90003": {
        "customer": "Robert & Linda Thompson",
        "address": "887 Willow Creek Dr",
        "account_type": "residential",
        "services": ["water", "sewer", "stormwater", "trash"],
        "status": "delinquent",
        "balance_current": 245.80,
        "balance_past_due": 489.20,
        "autopay": False,
        "last_payment": {"date": "2024-11-18", "amount": 135.00},
    },
    "ACCT-90004": {
        "customer": "Sunnyvale Elementary School",
        "address": "300 Education Way",
        "account_type": "institutional",
        "services": ["water", "sewer", "stormwater", "irrigation"],
        "status": "active",
        "balance_current": 1890.25,
        "balance_past_due": 0.00,
        "autopay": True,
        "last_payment": {"date": "2025-02-28", "amount": 1756.00},
    },
}

USAGE_HISTORY = {
    "ACCT-90001": [
        {"period": "2024-09", "water_gallons": 4200, "sewer_gallons": 3780, "amount": 98.50},
        {"period": "2024-10", "water_gallons": 3800, "sewer_gallons": 3420, "amount": 92.10},
        {"period": "2024-11", "water_gallons": 3100, "sewer_gallons": 2790, "amount": 84.30},
        {"period": "2024-12", "water_gallons": 2900, "sewer_gallons": 2610, "amount": 81.20},
        {"period": "2025-01", "water_gallons": 3000, "sewer_gallons": 2700, "amount": 82.90},
        {"period": "2025-02", "water_gallons": 3200, "sewer_gallons": 2880, "amount": 86.45},
    ],
    "ACCT-90003": [
        {"period": "2024-09", "water_gallons": 8500, "sewer_gallons": 7650, "amount": 145.20},
        {"period": "2024-10", "water_gallons": 9200, "sewer_gallons": 8280, "amount": 152.80},
        {"period": "2024-11", "water_gallons": 12400, "sewer_gallons": 11160, "amount": 198.50},
        {"period": "2024-12", "water_gallons": 14800, "sewer_gallons": 13320, "amount": 232.10},
        {"period": "2025-01", "water_gallons": 13200, "sewer_gallons": 11880, "amount": 215.40},
        {"period": "2025-02", "water_gallons": 11500, "sewer_gallons": 10350, "amount": 189.80},
    ],
}

RATE_STRUCTURES = {
    "water_residential": {
        "base_charge": 18.50,
        "tiers": [
            {"range": "0-3,000 gal", "rate_per_1000": 4.25},
            {"range": "3,001-6,000 gal", "rate_per_1000": 6.50},
            {"range": "6,001-10,000 gal", "rate_per_1000": 9.75},
            {"range": "Over 10,000 gal", "rate_per_1000": 14.00},
        ],
    },
    "water_commercial": {
        "base_charge": 45.00,
        "tiers": [
            {"range": "0-10,000 gal", "rate_per_1000": 5.80},
            {"range": "10,001-50,000 gal", "rate_per_1000": 5.25},
            {"range": "Over 50,000 gal", "rate_per_1000": 4.90},
        ],
    },
    "sewer": {"base_charge": 12.75, "rate_per_1000": 5.10},
    "stormwater": {"residential": 8.50, "commercial_per_eru": 8.50},
    "trash": {"residential": 22.00},
}

# Daily smart-meter reads for the current billing period (hourly reads summed per day).
DAILY_USAGE = {
    "RES-782MD": [
        {"date": "Feb 24", "gallons": 150},
        {"date": "Feb 25", "gallons": 150},
        {"date": "Feb 26", "gallons": 150},
        {"date": "Feb 27", "gallons": 150},
        {"date": "Feb 28", "gallons": 150},
        {"date": "Feb 29", "gallons": 150},
        {"date": "Mar 1", "gallons": 150},
        {"date": "Mar 2", "gallons": 150},
        {"date": "Mar 3", "gallons": 150},
        {"date": "Mar 4", "gallons": 150},
        {"date": "Mar 5", "gallons": 150},
        {"date": "Mar 6", "gallons": 150},
        {"date": "Mar 7", "gallons": 150},
        {"date": "Mar 8", "gallons": 150},
        {"date": "Mar 9", "gallons": 150},
        {"date": "Mar 10", "gallons": 4375},
        {"date": "Mar 11", "gallons": 4375},
        {"date": "Mar 12", "gallons": 4375},
        {"date": "Mar 13", "gallons": 4375},
        {"date": "Mar 14", "gallons": 150},
        {"date": "Mar 15", "gallons": 150},
        {"date": "Mar 16", "gallons": 150},
        {"date": "Mar 17", "gallons": 150},
        {"date": "Mar 18", "gallons": 150},
        {"date": "Mar 19", "gallons": 150},
        {"date": "Mar 20", "gallons": 150},
        {"date": "Mar 21", "gallons": 150},
        {"date": "Mar 22", "gallons": 150},
        {"date": "Mar 23", "gallons": 150},
        {"date": "Mar 24", "gallons": 150},
        {"date": "Mar 25", "gallons": 150},
        {"date": "Mar 26", "gallons": 150},
        {"date": "Mar 27", "gallons": 150},
        {"date": "Mar 28", "gallons": 150}
    ],
}
BASELINE_GAL_PER_DAY = 150

# Municipal Code 18.42 one-time leak adjustment.
LEAK_ADJUSTMENT_POLICY = {
    "code": "Municipal Code 18.42",
    "name": "One-time leak adjustment per household",
    "basis": "Excess volume above the 12-month typical usage is re-billed at the water-only rate and sewer charges on the excess are waived, because the leaked water did not enter the sewer system.",
    "water_only_rate_per_1000": 2.20,
    "repair_proof_days": 30,
    "repair_proof": "receipt or invoice",
    "one_time_only": True,
    "requirements": [
        "Documented repair (receipt or invoice) within 30 days",
        "No prior leak adjustment on the account",
        "Billing specialist approval",
    ],
}

AREA_MEDIAN_INCOME = 47650
AMI_ELIGIBILITY_PCT = 80

ASSISTANCE_PROGRAMS = {
    "LIWAP": {
        "name": "Low-Income Water Assistance Program (LIWAP)",
        "eligibility": "Household income at or below 80% of area median income",
        "benefit": "Up to $150/year utility credit",
        "benefit_amount": 150,
        "documents_required": [
            "Proof of income - recent pay stubs or last year's tax return",
            "Copy of lease or property deed showing residency",
        ],
        "status": "accepting_applications",
    },
    "LIHEAP": {
        "name": "LIHEAP Emergency Utility Fund",
        "eligibility": "Household income at or below 80% of area median income",
        "benefit": "One-time $200 grant",
        "benefit_amount": 200,
        "documents_required": ["Proof of income", "Current utility bill"],
        "status": "accepting_applications",
    },
    "senior_discount": {
        "name": "Senior Citizen Rate Discount",
        "eligibility": "Age 65+ and income at or below 80% of area median income",
        "benefit": "25% rate discount",
        "benefit_amount": 0,
        "documents_required": ["Proof of age", "Proof of income"],
        "status": "accepting_applications",
    },
    "payment_plan": {
        "name": "Extended Payment Arrangement",
        "eligibility": "Any residential customer with a balance due",
        "benefit": "Up to 12 interest-free installments",
        "benefit_amount": 0,
        "documents_required": ["Signed payment agreement"],
        "status": "always_available",
        "max_installments": 12,
        "default_installments": 6,
        "interest_pct": 0,
        "first_due": "April 15",
    },
}

APPLICATION_TERMS = {
    "response_deadline_days": 14,
    "submission": "Online assistance portal",
    "delivery": "Email and postal mail",
}

REPAIR_PROGRAM = {
    "name": "Water Conservation Assistance Program",
    "eligibility": "Income-qualified residents (based on LIWAP income qualification)",
    "free_repairs": ["Toilet flapper", "faucet aerators", "leak detection"],
    "additional_items": ["Low-flow showerhead", "leak detection dye tablets"],
    "provider": "City Maintenance - licensed plumber",
    "proposed_slot": "Tuesday, April 2 (1:00-3:00 PM window)",
    "program_value": 85,
    "estimated_savings_gal_per_month": 6000,
}

FOLLOW_UP_DAYS = 30

FPL_REFERENCE_2025 = {1: 15650, 2: 21150, 3: 26650, 4: 32150, 5: 37650}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_account(query):
    """Account ID or street address (e.g. 'RES-782MD' or '782 Maple Drive'); default the demo account; None on a miss."""
    if not query:
        return "RES-782MD"
    q = str(query).lower().strip()
    for aid, acct in UTILITY_ACCOUNTS.items():
        if aid.lower() in q or q in acct["address"].lower() or acct["address"].lower() in q:
            return aid
    return None


def _not_found(title, query, boundary):
    return f"# {title}\n\nNo synthetic account found for `{query}`. {boundary}"


def _leak_window(account_id):
    """Days whose usage exceeds 3x the normal daily baseline: (first, last, days, gallons, gallons per hour)."""
    days = [d for d in DAILY_USAGE.get(account_id, []) if d["gallons"] > BASELINE_GAL_PER_DAY * 3]
    if not days:
        return None
    total = sum(d["gallons"] for d in days)
    return {"first": days[0]["date"], "last": days[-1]["date"], "days": len(days), "gallons": total,
            "gal_per_hour": round(total / (len(days) * 24))}


def _leak_adjustment(acct):
    """Credit under Municipal Code 18.42, all in cents: excess re-billed at the water-only rate, sewer waived."""
    excess = acct["current_gallons"] - acct["typical_gallons"]
    standard_c = int(round(acct["balance_current"] * 100)) - int(round(acct["typical_bill"] * 100))
    adjusted_c = int(round(excess * LEAK_ADJUSTMENT_POLICY["water_only_rate_per_1000"] * 100 / 1000))
    credit_c = standard_c - adjusted_c
    new_bill_c = int(round(acct["balance_current"] * 100)) - credit_c
    reduction = round(credit_c * 100 / int(round(acct["balance_current"] * 100)))
    return {"excess": excess, "standard": standard_c / 100, "adjusted": adjusted_c / 100,
            "credit": credit_c / 100, "new_bill": new_bill_c / 100, "reduction_pct": reduction}


def _plan(amount, months):
    return round(amount / months, 2)


def _resident_screen(acct):
    income = acct["household_income_estimate"]
    pct = round(income * 100 / AREA_MEDIAN_INCOME)
    qualifies = pct <= AMI_ELIGIBILITY_PCT
    senior = acct["resident_age"] >= 65 and qualifies
    relief = (ASSISTANCE_PROGRAMS["LIWAP"]["benefit_amount"] + ASSISTANCE_PROGRAMS["LIHEAP"]["benefit_amount"]) if qualifies else 0
    return {"income": income, "pct_ami": pct, "qualifies": qualifies, "senior": senior, "relief": relief}


def _usage_trend(account_id):
    """Latest month versus the same baseline the leak screen uses (average of the first two months)."""
    history = USAGE_HISTORY.get(account_id, [])
    if len(history) < 3:
        return "insufficient_data"
    baseline = sum(h["water_gallons"] for h in history[:2]) / 2
    recent = history[-1]["water_gallons"]
    if recent >= baseline * 1.20:
        return "significantly_increasing"
    if recent > baseline * 1.05:
        return "slightly_increasing"
    if recent < baseline * 0.80:
        return "significantly_decreasing"
    if recent < baseline * 0.95:
        return "slightly_decreasing"
    return "stable"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "billing_inquiry",
    "usage_analysis",
    "payment_plan",
    "assistance_programs",
    "leak_adjustment",
    "application_packet",
    "repair_assistance",
    "resolution_summary",
    "income_screen",
]

_DRAFT = ("Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no "
          "application submitted, no repair scheduled, and nothing was sent to the customer.")


class UtilityBillingAssistanceAgent(BasicAgent):
    """Municipal utility billing assistance agent."""

    def __init__(self):
        self.name = "UtilityBillingAssistanceAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Utility Billing Assistance Agent",
            "description": (
                __manifest__["description"] + " Always use this tool for a resident's high water bill. The demo "
                "account is RES-782MD at 782 Maple Drive (the default; an address also works as account_id). A "
                "billing specialist walks the operations in order: pull up the account -> billing_inquiry; hourly "
                "data -> usage_analysis; leak adjustment policy or the credit amount -> leak_adjustment; assistance "
                "programs or eligibility status -> assistance_programs; set up the payment plan / start the LIWAP "
                "application / documents needed -> application_packet; repair assistance -> repair_assistance; send "
                "the complete package and update the account -> resolution_summary (a draft with the total relief and "
                "follow-up; nothing is sent). Call this tool on every one of these asks, even when an earlier answer "
                "already showed some figures: program names, amounts and appointments come only from the tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "billing_inquiry: pull up an account (bill, typical usage, % increase, meter, status). "
                            "usage_analysis: hourly / daily smart-meter data and leak pattern. payment_plan: "
                            "installment options. assistance_programs: assistance programs and the resident's "
                            "eligibility status. leak_adjustment: the leak adjustment policy and the credit amount. "
                            "application_packet: set up the payment plan and the LIWAP application with the "
                            "documents needed. repair_assistance: repair assistance programs and a proposed "
                            "appointment. resolution_summary: the complete assistance package and account updates."
                        ),
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Synthetic account ID or street address, e.g. RES-782MD or '782 Maple Drive' (default RES-782MD).",
                    },
                    "household_size": {
                        "type": "integer",
                        "description": "income_screen only: household size.",
                    },
                    "annual_income": {
                        "type": "number",
                        "description": "income_screen only: annual household income.",
                    },
                    "age": {
                        "type": "integer",
                        "description": "income_screen only: applicant age for the senior-discount screen.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "billing_inquiry")
        dispatch = {
            "billing_inquiry": self._billing_inquiry,
            "usage_analysis": self._usage_analysis,
            "payment_plan": self._payment_plan,
            "assistance_programs": self._assistance_programs,
            "leak_adjustment": self._leak_adjustment_op,
            "application_packet": self._application_packet,
            "repair_assistance": self._repair_assistance,
            "resolution_summary": self._resolution_summary,
            "income_screen": self._income_screen,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    # -- billing_inquiry -------------------------------------------------
    def _billing_inquiry(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        if query == "all":
            return self._portfolio()
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Billing Inquiry", query, "No account record was changed.")
        acct = UTILITY_ACCOUNTS[account_id]
        total_due = acct["balance_current"] + acct["balance_past_due"]
        lines = [f"# Billing Inquiry: {account_id}\n"]
        if "typical_gallons" in acct:
            increase = round((acct["current_gallons"] - acct["typical_gallons"]) * 100 / acct["typical_gallons"])
            lines.append("**Account Usage Analysis - Status: Investigating Consumption Anomaly**\n")
            lines.append(f"- **Account Number:** {account_id}")
            lines.append(f"- **Property Address:** {acct['address']} ({acct['property']})")
            lines.append(f"- **Current Bill Amount:** ${acct['balance_current']:,.2f} for {acct['current_gallons']:,} gallons ({acct['billing_period']})")
            lines.append(f"- **Typical Monthly:** ${acct['typical_bill']:,.2f} for {acct['typical_gallons']:,} gallons")
            lines.append(f"- **Percentage Increase:** {increase}% above 12-month baseline")
            lines.append(f"- **Meter Type:** {acct['meter']}")
            past = "no payment issues" if acct["balance_past_due"] == 0 else f"${acct['balance_past_due']:,.2f} past due"
            lines.append(f"- **Account Status:** {acct['status'].title()} - {past}")
            lines.append(f"- **Customer Tenure:** {acct['tenure_years']} years at this address")
            lines.append("\nNext: pull the hourly smart-meter data to see when the water was used?")
        else:
            lines.append(f"- **Customer:** {acct['customer']}")
            lines.append(f"- **Address:** {acct['address']}")
            lines.append(f"- **Account Type:** {acct['account_type'].title()}")
            lines.append(f"- **Services:** {', '.join(s.replace('_', ' ').title() for s in acct['services'])}")
            lines.append(f"- **Status:** {acct['status'].title()}")
            lines.append(f"- **Current Charges:** ${acct['balance_current']:,.2f}")
            lines.append(f"- **Past Due:** ${acct['balance_past_due']:,.2f}")
            lines.append(f"- **Total Due:** ${total_due:,.2f}")
            lines.append(f"- **Auto-Pay:** {'Yes' if acct['autopay'] else 'No'}")
            lines.append(f"- **Last Payment:** ${acct['last_payment']['amount']:,.2f} on {acct['last_payment']['date']}")
        lines.append("\n> Read-only synthetic account view. No balance, payment, service, or account record was changed.")
        return "\n".join(lines)

    def _portfolio(self) -> str:
        lines = ["# Utility Accounts Summary\n"]
        lines.append("| Account | Customer | Type | Current | Past Due | Status |")
        lines.append("|---|---|---|---|---|---|")
        for aid, acct in UTILITY_ACCOUNTS.items():
            lines.append(
                f"| {aid} | {acct['customer']} | {acct['account_type'].title()} "
                f"| ${acct['balance_current']:,.2f} | ${acct['balance_past_due']:,.2f} | {acct['status'].title()} |"
            )
        total_ar = sum(a["balance_current"] + a["balance_past_due"] for a in UTILITY_ACCOUNTS.values())
        lines.append(f"\n**Total Accounts Receivable:** ${total_ar:,.2f}")
        lines.append("\n> Synthetic portfolio summary. No balance, payment, service, or account record was changed.")
        return "\n".join(lines)

    # -- usage_analysis --------------------------------------------------
    def _usage_analysis(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Usage Analysis", query, "No leak diagnosis or billing action was performed.")
        acct = UTILITY_ACCOUNTS[account_id]
        lines = [f"# Usage Analysis: {account_id}\n"]
        window = _leak_window(account_id)
        if window:
            daily = DAILY_USAGE[account_id]
            lines.append(f"**Smart-meter data ({acct['billing_period']}, {len(daily)} days, {sum(d['gallons'] for d in daily):,} gallons):**\n")
            lines.append(f"- **Concentrated usage:** {window['gallons']:,} gallons during a {window['days']}-day period from "
                         f"{window['first']} through {window['last']}")
            lines.append(f"- **Flow during that window:** nearly constant at {window['gal_per_hour']} gallons per hour, 24 hours a day")
            lines.append(f"- **Before and after the window:** normal {BASELINE_GAL_PER_DAY} gallons per day")
            lines.append("- **Pattern:** constant around-the-clock flow is consistent with an internal leak, most likely a "
                         "toilet flapper valve")
            lines.append("\n| Date | Gallons |")
            lines.append("|---|---|")
            for d in daily:
                if d["gallons"] > BASELINE_GAL_PER_DAY * 3:
                    lines.append(f"| {d['date']} | {d['gallons']:,} |")
            lines.append("\nNext: check the leak adjustment policy?")
        else:
            history = USAGE_HISTORY.get(account_id, [])
            trend = _usage_trend(account_id)
            lines.append(f"**Customer:** {acct.get('customer', 'Unknown')}")
            lines.append(f"**Usage Trend (vs. first-two-month baseline):** {trend.replace('_', ' ').title()}\n")
            if history:
                lines.append("| Period | Water (gal) | Sewer (gal) | Amount |")
                lines.append("|---|---|---|---|")
                for h in history:
                    lines.append(f"| {h['period']} | {h['water_gallons']:,} | {h['sewer_gallons']:,} | ${h['amount']:,.2f} |")
                baseline = sum(h["water_gallons"] for h in history[:2]) / 2
                latest = history[-1]["water_gallons"]
                suspected = latest >= baseline * 1.20
                lines.append("\n## Leak screening\n")
                lines.append(f"- **Anomaly indicator:** {'REVIEW POSSIBLE LEAK' if suspected else 'No sustained leak signal in this snapshot'}")
                lines.append(f"- **Baseline used:** {baseline:,.0f} gallons")
                lines.append(f"- **Latest usage:** {latest:,.0f} gallons")
                if suspected:
                    lines.append("- Draft policy estimate: run the leak adjustment once an inspection confirms the excess volume (no hourly smart-meter data on file).")
        lines.append("\n> Screening only. This is not a leak diagnosis, bill adjustment, repair order, or customer notice.")
        return "\n".join(lines)

    # -- leak_adjustment -------------------------------------------------
    def _leak_adjustment_op(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Leak Adjustment", query, "No credit was applied.")
        acct = UTILITY_ACCOUNTS[account_id]
        pol = LEAK_ADJUSTMENT_POLICY
        lines = [f"# Leak Adjustment Calculation: {account_id}\n"]
        if "typical_gallons" not in acct:
            lines.append(f"{account_id} has no smart-meter leak window on file; a field inspection is required before a "
                         f"{pol['code']} adjustment can be calculated.")
            lines.append(f"\n> {_DRAFT}")
            return "\n".join(lines)
        a = _leak_adjustment(acct)
        eligible = acct["prior_leak_adjustments"] == 0
        lines.append(f"**Status:** {'Qualifies' if eligible else 'Not eligible (prior adjustment on file)'} under "
                     f"{pol['code']} - draft credit pending billing-specialist approval (not applied)\n")
        lines.append(f"**Policy:** {pol['name']}. {pol['basis']}\n")
        lines.append(f"- **Excess Water Volume:** {a['excess']:,} gallons above the 12-month baseline")
        lines.append(f"- **Standard charge on the excess:** ${a['standard']:,.2f} (water + sewer)")
        lines.append(f"- **Adjusted charge:** ${a['adjusted']:,.2f} at the water-only rate of "
                     f"${pol['water_only_rate_per_1000']:.2f} per 1,000 gallons (sewer waived)")
        lines.append(f"- **Credit Amount:** ${a['credit']:,.2f}")
        lines.append(f"- **New Bill Total:** ${a['new_bill']:,.2f} (from ${acct['balance_current']:,.2f}, {a['reduction_pct']}% reduction)")
        lines.append(f"- **Repair Proof Required:** within {pol['repair_proof_days']} days ({pol['repair_proof']})")
        lines.append("- **Policy Limitation:** one-time use only")
        lines.append("\nNext: check assistance programs if the adjusted bill is still hard to pay?")
        lines.append(f"\n> {_DRAFT}")
        return "\n".join(lines)

    # -- payment_plan ----------------------------------------------------
    def _payment_plan(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Draft Payment Plan Options", query, "No payment arrangement was created.")
        acct = UTILITY_ACCOUNTS[account_id]
        pp = ASSISTANCE_PROGRAMS["payment_plan"]
        lines = [f"# Draft Payment Plan Options: {account_id}\n"]
        if acct["balance_past_due"] > 0:
            amount, basis = acct["balance_past_due"], "Past Due Balance"
        elif "typical_gallons" in acct:
            amount, basis = _leak_adjustment(acct)["new_bill"], "Adjusted Bill (after the draft leak credit)"
        else:
            amount, basis = acct["balance_current"], "Current Balance"
        lines.append(f"**{basis}:** ${amount:,.2f}\n")
        months = pp["default_installments"]
        lines.append(f"**Recommended:** {months} months at ${_plan(amount, months):,.2f}/month "
                     f"({pp['interest_pct']}% interest), first payment {pp['first_due']}\n")
        lines.append("| Installments | Monthly Payment | Total |")
        lines.append("|---|---|---|")
        for m in [3, 6, 9, 12]:
            lines.append(f"| {m} months | ${_plan(amount, m):,.2f} | ${amount:,.2f} |")
        lines.append("\n## Payment Plan Requirements\n")
        lines.append(f"- {pp['eligibility']}")
        lines.append(f"- Maximum installments: {pp['max_installments']}")
        lines.append(f"- Documents required: {', '.join(pp['documents_required'])}")
        lines.append("\n> Options only. No payment arrangement was created; authorized billing staff and the customer must approve it.")
        return "\n".join(lines)

    # -- assistance_programs ---------------------------------------------
    def _program_table(self):
        lines = ["| Program | Eligibility | Benefit |", "|---|---|---|"]
        for prog in ASSISTANCE_PROGRAMS.values():
            lines.append(f"| {prog['name']} | {prog['eligibility']} | {prog['benefit']} |")
        lines.append(f"\nArea median income (synthetic): ${AREA_MEDIAN_INCOME:,}; programs use the {AMI_ELIGIBILITY_PCT}% AMI limit.\n")
        return lines

    def _assistance_programs(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Utility Assistance Programs", query, "No eligibility determination was made.")
        acct = UTILITY_ACCOUNTS[account_id]
        lines = ["# Utility Assistance Programs - Preliminary Screening\n"] + self._program_table()
        if "household_income_estimate" in acct:
            s = _resident_screen(acct)
            status = "POTENTIALLY ELIGIBLE - qualifies for multiple programs" if s["qualifies"] else "ABOVE SYNTHETIC LIMIT"
            plan_amount = _leak_adjustment(acct)["new_bill"]
            pp = ASSISTANCE_PROGRAMS["payment_plan"]
            lines.append(f"## Eligibility status: {account_id} ({acct['address']}) - {status}\n")
            lines.append(f"- **Household Income:** ${s['income']:,} ({acct['income_source']})")
            lines.append(f"- **Area Median Income:** {s['pct_ami']}% of AMI - {'qualifies' if s['qualifies'] else 'above the limit'}")
            if s["qualifies"]:
                lines.append(f"- **LIWAP Eligibility:** {ASSISTANCE_PROGRAMS['LIWAP']['benefit']}")
                lines.append(f"- **LIHEAP Emergency Fund:** {ASSISTANCE_PROGRAMS['LIHEAP']['benefit']} available")
            lines.append(f"- **Payment Plan Option:** {pp['default_installments']} months at "
                         f"${_plan(plan_amount, pp['default_installments']):,.2f}/month ({pp['interest_pct']}% interest)")
            lines.append(f"- **Senior Discount:** {'Potentially eligible' if s['senior'] else 'Not applicable (resident age ' + str(acct['resident_age']) + ')'}")
            lines.append(f"- **Total Potential Relief:** ${s['relief']:,} (${ASSISTANCE_PROGRAMS['LIWAP']['benefit_amount']} + "
                         f"${ASSISTANCE_PROGRAMS['LIHEAP']['benefit_amount']})")
            lines.append("\nNext: set up the payment plan and start the LIWAP application?")
        else:
            lines.append(f"No income information on file for {account_id}; use income_screen with household size and annual income.")
        lines.append("\n> Screening only. No eligibility determination, application, enrollment, payment plan, or repair appointment has been completed.")
        return "\n".join(lines)

    # -- income_screen ---------------------------------------------------
    def _income_screen(self, **kwargs) -> str:
        annual_income = kwargs.get("annual_income")
        age = kwargs.get("age")
        household_size = kwargs.get("household_size")
        lines = ["# Utility Assistance Programs - Preliminary Screening\n"] + self._program_table()
        if annual_income is None:
            lines.append("Provide household size and annual income for a preliminary, non-binding screen.")
        else:
            pct = round(annual_income * 100 / AREA_MEDIAN_INCOME)
            ok = pct <= AMI_ELIGIBILITY_PCT
            lines.append("## Applicant screening\n")
            lines.append(f"- Household income: ${annual_income:,.0f} = {pct}% of AMI")
            if household_size in FPL_REFERENCE_2025:
                lines.append(f"- Federal poverty level reference ({household_size}-person household): ${FPL_REFERENCE_2025[household_size]:,}")
            lines.append(f"- LIWAP / LIHEAP income screen: {'POTENTIALLY ELIGIBLE' if ok else 'ABOVE SYNTHETIC LIMIT'}")
            senior = bool(age and age >= 65 and ok)
            lines.append(f"- Senior discount screen: {'POTENTIALLY ELIGIBLE' if senior else 'NOT ESTABLISHED'}")
        lines.append("\n> Screening only. No eligibility determination, application, enrollment, payment plan, or repair appointment has been completed.")
        return "\n".join(lines)

    # -- application_packet ----------------------------------------------
    def _application_packet(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Application Packet", query, "No application was started.")
        acct = UTILITY_ACCOUNTS[account_id]
        pp = ASSISTANCE_PROGRAMS["payment_plan"]
        liwap = ASSISTANCE_PROGRAMS["LIWAP"]
        terms = APPLICATION_TERMS
        amount = _leak_adjustment(acct)["new_bill"] if "typical_gallons" in acct else acct["balance_current"] + acct["balance_past_due"]
        months = pp["default_installments"]
        lines = [f"# Payment Plan and LIWAP Application Packet (Draft): {account_id}\n"]
        lines.append("**Payment plan - ready for billing staff to set up in the billing system:**")
        lines.append(f"- {months} months at ${_plan(amount, months):,.2f}/month ({pp['interest_pct']}% interest) on ${amount:,.2f}, "
                     f"first payment {pp['first_due']}")
        lines.append("\n**LIWAP application - documents the resident needs:**")
        for doc in liwap["documents_required"]:
            lines.append(f"- {doc}")
        lines.append("\n**Pre-filled application fields:**")
        lines.append(f"- Account: {account_id}; service address: {acct['address']}")
        if "household_income_estimate" in acct:
            lines.append(f"- Household income (estimate): ${acct['household_income_estimate']:,} ({acct['income_source']}; resident confirms)")
        lines.append(f"\n**Delivery:** application forms ready to email with a {terms['response_deadline_days']}-day response "
                     f"deadline; the resident submits everything through the {terms['submission'].lower()}.")
        lines.append("\nNext: check repair assistance to fix the leak?")
        lines.append(f"\n> {_DRAFT}")
        return "\n".join(lines)

    # -- repair_assistance -----------------------------------------------
    def _repair_assistance(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Repair Assistance", query, "No repair was scheduled.")
        acct = UTILITY_ACCOUNTS[account_id]
        r = REPAIR_PROGRAM
        qualifies = "household_income_estimate" in acct and _resident_screen(acct)["qualifies"]
        lines = [f"# {r['name']}: {account_id}\n"]
        lines.append(f"**Status:** {'Customer qualifies - free services available' if qualifies else 'Income qualification needed'}\n")
        lines.append(f"- **Free Repairs Offered:** {', '.join(r['free_repairs'])}")
        lines.append(f"- **Additional Items:** {', '.join(r['additional_items'])}")
        lines.append(f"- **Proposed Appointment:** {r['proposed_slot']} - confirm availability with the resident (not booked)")
        lines.append(f"- **Service Provider:** {r['provider']}")
        lines.append(f"- **Estimated Water Savings:** {r['estimated_savings_gal_per_month']:,} gallons/month after repairs")
        lines.append(f"- **Program Value:** ${r['program_value']} in free parts and labor")
        lines.append(f"- **Eligibility:** {r['eligibility']}")
        lines.append("\nNext: prepare the complete assistance package for the resident?")
        lines.append(f"\n> {_DRAFT}")
        return "\n".join(lines)

    # -- resolution_summary ----------------------------------------------
    def _resolution_summary(self, **kwargs) -> str:
        query = kwargs.get("account_id")
        account_id = _resolve_account(query)
        if account_id is None:
            return _not_found("Resolution Summary", query, "Nothing was sent.")
        acct = UTILITY_ACCOUNTS[account_id]
        lines = [f"# Complete Assistance Package (Draft): {account_id}\n"]
        if "typical_gallons" not in acct:
            lines.append("No leak case on file for this account.")
            lines.append(f"\n> {_DRAFT}")
            return "\n".join(lines)
        a = _leak_adjustment(acct)
        s = _resident_screen(acct)
        pp = ASSISTANCE_PROGRAMS["payment_plan"]
        months = pp["default_installments"]
        total = a["credit"] + s["relief"]
        lines.append(f"Package for the customer at {acct['address']}, ready to send by {APPLICATION_TERMS['delivery'].lower()} "
                     "once a billing specialist approves.\n")
        lines.append("**Account actions to record after approval:**")
        lines.append(f"- ${a['credit']:,.2f} leak adjustment credit ({LEAK_ADJUSTMENT_POLICY['code']}); new bill ${a['new_bill']:,.2f}")
        lines.append(f"- {months}-month payment plan at ${_plan(a['new_bill'], months):,.2f}/month starting {pp['first_due']}")
        lines.append("- LIWAP application in progress (documents due within "
                     f"{APPLICATION_TERMS['response_deadline_days']} days)")
        lines.append("- LIHEAP emergency fund information provided")
        lines.append(f"- Free plumbing repair appointment proposed for {REPAIR_PROGRAM['proposed_slot']}")
        lines.append(f"\n**Total customer financial relief:** ${total:,.2f} (${a['credit']:,.2f} credit + "
                     f"${ASSISTANCE_PROGRAMS['LIWAP']['benefit_amount']} LIWAP + ${ASSISTANCE_PROGRAMS['LIHEAP']['benefit_amount']} LIHEAP), "
                     f"plus ${REPAIR_PROGRAM['program_value']} in free repairs")
        lines.append(f"**Follow-up:** flag the account for a {FOLLOW_UP_DAYS}-day follow-up (repair proof due)")
        lines.append(f"\n> {_DRAFT}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main — the demo video's turns
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = UtilityBillingAssistanceAgent()
    for op in ["billing_inquiry", "usage_analysis", "leak_adjustment", "assistance_programs",
               "application_packet", "repair_assistance", "resolution_summary", "payment_plan"]:
        print("=" * 80)
        print(agent.perform(operation=op, account_id="782 Maple Drive"))
