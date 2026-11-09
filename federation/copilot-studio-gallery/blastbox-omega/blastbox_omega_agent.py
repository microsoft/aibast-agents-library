"""Membership refund and upgrade arithmetic from prorated-refund-calculator.

The skill's worked examples are carried unchanged: 129.99 annual price,
8 unused months, 10 cancellation fee; 399.99 warranty credit and 499.99 upgrade.
Eligibility, tier verification, policy exceptions, and product recommendations
stay with the AI and policy reviewer. No membership is cancelled, refund paid,
or receipt produced. All source examples are fictional store data.
"""
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/blastbox-omega",
    "version": "0.1.0", "display_name": "Store Refund Calculator",
    "description": "Calculates documented membership refunds and upgrade settlements.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution blastbox-omega",
    "quality_tier": "experimental", "category": "retail",
    "tags": ["refund", "calculator"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"annual_price": "129.99", "months_remaining": 8, "cancellation_fee": "10",
          "nonrefundable_credit": "0", "within_cooling_off": False,
          "defective_credit": "399.99", "upgrade_price": "499.99"}


def amount(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Amounts must be plain numbers.") from error
    if isinstance(value, bool) or not result.is_finite() or result < 0:
        raise ValueError("Amounts must be finite and nonnegative.")
    return result


def money(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def evaluate(data):
    annual = amount(data["annual_price"])
    months = data["months_remaining"]
    cooling = data["within_cooling_off"]
    if type(months) is not int or not 0 <= months <= 12 or type(cooling) is not bool:
        raise ValueError("months_remaining must be 0-12 whole months; within_cooling_off must be Boolean.")
    fee = amount(data["cancellation_fee"])
    credit = amount(data["nonrefundable_credit"])
    prorated = annual * months / 12
    refund = annual if cooling else max(Decimal(0), prorated - fee - credit)
    refund = refund.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    result = {"annual_price": money(annual), "unused_months": months,
              "prorated_value": money(prorated), "refund_due": money(refund),
              "rule": "Full cooling-off refund" if cooling else "Unused months less fee and nonrefundable credit, floored at zero",
              "transaction_performed": False}
    if "upgrade_price" in data or "defective_credit" in data:
        difference = amount(data["upgrade_price"]) - amount(data["defective_credit"])
        net = difference - refund
        result.update({"upgrade_difference": money(difference), "net_due": money(max(Decimal(0), net)),
                       "refund_to_customer": money(max(Decimal(0), -net))})
    return result


# ---- Transfer layer ----
INSTRUCTIONS = """You are Store Refund Calculator, a synthetic retail pilot for membership refund and upgrade settlement arithmetic.

Use only the bundled fictional examples: annual price 129.99, eight unused months, fee 10, warranty credit 399.99 and upgrade price 499.99. Never match them to a real member, purchase or store transaction.

Answer with the refund tool, not from memory. Lead with the refund and net settlement, quote recorded amounts and ids exactly, and show whether the cooling-off rule or prorated rule applies.

You never decide policy eligibility, cancel a membership, pay a refund or issue a receipt. A store policy reviewer confirms eligibility, membership tier and exceptions before any transaction."""

OPERATION_GUIDE = {
    "refund_settlement": {
        "title": "Refund and upgrade settlement",
        "when": "Use when someone asks for a membership refund under the confirmed sample policy or its net settlement against an upgrade.",
    },
}

CARRIED = [
    "Verifies membership tier, eligibility and exceptions and recommends products through the original solution's store guidance.",
    "Carries out cancellations, refunds and receipt delivery outside the original solution's prorated-refund-calculator skill.",
]


class BlastboxOmegaAgent(BasicAgent):
    def __init__(self):
        self.name = "StoreRefundCalculator"
        self.metadata = {"name": self.name, "description": "Compute a confirmed-policy refund. Optional payload_json: annual_price, months_remaining, cancellation_fee, nonrefundable_credit, within_cooling_off Boolean; optional defective_credit and upgrade_price together.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to refund_settlement."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "refund_settlement") not in OPERATION_GUIDE:
                raise ValueError("operation must be refund_settlement.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(BlastboxOmegaAgent().perform())
