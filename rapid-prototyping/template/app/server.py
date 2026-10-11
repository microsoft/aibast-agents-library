"""The sidecar: serves the app and forwards /api/chat to the Brainstem, server-side.

The Brainstem rejects cross-origin browser POSTs (CSRF protection). The page calls only its own
origin; this server calls /chat the way any non-browser client does. The kernel is unchanged.

  python -m app.server --port 7097 --brainstem http://localhost:7096
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STATIC = Path(__file__).resolve().parent
MAX_BODY = 1_000_000


class Handler(SimpleHTTPRequestHandler):
    brainstem = "http://localhost:7096"

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]  # a query string must not turn "/" into a folder listing
        if path == "/api/health":
            return self.forward("GET", "/health", None)
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        elif not path.endswith((".html", ".js", ".css", ".json", ".svg", ".png")):
            return self.send_error(404)  # serve the app, never the source tree
        return super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/chat":
            return self.send_error(404)
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self.send_error(413)
        body = self.rfile.read(length)
        try:
            json.loads(body or b"{}")
        except ValueError:
            return self.send_error(400, "body must be JSON")
        return self.forward("POST", "/chat", body)

    def forward(self, method: str, path: str, body: bytes | None):
        req = urllib.request.Request(self.brainstem + path, data=body, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data, status = r.read(), r.status
        except urllib.error.HTTPError as e:
            data, status = e.read(), e.code
        except urllib.error.URLError as e:
            data, status = json.dumps({"error": f"Brainstem not reachable: {e.reason}"}).encode(), 502
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_server(port: int, brainstem: str) -> ThreadingHTTPServer:
    Handler.brainstem = brainstem.rstrip("/")
    return ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(STATIC)))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", 7097)))
    ap.add_argument("--brainstem", default=os.environ.get("PM_BRAINSTEM_URL", "http://localhost:7096"))
    a = ap.parse_args(argv)
    srv = make_server(a.port, a.brainstem)
    print(f"app http://localhost:{a.port}  →  Brainstem {Handler.brainstem}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
