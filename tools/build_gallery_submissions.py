#!/usr/bin/env python3
"""Lay out AIBAST industry solutions as microsoft/copilot-studio-gallery submissions.

One hand-authored input (tools/gallery_submissions.json) -> one idempotent build:

    submissions/<slug>/
        metadata.json      gallery metadata (name, description, tags, category, author)
        README.md          visitor overview written from the solution catalog
        solution/          the exported, unmanaged Copilot Studio solution, unpacked

This follows the gallery's own documented process: export the solution unmanaged,
unpack it, add the two sidecar files. The payload is the native export already kept
under solutions/<slug>/exports/. The build applies a small, documented normalization
so the sample reads like a product rather than an internal build:

  * the agent display name and the solution display name become the advertised
    solution name (the export carried internal build names);
  * the solution description becomes the executive summary;
  * when the export has no greeting, a greeting listing the sample prompts is added;
  * the model series is set to "Auto" so the sample imports into any tenant.

Nothing else in the export is touched. The build also writes the deterministic download
`solutions/<slug>/exports/<slug>-gallery-solution.zip` (the gallery's "Download ZIP",
served from the raw base because Pages never carries archives) and a thin page shell
`submissions/<slug>/index.html` that renders `api/v1/gallery/<slug>.json`. `--check`
rebuilds into memory and fails on any drift from the committed tree, so CI can ratchet
the layout. tools/build_library_api.py imports `gallery_docs` from here for the API.

Usage:
    python tools/build_gallery_submissions.py            # build every listed slug
    python tools/build_gallery_submissions.py --check    # verify the tree matches
    python tools/build_gallery_submissions.py --only first-time-fix
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "tools" / "gallery_submissions.json"
STATE_PATH = ROOT / "state" / "copilot_studio_solution_exports.json"
REGISTRY_PATH = ROOT / "registry.json"
OUT_ROOT = ROOT / "submissions"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DESCRIPTION_MAX = 320
TAG_MAX = 40

GALLERY_CATEGORIES = {
    "Customer service",
    "Sales & marketing",
    "IT & security",
    "Operations",
    "Project & communications management",
    "HR",
    "Finance",
    "Legal & compliance",
    "Productivity & knowledge",
    "Agent Building",
    "Governance",
    "Other",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def slugify_tag(value: str) -> str:
    tag = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return tag[:TAG_MAX].rstrip("-")


def short_description(solution: dict) -> str:
    for key in ("card_pitch", "executive_summary"):
        text = (solution.get(key) or "").strip()
        if text and len(text) <= DESCRIPTION_MAX:
            return text
    text = (solution.get("executive_summary") or "").strip()
    if len(text) > DESCRIPTION_MAX:
        cut = text[: DESCRIPTION_MAX - 1]
        cut = cut[: cut.rfind(" ")]
        text = cut.rstrip(",;:") + "."
    return text


class Export:
    """The unpacked native export plus what the build learned about it."""

    def __init__(self, zip_path: Path) -> None:
        self.files: dict[str, bytes] = {}
        with zipfile.ZipFile(zip_path) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if info.is_dir():
                    continue
                name = info.filename
                if name.startswith("/") or ".." in Path(name).parts:
                    raise ValueError(f"unsafe member in {zip_path}: {name}")
                self.files[name] = archive.read(info)
        self._finish(str(zip_path))

    @classmethod
    def from_directory(cls, directory: Path) -> "Export":
        export = cls.__new__(cls)
        export.files = {
            p.relative_to(directory).as_posix(): p.read_bytes()
            for p in sorted(directory.rglob("*")) if p.is_file()
        }
        export._finish(str(directory))
        return export

    def _finish(self, origin: str) -> None:
        # [Content_Types].xml is a ZIP packaging part: required in an export ZIP, optional in an
        # exploded folder (the Copilot Studio Gallery accepts folders without it).
        packaging = ("[Content_Types].xml",) if origin.endswith(".zip") else ()
        for required in ("solution.xml", "customizations.xml", *packaging):
            if required not in self.files:
                raise ValueError(f"{origin} has no {required}")
        # A Copilot Studio solution may hold one agent (ours), several, or none (workflow-only
        # solutions exist in the Copilot Studio Gallery). The build reads whatever is there.
        self.bot_xml_paths = sorted(name for name in self.files if re.fullmatch(r"bots/[^/]+/bot\.xml", name))
        self.bot_xml_path = self.bot_xml_paths[0] if self.bot_xml_paths else None
        self.bot_dir = self.bot_xml_path.rsplit("/", 1)[0] if self.bot_xml_path else None
        self.config_path = f"{self.bot_dir}/configuration.json" if self.bot_dir else None
        if self.config_path and self.config_path not in self.files:
            raise ValueError(f"{origin} has no {self.config_path}")

    def require_single_bot(self, origin: str) -> None:
        """Our own exports hold exactly one agent; the gallery's may not."""
        if len(self.bot_xml_paths) != 1:
            raise ValueError(f"{origin} must hold exactly one bot, found {len(self.bot_xml_paths)}")

    def text(self, name: str) -> str:
        return self.files[name].decode("utf-8-sig")

    def components(self, kind: str, bot_schema: str | None = None) -> list[dict]:
        """Components of one kind; with `bot_schema`, only those that belong to that agent
        (component folders are named `<agent schema>.<kind>.<name>`)."""
        rows = []
        for name in sorted(self.files):
            match = re.fullmatch(r"botcomponents/([^/]+)/botcomponent\.xml", name)
            if not match or f".{kind}." not in match.group(1):
                continue
            if bot_schema and not match.group(1).startswith(f"{bot_schema}.{kind}."):
                continue
            xml = self.text(name)
            display = re.search(r"<name>(.*?)</name>", xml, re.S)
            description = re.search(r"<description>(.*?)</description>", xml, re.S)
            rows.append(
                {
                    "schema": match.group(1),
                    "name": unescape_xml(display.group(1)) if display else match.group(1),
                    "description": unescape_xml(description.group(1)).strip() if description else "",
                }
            )
        return rows

    def knowledge_files(self, bot_schema: str | None = None) -> list[str]:
        prefix = re.escape(bot_schema) + r"\." if bot_schema else ""
        pattern = r"botcomponents/" + prefix + r"[^/]+/filedata/[^/]+"
        return sorted(Path(name).name for name in self.files if re.fullmatch(pattern, name))


