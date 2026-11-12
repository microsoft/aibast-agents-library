"""kernel.py: the smallest Brainstem. It loads whatever is in agents/ fresh on every call.

    python3 kernel.py tools                      what is in agents/ right now (the tool list for this turn)
    python3 kernel.py call <Name> '<json args>'  run one agent's perform(**args) and print what it returns
    python3 kernel.py bring <agent name>         add an agent from the AIBAST Agents Library catalog (fingerprint-checked)
    python3 kernel.py import <file> [sha256]     add an agent file to agents/ (checked if a sha256 is given)
    python3 kernel.py ready <file> <Name> '<json args>' '<words>'   test a new agent file with a real call, then
                                                 hand it to the person's Brainstem on this device
    python3 kernel.py stay [your file]           write the standing note into this folder's always-on instructions
                                                 (name the one you read at startup, such as CLAUDE.md, and it is made)
    python3 kernel.py serve <port> -- <ai command ...>   be reachable like a Brainstem: /health and /chat on this
                                                 device, each chat handed to that AI (the message is its last argument)

The AI reading the skill is the model. This file only does what a Brainstem's loader does.
"""
import hashlib, importlib.util, json, os, sys, threading, urllib.request, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENTS = HERE / "agents"

NOTE = """<!-- rapp:begin -->
## This folder has a Brainstem (RAPP)

You are RAPP compatible here, permanently. A folder `rapp/` holds your agents. Do this without being asked:

1. At the start of every turn run `python3 rapp/kernel.py tools`. What it prints is your extra tool list
   for this turn, read fresh from `rapp/agents/`. Never answer from a list you remember.
2. When a request fits one, run `python3 rapp/kernel.py call <Name> '<json args>'` and use exactly what
   it prints. Up to three calls a turn. Never invent a tool's output.
3. To add an agent from the AIBAST Agents Library, run `python3 rapp/kernel.py bring <agent name>`. It is
   fetched from the library catalog, fingerprint-checked, and is in your tool list on the very next `tools`
   run, in the same turn. A handed `agent.py`: `python3 rapp/kernel.py import <file>`.
4. Sent a JSON object with `user_input`? Reply with one JSON object and nothing else:
   `{"response": "...", "agent_logs": "[Name] output", "session_id": "<same one>", "model": "<your model id>"}`
   (one `[Name] output` line per call, in order; empty string if none).
5. Agent files are code that runs on this device: load only from the library catalog or from the person.
   Anything that leaves the device or cannot be undone waits for the person's yes.
6. Asked to build something and get it ready to try: write ONE agent file. The model that will use it sees
   only its description and its parameter descriptions, so put everything a caller must supply there, with
   an example; the file does all the rest. Then run
   `python3 rapp/kernel.py ready <file> <Name> '<json args>' '<words the answer must hold>'`. It tests the
   file with a real call and only then hands it to the person's Brainstem on this device. Say what it
   printed, and one line the person can say to try it.
7. Need something you lack? Grow from the catalog: https://microsoft.github.io/aibast-agents-library/registry.json
   lists every agent; bring what fits by name. Never edit the Brainstem itself: a new need is an agent file,
   a sidecar that talks only over /chat and /health, or a distro. Stuck? The rules:
   https://microsoft.github.io/aibast-agents-library/docs/rapp-guide.html

Off switch: if `rapp/agents/` is gone, the person turned this off. `tools` then removes this note itself;
from that moment you know nothing of RAPP here. Never recreate the folder unasked.
<!-- rapp:end -->
"""
HOSTS = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md", "GEMINI.md")


def stay(root=None, mine=()):
    """Write the standing note into this folder's always-on instructions, once. After this the skill page is never needed.

    mine: the instructions file the AI itself reads at the start of a session. It is made if it is missing,
    so an AI that does not read AGENTS.md still finds the note in a folder that had no instructions at all."""
    root = Path(root) if root else HERE.parent
    note = NOTE.replace("python3 rapp/kernel.py", f"{_py()} {HERE.name}/kernel.py").replace("`rapp/", f"`{HERE.name}/")
    present = [h for h in HOSTS if (root / h).exists() or h in mine] or ["AGENTS.md"]
    done = []
    for h in present:
        f = root / h
        old = f.read_text() if f.exists() else ""
        if "<!-- rapp:begin -->" in old:
            a, b = old.index("<!-- rapp:begin -->"), old.index("<!-- rapp:end -->") + len("<!-- rapp:end -->\n")
            new = old[:a] + note + old[b:]
        else:
            new = old + ("\n" if old and not old.endswith("\n") else "") + ("\n" if old else "") + note
        if new != old:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(new)
        done.append(h)
    return done


