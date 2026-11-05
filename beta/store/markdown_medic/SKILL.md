---
name: "markdown-medic"
description: "Check a markdown file or docs folder for broken relative links and images, skipped heading levels, duplicate anchors; or generate a table of contents. Never makes network calls."
---

Markdown Medic — find what's broken in a docs tree before a reader does.

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

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "links",
        "headings",
        "toc",
        "stats"
      ],
      "description": "Which check to run."
    },
    "path": {
      "type": "string",
      "description": "A .md file or a folder of them."
    }
  },
  "required": [
    "action",
    "path"
  ]
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic implementation

Run this instead of improvising when the inputs are well-formed:

```python  # rapp:deterministic
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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
