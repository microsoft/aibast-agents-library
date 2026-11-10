"""
Contract Compliance Reviewer: internal consistency check, as a one-file cartridge.

Built by the AIBAST Agents Library on top of the Copilot Studio Gallery solution
"contract-compliance-reviewer" (MIT, by its gallery authors). Their agent reviews a contract by
following written instructions; this file does the internal-consistency part in code, so the same
contract always gives the same findings and anyone can re-run it to check.

What it checks, deterministically:
  - references to clauses or schedules that are not in the contract
  - unfilled placeholders such as [INSERT ADDRESS]
  - capitalised terms used but never defined (beyond the parties and headings)
  - a clause that restates another clause's number of days and gets it wrong
It does not judge law or policy; those stay with a qualified legal professional.
All sample data below is fictional.
"""
import json
import os
import re
import sys

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
    "name": "@aibast-agents-library/contract-compliance-reviewer",
    "version": "0.2.0",
    "display_name": "Contract Compliance Reviewer",
    "description": "Finds internal inconsistencies in a contract (missing references, placeholders, undefined terms, conflicting day counts) the same way every time. AI-assisted review, not legal advice.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution contract-compliance-reviewer",
    "tags": ["legal", "contract-review", "consistency", "human-in-the-loop"],
    "category": "professional_services",
    "quality_tier": "experimental",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAMPLE_CONTRACT = """MASTER SERVICES AGREEMENT between Northwind Traders Ltd (the Supplier) and Alder Grove Clinics Ltd (the Customer), dated 1 March 2026.
1. Definitions. Services means the support services described in Schedule A.
2. Term. This Agreement runs for 24 months from the Effective Date.
3. Fees. The Customer shall pay each invoice within 30 days of receipt.
4. Late payment. Invoices unpaid after 45 days, being the payment period in clause 3, accrue interest at 4 percent.
5. Acceptance. The Customer shall accept the Deliverables within 10 days of delivery.
6. Termination. Either party may terminate on 60 days written notice.
7. Exit. On termination under clause 6, which requires 90 days notice, the Supplier shall return all data.
8. Liability. Liability is capped at the fees paid in the prior 12 months, subject to clause 9.2.
9. Data. 9.1 The Supplier shall process data as set out in Schedule B.
10. Notices. Notices to the Customer go to [INSERT ADDRESS].
Schedule A: Support Services.
(No Schedule B is attached.)"""

FOOTER = "AI-assisted review, not legal advice. A qualified legal professional must confirm every finding."
_COMMON = {"The", "This", "Either", "On", "Notices", "Liability", "Invoices", "MASTER", "SERVICES", "AGREEMENT",
           "Schedule", "Agreement", "Customer", "Supplier", "Ltd", "No"}


