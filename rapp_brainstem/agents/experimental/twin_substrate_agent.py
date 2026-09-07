"""twin_substrate_agent.py — designate ANY parent, virtual or physical, and give
its twin a substrate: the parent's own record, harvested, indexed, queryable.

ONE file. Stdlib only. Drop into agents/ on any standard brainstem. Touches NO
engine file — brainstem.py, VERSION, soul.md and the rest of the Grail kernel are
never read for write and never modified. This is a cartridge, per Article II.

WHAT THIS ADDS TO THE TWIN CONTRACT
-----------------------------------
`rapp/1-twin` (canon, twin-opus) says a twin is "soul + agents + memory, running
live on whatever model the host provides... what transfers is judgment." That
stands unchanged. Canon also has `parent_rappid` — but that is LINEAGE: which
TWIN this twin descends from, walking back to the rapp species root.

Nothing in canon says what a twin is a twin OF. `kind="place"` hands a physical
parent a VOICE template and no knowledge — roleplay, not a twin.

`rapp/2-twin` is additive. Two new blocks, no field removed, no reader broken:

  parent    — the SUBJECT. Anything virtual or physical can be designated.
              Open vocabulary: person, place, repo, device, org, process,
              vehicle, document, system, animal, account, machine, ...
              An enum would be the same mistake as a fixed twin taxonomy.

  substrate — where the twin's knowledge of that parent comes from. A list of
              sources, each with a registered type, harvested into one normalized
              event stream and indexed. Every parent class uses the SAME engine;
              only the source types differ. A person's substrate is transcripts
              and commits. A building's is photos, inspections and sensor logs.

A twin without a substrate guesses at its parent. A twin with one KNOWS it, and
every answer carries a ptr back to the exact line of evidence.

USAGE (over /chat)
------------------
  "Designate my workflow as a parent and twin it"
    -> TwinSubstrate(action="designate", twin="kody-workflow",
                     parent_class="person", parent_nature="virtual",
                     preset="workflow")
  "Harvest it"        -> TwinSubstrate(action="harvest", twin="kody-workflow")
  "How did I fix the device-code auth hang?"
                      -> TwinSubstrate(action="recall", twin="kody-workflow",
                                       query="device code auth hang")

BULK MODE (outside a request timeout)
-------------------------------------
  python twin_substrate_agent.py harvest kody-workflow
  python twin_substrate_agent.py status  kody-workflow
"""

import csv
import fnmatch
import glob
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone

try:
    from agents.basic_agent import BasicAgent
except Exception:  # CLI mode, outside the brainstem
    class BasicAgent:
        def __init__(self, *a, **k): pass


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/twin_substrate_agent",
    "version": "1.0.0",
    "display_name": "Twin Substrate",
    "description": (
        "Designate anything virtual or physical as the parent of a twin, bind the "
        "sources that record it, harvest them into one indexed substrate, and query "
        "it. Every answer cites a pointer back to the original evidence."
    ),
    "author": "kody-w",
    "tags": ["twin", "substrate", "parent", "exhaust", "index", "local-first"],
    "category": "general",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic_agent"],
    "example_call": "Designate my workflow as a parent and build its twin substrate.",
}

TWIN_SCHEMA = "rapp/2-twin"
ACTIONS = ("designate", "bind", "harvest", "search", "recall", "timeline",
           "status", "list", "inspect", "sources", "open")


# ── Paths ───────────────────────────────────────────────────────────────

def _twins_root():
    return pathlib.Path(os.environ.get("BRAINSTEM_TWINS_ROOT")
                        or (pathlib.Path.home() / ".brainstem" / "twins"))


def _twin_dir(twin):
    return _twins_root() / _slug(twin)


def _slug(name):
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", (name or "").strip().lower()).strip("-.")
    return s or "twin"


def _expand(p):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(str(p))))


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _iso(ts):
    """Normalize epoch seconds / ms / ISO string -> ISO-8601 UTC."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        if ts > 1e11:      # milliseconds
            ts = ts / 1000.0
        try:
            return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")
        except Exception:
            return None
    s = str(ts).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(
            timezone.utc).isoformat(timespec="seconds")
    except Exception:
        return s[:19]


# ── Redaction — pointers, never values ──────────────────────────────────
# The substrate is an index of a parent's record. Credential-shaped strings are
# dropped at harvest so they cannot enter the store even once.

_SECRET_PATTERNS = [
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}"), "github-token"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "api-key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws-key-id"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "jwt"),
    (re.compile(r"(?i)\b(?:api[_-]?key|secret|password|passwd|token|bearer)"
                r"\s*[:=]\s*[\"']?([A-Za-z0-9/+_-]{16,})[\"']?"), "assignment"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "slack-token"),
]


def _scrub(text):
    if not text:
        return text
    for rx, kind in _SECRET_PATTERNS:
        text = rx.sub(f"[REDACTED:{kind}]", text)
    return text


# ── Store ───────────────────────────────────────────────────────────────

_DDL = """
CREATE TABLE IF NOT EXISTS events (
  id          INTEGER PRIMARY KEY,
  ts          TEXT,
  source      TEXT NOT NULL,
  source_type TEXT NOT NULL,
  ref         TEXT,
  kind        TEXT,
  title       TEXT,
  text        TEXT,
  ptr         TEXT,
  meta        TEXT,
  dedup       TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_events_ts     ON events(ts);
CREATE INDEX IF NOT EXISTS ix_events_source ON events(source);
CREATE INDEX IF NOT EXISTS ix_events_ref    ON events(ref);

CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
  title, text, content='events', content_rowid='id', tokenize='porter unicode61'
);
CREATE TRIGGER IF NOT EXISTS events_ai AFTER INSERT ON events BEGIN
  INSERT INTO events_fts(rowid, title, text) VALUES (new.id, new.title, new.text);
