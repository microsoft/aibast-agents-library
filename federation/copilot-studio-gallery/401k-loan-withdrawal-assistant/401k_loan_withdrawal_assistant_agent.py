"""Loan limits and payments from the gallery calculator and SAMPLE plan-rules skill.

Carries the README's $64,000 vested/$10,000 cash example unchanged: 8.50%,
26 payments per year, $75 origination fee, and a five-year term.
Tax treatment, hardship eligibility, advice, and benefits handoff stay with
the AI and plan administrator. Maintenance fees are not loan interest.
These are illustrative SAMPLE plan estimates, not financial or tax advice.
"""
import json
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/401k-loan-withdrawal-assistant",
    "version": "0.1.0", "display_name": "401k Loan and Withdrawal Assistant",
    "description": "Calculates loan limits and payments using the fictional sample plan.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution 401k-loan-withdrawal-assistant",
    "quality_tier": "experimental", "category": "benefits",
    "tags": ["loans", "calculator"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"vested_balance": 64000, "current_loan_balance": 0,
          "highest_loan_balance_last_12_months": 0, "outstanding_loan_count": 0,
          "net_amount_needed": 10000, "years": 5}
PLAN = {"name": "Contoso 401(k) Savings Plan (sample)", "minimum_loan": 1000,
        "maximum_loans": 2, "annual_rate_percent": "8.50", "payments_per_year": 26,
        "origination_fee": 75, "annual_maintenance_fee": 25,
        "general_purpose_max_years": 5, "residence_max_years": 15}


def number(value, name, maximum=100000000):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(name + " must be a plain number.") from error
    if isinstance(value, bool) or not result.is_finite() or not 0 <= result <= maximum:
        raise ValueError(name + " is outside the permitted range.")
    return result


def money(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def evaluate(data):
    vested = number(data["vested_balance"], "vested_balance")
    current = number(data["current_loan_balance"], "current_loan_balance")
    highest = number(data["highest_loan_balance_last_12_months"], "highest_loan_balance_last_12_months")
    count = number(data["outstanding_loan_count"], "outstanding_loan_count", 100)
    if highest < current or count != count.to_integral_value():
        raise ValueError("Highest balance must cover the current balance; loan count must be whole.")
    limit = max(Decimal(0), min(Decimal(50000) - highest, vested / 2 - current))
    limit = limit.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    eligible = count < PLAN["maximum_loans"] and limit >= PLAN["minimum_loan"]
    net = number(data["net_amount_needed"], "net_amount_needed", 10000000)
    years = number(data["years"], "years", 15)
    residence = data.get("principal_residence", False)
    if type(residence) is not bool:
        raise ValueError("principal_residence must be a Boolean.")
    if net < 1 or years < 1 or years > (15 if residence else 5):
        raise ValueError("Sample plan term is 1-5 years, or up to 15 for a principal residence; cash must be positive.")
    principal = (net + PLAN["origination_fee"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    periods = int((years * 26).to_integral_value(rounding=ROUND_HALF_UP))
    rate = Decimal(PLAN["annual_rate_percent"]) / 100 / 26
    payment = (principal * rate / (1 - (1 + rate) ** -periods)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"plan": PLAN, "maximum_new_loan": money(limit), "eligible": eligible,
            "requested_loan_within_limit": eligible and PLAN["minimum_loan"] <= principal <= limit,
            "principal": money(principal), "cash_received": money(principal - 75),
            "number_of_payments": periods, "payment_per_period": money(payment),
            "total_interest": money(payment * periods - principal),
            "disclaimer": "SAMPLE settings; your SPD governs. Recordkeeper must confirm. Annual maintenance fees excluded from interest."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Retirement Loan Assistant, a synthetic benefits pilot for estimating a sample retirement plan loan's limit and payments.

Use only the bundled fictional plan and its vested balance of 64,000 and cash need of 10,000. Never match these records to a real participant, employer or account.

Answer with the loan estimate tool, not from memory. Lead with the borrowing limit and payment estimate, quote recorded plan fields and ids exactly, and keep maintenance fees separate from interest.

You never approve a loan, determine hardship eligibility, move money or give financial or tax advice. The plan administrator and recordkeeper must review the estimate against the governing plan documents."""

OPERATION_GUIDE = {
    "loan_estimate": {
        "title": "Sample loan estimate",
        "when": "Use when someone asks for the sample plan's borrowing limit, eligibility checks, payment schedule or interest estimate.",
        "ask": "Under the sample retirement plan on file, how much could I borrow, what would each payment be, and how much interest would I pay?",
    },
}

CARRIED = [
    "Explains tax treatment, hardship eligibility and plan exceptions through the original solution's benefits guidance and SAMPLE plan-rules skill.",
    "Hands the reviewed request to the plan administrator through the original solution's benefits handoff.",
]


class RetirementLoanAssistantAgent(BasicAgent):
    def __init__(self):
        self.name = "RetirementLoanAssistant"
        self.metadata = {"name": self.name, "description": "Estimate sample-plan limits and payments. Optional payload_json: vested_balance, current_loan_balance, highest_loan_balance_last_12_months, outstanding_loan_count, net_amount_needed, years, optional principal_residence Boolean.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to loan_estimate."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "loan_estimate") not in OPERATION_GUIDE:
                raise ValueError("operation must be loan_estimate.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(RetirementLoanAssistantAgent().perform())