def _clauses(text):
    """{'3': 'The Customer shall pay ...', '9.1': ...} from numbered lines."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\.\s+([^.]+)\.\s*(.*)", line)
        if m:
            out[m.group(1)] = m.group(3)
            for sub in re.finditer(r"(\d+\.\d+)\s+(.*?)(?=\s\d+\.\d+\s|$)", m.group(3)):
                out[sub.group(1)] = sub.group(2)
    return out


def review(contract=None):
    text = contract or SAMPLE_CONTRACT
    clauses = _clauses(text)
    schedules = set(re.findall(r"^Schedule ([A-Z])\s*:", text, flags=re.M))
    findings = []

    for ref in sorted(set(re.findall(r"\bclause (\d+(?:\.\d+)?)", text, flags=re.I)), key=lambda s: [int(x) for x in s.split(".")]):
        if ref not in clauses:
            findings.append(("Cross-reference", f"clause {ref}", f"Clause {ref} is referred to but does not exist."))
    for ref in sorted(set(re.findall(r"\bSchedule ([A-Z])\b", text))):
        if ref not in schedules:
            findings.append(("Missing schedule", f"Schedule {ref}", f"Schedule {ref} is referred to but is not attached."))
    for ph in re.findall(r"\[[A-Z][A-Z ]+\]", text):
        num = next((n for n, body in clauses.items() if ph in body), None)
        findings.append(("Unfilled placeholder", f"clause {num}" if num else "contract", f"{ph} has not been filled in."))

    # A clause that says "<N> days ... clause <M>" or "clause <M>, which requires <N> days": compare with clause M's own day count.
    for num, body in clauses.items():
        for m in re.finditer(r"(\d+) days[^.]*?clause (\d+)|clause (\d+)[^.]*?requires (\d+) days", body):
            stated, target = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
            actual = re.search(r"(\d+) days", clauses.get(target, ""))
            if actual and actual.group(1) != stated:
                findings.append(("Conflicting terms", f"clause {num} vs clause {target}",
                                 f"Clause {num} says {stated} days for what clause {target} sets at {actual.group(1)} days."))

    defined = set(re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*) means\b", text))
    for term in sorted(set(re.findall(r"\bthe ([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b", text))):
        if term not in defined and term.split()[0] not in _COMMON:
            where = next((f"clause {n}" for n, body in clauses.items() if f"the {term}" in body), "contract")
            findings.append(("Undefined term", where, f'"{term}" is used as a defined term but never defined.'))

    lines = ["# Internal Consistency Review", "", "| # | Location | Category | Finding |", "|---|---|---|---|"]
    lines += [f"| {i} | {loc} | {cat} | {desc} |" for i, (cat, loc, desc) in enumerate(findings, 1)]
    lines += ["", f"{len(findings)} findings.", "", FOOTER]
    return "\n".join(lines)


POLICIES = {
    "AG-POL-01": "Supplier invoices are paid within 30 days of receipt.",
    "AG-POL-02": "Interest on late payment must not exceed 2 percent.",
    "AG-POL-03": "Alder Grove must be able to terminate on no more than 60 days written notice.",
    "AG-POL-04": "The supplier's liability cap must be at least the fees paid in the prior 24 months.",
    "AG-POL-05": "A contract touching patient data attaches a data processing schedule and names a data protection contact.",
    "AG-POL-06": "On exit the supplier returns all data within 30 days and confirms deletion in writing.",
    "AG-POL-07": "No blank fields, placeholders, or references to missing schedules or clauses.",
}


def _num(pattern, text):
    m = re.search(pattern, text, flags=re.I)
    return int(m.group(1)) if m else None


def policy_check(contract=None):
    """Checks the contract against the synthetic Alder Grove policies. Met / Not met / Not found, never a guess."""
    text = contract or SAMPLE_CONTRACT
    c = _clauses(text)
    rows = []
    pay = _num(r"pay each invoice within (\d+) days", text)
    rows.append(("AG-POL-01", "clause 3", "Met" if pay == 30 else ("Not found" if pay is None else "Not met"), f"Payment within {pay} days." if pay else "No payment period found."))
    rate = _num(r"interest at (\d+) percent", text)
    rows.append(("AG-POL-02", "clause 4", "Not found" if rate is None else ("Met" if rate <= 2 else "Not met"), f"Late interest is {rate} percent; the limit is 2 percent." if rate is not None else "No late interest found."))
    notice = sorted({int(n) for n in re.findall(r"(\d+) days(?: written)? notice", text)})
    st = "Not found" if not notice else ("Met" if max(notice) <= 60 else "Not met")
    rows.append(("AG-POL-03", "clauses 6, 7", st, f"Notice periods stated: {', '.join(map(str, notice))} days." + (" The contract contradicts itself." if len(notice) > 1 else "") if notice else "No termination notice found."))
    cap = _num(r"fees paid in the prior (\d+) months", text)
    rows.append(("AG-POL-04", "clause 8", "Not found" if cap is None else ("Met" if cap >= 24 else "Not met"), f"Cap is {cap} months of fees; the minimum is 24." if cap else "No liability cap found."))
    sched_b = bool(re.search(r"^Schedule B\s*:", text, flags=re.M))
    contact = bool(re.search(r"data protection (contact|officer)", text, flags=re.I))
    rows.append(("AG-POL-05", "clause 9", "Met" if sched_b and contact else "Not met", ("Schedule B is not attached. " if not sched_b else "") + ("No data protection contact is named." if not contact else "")))
    ret = _num(r"return all data within (\d+) days", text)
    deletion = bool(re.search(r"confirm\w* deletion", text, flags=re.I))
    rows.append(("AG-POL-06", "clause 7", "Met" if ret is not None and ret <= 30 and deletion else "Not met", ("No return deadline. " if ret is None else "") + ("No written confirmation of deletion." if not deletion else "")))
    gaps = re.findall(r"\[[A-Z][A-Z ]+\]", text) + ([] if sched_b else ["missing Schedule B"]) + [f"missing clause {r}" for r in re.findall(r"\bclause (\d+(?:\.\d+)?)", text, flags=re.I) if r not in c]
    rows.append(("AG-POL-07", "contract", "Met" if not gaps else "Not met", "Gaps: " + ", ".join(dict.fromkeys(gaps)) + "." if gaps else "No gaps found."))
    lines = ["# Policy Check (synthetic Alder Grove policies)", "", "| Policy | Where | Result | Detail |", "|---|---|---|---|"]
    lines += [f"| {p} | {w} | {r} | {d.strip()} |" for p, w, r, d in rows]
    lines += ["", f"{sum(r == 'Not met' for _, _, r, _ in rows)} of {len(rows)} policies not met.", "", FOOTER]
    return "\n".join(lines)


# ---- Transfer layer: the written parts every output copies word for word ----
INSTRUCTIONS = """You are Contract Compliance Reviewer, a synthetic first-pass contract review pilot for the legal team of Alder Grove Clinics, a fictional group of outpatient clinics.

