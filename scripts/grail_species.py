#!/usr/bin/env python3
"""Grail species shape: compute, fetch, and diff the Brainstem kernel contract.

The AIBAST Agents Library vendors the RAPP Brainstem kernel in ``rapp_brainstem/``.
Kernel updates flow down from the Grail (``kody-w/rapp-installer``), but the
vendored copy is allowed to grow on its own.  This tool captures the parts of
the kernel that must stay identical for the two to remain the same species and
to layer over each other on one machine:

* every Flask route the Grail exposes
* the ``BasicAgent`` public interface
* the agent discovery rule (``*_agent.py``, flat, ``experimental/`` excluded)
* the ``sys.modules`` import shims
* the default port and the ``/chat`` response field
* the install layout (``~/.brainstem``, ``venv/``, ``src/rapp_brainstem``)

Additions on the vendored side (new routes, env keys, files) are allowed.
Removals or changes to the items above are a species break.

Usage::

    python scripts/grail_species.py shape rapp_brainstem --installer install.sh --json
    python scripts/grail_species.py fetch-grail /tmp/grail [--ref main]
    python scripts/grail_species.py diff rapp/GRAIL-SPECIES.json vendored.json

Standard library only.
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

GRAIL_REPO = "kody-w/rapp-installer"
KERNEL_DIR = "rapp_brainstem"
INSTALLER = "install.sh"
SHAPE_VERSION = 1

_ROUTE_RE = re.compile(
    r"""@app\.route\(\s*["']([^"']+)["']\s*(?:,\s*methods\s*=\s*\[([^\]]*)\])?""",
)
_ENV_RE = re.compile(
    r"""os\.(?:getenv|environ\.get)\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""
    r"""|os\.environ\[\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*\]"""
)
_SHIM_RE = re.compile(r"""sys\.modules\[\s*["']([A-Za-z0-9_.]+)["']\s*\]\s*=""")
_GLOB_RE = re.compile(r"""glob\.glob\(\s*os\.path\.join\(\s*AGENTS_PATH\s*,\s*["']([^"']+)["']\s*\)""")
_DISCOVERY_RE = re.compile(r"""pattern\s*=\s*os\.path\.join\(\s*AGENTS_PATH\s*,\s*["']([^"']+)["']\s*\)""")
_PORT_RE = re.compile(r"""os\.getenv\(\s*["']PORT["']\s*\)\s*or\s*["'](\d+)["']""")
_RESPONSE_RE = re.compile(r"""["'](response)["']\s*:\s*reply""")
_SH_VAR_RE = re.compile(r"""^\s*([A-Z_]+)=["']?([^"'\n]+)["']?\s*$""", re.M)


# --------------------------------------------------------------------------- shape


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _routes(source: str) -> list[str]:
    routes: set[str] = set()
    for path, methods in _ROUTE_RE.findall(source):
        verbs = re.findall(r"[A-Z]+", methods) or ["GET"]
        for verb in verbs:
            routes.add(f"{verb} {path}")
    return sorted(routes)


def _env_keys(source: str) -> list[str]:
    keys = {a or b for a, b in _ENV_RE.findall(source)}
    # helper wrappers such as ``def _env_enabled(name, ...): os.getenv(name)``
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return sorted(keys)
    wrappers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.args.args:
            first = node.args.args[0].arg
            body_src = ast.get_source_segment(source, node) or ""
            if re.search(rf"os\.(?:getenv|environ\.get)\(\s*{first}\b", body_src):
                wrappers.add(node.name)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in wrappers
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            keys.add(node.args[0].value)
    return sorted(keys)


