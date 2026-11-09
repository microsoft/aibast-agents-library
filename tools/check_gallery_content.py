#!/usr/bin/env python3
"""The Copilot Studio Gallery's five publication checks, the deterministic part, over submissions/.

Source: the gallery's .github/instructions/submission-review.instructions.md (pinned commit in
tools/gallery_contract.json). A reviewer there applies these by reading; this tool applies what can
be read mechanically so a folder fails here before it ever reaches a reviewer, in either direction.

  1. Sample and regulated use   README says it is a sample AND carries the illustrative / may be wrong /
                                not professional advice / qualified human review wording.
  2. Secrets and private data   no credential-shaped files in the package (.env, .pem, .key, .pfx, .p12);
                                value scanning stays with GitHub secret scanning, which runs on the repo.
  3. Consequential destinations every connector, connection reference, flow and tool the package declares
                                is named in the README (a visitor learns where data goes before importing).
  4. Honest capabilities        README makes no production-readiness or certification claim.
  5. Essential prerequisites    same declarations as 3 must appear under a prerequisites heading.

Exit 0 when every folder passes; otherwise one line per finding and exit 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SAMPLE = re.compile(r"\b(sample|synthetic|demo|illustrative|not (for )?production|prototype)\b", re.I)
REVIEW = re.compile(r"(human review|qualified (person|professional|human)|review(ed)? by a (qualified|licensed)|"
                    r"not (professional|legal|medical|financial|tax) advice|may be (wrong|incorrect|inaccurate)|not a substitute for)", re.I)
OVERCLAIM = re.compile(r"\b(production[- ]ready|certified|HIPAA[- ]compliant|SOC ?2|GDPR[- ]compliant|PCI[- ]compliant|fully compliant|guarantees?)\b", re.I)
CREDENTIAL_FILES = (".env", ".pem", ".key", ".pfx", ".p12")
PREREQ_HEADING = re.compile(r"^#{1,4}\s.*(prerequisite|before you|requirements?|setup|set it up|import)", re.I | re.M)


FRIENDLY_CONNECTORS = {"shared_workiqmcp": "Work IQ MCP", "shared_commondataserviceforapps": "Microsoft Dataverse",
                       "shared_office365": "Office 365 Outlook", "shared_sharepointonline": "SharePoint", "shared_teams": "Microsoft Teams"}


def connector_label(connector_id: str) -> str:
    short = connector_id.rstrip("/").rsplit("/", 1)[-1]
    friendly = FRIENDLY_CONNECTORS.get(short)
    return f"{friendly} (`{short}`)" if friendly else f"`{short}`"


def declared_connections_xml(xml: str) -> list[str]:
    """Connector short ids declared as connection references in customizations.xml."""
    ids = set()
    for m in re.finditer(r"<connectionreference[^>]*>(.*?)</connectionreference>", xml, re.S):
        conn = re.search(r"<connectorid>(.*?)</connectorid>", m.group(1), re.S)
        if conn:
            ids.add(conn.group(1).strip().rstrip("/").rsplit("/", 1)[-1])
    return sorted(ids)


def declared_destinations(solution: Path) -> list[str]:
    """What the package declares that reaches outside it: connector ids (connection references),
    flows and tool/action components. Each must be named in the README."""
    names: set[str] = set()
    cust = solution / "customizations.xml"
    if cust.exists():
        names.update(declared_connections_xml(cust.read_text(encoding="utf-8-sig", errors="replace")))
    for wf in sorted((solution / "Workflows").glob("*.json")) if (solution / "Workflows").is_dir() else []:
        names.add(f"flow {wf.stem.rsplit('-', 1)[0]}")
    for comp in sorted((solution / "botcomponents").glob("*/botcomponent.xml")) if (solution / "botcomponents").is_dir() else []:
        kind = comp.parent.name
        if ".tool." in kind or ".action." in kind or ".connector." in kind or ".mcp." in kind:
            disp = re.search(r"<name>(.*?)</name>", comp.read_text(encoding="utf-8-sig", errors="replace"), re.S)
            names.add(disp.group(1).strip() if disp else kind)
    return sorted(names)


def check_folder(folder: Path) -> list[str]:
    findings = []
    slug = folder.name
    readme_path = folder / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    if not readme:
        return [f"{slug}: README.md missing (checks 1, 3, 4, 5 cannot be read)"]
    # 1
    if not SAMPLE.search(readme):
        findings.append(f"{slug}: check 1, README never says this is a sample")
    if not REVIEW.search(readme):
        findings.append(f"{slug}: check 1, README lacks the illustrative / may be wrong / not advice / qualified human review wording")
    # 2
    package = folder / "solution" if (folder / "solution").is_dir() else folder / "app"
    for p in package.rglob("*") if package.is_dir() else []:
        if p.is_file() and (p.name.lower().endswith(CREDENTIAL_FILES) or p.name.lower() == ".env"):
            findings.append(f"{slug}: check 2, credential-shaped file in the package: {p.relative_to(folder)}")
    # 3 + 5
    if (folder / "solution").is_dir():
        lowered = readme.lower()
        missing = [n for n in declared_destinations(folder / "solution") if n.lower() not in lowered and n.lower().removeprefix("flow ") not in lowered]
        for n in missing:
            findings.append(f"{slug}: checks 3/5, package declares '{n}' but the README never names it")
        if declared_destinations(folder / "solution") and not PREREQ_HEADING.search(readme):
            findings.append(f"{slug}: check 5, package declares connections or flows but the README has no prerequisites section")
    # 4
    for m in OVERCLAIM.finditer(readme):
        line = readme.count("\n", 0, m.start()) + 1
        context = readme[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        if re.search(r"\b(not|never|no|isn't|is not|without)\b[^.]{0,30}$", readme[max(0, m.start() - 40):m.start()], re.I):
            continue  # "not production-ready" is the honest form
        findings.append(f"{slug}: check 4, README line {line} claims '{m.group(0)}' ({context.strip()})")
    return findings


def main(argv=None) -> int:
    """`check_gallery_content.py [root] [--strict-all]`. Folders we author (listed in
    tools/gallery_submissions.json) must pass; folders that arrived from elsewhere are reported, not
    failed, unless --strict-all (the gallery's reviewer judges 'equivalent wording' by reading, and
    their own tree does not pass this mechanical reading: 1 of 36 on 2026-11-09)."""
    args = [a for a in (argv if argv is not None else sys.argv[1:])]
    strict_all = "--strict-all" in args
    args = [a for a in args if not a.startswith("--")]
    root = Path(args[0]) if args else ROOT
    config = root / "tools" / "gallery_submissions.json"
    ours = set(json.loads(config.read_text())["submissions"]) if config.exists() else set()
    folders = sorted(p for p in (root / "submissions").iterdir()
                     if p.is_dir() and not p.name.startswith(("_", ".")) and (p / "metadata.json").exists())
    failures, reports = [], []
    for folder in folders:
        for f in check_folder(folder):
            (failures if strict_all or folder.name in ours else reports).append(f)
    for f in failures:
        print(f"FAIL {f}")
    for f in reports:
        print(f"note {f}")
    failed = {f.split(":")[0] for f in failures}
    noted = {f.split(":")[0] for f in reports}
    print(f"gallery content checks: {len(folders) - len(failed) - len(noted)} of {len(folders)} folders pass; "
          f"{len(failed)} fail ({len(failures)} findings); {len(noted)} inbound folders noted ({len(reports)} findings)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
