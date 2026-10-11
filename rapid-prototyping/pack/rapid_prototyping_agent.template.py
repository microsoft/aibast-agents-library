"""Rapid Prototyping: the RAPP live guide for Solution Engineers, on your own Brainstem.

Downloading this one file and loading it into your Brainstem is your sign-off: it does nothing until
you put it there and ask. Everything it installs is written out in full at the bottom of this file,
as readable text, so what you review is exactly what runs.

Say "set up rapid prototyping" once, then "open the RAPP live guide". The guide walks you from a
discovery call to a working prototype, step by step, on this computer only.

What it does, only when you ask:
- setup: writes the rapid prototyping files (below) into ~/.brainstem-proto, beside the Brainstem,
  never inside it, and adds the `brainstem-proto` command. No download.
- guide: starts the guide on this computer only. A small server on 127.0.0.1 serves the guide page
  and answers nothing else: one-time pairing, closes itself after 45 idle minutes. No website can
  reach it.
- new: creates a prototype from an idea or a pasted transcript (use the sample, or content you're
  approved to process with your Brainstem's AI).
- status: what's installed and running.
- uninstall: removes ~/.brainstem-proto and the command; your prototypes are kept.

Turn it off on a computer with RAPID_PROTOTYPING_DISABLED=1. It stores no secrets and sends
nothing anywhere. The only network use is optional: fetching an AIBAST agent template you pick,
checked against the library's published fingerprint before it is used.
"""
import json
import os
import re
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/rapid-prototyping",
    "version": "0.2.0",
    "display_name": "Rapid Prototyping",
    "description": "The RAPP live guide for Solution Engineers: from a discovery call to a working prototype on your own Brainstem, on this computer only.",
    "author": "AIBAST",
    "tags": ["rapp", "prototyping", "guide", "solution-engineering"],
    "category": "productivity",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


def _home() -> Path:
    return Path(os.environ.get("PROTO_HOME", Path.home() / ".brainstem-proto"))


def _bin() -> Path:
    return Path(os.environ.get("PROTO_BIN", Path.home() / ".local" / "bin")) / "brainstem-proto"


def _python() -> str:
    venv = Path.home() / ".brainstem" / ("venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python")
    return str(venv) if venv.exists() else sys.executable


def _listening(port: int) -> bool:
    with socket.socket() as sk:
        sk.settimeout(0.3)
        return sk.connect_ex(("127.0.0.1", port)) == 0


def _is_guide(port: int) -> bool:
    """A running guide bridge (not just any program on that port)."""
    import urllib.request
    req = urllib.request.Request(f"http://127.0.0.1:{port}/hello", headers={"Sec-Fetch-Site": "same-origin"})
    try:
        with urllib.request.urlopen(req, timeout=1) as r:
            return json.loads(r.read()).get("bridge") is True
    except Exception:
        return False


