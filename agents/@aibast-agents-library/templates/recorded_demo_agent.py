"""Run a step-by-step demo of any AIBAST library solution from its recorded answers.

One file, two front ends:
- Brainstem loads it as an agent (RecordedDemo).
- An AI assistant runs it from the terminal through the skill:
  python3 recorded_demo_agent.py <list|start|stop> ...

It serves the standard Brainstem chat page, unchanged, with one addition: the
up arrow loads the next recorded question and Enter shows the recorded answer.
Nothing is sent to an AI, no sign-in is needed, and every reply is marked as a
recorded answer on sample data. It listens on this computer only.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from basic_agent import BasicAgent
except ImportError:  # running as a plain script outside Brainstem
    class BasicAgent:  # type: ignore[no-redef]
        def __init__(self, name=None, metadata=None):
            self.name, self.metadata = name, metadata


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/recorded-demo",
    "version": "0.1.0",
    "display_name": "Recorded demo",
    "description": (
        "Runs a step-by-step demo of an AIBAST library solution in the standard "
        "Brainstem chat page from its recorded answers. No AI call, no sign-in."
    ),
    "author": "AIBAST",
    "tags": ["demo", "recorded", "walkthrough"],
    "category": "general",
    "quality_tier": "pilot",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

DEFAULT_LIBRARY = "https://microsoft.github.io/aibast-agents-library/"
DEFAULT_PAGE = ("https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
                "rapp_brainstem/index.html")
LOCAL_PAGE = os.path.expanduser("~/.brainstem/src/rapp_brainstem/index.html")
DEFAULT_PORT = 8751
MARK = "Recorded answer. Sample data only."
STATE = os.path.join(tempfile.gettempdir(), "aibast-recorded-demo.json")

# The only addition to the chat page: up arrow loads the next recorded question,
# down arrow the previous one. The position follows the conversation itself.
INJECT = r"""
(function () {
  const STEPS = (window.__WALKTHROUGH__ || {}).steps || [];
  const box = document.getElementById("input");
  if (!box || !STEPS.length) return;
  let cursor = -1;
  function asked() {
    const said = [...document.querySelectorAll("#chat .msg.user")].map(m => (m.innerText || "").trim());
    let p = -1;
    said.forEach(t => { if (p + 1 < STEPS.length && t.includes(STEPS[p + 1].prompt)) p++; });
    return said.length ? p : -1;
  }
  const isStep = v => STEPS.some(s => s.prompt === v);
  const hint = () => { const n = asked() + 1; box.placeholder = n < STEPS.length
    ? `Press ↑ for step ${n + 1} of ${STEPS.length}` : "Message brainstem..."; };
  function load(i) {
    if (i < 0 || i >= STEPS.length) return;
    cursor = i; box.value = STEPS[i].prompt;
    box.dispatchEvent(new Event("input", { bubbles: true }));
    box.setSelectionRange(box.value.length, box.value.length); hint();
  }
  box.addEventListener("keydown", e => {
    if (e.key === "ArrowUp" && (box.value === "" || isStep(box.value))) {
      e.preventDefault(); load(Math.min((box.value === "" ? asked() : cursor) + 1, STEPS.length - 1)); }
    else if (e.key === "ArrowDown" && isStep(box.value)) { e.preventDefault(); load(Math.max(cursor - 1, 0)); }
  }, true);
  const chat = document.getElementById("chat");
  if (chat) new MutationObserver(() => { if (box.value === "") hint(); }).observe(chat, { childList: true, subtree: true });
  hint();
})();
"""


class DemoError(Exception):
    pass


def _read(rel: str, source: str) -> bytes:
    if source.startswith("http"):
        with urllib.request.urlopen(source.rstrip("/") + "/" + rel, timeout=60) as r:
            return r.read()
    with open(os.path.join(source, rel), "rb") as fh:
        return fh.read()


def _page(page: str) -> bytes:
    if page:
        if page.startswith("http"):
            with urllib.request.urlopen(page, timeout=60) as r:
                return r.read()
        with open(page, "rb") as fh:
            return fh.read()
    if os.path.isfile(LOCAL_PAGE):
        with open(LOCAL_PAGE, "rb") as fh:
            return fh.read()
    with urllib.request.urlopen(DEFAULT_PAGE, timeout=60) as r:
        return r.read()


def catalog(source: str = DEFAULT_LIBRARY) -> list[dict]:
    """Every solution that has at least one recorded answer."""
    try:
        items = json.loads(_read("api/v1/search.json", source)).get("solutions", [])
    except Exception as exc:  # noqa: BLE001
        raise DemoError(f"Could not read the library ({exc}).") from exc
    return [{"solution": i.get("slug"), "name": i.get("name")} for i in items if i.get("slug")]


def walkthrough(slug: str, source: str = DEFAULT_LIBRARY) -> dict:
    """The library's public record, as the steps the up arrow walks through."""
    if not slug or not all(c.isalnum() or c == "-" for c in slug):
        raise DemoError("Solution name must look like 'first-time-fix'.")
    try:
        rec = json.loads(_read(f"api/v1/solutions/{slug}.json", source))
    except Exception as exc:  # noqa: BLE001
        raise DemoError(f"No library record found for '{slug}' ({exc}).") from exc
    steps = []
    for s in (rec.get("try") or {}).get("scenarios") or []:
        if not (s.get("recorded") and s.get("doc")):
            continue
        doc = json.loads(_read(s["doc"], source))
        ans = doc.get("answer")
        text = ans.get("answer") if isinstance(ans, dict) else ans
        if not text:
            continue
        steps.append({"label": s.get("title", ""), "kind": "ask", "agent": [rec["name"]],
                      "prompt": doc.get("question") or s["prompt"], "recorded_answer": str(text)})
    if not steps:
        raise DemoError(f"'{slug}' has no recorded answers yet.")
    return {"title": f"{rec['name']}: step-by-step demo (recorded answers, sample data)",
            "agent": rec["name"], "solution": slug, "steps": steps}


