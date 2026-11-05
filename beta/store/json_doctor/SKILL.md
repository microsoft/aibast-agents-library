---
name: "json-doctor"
description: "Inspect, validate, diff or query a JSON/JSONL file. Infers the shape with per-field coverage, points at the exact line and column of a syntax error, compares two files structurally, and pulls values out by dotted path."
---

JSON Doctor — understand, validate and compare JSON without opening it.

Four things you actually need when a JSON file is too big to read:

    inspect   what shape is this? (inferred schema, key coverage, sample values)
    validate  is it well-formed, and where exactly does it break?
    diff      what changed between two of them, structurally?
    query     pull a value out by dotted path, including through arrays

Works on .json and .jsonl. No network, no credentials, no dependencies.

WHY IT REPORTS COVERAGE, NOT JUST KEYS

A key that appears in 3% of records is a different fact from one that appears in
100%, and the difference is usually the bug. A schema that says {"id": "string"}
hides that half the records have no id at all. So every inferred field carries
how often it was actually present, and optional fields are named as optional.

WHY VALIDATION POINTS AT A LINE AND COLUMN

"Invalid JSON" is a useless error on a 40MB file. json.JSONDecodeError already
knows the position; this surfaces it with the surrounding text so you can see
the trailing comma rather than go hunting for it.

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
        "inspect",
        "validate",
        "diff",
        "query"
      ],
      "description": "What to do."
    },
    "path": {
      "type": "string",
      "description": "Path to the JSON/JSONL file."
    },
    "other": {
      "type": "string",
      "description": "Second file, for action=diff."
    },
    "key": {
      "type": "string",
      "description": "Dotted path for action=query, e.g. users.0.name"
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
        action = kwargs.get("action")
        path = kwargs.get("path")
        if not path or not os.path.isfile(path):
            return json.dumps({"status": "error",
                               "message": f"file not found: {path}"}, indent=2)
        try:
            if action == "validate":
                try:
                    data, mode = _load(path)
                except (json.JSONDecodeError, ValueError) as e:
                    detail = {"status": "ok", "valid": False, "error": str(e)}
                    if isinstance(e, json.JSONDecodeError):
                        text = open(path, encoding="utf-8").read()
                        lo = max(0, e.pos - 60)
                        detail.update({"line": e.lineno, "column": e.colno,
                                       "context": text[lo:e.pos + 60]})
                    return json.dumps(detail, indent=2)
                n = len(data) if isinstance(data, list) else 1
                return json.dumps({"status": "ok", "valid": True, "mode": mode,
                                   "records": n,
                                   "root_type": _typename(data)}, indent=2)

            data, mode = _load(path)

            if action == "inspect":
                n = len(data) if isinstance(data, list) else 1
                return json.dumps({
                    "status": "ok", "mode": mode, "root_type": _typename(data),
                    "records": n, "bytes": os.path.getsize(path),
                    "fields": _infer(data),
                    "note": "coverage is the share of records containing the "
                            "field; anything under 100% is marked optional",
                }, indent=2)

            if action == "query":
                key = kwargs.get("key") or ""
                val, err = _walk(data, key)
                if err:
                    return json.dumps({"status": "error", "path": key,
                                       "message": err}, indent=2)
                return json.dumps({"status": "ok", "path": key,
                                   "type": _typename(val), "value": val}, indent=2)

            if action == "diff":
                other = kwargs.get("other")
                if not other or not os.path.isfile(other):
                    return json.dumps({"status": "error",
                                       "message": f"second file not found: {other}"}, indent=2)
                b, _ = _load(other)
                fa, fb = _infer(data), _infer(b)
                added = sorted(set(fb) - set(fa))
                removed = sorted(set(fa) - set(fb))
                changed = []
                for k in sorted(set(fa) & set(fb)):
                    if fa[k]["types"] != fb[k]["types"]:
                        changed.append({"field": k, "from": fa[k]["types"],
                                        "to": fb[k]["types"]})
                    elif fa[k]["coverage"] != fb[k]["coverage"]:
                        changed.append({"field": k, "coverage":
                                        f"{fa[k]['coverage']} -> {fb[k]['coverage']}"})
                return json.dumps({
                    "status": "ok",
                    "identical_shape": not (added or removed or changed),
                    "fields_added": added, "fields_removed": removed,
                    "fields_changed": changed,
                    "records": {"a": len(data) if isinstance(data, list) else 1,
                                "b": len(b) if isinstance(b, list) else 1},
                }, indent=2)

            return json.dumps({"status": "error",
                               "message": f"unknown action {action!r}",
                               "valid": ["inspect", "validate", "diff", "query"]}, indent=2)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
