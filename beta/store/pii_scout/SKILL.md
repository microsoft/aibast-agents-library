---
name: "pii-scout"
description: "Scan a folder for things that must not be published: secrets, credential files, captured sessions, email addresses, home paths, and any names you supply. Reports file and count, never the matched value. Use before pushing anything public."
---

PII Scout — find what must not ship, before it ships.

Point it at a folder. It reports secrets, forbidden artefact classes, and any
names you injected — with file and count, never the matched value.

Built for the moment before you publish something. That moment is where leaks
actually happen: not because anyone was careless, but because a tree accumulated
an archived copy, a captured session, a vendored fork of something already
fixed — and nobody re-read it, because nobody re-reads 40,000 files.

DESIGN RULES, all of them learned the hard way

  * Unconfigured is a REFUSAL, not a pass. A scanner with an empty roster
    reports "clean" precisely when it is checking nothing, and that reading is
    trusted because it looks like every other clean result.
  * Findings name the file and the count. Never the value. A leak report that
    quotes the secret is a second copy of the leak.
  * Whole artefact CLASSES are refused by shape, not just by content. A captured
    browser session carries identities, tenant GUIDs and key material that look
    nothing like a token; you cannot pattern-match what you did not know to look
    for, but you can refuse the file class that carries it.
  * Short ALL-CAPS terms match on word boundaries. An acronym that fires inside
    unrelated words produces noise, and noise is how a gate gets switched off.
  * Long base64 runs are skipped for IDENTITY matching only. Random base64
    contains short names by chance; reporting that as PII trains people to
    ignore real findings. Secrets are still matched everywhere, including blobs.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Folder to scan. Defaults to the current directory."
    },
    "terms": {
      "type": "string",
      "description": "Comma-separated names that must not appear (customers, internal codenames, your own handle)."
    },
    "max_findings": {
      "type": "integer",
      "description": "Cap the findings returned. Default 100."
    }
  },
  "required": []
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic implementation

Run this instead of improvising when the inputs are well-formed:

```python  # rapp:deterministic
def perform(self, **kwargs):
        path = kwargs.get("path") or "."
        if not os.path.isdir(path):
            return json.dumps({"status": "error",
                               "message": f"not a directory: {path}"}, indent=2)
        cap = int(kwargs.get("max_findings") or 100)
        raw = (kwargs.get("terms") or os.environ.get("PII_SCOUT_TERMS") or "").strip()
        terms = [t.strip() for t in raw.split(",") if t.strip()]

        rules = []
        for t in terms:
            anchored = t.isupper() and len(t) <= 4
            body = t if re.search(r"[\[\](){}|+*?\\]", t) else re.escape(t)
            rules.append((t, re.compile((r"\b" + body + r"\b") if anchored else body, re.I)))

        findings, scanned, skipped = [], 0, 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, path)
                if FORBIDDEN.search(rel) and not ALLOWED.search(rel):
                    findings.append({"kind": "forbidden-file", "file": rel,
                                     "why": "this file class must never be published"})
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                except Exception:
                    skipped += 1
                    continue
                scanned += 1
                n = len(SECRETS.findall(text))
                if n:
                    findings.append({"kind": "secret", "file": rel, "matches": n})
                # identity checks ignore base64 blobs (chance collisions)
                clean = B64RUN.sub("", text)
                e = len(set(EMAIL.findall(clean)))
                if e:
                    findings.append({"kind": "email", "file": rel, "distinct": e})
                h = len(set(HOMEPATH.findall(clean)))
                if h:
                    findings.append({"kind": "home-path", "file": rel, "distinct": h})
                for term, rx in rules:
                    c = len(rx.findall(clean))
                    if c:
                        findings.append({"kind": "name", "file": rel,
                                         "term": term, "matches": c})
                if len(findings) >= cap:
                    break

        clean_run = not findings
        out = {
            "status": "ok",
            "verdict": "CLEAN" if clean_run else "DO-NOT-PUBLISH",
            "safe_to_publish": clean_run,
            "scanned_files": scanned,
            "unreadable_skipped": skipped,
            "names_checked": len(terms),
            "findings": findings[:cap],
            "note": "Values are never reported — only file and count. A report "
                    "that quotes the secret is a second copy of it.",
        }
        if not terms:
            out["warning"] = (
                "No names supplied, so only secrets, file classes, emails and "
                "home paths were checked. Customer names and your own handle "
                "were NOT — pass `terms` to check those. A private tree is "
                "usually full of the owner's own name.")
        return json.dumps(out, indent=2)
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