def make_handler(walk: dict, html: bytes):
    name = walk["agent"]
    log = f"[{name}] {MARK} Nothing was sent to an AI."
    shown = [{k: v for k, v in s.items() if k != "recorded_answer"} for s in walk["steps"]]
    data = json.dumps({"steps": shown}).replace("</", "<\\/")
    extra = f"<script>window.__WALKTHROUGH__ = {data};</script>\n<script>\n{INJECT}\n</script>\n".encode()
    i = html.rfind(b"</body>")
    page = html[:i] + extra + html[i:] if i >= 0 else html + extra
    fixed = {
        "/health": {"agents": [name], "copilot": "✓", "copilot_username": None,
                    "model": "recorded", "status": "ok", "version": "recorded-demo"},
        "/agents": {"files": [{"agents": [name], "filename": "recorded_demo"}]},
        "/models": {"current": "recorded",
                    "models": [{"available": True, "id": "recorded", "name": "Recorded answers"}]},
        "/login/status": {"pending": False},
        "/voice/config": {},
    }

    def answer(text: str) -> str:
        text = (text or "").strip()
        for s in walk["steps"]:
            if s["prompt"].strip() == text:
                return s["recorded_answer"].rstrip() + f"\n\n*{MARK}*"
        return ("This is a recorded demo, so it only answers its recorded questions. "
                "Press the up arrow to load the next one.")

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *args):  # quiet
            pass

        def _json(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(page)
            elif path in fixed:
                self._json(fixed[path])
            else:
                self._json({"error": "not part of the recorded demo"}, 404)

        def do_POST(self):
            path = self.path.split("?")[0]
            size = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(size) or b"{}")
            except ValueError:
                body = {}
            if path not in ("/chat", "/chat/stream"):
                return self._json({"error": "not part of the recorded demo"}, 404)
            text = answer(body.get("user_input"))
            done = {"response": text, "agent_logs": log, "model": "recorded",
                    "session_id": body.get("session_id") or str(uuid.uuid4())}
            if path == "/chat":
                return self._json(done)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

            def emit(event):
                self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                self.wfile.flush()

            emit({"type": "agent", "logs": log})
            for at in range(0, len(text), 14):
                emit({"type": "delta", "text": text[at:at + 14]})
                time.sleep(0.012)
            emit({"type": "done", **done})

    return Handler


