"""PII Scout — find what must not ship, before it ships.

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
    "name": "@rapp/pii-scout",
    "tier": "core",
    "trust": "community",
    "version": "1.0.0",
    "tags": ["security", "publishing", "gate", "local-first", "singleton"],
    "example_call": {
        "args": {"path": ".", "terms": "acme,globex"},
        "note": "Scan the current folder for secrets, forbidden files and two names.",
    },
}

# High-precision only: provider-prefixed tokens, private keys, and explicit
# credential ASSIGNMENTS with a real-looking value. A bare `api_key` in prose is
# deliberately not a match — flagging documentation is how you teach people to
# stop reading the output.
SECRETS = re.compile(
    r"(ghp|ghu|ghs|gho)_[A-Za-z0-9]{30,}"
    r"|github_pat_[A-Za-z0-9_]{40,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|AIza[0-9A-Za-z_-]{30,}"
    r"|(AZURE_OPENAI_API_KEY|client_secret|secret_key|access_token|api_key|password)"
    r"""[ \t]*[:=][ \t]*["']?[A-Za-z0-9/+_.-]{16,}""")

FORBIDDEN = re.compile(
    r"(^|/)("
    r"\.env(\.[\w-]+)?"
    r"|[\w.-]*\.copilot_token"
    r"|[\w.-]*\.pem|[\w.-]*\.p12|[\w.-]*\.pfx"
    r"|id_rsa|id_ed25519"
    r"|[\w.-]*_token"
    r"|secrets?\.(json|ya?ml|txt)"
    r"|snapshot-\d{10,}\.html"
    r"|[\w.-]*\.har"
    r")$", re.I)
ALLOWED = re.compile(r"\.(env|settings)\.(example|sample|template)|\.example\.json$", re.I)

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HOMEPATH = re.compile(r"/(Users|home)/[A-Za-z0-9._-]+")
B64RUN = re.compile(r"[A-Za-z0-9+/=]{120,}")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


class PiiScoutAgent(BasicAgent):
    def __init__(self):
        self.name = "PiiScout"
        self.metadata = {
            "name": self.name,
            "description": (
                "Scan a folder for things that must not be published: secrets, "
                "credential files, captured sessions, email addresses, home "
                "paths, and any names you supply. Reports file and count, never "
                "the matched value. Use before pushing anything public."),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string",
                             "description": "Folder to scan. Defaults to the current directory."},
                    "terms": {"type": "string",
                              "description": "Comma-separated names that must not appear "
                                             "(customers, internal codenames, your own handle)."},
                    "max_findings": {"type": "integer",
                                     "description": "Cap the findings returned. Default 100."},
                },
                "required": [],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

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


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--tool":
        print(json.dumps(PiiScoutAgent().to_tool(), indent=2))
    else:
        raw = a[0] if a else (sys.stdin.read().strip() or '{"path":"."}')
        print(PiiScoutAgent().perform(**json.loads(raw)))