def _basic_agent(kernel: Path) -> dict:
    candidates = [kernel / "agents" / "basic_agent.py", kernel / "basic_agent.py"]
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        return {"file": None, "class": None, "methods": {}}
    tree = ast.parse(_read(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "BasicAgent":
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [a.arg for a in item.args.args]
                    if item.args.vararg:
                        args.append("*" + item.args.vararg.arg)
                    if item.args.kwarg:
                        args.append("**" + item.args.kwarg.arg)
                    methods[item.name] = args
            return {
                "file": str(path.relative_to(kernel)),
                "class": node.name,
                "methods": methods,
                "has_metadata": "metadata" in _read(path),
                "has_perform": "perform" in methods,
            }
    return {"file": str(path.relative_to(kernel)), "class": None, "methods": {}}


def _discovery(source: str) -> dict:
    """Agent discovery rule: the glob assigned to ``pattern`` under AGENTS_PATH."""
    found = _DISCOVERY_RE.findall(source)
    agent_glob = next((g for g in found if g.endswith("_agent.py")), found[0] if found else None)
    flat = bool(agent_glob) and "**" not in agent_glob and "/" not in agent_glob
    return {
        "glob": agent_glob,
        "flat": flat,
        # a flat glob never descends into subdirectories such as experimental/
        "subdirectories_excluded": flat,
        "listing_globs": sorted(set(_GLOB_RE.findall(source))),
    }


def _inventory(kernel: Path) -> list[str]:
    names: list[str] = []
    for path in sorted(kernel.rglob("*")):
        rel = path.relative_to(kernel)
        parts = rel.parts
        if any(p in {"__pycache__", "tests", ".git"} for p in parts):
            continue
        if rel.name.startswith(".env"):
            continue
        if path.is_file():
            names.append(rel.as_posix())
    return names


def _install_layout(installer: Path | None) -> dict:
    if installer is None or not installer.exists():
        return {}
    source = _read(installer)
    vars_ = dict(_SH_VAR_RE.findall(source))
    layout = {
        "BRAINSTEM_HOME": vars_.get("BRAINSTEM_HOME"),
        "VENV_DIR": vars_.get("VENV_DIR"),
    }
    src_dirs = sorted(set(re.findall(r"\$BRAINSTEM_HOME/(src/rapp_brainstem)", source)))
    layout["SRC_DIR"] = "$BRAINSTEM_HOME/" + src_dirs[0] if src_dirs else None
    layout["AGENTS_DIR"] = (
        "$BRAINSTEM_HOME/src/rapp_brainstem/agents"
        if "$BRAINSTEM_HOME/src/rapp_brainstem/agents" in source
        else None
    )
    layout["overrides"] = sorted(
        set(re.findall(r"\$\{(BRAINSTEM_REPO_URL|BRAINSTEM_REPO_REF|BRAINSTEM_VERSION_URL)", source))
    )
    return layout


def compute_shape(kernel: Path, installer: Path | None = None) -> dict:
    brainstem = kernel / "brainstem.py"
    source = _read(brainstem)
    version_file = kernel / "VERSION"
    port = _PORT_RE.search(source)
    response = _RESPONSE_RE.search(source)
    return {
        "shape_version": SHAPE_VERSION,
        "kernel_version": _read(version_file).strip() if version_file.exists() else None,
        "routes": _routes(source),
        "basic_agent": _basic_agent(kernel),
        "discovery": _discovery(source),
        "env_keys": _env_keys(source),
        "default_port": int(port.group(1)) if port else None,
        "chat_response_field": response.group(1) if response else None,
        "shims": sorted(set(_SHIM_RE.findall(source))),
        "inventory": _inventory(kernel),
        "install_layout": _install_layout(installer),
    }


# --------------------------------------------------------------------------- fetch


def _http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "grail-species"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "grail-species"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def fetch_grail(outdir: Path, ref: str = "main", repo: str = GRAIL_REPO) -> dict:
    """Download ``rapp_brainstem/`` and ``install.sh`` from the Grail into outdir."""
    commit = _http_json(f"https://api.github.com/repos/{repo}/commits/{ref}")
    sha = commit["sha"]
    tree = _http_json(f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("Grail tree listing was truncated; cannot fetch reliably")
    wanted = [
        entry["path"]
        for entry in tree["tree"]
        if entry["type"] == "blob"
        and (entry["path"].startswith(KERNEL_DIR + "/") or entry["path"] == INSTALLER)
        and "__pycache__" not in entry["path"]
    ]
    outdir.mkdir(parents=True, exist_ok=True)
    for rel in wanted:
        target = outdir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            _http_bytes(f"https://raw.githubusercontent.com/{repo}/{sha}/{rel}")
        )
    source = {
        "repo": repo,
        "ref": ref,
        "commit": sha,
        "fetched_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
        "files": len(wanted),
    }
    (outdir / "SOURCE.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    return source


# ---------------------------------------------------------------------------- diff


def diff_shapes(grail: dict, vendored: dict) -> dict:
    """Return {"breaks": [...], "ahead": [...], "added": [...], "rows": [...]}."""
    breaks: list[str] = []
    ahead: list[str] = []
    added: list[str] = []
    rows: list[tuple[str, str, str]] = []

    def set_check(label: str, g: list, v: list, allow_add: bool = True):
        gs, vs = set(g), set(v)
        missing = sorted(gs - vs)
        extra = sorted(vs - gs)
        kept = len(gs & vs)
        rows.append((label, f"kept {kept}", f"added {len(extra)}, missing {len(missing)}"))
        for item in missing:
            breaks.append(f"{label}: missing {item}")
        for item in extra:
            if allow_add:
                added.append(f"{label}: added {item}")
            else:
                breaks.append(f"{label}: unexpected {item}")

    def eq_check(label: str, g, v):
        ok = g == v
        rows.append((label, "same" if ok else "DIFFERENT", "" if ok else f"grail={g!r} vendored={v!r}"))
        if not ok:
            breaks.append(f"{label}: grail={g!r} vendored={v!r}")

    set_check("routes", grail["routes"], vendored["routes"])
    gm, vm = grail["basic_agent"]["methods"], vendored["basic_agent"]["methods"]
    set_check("basic_agent.methods", list(gm), list(vm))
    for name, sig in gm.items():
        if name in vm and vm[name] != sig:
            breaks.append(f"basic_agent.{name} signature: grail={sig} vendored={vm[name]}")
            rows.append((f"basic_agent.{name}", "DIFFERENT", f"{sig} -> {vm[name]}"))
    eq_check("basic_agent.class", grail["basic_agent"]["class"], vendored["basic_agent"]["class"])
    eq_check("discovery", grail["discovery"], vendored["discovery"])
    set_check("shims", grail["shims"], vendored["shims"], allow_add=False)
    eq_check("default_port", grail["default_port"], vendored["default_port"])
    eq_check("chat_response_field", grail["chat_response_field"], vendored["chat_response_field"])
    set_check("env_keys", grail["env_keys"], vendored["env_keys"])
    set_check("inventory", grail["inventory"], vendored["inventory"])
    gl, vl = grail.get("install_layout") or {}, vendored.get("install_layout") or {}
    if gl and vl:
        for key in ("BRAINSTEM_HOME", "VENV_DIR", "SRC_DIR", "AGENTS_DIR"):
            eq_check(f"install_layout.{key}", gl.get(key), vl.get(key))
        # installer env overrides are additive: the vendored installer may accept more
        set_check("install_layout.overrides", gl.get("overrides") or [], vl.get("overrides") or [])
    if grail.get("kernel_version") != vendored.get("kernel_version"):
        ahead.append(
            f"kernel_version: grail={grail.get('kernel_version')} vendored={vendored.get('kernel_version')}"
        )
        rows.append(("kernel_version", "DIFFERENT", f"{grail.get('kernel_version')} -> {vendored.get('kernel_version')}"))
    else:
        rows.append(("kernel_version", "same", grail.get("kernel_version") or ""))

    # "ahead" = the Grail has things the vendored copy lacks; these are the
    # same items already recorded as breaks, restated for the live report.
    ahead.extend(b for b in breaks if ": missing " in b)
    return {"breaks": breaks, "ahead": ahead, "added": added, "rows": rows}


def render_table(result: dict) -> str:
    width = max(len(r[0]) for r in result["rows"]) + 2
    lines = [f"{'check'.ljust(width)}{'status'.ljust(12)}detail"]
    lines.append("-" * (width + 12 + 40))
    for label, status, detail in result["rows"]:
        lines.append(f"{label.ljust(width)}{status.ljust(12)}{detail}")
    if result["added"]:
        lines.append("")
        lines.append("Vendored additions (allowed):")
        lines.extend(f"  + {item}" for item in result["added"])
    if result["breaks"]:
        lines.append("")
        lines.append("SPECIES BREAK:")
        lines.extend(f"  ! {item}" for item in result["breaks"])
    else:
        lines.append("")
        lines.append("Same species: every Grail contract item is present in the vendored kernel.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------- main


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_shape = sub.add_parser("shape", help="compute the species shape of a kernel directory")
    p_shape.add_argument("kernel")
    p_shape.add_argument("--installer", default=None, help="install.sh to read layout constants from")
    p_shape.add_argument("--source", default=None, help="SOURCE.json written by fetch-grail to embed")
    p_shape.add_argument("--json", action="store_true", help="print JSON (default)")

    p_fetch = sub.add_parser("fetch-grail", help="download the Grail kernel + installer")
    p_fetch.add_argument("outdir")
    p_fetch.add_argument("--ref", default="main")
    p_fetch.add_argument("--repo", default=GRAIL_REPO)

    p_diff = sub.add_parser("diff", help="diff a Grail shape against a vendored shape")
    p_diff.add_argument("grail")
    p_diff.add_argument("vendored")

    args = parser.parse_args(argv)

    if args.cmd == "shape":
        kernel = Path(args.kernel)
        installer = Path(args.installer) if args.installer else None
        shape = compute_shape(kernel, installer)
        if args.source:
            shape["source"] = _load(args.source)
        print(json.dumps(shape, indent=2))
        return 0

    if args.cmd == "fetch-grail":
        source = fetch_grail(Path(args.outdir), ref=args.ref, repo=args.repo)
        print(json.dumps(source, indent=2))
        return 0

    if args.cmd == "diff":
        result = diff_shapes(_load(args.grail), _load(args.vendored))
        print(render_table(result))
        return 1 if result["breaks"] else 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