Use only the bundled synthetic records: the Alder Grove contract policies AG-POL-01 to AG-POL-07 and the sample agreement AG-MSA-2026-014. Never match them to a real organization, person or contract.

Answer with the review tools, not from memory. Lead with the findings table, quote clause numbers and policy ids exactly as recorded, and say how many findings there are.

You never change, sign, send or approve a contract. Every answer ends by saying it is AI-assisted review, not legal advice, and that a qualified legal professional must confirm every finding."""

OPERATION_GUIDE = {
    "consistency_review": {
        "title": "Internal consistency review",
        "when": "Use when someone asks whether a contract contradicts itself: conflicting clauses or day counts, references to clauses or schedules that are not there, unfilled placeholders, or terms used but never defined.",
        "ask": "Before legal sees it, can you check whether the Northwind master services agreement on file (AG-MSA-2026-014) contradicts itself anywhere?",
    },
    "policy_check": {
        "title": "Policy check",
        "when": "Use when someone asks whether a contract meets Alder Grove's contract policies (payment terms, late interest, termination notice, liability cap, patient data, data return, completeness).",
        "ask": "Does the Northwind master services agreement on file (AG-MSA-2026-014) meet our contract policies? Show me which ones it fails.",
    },
}

# What the original gallery solution does that is not code. Carried into the package unchanged and
# marked as the part that stays with the AI and the legal professional.
CARRIED = [
    "Marks up a new copy of the contract in Word with highlights and margin comments (the original solution's add_comments.py helper).",
    "Checks the contract against current law using official sources only, when web search is allowed.",
]


class ContractComplianceReviewerAgent(BasicAgent):
    def __init__(self):
        self.name = "ContractConsistencyReview"
        self.metadata = {
            "name": self.name,
            "description": "Reviews a contract. operation 'consistency_review' finds internal inconsistencies; 'policy_check' checks it against the synthetic Alder Grove contract policies. Leave contract_text empty to review the agreement on file: AG-MSA-2026-014, the master services agreement between Northwind Traders Ltd and Alder Grove Clinics Ltd (fictional).",
            "parameters": {"type": "object", "properties": {
                "operation": {"type": "string", "enum": ["consistency_review", "policy_check"], "description": "Which review to run. Default consistency_review."},
                "contract_text": {"type": "string", "description": "The contract to review, as plain text. Optional."}}, "required": []},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        if kwargs.get("operation") == "policy_check":
            return policy_check(kwargs.get("contract_text") or None)
        return review(kwargs.get("contract_text") or None)


if __name__ == "__main__":
    print(review())