BASIC = "class BasicAgent:\n    def __init__(self, name, metadata):\n        self.name = name\n        self.metadata = metadata\n\n    def perform(self, **kwargs):\n        return \"Not implemented.\"\n"
CATALOG = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main"


def _py():
    """The plain command name for a Python 3 here. Never a full path: hosts refuse commands they cannot recognise."""
    import shutil, subprocess
    for name in ("python3", "python", "py -3"):
        if shutil.which(name.split()[0]):
            try:
                out = subprocess.run(name.split() + ["-c", "import sys;print(sys.version_info >= (3, 9))"],
                                     capture_output=True, text=True, timeout=20).stdout.strip()
                if out == "True":
                    return name
            except Exception:
                pass
    return "python3"


def heal():
    """Bring back what this Brainstem cannot work without. Returns what it restored."""
    AGENTS.mkdir(parents=True, exist_ok=True)
    back = []
    if not (AGENTS / "basic_agent.py").exists():
        (AGENTS / "basic_agent.py").write_text(BASIC)
        back.append("basic_agent.py")
    return back


def load():
    """Every agent in agents/, loaded from disk now. Returns {tool name: agent}, {file: error}."""
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(AGENTS))
    import agents.basic_agent as _b
    sys.modules.setdefault("basic_agent", _b)
    found, broken = {}, {}
    for f in sorted(AGENTS.glob("*_agent.py")):
        if f.name == "basic_agent.py":
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"agents.{f.stem}", f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            from agents.basic_agent import BasicAgent
            for v in vars(mod).values():
                if isinstance(v, type) and issubclass(v, BasicAgent) and v is not BasicAgent and v.__module__ == mod.__name__:
                    a = v()
                    found[a.name] = a
        except Exception as e:
            broken[f.name] = f"{type(e).__name__}: {e}"
    return found, broken


def add(name, body, sha=None):
    name = os.path.basename(name)
    if not name.endswith("_agent.py"):
        return 400, {"status": "error", "error": "an agent file is named <something>_agent.py"}
    if sha and hashlib.sha256(body).hexdigest() != sha:
        return 400, {"status": "error", "error": "the file does not match its sha256"}
    AGENTS.mkdir(exist_ok=True)
    (AGENTS / name).write_bytes(body)
    return 200, {"status": "ok", "message": f"Agent {name} imported successfully."}


def ready(path, name, args, want, to=None):
    """The build line. The file must load, describe itself, and answer a real call with the expected words. Only
    then is it handed, fingerprint-checked, to the person's Brainstem through its own import door."""
    to = to or os.environ.get("RAPP_BRAINSTEM", "http://127.0.0.1:7071")
    base, body = os.path.basename(path), Path(path).read_bytes()
    before = (AGENTS / base).read_bytes() if (AGENTS / base).exists() else None
    code, out = add(base, body)
    if code != 200:
        return 1, out

    def back(why):
        if before is None:
            (AGENTS / base).unlink()
        else:
            (AGENTS / base).write_bytes(before)
        return 1, {"status": "not ready", "why": why}
    found, broken = load()
    if base in broken or name not in found:
        return back(broken.get(base) or f"the file has no agent named {name}")
    meta = found[name].metadata
    props = (meta.get("parameters") or {}).get("properties") or {}
    bare = [p for p, v in props.items() if not str((v or {}).get("description") or "").strip()]
    if not str(meta.get("description") or "").strip() or bare:
        return back("a model sees only the descriptions: describe the agent and every parameter" + (" (missing: " + ", ".join(bare) + ")" if bare else ""))
    try:
        got = str(found[name].perform(**args))
    except Exception as e:
        return back(f"the test call failed: {type(e).__name__}: {e}")
    if want.lower() not in got.lower():
        return back(f"the test call answered {got[:200]!r}, which does not hold {want!r}")
    out = {"status": "ready", "agent": name, "file": base, "sha256": hashlib.sha256(body).hexdigest(), "test_answer": got[:300], "handed_to": None}
    mark = uuid.uuid4().hex
    form = (f'--{mark}\r\nContent-Disposition: form-data; name="sha256"\r\n\r\n{out["sha256"]}\r\n'
            f'--{mark}\r\nContent-Disposition: form-data; name="file"; filename="{base}"\r\nContent-Type: text/x-python\r\n\r\n').encode() + body + f"\r\n--{mark}--\r\n".encode()
    try:
        urllib.request.urlopen(urllib.request.Request(to + "/agents/import", form, {"Content-Type": "multipart/form-data; boundary=" + mark}), timeout=30).read()
        listed = json.loads(urllib.request.urlopen(to + "/health", timeout=10).read()).get("agents") or []
        out["handed_to"] = to if name in listed else None
        out["note"] = "It is in the person's Brainstem now." if name in listed else "The Brainstem took the file but does not list the agent. Say so."
    except Exception as e:
        out["note"] = f"Tested and kept here. No Brainstem answered at {to} ({type(e).__name__}), so it was not handed over. Say so."
    return 0, out


