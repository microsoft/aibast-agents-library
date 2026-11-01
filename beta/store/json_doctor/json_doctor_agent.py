"""JSON Doctor — understand, validate and compare JSON without opening it.

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
"""

import json
import os
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
    "name": "@rapp/json-doctor",
    "tier": "core",
    "trust": "community",
    "version": "1.0.0",
    "tags": ["data", "json", "schema", "diff", "local-first", "singleton"],
    "example_call": {
        "args": {"action": "inspect", "path": "data.json"},
        "note": "Infer the shape of a JSON file, with per-field coverage.",
    },
}

MAX_BYTES = 64 * 1024 * 1024


def _typename(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return type(v).__name__


def _load(path):
    """Returns (records, mode). JSONL becomes a list of records so the same
    shape-inference works for both without a special case downstream."""
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError(f"file larger than {MAX_BYTES} bytes")
    text = open(path, encoding="utf-8").read()
    if path.endswith((".jsonl", ".ndjson")):
        recs = []
        for i, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"line {i}: {e.msg} at column {e.colno}")
        return recs, "jsonl"
    return json.loads(text), "json"


def _infer(records):
    """Field -> {types, present_in, coverage}. Coverage is the point: a key in
    3% of records is a different fact from one in 100%."""
    if isinstance(records, dict):
        records = [records]
    if not isinstance(records, list):
        return {"_root": {"types": [_typename(records)], "present_in": 1,
                          "coverage": "100%"}}
    objs = [r for r in records if isinstance(r, dict)]
    total = len(records)
    if not objs:
        kinds = sorted({_typename(r) for r in records})
        return {"_items": {"types": kinds, "present_in": total, "coverage": "100%"}}
    fields = {}
    for r in objs:
        for k, v in r.items():
            f = fields.setdefault(k, {"types": set(), "present_in": 0, "sample": None})
            f["types"].add(_typename(v))
            f["present_in"] += 1
            if f["sample"] is None and v not in (None, "", [], {}):
                s = v if not isinstance(v, (dict, list)) else _typename(v)
                f["sample"] = (s[:60] + "…") if isinstance(s, str) and len(s) > 60 else s
    out = {}
    for k, f in sorted(fields.items(), key=lambda x: -x[1]["present_in"]):
        pct = 100.0 * f["present_in"] / max(1, len(objs))
        out[k] = {"types": sorted(f["types"]), "present_in": f["present_in"],
                  "coverage": f"{pct:.0f}%", "sample": f["sample"]}
        if pct < 100:
            out[k]["optional"] = True
    return out


def _walk(obj, path):
    cur = obj
    for part in [p for p in path.split(".") if p]:
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
                continue
            except (ValueError, IndexError):
                return None, f"no index {part!r} in array of {len(cur)}"
        if isinstance(cur, dict):
            if part not in cur:
                return None, f"no key {part!r}; available: {sorted(cur)[:8]}"
            cur = cur[part]
            continue
        return None, f"cannot descend into {_typename(cur)} at {part!r}"
    return cur, None


class JsonDoctorAgent(BasicAgent):
    def __init__(self):
        self.name = "JsonDoctor"
        self.metadata = {
            "name": self.name,
            "description": (
                "Inspect, validate, diff or query a JSON/JSONL file. Infers the "
                "shape with per-field coverage, points at the exact line and "
                "column of a syntax error, compares two files structurally, and "
                "pulls values out by dotted path."),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string",
                               "enum": ["inspect", "validate", "diff", "query"],
                               "description": "What to do."},
                    "path": {"type": "string", "description": "Path to the JSON/JSONL file."},
                    "other": {"type": "string",
                              "description": "Second file, for action=diff."},
                    "key": {"type": "string",
                            "description": "Dotted path for action=query, e.g. users.0.name"},
                },
                "required": ["action", "path"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

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


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--tool":
        print(json.dumps(JsonDoctorAgent().to_tool(), indent=2))
    else:
        raw = a[0] if a else (sys.stdin.read().strip() or "{}")
        print(JsonDoctorAgent().perform(**json.loads(raw)))