def serve(slug: str, port: int = DEFAULT_PORT, source: str = DEFAULT_LIBRARY,
          page: str = "", open_browser: bool = True) -> None:
    walk = walkthrough(slug, source)
    handler = make_handler(walk, _page(page))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        raise DemoError(f"Port {port} is in use. Try another with --port.") from exc
    url = f"http://localhost:{port}/"
    print(f"{walk['agent']}: {len(walk['steps'])} recorded steps on {url}", flush=True)
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


# ------------------------------------------------------------ Brainstem side
def _start_background(slug: str, port: int, source: str) -> dict:
    walk = walkthrough(slug, source)  # fail early, in plain words
    _stop_background()
    proc = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "start", slug, "--port", str(port),
         "--source", source, "--no-open"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump({"pid": proc.pid, "port": port, "solution": slug}, fh)
    url = f"http://localhost:{port}/"
    return {"ok": True, "url": url, "steps": len(walk["steps"]),
            "summary": (f"The {walk['agent']} demo is ready at {url}. Press the up arrow for each "
                        f"of its {len(walk['steps'])} recorded questions, then Enter.")}


def _stop_background() -> dict:
    try:
        with open(STATE, encoding="utf-8") as fh:
            state = json.load(fh)
        os.kill(int(state["pid"]), signal.SIGTERM)
    except (OSError, ValueError, KeyError):
        return {"ok": True, "summary": "No recorded demo was running."}
    finally:
        try:
            os.remove(STATE)
        except OSError:
            pass
    return {"ok": True, "summary": "The recorded demo is stopped."}


def run(kw: dict) -> dict:
    op = kw.get("operation")
    source = kw.get("source") or os.environ.get("AIBAST_DEMO_SOURCE") or DEFAULT_LIBRARY
    try:
        if op == "list":
            items = catalog(source)
            return {"ok": True, "solutions": items, "summary": f"{len(items)} solutions in the library."}
        if op == "stop":
            return _stop_background()
        if op == "start":
            if not kw.get("solution"):
                raise DemoError("Say which solution to demo.")
            return _start_background(kw["solution"], int(kw.get("port") or DEFAULT_PORT), source)
        raise DemoError("Unknown operation.")
    except DemoError as exc:
        return {"ok": False, "summary": str(exc)}


class RecordedDemoAgent(BasicAgent):
    def __init__(self):
        self.name = "RecordedDemo"
        self.metadata = {
            "name": self.name,
            "description": (
                "Starts a step-by-step demo of an AIBAST library solution (for example "
                "first-time-fix) in the standard chat page, from its recorded answers on "
                "sample data. No AI call and no sign-in. Use operation 'list' to see the "
                "solutions, 'start' to run one and get its address, and 'stop' to end it."),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["list", "start", "stop"]},
                    "solution": {"type": "string", "description": "Library solution slug, e.g. first-time-fix"},
                    "port": {"type": "integer", "description": "Port on this computer (default 8751)"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kw) -> str:
        return json.dumps(run(kw))


# ---------------------------------------------------------------- CLI side
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Step-by-step demo of an AIBAST solution from recorded answers.")
    ap.add_argument("operation", choices=["list", "start", "stop"])
    ap.add_argument("solution", nargs="?", default="")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--source", default="", help="library address or a local copy of it")
    ap.add_argument("--page", default="", help="a Brainstem index.html to use")
    ap.add_argument("--no-open", action="store_true", help="do not open the browser")
    a = ap.parse_args(argv)
    source = a.source or os.environ.get("AIBAST_DEMO_SOURCE") or DEFAULT_LIBRARY
    if a.operation != "start":
        out = run({"operation": a.operation, "source": source})
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1
    try:
        if not a.solution:
            raise DemoError("Say which solution to demo.")
        serve(a.solution, a.port, source, a.page, not a.no_open)
    except DemoError as exc:
        print(json.dumps({"ok": False, "summary": str(exc)}, indent=2))
        return 1
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
