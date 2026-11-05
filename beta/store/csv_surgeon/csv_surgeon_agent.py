"""CSV Surgeon — profile a CSV and find the rows that will break something.

    profile   per-column type, null rate, cardinality, min/max, sample values
    issues    ragged rows, duplicate headers, mixed types, whitespace-padded keys
    dupes     duplicate records, by whole row or by chosen key columns
    slice     head/tail/filter rows without loading the file into a spreadsheet

Pure stdlib `csv`, no pandas, no network, no credentials.

WHY IT LEADS WITH NULL RATE AND CARDINALITY

Those two numbers explain most CSV surprises. A column that is 40% empty will
break a join you thought was safe. A column with cardinality 1 is a constant
someone forgot to remove. A column with cardinality == row count is an id, and
joining on anything else is probably a mistake. None of that is visible by
looking at the first ten rows, which is what everyone does.

WHY RAGGED ROWS GET THEIR OWN CHECK

A row with the wrong number of fields is the single most common CSV defect, and
most tools silently pad or truncate it. The data then looks fine and is wrong.
This reports the row number so you can go and look at it.

WHY WHITESPACE IN HEADERS IS A FINDING

`"name"` and `"name "` are different keys in every downstream consumer, and the
difference is invisible in every viewer. It produces bugs that read as
impossible.
"""

import csv
import io
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
    "name": "@rapp/csv-surgeon",
    "tier": "core",
    "trust": "community",
    "version": "1.0.0",
    "tags": ["data", "csv", "profiling", "quality", "local-first", "singleton"],
    "example_call": {
        "args": {"action": "profile", "path": "data.csv"},
        "note": "Per-column types, null rates and cardinality.",
    },
}

MAX_BYTES = 256 * 1024 * 1024
SAMPLE_CAP = 200_000


def _kind(s):
    if s is None or s == "":
        return "empty"
    t = s.strip()
    if t.lower() in ("true", "false"):
        return "bool"
    try:
        int(t)
        return "int"
    except ValueError:
        pass
    try:
        float(t)
        return "float"
    except ValueError:
        pass
    return "string"


def _read(path, limit=SAMPLE_CAP):
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError(f"file larger than {MAX_BYTES} bytes")
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        sample = fh.read(64 * 1024)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel        # a single-column file sniffs as an error
        r = csv.reader(fh, dialect)
        rows = []
        for i, row in enumerate(r):
            if i > limit:
                break
            rows.append(row)
    delim = getattr(dialect, "delimiter", ",")
    return rows, delim


