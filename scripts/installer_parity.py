#!/usr/bin/env python3
"""Installer parity: run a Brainstem one-liner on a clean machine, capture what
it does, and compare this repository's installer with the Grail's.

The rule this tool enforces: this repository's one-liner behaves like the
Grail's, except for the differences named in ALLOWED below. Each allowed
difference has an id that must also appear in rapp/KERNEL-DRIFT.md, so a new
difference cannot ship without being written down first.

Subcommands
    capture   run a one-liner twice (first run, second run) and save a capture
    compare   compare a Grail capture with this repository's capture
    ledger    check every allowed id is recorded in the drift ledger
    moved     report whether the Grail installers changed since the pinned commit

Standard library only. Works on macOS and Windows runners.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

def _grail_repo() -> str:
    """Where kernel updates come from: one setting, the species contract's source.repo.
    Point it at a company-owned copy of the Grail and every tool follows (GRAIL_SOURCE_REPO overrides)."""
    import json as _json, os as _os
    if _os.environ.get("GRAIL_SOURCE_REPO"):
        return _os.environ["GRAIL_SOURCE_REPO"]
    try:
        contract = Path(__file__).resolve().parents[1] / "rapp" / "GRAIL-SPECIES.json"
        return _json.loads(contract.read_text())["source"]["repo"]
    except (OSError, KeyError, ValueError):
        return "kody-w/rapp-installer"


GRAIL_REPO = _grail_repo()
HEALTH = "http://127.0.0.1:7071/health"
VERSION = "http://127.0.0.1:7071/version"
FIRST_RUN_CAP = 1500  # seconds; the sign-in code step alone waits about five minutes
SECOND_RUN_CAP = 480
RUNTIME = "src/rapp_brainstem/"
MAX_SRC_KIB = 25000  # same ceiling tests/preflight_public_installers.sh uses

# --------------------------------------------------------------------- allowed
#
# Every way this repository's one-liner may differ from the Grail's. Anything a
# comparison finds that is not matched here is a failure. `status` is "kept"
# (deliberate) or "open" (seen, not yet decided; still recorded so it is visible).

ALLOWED = [
    {
        "id": "light-download",
        "status": "kept",
        "why": "This repository is far larger than the Grail, so the installer downloads only the runtime folder.",
        "ours_lines": [
            r"^Fresh install .* cloning repository",
            r"^Downloading only the Brainstem runtime",
            r"^Cloning into ",
            r"^Limiting the install source to the Brainstem runtime",
            r"^Solution bundles excluded from installer updates",
        ],
        "grail_lines": [r"^Cloning repository", r"^Fresh install .* cloning repository"],
    },
    {
        "id": "progress-notes",
        "status": "kept",
        "why": "Long steps say what they are doing so a slow machine does not look frozen.",
        "ours_lines": [
            r"^\[\.\.\] ",
            r"^Creating Python virtual environment",
            r"^Using Python [\d.#]+ for the virtual environment",
            r"^Installing Python packages",
            r"^This can take several minutes",
            r"^Open http://localhost:7071 to chat",
            r"^Next time, just type: brainstem",
        ],
        "grail_lines": [r"^Creating virtual environment"],
    },
    {
        "id": "extra-agent",
        "status": "kept",
        "why": "This distribution ships one extra agent, LearnNew, and its test.",
        "agents": ["LearnNew"],
        "files": ["agents/rar_rapp_learn_new_agent.py", "tests/test_learn_new_agent.py"],
        "ours_lines": [r"^\[brainstem\] Agent loaded: LearnNew"],
    },
    {
        "id": "mouse-terminal",
        "status": "kept",
        "why": "A terminal screen for machines with no browser; shipped as one extra file.",
        "files": ["tui.py"],
        "ours_lines": [r"^No GUI browser detected", r"^Mouse terminal UI "],
    },
    {
        "id": "downstream-version",
        "status": "kept",
        "why": "The kernel version may be a downstream release ahead of the pinned Grail.",
        "version": True,
    },
    {
        "id": "second-run-keeps-server",
        "status": "open",
        "why": "On a second run the Grail stops the running Brainstem and starts it again; ours leaves a healthy, current one running.",
        "ours_lines": [
            r"^Your Brainstem is already running",
            r"^Restarting your Brainstem",
            r"^Picked up the latest Brainstem changes",
        ],
        "grail_lines": [
            r"^Stopping existing server",
            r"^Starting RAPP Brainstem",
            r"^RAPP Brainstem v# starting on",
            r"^\[brainstem\] Agent loaded: ",
        ],
        "second_run_only": True,
    },
    {
        "id": "version-check-fallback",
        "status": "kept",
        "why": "If the version lookup fails, ours says so and takes the full install path, which repeats first-run lines.",
        "ours_lines": [
            r"^\[!\] Could not check remote version",
            r"^Could not check remote version",
            r"^Local: +v#",
            r"^Remote: +v#",
            r"^Installing RAPP Brainstem",
            r"^Source code ready",
            r"^Installing dependencies",
            r"^Dependencies installed",
            r"^RAPP Brainstem v# installed",
            r"^Already up to date",
        ],
        "grail_lines": [r"^Dependencies verified"],
        "second_run_only": True,
    },
]

# Lines that are not installer steps: package manager chatter, download
# counters, the server's own log, and values that differ on every run.
NOISE = [
    r"^(Collecting|Downloading|Using cached|Requirement already|Installing collected|Successfully (installed|uninstalled)|Uninstalling) ",
    r"^(Attempting uninstall|Found existing installation)",
    r"^(remote:|Receiving objects|Resolving deltas|Updating files|Filtering content|Unpacking objects)",
    r"^[-=+| ]*$",
    r"Your code:",
    r"\"(GET|POST) /",
    r"^\* ",
    r"^WARNING: This is a development server",
    r"^Press CTRL\+C",
    r"^\[brainstem\] (?!Agent loaded)",
    r"^(Soul|Agents|Model|Voice|Auth|LAN): ",
    r"^[\d.]+/[\d.]+ [kM]B",
    r"^\[notice\]",
    r"^(Local|Remote) version: ",
]

STATE_FILE = re.compile(r"(^|/)(\.[^/]+|__pycache__/.*|[^/]+\.pyc|voice\.zip)$")
ANSI = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")


# --------------------------------------------------------------------- capture


def _get(url: str, timeout: float = 4.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except Exception:
        return None


def _installer_command(url: str | None, file: str | None) -> list[str]:
    windows = platform.system() == "Windows"
    if windows:
        body = f"irm {url} | iex" if url else f"& ([scriptblock]::Create((Get-Content -Raw '{file}')))"
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", body]
    body = f"curl -fsSL {url} | bash" if url else f"bash '{file}'"
    return ["bash", "-c", body]


def _tree(home: Path) -> list[str]:
    root = home / ".brainstem"
    out: list[str] = []
    if not root.is_dir():
        return out
    skip = {"venv", ".git", "__pycache__", "node_modules"}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip]
        for name in files:
            out.append((Path(base) / name).relative_to(root).as_posix())
    return sorted(out)


def _kib(path: Path) -> int:
    total = 0
    for base, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(base) / name).stat().st_size
            except OSError:
                pass
    return total // 1024


def _snapshot(out: Path, label: str, home: Path, state: str, seconds: int, download_failures: int = 0) -> None:
    src = home / ".brainstem" / "src"
    raw = (out / f"{label}.raw").read_bytes() if (out / f"{label}.raw").exists() else b""
    (out / f"{label}.log").write_text(ANSI.sub("", raw.decode("utf-8", "replace")).replace("\r", "\n"), encoding="utf-8")
    (out / f"{label}.tree.txt").write_text("\n".join(_tree(home)) + "\n", encoding="utf-8")
    beside = sorted(p.name for p in src.iterdir() if p.name not in (".git", "rapp_brainstem")) if src.is_dir() else []
    meta = {
        "state": state,
        "seconds": seconds,
        "download_failures": download_failures,
        "health": _get(HEALTH),
        "version": _get(VERSION),
        "src_kib": _kib(src) if src.is_dir() else None,
        "beside_runtime": beside,
    }
    (out / f"{label}.meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"{label}: {state} after {seconds}s; health={'yes' if meta['health'] else 'no'}; "
          f"files={len(_tree(home))}; beside runtime={len(beside)}; src={meta['src_kib']} KiB; "
          f"link failures={download_failures}", flush=True)


def _run(out: Path, label: str, cmd: list[str], home: Path, cap: int, until_health: bool) -> None:
    """Run the one-liner. If the link itself fails (the shell exits at once
    without the installer ever starting), wait and try again, and count it."""
    failures = 0
    while True:
        state, seconds = _run_once(out, label, cmd, cap, until_health)
        raw = (out / f"{label}.raw").read_bytes()
        started = b"Brainstem" in raw and b"Checking" in raw
        if started or failures >= 4 or not state.startswith("exited") or state == "exited 0":
            break
        failures += 1
        (out / f"{label}.download-fail-{failures}.txt").write_bytes(raw)
        print(f"{label}: the one-liner did not download (try {failures}); waiting 30s", flush=True)
        time.sleep(30)
    _snapshot(out, label, home, state, seconds, failures)


def _run_once(out: Path, label: str, cmd: list[str], cap: int, until_health: bool) -> tuple[str, int]:
    start = time.time()
    with open(out / f"{label}.raw", "wb") as sink:
        proc = subprocess.Popen(cmd, stdout=sink, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        state = "timeout"
        while time.time() - start < cap:
            time.sleep(5)
            code = proc.poll()
            if code is not None:
                state = f"exited {code}"
                break
            if until_health and _get(HEALTH) is not None:
                time.sleep(20)
                state = "serving"
                break
        else:
            state = "still running at the cap"
    return state, int(time.time() - start)


def grail_one_liner_url() -> str:
    """The Grail's own published one-liner for this system, as its README gives it."""
    owner, name = GRAIL_REPO.split("/")
    if platform.system() == "Windows":
        return f"https://raw.githubusercontent.com/{owner}/{name}/main/install.ps1"
    return f"https://{owner}.github.io/{name}/install.sh"


