"""Markdown Medic — find what's broken in a docs tree before a reader does.

Four checks that catch the things people actually hit:

    links      relative links and image paths that point at nothing
    headings   skipped levels (h2 -> h4) and duplicate anchors
    toc        generate a table of contents with GitHub-style anchors
    stats      per-file size, heading depth, link and code-fence counts

No network by default: only relative links are resolved, because those are the
ones you broke. External URLs are counted but never fetched — a docs linter
that makes network calls is slow, flaky, and fails in CI for reasons that have
nothing to do with your docs.

WHY DUPLICATE ANCHORS MATTER

Two headings with the same text generate the same anchor, so every link to the
second one silently lands on the first. Nothing errors. The page just quietly
sends readers to the wrong section, and it survives every review because the
link "works".

WHY SKIPPED HEADING LEVELS MATTER

h2 -> h4 renders fine and reads fine. It breaks screen-reader navigation and
every tool that builds structure from headings, which is most of them.
"""

import json
import os
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # standalone — no brainstem required
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            if name:
                self.name = name
            if metadata:
                self.metadata = metadata

        def perform(self, **kwargs):
            return "Not implemented."

        def to_tool(self):
            return {"type": "function", "function": {
                "name": self.name,
                "description": self.metadata.get("description", ""),
                "parameters": self.metadata.get("parameters", {})}}


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@rapp/markdown-medic",
    "tier": "core",
    "trust": "community",
    "version": "1.0.0",
    "tags": ["docs", "markdown", "lint", "links", "local-first", "singleton"],
    "example_call": {
        "args": {"action": "links", "path": "./docs"},
        "note": "Find relative links and images that point at nothing.",
    },
}

LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
FENCE = re.compile(r"^```", re.M)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", "site"}


def _md_files(path):
    if os.path.isfile(path):
        return [path]
    out = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        out += [os.path.join(root, f) for f in files
                if f.lower().endswith((".md", ".markdown"))]
    return sorted(out)


def _anchor(text):
    """GitHub's rule: lowercase, strip anything not alnum/space/hyphen, spaces
    to hyphens. Reimplemented rather than guessed because a wrong anchor makes
    the whole TOC subtly useless."""
    t = re.sub(r"`([^`]*)`", r"\1", text)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.strip().lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"\s+", "-", t)


def _strip_code(text):
    """Links inside fenced code are examples, not links. Counting them produces
    false 'broken link' reports and teaches people to ignore the tool."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


class MarkdownMedicAgent(BasicAgent):
    def __init__(self):
        self.name = "MarkdownMedic"
        self.metadata = {
            "name": self.name,
            "description": (
                "Check a markdown file or docs folder for broken relative links "
                "and images, skipped heading levels, duplicate anchors; or "
                "generate a table of contents. Never makes network calls."),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string",
                               "enum": ["links", "headings", "toc", "stats"],
                               "description": "Which check to run."},
                    "path": {"type": "string",
                             "description": "A .md file or a folder of them."},
                },
                "required": ["action", "path"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        action, path = kwargs.get("action"), kwargs.get("path")
        if not path or not os.path.exists(path):
            return json.dumps({"status": "error",
                               "message": f"not found: {path}"}, indent=2)
        files = _md_files(path)
        if not files:
            return json.dumps({"status": "ok", "files": 0,
                               "note": "no .md files found"}, indent=2)
        base = path if os.path.isdir(path) else os.path.dirname(path) or "."

        try:
            if action == "links":
                broken, ext, ok = [], 0, 0
                for f in files:
                    body = _strip_code(open(f, encoding="utf-8", errors="ignore").read())
                    for bang, text, href in LINK.findall(body):
                        if href.startswith(("http://", "https://", "mailto:", "#")):
                            ext += 1
                            continue
                        target = os.path.normpath(
                            os.path.join(os.path.dirname(f), href.split("#")[0]))
                        if href.split("#")[0] and not os.path.exists(target):
                            broken.append({"file": os.path.relpath(f, base),
                                           "kind": "image" if bang else "link",
                                           "text": text[:40], "href": href})
                        else:
                            ok += 1
                return json.dumps({
                    "status": "ok", "files": len(files), "broken": len(broken),
                    "relative_ok": ok, "external_not_checked": ext,
                    "findings": broken[:100],
                    "note": "External URLs are counted, never fetched — a linter "
                            "that makes network calls fails in CI for reasons "
                            "unrelated to your docs.",
                }, indent=2)

            if action == "headings":
                issues = []
                for f in files:
                    body = _strip_code(open(f, encoding="utf-8", errors="ignore").read())
                    hs = HEADING.findall(body)
                    seen, prev = {}, 0
                    for hashes, text in hs:
                        lvl = len(hashes)
                        if prev and lvl > prev + 1:
                            issues.append({"file": os.path.relpath(f, base),
                                           "kind": "skipped-level",
                                           "detail": f"h{prev} -> h{lvl}",
                                           "heading": text[:50]})
                        a = _anchor(text)
                        if a in seen:
                            issues.append({"file": os.path.relpath(f, base),
                                           "kind": "duplicate-anchor",
                                           "detail": f"#{a}", "heading": text[:50]})
                        seen[a] = True
                        prev = lvl
                return json.dumps({
                    "status": "ok", "files": len(files), "issues": len(issues),
                    "findings": issues[:100],
                    "note": "Duplicate anchors silently send every link to the "
                            "second heading to the first one instead.",
                }, indent=2)

            if action == "toc":
                out = []
                for f in files:
                    body = _strip_code(open(f, encoding="utf-8", errors="ignore").read())
                    lines = []
                    for hashes, text in HEADING.findall(body):
                        lvl = len(hashes)
                        if lvl == 1:
                            continue
                        clean = re.sub(r"`([^`]*)`", r"\1", text)
                        lines.append("  " * (lvl - 2) + f"- [{clean}](#{_anchor(text)})")
                    if lines:
                        out.append({"file": os.path.relpath(f, base),
                                    "toc": "\n".join(lines)})
                return json.dumps({"status": "ok", "files": len(out),
                                   "tables_of_contents": out[:20]}, indent=2)

            if action == "stats":
                rows = []
                for f in files:
                    raw = open(f, encoding="utf-8", errors="ignore").read()
                    body = _strip_code(raw)
                    hs = HEADING.findall(body)
                    rows.append({
                        "file": os.path.relpath(f, base),
                        "bytes": len(raw.encode()), "lines": raw.count("\n") + 1,
                        "headings": len(hs),
                        "max_depth": max([len(h) for h, _ in hs], default=0),
                        "links": len(LINK.findall(body)),
                        "code_fences": len(FENCE.findall(raw)) // 2,
                    })
                rows.sort(key=lambda r: -r["bytes"])
                return json.dumps({"status": "ok", "files": len(rows),
                                   "total_bytes": sum(r["bytes"] for r in rows),
                                   "documents": rows[:60]}, indent=2)

            return json.dumps({"status": "error",
                               "message": f"unknown action {action!r}",
                               "valid": ["links", "headings", "toc", "stats"]}, indent=2)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--tool":
        print(json.dumps(MarkdownMedicAgent().to_tool(), indent=2))
    else:
        raw = a[0] if a else (sys.stdin.read().strip() or "{}")
        print(MarkdownMedicAgent().perform(**json.loads(raw)))