def unescape_xml(value: str) -> str:
    return (
        value.replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )


def normalize_export(export: Export, display_name: str, description: str, prompts: list[dict]) -> dict:
    """Apply the documented normalization in place; return what changed."""
    changes = {}

    export.require_single_bot("export")
    bot_xml = export.text(export.bot_xml_path)
    new_bot_xml, count = re.subn(
        r"<name>.*?</name>", f"<name>{escape(display_name)}</name>", bot_xml, count=1, flags=re.S
    )
    if count != 1:
        raise ValueError(f"{export.bot_xml_path} has no <name>")
    if new_bot_xml != bot_xml:
        changes["agent_name"] = display_name
        export.files[export.bot_xml_path] = new_bot_xml.encode("utf-8")

    solution_xml = export.text("solution.xml")
    new_solution_xml = re.sub(
        r"(<SolutionManifest>\s*<UniqueName>.*?</UniqueName>\s*<LocalizedNames>\s*<LocalizedName description=\")[^\"]*(\")",
        lambda m: m.group(1) + escape(display_name, {'"': "&quot;"}) + m.group(2),
        solution_xml,
        count=1,
        flags=re.S,
    )
    description_xml = (
        "<Descriptions>\n      <Description description=\""
        + escape(description, {'"': "&quot;"})
        + '" languagecode="1033" />\n    </Descriptions>'
    )
    new_solution_xml = re.sub(
        r"(<LocalizedNames>.*?</LocalizedNames>\s*)<Descriptions\s*/>",
        lambda m: m.group(1) + description_xml,
        new_solution_xml,
        count=1,
        flags=re.S,
    )
    if new_solution_xml != solution_xml:
        changes["solution_display_name"] = display_name
        export.files["solution.xml"] = new_solution_xml.encode("utf-8")

    config = json.loads(export.text(export.config_path))
    settings = config.get("agentSettings", {})
    model = settings.get("model")
    if isinstance(model, dict) and model.get("series") != "Auto":
        changes["model_series"] = {"from": model.get("series"), "to": "Auto"}
        model["series"] = "Auto"
    if not (settings.get("greetingText") or "").strip() and prompts:
        settings["greetingText"] = greeting_text(display_name, prompts)
        changes["greeting"] = "added from sample prompts"
    export.files[export.config_path] = (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return changes


def greeting_text(display_name: str, prompts: list[dict]) -> str:
    lines = [
        f"Hi, I'm the {display_name}. Everything here runs on a fixed synthetic dataset, so you can try it without connecting anything.",
        "",
        "Pick one of these to start:",
        "",
    ]
    for prompt in prompts:
        lines.append(f'- **{prompt["label"]}** - "{prompt["prompt"]}"')
    lines += ["", "Ask one question at a time and I'll tell you what the records show and where the limits are."]
    return "\n".join(lines) + "\n"


def write_tree(target: Path, files: dict[str, bytes]) -> None:
    if target.exists():
        for path in sorted(target.rglob("*"), reverse=True):
            if path.is_symlink() or path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    for name, data in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def read_tree(target: Path) -> dict[str, bytes]:
    if not target.exists():
        return {}
    return {
        path.relative_to(target).as_posix(): path.read_bytes()
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }


def render_readme(slug: str, solution: dict, export: Export, row: dict, metadata: dict) -> str:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.check_gallery_content import connector_label, declared_connections_xml

    name = metadata["name"]
    skills = export.components("skill")
    knowledge = export.knowledge_files()
    tools = export.components("tool")
    prompts = solution.get("sample_prompts") or []
    personas = solution.get("personas") or []
    capabilities = solution.get("capabilities") or []
    outcomes = solution.get("outcomes") or []
    industries = solution.get("industries") or []
    library_url = f"https://microsoft.github.io/aibast-agents-library/solutions/{slug}/quest.html"
    unique_name = re.search(r"<UniqueName>(.*?)</UniqueName>", export.text("solution.xml")).group(1)

    out = [f"# {name}", ""]
    out.append((solution.get("executive_summary") or metadata["description"]).strip())
    out.append("")
    out.append(
        "This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. "
        "It needs no connections, so you can import it and start chatting in the test pane. "
        f"It comes from the [AIBAST Agents Library]({library_url}), Microsoft's catalog of industry agent templates."
    )
    out.append("")
    if personas or industries:
        out += ["## Who it is for", ""]
        if personas:
            out.append("- **Personas:** " + ", ".join(personas))
        if industries:
            out.append("- **Industries:** " + ", ".join(industries))
        out.append("")
    if prompts:
        out += ["## What you can try", "", "Send one prompt at a time in a new chat.", ""]
        out += ["| Prompt | What happens |", "| --- | --- |"]
        for prompt in prompts:
            label = prompt.get("label", "").replace("|", "/")
            text = prompt.get("prompt", "").replace("|", "/")
            out.append(f"| `{text}` | {label} |")
        out.append("")
    if capabilities:
        out += ["## What the agent does", ""]
        out += [f"- {item}" for item in capabilities]
        out.append("")
    out += ["## What the solution contains", ""]
    out.append(f"- One CLI-authored Copilot Studio agent (`{unique_name}`) with instructions and a greeting that lists the sample prompts.")
    if skills:
        out.append(f"- {len(skills)} agent skills, one per operation:")
        for skill in skills:
            out.append(f"  - `{skill['name']}` - {skill['description']}")
    if knowledge:
        out.append(f"- {len(knowledge)} knowledge files holding the synthetic records and operating rules:")
        out += [f"  - `{item}`" for item in knowledge]
    if tools:
        out.append(f"- {len(tools)} tools:")
        out += [f"  - `{tool['name']}` - {tool['description']}" for tool in tools]
    else:
        out.append("- No connectors, flows, or connection references. Nothing to bind after import.")
    out.append("")
    out += [
        "## Prerequisites and import",
        "",
        "Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. "
        "You need permission to import an unmanaged solution.",
        "",
    ]
    connections = declared_connections_xml(export.text("customizations.xml"))
    if connections:
        out += ["This package declares these connections. Importing asks you to pick or create a connection for each; "
                "nothing is read until you do:", ""]
        out += [f"- {connector_label(c)}" for c in connections]
        out.append("")
    out += [
        "1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package "
        "the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. "
        "Do not include the gallery metadata or this README.",
        f"2. Open **{name}** in Copilot Studio and start a new test chat. The greeting lists the prompts above.",
        "3. Publish and share the agent when you are ready for others to use it.",
        "",
        "Running examples consumes Copilot Credits.",
        "",
    ]
    if outcomes:
        out += ["## Outcomes this pattern targets", ""]
        out += [f"- {item}" for item in outcomes]
        out.append("")
    out += [
        "## Boundaries",
        "",
        "- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.",
        "- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.",
        "- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.",
        "",
        "### Before you rely on it",
        "",
        "This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not "
        "professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review "
        "every output before it informs a real decision, record, message or action.",
        "",
        "This submission contains an editable **unmanaged** solution exported from Copilot Studio. "
        f"Source environment export recorded {row['exported_at'][:10]}.",
        "",
    ]
    return "\n".join(out)


FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def deterministic_zip(files: dict[str, bytes]) -> bytes:
    """Zip the exploded solution with fixed timestamps so the bytes depend only on content."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE_TIME)
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[name])
    return buffer.getvalue()


def gallery_zip_path(slug: str) -> str:
    return f"solutions/{slug}/exports/{slug}-gallery-solution.zip"


PAGE_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - AIBAST Agents Library</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="../_shared/gallery.css">
</head>
<body data-slug="{slug}" data-api="../../api/v1/gallery/{slug}.json">
<header class="g-top">
  <a class="g-brand" href="../../index.html">AIBAST Agents Library</a>
  <nav><a href="../index.html">Gallery</a><a href="../../solutions/{slug}/quest.html">Guided quest</a></nav>
</header>
<main id="solution" class="g-main"><p class="g-loading">Loading {title}&hellip;</p></main>
<noscript><p class="g-main">This page renders <a href="../../api/v1/gallery/{slug}.json">api/v1/gallery/{slug}.json</a>; the same facts are in <a href="README.md">README.md</a>.</p></noscript>
<script src="../_shared/gallery.js"></script>
</body>
</html>
"""


def page_shell(slug: str, metadata: dict) -> str:
    """The page shell carries the site's design tokens and Clarity tag the way every other
    published page does, so scripts/apply_design_tokens.py and apply_clarity_tag.py find
    nothing to change and --check stays green."""
    html = PAGE_SHELL.format(
        slug=slug,
        title=html_escape(metadata["name"]),
        description=html_escape(metadata["description"]),
    )
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import clarity_tag, design_tokens
    html = design_tokens.stamp(html, design_tokens.render_tokens())
    return clarity_tag.stamp(html, clarity_tag.current_tag(ROOT))


def html_escape(text: str) -> str:
    return escape(text, {'"': "&quot;"})


_LINK_BASE: str | None = None


def _safe_href(href: str) -> str | None:
    """A README is content, sometimes another library's. Web, mail and in-page links pass; a relative
    link resolves against the folder the README came from when one is known; any other scheme is
    dropped and the link text stays as text."""
    if re.match(r"^(https?://|mailto:|#)", href, re.I):
        return href
    if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I) or href.startswith("//"):
        return None
    return (_LINK_BASE + href.lstrip("./")) if _LINK_BASE else href