def capture(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    home = Path.home()
    if args.grail:
        args.url = grail_one_liner_url()
    cmd = _installer_command(args.url, args.file)
    source = args.url or args.file
    data = urllib.request.urlopen(args.url, timeout=60).read() if args.url else Path(args.file).read_bytes()
    (out / "installer.json").write_text(json.dumps({
        "source": source, "sha256": hashlib.sha256(data).hexdigest(), "os": platform.system()}, indent=2) + "\n")
    _run(out, "run1", cmd, home, FIRST_RUN_CAP, until_health=True)
    _run(out, "run2", cmd, home, SECOND_RUN_CAP, until_health=False)
    return 0


# --------------------------------------------------------------------- compare


def steps(log_text: str) -> list[str]:
    """The installer's own step lines, in order, with run-specific values removed."""
    out: list[str] = []
    noise = [re.compile(p) for p in NOISE]
    for line in ANSI.sub("", log_text).replace("\r", "\n").splitlines():
        line = line.encode("ascii", "ignore").decode().strip()
        line = re.sub(r"^\?+\s*", "", line)                      # glyphs a console could not print
        line = re.sub(r"\s+-\s+|\s{2,}", " ", line)               # a dash one console prints and another drops
        line = re.sub(r"^\[(OK|!|x|X)\]\s*", "", line).strip()   # status marks; the wording is what is compared
        if not line or any(n.search(line) for n in noise):
            continue
        line = re.sub(r"\d+(\.\d+)+[\w.-]*", "#", line)          # versions
        line = re.sub(r"\(PID \d+\)", "(PID #)", line)
        line = re.sub(r"(/Users/|C:\\Users\\)\S+", "<path>", line)
        if line not in out:
            out.append(line)
    return out


def _read(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig", "replace").replace("\x00", "") if path.exists() else ""


def _meta(d: Path, label: str) -> dict:
    p = d / f"{label}.meta.json"
    if p.exists():
        return json.loads(_read(p))
    # Captures made before meta.json existed keep health and state in separate files.
    health = None
    try:
        health = json.loads(_read(d / f"{label}.health.json"))
    except Exception:
        pass
    return {"state": _read(d / f"{label}.state.txt").strip(), "health": health, "src_kib": None, "beside_runtime": None}


def _runtime_files(d: Path, label: str) -> set[str]:
    out = set()
    for line in _read(d / f"{label}.tree.txt").splitlines():
        line = line.strip().lstrip("./")
        if line.startswith(RUNTIME):
            rel = line[len(RUNTIME):]
            if not STATE_FILE.search(rel):
                out.add(rel)
    return out


def _allowed(line: str, side: str, second: bool) -> str | None:
    for entry in ALLOWED:
        if entry.get("second_run_only") and not second:
            continue
        for pattern in entry.get(f"{side}_lines", []):
            if re.search(pattern, line):
                return entry["id"]
    return None


def compare_dirs(grail: Path, ours: Path) -> dict:
    problems: list[str] = []
    used: set[str] = set()
    notes: list[str] = []

    for label in ("run1", "run2"):
        second = label == "run2"
        gm, om = _meta(grail, label), _meta(ours, label)
        for who, m in (("the Grail's", gm), ("this repository's", om)):
            if m.get("download_failures"):
                notes.append(f"{label}: {who} one-liner link failed {m['download_failures']} time(s) before it downloaded")
        if not _read(ours / f"{label}.log").strip():
            problems.append(f"{label}: this repository's capture is empty")
            continue
        if not _read(grail / f"{label}.log").strip():
            notes.append(f"{label}: no Grail capture to compare against (not compared)")
            continue

        gs, os_ = steps(_read(grail / f"{label}.log")), steps(_read(ours / f"{label}.log"))
        for line in [l for l in os_ if l not in gs]:
            hit = _allowed(line, "ours", second)
            used.add(hit) if hit else problems.append(f"{label}: only ours shows: {line}")
        for line in [l for l in gs if l not in os_]:
            hit = _allowed(line, "grail", second)
            used.add(hit) if hit else problems.append(f"{label}: only the Grail shows: {line}")

        gh, oh = gm.get("health"), om.get("health")
        if gh and not oh:
            problems.append(f"{label}: the Grail's Brainstem answered and ours did not")
        if gh and oh:
            if set(gh) != set(oh):
                problems.append(f"{label}: /health fields differ: {sorted(set(gh) ^ set(oh))}")
            if gh.get("status") != oh.get("status"):
                problems.append(f"{label}: /health status differs: Grail {gh.get('status')} / ours {oh.get('status')}")
            extra = set(oh.get("agents") or []) - set(gh.get("agents") or [])
            missing = set(gh.get("agents") or []) - set(oh.get("agents") or [])
            ok_agents = {a for e in ALLOWED for a in e.get("agents", [])}
            if missing:
                problems.append(f"{label}: ours is missing agents the Grail loads: {sorted(missing)}")
            if extra - ok_agents:
                problems.append(f"{label}: ours loads agents that are not listed: {sorted(extra - ok_agents)}")
            if extra:
                used.add("extra-agent")
            if gh.get("version") != oh.get("version"):
                used.add("downstream-version")
                notes.append(f"{label}: kernel version Grail {gh.get('version')} / ours {oh.get('version')}")

        gf, of = _runtime_files(grail, label), _runtime_files(ours, label)
        ok_files = {f: e["id"] for e in ALLOWED for f in e.get("files", [])}
        for f in sorted(gf - of):
            problems.append(f"{label}: runtime file only in the Grail: {f}")
        for f in sorted(of - gf):
            used.add(ok_files[f]) if f in ok_files else problems.append(f"{label}: runtime file only in ours: {f}")

        # The size line: ours keeps nothing beside the runtime folder.
        beside = om.get("beside_runtime")
        if beside is None:
            beside = sorted({l.strip().lstrip("./").split("/")[1] for l in _read(ours / f"{label}.tree.txt").splitlines()
                             if l.strip().lstrip("./").startswith("src/") and not l.strip().lstrip("./").startswith(RUNTIME)})
        if beside:
            problems.append(f"{label}: ours keeps {len(beside)} item(s) beside the runtime folder, e.g. {beside[:4]}")
        if om.get("src_kib") is not None and om["src_kib"] > MAX_SRC_KIB:
            problems.append(f"{label}: ours install source is {om['src_kib']} KiB, over the {MAX_SRC_KIB} KiB ceiling")

    return {"problems": problems, "allowed_used": sorted(used), "notes": notes}


def compare(args) -> int:
    result = compare_dirs(Path(args.grail), Path(args.ours))
    name = args.name or "comparison"
    print(f"## Installer parity: {name}\n")
    for n in result["notes"]:
        print(f"- note: {n}")
    status = {e["id"]: e["status"] for e in ALLOWED}
    for i in result["allowed_used"]:
        print(f"- allowed difference seen: `{i}` ({status[i]})")
    if result["problems"]:
        print(f"\n**{len(result['problems'])} difference(s) not on the allowed list:**\n")
        for p in result["problems"]:
            print(f"- {p}")
        return 1
    print("\nNo difference outside the allowed list.")
    return 0


# ---------------------------------------------------------------- ledger, moved


def ledger(args) -> int:
    text = Path(args.ledger).read_text(encoding="utf-8")
    missing = [e["id"] for e in ALLOWED if f"`{e['id']}`" not in text]
    if missing:
        print("Allowed differences not recorded in the drift ledger: " + ", ".join(missing))
        return 1
    print(f"{len(ALLOWED)} of {len(ALLOWED)} allowed differences are recorded in {args.ledger}")
    return 0


def moved(args) -> int:
    text = Path(args.ledger).read_text(encoding="utf-8")
    pin = re.search(r"Pinned Grail: `[^@`]+@([0-9a-f]{7,40})`", text)
    if not pin:
        print("No pinned Grail commit found in the drift ledger")
        return 2
    changed = []
    for name in ("install.sh", "install.ps1", "install.cmd", "install.command"):
        def fetch(ref: str) -> bytes | None:
            try:
                return urllib.request.urlopen(f"https://raw.githubusercontent.com/{GRAIL_REPO}/{ref}/{name}", timeout=60).read()
            except Exception:
                return None
        pinned, head = fetch(pin.group(1)), fetch("main")
        if pinned is None or head is None:
            print(f"could not read {name} (not compared)")
        elif pinned != head:
            changed.append(name)
    if changed:
        print(f"Grail installers changed since the pinned commit {pin.group(1)}: {', '.join(changed)}")
        return 1
    print(f"Grail installers are unchanged since the pinned commit {pin.group(1)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    src = c.add_mutually_exclusive_group(required=True)
    src.add_argument("--url")
    src.add_argument("--file")
    src.add_argument("--grail", action="store_true", help="run the Grail's own published one-liner")
    c.add_argument("--out", required=True)
    c.set_defaults(fn=capture)
    m = sub.add_parser("compare")
    m.add_argument("grail")
    m.add_argument("ours")
    m.add_argument("--name")
    m.set_defaults(fn=compare)
    l = sub.add_parser("ledger")
    l.add_argument("--ledger", default="rapp/KERNEL-DRIFT.md")
    l.set_defaults(fn=ledger)
    v = sub.add_parser("moved")
    v.add_argument("--ledger", default="rapp/KERNEL-DRIFT.md")
    v.set_defaults(fn=moved)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