END;
CREATE TRIGGER IF NOT EXISTS events_ad AFTER DELETE ON events BEGIN
  INSERT INTO events_fts(events_fts, rowid, title, text)
  VALUES('delete', old.id, old.title, old.text);
END;

CREATE TABLE IF NOT EXISTS watermarks (
  source TEXT NOT NULL, path TEXT NOT NULL,
  mtime_ns INTEGER, size INTEGER, offset INTEGER DEFAULT 0, seen_utc TEXT,
  PRIMARY KEY (source, path)
);
"""


def _connect(twin):
    d = _twin_dir(twin)
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(d / "substrate.db"), timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript(_DDL)
    return con


# ── Manifest (additive — never regenerates what a prior author wrote) ────

def _manifest_path(twin):
    return _twin_dir(twin) / "manifest.json"


def _read_manifest(twin):
    p = _manifest_path(twin)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def _write_manifest(twin, man):
    p = _manifest_path(twin)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=2))
    tmp.replace(p)


# ── Source type registry ────────────────────────────────────────────────
# A harvester yields normalized event dicts. Adding a parent class never means
# touching the engine — it means registering a source type here.

HARVESTERS = {}


def harvester(name):
    def deco(fn):
        HARVESTERS[name] = fn
        return fn
    return deco


def _ev(ts, kind, title, text, ref=None, ptr=None, **meta):
    return {"ts": _iso(ts), "kind": kind, "title": (title or "")[:500],
            "text": text or "", "ref": ref, "ptr": ptr, "meta": meta}


def _wm_get(con, source, path):
    r = con.execute("SELECT mtime_ns,size,offset FROM watermarks WHERE source=? AND path=?",
                    (source, path)).fetchone()
    return r or (None, None, 0)


def _wm_set(con, source, path, mtime_ns, size, offset=0):
    con.execute("INSERT INTO watermarks(source,path,mtime_ns,size,offset,seen_utc) "
                "VALUES(?,?,?,?,?,?) ON CONFLICT(source,path) DO UPDATE SET "
                "mtime_ns=excluded.mtime_ns,size=excluded.size,offset=excluded.offset,"
                "seen_utc=excluded.seen_utc",
                (source, path, mtime_ns, size, offset, _now()))


def _unchanged(con, source, path):
    try:
        st = os.stat(path)
    except OSError:
        return True
    m, s, _ = _wm_get(con, source, path)
    if m == st.st_mtime_ns and s == st.st_size:
        return True
    return False


def _mark(con, source, path):
    try:
        st = os.stat(path)
        _wm_set(con, source, path, st.st_mtime_ns, st.st_size)
    except OSError:
        pass


def _text_of(content):
    """Flatten an Anthropic-style message content field to plain text."""
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for b in content:
            if isinstance(b, str):
                out.append(b)
            elif isinstance(b, dict):
                if b.get("type") == "text" and b.get("text"):
                    out.append(b["text"])
                elif b.get("type") == "tool_use":
                    out.append(f"[tool:{b.get('name','?')}]")
                elif b.get("type") == "thinking":
                    continue
    return "\n".join(out)


@harvester("claude_transcripts")
def _h_claude(con, src, emit):
    """Claude Code session JSONL. Indexes turn text + metadata, not raw tool
    payloads — those stay on disk and are reachable through the ptr."""
    root = _expand(src.get("root", "~/.claude/projects"))
    limit = int(src.get("limit_files") or 0)
    files = sorted(glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True),
                   key=lambda p: -os.path.getmtime(p) if os.path.exists(p) else 0)
    if limit:
        files = files[:limit]
    n = 0
    for fp in files:
        if _unchanged(con, src["id"], fp):
            continue
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                for ln, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    t = d.get("type")
                    if t not in ("user", "assistant"):
                        continue
                    msg = d.get("message") or {}
                    body = _text_of(msg.get("content"))
                    if not body or len(body) < 12:
                        continue
                    ref = d.get("cwd") or d.get("slug") or os.path.basename(os.path.dirname(fp))
                    emit(_ev(d.get("timestamp"), f"turn.{t}",
                             (d.get("aiTitle") or body.strip().split("\n")[0])[:200],
                             body, ref=ref, ptr=f"{fp}:{ln}",
                             session=d.get("sessionId"), branch=d.get("gitBranch"),
                             cwd=d.get("cwd")))
                    n += 1
        except OSError:
            continue
        _mark(con, src["id"], fp)
    return n


@harvester("prompt_history")
def _h_prompts(con, src, emit):
    """The intent stream: what was asked for, in the parent's own words."""
    fp = _expand(src.get("path", "~/.claude/history.jsonl"))
    if not os.path.exists(fp) or _unchanged(con, src["id"], fp):
        return 0
    n = 0
    with open(fp, "r", encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            try:
                d = json.loads(line)
            except Exception:
                continue
            disp = (d.get("display") or "").strip()
            if not disp or disp.startswith("/clear"):
                continue
            emit(_ev(d.get("timestamp"), "prompt", disp[:200], disp,
                     ref=d.get("project"), ptr=f"{fp}:{ln}",
                     session=d.get("sessionId")))
            n += 1
    _mark(con, src["id"], fp)
    return n


def _git_toplevel(path):
    """The repo containing `path`, or '' when it is not inside one."""
    try:
        out = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


@harvester("git_estate")
def _h_git(con, src, emit):
    """Shipped truth. One root of repos, or a single repo."""
    root = _expand(src.get("root", "."))
    since = src.get("since", "1 year ago")
    maxr = int(src.get("max_repos") or 0)
    repos = []
    if os.path.isdir(os.path.join(root, ".git")):
        repos = [root]
    elif _git_toplevel(root):
        repos = [_git_toplevel(root)]  # a subfolder of a repo: harvest the repo it belongs to
    else:
        for entry in sorted(os.listdir(root)):
            p = os.path.join(root, entry)
            if os.path.isdir(os.path.join(p, ".git")):
                repos.append(p)
    if maxr:
        repos = repos[:maxr]
    n = 0
    for repo in repos:
        try:
            out = subprocess.run(
                ["git", "-C", repo, "log", f"--since={since}", "--all", "--no-merges",
                 "--date=iso-strict",
                 "--pretty=format:%H%x1f%ad%x1f%an%x1f%s%x1f%b%x1e"],
                capture_output=True, text=True, timeout=60).stdout
        except Exception:
            continue
        name = os.path.basename(repo)
        for rec in out.split("\x1e"):
            rec = rec.strip("\n")
            if not rec:
                continue
            parts = rec.split("\x1f")
            if len(parts) < 4:
                continue
            sha, date, author, subj = parts[0], parts[1], parts[2], parts[3]
            bodytxt = parts[4] if len(parts) > 4 else ""
            emit(_ev(date, "commit", subj, (subj + "\n" + bodytxt).strip(),
                     ref=name, ptr=f"{repo}#{sha}", sha=sha, author=author))
            n += 1
    return n


@harvester("filesystem")
def _h_fs(con, src, emit):
    """Text-bearing files under a root: notes, docs, inspections, reports."""
    root = _expand(src.get("root", "."))
    globs = src.get("globs") or ["**/*.md"]
    maxb = int(src.get("max_bytes") or 400_000)
    n = 0
    for g in globs:
        for fp in glob.glob(os.path.join(root, g), recursive=True):
            if not os.path.isfile(fp) or _unchanged(con, src["id"], fp):
                continue
            try:
                if os.path.getsize(fp) > maxb:
                    continue
                body = open(fp, "r", encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            st = os.stat(fp)
            emit(_ev(st.st_mtime, "document", os.path.basename(fp), body,
                     ref=os.path.relpath(fp, root), ptr=f"{fp}:1"))
            _mark(con, src["id"], fp)
            n += 1
    return n


@harvester("shell_history")
def _h_shell(con, src, emit):
    fp = _expand(src.get("path", "~/.zsh_history"))
    if not os.path.exists(fp) or _unchanged(con, src["id"], fp):
        return 0
    n = 0
    rx = re.compile(r"^: (\d+):\d+;(.*)$")
    with open(fp, "r", encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            m = rx.match(line)
            ts, cmd = (int(m.group(1)), m.group(2)) if m else (None, line)
            cmd = cmd.strip()
            if len(cmd) < 4:
                continue
            emit(_ev(ts, "command", cmd[:200], cmd, ptr=f"{fp}:{ln}"))
            n += 1
    _mark(con, src["id"], fp)
    return n


@harvester("csv_timeseries")
def _h_csv(con, src, emit):
    """PHYSICAL parents: sensor readings, meter logs, inspection rows.
    Any CSV with a timestamp column becomes substrate."""
    root = _expand(src.get("root", "."))
    tscol = src.get("ts_column")
    paths = [root] if os.path.isfile(root) else glob.glob(
        os.path.join(root, src.get("glob", "**/*.csv")), recursive=True)
    n = 0
    for fp in paths:
        if _unchanged(con, src["id"], fp):
            continue
        try:
            with open(fp, "r", encoding="utf-8", errors="replace", newline="") as fh:
                rd = csv.DictReader(fh)
                cols = rd.fieldnames or []
                tc = tscol or next((c for c in cols if c and re.search(
                    r"(?i)time|date|ts\b", c)), None)
                for ln, row in enumerate(rd, 2):
                    body = "; ".join(f"{k}={v}" for k, v in row.items() if v)
                    if not body:
                        continue
                    emit(_ev(row.get(tc) if tc else os.path.getmtime(fp), "reading",
                             body[:200], body, ref=os.path.basename(fp),
                             ptr=f"{fp}:{ln}"))
                    n += 1
        except OSError:
            continue
        _mark(con, src["id"], fp)
    return n


@harvester("media")
def _h_media(con, src, emit):
    """PHYSICAL parents: photographs of a place, a device, a vehicle, a build.
    Indexes the observation (what/when/where on disk), not pixels."""
    root = _expand(src.get("root", "."))
    exts = tuple(e.lower() for e in (src.get("exts") or
                 [".jpg", ".jpeg", ".png", ".heic", ".mov", ".mp4", ".pdf"]))
    n = 0
    for dirpath, _, names in os.walk(root):
        for nm in names:
            if not nm.lower().endswith(exts):
                continue
            fp = os.path.join(dirpath, nm)
            if _unchanged(con, src["id"], fp):
                continue
            try:
                st = os.stat(fp)
            except OSError:
                continue
            rel = os.path.relpath(fp, root)
            # The folder path is the human's own labelling — real signal.
            body = f"{nm} in {os.path.dirname(rel) or '.'} ({st.st_size} bytes)"
            emit(_ev(st.st_mtime, "observation", nm, body, ref=rel, ptr=f"{fp}:1",
                     bytes=st.st_size))
            _mark(con, src["id"], fp)
            n += 1
    return n


@harvester("jsonl")
def _h_jsonl(con, src, emit):
    """Generic escape hatch: any JSONL, with configurable field mapping."""
    fp = _expand(src.get("path", ""))
    if not fp or not os.path.exists(fp) or _unchanged(con, src["id"], fp):
        return 0
    fts, ftx, fti = src.get("ts_field", "timestamp"), src.get("text_field", "text"), \
        src.get("title_field", "title")
    n = 0
    with open(fp, "r", encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            try:
                d = json.loads(line)
            except Exception:
                continue
            body = d.get(ftx) or json.dumps(d)[:2000]
            emit(_ev(d.get(fts), src.get("kind", "record"),
                     str(d.get(fti) or body)[:200], str(body), ptr=f"{fp}:{ln}"))
            n += 1
    _mark(con, src["id"], fp)
    return n


# ── Presets — starting substrates for common parent classes ─────────────
# Not a taxonomy. Convenience only; any source list can be built by hand.

PRESETS = {
    "workflow": [
        {"type": "claude_transcripts", "root": "~/.claude/projects"},
        {"type": "prompt_history", "path": "~/.claude/history.jsonl"},
        {"type": "filesystem", "root": "~/.claude/projects", "globs": ["**/memory/*.md"]},
        {"type": "shell_history", "path": "~/.zsh_history"},
    ],
    "repo": [
        {"type": "git_estate", "root": "."},
        {"type": "filesystem", "root": ".", "globs": ["**/*.md"]},
    ],
    "estate": [
        {"type": "git_estate", "root": "~/Documents/GitHub", "since": "1 year ago"},
    ],
    "place": [
        {"type": "media", "root": "."},
        {"type": "filesystem", "root": ".", "globs": ["**/*.md", "**/*.txt"]},
        {"type": "csv_timeseries", "root": "."},
    ],
    "device": [
        {"type": "csv_timeseries", "root": "."},
        {"type": "filesystem", "root": ".", "globs": ["**/*.log", "**/*.md"]},
    ],
}


# ── Operations ──────────────────────────────────────────────────────────

def op_designate(twin, parent_class="thing", parent_nature="virtual",
                 display_name=None, address=None, preset=None, note=None, **_):
    """Designate a parent and give its twin a substrate.

    parent_class is an OPEN vocabulary. person, place, repo, device, org,
    process, vehicle, document, system, animal, account — or anything else.
    A closed enum here would recreate the exact limitation this fixes.
    """
    if parent_nature not in ("virtual", "physical", "hybrid"):
        return (f"parent_nature must be virtual, physical or hybrid "
                f"(got {parent_nature!r}). A physical parent is a real-world "
                f"thing — a building, a machine, a vehicle, a body of land.")
    slug = _slug(twin)
    man = _read_manifest(slug)          # preserve anything already authored
    addrs = address if isinstance(address, list) else ([address] if address else [])
    norm_addrs = []
    for a in addrs:
        if isinstance(a, dict):
            norm_addrs.append(a)
        elif isinstance(a, str):
            if "://" in a:
                sch, val = a.split("://", 1)
                norm_addrs.append({"scheme": sch, "value": val})
            elif os.path.exists(_expand(a)):
                norm_addrs.append({"scheme": "file", "value": _expand(a)})
            else:
                norm_addrs.append({"scheme": "name", "value": a})

    parent = man.get("parent") or {}
    parent.update({
        "nature": parent_nature,
        "class": parent_class,
        "display_name": display_name or _display(slug),
        "address": norm_addrs or parent.get("address") or [],
        "designated_utc": parent.get("designated_utc") or _now(),
    })
    if note:
        parent["note"] = note

    sources = (man.get("substrate") or {}).get("sources") or []
    if preset:
        if preset not in PRESETS:
            return f"Unknown preset {preset!r}. Available: {', '.join(sorted(PRESETS))}"
        base = _expand(norm_addrs[0]["value"]) if (
            norm_addrs and norm_addrs[0].get("scheme") == "file") else None
        for s in PRESETS[preset]:
            s = dict(s)
            if base:
                for key in ("root", "path"):
                    if s.get(key) in (".", "./"):
                        s[key] = base
                    elif key in s and str(s[key]).startswith("./"):
                        s[key] = os.path.join(base, str(s[key])[2:])
            s["id"] = s.get("id") or _sid(s)
            if not any(x.get("id") == s["id"] for x in sources):
                sources.append(s)

    # rapp/1-twin fields are preserved untouched; rapp/2-twin is purely additive.
    man.setdefault("name", slug)
    man.setdefault("display_name", parent["display_name"])
    man.setdefault("created_utc", _now())
    man.setdefault("kind", "RAPP Twin")
    man["schema"] = TWIN_SCHEMA
    man["parent"] = parent
    man["substrate"] = {
        "store": str(_twin_dir(slug) / "substrate.db"),
        "sources": sources,
        "engine": "@kody-w/twin_substrate_agent",
    }
    man.setdefault("what_a_twin_is",
                   "soul + agents + memory, running live on whatever model the host "
                   "provides. Not a copy of a model - weights do not move. What "
                   "transfers is judgment.")
    man["parent_contract"] = (
        "`parent` is the SUBJECT this twin is a twin OF - anything virtual or "
        "physical may be designated. Distinct from `parent_rappid`, which is "
        "LINEAGE (which twin this one descends from). Both may be present.")
    _write_manifest(slug, man)
    _connect(slug).close()

    lines = [f"Designated parent for twin '{slug}'.",
             f"  parent : {parent['display_name']}  [{parent_nature}/{parent_class}]"]
    for a in parent["address"]:
        lines.append(f"  address: {a.get('scheme')}://{a.get('value')}")
    lines.append(f"  sources: {len(sources)} bound"
                 + (f" (preset '{preset}')" if preset else ""))
    lines.append(f"  store  : {man['substrate']['store']}")
    if sources:
        for s in sources:
            lines.append(f"     - {s['type']}: {s.get('root') or s.get('path') or ''}")
    lines.append("")
    lines.append("Nothing is indexed yet. Harvest to give the twin its knowledge:")
    lines.append(f"  TwinSubstrate(action='harvest', twin='{slug}')")
    return "\n".join(lines)


def _display(slug):
    return " ".join(w.capitalize() for w in re.split(r"[-_.]+", slug) if w)


def _sid(s):
    key = json.dumps({k: v for k, v in s.items() if k != "id"}, sort_keys=True)
    return s["type"] + ":" + hashlib.sha256(key.encode()).hexdigest()[:8]


def op_bind(twin, source_type=None, root=None, path=None, **kw):
    """Bind one more source to an existing parent's substrate."""
    slug = _slug(twin)
    man = _read_manifest(slug)
    if not man.get("parent"):
        return (f"Twin '{slug}' has no designated parent yet. "
                f"Run action='designate' first.")
    if source_type not in HARVESTERS:
        return (f"Unknown source_type {source_type!r}.\nRegistered: "
                + ", ".join(sorted(HARVESTERS)))
    src = {"type": source_type}
    if root:
        src["root"] = root
    if path:
        src["path"] = path
    for k, v in kw.items():
        if k in ("globs", "exts", "since", "max_repos", "limit_files",
                 "ts_column", "glob", "kind", "max_bytes"):
            src[k] = v
    src["id"] = _sid(src)
    sources = man["substrate"]["sources"]
    if any(x.get("id") == src["id"] for x in sources):
        return f"That exact source is already bound to '{slug}'."
    sources.append(src)
    _write_manifest(slug, man)
    return (f"Bound {source_type} -> {src.get('root') or src.get('path')} to '{slug}'. "
            f"{len(sources)} sources total. Harvest to index it.")


def op_harvest(twin, source_type=None, limit_files=None, **_):
    slug = _slug(twin)
    man = _read_manifest(slug)
    sources = (man.get("substrate") or {}).get("sources") or []
    if not sources:
        return f"Twin '{slug}' has no bound sources. Designate a parent first."
    con = _connect(slug)
    total, report, t0 = 0, [], time.time()
    for src in sources:
        if source_type and src["type"] != source_type:
            continue
        fn = HARVESTERS.get(src["type"])
        if not fn:
            report.append(f"  ! {src['type']}: no harvester registered")
            continue
        src = dict(src)
        src["id"] = src.get("id") or _sid(src)
        if limit_files:
            src["limit_files"] = int(limit_files)
        batch = []

        def emit(ev, _b=batch):
            ev["text"] = _scrub(ev.get("text"))
            ev["title"] = _scrub(ev.get("title"))
            _b.append(ev)
            if len(_b) >= 2000:
                _flush(con, src, _b)

        try:
            n = fn(con, src, emit)
        except Exception as e:
            con.commit()
            report.append(f"  ! {src['type']}: {type(e).__name__}: {e}")
            continue
        _flush(con, src, batch)
        con.commit()
        total += n
        report.append(f"  + {src['type']:<20} {n:>7,} events")
    rows = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    con.close()
    dt = time.time() - t0
    return ("\n".join([f"Harvested substrate for '{slug}' in {dt:.1f}s:"] + report
                      + [f"  = {total:,} new  |  {rows:,} total events in store"]))


def _flush(con, src, batch):
    if not batch:
        return
    rows = []
    for ev in batch:
        dedup = hashlib.sha256(
            f"{src['id']}|{ev.get('ptr')}|{ev.get('ts')}|{(ev.get('text') or '')[:200]}"
            .encode()).hexdigest()
        rows.append((ev.get("ts"), src["id"], src["type"], ev.get("ref"),
                     ev.get("kind"), ev.get("title"), ev.get("text"),
                     ev.get("ptr"), json.dumps(ev.get("meta") or {}), dedup))
    con.executemany(
        "INSERT OR IGNORE INTO events(ts,source,source_type,ref,kind,title,text,ptr,meta,dedup)"
        " VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
    batch.clear()


def _fts_query(q):
    """Build a safe FTS5 MATCH expression from free text."""
    toks = re.findall(r"[A-Za-z0-9_]{2,}", q or "")
    if not toks:
        return None
    return " OR ".join(f'"{t}"' for t in toks)


def op_search(twin, query=None, limit=12, source_type=None, since=None,
              ref=None, **_):
    slug = _slug(twin)
    m = _fts_query(query)
    if not m:
        return "Give me a query with at least one word."
    con = _connect(slug)
    sql = ("SELECT e.ts,e.source_type,e.ref,e.kind,e.title,e.text,e.ptr,"
           " bm25(events_fts) AS rank"
           " FROM events_fts JOIN events e ON e.id=events_fts.rowid"
           " WHERE events_fts MATCH ?")
    args = [m]
    if source_type:
        sql += " AND e.source_type=?"; args.append(source_type)
    if since:
        sql += " AND e.ts>=?"; args.append(since)
    if ref:
        sql += " AND e.ref LIKE ?"; args.append(f"%{ref}%")
    sql += " ORDER BY rank LIMIT ?"
    args.append(int(limit))
    try:
        rows = con.execute(sql, args).fetchall()
    except sqlite3.OperationalError as e:
        con.close()
        return f"Query failed: {e}"
    con.close()
    if not rows:
        return f"Nothing in {slug}'s substrate matches {query!r}."
    out = [f"{len(rows)} hit(s) in {slug}'s substrate for {query!r}:", ""]
    for ts, st, ref_, kind, title, text, ptr, _r in rows:
        out.append(f"[{(ts or '?')[:19]}] {st}/{kind}  {ref_ or ''}")
        out.append(f"  {(title or '').strip()[:180]}")
        snip = re.sub(r"\s+", " ", (text or "")).strip()
        if len(snip) > 240:
            snip = snip[:240] + "..."
        if snip and snip[:120] != (title or "").strip()[:120]:
            out.append(f"  {snip}")
        out.append(f"  ptr: {ptr}")
        out.append("")
    out.append("Open any ptr with action='open' to read the original evidence.")
    return "\n".join(out)


def op_recall(twin, query=None, limit=8, **_):
    """'How was this handled before?' — the answer plus its evidence."""
    slug = _slug(twin)
    m = _fts_query(query)
    if not m:
        return "Give me something to recall."
    con = _connect(slug)
    rows = con.execute(
        "SELECT e.ts,e.source_type,e.ref,e.kind,e.title,e.text,e.ptr"
        " FROM events_fts JOIN events e ON e.id=events_fts.rowid"
        " WHERE events_fts MATCH ? ORDER BY bm25(events_fts) LIMIT ?",
        (m, int(limit) * 3)).fetchall()
    con.close()
    if not rows:
        return f"{slug}'s substrate has no record of {query!r}."
    by_ref = {}
    for r in rows:
        by_ref.setdefault(r[2] or "?", []).append(r)
    out = [f"What {slug}'s parent actually did about {query!r}:", ""]
    for ref_, group in list(by_ref.items())[:int(limit)]:
        span = sorted(x[0] or "" for x in group)
        out.append(f"### {ref_}   ({len(group)} events, {span[0][:10]} -> {span[-1][:10]})")
        for ts, st, _rf, kind, title, text, ptr in group[:3]:
            out.append(f"  [{(ts or '?')[:10]}] {kind}: {(title or '')[:150]}")
            out.append(f"     ptr: {ptr}")
        out.append("")
    return "\n".join(out)


def op_timeline(twin, since=None, until=None, ref=None, limit=40, **_):
    slug = _slug(twin)
    con = _connect(slug)
    sql = ("SELECT substr(ts,1,10) d, source_type, COUNT(*), "
           " MIN(title) FROM events WHERE ts IS NOT NULL")
    args = []
    if since:
        sql += " AND ts>=?"; args.append(since)
    if until:
        sql += " AND ts<=?"; args.append(until)
    if ref:
        sql += " AND ref LIKE ?"; args.append(f"%{ref}%")
    sql += " GROUP BY d, source_type ORDER BY d DESC LIMIT ?"
    args.append(int(limit))
    rows = con.execute(sql, args).fetchall()
    con.close()
    if not rows:
        return f"No timeline for '{slug}' in that window."
    out = [f"{slug} substrate timeline" + (f" (ref~{ref})" if ref else ""), ""]
    cur = None
    for d, st, c, sample in rows:
        if d != cur:
            out.append(f"{d}"); cur = d
        out.append(f"   {st:<20} {c:>6,}   {(sample or '')[:90]}")
    return "\n".join(out)


def op_status(twin=None, **_):
    if not twin:
        return op_list()
    slug = _slug(twin)
    man = _read_manifest(slug)
    if not man:
        return f"No twin '{slug}'. Use action='list' to see what exists."
    p = man.get("parent") or {}
    con = _connect(slug)
    total = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    per = con.execute("SELECT source_type, COUNT(*), MIN(ts), MAX(ts) FROM events"
                      " GROUP BY source_type ORDER BY 2 DESC").fetchall()
    refs = con.execute("SELECT ref, COUNT(*) c FROM events WHERE ref IS NOT NULL"
                       " GROUP BY ref ORDER BY c DESC LIMIT 8").fetchall()
    con.close()
    db = _twin_dir(slug) / "substrate.db"
    size = db.stat().st_size if db.exists() else 0
    out = [f"Twin: {man.get('display_name') or slug}   [schema {man.get('schema')}]"]
    if p:
        out.append(f"Parent: {p.get('display_name')}  "
                   f"[{p.get('nature')}/{p.get('class')}]  since {p.get('designated_utc','?')[:10]}")
        for a in p.get("address") or []:
            out.append(f"   address: {a.get('scheme')}://{a.get('value')}")
    else:
        out.append("Parent: NONE DESIGNATED — this twin has no subject.")
    if man.get("parent_rappid"):
        out.append(f"Lineage: descends from {man['parent_rappid'][:40]}...")
    out.append(f"Substrate: {total:,} events, {size/1e6:.1f} MB")
    for st, c, mn, mx in per:
        out.append(f"   {st:<20} {c:>8,}   {(mn or '?')[:10]} -> {(mx or '?')[:10]}")
    if refs:
        out.append("Most-recorded refs:")
        for r, c in refs:
            out.append(f"   {c:>7,}  {r}")
    return "\n".join(out)


def op_list(**_):
    root = _twins_root()
    if not root.exists():
        return "No twins on this device yet."
    out = ["Twins on this device:", ""]
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        man = _read_manifest(d.name)
        p = man.get("parent") or {}
        db = d / "substrate.db"
        n = 0
        if db.exists():
            try:
                c = sqlite3.connect(str(db))
                n = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                c.close()
            except Exception:
                pass
        if p:
            tag = f"{p.get('nature')}/{p.get('class')}: {p.get('display_name')}"
        else:
            tag = "no parent designated"
        out.append(f"  {d.name:<28} {tag}")
        out.append(f"  {'':<28} schema {man.get('schema','?')}, "
                   f"{n:,} substrate events")
    out.append("")
    out.append("Anything virtual or physical can be designated a parent.")
    return "\n".join(out)


def op_sources(**_):
    out = ["Registered substrate source types:", ""]
    doc = {
        "claude_transcripts": "Claude Code session JSONL (virtual: a person's work)",
        "prompt_history": "prompt stream — intent in the parent's own words",
        "git_estate": "commits across a root of repos, or one repo",
        "filesystem": "text files by glob — notes, docs, reports, inspections",
        "shell_history": "commands actually run",
        "csv_timeseries": "PHYSICAL: sensor/meter/inspection rows with a timestamp",
        "media": "PHYSICAL: photos/video/PDF of a place, device, vehicle, build",
        "jsonl": "generic JSONL with configurable field mapping",
    }
    for t in sorted(HARVESTERS):
        out.append(f"  {t:<20} {doc.get(t,'')}")
    out += ["", "Presets: " + ", ".join(sorted(PRESETS)),
            "", "A new parent class never needs an engine change — it needs a "
            "source type registered here."]
    return "\n".join(out)


def op_inspect(twin, **_):
    slug = _slug(twin)
    man = _read_manifest(slug)
    if not man:
        return f"No twin '{slug}'."
    return json.dumps(man, indent=2)


def op_open(ptr=None, context=6, **_):
    """Read the original evidence a ptr points at."""
    if not ptr:
        return "Give me a ptr from a search result."
    if "#" in ptr and ":" not in ptr.rsplit("#", 1)[-1]:
        repo, sha = ptr.rsplit("#", 1)
        try:
            return subprocess.run(["git", "-C", repo, "show", "--stat", sha],
                                  capture_output=True, text=True,
                                  timeout=30).stdout[:4000]
        except Exception as e:
            return f"Could not open {ptr}: {e}"
    fp, _, ln = ptr.rpartition(":")
    if not fp or not ln.isdigit():
        fp, ln = ptr, "1"
    if not os.path.exists(fp):
        return f"Gone from disk: {fp}"
    ln = int(ln)
    try:
        with open(fp, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as e:
        return f"Could not read {fp}: {e}"
    lo, hi = max(0, ln - 1), min(len(lines), ln - 1 + max(1, int(context)))
    chunk = "".join(lines[lo:hi])
    if fp.endswith(".jsonl"):
        try:
            d = json.loads(lines[ln - 1])
            body = _text_of((d.get("message") or {}).get("content"))
            if not body:
                # Not a transcript line (e.g. history.jsonl uses `display`).
                body = next((str(d[k]) for k in ("display", "text", "content",
                                                 "prompt", "summary")
                             if d.get(k)), "")
            if not body:
                body = json.dumps(d, indent=2)[:2000]
            hdr = " ".join(f"{k}={d[k]}" for k in ("type", "timestamp", "cwd",
                                                   "project", "sessionId")
                           if d.get(k))
            chunk = f"{hdr}\n\n{body}"
        except Exception:
            pass
    return f"--- {fp}:{ln}\n{_scrub(chunk)[:4000]}"


OPS = {"designate": op_designate, "bind": op_bind, "harvest": op_harvest,
       "search": op_search, "recall": op_recall, "timeline": op_timeline,
       "status": op_status, "list": op_list, "inspect": op_inspect,
       "sources": op_sources, "open": op_open}


# ── Agent surface ───────────────────────────────────────────────────────

class TwinSubstrateAgent(BasicAgent):
    def __init__(self):
        self.name = "TwinSubstrate"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"] + (
                " Actions: designate (make anything virtual or physical the parent "
                "of a twin), bind (add a source), harvest (index it), search, "
                "recall, timeline, status, list, sources, inspect, open."),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": list(ACTIONS),
                               "description": "What to do."},
                    "twin": {"type": "string",
                             "description": "Twin name, e.g. 'kody-workflow'."},
                    "parent_class": {"type": "string",
                                     "description": "OPEN vocabulary: person, place, "
                                     "repo, device, org, process, vehicle, document, "
                                     "system, or anything else."},
                    "parent_nature": {"type": "string",
                                      "enum": ["virtual", "physical", "hybrid"]},
                    "display_name": {"type": "string"},
                    "address": {"type": "string",
                                "description": "Where the parent lives: a path, URL, "
                                "geo coordinate, serial number."},
                    "preset": {"type": "string",
                               "description": "Starter source set: "
                               + ", ".join(sorted(PRESETS))},
                    "source_type": {"type": "string",
                                    "description": "For bind/harvest: "
                                    + ", ".join(sorted(HARVESTERS))},
                    "root": {"type": "string"},
                    "path": {"type": "string"},
                    "query": {"type": "string"},
                    "ref": {"type": "string"},
                    "since": {"type": "string"},
                    "until": {"type": "string"},
                    "ptr": {"type": "string"},
                    "limit": {"type": "integer"},
                    "note": {"type": "string"},
                },
                "required": ["action"],
            },
        }
        super().__init__()

    def perform(self, **kwargs):
        kwargs.pop("user_guid", None)
        action = (kwargs.pop("action", "") or "").strip().lower()
        fn = OPS.get(action)
        if not fn:
            return (f"Unknown action {action!r}. One of: {', '.join(ACTIONS)}")
        if action in ("designate", "bind", "harvest", "search", "recall",
                      "timeline", "inspect") and not kwargs.get("twin"):
            return f"action='{action}' needs a twin name."
        try:
            return fn(**kwargs)
        except TypeError as e:
            return f"Bad arguments for '{action}': {e}"
        except Exception as e:
            return f"{action} failed: {type(e).__name__}: {e}"


# ── CLI — bulk harvest outside a request timeout ────────────────────────

def _main(argv):
    if len(argv) < 2:
        print(__doc__)
        print("\nActions: " + ", ".join(ACTIONS))
        return 0
    action, rest = argv[1], argv[2:]
    fn = OPS.get(action)
    if not fn:
        print(f"Unknown action {action!r}. One of: {', '.join(ACTIONS)}")
        return 2
    kw = {}
    pos = []
    for a in rest:
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            kw[k] = v
        else:
            pos.append(a)
    if pos and "twin" not in kw and action not in ("open", "sources", "list"):
        kw["twin"] = pos[0]
        pos = pos[1:]
    if pos and action in ("search", "recall") and "query" not in kw:
        kw["query"] = " ".join(pos)
    if pos and action == "open" and "ptr" not in kw:
        kw["ptr"] = pos[0]
    print(fn(**kw))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
