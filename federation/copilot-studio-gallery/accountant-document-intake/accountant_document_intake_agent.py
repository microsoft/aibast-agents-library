"""Document intake gates from README.md, What's inside / Workflow.

Folders and Office lock files stop. Non-source outputs stop. Full and Partial
source extractions are retained with their reasoning, anomalies, and provenance.
Reading documents, deciding whether they are sources, and interpreting figures
remain with the AI extraction step. No document is read or row written here.
All bundled sample values are fictional; timestamps are supplied, not generated.
"""
import json
from datetime import datetime

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/accountant-document-intake",
    "version": "0.1.0", "display_name": "Accountant Document Intake",
    "description": "Checks extraction intake gates and prepares an accounting row.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution accountant-document-intake",
    "quality_tier": "experimental", "category": "finance",
    "tags": ["accounting", "intake"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"filename": "northwind-invoice.pdf", "isFolder": False,
          "ingested_at": "2026-11-01T10:00:00+00:00",
          "extracted": {"isSourceDocument": True, "invoiceNumber": "NW-100",
                        "invoiceDate": None, "vendor": "Northwind Traders",
                        "amountDue": 1250, "currency": "USD", "extractionStatus": "Partial",
                        "transformationNote": "Amount copied from the stated total.",
                        "outliersNote": "Invoice date was unreadable."}}
FIELDS = ("invoiceNumber", "invoiceDate", "vendor", "amountDue", "currency",
          "extractionStatus", "transformationNote", "outliersNote")


def evaluate(data):
    filename = data["filename"]
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename is required.")
    folder = data.get("isFolder", False)
    if type(folder) is not bool:
        raise ValueError("isFolder must be a Boolean.")
    if folder or filename.startswith("~$"):
        return {"should_create_row": False, "reason": "Folder or Office lock file."}
    extracted = data["extracted"]
    if not isinstance(extracted, dict) or type(extracted.get("isSourceDocument")) is not bool:
        raise ValueError("extracted.isSourceDocument must be an explicit Boolean.")
    if not extracted["isSourceDocument"]:
        return {"should_create_row": False, "reason": "Previous output, not a source document."}
    if extracted.get("extractionStatus") not in ("Full", "Partial"):
        raise ValueError("extractionStatus must be Full or Partial.")
    stamp = datetime.fromisoformat(data["ingested_at"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("ingested_at must include a time zone.")
    row = {field: extracted.get(field) for field in FIELDS}
    row.update({"sourceFileName": filename, "ingested_at": data["ingested_at"]})
    return {"should_create_row": True, "row": row, "written": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Accountant Document Intake, a synthetic accounting pilot that checks already-extracted source fields before preparing an intake row.

Use only the bundled fictional invoice NW-100, its supplied ingestion timestamp and its partial extraction. Never match them to a real vendor, document or ledger.

Answer with the intake tool, not from memory. Lead with whether a row should be created, quote invoice ids and field names exactly, and retain missing values, transformation notes and anomalies without guessing.

You never read a live document, write a row, approve an invoice or send a payment. An accountant reviews source status, extracted figures and provenance before any real logging."""

OPERATION_GUIDE = {
    "intake_check": {
        "title": "Document intake check",
        "when": "Use when someone asks whether a folder, lock file or extracted source document should produce an accounting row and which provenance fields it retains.",
        "ask": "Should the Northwind invoice file on file, northwind-invoice.pdf, become an accounting row, and what source details does it keep?",
    },
}

CARRIED = [
    "Reads documents, identifies source documents and interprets figures in the original solution's AI extraction step.",
    "Retrieves source files and writes approved accounting rows through the original solution's intake workflow.",
]


class AccountantDocumentIntakeAgent(BasicAgent):
    def __init__(self):
        self.name = "AccountantDocumentIntake"
        self.metadata = {"name": self.name, "description": "Check intake gates. Optional payload_json: filename, isFolder, ingested_at, extracted object including isSourceDocument and extractionStatus (Full/Partial). With no payload_json it uses the sample on file: the Northwind invoice file northwind-invoice.pdf.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to intake_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "intake_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be intake_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(AccountantDocumentIntakeAgent().perform())