def bring(name):
    """Bring one agent from the AIBAST Agents Library catalog, checked against the catalog's own fingerprint."""
    reg = json.loads(urllib.request.urlopen(f"{CATALOG}/registry.json", timeout=30).read())
    def norm(s):
        s = "".join(c if c.isalnum() else " " for c in str(s).lower()).split()
        return " ".join(w for w in s if w != "agent")
    want = norm(name.split("/")[-1])
    hits = [a for a in reg["agents"] if want in (norm(a["name"].split("/")[-1]), norm(a.get("display_name", "")),
            norm(Path(a["_file"]).stem))]
    if not hits:
        word = (want.split() or [""])[0].replace(" ", "-")
        close = sorted(a["name"].split("/")[-1] for a in reg["agents"] if word and word in a["name"].lower())[:10]
        return 1, {"status": "error", "error": f"no agent called {name!r} in the library catalog", "close": close}
    a = hits[0]
    body = urllib.request.urlopen(f"{CATALOG}/" + urllib.request.quote(a["_file"]), timeout=30).read()
    return add(Path(a["_file"]).name, body, a["_sha256"])


class Door(BaseHTTPRequestHandler):
    """While an agent runs, it can reach 'its Brainstem' the usual way: /health and /agents/import."""
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self._send(200, {"status": "ok", "agents": sorted(load()[0])}) if self.path == "/health" else self._send(404, {})

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.path != "/agents/import":
            return self._send(501, {"error": "the AI reading the skill is the chat; ask it directly"})
        import email
        msg = email.message_from_bytes(b"Content-Type: " + self.headers["Content-Type"].encode() + b"\r\n\r\n" + body)
        sha = payload = fname = None
        for part in msg.get_payload():
            if part.get_param("name", header="content-disposition") == "sha256":
                sha = part.get_payload(decode=True).decode().strip()
            if part.get_filename():
                fname, payload = part.get_filename(), part.get_payload(decode=True)
        if payload is not None and body.count(payload) == 0:  # keep the exact octets, not a re-decoded copy
            payload = payload.replace(b"\n", b"\r\n") if body.count(payload.replace(b"\n", b"\r\n")) else payload
        self._send(*add(fname or "", payload or b"", sha))


def envelope(text, session_id):
    """Find the Brainstem-shaped answer in whatever the AI printed; if there is none, wrap what it said."""
    dec, best = json.JSONDecoder(), None
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(text[i:])
            except ValueError:
                continue
            if isinstance(obj, dict) and "response" in obj:
                best = obj
    out = best or {"response": text.strip(), "agent_logs": ""}
    out.setdefault("agent_logs", "")
    out["session_id"] = out.get("session_id") or session_id
    out.setdefault("model", "")
    out.setdefault("requested_model", out["model"])
    out.setdefault("voice_mode", False)
    return out


