"""RAPP learning content for the library static API (api/v1/rapp/).

Read at build time from this repository's own copies, never hand-copied:

- docs/rapp-guide.html      the 14 production steps and the Experimental tools section
- docs/vault/**/*.md        one note per concept, the per-step explanation, and the glossary
- docs/experimental/tools.json  the experimental tools list

Every document names its sources with path and sha256, so a reader can check
that the answer matches the file it came from. Called from build_library_api.py.
"""

from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
from pathlib import Path

SCHEMA_RAPP_INDEX = "aibast-rapp-index/1.0"
SCHEMA_RAPP_STEP = "aibast-rapp-step/1.0"
SCHEMA_RAPP_CONCEPT = "aibast-rapp-concept/1.0"
SCHEMA_RAPP_GLOSSARY = "aibast-rapp-glossary/1.0"
SCHEMA_RAPP_TOOLS = "aibast-rapp-tools/1.0"

GUIDE = "docs/rapp-guide.html"
VAULT = "docs/vault"
TOOLS = "docs/experimental/tools.json"
STEPS = 14
# Vault folders that hold concepts. Production Guide step notes become steps;
# the generated index and the notice files are not concepts.
CONCEPT_SECTIONS = ("Start Here", "Production Guide", "Protocol", "Operations", "Building", "ms-rapp-1", "Reference")
PROOF_HEADINGS = ("checklist", "decision point", "quality gate", "exit", "gate")


class RappContentError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source(root: Path, rel: str, anchor: str | None = None) -> dict:
    src = {"path": rel, "sha256": _sha((root / rel).read_bytes())}
    if anchor:
        src["anchor"] = anchor
    return src


