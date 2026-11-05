"""Log Detective — turn a wall of log lines into the three things you needed.

    summarise   level counts, time span, busiest minute, top error signatures
    signatures  cluster near-identical errors by shape, not text
    timeline    events per bucket, so a spike has a timestamp
    grep        filtered lines with surrounding context

No network, no credentials, no parsing config. Handles plain text, and reads
JSON-lines logs structurally when it detects them.

WHY IT CLUSTERS BY SIGNATURE INSTEAD OF COUNTING LINES

Ten thousand errors are usually four errors. Raw counts hide that: every line
differs by a request id, a timestamp, a port number, so nothing groups and you
scroll. Normalising the variable parts — numbers, hex ids, UUIDs, paths, quoted
strings — collapses them into a handful of shapes, and the shape is the bug.

WHY 'BUSIEST MINUTE' IS ITS OWN NUMBER

An incident is a spike, and a spike is invisible in a total. Knowing that 80% of
the day's errors landed inside one minute changes what you go and look at.

WHY IT NEVER PHONES HOME

Logs are the single most PII-dense artifact most systems produce. Anything that
uploads them to be "analysed" is a data-egress decision disguised as a feature.
This reads local files and returns local results.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

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
    "name": "@rapp/log-detective",
    "tier": "core",
    "trust": "community",
    "version": "1.0.0",
    "tags": ["logs", "debugging", "observability", "local-first", "singleton"],
    "example_call": {
        "args": {"action": "signatures", "path": "app.log"},
        "note": "Cluster near-identical errors by shape.",
    },
}

MAX_BYTES = 512 * 1024 * 1024
LEVEL = re.compile(r"\b(TRACE|DEBUG|INFO|NOTICE|WARN(?:ING)?|ERROR|ERR|FATAL|CRITICAL)\b", re.I)
TS = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"          # 2026-07-25 04:10:11
    r"|(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"             # apache
    r"|(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})")            # syslog

# Order matters: UUID before hex before plain number, or the general rules eat
# the specific ones and every signature collapses into the same mush.
NORMALISERS = [
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>"),
    (re.compile(r"\b0x[0-9a-f]+\b", re.I), "<hex>"),
    (re.compile(r"\b[0-9a-f]{16,}\b", re.I), "<hash>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), "<ip>"),
    (re.compile(r"[\"'][^\"']{1,80}[\"']"), "<str>"),
    (re.compile(r"(/[\w.\-]+){2,}"), "<path>"),
    # Numbers carry unit suffixes in real logs (815ms, 30s, 5KB, db-7). A
    # trailing \b never matches between a digit and a letter, so "815ms" kept
    # its number and every line became its own signature -- 96 clusters where
    # there were 3. Consume an optional unit so the shape actually groups.
    (re.compile(r"\b\d+(?:\.\d+)?(?:ms|s|m|h|d|kb|mb|gb|b|%)?\b", re.I), "<n>"),
]


def _norm(line):
    s = LEVEL.sub("", TS.sub("", line)).strip()
    for rx, rep in NORMALISERS:
        s = rx.sub(rep, s)
    return re.sub(r"\s+", " ", s).strip()[:200]


def _lines(path, cap=2_000_000):
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError(f"file larger than {MAX_BYTES} bytes")
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, ln in enumerate(fh):
            if i >= cap:
                break
            ln = ln.rstrip("\n")
            if ln.strip():
                out.append(ln)
    return out


def _structured(line):
    """A JSON-lines log carries level and message as fields; using them beats
    regexing text that was already structured."""
    t = line.lstrip()
    if not t.startswith("{"):
        return None
    try:
        d = json.loads(t)
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    lvl = d.get("level") or d.get("severity") or d.get("lvl")
    msg = d.get("message") or d.get("msg") or d.get("event")
    return {"level": str(lvl).upper() if lvl else None,
            "message": str(msg) if msg else None,
            "ts": d.get("time") or d.get("timestamp") or d.get("ts")}


class LogDetectiveAgent(BasicAgent):
    def __init__(self):
        self.name = "LogDetective"
        self.metadata = {
            "name": self.name,
            "description": (
                "Summarise a log file, cluster near-identical errors into "
                "signatures, build a timeline of events per bucket, or grep "
                "with context. Reads plain text and JSON-lines. Never uploads "
                "anything."),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string",
                               "enum": ["summarise", "signatures", "timeline", "grep"],
                               "description": "What to do."},
                    "path": {"type": "string", "description": "Path to the log file."},
                    "pattern": {"type": "string",
                                "description": "For grep: a regular expression."},
                    "context": {"type": "integer",
                                "description": "For grep: lines of context. Default 1."},
                    "top": {"type": "integer",
                            "description": "How many signatures/buckets. Default 10."},
                },
                "required": ["action", "path"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        action, path = kwargs.get("action"), kwargs.get("path")
        if not path or not os.path.isfile(path):
            return json.dumps({"status": "error",
                               "message": f"file not found: {path}"}, indent=2)
        top = int(kwargs.get("top") or 10)
        try:
            lines = _lines(path)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)
        if not lines:
            return json.dumps({"status": "ok", "lines": 0,
                               "note": "file is empty"}, indent=2)

        struct = sum(1 for ln in lines[:200] if _structured(ln))
        jsonl = struct > len(lines[:200]) * 0.6

        def level_of(ln):
            if jsonl:
                s = _structured(ln)
                if s and s["level"]:
                    return s["level"]
            m = LEVEL.search(ln)
            return m.group(1).upper() if m else None

        def body_of(ln):
            if jsonl:
                s = _structured(ln)
                if s and s["message"]:
                    return s["message"]
            return ln

        try:
            if action == "summarise":
                levels = Counter(level_of(l) or "UNLABELLED" for l in lines)
                stamps = [m.group(0) for l in lines
                          for m in [TS.search(l)] if m]
                minutes = Counter(s[:16] for s in stamps)
                bad = [l for l in lines
                       if (level_of(l) or "") in ("ERROR", "ERR", "FATAL", "CRITICAL")]
                sigs = Counter(_norm(body_of(l)) for l in bad)
                busiest = minutes.most_common(1)[0] if minutes else None
                return json.dumps({
                    "status": "ok", "format": "jsonl" if jsonl else "text",
                    "lines": len(lines), "levels": dict(levels.most_common()),
                    "first_timestamp": stamps[0] if stamps else None,
                    "last_timestamp": stamps[-1] if stamps else None,
                    "busiest_minute": ({"minute": busiest[0], "events": busiest[1]}
                                       if busiest else None),
                    "error_lines": len(bad),
                    "top_error_signatures": [
                        {"count": c, "signature": s} for s, c in sigs.most_common(top)],
                    "note": "an incident is a spike, and a spike is invisible in a total",
                }, indent=2)

            if action == "signatures":
                sigs, examples = Counter(), {}
                for l in lines:
                    lv = level_of(l) or ""
                    if lv in ("ERROR", "ERR", "FATAL", "CRITICAL", "WARN", "WARNING"):
                        s = _norm(body_of(l))
                        sigs[s] += 1
                        examples.setdefault(s, l[:200])
                total = sum(sigs.values())
                out = [{"count": c, "share": f"{100.0*c/max(1,total):.0f}%",
                        "signature": s, "example": examples[s]}
                       for s, c in sigs.most_common(top)]
                return json.dumps({
                    "status": "ok", "lines": len(lines),
                    "problem_lines": total, "distinct_signatures": len(sigs),
                    "signatures": out,
                    "note": "ten thousand errors are usually four errors — "
                            "variable parts are normalised so the shape groups",
                }, indent=2)

            if action == "timeline":
                buckets = Counter()
                for l in lines:
                    m = TS.search(l)
                    if m:
                        buckets[m.group(0)[:16]] += 1
                ordered = sorted(buckets.items())
                peak = max(buckets.values()) if buckets else 0
                return json.dumps({
                    "status": "ok", "buckets": len(ordered),
                    "peak_events": peak,
                    "timeline": [{"bucket": b, "events": c,
                                  "bar": "#" * max(1, round(20 * c / max(1, peak)))}
                                 for b, c in ordered[:120]],
                }, indent=2)

            if action == "grep":
                pat = kwargs.get("pattern")
                if not pat:
                    return json.dumps({"status": "error",
                                       "message": "pattern is required for grep"}, indent=2)
                try:
                    rx = re.compile(pat, re.I)
                except re.error as e:
                    return json.dumps({"status": "error",
                                       "message": f"bad regex: {e}"}, indent=2)
                ctx = int(kwargs.get("context") or 1)
                hits = []
                for i, l in enumerate(lines):
                    if rx.search(l):
                        hits.append({"line_no": i + 1,
                                     "before": lines[max(0, i - ctx):i],
                                     "match": l[:300],
                                     "after": lines[i + 1:i + 1 + ctx]})
                    if len(hits) >= 200:
                        break
                return json.dumps({"status": "ok", "lines": len(lines),
                                   "matches": len(hits), "hits": hits[:100]}, indent=2)

            return json.dumps({"status": "error",
                               "message": f"unknown action {action!r}",
                               "valid": ["summarise", "signatures", "timeline", "grep"]}, indent=2)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--tool":
        print(json.dumps(LogDetectiveAgent().to_tool(), indent=2))
    else:
        raw = a[0] if a else (sys.stdin.read().strip() or "{}")
        print(LogDetectiveAgent().perform(**json.loads(raw)))
