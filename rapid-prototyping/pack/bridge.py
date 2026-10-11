"""Guide bridge: lets the RAPP production guide (a public web page) drive the person's own Brainstem.

  brainstem-proto guide      # starts this bridge on 127.0.0.1:7090 and opens the guide, paired

Local only: the bridge serves the guide page itself on 127.0.0.1 and answers only that page; no website
can reach it. Security model:
  1. Pairing: a one-time code is printed here and passed to the page in the URL fragment (never sent to
     any server). The page exchanges it once for a session token; every request must carry that token.
  2. Origin allowlist (exact) and Host must be localhost/127.0.0.1 (blocks other sites and DNS rebinding).
  3. A fixed menu: status, create a prototype from transcript text, check it, chat with THAT prototype's
     Brainstem. No paths, no shell, no kernel endpoints, never the everyday Brainstem on 7071.
  4. Limits: request size, one prototype build at a time, idle shutdown, token expiry.
  5. Never stores or forwards the Brainstem's LAN secret. The kernel is unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import subprocess
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROTO_HOME = Path(os.environ.get("PROTO_HOME", Path.home() / ".brainstem-proto"))
PROJECTS = Path(os.environ.get("BRAINSTEM_PROTOTYPES", Path.home() / "BrainstemPrototypes"))
# Local only: the bridge serves the guide page itself and answers only that page's origin.
# No website, Microsoft's included, can reach it. Set when the server starts.
ALLOWED_ORIGINS: set[str] = set()
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}
MAX_BODY = 200_000          # a transcript, not a file dump
TOKEN_TTL = 4 * 3600
IDLE_EXIT = 45 * 60

LOCAL = {"on": False, "origin": ""}  # local mode: the bridge serves the guide page itself (no published site needed)
STATE = {"pair": secrets.token_urlsafe(9), "tokens": {}, "last": time.time(), "building": False, "projects": {}}
LOCK = threading.Lock()


def _now() -> float:
    return time.time()


class Bridge(BaseHTTPRequestHandler):
    server_version = "BrainstemGuideBridge/1"

    def log_message(self, *a):
        pass

    # ---------- guards ----------
    def _origin_ok(self) -> str | None:
        origin = (self.headers.get("Origin") or "").rstrip("/")
        if not origin and LOCAL["on"] and (self.headers.get("Sec-Fetch-Site") or "") == "same-origin":
            origin = LOCAL["origin"]  # the guide this bridge serves itself (browsers omit Origin on same-origin GETs)
        return origin if origin in ALLOWED_ORIGINS else None

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return host in ALLOWED_HOSTS

    def _cors(self, origin: str) -> None:
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "content-type, authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Private-Network", "true")  # Chrome local network access
        self.send_header("Access-Control-Max-Age", "600")

    def _reply(self, code: int, obj, origin: str | None = None) -> None:
        data = json.dumps(obj, default=str).encode()
        self.send_response(code)
        if origin:
            self._cors(origin)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _authorized(self) -> bool:
        tok = (self.headers.get("Authorization") or "").removeprefix("Bearer ").strip()
        exp = STATE["tokens"].get(tok)
        return bool(tok and exp and exp > _now())

    def _gate(self, need_token: bool = True):
        if not self._host_ok():
            self._reply(403, {"error": "bad host"})
            return None
        origin = self._origin_ok()
        if not origin:
            self._reply(403, {"error": "This bridge only answers the RAPP guide."})
            return None
        if need_token and not self._authorized():
            self._reply(401, {"error": "Not paired. Run `brainstem-proto guide` and open the link it prints."}, origin)
            return None
        STATE["last"] = _now()
        return origin

    def _body(self) -> dict | None:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return None
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return None

    # ---------- routes ----------
    def do_OPTIONS(self):
        origin = self._origin_ok()
        if not origin or not self._host_ok():
            self.send_response(403)
            self.end_headers()
            return
        self.send_response(204)
        self._cors(origin)
        self.end_headers()

    def do_GET(self):
        if LOCAL["on"] and self.path.split("?", 1)[0] == "/guide":
            if not self._host_ok():
                return self._reply(403, {"error": "bad host"})
            page = PROTO_HOME / "guide" / "rapp-guide-live.html"
            data = page.read_bytes() if page.exists() else b"<p>The guide page is missing; set up rapid prototyping again.</p>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        origin = self._gate(need_token=False)
        if not origin:
            return
        if self.path == "/hello":  # unauthenticated: only says a bridge is here, nothing else
            return self._reply(200, {"bridge": True, "paired": False}, origin)
        if not self._authorized():
            return self._reply(401, {"error": "Not paired."}, origin)
        if self.path == "/status":
            return self._reply(200, self._status(), origin)
        if self.path.startswith("/templates"):
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import templates
            q = self.path.partition("?q=")[2][:60]
            try:
                return self._reply(200, {"templates": templates.listing(urllib.request.unquote(q))[:40]}, origin)
            except Exception as e:
                return self._reply(502, {"error": f"Couldn't reach the AIBAST registry: {e}"}, origin)
        return self._reply(404, {"error": "unknown"}, origin)

    def do_POST(self):
        if self.path == "/pair":
            origin = self._gate(need_token=False)
            if not origin:
                return
            body = self._body() or {}
            with LOCK:
                ok = STATE["pair"] and secrets.compare_digest(str(body.get("code", "")), STATE["pair"])
                if ok:
                    STATE["pair"] = None  # one-time
                    tok = secrets.token_urlsafe(24)
                    STATE["tokens"][tok] = _now() + TOKEN_TTL
            if not ok:
                return self._reply(403, {"error": "That pairing code is wrong or already used."}, origin)
            return self._reply(200, {"token": tok, "status": self._status()}, origin)
        origin = self._gate()
        if not origin:
            return
        body = self._body()
        if body is None:
            return self._reply(413, {"error": "Too large (transcripts up to 200 KB)."}, origin)
        if self.path == "/prototype":
            return self._reply(*self._prototype(body), origin)
        if self.path == "/check":
            return self._reply(*self._check(body), origin)
        if self.path == "/chat":
            return self._reply(*self._chat(body), origin)
        return self._reply(404, {"error": "unknown"}, origin)

    # ---------- actions ----------
    def _status(self) -> dict:
        try:
            with urllib.request.urlopen("http://127.0.0.1:7071/health", timeout=3) as r:
                h = json.loads(r.read())
            brainstem = {"running": True, "version": h.get("version"), "model": h.get("model")}
        except Exception:
            brainstem = {"running": False}
        installed = (Path.home() / ".brainstem/src/rapp_brainstem/brainstem.py").exists()
        return {"bridge": True, "brainstem_installed": installed, "brainstem": brainstem,
                "pack": (PROTO_HOME / "brainstem-proto").exists(), "prototypes": list(STATE["projects"])}

    def _prototype(self, body: dict):
        """Create a real prototype from transcript text, start it, check it, analyse the call."""
        name = re.sub(r"[^a-z0-9]+", "-", str(body.get("name", "guide-prototype")).lower()).strip("-")[:40] or "guide-prototype"
        transcript = str(body.get("transcript", ""))
        if not transcript.strip():
            return 400, {"error": "Paste a transcript first."}
        with LOCK:
            if STATE["building"]:
                return 409, {"error": "Already building one; wait for it to finish."}
            STATE["building"] = True
        try:
            tmp = PROTO_HOME / "guide-inbox"
            tmp.mkdir(parents=True, exist_ok=True)
            tfile = tmp / f"{name}.txt"
            tfile.write_text(transcript)
            env = {**os.environ, "PROTO_NO_EDITOR": "1"}
            template = str(body.get("template") or "")
            if template and not re.fullmatch(r"(@aibast-agents-library/)?[a-z0-9-]{1,80}", template):
                return 400, {"error": "Not an AIBAST template name."}
            args = ["new"] + (["--template", template] if template else []) + ["--transcript", str(tfile), name]
            run = subprocess.run([str(PROTO_HOME / "brainstem-proto")] + args,
                                 capture_output=True, text=True, timeout=600, env=env)
            tfile.unlink(missing_ok=True)  # the copy lives only in the prototype's discovery/ folder
            m = re.search(r"Created (.+)", run.stdout)
            if not m:
                return 500, {"error": "Couldn't create the prototype.", "log": run.stdout[-1500:] + run.stderr[-500:]}
            d = Path(m.group(1).strip())
            ports = (d / ".proto-ports").read_text().split()
            STATE["projects"][d.name] = {"dir": str(d), "bs": int(ports[0]), "app": int(ports[1])}
            disc = (d / "DISCOVERY.md").read_text() if (d / "DISCOVERY.md").exists() else ""
            agents = sorted(p.name for p in (d / "brainstem" / "agents").glob("*_agent.py"))
            return 200, {"prototype": d.name, "folder": str(d), "app_url": f"http://localhost:{ports[1]}", "agents": agents,
                         "template": template or None,
                         "check": [ln for ln in run.stdout.splitlines() if ln[:1] in ("✓", "✗")],
                         "discovery": disc, "first_prompt": (d / "FIRST-PROMPT.md").read_text()}
        finally:
            STATE["building"] = False

    def _project(self, body: dict):
        p = STATE["projects"].get(str(body.get("prototype", "")))
        return p

    def _check(self, body: dict):
        p = self._project(body)
        if not p:
            return 404, {"error": "No such prototype from this guide session."}
        env = {**os.environ, "BS_PORT": str(p["bs"]), "APP_PORT": str(p["app"])}
        run = subprocess.run(["bash", "scripts/check.sh"], cwd=p["dir"], capture_output=True, text=True, timeout=200, env=env)
        return 200, {"ok": run.returncode == 0, "lines": [ln for ln in run.stdout.splitlines() if ln.strip()]}

    def _chat(self, body: dict):
        p = self._project(body)
        if not p:
            return 404, {"error": "No such prototype from this guide session."}
        text = str(body.get("message", ""))[:4000]
        req = urllib.request.Request(f"http://127.0.0.1:{p['app']}/api/chat", method="POST",
                                     data=json.dumps({"user_input": text}).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            return 200, {"response": (d.get("response") or "").split("|||VOICE|||")[0], "agent_logs": d.get("agent_logs")}
        except urllib.error.URLError as e:
            return 502, {"error": f"The prototype isn't answering ({e.reason}). Try Check."}


def _idle_watch(server: ThreadingHTTPServer) -> None:
    while True:
        time.sleep(30)
        if _now() - STATE["last"] > IDLE_EXIT:
            print("Guide bridge closed after being idle.", flush=True)
            server.shutdown()
            return


def make_server(port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Bridge)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=int(os.environ.get("GUIDE_BRIDGE_PORT", 7090)))
    ap.add_argument("--guide", default="local", help=argparse.SUPPRESS)  # always local
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args(argv)
    if os.environ.get("RAPID_PROTOTYPING_DISABLED"):
        raise SystemExit("Rapid prototyping is turned off on this computer (RAPID_PROTOTYPING_DISABLED).")
    srv = make_server(a.port)
    LOCAL["on"], LOCAL["origin"] = True, f"http://127.0.0.1:{a.port}"
    ALLOWED_ORIGINS.clear()
    ALLOWED_ORIGINS.add(LOCAL["origin"])
    a.guide = f"{LOCAL['origin']}/guide"
    url = f"{a.guide}#pair={STATE['pair']}&port={a.port}"
    print(f"Guide bridge on http://127.0.0.1:{a.port} (answers only {', '.join(sorted(ALLOWED_ORIGINS))}).", flush=True)
    print(f"Pairing code: {STATE['pair']}", flush=True)
    print(f"Open: {url}", flush=True)
    if not a.no_open:
        subprocess.run(["open" if os.uname().sysname == "Darwin" else "xdg-open", url], check=False)
    threading.Thread(target=_idle_watch, args=(srv,), daemon=True).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