def _text(fragment: str) -> str:
    """HTML fragment -> plain text, one line per block, list items as '- '."""
    s = re.sub(r"<(script|style)\b.*?</\1>", "", fragment, flags=re.S)
    s = re.sub(r"<li\b[^>]*>", "\n- ", s)
    s = re.sub(r"</?(p|div|ul|ol|h[1-6]|br|tr|pre|table)\b[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln and ln != "-")


def _items(fragment: str) -> list[str]:
    return [t for t in (_text(m) for m in re.findall(r"<li\b[^>]*>(.*?)</li>", fragment, flags=re.S)) if t]


def _section(guide: str, sid: str) -> str:
    start = guide.find(f'<div class="content-section" id="{sid}"')
    if start < 0:
        start = guide.find(f'<div class="content-section active" id="{sid}"')
    if start < 0:
        raise RappContentError(f"{GUIDE}: no section #{sid}")
    end = guide.find('<div class="content-section', start + 10)
    return guide[start:end if end > 0 else len(guide)]


def _h3_blocks(section: str) -> list[tuple[str, str]]:
    parts = re.split(r"<h3>(.*?)</h3>", section, flags=re.S)
    out = []
    for i in range(1, len(parts), 2):
        heading = _text(parts[i]).lstrip("✓").strip()
        out.append((heading, parts[i + 1]))
    return out


def _md_blocks(body: str) -> list[tuple[str, str]]:
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    return [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def _frontmatter(text: str) -> tuple[dict, str]:
    meta: dict[str, str] = {}
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            text = text[end + 5:]
    return meta, text.strip() + "\n"


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def _notes(root: Path) -> list[tuple[str, dict, str]]:
    notes = []
    for section in CONCEPT_SECTIONS:
        for path in sorted((root / VAULT / section).glob("*.md")):
            rel = path.relative_to(root).as_posix()
            meta, body = _frontmatter(path.read_text(encoding="utf-8"))
            notes.append((rel, meta, body))
    return notes


def _step_notes(notes) -> dict[int, tuple[str, dict, str]]:
    out = {}
    for rel, meta, body in notes:
        m = re.match(r"Step (\d\d) ", meta.get("title", ""))
        if meta.get("section") == "Production Guide" and m:
            out[int(m.group(1))] = (rel, meta, body)
    return out


def step_docs(root: Path, notes) -> dict[int, dict]:
    guide = (root / GUIDE).read_text(encoding="utf-8")
    by_step = _step_notes(notes)
    docs = {}
    for n in range(1, STEPS + 1):
        sec = _section(guide, f"step{n}")
        title = _text(re.search(r'<h1 class="section-title">(.*?)</h1>', sec, flags=re.S).group(1))
        sub = re.search(r'<p class="section-subtitle">(.*?)</p>', sec, flags=re.S)
        badge = re.search(r'<span class="badge[^"]*">(.*?)</span>', sec, flags=re.S)
        blocks = _h3_blocks(sec)
        named = {h.lower(): b for h, b in blocks}
        do = [_text(named[k]) for k in ("objective", "business summary") if k in named]
        proof = []
        for h, b in blocks:
            if any(p in h.lower() for p in PROOF_HEADINGS):
                proof.append({"check": h, "items": _items(b) or [_text(b)]})
        if n not in by_step:
            raise RappContentError(f"{VAULT}/Production Guide: no note for step {n}")
        note_rel, note_meta, note_body = by_step[n]
        for h, b in _md_blocks(note_body):
            if any(p in h.lower() for p in PROOF_HEADINGS) and not any(x["check"].lower() == h.lower() for x in proof):
                bullets = [ln[2:].strip() for ln in b.splitlines() if ln.startswith(("- ", "* "))]
                proof.append({"check": h, "items": bullets or [b.strip()], "from": "explain"})
        docs[n] = {
            "schema": SCHEMA_RAPP_STEP,
            "step": n,
            "of": STEPS,
            "title": title,
            "summary": _text(sub.group(1)) if sub else "",
            "kind": _text(badge.group(1)).lower() if badge else "",
            "do": "\n".join(do),
            "duration": _text(named["duration"]) if "duration" in named else "",
            "owner": _text(named["owner"]) if "owner" in named else "",
            "get": _items(named.get("output", "")),
            "proof": proof,
            "done_when": "Every proof check passes." if proof else "Every item in get exists; this step has no separate checklist.",
            "sections": [{"heading": h, "text": _text(b)} for h, b in blocks],
            "explain": {"title": note_meta.get("title", ""), "markdown": note_body},
            "prev": f"api/v1/rapp/steps/{n - 1}.json" if n > 1 else None,
            "next": f"api/v1/rapp/steps/{n + 1}.json" if n < STEPS else None,
            "page": f"docs/rapp-guide.html#step{n}",
            "sources": [_source(root, GUIDE, f"step{n}"), _source(root, note_rel)],
        }
    return docs


def concept_docs(root: Path, notes) -> dict[str, dict]:
    steps = {rel for rel, _, _ in _step_notes(notes).values()}
    docs = {}
    for rel, meta, body in notes:
        if rel in steps:
            continue
        title = meta.get("title") or Path(rel).stem
        slug = slugify(title)
        if slug in docs:
            raise RappContentError(f"duplicate concept slug {slug} from {rel}")
        docs[slug] = {
            "schema": SCHEMA_RAPP_CONCEPT,
            "slug": slug,
            "title": title,
            "section": meta.get("section", ""),
            "hook": meta.get("hook", ""),
            "markdown": body,
            "sources": [_source(root, rel)],
        }
    return docs


def glossary_doc(root: Path) -> dict:
    rel = f"{VAULT}/Reference/Glossary.md"
    _, body = _frontmatter((root / rel).read_text(encoding="utf-8"))
    terms, group = [], ""
    for line in body.splitlines():
        if line.startswith("## "):
            group = line[3:].strip()
            continue
        m = re.match(r"- \*\*(.+?)\*\* — (.+)", line)
        if m:
            terms.append({"term": m.group(1), "group": group, "definition": m.group(2).strip()})
    if not terms:
        raise RappContentError(f"{rel}: no glossary terms")
    return {"schema": SCHEMA_RAPP_GLOSSARY, "count": len(terms), "terms": terms,
            "concept": "api/v1/rapp/concepts/glossary.json", "sources": [_source(root, rel)]}


def tools_doc(root: Path) -> dict:
    data = json.loads((root / TOOLS).read_text(encoding="utf-8"))
    guide = (root / GUIDE).read_text(encoding="utf-8")
    about = _text(_section(guide, "tools"))
    tools = [{k: t.get(k) for k in ("name", "kind", "display_name", "description", "version")
              if t.get(k) is not None} for t in data.get("tools", [])]
    return {"schema": SCHEMA_RAPP_TOOLS, "title": "Experimental tools", "disclaimer": data["disclaimer"],
            "count": len(tools), "tools": tools, "registry": TOOLS, "page": "docs/rapp-guide.html#tools",
            "about": about,
            "sources": [_source(root, TOOLS), _source(root, GUIDE, "tools")]}


def rapp_files(root: Path) -> tuple[dict[str, object], dict]:
    notes = _notes(root)
    steps = step_docs(root, notes)
    concepts = concept_docs(root, notes)
    files: dict[str, object] = {}
    for n, doc in steps.items():
        files[f"api/v1/rapp/steps/{n}.json"] = doc
    for slug, doc in concepts.items():
        files[f"api/v1/rapp/concepts/{slug}.json"] = doc
    glossary = glossary_doc(root)
    tools = tools_doc(root)
    files["api/v1/rapp/glossary.json"] = glossary
    files["api/v1/rapp/tools.json"] = tools
    summary = {"steps": len(steps), "concepts": len(concepts), "terms": glossary["count"], "tools": tools["count"]}
    files["api/v1/rapp/index.json"] = {
        "schema": SCHEMA_RAPP_INDEX,
        "title": "Learn RAPP step by step",
        "description": "The RAPP production guide as data: 14 steps from discovery call to post-deployment review, "
                       "the concepts behind them, a glossary and the experimental tools.",
        "summary": summary,
        "start": ["Read api/v1/rapp/steps/1.json, then follow next.",
                  "Each step has do (what to do), get (what you get) and proof (how you know it is done).",
                  "Look up a word in api/v1/rapp/glossary.json, or a topic in api/v1/rapp/concepts/<slug>.json."],
        "steps": [{"step": n, "title": d["title"], "summary": d["summary"], "doc": f"api/v1/rapp/steps/{n}.json"}
                  for n, d in steps.items()],
        "concepts": [{"slug": s, "title": d["title"], "section": d["section"], "hook": d["hook"],
                      "doc": f"api/v1/rapp/concepts/{s}.json"} for s, d in concepts.items()],
        "glossary": "api/v1/rapp/glossary.json",
        "tools": "api/v1/rapp/tools.json",
        "endpoints": {"step": "api/v1/rapp/steps/{n}.json", "concept": "api/v1/rapp/concepts/{slug}.json",
                      "glossary": "api/v1/rapp/glossary.json", "tools": "api/v1/rapp/tools.json"},
    }
    return files, summary
