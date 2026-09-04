"""RAPP/1 sidecar that connects Scout to an unchanged Brainstem kernel."""

from __future__ import annotations

import argparse
import functools
import hmac
import http.client
import json
import os
import socket
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


try:
    from agents.basic_agent import BasicAgent
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from agents.basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@rapp/scout-workspace-gateway",
    "version": "1.0.0",
    "display_name": "Scout Workspace Gateway",
    "description": (
        "Runs a capability-gated loopback sidecar between Microsoft Scout and "
        "an unchanged RAPP Brainstem kernel."
    ),
    "author": "RAPP",
    "tags": ["scout", "workspace", "gateway", "sidecar", "rapp-1"],
    "category": "orchestration",
    "quality_tier": "experimental",
    "requires_env": [],
    "example_call": "Report the Scout workspace gateway status.",
}


_SECRET_HEADER = "X-Scout-Gateway-Secret"
_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}
_REQUEST_HEADERS = {
    "accept",
    "accept-encoding",
    "content-type",
    "if-none-match",
    "range",
    "x-voice-password",
}
_GET_ROUTES = {
    "/health",
    "/version",
    "/models",
    "/login/status",
}
_POST_ROUTES = {
    "/chat",
    "/chat/stream",
    "/login",
    "/login/poll",
    "/login/retry",
    "/models/set",
}


@dataclass(frozen=True)
class GatewayConfig:
    listen_port: int
    upstream_port: int
    secret: str
    workspace: Path

    @property
    def gateway_url(self) -> str:
        return f"http://127.0.0.1:{self.listen_port}"

    @property
    def allowed_origins(self) -> frozenset[str]:
        return frozenset({
            "null",
            "file://",
            self.gateway_url,
            f"http://localhost:{self.listen_port}",
            f"http://[::1]:{self.listen_port}",
        })


class ScoutGatewayHandler(BaseHTTPRequestHandler):
    server_version = "RAPPScoutGateway/1.0"
    protocol_version = "HTTP/1.0"

    def __init__(self, *args, config: GatewayConfig, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)

    def log_message(self, format_string, *args):
        message = format_string % args
        print(f"[scout-gateway] {self.client_address[0]} {message}", flush=True)

    def _origin(self) -> str:
        origin = self.headers.get("Origin") or ""
        return origin.rstrip("/") if origin.startswith(("http://", "https://")) else origin

    def _origin_allowed(self) -> bool:
        origin = self._origin()
        return not origin or origin in self.config.allowed_origins

    def _host_allowed(self) -> bool:
        host = self.headers.get("Host") or ""
        try:
            hostname = urlsplit(f"//{host}").hostname
        except ValueError:
            return False
        return bool(
            hostname
            and hostname.lower() in {"localhost", "127.0.0.1", "::1"}
        )

    def _has_secret(self) -> bool:
        supplied = self.headers.get(_SECRET_HEADER, "")
        return bool(
            supplied
            and hmac.compare_digest(supplied, self.config.secret)
        )

    def _send_cors(self):
        origin = self._origin()
        if origin in self.config.allowed_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self._send_cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _deny_foreign_origin(self) -> bool:
        if not self._host_allowed():
            self._send_json(400, {"error": "Host must resolve to loopback."})
            return True
        if self._origin_allowed():
            return False
        self._send_json(403, {"error": "Foreign browser origins are forbidden."})
        return True

    def _require_capability(self) -> bool:
        if self._deny_foreign_origin():
            return False
        if self._has_secret():
            return True
        self._send_json(403, {
            "error": f"A valid {_SECRET_HEADER} header is required.",
        })
        return False

    def _route_allowed(self) -> bool:
        path = urlsplit(self.path).path
        if self.command in {"GET", "HEAD"}:
            return path in _GET_ROUTES
        if self.command == "POST":
            return path in _POST_ROUTES
        return False

    def _serve_workspace(self):
        page = Path(__file__).with_name("workspace.html")
        try:
            body = page.read_bytes()
        except OSError as exc:
            self._send_json(500, {"error": f"Workspace UI unavailable: {exc}"})
            return
        marker = b"/*__SCOUT_RUNTIME_CONFIG__*/"
        if marker not in body:
            self._send_json(500, {"error": "Workspace UI runtime marker is missing."})
            return
        runtime = (
            "window.__SCOUT_BRAINSTEM__ = "
            + json.dumps({
                "url": self.config.gateway_url,
                "secret": self.config.secret,
            }, separators=(",", ":"))
            + ";"
        ).encode("utf-8")
        body = body.replace(marker, runtime, 1)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _proxy(self):
        if not self._require_capability():
            return
        if not self._route_allowed():
            self._send_json(404, {"error": "Route is not exposed by the Scout gateway."})
            return

        transfer_encoding = (
            self.headers.get("Transfer-Encoding") or ""
        ).strip().lower()
        if transfer_encoding and transfer_encoding != "identity":
            self._send_json(501, {
                "error": "Chunked request bodies are not supported.",
            })
            return
        length_header = self.headers.get("Content-Length")
        try:
            body_length = int(length_header) if length_header else 0
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length header."})
            return
        if body_length < 0 or body_length > 16 * 1024 * 1024:
            self._send_json(413, {"error": "Request body exceeds 16 MiB."})
            return
        body = self.rfile.read(body_length) if body_length else None
        headers = {
            name: value
            for name, value in self.headers.items()
            if name.lower() in _REQUEST_HEADERS
        }

        upstream = http.client.HTTPConnection(
            "127.0.0.1",
            self.config.upstream_port,
            timeout=130,
        )
        try:
            upstream.request(self.command, self.path, body=body, headers=headers)
            response = upstream.getresponse()
        except (ConnectionRefusedError, ConnectionResetError, socket.timeout, OSError) as exc:
            upstream.close()
            self._send_json(502, {"error": f"Brainstem kernel unavailable: {exc}"})
            return

        self.send_response(response.status, response.reason)
        self._send_cors()
        for name, value in response.getheaders():
            lowered = name.lower()
            if lowered in _HOP_BY_HOP_HEADERS or lowered == "content-length":
                continue
            self.send_header(name, value)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            try:
                while True:
                    chunk = response.read1(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (ConnectionResetError, BrokenPipeError, socket.timeout, OSError):
                self.close_connection = True
        upstream.close()

    def do_OPTIONS(self):
        if self._deny_foreign_origin():
            return
        requested = {
            item.strip().lower()
            for item in (
                self.headers.get("Access-Control-Request-Headers") or ""
            ).split(",")
            if item.strip()
        }
        if _SECRET_HEADER.lower() not in requested:
            self._send_json(403, {
                "error": f"Preflight must request {_SECRET_HEADER}.",
            })
            return
        self.send_response(204)
        self._send_cors()
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, X-Scout-Gateway-Secret, X-Voice-Password",
        )
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            return
        if path in {"/", "/workspace.html"}:
            if self._deny_foreign_origin():
                return
            self._serve_workspace()
            return
        if path == "/_scout/health":
            if not self._require_capability():
                return
            self._send_json(200, {
                "status": "ok",
                "schema": "rapp-scout-gateway/1",
                "upstream": f"http://127.0.0.1:{self.config.upstream_port}",
                "workspace": str(self.config.workspace),
            })
            return
        self._proxy()

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self._proxy()


