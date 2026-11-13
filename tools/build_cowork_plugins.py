#!/usr/bin/env python3
"""Build one Cowork plugin per solution: one plugin, one skill, its data beside it.

Each solution already ships its jobs as skills under ``manual/skills`` and its
synthetic data as knowledge files. Microsoft 365 Copilot Cowork accepts a plugin
as a .zip (Cowork > Customize > Add > Upload). This builder folds a solution's
jobs into ONE skill, one to one with the solution's agent, and writes
``solutions/<slug>/exports/<slug>-cowork-plugin.zip``.

    python tools/build_cowork_plugins.py            # write every plugin
    python tools/build_cowork_plugins.py --check    # fail if any is stale or missing

The output is deterministic (fixed timestamps, sorted entries), so --check is a
byte comparison. The three plugins first proven by hand in Cowork
(account-intelligence, first-time-fix, claims-processing) are built by this
same code.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLUTIONS = ROOT / "solutions"
VERSION = "1.0.0"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def _order(path: Path) -> tuple[int, str]:
    """Skill folders carry their order as a trailing number (…_01, …_bp03)."""
    found = re.search(r"(\d+)$", path.parent.name)
    return (int(found.group(1)) if found else 0, path.parent.name)


def _knowledge(solution: Path) -> list[Path]:
    for folder in (solution / "manual" / "knowledge",
                   solution / "copilot-studio" / "capabilities" / "knowledge" / "files"):
        files = sorted(folder.glob("*.md")) if folder.is_dir() else []
        if files:
            return files
    return []


def _short(slug: str, path: Path) -> str:
    name = re.sub(r"^aibast_", "", path.name)
    return re.sub(rf"^{re.escape(slug)}-", "", name)


def _plain(value: str) -> str:
    """A front-matter value as plain text: unwrap a double-quoted scalar."""
    value = value.strip()
    if value.startswith('"'):
        try:
            return json.loads(value)
        except ValueError:
            return value.strip('"')
    return value


def card_name(slug: str) -> str:
    """The solution's name as the library card shows it, so every surface agrees.

    The first heading of a solution's instructions is not always its name
    (several read "Role"), so the catalog entry is the source.
    """
    entry = ROOT / "api" / "v1" / "solutions" / f"{slug}.json"
    if not entry.is_file():
        return ""
    return str(json.loads(entry.read_text(encoding="utf-8")).get("name") or "").strip()


def build_skill(solution: Path) -> tuple[str, dict[str, str], str]:
    """Return (SKILL.md text, {file name: text} for the data files, title)."""
    slug = solution.name
    glob_text = (solution / "manual" / "GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    title = card_name(slug)
    if not title:
        heading = re.search(r"^# (.+?)(?: — .*)?$", glob_text, re.M)
        title = heading.group(1).strip() if heading else slug.replace("-", " ").title()
    always = re.sub(r"^# .*\n", "", glob_text.strip()).replace("\n## ", "\n### ").strip()

    jobs, sections = [], []
    for path in sorted((solution / "manual" / "skills").glob("*/SKILL.md"), key=_order):
        text = path.read_text(encoding="utf-8")
        front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        described = re.search(r"^description:\s*(.+)$", front.group(1), re.M) if front else None
        body = re.sub(r"<!--.*?-->\s*", "", text[front.end():] if front else text, flags=re.S).strip()
        top = re.match(r"^# (.+)\n", body)
        job = top.group(1).split("—")[-1].strip() if top else path.parent.name
        body = re.sub(r"^# .*\n", "", body)
        body = re.sub(r"^## ", "### ", body, flags=re.M).strip()
        when = _plain(described.group(1)) if described else ""
        jobs.append(job)
        sections.append(f"## Job: {job}\n\n" + (f"When: {when}\n\n" if when else "") + body)

    data = {_short(slug, p): p.read_text(encoding="utf-8") for p in _knowledge(solution)}
    description = (f"{title}. Jobs: {'; '.join(jobs)}. Synthetic demo data only. "
                   "Use for any of those requests.")
    read_first = ""
    if data:
        names = ", ".join(f"`{name}`" for name in data)
        read_first = (f"Read {names} beside this file first; where a job says "
                      "\"knowledge files\", it means those. ")
    skill = (
        "---\n"
        f"name: {slug}\n"
        # a JSON string is a valid YAML double-quoted scalar; an unquoted
        # "Jobs: ..." is rejected by Cowork's YAML reader
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"One agent, {len(jobs)} jobs. Pick the job that matches the request and follow its "
        f"section. {read_first}Everything is synthetic demo data.\n\n"
        f"## Always\n\n{always}\n\n" + "\n\n".join(sections) + "\n"
    )
    return skill, data, title


def build_zip(solution: Path) -> bytes:
    slug = solution.name
    skill, data, title = build_skill(solution)
    manifest = {
        "name": slug,
        # Cowork allows only lowercase letters, numbers and hyphens in "name" and
        # shows it title-cased ("Ask Hr"); "displayName" is the label people see.
        "displayName": title,
        "version": VERSION,
        "description": f"{title} from the AI Agents Library (synthetic demo data).",
        "author": {"name": "AI Agents Library"},
    }
    entries = {".claude-plugin/plugin.json": json.dumps(manifest, indent=2) + "\n",
               f"skills/{slug}/SKILL.md": skill}
    entries.update({f"skills/{slug}/{name}": text for name, text in data.items()})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name].encode("utf-8"))
    return buffer.getvalue()


def solutions() -> list[Path]:
    return sorted(p for p in SOLUTIONS.iterdir()
                  if (p / "manual" / "GLOBAL-INSTRUCTIONS.md").is_file()
                  and any((p / "manual" / "skills").glob("*/SKILL.md")))


def target(solution: Path) -> Path:
    return solution / "exports" / f"{solution.name}-cowork-plugin.zip"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if any plugin is stale")
    args = parser.parse_args()
    stale = []
    for solution in solutions():
        built, out = build_zip(solution), target(solution)
        if args.check:
            if not out.is_file() or out.read_bytes() != built:
                stale.append(out.relative_to(ROOT).as_posix())
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(built)
    if stale:
        print("Stale or missing Cowork plugins (run tools/build_cowork_plugins.py):")
        print("\n".join(f"  {name}" for name in stale))
        return 1
    print(f"{'Checked' if args.check else 'Built'} {len(solutions())} Cowork plugins")
    return 0


if __name__ == "__main__":
    sys.exit(main())
