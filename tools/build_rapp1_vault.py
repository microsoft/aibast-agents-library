#!/usr/bin/env python3
"""Build or verify the RAPP/1 reference vault behind the production guide.

The vault at docs/vault/ is a folder of Markdown notes that expands
docs/rapp-guide.html: every guide step, and the RAPP/1 protocol it rests on.
This tool validates the notes and renders everything derived from them:

- manifest.json        note list, order, byte counts and sha256 per note
- content-bundle.json  the notes themselves, hash-pinned, read by the viewer
- _index.md            the generated index note
- llms.txt             short plain-text map for AI tools
- llms-full.txt        every note as one plain-text file
- rapp1-vault.zip      the same notes as an Obsidian vault, byte-reproducible

    python tools/build_rapp1_vault.py --write   # regenerate after editing notes
    python tools/build_rapp1_vault.py --check   # fail on any drift (CI)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "docs" / "vault"
SITE = "https://microsoft.github.io/aibast-agents-library/docs/vault/"

# The upstream specification these notes expand. Its address and licence text
# live in NOTICE.md; notes cite it by section and this commit.
UPSTREAM_COMMIT = "0b24e7d60786d39d97265338add9ca784bf5a7ab"

SECTIONS = ("Start Here", "Production Guide", "Protocol", "Operations", "Building", "ms-rapp-1", "Reference")
# Notes in these sections restate the upstream specification, so each must name the pin.
PINNED_SECTIONS = ("Protocol", "Operations")
TOP_LEVEL = ("README.md", "_index.md", "NOTICE.md")
GENERATED = {"_index.md"}
REQUIRED_FIELDS = ("title", "section", "status", "hook", "source")
STATUSES = {"published", "draft"}

FORBIDDEN_IDENTITY = (
    "github.com/kody-w/",
    "raw.githubusercontent.com/kody-w/",
    "kody-w.github.io",
    "kodyw.com",
)
# NOTICE.md carries the upstream licence notice, which names its source.
IDENTITY_EXEMPT = {"NOTICE.md"}
TONE_TERMS = (
    "organism", "organisms", "creature", "creatures", "summon", "summons", "summoned",
    "incantation", "easter egg", "minigame", "safe word", "magic", "magical", "spell",
)
TONE_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in TONE_TERMS) + r")\b", re.IGNORECASE)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]+)?\]\]")
ZIP_ROOT = "RAPP1 Reference Vault/"
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


class VaultError(ValueError):
    pass


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[match.group(1)] = value
    return meta, text[end + 4 :].lstrip("\n")


def strip_code(body: str) -> str:
    """Drop fenced and inline code so identifiers there are not judged as prose."""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", body)


def discover() -> list[Path]:
    notes = [VAULT / name for name in TOP_LEVEL if name not in GENERATED]
    for section in SECTIONS:
        folder = VAULT / section
        if not folder.is_dir():
            raise VaultError(f"missing section folder: {section}")
        notes.extend(sorted(folder.glob("*.md"), key=lambda p: p.name.lower()))
    strays = {
        p for p in VAULT.rglob("*.md")
        if p.relative_to(VAULT).as_posix() not in GENERATED
    } - set(notes)
    if strays:
        raise VaultError(f"notes outside the known sections: {sorted(str(s.relative_to(VAULT)) for s in strays)}")
    return notes


def load_notes() -> list[dict]:
    notes = []
    for path in discover():
        if not path.exists():
            raise VaultError(f"missing note: {path.relative_to(VAULT)}")
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        rel = path.relative_to(VAULT).as_posix()
        notes.append({"path": rel, "raw": raw, "meta": meta, "body": body})
    return notes


def validate(notes: list[dict]) -> None:
    problems: list[str] = []
    names = {Path(n["path"]).stem.lower() for n in notes} | {"_index", "index", "welcome"}
    for note in notes:
        rel, meta, body = note["path"], note["meta"], note["body"]
        for field in REQUIRED_FIELDS:
            if field == "section" and "/" not in rel:
                continue
            if not meta.get(field):
                problems.append(f"{rel}: frontmatter needs '{field}'")
        if meta.get("status") and meta["status"] not in STATUSES:
            problems.append(f"{rel}: status must be one of {sorted(STATUSES)}")
        if "/" in rel:
            section, stem = rel.split("/", 1)
            if meta.get("section") != section:
                problems.append(f"{rel}: section '{meta.get('section')}' does not match its folder")
            if meta.get("title") != Path(stem).stem:
                problems.append(f"{rel}: title must equal the file name so wikilinks resolve in Obsidian")
            if section in PINNED_SECTIONS and meta.get("upstream_commit") != UPSTREAM_COMMIT:
                problems.append(f"{rel}: must pin upstream_commit {UPSTREAM_COMMIT}")
        if meta.get("upstream_commit") and meta["upstream_commit"] != UPSTREAM_COMMIT:
            problems.append(f"{rel}: upstream_commit differs from the vault pin")
        if not re.search(r"^# ", body, re.M):
            problems.append(f"{rel}: needs a '# ' heading")
        for target in WIKILINK_RE.findall(strip_code(body)):
            # Obsidian writes [[Note\|alias]] inside tables; the backslash is not part of the name.
            if target.rstrip("\\").strip().lower() not in names:
                problems.append(f"{rel}: wikilink [[{target}]] has no note")
        lowered = note["raw"].lower()
        if rel not in IDENTITY_EXEMPT:
            for forbidden in FORBIDDEN_IDENTITY:
                if forbidden in lowered:
                    problems.append(f"{rel}: contains personal-fork address {forbidden}")
        for match in TONE_RE.finditer(strip_code(body)):
            problems.append(f"{rel}: wording '{match.group(0)}' does not meet the documentation tone bar")
    if problems:
        raise VaultError("\n".join(problems))


def render_index(notes: list[dict]) -> str:
    lines = [
        "---",
        "title: Index",
        "status: published",
        "hook: Every note in the vault, grouped by section.",
        "source: generated by tools/build_rapp1_vault.py",
        "---",
        "",
        "# Index",
        "",
        "Every note in the RAPP/1 reference vault, grouped by section. Start with [[Welcome]] or [[Reading Paths]].",
    ]
    for section in SECTIONS:
        lines += ["", f"## {section}", ""]
        for note in notes:
            if note["path"].startswith(section + "/"):
                stem = Path(note["path"]).stem
                lines.append(f"- [[{stem}]] - {note['meta'].get('hook', '')}")
    return "\n".join(lines) + "\n"


def ordered(notes: list[dict], index_text: str) -> list[dict]:
    meta, body = parse_frontmatter(index_text)
    index = {"path": "_index.md", "raw": index_text, "meta": meta, "body": body}
    top = [n for n in notes if "/" not in n["path"]]
    return [top[0], index, *top[1:], *[n for n in notes if "/" in n["path"]]]


def title_of(note: dict) -> str:
    if note["path"] == "README.md":
        return "Welcome"
    return note["meta"].get("title") or Path(note["path"]).stem


def render_all() -> dict[str, bytes]:
    notes = load_notes()
    index_text = render_index(notes)
    allnotes = ordered(notes, index_text)
    validate(allnotes)

    entries, bundle = [], {}
    for note in allnotes:
        raw = note["raw"].encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        section = note["path"].split("/", 1)[0] if "/" in note["path"] else None
        entries.append({
            "path": note["path"],
            "title": title_of(note),
            "section": section,
            "status": note["meta"].get("status", "published"),
            "bytes": len(raw),
            "sha256": digest,
        })
        bundle[note["path"]] = {"bytes": len(raw), "sha256": digest, "content": note["raw"]}

    renderer = (VAULT / "marked.min.js").read_bytes()
    manifest = {
        "title": "RAPP/1 Reference Vault",
        "subtitle": "Production guide reference",
        "github": {
            "owner": "microsoft",
            "repo": "aibast-agents-library",
            "navigation_ref": "main",
            "vault_path": "docs/vault",
        },
        "entry": "README.md",
        "index": "_index.md",
        "upstream": {"name": "RAPP/1 specification", "license": "MIT", "commit": UPSTREAM_COMMIT, "notice": "NOTICE.md"},
        "notes": entries,
        "runtime_content": {
            "bundle": "content-bundle.json",
            "renderer": "marked.min.js",
            "renderer_package": "marked@12.0.2",
            "renderer_sha256": hashlib.sha256(renderer).hexdigest(),
            "renderer_license": "vendor/marked-LICENSE.txt",
            "network_fallback": False,
            "hash_required": True,
        },
    }
    content_bundle = {
        "schema": "rapp-vault-content-bundle/1.0",
        "record_kind": "immutable-checked-in-vault-content",
        "network_fallback": False,
        "note_count": len(bundle),
        "notes": bundle,
    }

    llms = [
        "# RAPP/1 Reference Vault",
        "",
        "> The reference vault for the RAPP production guide in the AIBAST Agents Library: every step of the",
        "> 14-step guide expanded, and the RAPP/1 protocol it rests on, as linked Markdown notes. Notes that",
        f"> restate the RAPP/1 specification are pinned to upstream commit {UPSTREAM_COMMIT} (MIT; see NOTICE.md).",
        "",
        f"- [Production guide]({SITE}../rapp-guide.html): the 14-step RAPP production process",
        f"- [All notes as one file]({SITE}llms-full.txt)",
        f"- [Obsidian vault download]({SITE}rapp1-vault.zip)",
    ]
    for section in (None, *SECTIONS):
        group = [e for e in entries if e["section"] == section]
        llms += ["", f"## {section or 'Vault'}", ""]
        for entry in group:
            meta, _ = parse_frontmatter(bundle[entry["path"]]["content"])
            url = SITE + "/".join(quote(part) for part in entry["path"].split("/"))
            hook = meta.get("hook", "")
            llms.append(f"- [{entry['title']}]({url})" + (f": {hook}" if hook else ""))
    full = [
        "# RAPP/1 Reference Vault - all notes",
        "",
        f"Source: {SITE} . Protocol notes are pinned to RAPP/1 upstream commit {UPSTREAM_COMMIT} (MIT; see NOTICE.md).",
    ]
    for entry in entries:
        full += ["", "=" * 72, f"FILE: {entry['path']}", "=" * 72, "", bundle[entry["path"]]["content"].rstrip("\n")]

    return {
        "_index.md": index_text.encode("utf-8"),
        "manifest.json": (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "content-bundle.json": (json.dumps(content_bundle, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "llms.txt": ("\n".join(llms) + "\n").encode("utf-8"),
        "llms-full.txt": ("\n".join(full) + "\n").encode("utf-8"),
        "rapp1-vault.zip": render_zip(allnotes, manifest),
    }


def render_zip(notes: list[dict], manifest: dict) -> bytes:
    files = {note["path"]: note["raw"].encode("utf-8") for note in notes}
    files[".obsidian/app.json"] = (json.dumps({"livePreview": True, "showLineNumber": False}, indent=2) + "\n").encode()
    files["HOW TO OPEN.md"] = (
        "# RAPP/1 Reference Vault\n\n"
        "This folder is an Obsidian vault.\n\n"
        "1. Unzip it.\n"
        "2. In Obsidian choose **Open folder as vault** and pick this folder.\n"
        "3. Start at README.md. Wikilinks, search and the graph work with no plugins.\n\n"
        f"Read it in the browser at {SITE}\n"
    ).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(ZIP_ROOT + name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name])
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if any derived file is stale")
    mode.add_argument("--write", action="store_true", help="regenerate derived files")
    args = parser.parse_args(argv)
    try:
        outputs = render_all()
    except (OSError, UnicodeDecodeError, VaultError) as error:
        print(f"vault invalid:\n{error}", file=sys.stderr)
        return 1
    if args.write:
        for name, data in outputs.items():
            (VAULT / name).write_bytes(data)
        print(f"wrote {len(outputs)} files; {len(json.loads(outputs['manifest.json'])['notes'])} notes")
        return 0
    stale = [name for name, data in outputs.items() if not (VAULT / name).exists() or (VAULT / name).read_bytes() != data]
    if stale:
        print(f"vault derived files are stale: {stale}; run python tools/build_rapp1_vault.py --write", file=sys.stderr)
        return 1
    print(f"vault ok: {len(json.loads(outputs['manifest.json'])['notes'])} notes, pinned to {UPSTREAM_COMMIT[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
