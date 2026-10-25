"""
M&A Target Sourcing Agent

Read-only acquisition screening support for a corporate development team, built on a fixed synthetic market
universe of eight fictional software companies: an acquisition thesis turned into screening criteria, a transparent
weighted ranking, a cited target dossier, a weighting challenge, an evidence-gap review, and an investment committee
screening memo draft. Every company, financial figure, signal and source is invented. The agent never contacts a
target, writes to a CRM, shares a document, or makes an investment decision.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/ma-target-sourcing",
    "version": "1.0.0",
    "display_name": "M&A Target Sourcing Agent",
    "description": "Turn an acquisition thesis into a transparent, cited target shortlist: screening criteria, a weighted ranking of a synthetic market universe, target dossiers with sources and diligence questions, a weighting challenge, evidence-gap review, and an investment committee screening memo draft. The agent is read-only; it never contacts a target, updates a CRM, shares a document, or makes an investment decision.",
    "author": "AIBAST",
    "tags": ["m-and-a", "corporate-development", "deal-sourcing", "target-screening", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic data (fixed snapshot date 2026-06-30; every company and figure is fictional)
# ---------------------------------------------------------------------------

SNAPSHOT_DATE = "2026-06-30"
STALE_BEFORE = "2025-06-30"   # evidence older than 12 months at the snapshot date is stale

THESIS = {
    "id": "TH-2026-014",
    "acquirer": "Fabrikam Information Services",
    "objective": "Add compliance and regulatory workflow software in Europe",
    "sector": "Compliance and regulatory workflow software",
    "region": "Europe",
    "min_revenue": 20,
    "max_revenue": 120,
    "positive_ebitda": True,
}

WEIGHTS = {"strategy": 40, "financial": 30, "market": 15, "execution": 15}

ALT_WEIGHTINGS = [
    {"name": "Base thesis", "strategy": 40, "financial": 30, "market": 15, "execution": 15},
    {"name": "Financial-first", "strategy": 25, "financial": 45, "market": 15, "execution": 15},
    {"name": "Equal weights", "strategy": 25, "financial": 25, "market": 25, "execution": 25},
]

CRITERIA_LABELS = {
    "strategy": "Strategy fit",
    "financial": "Financial quality",
    "market": "Market signal",
    "execution": "Execution fit",
}

# Revenue and EBITDA in USD millions (synthetic). Scores are 0-100 analyst-calibrated criteria scores.
TARGETS = {
    "T-01": {"name": "Lumenrock Compliance Systems", "focus": "Regulatory change and policy workflow", "region": "Europe",
             "revenue": 64, "ebitda": 14.1, "growth": 18, "recurring": 88,
             "scores": {"strategy": 92, "financial": 84, "market": 78, "execution": 80},
             "risks": ["Top five clients are 31% of revenue", "Founder-led sales motion"],
             "questions": ["How concentrated is renewal exposure in the next 18 months?",
                           "Which product modules are sold standalone versus bundled?",
                           "What would it take to move sales beyond the founders?"],
             "evidence": [{"id": "T-01-S1", "type": "Financials", "title": "FY2025 audited summary (synthetic)", "date": "2026-03-31"},
                          {"id": "T-01-S2", "type": "Product", "title": "Analyst product review (synthetic)", "date": "2026-05-12"},
                          {"id": "T-01-S3", "type": "Customer", "title": "Customer reference notes (synthetic)", "date": "2025-11-04"}]},
    "T-02": {"name": "Veridane Analytics", "focus": "Risk analytics for compliance teams", "region": "Europe",
             "revenue": 38, "ebitda": 6.5, "growth": 24, "recurring": 81,
             "scores": {"strategy": 74, "financial": 80, "market": 86, "execution": 70},
             "risks": ["Partner-dependent distribution"],
             "questions": ["What share of new bookings comes through partners?",
                           "How portable is the analytics engine to our data platform?",
                           "Which retention terms apply to the partner contracts?"],
             "evidence": [{"id": "T-02-S1", "type": "Financials", "title": "Management accounts (synthetic)", "date": "2025-12-31"},
                          {"id": "T-02-S2", "type": "Customer", "title": "Customer survey extract (synthetic)", "date": "2026-04-02"}]},
    "T-03": {"name": "Halverd Audit Cloud", "focus": "Audit and controls workflow", "region": "Europe",
             "revenue": 92, "ebitda": 17.5, "growth": 11, "recurring": 76,
             "scores": {"strategy": 88, "financial": 72, "market": 70, "execution": 62},
             "risks": ["Platform migration underway", "Two-country operating model"],
             "questions": ["When does the platform migration finish, and at what cost?",
                           "How are the two country entities integrated today?",
                           "What is net revenue retention after the migration?"],
             "evidence": [{"id": "T-03-S1", "type": "Financials", "title": "FY2024 filed accounts (synthetic)", "date": "2025-03-31"},
                          {"id": "T-03-S2", "type": "Product", "title": "Product roadmap brief (synthetic)", "date": "2026-01-15"},
                          {"id": "T-03-S3", "type": "Customer", "title": "Customer reference notes (synthetic)", "date": "2026-05-20"}]},
    "T-04": {"name": "Brightquay Reg Data", "focus": "Regulatory data feeds", "region": "North America",
             "revenue": 55, "ebitda": 9.9, "growth": 14, "recurring": 90,
             "scores": {"strategy": 80, "financial": 82, "market": 74, "execution": 72},
             "risks": ["Outside the thesis region"], "questions": [], "evidence": []},
    "T-05": {"name": "Oskarvale Workflow", "focus": "Compliance case management", "region": "Europe",
             "revenue": 21, "ebitda": -1.8, "growth": 32, "recurring": 79,
             "scores": {"strategy": 78, "financial": 40, "market": 80, "execution": 66},
             "risks": ["Loss-making"], "questions": [], "evidence": []},
    "T-06": {"name": "Cindral Risk Labs", "focus": "Enterprise risk platform", "region": "Europe",
             "revenue": 140, "ebitda": 25.2, "growth": 9, "recurring": 83,
             "scores": {"strategy": 70, "financial": 78, "market": 68, "execution": 58},
             "risks": ["Above the revenue band"], "questions": [], "evidence": []},
    "T-07": {"name": "Tessaline Controls", "focus": "Compliance controls testing", "region": "Europe",
             "revenue": 47, "ebitda": 7.1, "growth": 15, "recurring": 84,
             "scores": {"strategy": 84, "financial": 76, "market": 72, "execution": 84},
             "risks": ["Single product line"],
             "questions": ["How much of the pipeline depends on the single product line?",
                           "Which adjacent modules are on the near-term roadmap?",
                           "What does the integration effort look like for our platform?"],
             "evidence": [{"id": "T-07-S1", "type": "Financials", "title": "Management accounts (synthetic)", "date": "2026-02-28"},
                          {"id": "T-07-S2", "type": "Product", "title": "Product review (synthetic)", "date": "2025-04-18"}]},
    "T-08": {"name": "Marrowgate Reporting", "focus": "Regulatory reporting templates", "region": "Europe",
             "revenue": 29, "ebitda": 4.4, "growth": 9, "recurring": 70,
             "scores": {"strategy": 60, "financial": 58, "market": 56, "execution": 78},
             "risks": ["Low growth"],
             "questions": ["What is driving the slower growth?",
                           "How many templates are customer-specific?",
                           "Which renewals are at risk this year?"],
             "evidence": [{"id": "T-08-S1", "type": "Financials", "title": "Management accounts (synthetic)", "date": "2026-01-31"}]},
}

REQUIRED_EVIDENCE = ["Financials", "Product", "Customer"]
SHORTLIST_SIZE = 3

_GATE = (
    "Synthetic screening support only. All companies, financials and sources are fictional. No target was "
    "contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_target(value):
    """Target ID or part of a company name; empty -> the top-ranked target; no match -> None."""
    if not value:
        return _ranked()[0]["id"]
    q = str(value).lower().strip()
    for key in TARGETS:
        if key.lower() in q or q in TARGETS[key]["name"].lower():
            return key
    return None


def _exclusion(t):
    """Why a target fails the thesis filters ('' when it passes)."""
    if t["region"] != THESIS["region"]:
        return f"Region {t['region']} is outside {THESIS['region']}"
    if t["revenue"] < THESIS["min_revenue"] or t["revenue"] > THESIS["max_revenue"]:
        return f"Revenue ${t['revenue']}M is outside the ${THESIS['min_revenue']}M-${THESIS['max_revenue']}M band"
    if THESIS["positive_ebitda"] and t["ebitda"] <= 0:
        return f"EBITDA ${t['ebitda']}M is not positive"
    return ""


def _score(t, w):
    """Weighted score in hundredths (integer arithmetic), formatted later with one decimal."""
    total = 0
    for k in ["strategy", "financial", "market", "execution"]:
        total += t["scores"][k] * w[k]
    return total


def _fmt(total):
    return f"{total / 100:.1f}"


def _ranked(w=None):
    w = w or WEIGHTS
    rows = []
    for key in TARGETS:
        t = TARGETS[key]
        if _exclusion(t) == "":
            rows.append({"id": key, "name": t["name"], "total": _score(t, w)})
    out = []
    while rows:
        best = rows[0]
        for r in rows:
            if r["total"] > best["total"]:
                best = r
        out.append(best)
        rows.remove(best)
    return out


def _shortlist_stable():
    first = [r["id"] for r in _ranked(ALT_WEIGHTINGS[0])][:SHORTLIST_SIZE]
    for w in ALT_WEIGHTINGS:
        if [r["id"] for r in _ranked(w)][:SHORTLIST_SIZE] != first:
            return False
    return True


def _gaps(key):
    t = TARGETS[key]
    have = {}
    for e in t["evidence"]:
        have[e["type"]] = e
    gaps = []
    for need in REQUIRED_EVIDENCE:
        if need not in have:
            gaps.append({"type": need, "issue": "Missing", "detail": "No source on file"})
        elif have[need]["date"] < STALE_BEFORE:
            gaps.append({"type": need, "issue": "Stale", "detail": f"{have[need]['id']} dated {have[need]['date']}"})
    return gaps


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = [
    "build_thesis", "screen_targets", "target_dossier", "challenge_ranking", "evidence_gaps", "ic_memo_draft",
]


class MATargetSourcingAgent(BasicAgent):
    """Acquisition target screening support (read-only, synthetic)."""

    def __init__(self):
        self.name = "MATargetSourcingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Always call this tool for acquisition and M&A target sourcing on the fictional Fabrikam "
                "Information Services thesis: turning an acquisition thesis into screening criteria, running the "
                "screen and ranking the targets that pass, a dossier on one target (default: the top-ranked one), "
                "checking whether the ranking holds under different weightings, finding thin or out-of-date "
                "evidence, and drafting the investment committee screening memo. Call it right away; every "
                "operation has demo defaults and the thesis is already loaded, so never ask for filters or "
                "weights. It never contacts targets, updates a CRM, shares documents, or makes investment decisions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "build_thesis to turn the acquisition thesis (sector, region, revenue band, profitability) "
                            "into screening criteria; screen_targets to run the screen and rank the targets that pass; "
                            "target_dossier for one target's profile, financials, sources and diligence questions; "
                            "challenge_ranking to test whether the ranking holds with different weightings (for "
                            "example weighting financial quality more heavily); evidence_gaps for thin, missing or "
                            "out-of-date evidence and research requests; ic_memo_draft for the investment committee "
                            "screening memo draft."
                        ),
                    },
                    "target": {
                        "type": "string",
                        "description": "Target ID such as T-01 or part of a company name (target_dossier). Default: the top-ranked target.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "build_thesis")
        handlers = {
            "build_thesis": self._build_thesis,
            "screen_targets": self._screen_targets,
            "target_dossier": self._target_dossier,
            "challenge_ranking": self._challenge_ranking,
            "evidence_gaps": self._evidence_gaps,
            "ic_memo_draft": self._ic_memo_draft,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`. Operations: {', '.join(OPERATIONS)}."
        if op == "target_dossier":
            key = _resolve_target(kwargs.get("target"))
            if key is None:
                return (f"# Unknown Target\n\nNo synthetic target matches `{kwargs.get('target')}`; no substitute "
                        f"target was used. Targets: {', '.join(TARGETS)}.\n\n> {_GATE}")
            return handler(key)
        return handler()

    def _build_thesis(self) -> str:
        th = THESIS
        passing = 0
        lines = []
        for key in TARGETS:
            reason = _exclusion(TARGETS[key])
            if reason == "":
                passing += 1
            else:
                lines.append(f"| {key} | {TARGETS[key]['name']} | {reason} |")
        out = [
            f"# Screening Criteria - {th['id']}",
            "",
            f"**Acquirer:** {th['acquirer']} | **Objective:** {th['objective']}",
            "",
            "| Criterion | Setting |",
            "|-----------|---------|",
            f"| Sector focus | {th['sector']} |",
            f"| Region | {th['region']} |",
            f"| Revenue band | ${th['min_revenue']}M-${th['max_revenue']}M |",
            "| Profitability | Positive EBITDA required |",
            f"| Score weights | Strategy fit {WEIGHTS['strategy']}%, financial quality {WEIGHTS['financial']}%, "
            f"market signal {WEIGHTS['market']}%, execution fit {WEIGHTS['execution']}% |",
            "",
            f"**Universe:** {len(TARGETS)} synthetic companies; **{passing} of {len(TARGETS)} pass** the filters.",
            "",
            "| Excluded | Company | Reason |",
            "|----------|---------|--------|",
        ] + lines + [
            "",
            "Next: run the screen and rank the targets that pass.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _screen_targets(self) -> str:
        ranked = _ranked()
        out = [
            f"# Ranked Longlist - {THESIS['id']}",
            "",
            f"{len(ranked)} targets pass the screen (snapshot {SNAPSHOT_DATE}). Weighted score = strategy fit "
            f"{WEIGHTS['strategy']}% + financial quality {WEIGHTS['financial']}% + market signal {WEIGHTS['market']}% "
            f"+ execution fit {WEIGHTS['execution']}%.",
            "",
            "| Rank | Target | Company | Revenue | EBITDA | Growth | Score |",
            "|------|--------|---------|---------|--------|--------|-------|",
        ]
        rank = 0
        for r in ranked:
            rank += 1
            t = TARGETS[r["id"]]
            out.append(f"| {rank} | {r['id']} | {t['name']} | ${t['revenue']}M | ${t['ebitda']}M | {t['growth']}% | "
                       f"{_fmt(r['total'])} |")
        top = ranked[0]
        out += [
            "",
            f"**Shortlist (top {SHORTLIST_SIZE}):** " + ", ".join(f"{r['id']} {r['name']}" for r in ranked[:SHORTLIST_SIZE]) + ".",
            f"**Leader:** {top['id']} {top['name']} at {_fmt(top['total'])}.",
            "",
            "Next: open the dossier on the top-ranked target.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _target_dossier(self, key) -> str:
        t = TARGETS[key]
        reason = _exclusion(t)
        if reason:
            return (f"# {key} {t['name']} - Excluded by the Screen\n\n{reason}. No dossier is prepared for "
                    f"excluded targets.\n\n> {_GATE}")
        ranked = _ranked()
        rank = 0
        total = 0
        for i in range(len(ranked)):
            if ranked[i]["id"] == key:
                rank = i + 1
                total = ranked[i]["total"]
        margin = t["ebitda"] / t["revenue"] * 100
        out = [
            f"# Target Dossier - {key} {t['name']}",
            "",
            f"**Focus:** {t['focus']} | **Region:** {t['region']} | **Rank:** {rank} of {len(ranked)} | "
            f"**Weighted score:** {_fmt(total)}",
            "",
            "| Synthetic financials | Value |",
            "|----------------------|-------|",
            f"| Revenue | ${t['revenue']}M |",
            f"| EBITDA | ${t['ebitda']}M ({margin:.1f}% margin) |",
            f"| Revenue growth | {t['growth']}% |",
            f"| Recurring revenue | {t['recurring']}% |",
            "",
            "| Criterion | Score | Weight |",
            "|-----------|-------|--------|",
        ]
        for k in ["strategy", "financial", "market", "execution"]:
            out.append(f"| {CRITERIA_LABELS[k]} | {t['scores'][k]} | {WEIGHTS[k]}% |")
        out += ["", "**Risk flags:** " + "; ".join(t["risks"]) + ".", "", "**Sources:**"]
        for e in t["evidence"]:
            out.append(f"- [{e['id']}] {e['type']}: {e['title']}, {e['date']}")
        out += ["", "**Diligence questions:**"]
        n = 0
        for q in t["questions"]:
            n += 1
            out.append(f"{n}. {q}")
        out += ["", f"> {_GATE}"]
        return "\n".join(out)

    def _challenge_ranking(self) -> str:
        out = [
            "# Ranking Challenge - Three Weightings",
            "",
            "| Target | " + " | ".join(w["name"] for w in ALT_WEIGHTINGS) + " |",
            "|--------|" + "|".join("------" for w in ALT_WEIGHTINGS) + "|",
        ]
        for r in _ranked():
            t = TARGETS[r["id"]]
            cells = []
            for w in ALT_WEIGHTINGS:
                cells.append(_fmt(_score(t, w)))
            out.append(f"| {r['id']} {t['name']} | " + " | ".join(cells) + " |")
        stable = _shortlist_stable()
        base = _ranked(ALT_WEIGHTINGS[0])
        fin = _ranked(ALT_WEIGHTINGS[1])
        gap_base = (base[1]["total"] - base[2]["total"]) / 100
        gap_fin = (fin[1]["total"] - fin[2]["total"]) / 100
        verdict = ("The top 3 holds under all 3 weightings." if stable
                   else "The top 3 changes between weightings; review the criteria before outreach.")
        out += [
            "",
            f"**Verdict:** {verdict}",
            f"**Watch:** the gap between rank 2 ({base[1]['id']}) and rank 3 ({base[2]['id']}) narrows from "
            f"{gap_base:.1f} to {gap_fin:.1f} points under Financial-first, so treat them as close.",
            "",
            "Next: check where the evidence behind the shortlist is thin or out of date.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _evidence_gaps(self) -> str:
        ranked = _ranked()
        shortlist = [r["id"] for r in ranked[:SHORTLIST_SIZE]]
        out = [
            f"# Evidence Coverage - Snapshot {SNAPSHOT_DATE}",
            "",
            f"Required per target: {', '.join(REQUIRED_EVIDENCE)}. Sources dated before {STALE_BEFORE} are stale.",
            "",
            "| Request | Target | Evidence | Issue | Detail | Shortlist |",
            "|---------|--------|----------|-------|--------|-----------|",
        ]
        total = 0
        on_short = 0
        targets_with = 0
        for r in ranked:
            gaps = _gaps(r["id"])
            if gaps:
                targets_with += 1
            for g in gaps:
                total += 1
                flag = "Yes" if r["id"] in shortlist else "No"
                if r["id"] in shortlist:
                    on_short += 1
                out.append(f"| RR-{total:02d} | {r['id']} | {g['type']} | {g['issue']} | {g['detail']} | {flag} |")
        out += [
            "",
            f"**{total} evidence gaps across {targets_with} targets; {on_short} sit on the shortlist.** "
            f"{shortlist[0]} {TARGETS[shortlist[0]]['name']} has complete, current evidence.",
            "",
            "The research requests above are drafts for the research team; none has been sent.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _ic_memo_draft(self) -> str:
        ranked = _ranked()
        short = ranked[:SHORTLIST_SIZE]
        revenue = 0
        open_gaps = 0
        for r in short:
            revenue += TARGETS[r["id"]]["revenue"]
            open_gaps += len(_gaps(r["id"]))
        out = [
            "# Investment Committee Screening Memo - DRAFT ICM-2026-07-01",
            "",
            f"**Thesis:** {THESIS['id']} {THESIS['objective']} | **Universe:** {len(TARGETS)} | "
            f"**Passed screen:** {len(ranked)} | **Shortlist:** {len(short)}",
            "",
            "| Rank | Target | Company | Score | Revenue | Key risk |",
            "|------|--------|---------|-------|---------|----------|",
        ]
        rank = 0
        for r in short:
            rank += 1
            t = TARGETS[r["id"]]
            out.append(f"| {rank} | {r['id']} | {t['name']} | {_fmt(r['total'])} | ${t['revenue']}M | {t['risks'][0]} |")
        out += [
            "",
            f"**Combined shortlist revenue:** ${revenue}M. **Ranking check:** "
            + (f"top {SHORTLIST_SIZE} stable under {len(ALT_WEIGHTINGS)} weightings." if _shortlist_stable()
               else "top 3 changes between weightings; review before outreach."),
            f"**Conditions before outreach:** close {open_gaps} open evidence gaps on the shortlist; the corporate "
            "development lead approves any first contact.",
            "**Ask of the committee:** approve the shortlist for confidential management outreach planning.",
            "",
            "Status: Draft for the corporate development lead. Not sent; no target contacted.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)


if __name__ == "__main__":
    agent = MATargetSourcingAgent()
    for op in OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
