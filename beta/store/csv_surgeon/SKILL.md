---
name: "csv-surgeon"
description: "Profile a CSV: per-column types, null rate, cardinality, min/max; or find ragged rows, duplicate headers and mixed types; or find duplicate records; or slice rows. Stdlib only, no network."
---

CSV Surgeon — profile a CSV and find the rows that will break something.

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
        "profile",
        "issues",
        "dupes",
        "slice"
      ],
      "description": "What to do."
    },
    "path": {
      "type": "string",
      "description": "Path to the .csv file."
    },
    "keys": {
      "type": "string",
      "description": "For dupes: comma-separated column names to match on. Default: the whole row."
    },
    "limit": {
      "type": "integer",
      "description": "For slice: how many rows. Default 10."
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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
