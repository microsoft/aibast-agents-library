"""Build docs/any-ai/SKILL.md from docs/any-ai/kernel.py (the page carries the file and its fingerprint).

Ported from the RAPP Brainstem skill pattern: one plain page any AI reads once.
    python tools/build_any_ai_skill.py          write SKILL.md
    python tools/build_any_ai_skill.py --check  fail if SKILL.md is stale
"""
import hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "any-ai"
SITE = "https://microsoft.github.io/aibast-agents-library"

HEAD = '''---
name: "aibast-brainstem"
description: "Read once, then never again. Lets you use and build Brainstem agents from the AIBAST Agents Library: you keep an agents/ folder, load every agent file in it fresh each turn, bring agents from the library catalog by name, build and test new ones, and answer in a Brainstem's chat shape. Use when the person says Brainstem, RAPP, names a library agent, or hands you an agent.py."
license: "MIT"
compatibility: "Any AI that can write a file and run Python 3.9+. Nothing is installed."
metadata:
  rapp-skill: "0.6.0-aibast"
---

# Use and build Brainstem agents, from one page

This page is a seed. It carries one small file. That file brings what it needs, checks it, and writes a
standing note into your own always-on instructions. After that you never need this page again.

## Before you start: ask once

Tell the person, in plain words, and wait for a yes:

> This sets up a folder called `rapp/` here and adds a short note to this folder's instructions file, so I
> can use and build agents for you. Bringing an agent downloads it from the AIBAST Agents Library catalog,
> checks its fingerprint, and runs it on this device. Deleting the `rapp/agents` folder turns it all off
> again, as if it was never here. OK?

## Then do this, in order

1. Find a Python 3. Try `python3 --version`, then `python --version`, then `py -3 --version`. Agents are
   Python files, the same as in a Brainstem, so one of these must work. If none does, tell the person this
   needs Python and wait for a yes, then install it: Windows
   `winget install --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements --silent`;
   macOS `brew install python@3.11`; Debian or Ubuntu `sudo apt-get install -y python3`. Use a new shell
   afterwards so the command is found. If Python cannot be installed, stop and give the person
   {site}/docs/installer.html, whose one line installs Python and a whole Brainstem.
2. Choose the home folder. It is `rapp/` here, with one exception: if a `rapp` folder already exists and has
   no `kernel.py` in it, it belongs to something else. Never write into it. Use `rapp-skill/` instead, or if
   that name is taken too, the first of `rapp-skill-2/`, `rapp-skill-3/` and so on that does not exist yet.
   Read that name wherever this page says `rapp/`. If the home folder already has `kernel.py`, skip to step 4.
3. Write `rapp/kernel.py` from the block at the bottom of this page, with a script, never by retyping. The
   file is everything between the opening fence line (four backticks plus `python`) and the closing fence
   line (four backticks), ending in one newline, LF line endings. Its sha256 must be
   `{sha}`. If it is not, stop and say so.
   (The same file is also at {site}/docs/any-ai/kernel.py.)
4. Run it with the Python 3 that worked, naming the instructions file you yourself read at the start of
   every session: `<python> rapp/kernel.py stay <your file>`
   Your file is `CLAUDE.md` if you are Claude Code, `GEMINI.md` if you are Gemini, `AGENTS.md` if you are
   Copilot or Codex. If you do not know, leave it off. It writes the standing note into your file (made if
   missing) and into any of `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md` that
   already exist. With no name and none existing, it makes `AGENTS.md`.
5. Read the note it just wrote and follow it from now on, starting this turn: run the `tools` line once now.
6. Tell the person it is done, in one sentence, and offer one library agent to try, for example
   "Bring the account intelligence agent and give me an account overview." This page can be deleted.

## What you can do from then on

- **Use agents.** You see each agent's name, description and parameters. You pick one and fill in the
  parameters; the agent file does the work, so results repeat and can be checked.
- **Bring agents** from the library catalog by name (`kernel.py bring <name>`), fingerprint-checked.
- **Build agents.** Asked to build something, write one agent file and run `kernel.py ready`. It is tested
  with a real call first and handed to the person's Brainstem on this device only when the check passes.
- **Grow without touching the Brainstem itself:** a new need is an agent file, a sidecar that talks only
  over `/chat` and `/health`, or a distro.
- **Stuck?** Read the RAPP guide: {site}/docs/rapp-guide.html

## Later, if the person wants it reachable like a Brainstem

Other programs can talk to you on a Brainstem's address, in a Brainstem's shape (`/health`, `/chat`), on
this device only. Start the door with the command that runs you for one message, the message last:
`<python> rapp/kernel.py serve 7071 -- <your one-message command>`. Only on the person's ask.

<!-- file: rapp/kernel.py -->
````python
'''


def build():
    k = (DIR / "kernel.py").read_text()
    sha = hashlib.sha256(k.encode()).hexdigest()
    return HEAD.replace("{site}", SITE).replace("{sha}", sha) + k + "````\n<!-- end -->\n"


if __name__ == "__main__":
    out = build()
    if "--check" in sys.argv:
        ok = (DIR / "SKILL.md").read_text() == out
        print("SKILL.md up to date" if ok else "SKILL.md is stale: run python tools/build_any_ai_skill.py")
        sys.exit(0 if ok else 1)
    (DIR / "SKILL.md").write_text(out)
    print("wrote docs/any-ai/SKILL.md")