class CsvSurgeonAgent(BasicAgent):
    def __init__(self):
        self.name = "CsvSurgeon"
        self.metadata = {
            "name": self.name,
            "description": (
                "Profile a CSV: per-column types, null rate, cardinality, "
                "min/max; or find ragged rows, duplicate headers and mixed "
                "types; or find duplicate records; or slice rows. Stdlib only, "
                "no network."),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string",
                               "enum": ["profile", "issues", "dupes", "slice"],
                               "description": "What to do."},
                    "path": {"type": "string", "description": "Path to the .csv file."},
                    "keys": {"type": "string",
                             "description": "For dupes: comma-separated column names "
                                            "to match on. Default: the whole row."},
                    "limit": {"type": "integer",
                              "description": "For slice: how many rows. Default 10."},
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
        try:
            rows, delim = _read(path)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)
        if not rows:
            return json.dumps({"status": "ok", "rows": 0, "note": "empty file"}, indent=2)

        header, body = rows[0], rows[1:]
        ncol = len(header)

        try:
            if action == "profile":
                cols = []
                for i, name in enumerate(header):
                    vals = [r[i] if i < len(r) else "" for r in body]
                    kinds = {}
                    nonempty = []
                    for v in vals:
                        k = _kind(v)
                        kinds[k] = kinds.get(k, 0) + 1
                        if k != "empty":
                            nonempty.append(v.strip())
                    uniq = len(set(nonempty))
                    nulls = kinds.get("empty", 0)
                    numeric = [x for x in nonempty
                               if _kind(x) in ("int", "float")]
                    col = {
                        "column": name,
                        "types": sorted([k for k in kinds if k != "empty"]) or ["empty"],
                        "null_rate": f"{100.0 * nulls / max(1, len(vals)):.0f}%",
                        "cardinality": uniq,
                        "sample": nonempty[0][:40] if nonempty else None,
                    }
                    if numeric:
                        nums = [float(x) for x in numeric]
                        col["min"], col["max"] = min(nums), max(nums)
                    if uniq == len(body) and body:
                        col["note"] = "unique per row — looks like an id"
                    elif uniq == 1 and nonempty:
                        col["note"] = "single value — constant column"
                    if len(col["types"]) > 1:
                        col["note"] = "MIXED TYPES — will break a strict consumer"
                    cols.append(col)
                return json.dumps({"status": "ok", "rows": len(body),
                                   "columns": ncol, "delimiter": delim,
                                   "profile": cols,
                                   "note": "null rate and cardinality explain most "
                                           "CSV surprises, and neither is visible "
                                           "in the first ten rows."}, indent=2)

            if action == "issues":
                issues = []
                seen_h = {}
                for i, h in enumerate(header):
                    if h != h.strip():
                        issues.append({"kind": "padded-header", "column": i,
                                       "detail": repr(h),
                                       "why": "'name' and 'name ' are different keys "
                                              "downstream, and look identical in a viewer"})
                    if h.strip() in seen_h:
                        issues.append({"kind": "duplicate-header",
                                       "column": i, "detail": h.strip()})
                    seen_h[h.strip()] = i
                    if not h.strip():
                        issues.append({"kind": "empty-header", "column": i})
                for n, r in enumerate(body, start=2):
                    if len(r) != ncol:
                        issues.append({"kind": "ragged-row", "row": n,
                                       "detail": f"{len(r)} fields, expected {ncol}",
                                       "why": "most tools silently pad or truncate "
                                              "this; the data then looks fine and is wrong"})
                    if len(issues) > 200:
                        break
                return json.dumps({"status": "ok", "rows": len(body),
                                   "issue_count": len(issues),
                                   "clean": not issues,
                                   "issues": issues[:100]}, indent=2)

            if action == "dupes":
                keyspec = (kwargs.get("keys") or "").strip()
                if keyspec:
                    names = [k.strip() for k in keyspec.split(",") if k.strip()]
                    missing = [n for n in names if n not in header]
                    if missing:
                        return json.dumps({"status": "error",
                                           "message": f"no such column(s): {missing}",
                                           "available": header}, indent=2)
                    idxs = [header.index(n) for n in names]
                else:
                    names, idxs = header, list(range(ncol))
                seen, dupes = {}, []
                for n, r in enumerate(body, start=2):
                    key = tuple(r[i] if i < len(r) else "" for i in idxs)
                    if key in seen:
                        dupes.append({"row": n, "first_seen_row": seen[key],
                                      "key": dict(zip(names, key))})
                    else:
                        seen[key] = n
                return json.dumps({"status": "ok", "rows": len(body),
                                   "matched_on": names,
                                   "duplicate_count": len(dupes),
                                   "duplicates": dupes[:100]}, indent=2)

            if action == "slice":
                lim = int(kwargs.get("limit") or 10)
                out = [dict(zip(header, r)) for r in body[:lim]]
                return json.dumps({"status": "ok", "rows": len(body),
                                   "returned": len(out), "records": out}, indent=2)

            return json.dumps({"status": "error",
                               "message": f"unknown action {action!r}",
                               "valid": ["profile", "issues", "dupes", "slice"]}, indent=2)
        except Exception as e:
            return json.dumps({"status": "error",
                               "message": f"{type(e).__name__}: {e}"}, indent=2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--tool":
        print(json.dumps(CsvSurgeonAgent().to_tool(), indent=2))
    else:
        raw = a[0] if a else (sys.stdin.read().strip() or "{}")
        print(CsvSurgeonAgent().perform(**json.loads(raw)))