class ScoutWorkspaceGatewayAgent(BasicAgent):
    def __init__(self):
        self.name = "ScoutWorkspaceGateway"
        self.metadata = {
            "name": self.name,
            "description": (
                "Reports the local Scout-to-Brainstem RAPP/1 sidecar state. "
                "The host controller owns gateway lifecycle."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        state_path = os.getenv("SCOUT_BRAINSTEM_STATE")
        if not state_path:
            state_path = str(
                Path(__file__).resolve().parents[3]
                / ".brainstem_data"
                / "scout"
                / "state.json"
            )
        path = Path(state_path)
        if not path.is_file():
            return json.dumps({
                "status": "stopped",
                "schema": "rapp-scout-gateway/1",
            })
        try:
            state = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            return json.dumps({"status": "error", "error": str(exc)})
        return json.dumps({
            "status": "running",
            "schema": state.get("schema"),
            "gateway_url": state.get("gateway_url"),
            "kernel_url": state.get("kernel_url"),
        })


def build_server(config: GatewayConfig) -> ThreadingHTTPServer:
    handler = functools.partial(ScoutGatewayHandler, config=config)
    server = ThreadingHTTPServer(("127.0.0.1", config.listen_port), handler)
    server.daemon_threads = True
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__manifest__["description"])
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream-port", type=int, required=True)
    parser.add_argument("--secret-file", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()

    try:
        secret = args.secret_file.read_text(encoding="ascii").strip()
    except OSError as exc:
        parser.error(f"cannot read gateway secret: {exc}")
    if len(secret) < 32:
        parser.error("gateway secret must contain at least 32 characters")

    config = GatewayConfig(
        listen_port=args.port,
        upstream_port=args.upstream_port,
        secret=secret,
        workspace=args.workspace.resolve(),
    )
    server = build_server(config)
    print(
        f"[scout-gateway] {config.gateway_url} -> "
        f"http://127.0.0.1:{config.upstream_port}",
        flush=True,
    )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
