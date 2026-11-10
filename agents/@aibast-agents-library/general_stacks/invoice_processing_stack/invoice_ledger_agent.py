"""
Invoice Ledger: the "Revised" workflow's ledger rules, as a one-file cartridge.

Built by the AIBAST Agents Library on top of the Copilot Studio Gallery solution
"invoice-processing" (MIT, by its gallery authors). In their Revised workflow an AI "Ledger Agent"
applies written rules to each extracted invoice. This file applies the same rules in code, so the
same invoice and ledger always give the same row and the same log decision.

Rules, taken from their solution:
  - ExtractionStatus: Complete if all five fields are found (InvoiceNumber, Vendor, InvoiceDate,
    AmountDue, Currency); Partial if some are found; Failed if none are found.
  - Complete and Partial are logged; Failed is skipped (ShouldLog).
  - A matching InvoiceNumber already in the ledger sets DuplicateOf to that row's id.
    Duplicates are still logged, not rejected.
  - Missing fields stay blank; nothing is guessed. AmountDue is numeric; dates use ISO format.
Reading the attachment (extraction) stays with their AI step. All sample data below is fictional.
"""
import json
import os
import sys
import re

try:
    from basic_agent import BasicAgent
except ImportError:
    try:  # inside a Brainstem the kernel also provides agents.basic_agent
        from agents.basic_agent import BasicAgent
    except ImportError:  # in the library tree, beside the other templates
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
        from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/invoice-processing",
    "version": "0.2.0",
    "display_name": "Invoice Processing",
    "description": "Applies invoice ledger rules (extraction status, duplicate check, log or skip) the same way every time, from invoice fields that were already extracted.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution invoice-processing",
    "tags": ["finance", "accounts-payable", "invoices", "ledger"],
    "category": "general",
    "quality_tier": "experimental",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

FIELDS = ("InvoiceNumber", "Vendor", "InvoiceDate", "AmountDue", "Currency")

SAMPLE_LEDGER = [
    {"id": "INV-ROW-0001", "InvoiceNumber": "FAB-1043", "Vendor": "Fabrikam Supplies", "AmountDue": 1250.0},
    {"id": "INV-ROW-0002", "InvoiceNumber": "TT-88-207", "Vendor": "Tailspin Toys", "AmountDue": 389.5},
]

SAMPLE_INVOICES = {
    "complete.pdf": {"InvoiceNumber": "NW-2026-118", "Vendor": "Northwind Traders", "InvoiceDate": "11/03/2026", "AmountDue": "$4,820.00", "Currency": "USD"},
    "partial.pdf": {"InvoiceNumber": "CS-5521", "Vendor": "Contoso Services", "InvoiceDate": "", "AmountDue": "975", "Currency": ""},
    "duplicate.pdf": {"InvoiceNumber": "FAB-1043", "Vendor": "Fabrikam Supplies", "InvoiceDate": "2026-10-28", "AmountDue": "1,250.00", "Currency": "USD"},
    "cover-letter.pdf": {"InvoiceNumber": "", "Vendor": "", "InvoiceDate": "", "AmountDue": "", "Currency": ""},
}


def _amount(value):
    digits = re.sub(r"[^0-9.\-]", "", str(value or ""))
    return float(digits) if re.fullmatch(r"-?\d+(\.\d+)?", digits) else None


def _iso(value):
    v = str(value or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", v)  # US month/day/year, as in the sample
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else None


def ledger_row(attachment, extracted, ledger):
    row = {
        "InvoiceNumber": (extracted.get("InvoiceNumber") or "").strip() or None,
        "Vendor": (extracted.get("Vendor") or "").strip() or None,
        "InvoiceDate": _iso(extracted.get("InvoiceDate")),
        "AmountDue": _amount(extracted.get("AmountDue")),
        "Currency": (extracted.get("Currency") or "").strip().upper() or None,
    }
    found = sum(1 for f in FIELDS if row[f] is not None)
    row["ExtractionStatus"] = "Complete" if found == len(FIELDS) else ("Partial" if found else "Failed")
    match = next((r for r in ledger if row["InvoiceNumber"] and r["InvoiceNumber"] == row["InvoiceNumber"]), None)
    row["DuplicateOf"] = match["id"] if match else None
    row["ShouldLog"] = row["ExtractionStatus"] != "Failed"
    row["AttachmentName"] = attachment
    return row


def process(invoices=None, ledger=None):
    invoices = invoices or SAMPLE_INVOICES
    ledger = ledger if ledger is not None else SAMPLE_LEDGER
    rows = [ledger_row(name, fields, ledger) for name, fields in sorted(invoices.items())]
    lines = ["# Invoice ledger decisions", "", "| Attachment | Invoice | Status | Duplicate of | Log it? |", "|---|---|---|---|---|"]
    lines += [f"| {r['AttachmentName']} | {r['InvoiceNumber'] or '—'} | {r['ExtractionStatus']} | {r['DuplicateOf'] or '—'} | {'yes' if r['ShouldLog'] else 'no, skipped'} |" for r in rows]
    lines += ["", "Rows to add:", "```json", json.dumps([r for r in rows if r["ShouldLog"]], indent=1), "```",
              "", "Sample data only. Nothing was written to any ledger; a person reviews before any real logging."]
    return "\n".join(lines)


# ---- Transfer layer ----
INSTRUCTIONS = """You are Invoice Ledger, a synthetic accounts payable pilot. Invoice fields have already been read from each email attachment; you apply the ledger rules to them.

Use only the bundled fictional sample: the ledger rows for Fabrikam Supplies and Tailspin Toys and the four sample attachments. Never match them to a real company or invoice.

Answer with the ledger tool, not from memory. Lead with the decisions table: each attachment's extraction status (Complete, Partial or Failed), whether it duplicates an existing row, and whether it is logged.

You never write to a ledger, pay, approve or email anyone. A person reviews every row before any real logging."""

OPERATION_GUIDE = {
    "ledger_decisions": {
        "title": "Ledger decisions",
        "when": "Use when someone asks which invoices would be logged, which are duplicates, which were only partly read, or what row would be added to the ledger.",
        "ask": "Of the sample invoices on file, which ones get logged, which are duplicates, and which were only partly read?",
    },
}

CARRIED = [
    "Reads invoice fields from email attachments (the original solution's AI extraction step in its Power Automate flow).",
    "Writes the approved rows to the Excel ledger and files the email, through the original solution's flow and connections.",
]


class InvoiceLedgerAgent(BasicAgent):
    def __init__(self):
        self.name = "InvoiceLedger"
        self.metadata = {
            "name": self.name,
            "description": "Decides, for invoice fields that were already extracted, the extraction status, whether it duplicates an existing ledger row, and whether to log it. Leave invoices_json empty to use the bundled fictional sample.",
            "parameters": {"type": "object", "properties": {
                "operation": {"type": "string", "enum": ["ledger_decisions"], "description": "The only operation. Optional."},
                "invoices_json": {"type": "string", "description": "Optional JSON object: attachment name -> {InvoiceNumber, Vendor, InvoiceDate, AmountDue, Currency}."}},
                "required": []},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        raw = kwargs.get("invoices_json")
        try:
            invoices = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return "invoices_json is not valid JSON. Send an object of attachment name -> extracted fields."
        return process(invoices)


if __name__ == "__main__":
    print(process())
