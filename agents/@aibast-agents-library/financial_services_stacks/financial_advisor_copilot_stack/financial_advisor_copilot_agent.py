"""
Financial Advisor Copilot Agent — Financial Services Stack

Assists branch bankers and financial advisors with service intake, client reviews, portfolio summaries,
discussion candidates, compliance checks and handoffs, plus the branch education-savings journey of the demo
customer Jennifer Martinez (529 plan research, enrollment checklist, a prefilled draft application, college-cost
projection, risk questionnaire and a proposed advisor follow-up). Fixed demo calendar: Thursday, September 5, 2024.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/financial-advisor-copilot",
    "version": "1.0.0",
    "display_name": "Financial Advisor Agent",
    "description": "Automate branch banking and advisory workflows to streamline customer interactions, strengthen compliance, and improve financial guidance.",
    "author": "AIBAST",
    "tags": ["advisor", "portfolio", "investment", "compliance", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CLIENT_PORTFOLIOS = {
    "CLI-3001": {
        "name": "Robert & Susan Whitfield",
        "advisor": "James Morrison, CFP",
        "risk_profile": "moderate",
        "age": 58,
        "retirement_target": 67,
        "total_assets": 1850000,
        "holdings": {
            "US Equities": {"value": 555000, "allocation": 30.0, "target": 35.0},
            "International Equities": {"value": 185000, "allocation": 10.0, "target": 15.0},
            "Fixed Income": {"value": 647500, "allocation": 35.0, "target": 30.0},
            "Real Estate (REITs)": {"value": 185000, "allocation": 10.0, "target": 10.0},
            "Alternatives": {"value": 92500, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 185000, "allocation": 10.0, "target": 5.0},
        },
        "annual_income": 285000,
        "annual_contributions": 45000,
        "last_review": "2024-12-15",
    },
    "CLI-3002": {
        "name": "Angela Martinez",
        "advisor": "James Morrison, CFP",
        "risk_profile": "aggressive",
        "age": 34,
        "retirement_target": 60,
        "total_assets": 420000,
        "holdings": {
            "US Equities": {"value": 210000, "allocation": 50.0, "target": 45.0},
            "International Equities": {"value": 84000, "allocation": 20.0, "target": 20.0},
            "Fixed Income": {"value": 42000, "allocation": 10.0, "target": 10.0},
            "Emerging Markets": {"value": 50400, "allocation": 12.0, "target": 15.0},
            "Alternatives": {"value": 21000, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 12600, "allocation": 3.0, "target": 5.0},
        },
        "annual_income": 145000,
        "annual_contributions": 24000,
        "last_review": "2025-01-20",
    },
    "CLI-3003": {
        "name": "William Chen Trust",
        "advisor": "Patricia Lane, CFA",
        "risk_profile": "conservative",
        "age": 72,
        "retirement_target": 0,
        "total_assets": 4200000,
        "holdings": {
            "US Equities": {"value": 630000, "allocation": 15.0, "target": 15.0},
            "International Equities": {"value": 210000, "allocation": 5.0, "target": 5.0},
            "Fixed Income": {"value": 1890000, "allocation": 45.0, "target": 45.0},
            "Municipal Bonds": {"value": 840000, "allocation": 20.0, "target": 20.0},
            "Real Estate (REITs)": {"value": 210000, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 420000, "allocation": 10.0, "target": 10.0},
        },
        "annual_income": 0,
        "annual_contributions": 0,
        "last_review": "2025-02-10",
    },
}

INVESTMENT_RECOMMENDATIONS = {
    "moderate": [
        {"action": "Rebalance to target allocation", "rationale": "Drift from target exceeds 3% in multiple asset classes"},
        {"action": "Reduce cash overweight", "rationale": "Excess cash drag on returns; deploy to equities"},
        {"action": "Increase international exposure", "rationale": "Underweight vs target; diversification benefit"},
    ],
    "aggressive": [
        {"action": "Increase emerging markets allocation", "rationale": "Below target; favorable long-term growth outlook"},
        {"action": "Consider small-cap tilt", "rationale": "Long time horizon supports higher-volatility allocations"},
        {"action": "Build cash reserve to target 5%", "rationale": "Slightly underweight cash for opportunistic rebalancing"},
    ],
    "conservative": [
        {"action": "Maintain current allocation", "rationale": "Portfolio aligned with targets; no rebalancing needed"},
        {"action": "Review bond duration", "rationale": "Consider shortening duration if rate hikes expected"},
        {"action": "Tax-loss harvesting review", "rationale": "Identify unrealized losses for year-end tax planning"},
    ],
}

COMPLIANCE_RULES = {
    "reg_bi": {"name": "Regulation Best Interest", "description": "Ensure recommendations are in client's best interest", "applies_to": "all"},
    "form_crs": {"name": "Form CRS Delivery", "description": "Relationship summary delivered at account opening and annually", "applies_to": "all"},
    "suitability": {"name": "Suitability Obligation", "description": "Investment recommendations suitable for client profile", "applies_to": "all"},
    "concentration_limit": {"name": "Concentration Limit", "description": "No single position exceeds 10% of portfolio", "applies_to": "all"},
    "senior_investor": {"name": "Senior Investor Protection", "description": "Enhanced protections for clients age 65+", "applies_to": "seniors"},
}


# Name/ID resolution for every client_id input (library resolver idiom: ID or part of a name; no match -> not found).
# The branch retail customer of the demo comes first, so an omitted client_id and a bare "Martinez" select her.
CLIENT_DIRECTORY = {
    "CLI-3004": {"name": "Jennifer Martinez and Emma Martinez", "segment": "Branch retail customer"},
    "CLI-3001": {"name": "Robert & Susan Whitfield", "segment": "Advisory client"},
    "CLI-3002": {"name": "Angela Martinez", "segment": "Advisory client"},
    "CLI-3003": {"name": "William Chen Trust", "segment": "Advisory client"},
}

# The demo customer: a walk-in branch customer opening a 529 education savings account for her daughter.
RETAIL_CUSTOMERS = {
    "CLI-3004": {
        "name": "Jennifer Martinez",
        "age": 35,
        "state": "California",
        "household_income": 125000,
        "liquid_savings": 50000,
        "mortgage": 300000,
        "high_interest_debt": "none reported",
        "investment_experience": "Basic",
        "comfort_allocation": {"equities": 35, "fixed_income": 65},
        "beneficiary": {"name": "Emma Martinez", "relationship": "daughter", "age": 5,
                        "dob": "March 15, 2019", "ssn_last4": "4321"},
        "goal": "Emma's college savings (college start 2037)",
        "initial_deposit": 1000,
        "monthly_contribution": 300,
        "portfolio_choice": "Age-Based Conservative",
        "advisor": "Sarah King, Education Planning Specialist",
        "draft_reference": "VS1-8609E7B8",
    },
}

EDUCATION_PLANS = {
    "California": {
        "plan": "California ScholarShare 529",
        "opening_fee": "No account opening fee",
        "expense_ratio": "~0.25%",
        "state_deduction": "California does not offer a state income tax deduction for 529 contributions",
        "federal": "Growth is tax-deferred and withdrawals for qualified education expenses are federally tax-free",
        "portfolios": [
            ("Age-Based Aggressive", "starts ~90% equities, reduces over time"),
            ("Age-Based Conservative", "starts ~75% equities, reduces quickly"),
            ("Static Portfolios", "you choose and maintain the allocation"),
            ("Single-Fund Options", "for custom building"),
        ],
    },
}

# Projected annual cost (tuition, fees, room & board) today and in 2037 at ~5% annual tuition inflation.
COLLEGE_COSTS = [
    {"type": "In-State Public", "today": 25707, "projected_2037": 52685},
    {"type": "Out-of-State Public", "today": 44014, "projected_2037": 90160},
    {"type": "Private Nonprofit", "today": 57570, "projected_2037": 117845},
]

PLANNING_ASSUMPTIONS = {
    "demo_date": "Thursday, September 5, 2024",
    "college_start_year": 2037,
    "years_to_college": 13,
    "annual_return": 0.05,
    "tuition_inflation": "5% annual",
}

ENROLLMENT_DOCUMENTS = [
    ("Account owner ID", "Driver's license or passport"),
    ("Beneficiary's SSN", "You've provided Emma's last four; keep the full SSN handy"),
    ("Proof of beneficiary's birth", "Certified birth certificate"),
    ("Proof of address", "Utility bill, bank statement, or other acceptable document"),
]

# Risk questionnaire points (0-100); 35-54 = Conservative.
RISK_BANDS = [(0, 34, "Very Conservative"), (35, 54, "Conservative"), (55, 74, "Moderate"), (75, 100, "Aggressive")]

ADVISOR_SLOTS = {
    "date": "Tuesday, September 10, 2024",
    "time": "3:30 PM PT",
    "duration": "30 minutes",
    "type": "Investment Review",
    "channel": "Microsoft Teams",
    "reminders": "24 hours, 1 hour, and 15 minutes before the meeting",
}

SERVICE_REQUESTS = {
    "CLI-3004": {"request": "529 education savings account", "verification": "pending authorized check", "route": "Education Planning Specialist (Sarah King)"},
    "CLI-3001": {"request": "retirement review", "verification": "pending authorized check", "route": "Financial Advisor"},
    "CLI-3002": {"request": "portfolio review", "verification": "pending authorized check", "route": "Financial Advisor"},
    "CLI-3003": {"request": "trust distribution question", "verification": "pending authorized check", "route": "Senior Advisor"},
}

SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings "
    "only. This is not investment, tax, legal, or financial advice; no identity was verified, no account "
    "was opened, and no order, transaction, transfer, or customer communication occurred.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _allocation_drift(holdings):
    """Calculate max allocation drift from target."""
    max_drift = 0
    for asset, data in holdings.items():
        drift = abs(data["allocation"] - data["target"])
        if drift > max_drift:
            max_drift = drift
    return round(max_drift, 1)


def _years_to_retirement(client):
    """Calculate years remaining to retirement."""
    if client["retirement_target"] == 0:
        return 0
    return max(0, client["retirement_target"] - client["age"])


def _compliance_flags(client):
    """Check for compliance issues."""
    flags = []
    for asset, data in client["holdings"].items():
        if data["allocation"] > 50:
            flags.append(f"Concentration risk: {asset} at {data['allocation']}%")
    if client["age"] >= 65:
        flags.append("Senior investor protections apply")
    drift = _allocation_drift(client["holdings"])
    if drift > 5:
        flags.append(f"Allocation drift of {drift}% exceeds threshold")
    return flags


def _resolve_client(value):
    """Client ID or part of a name -> client ID; empty -> the demo customer; no match -> None (never another record)."""
    if not value:
        return "CLI-3004"
    q = str(value).lower().strip()
    for key in CLIENT_DIRECTORY:
        if key.lower() in q or q in CLIENT_DIRECTORY[key]["name"].lower():
            return key
    return None


def _money(value):
    return f"${value:,.0f}"


def _round10(value):
    return int(round(value / 10.0)) * 10


def _future_value(monthly, initial, months, annual_return):
    """Monthly contributions at month end and an initial deposit, compounded monthly."""
    rate = annual_return / 12
    value, deposit = 0.0, float(initial)
    for _ in range(months):
        value = value * (1 + rate) + monthly
        deposit = deposit * (1 + rate)
    return value, deposit


def _plan_projection(customer):
    a = PLANNING_ASSUMPTIONS
    months = a["years_to_college"] * 12
    monthly_value, deposit_value = _future_value(
        customer["monthly_contribution"], customer["initial_deposit"], months, a["annual_return"])
    in_state_total = COLLEGE_COSTS[0]["projected_2037"] * 4
    per_dollar, _ = _future_value(1, 0, months, a["annual_return"])
    return {
        "months": months,
        "monthly_value": _round10(monthly_value),
        "deposit_value": _round10(deposit_value),
        "total_value": _round10(monthly_value + deposit_value),
        "in_state_total": in_state_total,
        "coverage": round(100 * monthly_value / in_state_total),
        "coverage_with_deposit": round(100 * (monthly_value + deposit_value) / in_state_total),
        "shortfall": _round10(in_state_total - monthly_value),
        "shortfall_with_deposit": _round10(in_state_total - monthly_value - deposit_value),
        "monthly_needed": _round10((in_state_total - deposit_value) / per_dollar),
    }


def _risk_factors(customer):
    """Questionnaire points: time horizon, income, liquidity, debt load, investment experience."""
    age, income = customer["age"], customer["household_income"]
    horizon = 15 if age < 45 else 10 if age < 60 else 5
    income_pts = 10 if income >= 100000 else 5
    liquidity = customer["liquid_savings"] / income
    liquidity_pts = 10 if liquidity >= 0.25 else 5
    debt_pts = 5 if customer["high_interest_debt"] == "none reported" else 0
    experience_pts = {"None": 0, "Basic": 5, "Moderate": 10, "Extensive": 20}[customer["investment_experience"]]
    return [
        ("Time horizon (age %d)" % age, horizon),
        ("Household income %s" % _money(income), income_pts),
        ("Liquid savings %s (%.0f%% of income)" % (_money(customer["liquid_savings"]), liquidity * 100), liquidity_pts),
        ("Debt: %s mortgage, high-interest debt %s" % (_money(customer["mortgage"]), customer["high_interest_debt"]), debt_pts),
        ("Investment experience: %s" % customer["investment_experience"], experience_pts),
    ]


def _risk_band(score):
    for low, high, band in RISK_BANDS:
        if low <= score <= high:
            return band
    return "Aggressive"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

OPERATIONS = [
    "service_intake", "client_review", "portfolio_summary", "recommendation_engine", "compliance_check",
    "advisor_handoff", "plan_research", "enrollment_checklist", "account_onboarding", "college_cost_projection",
    "risk_assessment", "schedule_followup",
]


class FinancialAdvisorCopilotAgent(BasicAgent):
    """Financial advisor copilot agent."""

    def __init__(self):
        self.name = "FinancialAdvisorCopilotAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Financial Advisor Copilot Agent",
            "description": (
                "Always call this tool for branch-banker, financial-advisor, customer, or compliance requests about "
                "who is waiting, what service they need, routing after identity checks, the advisor book, "
                "a named client's allocation drift, discussion candidates before an order, senior-investor "
                "controls, or a banker-to-advisor handoff, and for the branch education-savings journey: 529 plan "
                "options for a child, the enrollment documents checklist, opening a 529 account (prepares the "
                "draft application), what college will cost and whether a monthly contribution is enough, a risk "
                "assessment from the customer's age, income, savings, mortgage and experience, and scheduling a "
                "follow-up with an advisor. The demo customer is Jennifer Martinez (daughter Emma, 5, California); "
                "call the tool right away, every operation has her demo defaults. Do not answer those workflows "
                "from general knowledge. Uses fictional records only; it never verifies identity, opens an account, "
                "moves money, sends an invite, gives financial advice, or places an order or transaction. "
                "Licensed-advisor, compliance, and authorized operational review are required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose service_intake for who is waiting, what they need, identity-check "
                            "status, or where to route them. Choose client_review for the advisor book, "
                            "assets, ages, review dates, or who is retired. Choose portfolio_summary for a "
                            "named client's allocation or drift. Choose recommendation_engine for "
                            "discussion candidates before advice or an order. Choose compliance_check for "
                            "senior-investor controls, concentration, drift, or regulatory checkpoints. "
                            "Choose advisor_handoff for a draft handoff with request, identity status, risk "
                            "context, and compliance flags. Choose plan_research for 529 / education savings "
                            "plan options, state benefits and a contribution scenario. Choose "
                            "enrollment_checklist for what is needed to complete 529 enrollment or which "
                            "documents to bring. Choose account_onboarding when the customer says to open the "
                            "529 account (gives the beneficiary's birth date, SSN last four, initial deposit "
                            "or monthly contribution). Choose college_cost_projection for what college will "
                            "cost when the child turns 18 or whether the monthly amount is enough. Choose "
                            "risk_assessment when the customer shares age, household income, savings, "
                            "mortgage or investing experience. Choose schedule_followup to set up a meeting "
                            "or call with a financial advisor."
                        ),
                        "enum": list(OPERATIONS),
                    },
                    "client_id": {
                        "type": "string",
                        "description": (
                            "Synthetic client mapping: Jennifer Martinez (the branch customer saving for her "
                            "daughter Emma) is CLI-3004 and the default; Robert and Susan Whitfield, the "
                            "Whitfields, or Whitfield is CLI-3001; Angela Martinez or Angela is CLI-3002; "
                            "William Chen Trust or Chen is CLI-3003. Omit for the demo customer, service-intake, "
                            "book-wide, or compliance-wide reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("client_id")
        client_id = _resolve_client(record_id)
        if client_id is None:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "client_review")
        dispatch = {
            "service_intake": self._service_intake,
            "client_review": self._client_review,
            "portfolio_summary": self._portfolio_summary,
            "recommendation_engine": self._recommendation_engine,
            "compliance_check": self._compliance_check,
            "advisor_handoff": self._advisor_handoff,
            "plan_research": self._plan_research,
            "enrollment_checklist": self._enrollment_checklist,
            "account_onboarding": self._account_onboarding,
            "college_cost_projection": self._college_cost_projection,
            "risk_assessment": self._risk_assessment,
            "schedule_followup": self._schedule_followup,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(client_id)

    def _service_intake(self, client_id) -> str:
        lines = ["# Branch Service Intake and Routing Preparation\n"]
        lines.append("| Client | Request | Identity Check | Proposed Route |")
        lines.append("|---|---|---|---|")
        for rid, request in SERVICE_REQUESTS.items():
            name = (RETAIL_CUSTOMERS.get(rid) or CLIENT_PORTFOLIOS[rid])["name"]
            lines.append(
                f"| {name} ({rid}) | {request['request'].title()} | "
                f"{request['verification'].title()} | {request['route']} |"
            )
        lines.append(
            "\nNo identity has been verified and no service has been assigned. Follow approved "
            "customer-identification and routing procedures before proceeding."
        )
        return "\n".join(lines)

    def _client_review(self, client_id) -> str:
        lines = ["# Client Review Summary\n"]
        lines.append("| Client | Advisor | Risk | Assets | Age | Retirement In | Last Review |")
        lines.append("|---|---|---|---|---|---|---|")
        for cid, c in CLIENT_PORTFOLIOS.items():
            yrs = _years_to_retirement(c)
            ret_str = f"{yrs} yrs" if yrs > 0 else "Retired"
            lines.append(
                f"| {c['name']} ({cid}) | {c['advisor']} | {c['risk_profile'].title()} "
                f"| ${c['total_assets']:,.0f} | {c['age']} | {ret_str} | {c['last_review']} |"
            )
        total_aum = sum(c["total_assets"] for c in CLIENT_PORTFOLIOS.values())
        lines.append(f"\n**Total AUM:** ${total_aum:,.0f}")
        lines.append(f"**Clients:** {len(CLIENT_PORTFOLIOS)}")
        return "\n".join(lines)

    def _portfolio_summary(self, client_id) -> str:
        if client_id not in CLIENT_PORTFOLIOS:
            return self._no_portfolio(client_id)
        client = CLIENT_PORTFOLIOS[client_id]
        drift = _allocation_drift(client["holdings"])
        lines = [f"# Portfolio Summary: {client['name']}\n"]
        lines.append(f"- **Risk Profile:** {client['risk_profile'].title()}")
        lines.append(f"- **Total Assets:** ${client['total_assets']:,.0f}")
        lines.append(f"- **Annual Contributions:** ${client['annual_contributions']:,.0f}")
        lines.append(f"- **Max Allocation Drift:** {drift}%\n")
        lines.append("## Holdings\n")
        lines.append("| Asset Class | Value | Current % | Target % | Drift |")
        lines.append("|---|---|---|---|---|")
        for asset, data in client["holdings"].items():
            d = round(data["allocation"] - data["target"], 1)
            sign = "+" if d > 0 else ""
            lines.append(
                f"| {asset} | ${data['value']:,.0f} | {data['allocation']}% "
                f"| {data['target']}% | {sign}{d}% |"
            )
        return "\n".join(lines)

    def _recommendation_engine(self, client_id) -> str:
        if client_id not in CLIENT_PORTFOLIOS:
            return self._no_portfolio(client_id)
        client = CLIENT_PORTFOLIOS[client_id]
        recs = INVESTMENT_RECOMMENDATIONS.get(client["risk_profile"], [])
        lines = [f"# Advisor-Review Considerations: {client['name']}\n"]
        lines.append(f"**Risk Profile:** {client['risk_profile'].title()}")
        lines.append(f"**Years to Retirement:** {_years_to_retirement(client) or 'Retired'}\n")
        lines.append("## Discussion Candidates\n")
        for i, rec in enumerate(recs, 1):
            lines.append(f"### {i}. {rec['action']}\n")
            lines.append(f"**Rationale:** {rec['rationale']}\n")
        lines.append("## Illustrative Allocation Differences\n")
        lines.append("| Asset Class | Current | Target | Review Direction | Illustrative Amount |")
        lines.append("|---|---|---|---|---|")
        for asset, data in client["holdings"].items():
            diff_pct = data["target"] - data["allocation"]
            if abs(diff_pct) >= 1.0:
                amount = abs(diff_pct / 100 * client["total_assets"])
                action = "Increase candidate" if diff_pct > 0 else "Reduce candidate"
                lines.append(f"| {asset} | {data['allocation']}% | {data['target']}% | {action} | ${amount:,.0f} |")
        lines.append(
            "\nThese are discussion candidates, not recommendations or orders. Validate objectives, "
            "risk tolerance, suitability, tax consequences, disclosures, and client consent."
        )
        return "\n".join(lines)

    def _compliance_check(self, client_id) -> str:
        lines = ["# Compliance Check Report\n"]
        lines.append("## Regulatory Requirements\n")
        lines.append("| Rule | Description | Applies To |")
        lines.append("|---|---|---|")
        for rule_id, rule in COMPLIANCE_RULES.items():
            lines.append(f"| {rule['name']} | {rule['description']} | {rule['applies_to'].title()} |")
        lines.append("\n## Client Compliance Status\n")
        for cid, c in CLIENT_PORTFOLIOS.items():
            flags = _compliance_flags(c)
            status = "Review Flags Found" if flags else "No Automated Flags"
            lines.append(f"### {c['name']} ({cid}) — {status}\n")
            if flags:
                for f in flags:
                    lines.append(f"- **Flag:** {f}")
            else:
                lines.append("- No automated flags detected; complete normal compliance review")
            lines.append("")
        return "\n".join(lines)

    def _no_portfolio(self, client_id) -> str:
        customer = RETAIL_CUSTOMERS[client_id]
        return (
            f"# No Advisory Portfolio: {customer['name']} ({client_id})\n\n"
            f"{customer['name']} is a branch retail customer with no advisory portfolio on the synthetic record. "
            f"Her open request is a 529 education savings account for {customer['beneficiary']['name']}; use the "
            "529 plan research, college-cost projection, or risk assessment instead."
        )

    def _advisor_handoff(self, client_id) -> str:
        if client_id in RETAIL_CUSTOMERS:
            return self._retail_handoff(client_id)
        client = CLIENT_PORTFOLIOS[client_id]
        request = SERVICE_REQUESTS.get(client_id, {})
        flags = _compliance_flags(client)
        lines = [f"# Draft Banker-to-Advisor Handoff: {client['name']}\n"]
        lines.append(f"- **Requested service:** {request.get('request', 'advisor review')}")
        lines.append(f"- **Identity status:** {request.get('verification', 'pending authorized check')}")
        lines.append(f"- **Proposed route:** {request.get('route', 'Financial Advisor')}")
        lines.append(f"- **Risk profile on synthetic record:** {client['risk_profile'].title()}")
        lines.append(f"- **Portfolio drift:** {_allocation_drift(client['holdings'])}%")
        lines.append("\n## Compliance Context\n")
        for flag in flags or ["No automated flag; complete normal policy checks"]:
            lines.append(f"- {flag}")
        lines.append(
            "\nDraft only. Confirm identity, consent, source records, and routing in approved systems; "
            "no case transfer or customer communication has occurred."
        )
        return "\n".join(lines)

    def _retail_handoff_lines(self, client_id):
        c = RETAIL_CUSTOMERS[client_id]
        b = c["beneficiary"]
        request = SERVICE_REQUESTS[client_id]
        proj = _plan_projection(c)
        score = sum(p for _, p in _risk_factors(c))
        return [
            f"- **Customer:** {c['name']} ({client_id}), age {c['age']}, {c['state']}",
            f"- **Requested service:** {request['request']}",
            f"- **Identity status:** {request['verification']}",
            f"- **Goal:** {c['goal']}; beneficiary {b['name']} (age {b['age']})",
            f"- **Plan chosen:** {EDUCATION_PLANS[c['state']]['plan']} ({c['portfolio_choice']}); "
            f"{_money(c['initial_deposit'])} initial + {_money(c['monthly_contribution'])}/month",
            f"- **Projection:** ~{_money(proj['monthly_value'])} at 18 covers ~{proj['coverage']}% of the "
            f"~{_money(proj['in_state_total'])} in-state 4-year cost; shortfall ~{_money(proj['shortfall'])}",
            f"- **Risk questionnaire:** {_risk_band(score)} ({score}/100), experience {c['investment_experience']}",
            f"- **Draft application reference:** {c['draft_reference']} (not submitted)",
            "- **Open questions:** contribution increase scenarios; portfolio mix (comfort 35/65 vs ~75% "
            "equities in the age-based track)",
        ]

    def _retail_handoff(self, client_id) -> str:
        c = RETAIL_CUSTOMERS[client_id]
        lines = [f"# Draft Banker-to-Advisor Handoff: {c['name']}\n"]
        lines += self._retail_handoff_lines(client_id)
        lines.append(f"- **Proposed route:** {SERVICE_REQUESTS[client_id]['route']}")
        lines.append(
            "\nDraft only. Confirm identity, consent, source records, and routing in approved systems; "
            "no case transfer or customer communication has occurred."
        )
        return "\n".join(lines)

    def _customer(self, client_id):
        return RETAIL_CUSTOMERS.get(client_id) or RETAIL_CUSTOMERS["CLI-3004"]

    def _plan_research(self, client_id) -> str:
        c = self._customer(client_id)
        b = c["beneficiary"]
        plan = EDUCATION_PLANS[c["state"]]
        a = PLANNING_ASSUMPTIONS
        proj = _plan_projection(c)
        lines = [f"# 529 Plan Options: {c['name']} — {b['name']} (age {b['age']}), {c['state']}\n"]
        lines.append(f"## Top Recommendation for Review — {plan['plan']}\n")
        lines.append(f"- {plan['opening_fee']} and a low expense ratio ({plan['expense_ratio']})")
        lines.append("- Age-based portfolios automatically shift from growth (equities) to conservative as college approaches")
        lines.append("- Broad menu: low-cost index funds, socially responsible options, actively managed portfolios")
        lines.append("\n## State-Specific Benefits\n")
        lines.append(f"- {plan['state_deduction']}")
        lines.append(f"- Federal: {plan['federal']}")
        lines.append("\n## Your Contribution Scenario\n")
        lines.append("| Item | Value |")
        lines.append("|---|---|")
        lines.append(f"| Monthly contribution | {_money(c['monthly_contribution'])} |")
        lines.append(f"| Time until college | {a['years_to_college']} years ({proj['months']} months) |")
        lines.append(f"| Estimated return (conservative growth) | {a['annual_return'] * 100:.0f}% annually |")
        lines.append(f"| Projected value at age 18 | ~{_money(proj['monthly_value'])} |")
        lines.append(f"| Projected in-state 4-year cost ({a['college_start_year']}) | ~{_money(proj['in_state_total'])} |")
        lines.append(f"| Coverage | ~{proj['coverage']}% |")
        lines.append("\nAssumes steady monthly contributions and no lump-sum deposits.")
        lines.append("\n## Portfolio Choices\n")
        for i, (name, desc) in enumerate(plan["portfolios"], 1):
            fit = " (fits a conservative approach)" if name == c["portfolio_choice"] else ""
            lines.append(f"{i}. **{name}** — {desc}{fit}")
        lines.append(
            f"\n**Next step:** model higher contribution levels or a different risk track to raise the "
            f"~{proj['coverage']}% coverage; a licensed advisor confirms suitability before enrollment."
        )
        return "\n".join(lines)

    def _enrollment_checklist(self, client_id) -> str:
        c = self._customer(client_id)
        b = c["beneficiary"]
        lines = [f"# 529 Enrollment Checklist: {c['name']} for {b['name']}\n"]
        lines.append("| Step | Item | Status |")
        lines.append("|---|---|---|")
        lines.append("| 1 | Risk profile | Complete |")
        lines.append(f"| 2 | Investment choice: {c['portfolio_choice']} | Complete |")
        lines.append("| 3 | Gather required documents (below) | Needed |")
        lines.append(f"| 4 | Funding setup: {_money(c['initial_deposit'])} initial deposit method + account for "
                     f"{_money(c['monthly_contribution'])}/month automatic contribution | Needed |")
        lines.append("| 5 | Submit & acknowledge: complete the form, acknowledge risk profile and disclosures, "
                     "sign electronically or in-branch | Needed |")
        lines.append("\n## Step 3 — Required Documents\n")
        for i, (doc, detail) in enumerate(ENROLLMENT_DOCUMENTS, 1):
            lines.append(f"{i}. **{doc}** — {detail}")
        lines.append("\n**Estimated time:** 20-30 minutes once documents are ready.")
        lines.append("**Your status:** risk profile complete, investment choice made — finalize forms and present documents.")
        return "\n".join(lines)

    def _account_onboarding(self, client_id) -> str:
        c = self._customer(client_id)
        b = c["beneficiary"]
        plan = EDUCATION_PLANS[c["state"]]
        lines = [f"# 529 Account Application — Prefilled Draft, Not Submitted\n"]
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        lines.append(f"| Draft reference | {c['draft_reference']} |")
        lines.append(f"| Owner | {c['name']} |")
        lines.append(f"| Beneficiary | {b['name']} (age {b['age']}, born {b['dob']}, SSN ending {b['ssn_last4']}) |")
        lines.append(f"| Time to college start | {PLANNING_ASSUMPTIONS['years_to_college']} years |")
        lines.append(f"| Plan | {plan['plan']} ({c['portfolio_choice'].replace('Age-Based ', '')}, Age-Based Allocation) |")
        lines.append(f"| Initial deposit | {_money(c['initial_deposit'])} — ready to fund at submission |")
        lines.append(f"| Monthly contribution | {_money(c['monthly_contribution'])} — schedule prefilled |")
        lines.append("\n## Pre-checks\n")
        lines.append("| Check | Result |")
        lines.append("|---|---|")
        lines.append("| Required application fields | Complete |")
        lines.append(f"| Beneficiary DOB and SSN last four match the customer record | Match ({b['dob']}, {b['ssn_last4']}) |")
        lines.append("| Beneficiary eligibility (under 18, US resident) | Eligible on record |")
        lines.append("| KYC / identity verification | Ready for banker verification with the documents listed |")
        lines.append(
            f"\nThe application is ready for you and the banker to submit. Not submitted: no account was opened "
            f"and no deposit was processed. **Next:** schedule the investment review with "
            f"{c['advisor'].split(',')[0]} to fine-tune the portfolio mix."
        )
        return "\n".join(lines)

    def _college_cost_projection(self, client_id) -> str:
        c = self._customer(client_id)
        b = c["beneficiary"]
        a = PLANNING_ASSUMPTIONS
        proj = _plan_projection(c)
        lines = [f"# Projected College Costs in {a['college_start_year']} — {b['name']} at 18\n"]
        lines.append(f"Based on historical averages and {a['tuition_inflation']} tuition inflation; tuition, fees, room & board.\n")
        lines.append(f"| School Type | Today's Avg. Annual Cost | {a['college_start_year']} Projected Annual | 4-Year Total |")
        lines.append("|---|---|---|---|")
        for row in COLLEGE_COSTS:
            lines.append(f"| {row['type']} | {_money(row['today'])} | ~{_money(row['projected_2037'])} | "
                         f"~{_money(row['projected_2037'] * 4)} |")
        lines.append(f"\n## Your {_money(c['monthly_contribution'])}/Month Plan — Projection\n")
        lines.append("| Item | Value |")
        lines.append("|---|---|")
        lines.append(f"| Initial deposit | {_money(c['initial_deposit'])} |")
        lines.append(f"| Monthly contribution | {_money(c['monthly_contribution'])} |")
        lines.append(f"| Time to college | {a['years_to_college']} years |")
        lines.append(f"| Assumed growth ({c['portfolio_choice']} portfolio) | {a['annual_return'] * 100:.0f}% annually |")
        lines.append(f"| Value at 18 from monthly contributions | ~{_money(proj['monthly_value'])} |")
        lines.append(f"| Covers | ~{proj['coverage']}% of the in-state 4-year cost |")
        lines.append(f"| Shortfall | ~{_money(proj['shortfall'])} |")
        lines.append(
            f"\nThe {_money(c['initial_deposit'])} initial deposit is extra buffer on top (about "
            f"{_money(proj['deposit_value'])} by {a['college_start_year']}); it is not counted in the coverage above.")
        lines.append(
            f"\n**Is {_money(c['monthly_contribution'])}/month enough?** Not for the full in-state cost: fully funding "
            f"~{_money(proj['in_state_total'])} by {a['college_start_year']} takes about "
            f"{_money(proj['monthly_needed'])}/month. The shortfall could be covered by increasing contributions, "
            "scholarships, or loans; an advisor can model the options."
        )
        return "\n".join(lines)

    def _risk_assessment(self, client_id) -> str:
        c = self._customer(client_id)
        b = c["beneficiary"]
        factors = _risk_factors(c)
        score = sum(p for _, p in factors)
        proj = _plan_projection(c)
        comfort = c["comfort_allocation"]
        lines = [f"# Risk Assessment: {c['name']}\n"]
        lines.append(f"**Profile:** {_risk_band(score)} (Score: {score}/100)  ")
        lines.append(f"**Investment experience:** {c['investment_experience']}  ")
        lines.append(f"**Income & liquidity:** {_money(c['household_income'])} household income, "
                     f"{_money(c['liquid_savings'])} in liquid savings  ")
        lines.append(f"**Debt:** {_money(c['mortgage'])} mortgage (no red flags unless high-interest)  ")
        lines.append("**Suitability status:** Consistent with an age-based 529 — for licensed-advisor confirmation\n")
        lines.append("| Questionnaire factor | Points |")
        lines.append("|---|---|")
        for label, pts in factors:
            lines.append(f"| {label} | {pts} |")
        lines.append(f"| **Total** | **{score}** |")
        lines.append("\n## Allocation Guidance\n")
        lines.append(f"- Your personal comfort level: {comfort['equities']}% equities / {comfort['fixed_income']}% "
                     "fixed income (lower volatility)")
        lines.append(f"- Age-based 529 track for {b['name']} (age {b['age']}): ~75% equities now, shifting to bonds by college")
        lines.append("- Why the difference? The education timeline is fixed and age-based plans front-load growth "
                     "to offset rising tuition, then de-risk automatically.")
        lines.append("\n## 529 Funding Check\n")
        lines.append(f"- Fully funding the in-state 4-year cost (~{_money(proj['in_state_total'])} by "
                     f"{PLANNING_ASSUMPTIONS['college_start_year']}) takes about {_money(proj['monthly_needed'])}/month")
        lines.append(f"- Your planned {_money(c['monthly_contribution'])}/month covers ~{proj['coverage']}%; "
                     f"the {_money(c['liquid_savings'])} in savings stays available as an emergency fund")
        lines.append("\n**Key note:** if any debt beyond the mortgage is high-interest, reduce it before increasing contributions.")
        lines.append("\nThis is a questionnaire summary for advisor review, not investment advice.")
        return "\n".join(lines)

    def _schedule_followup(self, client_id) -> str:
        rid = client_id if client_id in RETAIL_CUSTOMERS else "CLI-3004"
        c = RETAIL_CUSTOMERS[rid]
        s = ADVISOR_SLOTS
        lines = [f"# Proposed Investment Review — Draft Invite, Not Sent\n"]
        lines.append("| Detail | Value |")
        lines.append("|---|---|")
        lines.append(f"| Date / time | {s['date']} — {s['time']} ({s['duration']}) |")
        lines.append(f"| Type | {s['type']} |")
        lines.append(f"| Participants | {c['name']} & {c['advisor']} |")
        lines.append(f"| Location | {s['channel']} (join link created when the invite is sent) |")
        lines.append(f"| Reminders | {s['reminders']} |")
        lines.append("\n## Context Passed to the Advisor (draft handoff)\n")
        lines += self._retail_handoff_lines(rid)
        lines.append(
            "\nThe Outlook / Teams invite is ready for you to send; no invite was sent and no case transfer or "
            "customer communication has occurred. **Next:** prepare a portfolio comparison report before the call."
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FinancialAdvisorCopilotAgent()
    for op in ["plan_research", "enrollment_checklist", "account_onboarding", "college_cost_projection",
               "risk_assessment", "schedule_followup"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="client_review"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="portfolio_summary", client_id="CLI-3001"))
