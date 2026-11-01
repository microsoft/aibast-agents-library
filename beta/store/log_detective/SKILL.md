---
name: "log-detective"
description: "Summarise a log file, cluster near-identical errors into signatures, build a timeline of events per bucket, or grep with context. Reads plain text and JSON-lines. Never uploads anything."
---

Log Detective — turn a wall of log lines into the three things you needed.

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
        "summarise",
        "signatures",
        "timeline",
        "grep"
      ],
      "description": "What to do."
    },
    "path": {
      "type": "string",
      "description": "Path to the log file."
    },
    "pattern": {
      "type": "string",
      "description": "For grep: a regular expression."
    },
    "context": {
      "type": "integer",
      "description": "For grep: lines of context. Default 1."
    },
    "top": {
      "type": "integer",
      "description": "How many signatures/buckets. Default 10."
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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
