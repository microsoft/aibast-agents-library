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

Nothing else in the export is touched. `--check` rebuilds into memory and fails on any
drift from the committed tree, so CI can ratchet the layout.

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
        for required in ("solution.xml", "customizations.xml", "[Content_Types].xml"):
            if required not in self.files:
                raise ValueError(f"{zip_path} has no {required}")
        bots = [name for name in self.files if re.fullmatch(r"bots/[^/]+/bot\.xml", name)]
        if len(bots) != 1:
            raise ValueError(f"{zip_path} must hold exactly one bot, found {len(bots)}")
        self.bot_xml_path = bots[0]
        self.bot_dir = self.bot_xml_path.rsplit("/", 1)[0]
        self.config_path = f"{self.bot_dir}/configuration.json"
        if self.config_path not in self.files:
            raise ValueError(f"{zip_path} has no {self.config_path}")

    def text(self, name: str) -> str:
        return self.files[name].decode("utf-8-sig")

    def components(self, kind: str) -> list[dict]:
        rows = []
        for name in sorted(self.files):
            match = re.fullmatch(r"botcomponents/([^/]+)/botcomponent\.xml", name)
            if not match or f".{kind}." not in match.group(1):
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

    def knowledge_files(self) -> list[str]:
        return sorted(
            Path(name).name
            for name in self.files
            if re.fullmatch(r"botcomponents/[^/]+/filedata/[^/]+", name)
        )


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
        "1. Import the unmanaged solution through Power Platform Solutions. When using the exploded "
        "source directly, package the contents of `solution/` as a ZIP with `solution.xml` and "
        "`customizations.xml` at its root. Do not include the gallery metadata or this README.",
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
        "This submission contains an editable **unmanaged** solution exported from Copilot Studio. "
        f"Source environment export recorded {row['exported_at'][:10]}.",
        "",
    ]
    return "\n".join(out)


def build_one(slug: str, spec: dict, config: dict, state_rows: dict, registry_rows: dict) -> dict[str, bytes]:
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
    for name, data in export.files.items():
        files[f"solution/{name}"] = data
    return files


def load_inputs():
    config = read_json(INPUT_PATH)
    state_rows = {row["slug"]: row for row in read_json(STATE_PATH)["solutions"]}
    registry_rows = {}
    for agent in read_json(REGISTRY_PATH)["agents"]:
        slug = (agent.get("_solution") or {}).get("package", {}).get("slug")
        if slug:
            registry_rows[slug] = agent
    return config, state_rows, registry_rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify submissions/ matches the build; write nothing")
    parser.add_argument("--only", action="append", default=[], help="build only this slug (repeatable)")
    args = parser.parse_args(argv)

    config, state_rows, registry_rows = load_inputs()
    wanted = config["submissions"]
    if args.only:
        missing = [slug for slug in args.only if slug not in wanted]
        if missing:
            parser.error(f"not in {INPUT_PATH.name}: {', '.join(missing)}")
        wanted = {slug: wanted[slug] for slug in args.only}

    drift = []
    for slug, spec in sorted(wanted.items()):
        files = build_one(slug, spec, config, state_rows, registry_rows)
        target = OUT_ROOT / slug
        if args.check:
            current = read_tree(target)
            if current != files:
                changed = sorted(set(current) ^ set(files) | {k for k in files if k in current and current[k] != files[k]})
                drift.append(f"{slug}: {len(changed)} file(s) differ, e.g. {changed[:3]}")
            else:
                print(f"ok    {slug} ({len(files)} files)")
        else:
            write_tree(target, files)
            print(f"built submissions/{slug} ({len(files)} files)")

    if args.check and not args.only:
        extra = sorted(p.name for p in OUT_ROOT.iterdir() if p.is_dir() and p.name not in config["submissions"]) if OUT_ROOT.exists() else []
        if extra:
            drift.append(f"unlisted submission folders: {extra}")

    if drift:
        print("DRIFT:\n  " + "\n  ".join(drift), file=sys.stderr)
        print("Run: python tools/build_gallery_submissions.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