class RapidPrototypingAgent(BasicAgent):
    def __init__(self):
        self.name = "RapidPrototyping"
        self.metadata = {
            "name": self.name,
            "description": (
                "RAPP rapid prototyping for Solution Engineers. Actions: 'setup' installs the guide's files on this "
                "computer (do once), 'guide' opens the live RAPP guide (served on this computer only), 'new' creates a "
                "prototype from an idea or a discovery-call transcript, 'status', 'uninstall'. Use when the user wants "
                "to prototype, open the RAPP guide, or turn a discovery call into a prototype."),
            "parameters": {"type": "object", "properties": {
                "action": {"type": "string", "enum": ["setup", "guide", "new", "status", "uninstall"]},
                "idea": {"type": "string", "description": "For 'new': what to prototype, in plain words."},
                "transcript": {"type": "string", "description": "For 'new': a discovery call transcript (text)."},
                "template": {"type": "string", "description": "For 'new': an AIBAST template name, e.g. claims-processing."},
            }, "required": ["action"]},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if os.environ.get("RAPID_PROTOTYPING_DISABLED"):
                return json.dumps({"ok": False, "error": "Rapid prototyping is turned off on this computer."})
            action = kwargs.get("action", "status")
            if action == "setup":
                return self._setup()
            if action == "guide":
                return self._guide()
            if action == "uninstall":
                return self._uninstall()
            if action == "new":
                return self._new(kwargs)
            return self._status()
        except Exception as e:  # a plain sentence for the chat, never a traceback
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})

    # ---------- setup: write the files below; no download ----------
    def _setup(self) -> str:
        home = _home()
        for rel, lines in PACK.items():
            dest = home / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("\n".join(lines))
        for script in [home / "brainstem-proto", *(home / "template" / "scripts").glob("*.sh")]:
            script.chmod(0o755)
        link = _bin()
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink():
            link.unlink()
        if not link.exists():
            link.symlink_to(home / "brainstem-proto")
        return json.dumps({"ok": True, "installed": str(home), "files": len(PACK), "downloaded": "nothing",
                           "next": "Say 'open the RAPP live guide' to start."})

    def _uninstall(self) -> str:
        import shutil
        home, link = _home(), _bin()
        if link.is_symlink() and Path(os.readlink(link)).resolve() == (home / "brainstem-proto").resolve():
            link.unlink()
        if (home / "brainstem-proto").exists():  # only remove a folder this agent created
            shutil.rmtree(home)
        return json.dumps({"ok": True, "removed": str(home), "kept": "your prototypes in ~/BrainstemPrototypes"})

    # ---------- guide: served on this computer only ----------
    def _guide(self) -> str:
        home = _home()
        if not (home / "bridge.py").exists():
            return json.dumps({"ok": False, "error": "Not set up yet. Say 'set up rapid prototyping' first."})
        port = os.environ.get("GUIDE_BRIDGE_PORT") or next(
            (str(p) for p in range(7090, 7100) if not _listening(p)), "7090")  # asking twice opens a second guide
        log = home / "guide-bridge.log"
        with open(log, "w") as out:
            subprocess.Popen([_python(), str(home / "bridge.py"), "--port", port, "--no-open"],
                             stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             env={**os.environ, "PROTO_HOME": str(home)}, start_new_session=True)
        for _ in range(30):
            m = re.search(r"Open: (\S+)", log.read_text() if log.exists() else "")
            if m:
                if not os.environ.get("PROTO_NO_BROWSER"):
                    webbrowser.open(m.group(1))
                return json.dumps({"ok": True, "opened": m.group(1).split("#")[0], "served": "on this computer only",
                                   "note": "It closes itself after 45 idle minutes. Use the sample, or content you're approved to process."})
            time.sleep(0.5)
        return json.dumps({"ok": False, "error": f"The guide didn't start; see {log}"})

    # ---------- new: a prototype from an idea or a transcript ----------
    def _new(self, kw: dict) -> str:
        home = _home()
        if not (home / "brainstem-proto").exists():
            return json.dumps({"ok": False, "error": "Not set up yet. Say 'set up rapid prototyping' first."})
        args, tfile = ["new"], None
        if kw.get("template"):
            args += ["--template", str(kw["template"])]
        if kw.get("transcript"):
            tfile = home / "guide-inbox" / "chat-transcript.txt"
            tfile.parent.mkdir(parents=True, exist_ok=True)
            tfile.write_text(str(kw["transcript"]))
            args += ["--transcript", str(tfile)]
        if str(kw.get("idea") or "").strip():
            args.append(str(kw["idea"]).strip())
        if len(args) == 1:
            return json.dumps({"ok": False, "error": "Tell me the idea, or paste the discovery call transcript."})
        run = subprocess.run([str(home / "brainstem-proto")] + args, capture_output=True, text=True, timeout=600,
                             env={**os.environ, "PROTO_NO_EDITOR": "1", "PROTO_HOME": str(home)})
        if tfile:
            tfile.unlink(missing_ok=True)
        m = re.search(r"Created (.+)", run.stdout)
        app = re.search(r"Started: (\S+)", run.stdout)
        return json.dumps({"ok": bool(m), "folder": m.group(1).strip() if m else None, "app": app.group(1) if app else None,
                           "check": [ln for ln in run.stdout.splitlines() if ln[:1] in ("✓", "✗")],
                           "next": "Open the folder in your AI tool and paste FIRST-PROMPT.md.",
                           "error": None if m else (run.stdout + run.stderr)[-400:]})

    def _status(self) -> str:
        return json.dumps({"ok": True, "installed": (_home() / "brainstem-proto").exists(), "home": str(_home()),
                           "guides_running_on": [p for p in range(7090, 7100) if _listening(p) and _is_guide(p)],
                           "files_in_this_agent": len(PACK)})


# ---------------------------------------------------------------------------------------------------
# The files `setup` writes, in full, as readable lines (path relative to ~/.brainstem-proto).
# Generated from the rapid prototyping pack by pack/build_agent.py. Nothing else is installed.
# ---------------------------------------------------------------------------------------------------
PACK = {}  # filled in by pack/build_agent.py