def _inline(text: str) -> str:
    """Inline markdown subset used by the generated README: code, bold, links."""
    out = []
    pos = 0
    pattern = re.compile(r"`([^`]+)`|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)")
    for match in pattern.finditer(text):
        out.append(html_escape(text[pos:match.start()]))
        if match.group(1) is not None:
            out.append(f"<code>{html_escape(match.group(1))}</code>")
        elif match.group(2) is not None:
            out.append(f"<strong>{_inline(match.group(2))}</strong>")
        else:
            href = _safe_href(match.group(4))
            label = _inline(match.group(3))
            out.append(f'<a href="{html_escape(href)}">{label}</a>' if href else label)
        pos = match.end()
    out.append(html_escape(text[pos:]))
    return "".join(out)


def markdown_to_html(markdown: str, link_base: str | None = None) -> str:
    """Render the README subset this tool writes, plus what other libraries' READMEs commonly use:
    headings, paragraphs, nested bullets, numbered lists, pipe tables, block quotes, fenced code,
    inline code/bold/links. Everything is escaped; raw HTML in a README shows as text.
    Deterministic, dependency-free. `link_base` resolves a README's relative links."""
    global _LINK_BASE
    previous, _LINK_BASE = _LINK_BASE, link_base
    try:
        return _markdown_to_html(markdown)
    finally:
        _LINK_BASE = previous