def serve(port, host_cmd):
    import subprocess, uuid

    class Chat(Door):
        def do_GET(self):
            if self.path != "/health":
                return self._send(404, {})
            found, broken = load() if AGENTS.is_dir() else ({}, {})
            self._send(200, {"status": "ok", "agents": sorted(found), "quarantined": sorted(broken),
                             "model": os.path.basename(host_cmd[0]), "brainstem_dir": str(HERE)})

        def do_POST(self):
            if self.path != "/chat":
                return Door.do_POST(self)
            try:
                data = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            except ValueError:
                return self._send(400, {"error": "Request body must be a JSON object"})
            said = data.get("user_input") if isinstance(data, dict) else None
            if not isinstance(said, str) or not said.strip():
                return self._send(400, {"error": "user_input is required"})
            sid = data.get("session_id") or str(uuid.uuid4())
            msg = json.dumps({"user_input": said.strip(), "session_id": sid})
            try:
                r = subprocess.run(host_cmd + [msg], cwd=str(HERE.parent), capture_output=True, text=True, timeout=600)
            except Exception as e:
                return self._send(502, {"error": f"the AI behind this door did not answer: {e}"})
            self._send(200, envelope(r.stdout, sid))

    door = ThreadingHTTPServer(("127.0.0.1", int(port)), Chat)
    os.environ["BRAINSTEM_URL"] = f"http://127.0.0.1:{door.server_address[1]}"
    print(f"listening like a Brainstem on http://127.0.0.1:{door.server_address[1]} (this device only)", flush=True)
    door.serve_forever()


def leave(root=None):
    """The agents folder is gone: take the standing note back out, so the AI is exactly as it was before."""
    root = Path(root) if root else HERE.parent
    for h in HOSTS:
        f = root / h
        old = f.read_text() if f.exists() else ""
        if "<!-- rapp:begin -->" not in old:
            continue
        a, b = old.index("<!-- rapp:begin -->"), old.index("<!-- rapp:end -->") + len("<!-- rapp:end -->\n")
        new = (old[:a].rstrip("\n") + "\n" + old[b:]).lstrip("\n") if old[:a].strip() or old[b:].strip() else ""
        f.write_text(new) if new.strip() else f.unlink()


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "tools"
    if cmd in ("tools", "call", "import", "ready", "bring") and not AGENTS.is_dir():
        leave()
        print(json.dumps({"tools": [], "off": "The agents folder was removed, so RAPP is off here. The standing "
                          "note has been taken out of the instructions file. Carry on as if it was never there."}))
        return 0
    if cmd == "tools":
        found, broken = load()
        print(json.dumps({"tools": [a.metadata for a in found.values()], "broken": broken}, indent=1))
    elif cmd == "call":
        found, _ = load()
        if argv[2] not in found:
            print(json.dumps({"error": f"no agent named {argv[2]} in agents/", "have": sorted(found)}))
            return 1
        door = ThreadingHTTPServer(("127.0.0.1", 0), Door)
        threading.Thread(target=door.serve_forever, daemon=True).start()
        os.environ["BRAINSTEM_URL"] = f"http://127.0.0.1:{door.server_address[1]}"
        print(found[argv[2]].perform(**json.loads(argv[3] if len(argv) > 3 else "{}")))
    elif cmd == "import":
        code, out = add(argv[2], Path(argv[2]).read_bytes(), argv[3] if len(argv) > 3 else None)
        print(json.dumps(out))
        return 0 if code == 200 else 1
    elif cmd == "bring":
        code, out = bring(" ".join(argv[2:]))
        print(json.dumps(out))
        return 0 if code == 200 else 1
    elif cmd == "ready":
        if len(argv) < 6:
            print("kernel.py ready <file> <Name> '<json args>' '<words the answer must hold>'")
            return 2
        code, out = ready(argv[2], argv[3], json.loads(argv[4]), argv[5], argv[6] if len(argv) > 6 else None)
        print(json.dumps(out, indent=1))
        return code
    elif cmd == "serve":
        cut = argv.index("--") if "--" in argv else len(argv)
        if cut == len(argv) or cut + 1 >= len(argv):
            print("say which AI sits behind the door: kernel.py serve <port> -- <ai command ...>")
            return 1
        serve(argv[2] if cut > 2 else 7071, argv[cut + 1:])
    elif cmd == "stay":
        mine = [a.replace("\\", "/") for a in argv[2:]]
        if [a for a in mine if a not in HOSTS]:
            print("stay takes one of: " + ", ".join(HOSTS))
            return 2
        back = heal()
        print("standing note written to: " + ", ".join(stay(mine=mine)) + ("; fetched: " + ", ".join(back) if back else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
