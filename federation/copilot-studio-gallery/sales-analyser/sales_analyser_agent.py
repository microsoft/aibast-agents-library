"""Sales example reconciliation and growth arithmetic from the gallery skills.

The two shipped *-content-example.json assets are carried verbatim below,
including their inconsistent totals and outlier claims. Default output audits
those examples instead of silently repairing them.
The metrics operation follows references/metrics-glossary.md: zero, missing,
negative bases and sign changes never produce misleading growth percentages.
File discovery, field mapping, FX research, narrative, charts, and document
rendering stay with the AI and its skills. No source file or email is changed.
"""
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/sales-analyser",
    "version": "0.1.0", "display_name": "Sales Figures Reconciliation",
    "description": "Audits shipped sample figures and computes clearly labelled growth edge cases.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution sales-analyser",
    "quality_tier": "experimental", "category": "finance",
    "tags": ["sales", "reconciliation"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE_EMAIL_JSON = '''{
  "_how_to_use": "Copy to the working folder as email_content.json, replace the values (reuse the headline, KPIs and data notes from the report), delete what you don't need, then run scripts/build_email.py email_content.json email.html --pdf report.pdf. Max 4 KPIs, 2 bar charts (8 bars each), 3 bullets per finding.",
  "subject": "Q4 2026 sales review: revenue +12% to GBP 4.2M",
  "preheader": "Q4 revenue grew 12% to GBP 4.2M; EMEA drove 9 of the 12 points.",
  "eyebrow": "Quarterly report",
  "title": "Q4 2026 Sales Review",
  "subtitle": "Calendar Q4 (Oct-Dec) vs Q4 2025 | GBP",
  "headline": "Q4 revenue grew 12% to GBP 4.2M versus Q4 2025, with EMEA contributing 9 of the 12 percentage points.",
  "kpis": [
    {"value": "GBP 4.2M", "label": "Revenue, Q4 2026", "delta": "+12% vs Q4 2025", "direction": "up"},
    {"value": "GBP 1.8M", "label": "EMEA revenue", "delta": "+38% vs Q4 2025", "direction": "up"},
    {"value": "GBP 0.6M", "label": "APAC revenue", "delta": "-12% vs Q4 2025", "direction": "down"}
  ],
  "bar_charts": [
    {
      "title": "Revenue by region",
      "subtitle": "Q4 2026, GBP",
      "unit": "money",
      "currency": "GBP",
      "highlight": "EMEA",
      "items": [
        {"label": "EMEA", "value": 1800000},
        {"label": "AMER", "value": 1400000},
        {"label": "APAC", "value": 600000},
        {"label": "LATAM", "value": 400000}
      ]
    },
    {
      "title": "Change vs Q4 2025",
      "subtitle": "% change by region",
      "unit": "pct",
      "mode": "variance",
      "items": [
        {"label": "EMEA", "value": 0.38},
        {"label": "AMER", "value": 0.02},
        {"label": "LATAM", "value": 0.05},
        {"label": "APAC", "value": -0.12}
      ]
    }
  ],
  "findings": [
    {"heading": "What changed", "bullets": [
      "EMEA added GBP 0.5M, including one GBP 2.5M November order (flagged in the data notes).",
      "APAC fell 12% after two strong months in Q4 2025."
    ]}
  ],
  "recommendations": [
    "Confirm whether the EMEA November order is a one-off before setting Q1 targets.",
    "Review APAC pipeline coverage for Q1 2027."
  ],
  "data_notes": {
    "scope": "Q4 2026 vs Q4 2025 (calendar), 6 files from Monthly Sales",
    "transformations": "3 subtotal rows and 1 duplicate removed; 'Emea' mapped to 'EMEA'",
    "fx": "EUR to GBP 0.8712 (1 EUR = 0.8712 GBP, XE mid-market spot, as of 23 Oct 2026), 3 rows",
    "flags": "One EMEA order = 26% of Q4 revenue, included",
    "caveats": "Rounded; may not sum"
  },
  "attachment_name": "Q4-2026-Sales-Review.pdf"
}
'''
SAMPLE_REPORT_JSON = '''{
  "_how_to_use": "Copy this file to the working folder as report_content.json, replace every value, delete what you don't need (an empty section is clutter), save chart PNGs next to it, then run scripts/render_report.py report_content.json report.pdf. Budgets: headline 20-35 words; 3-5 KPIs; max 3 bullets per section, ~20 words each; one chart per section.",
  "title": "Q4 2026 Sales Review",
  "subtitle": "Calendar Q4 (1 Oct - 31 Dec 2026) vs Q4 2025 | All figures GBP",
  "eyebrow": "Quarterly report",
  "headline": "Q4 revenue grew 12% to GBP 4.2M versus Q4 2025, with EMEA contributing 9 of the 12 percentage points.",
  "kpis": [
    {"value": "GBP 4.2M", "label": "Revenue, Q4 2026", "delta": "+12% vs Q4 2025", "direction": "up"},
    {"value": "GBP 1.8M", "label": "EMEA revenue", "delta": "+38% vs Q4 2025", "direction": "up"},
    {"value": "GBP 0.6M", "label": "APAC revenue", "delta": "-12% vs Q4 2025", "direction": "down"},
    {"value": "43%", "label": "EMEA share of total", "delta": "+8.2 pp", "direction": "up"}
  ],
  "sections": [
    {
      "heading": "Regional performance",
      "chart": "revenue_by_region.png",
      "caption": "Revenue by region, Q4 2026, GBP. EMEA highlighted.",
      "bullets": [
        "EMEA added GBP 0.5M, driven by one GBP 2.5M November order (flagged below).",
        "AMER was flat at GBP 1.4M (+2%).",
        "APAC fell 12% after two strong months in Q4 2025."
      ],
      "table": {
        "columns": ["Region", "Q4 2026", "Q4 2025", "Change", "Contribution"],
        "numeric_columns": [1, 2, 3, 4],
        "rows": [
          ["EMEA", "1.80M", "1.30M", "+38%", "+9.0 pp"],
          ["AMER", "1.40M", "1.37M", "+2%", "+0.5 pp"],
          ["APAC", "0.60M", "0.68M", "-12%", "-1.5 pp"],
          ["Total", "4.20M", "3.75M", "+12%", "+12.0 pp"]
        ],
        "total_row": true
      }
    }
  ],
  "recommendations": [
    "Confirm whether the GBP 2.5M EMEA order is a one-off before setting Q1 targets.",
    "Review APAC pipeline coverage for Q1 2027."
  ],
  "data_notes": {
    "scope": "Q4 2026 vs Q4 2025 (calendar). 6 monthly files from Monthly Sales; none skipped.",
    "transformations": ["Removed 3 subtotal rows (GBP 9.9M)", "removed 1 duplicate row (GBP 84K)", "mapped 'Emea' to 'EMEA' (14 rows)"],
    "fx": "EUR to GBP 0.8712 (1 EUR = 0.8712 GBP), XE mid-market spot as of 23 Oct 2026 14:00 UTC; applied to 3 rows.",
    "flags": "EMEA order of GBP 2.5M on 20 Nov 2026 is 26% of Q4 revenue - included.",
    "caveats": "Figures rounded; may not sum."
  }
}
'''
SAMPLE = {"operation": "audit_examples"}


def number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Metrics require plain numeric figures.") from error
    if isinstance(value, bool) or not result.is_finite():
        raise ValueError("Metrics require finite numeric figures.")
    return result


def rounded(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def evaluate(data):
    operation = data.get("operation", "audit_examples")
    if operation == "audit_examples":
        email, report = json.loads(SAMPLE_EMAIL_JSON), json.loads(SAMPLE_REPORT_JSON)
        regions = email["bar_charts"][0]["items"]
        rows = report["sections"][0]["table"]["rows"]
        detail = sum(number(row[1][:-1]) * 1000000 for row in rows[:-1])
        stated = number(rows[-1][1][:-1]) * 1000000
        email_total = sum(number(row["value"]) for row in regions)
        return {"currency": "GBP", "email_region_sum": rounded(email_total),
                "report_detail_sum": rounded(detail), "report_stated_total": rounded(stated),
                "report_unreconciled_difference": rounded(stated - detail),
                "claimed_outlier_amount": "2500000.00",
                "calculated_outlier_share_percent": rounded(Decimal(2500000) / stated * 100),
                "flags": ["Report detail rows omit the email's LATAM amount of GBP 400,000.",
                          "GBP 2.5M is 59.52% of GBP 4.2M, not the sample's stated 26%.",
                          "The stated EMEA order exceeds stated EMEA total revenue of GBP 1.8M."],
                "Data notes": {"files": ["email-content-example.json", "report-content-example.json"],
                               "transformations": "None; examples preserved unchanged and checked arithmetically.",
                               "fx": "No conversion; all checked amounts already GBP.",
                               "caveats": "Illustrative source content, not validated transactions. Not an audit report."}}
    if operation != "metrics":
        raise ValueError("operation must be audit_examples or metrics.")
    current = number(data["current"])
    prior = None if data["prior"] is None else number(data["prior"])
    currency, files = data["currency"], data["files"]
    if not isinstance(currency, str) or not currency.strip() or not isinstance(files, list) or not files or any(
            not isinstance(name, str) or not name.strip() for name in files):
        raise ValueError("Name the single confirmed currency and nonempty source files list.")
    percent = None
    if prior is None:
        status = "n/a - no comparable period"
    elif prior == 0:
        status = "n/a - new"
    elif prior < 0 or current < 0:
        status = "absolute change only - negative base or sign change"
    else:
        percent, status = rounded((current - prior) / prior * 100), "comparable"
    return {"current": rounded(current), "prior": rounded(prior) if prior is not None else None,
            "absolute_change": rounded(current - prior) if prior is not None else None,
            "percent_change": percent, "status": status, "currency": currency,
            "Data notes": {"files": files, "transformations": "Unrounded figures used; display rounded to two decimals.",
                           "fx": "No conversion; caller confirms one currency and comparable periods.",
                           "flags": status, "caveats": "Not an audit tool; partial periods require like-for-like comparison."}}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Sales Figures Reconciliation, a synthetic finance pilot reconciling example sales figures and calculating comparable-period growth.

Use only the bundled fictional quarterly report and email examples and their stated figures. Never match them to real transactions, companies or financial reports.

Answer with the reconciliation tool, not from memory. Lead with discrepancies or the growth result, quote source filenames and ids exactly, retain data notes, and label missing, zero or negative comparison bases without misleading percentages.

You never repair source examples silently, research exchange rates, publish a report or claim an audit opinion. A finance reviewer confirms source mapping, currency and period comparability before using the analysis."""

OPERATION_GUIDE = {
    "audit_examples": {
        "title": "Example sales reconciliation",
        "when": "Use when someone asks whether the bundled report and email totals, regional details and outlier claims reconcile.",
        "ask": "Do the totals, regional details and outlier claims in the sample sales report and email match up?",
    },
    "metrics": {
        "title": "Comparable sales growth",
        "when": "Use when someone asks for absolute and percentage growth from confirmed comparable figures, including missing, zero or negative prior values.",
        "ask": "What is the absolute and percentage growth for the bundled sample comparable figures? Use the SalesFiguresReconciliation tool with operation metrics and no other inputs.",
    },
}

CARRIED = [
    "Discovers files, maps fields, researches exchange rates and writes the narrative through the original solution's sales analysis skills.",
    "Builds charts, renders PDF reports and prepares HTML email through the original solution's render_report.py and build_email.py helpers.",
]


class SalesAnalyserAgent(BasicAgent):
    def __init__(self):
        self.name = "SalesFiguresReconciliation"
        self.metadata = {"name": self.name, "description": "Audit unchanged source examples by default. Optional payload_json: operation metrics, numeric current, numeric or null prior, confirmed currency, files list. Only already-comparable, single-currency figures are accepted.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; overrides the payload operation. Default audit_examples."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            if "operation" in kwargs:
                operation = kwargs["operation"]
                if operation not in OPERATION_GUIDE:
                    raise ValueError("operation must be audit_examples or metrics.")
                if "payload_json" not in kwargs and operation == "metrics":
                    data = {"current": 4200000, "prior": 3750000, "currency": "GBP",
                            "files": ["email-content-example.json", "report-content-example.json"]}
                data = {**data, "operation": operation}
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(SalesAnalyserAgent().perform())