def _markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            html.append(f"<h{level}>{_inline(heading.group(2).strip())}</h{level}>")
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            html.append("<pre><code>" + html_escape("\n".join(code)) + "</code></pre>")
            continue
        if line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            html.append("<blockquote>" + _markdown_to_html("\n".join(quote)) + "</blockquote>")
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
            html.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>")
            for r in body:
                html.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            html.append("</tbody></table>")
            continue
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            html.append(_render_list(lines, i))
            while i < len(lines) and (re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) or (lines[i].startswith("   ") and lines[i].strip())):
                i += 1
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||>|```|\s*[-*]\s|\s*\d+\.\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        html.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(html)


def _render_list(lines: list[str], start: int) -> str:
    items: list[tuple[int, str, bool]] = []
    i = start
    while i < len(lines):
        match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
        if match:
            indent = len(match.group(1))
            items.append((indent, match.group(3), match.group(2) != "-" and match.group(2) != "*"))
            i += 1
        elif lines[i].startswith("   ") and lines[i].strip() and items:
            indent, text, ordered = items[-1]
            items[-1] = (indent, text + " " + lines[i].strip(), ordered)
            i += 1
        else:
            break
    out: list[str] = []
    stack: list[tuple[int, str]] = []
    for indent, text, ordered in items:
        tag = "ol" if ordered else "ul"
        while stack and stack[-1][0] > indent:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or stack[-1][0] < indent:
            out.append(f"<{tag}><li>{_inline(text)}")
            stack.append((indent, tag))
        else:
            out.append(f"</li><li>{_inline(text)}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def discover_submissions(root: Path) -> list[str]:
    """Every submissions/<slug>/ that has metadata.json and either solution/ or app/: the Copilot
    Studio Gallery's folder contract. A folder is the unit; no list has to be kept in step."""
    base = root / "submissions"
    if not base.is_dir():
        return []
    return sorted(
        p.name for p in base.iterdir()
        if p.is_dir() and not p.name.startswith(("_", ".")) and (p / "metadata.json").is_file()
        and ((p / "solution").is_dir() or (p / "app").is_dir())
    )


def metadata_authors(metadata: dict) -> list[dict]:
    """Both gallery forms: `author`/`authorUrl` (one) or `authors: [{name, url}]` (several)."""
    if metadata.get("authors"):
        return [{"name": a.get("name"), "url": a.get("url")} for a in metadata["authors"]]
    if metadata.get("author"):
        return [{"name": metadata["author"], "url": metadata.get("authorUrl")}]
    return []


def _agent_doc(export: "Export", bot_xml_path: str, slug: str) -> dict:
    bot_dir = bot_xml_path.rsplit("/", 1)[0]
    bot_xml = export.text(bot_xml_path)
    config_path = f"{bot_dir}/configuration.json"
    config_json = json.loads(export.text(config_path)) if config_path in export.files else {}
    name = re.search(r"<name>(.*?)</name>", bot_xml, re.S)
    template = re.search(r"<template>(.*?)</template>", bot_xml)
    schema = bot_dir.rsplit("/", 1)[-1]
    scoped = len(export.bot_xml_paths) > 1
    skills = export.components("skill", schema if scoped else None)
    tools = export.components("tool", schema if scoped else None)
    knowledge = export.knowledge_files(schema if scoped else None)
    return {
        "name": unescape_xml(name.group(1)) if name else schema,
        "schema_name": bot_dir.rsplit("/", 1)[-1],
        "template": template.group(1) if template else None,
        "model": config_json.get("agentSettings", {}).get("model", {}).get("series"),
        "greeting": config_json.get("agentSettings", {}).get("greetingText", ""),
        "skills": skills,
        "tools": tools,
        "knowledge": knowledge,
    }


def submission_doc(folder: Path, slug: str, spec: dict, raw_base: str, root: Path) -> dict:
    """The API document for one folder in the Copilot Studio Gallery shape. `root` is the tree the
    folder lives in (ours, or another library's checkout); the folder is read as it is."""
    import hashlib
    metadata = read_json(folder / "metadata.json")
    readme_path = folder / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    solution_dir = folder / "solution"
    kind = "managed-app" if metadata.get("submissionType") == "managed-app" or not solution_dir.is_dir() else "solution"
    package_dir = solution_dir if kind == "solution" else folder / "app"
    files = sorted(p.relative_to(package_dir).as_posix() for p in package_dir.rglob("*") if p.is_file())
    agents: list[dict] = []
    version = unique_name = None
    if kind == "solution":
        export = Export.from_directory(solution_dir)
        solution_xml = export.text("solution.xml")
        m = re.search(r"<Version>(.*?)</Version>", solution_xml)
        version = m.group(1) if m else None
        m = re.search(r"<UniqueName>(.*?)</UniqueName>", solution_xml)
        unique_name = m.group(1) if m else None
        agents = [_agent_doc(export, path, slug) for path in export.bot_xml_paths]
    skills = [s for a in agents for s in a["skills"]]
    zip_rel = gallery_zip_path(slug)
    zip_path = root / zip_rel
    zip_bytes = zip_path.read_bytes() if zip_path.exists() else b""
    authors = metadata_authors(metadata)
    doc = {
        "schema": "aibast-gallery-solution/1.0",
        "slug": slug,
        "kind": kind,
        "name": metadata["name"],
        "description": metadata["description"],
        "category": spec.get("category") or metadata.get("category"),
        "tags": metadata.get("tags", []),
        "author": authors[0] if authors else {"name": None, "url": None},
        "authors": authors,
        "featured": bool(spec.get("featured", metadata.get("featured", False))),
        "created": metadata.get("createdAt"),
        "updated": metadata.get("updatedAt"),
        "version": version,
        "unique_name": unique_name,
        "try": {
            "label": "Try it without deploying",
            "page": f"solutions/_shared/m365-copilot-demo.html?scenario={slug}-{skills[0]['name']}" if skills and (root / "solutions" / slug).is_dir() else None,
            "scenarios": [f"solutions/_shared/m365-copilot-demo.html?scenario={slug}-{s['name']}" for s in skills] if (root / "solutions" / slug).is_dir() else [],
        },
        "agents": agents,
        "counts": {"agents": len(agents), "skills": len(skills),
                   "tools": sum(len(a["tools"]) for a in agents),
                   "knowledge": sum(len(a["knowledge"]) for a in agents), "files": len(files)},
        "files": files,
        "download": {
            "path": zip_rel if zip_bytes else None,
            "url": raw_base + zip_rel if zip_bytes else None,
            "sha256": hashlib.sha256(zip_bytes).hexdigest() if zip_bytes else None,
            "bytes": len(zip_bytes) or None,
            "note": ("Unmanaged Copilot Studio solution. Import through Power Platform Solutions; review the source before importing."
                     if kind == "solution" else "Managed app (Copilot Managed Runtime). Build and deploy from the app/ folder."),
        },
        "source": {"folder": f"submissions/{slug}/", "readme": f"submissions/{slug}/README.md", "page": f"submissions/{slug}/"},
        "readme_markdown": readme,
        "readme_html": markdown_to_html(readme),
    }
    return doc


def federated_docs(root: Path, federation_dir: Path | None, taken: set[str]) -> dict[str, dict]:
    """Documents for the solutions of every other library fetched into `federation_dir`
    (tools/federate_gallery.py). Their folders are read unchanged. When a slug is already taken
    (two libraries each have their own solution for the same use case) theirs is listed as another
    version: keyed `<slug>-<variant_suffix>`, with `variant_of` naming the one that holds the address."""
    docs: dict[str, dict] = {}
    config_path = root / "tools" / "gallery_federation.json"
    if not federation_dir or not config_path.exists():
        return docs
    for source in read_json(config_path)["sources"]:
        tree = federation_dir / source["key"]
        record_path = tree / ".federation.json"
        if not source.get("enabled") or not record_path.exists():
            continue
        record = read_json(record_path)
        for slug in discover_submissions(tree):
            key = slug
            if slug in taken or slug in docs:
                key = f"{slug}-{source.get('variant_suffix') or source['key']}"
                if key in taken or key in docs:
                    continue
            try:
                doc = submission_doc(tree / "submissions" / slug, slug, {}, source["raw_base"], tree)
            except (ValueError, KeyError, json.JSONDecodeError) as error:
                print(f"federation: skipped {source['key']}/{slug} ({error})", file=sys.stderr)
                continue
            published = record.get("downloads", {}).get(slug)
            if published:
                doc["download"].update({"url": published, "path": None, "published_by": source["name"]})
            doc["origin"] = {"key": source["key"], "name": source["name"], "home": source.get("home"),
                             "url": source["page_base"] + slug + "/", "repository": source["repository"],
                             "commit": record["commit"], "license": source.get("license"),
                             "folder": source["tree_base"] + f"submissions/{slug}/", "tree": str(tree)}
            # Tags key pages on this site; other libraries mix case ("MCP" and "mcp"), which collides
            # on disk. Their metadata file is untouched; only this site's key is normalized.
            doc["tags"] = list(dict.fromkeys(t for t in (slugify_tag(str(x)) for x in doc["tags"]) if t))
            doc["readme_html"] = markdown_to_html(doc["readme_markdown"], source["raw_base"] + f"submissions/{slug}/")
            doc["source"] = {"folder": doc["origin"]["folder"], "readme": source["raw_base"] + f"submissions/{slug}/README.md", "page": doc["origin"]["url"]}
            if key != slug:
                doc["variant_of"] = slug
                doc["slug"] = key
            docs[key] = doc
    return docs


def gallery_docs(root: Path, raw_base: str) -> tuple[dict[str, dict], dict]:
    """One API document per submission plus an index, read from the submissions/ tree.
    Folders are discovered (the gallery contract); tools/gallery_submissions.json only adds
    AIBAST overrides (featured, category). tools/build_library_api.py calls this so the gallery
    rides the library's static API."""
    config_path = root / "tools" / "gallery_submissions.json"
    config = read_json(config_path) if config_path.exists() else {"submissions": {}}
    docs: dict[str, dict] = {}
    cards = []
    for slug in discover_submissions(root):
        doc = submission_doc(root / "submissions" / slug, slug, config.get("submissions", {}).get(slug, {}), raw_base, root)
        docs[slug] = doc
        cards.append({"slug": slug, "name": doc["name"], "description": doc["description"], "category": doc["category"],
                      "tags": doc["tags"], "counts": doc["counts"], "updated": doc["updated"],
                      "doc": f"api/v1/gallery/{slug}.json", "page": doc["source"]["page"], "try": doc["try"]["page"]})
    index = {"schema": "aibast-gallery-index/1.0", "count": len(cards),
             "note": "Industry solutions in the Copilot Studio Gallery shape: metadata, README and the exploded unmanaged solution per folder.",
             "solutions": cards}
    return docs, index


ACADEMY_PATH = ROOT / "academy.json"
DEMO_CASES_DIR = ROOT / "tests" / "demo_cases"
LIBRARY_SIDECAR_SCHEMA = "aibast-library-solution/1.0"


ATTESTATION_PATH = ROOT / "state" / "gallery_import_attestation.json"


def import_attestation(slug: str) -> dict | None:
    """The gallery's fresh-environment import attestation for this slug, if tools/attest_gallery_imports.py
    recorded one: when, into which environment (name only), and the ZIP hash it imported."""
    if not ATTESTATION_PATH.exists():
        return None
    rec = read_json(ATTESTATION_PATH).get("imports", {}).get(slug)
    if not rec or not rec.get("imported"):
        return None
    return {"imported": True, "fresh_environment": rec.get("environment_name") or "fresh sandbox",
            "on": (rec.get("checked_at") or "")[:10], "zip_sha256": rec.get("zip_sha256"),
            "dependency_check_skipped": bool(rec.get("dependency_check_skipped"))}


def library_sidecar(slug: str, solution: dict, row: dict, course: dict | None, cases: dict | None) -> dict:
    """library.json: the AIBAST facts beside the gallery metadata. The gallery checker ignores the
    file (verified 2026-11-09); the site generator reads it. Availability of the one-pager and the
    demo video is recorded, never the files themselves (they live in the AIBAST SharePoint library)."""
    prompts = solution.get("sample_prompts") or []
    arch = solution.get("architecture") or {}
    passed = sum(1 for c in (cases or {}).get("cases", []) if (c.get("status") or "passed") != "failed") if cases else None
    return {
        "schema": LIBRARY_SIDECAR_SCHEMA,
        "slug": slug,
        "headline": (solution.get("sales_headline") or "").strip() or None,
        "industries": solution.get("industries") or [],
        "personas": solution.get("personas") or [],
        "products": solution.get("featured_tools") or [],
        "requirements": solution.get("agent_requirements") or [],
        "journey_stage": solution.get("journey_stage"),
        "capabilities": solution.get("capabilities") or [],
        "outcomes": solution.get("outcomes") or [],
        "why_try": (solution.get("why_try") or "").strip() or None,
        "sample_prompts": [{"label": p.get("label"), "prompt": p.get("prompt"), "demo": p.get("demo_url")} for p in prompts],
        "business_flow": arch.get("business_flow") or [],
        "assets": {"demo_video": bool(solution.get("has_demo_video")), "onepager": bool(solution.get("has_onepager"))},
        "learn": {
            "quest": (course or {}).get("quest_url") or f"solutions/{slug}/quest.html",
            "field_guide": (course or {}).get("field_guide_url") or f"solutions/{slug}/field-guide.html",
            "manual_tutorial": (course or {}).get("manual_url") or f"solutions/{slug}/manual-tutorial.html",
            "evidence": (course or {}).get("evidence_url") or f"solutions/{slug}/evidence-report.html",
            "academy_path": (course or {}).get("primary_path"),
            "manual_steps": (course or {}).get("manual_steps"),
        },
        "install": {
            "brainstem": f"curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash -s -- --agent {slug}",
            "ai_prompt": f"Get https://microsoft.github.io/aibast-agents-library/solutions/{slug}/SKILL.md and do it",
        },
        "tests": {"cases": len((cases or {}).get("cases", [])) if cases else None, "passed": passed},
        "attestation": import_attestation(slug),
        "source": {"agent": solution.get("package", {}).get("slug") and f"solutions/{slug}/", "export_environment": row.get("source_environment")},
    }


def build_one(slug: str, spec: dict, config: dict, state_rows: dict, registry_rows: dict, courses: dict | None = None) -> dict[str, bytes]:
    if not SLUG_RE.match(slug):
        raise ValueError(f"slug {slug!r} is not gallery-safe")
    if slug not in state_rows:
        raise ValueError(f"no Copilot Studio export recorded for {slug}")
    if slug not in registry_rows:
        raise ValueError(f"no registry solution row for {slug}")
    category = spec.get("category")
    if category not in GALLERY_CATEGORIES:
        raise ValueError(f"{slug}: category {category!r} is not a gallery category")

    row = state_rows[slug]
    agent = registry_rows[slug]
    solution = agent["_solution"]
    export = Export(ROOT / row["zip"])

    display_name = solution["advertised_name"].strip()
    description = short_description(solution)
    prompts = solution.get("sample_prompts") or []
    normalize_export(export, display_name, description, prompts)

    tags = []
    for tag in list(agent.get("tags") or []) + list(config.get("common_tags") or []) + list(spec.get("tags") or []):
        tag = slugify_tag(tag)
        if tag and tag not in tags:
            tags.append(tag)

    metadata = {
        "name": display_name,
        "description": description,
        "tags": tags,
        "category": category,
        "author": config["author"]["name"],
        "authorUrl": config["author"]["url"],
        "createdAt": row["exported_at"][:10],
        "updatedAt": spec.get("updatedAt") or row["exported_at"][:10],
        "featured": bool(spec.get("featured", False)),
    }

    files: dict[str, bytes] = {"metadata.json": dump_json(metadata).encode("utf-8")}
    files["README.md"] = render_readme(slug, solution, export, row, metadata).encode("utf-8")
    course = (courses or {}).get(slug)
    cases_path = DEMO_CASES_DIR / f"{slug}.json"
    cases = read_json(cases_path) if cases_path.exists() else None
    files["library.json"] = dump_json(library_sidecar(slug, solution, row, course, cases)).encode("utf-8")
    for name, data in export.files.items():
        files[f"solution/{name}"] = data
    return files, deterministic_zip(export.files)


def load_inputs():
    config = read_json(INPUT_PATH)
    state_rows = {row["slug"]: row for row in read_json(STATE_PATH)["solutions"]}
    registry_rows = {}
    for agent in read_json(REGISTRY_PATH)["agents"]:
        slug = (agent.get("_solution") or {}).get("package", {}).get("slug")
        if slug:
            registry_rows[slug] = agent
    courses = {}
    if ACADEMY_PATH.exists():
        courses = {c["slug"]: c for c in read_json(ACADEMY_PATH).get("courses", [])}
    return config, state_rows, registry_rows, courses


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify submissions/ matches the build; write nothing")
    parser.add_argument("--only", action="append", default=[], help="build only this slug (repeatable)")
    args = parser.parse_args(argv)

    config, state_rows, registry_rows, courses = load_inputs()
    wanted = config["submissions"]
    if args.only:
        missing = [slug for slug in args.only if slug not in wanted]
        if missing:
            parser.error(f"not in {INPUT_PATH.name}: {', '.join(missing)}")
        wanted = {slug: wanted[slug] for slug in args.only}

    drift = []
    for slug, spec in sorted(wanted.items()):
        files, archive = build_one(slug, spec, config, state_rows, registry_rows, courses)
        target = OUT_ROOT / slug
        zip_target = ROOT / gallery_zip_path(slug)
        if args.check:
            current = read_tree(target)
            if not zip_target.exists() or zip_target.read_bytes() != archive:
                drift.append(f"{slug}: {gallery_zip_path(slug)} differs or is missing")
            if current != files:
                changed = sorted(set(current) ^ set(files) | {k for k in files if k in current and current[k] != files[k]})
                drift.append(f"{slug}: {len(changed)} file(s) differ, e.g. {changed[:3]}")
            else:
                print(f"ok    {slug} ({len(files)} files)")
        else:
            write_tree(target, files)
            zip_target.parent.mkdir(parents=True, exist_ok=True)
            if not zip_target.exists() or zip_target.read_bytes() != archive:
                zip_target.write_bytes(archive)
            print(f"built submissions/{slug} ({len(files)} files) + {gallery_zip_path(slug)}")

    if args.check and not args.only:
        extra = sorted(p.name for p in OUT_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_") and p.name not in config["submissions"]) if OUT_ROOT.exists() else []
        if extra:
            drift.append(f"unlisted submission folders: {extra}")

    if drift:
        print("DRIFT:\n  " + "\n  ".join(drift), file=sys.stderr)
        print("Run: python tools/build_gallery_submissions.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
