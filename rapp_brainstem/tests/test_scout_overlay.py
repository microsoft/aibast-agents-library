import importlib.util
import http.client
import json
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCOUT = ROOT / "agents" / "experimental" / "scout"
GATEWAY_PATH = SCOUT / "scout_gateway_agent.py"


def _load_gateway():
    spec = importlib.util.spec_from_file_location("scout_gateway_agent", GATEWAY_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gateway = _load_gateway()


class UpstreamHandler(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, format_string, *args):
        return

    def _record(self, body=b""):
        self.__class__.requests.append({
            "method": self.command,
            "path": self.path,
            "headers": {key.lower(): value for key, value in self.headers.items()},
            "body": body,
        })

    def do_GET(self):
        self._record()
        if self.path == "/health":
            payload = {
                "status": "unauthenticated",
                "version": "0.6.17",
                "model": "gpt-4o",
                "agents": [],
            }
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self._record(body)
        if self.path == "/chat/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            self.wfile.write(b'data: {"type":"delta","text":"first"}\n\n')
            self.wfile.flush()
            time.sleep(0.8)
            self.wfile.write(b'data: {"type":"done"}\n\n')
            self.wfile.flush()
            return
        payload = {
            "response": "gateway echo",
            "session_id": "vm-test",
            "agent_logs": "",
        }
        encoded = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


@pytest.fixture
def overlay_servers():
    UpstreamHandler.requests = []
    upstream = ThreadingHTTPServer(("127.0.0.1", 0), UpstreamHandler)
    upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        gateway_port = probe.getsockname()[1]
    config = gateway.GatewayConfig(
        listen_port=gateway_port,
        upstream_port=upstream.server_address[1],
        secret="test-secret-" + ("x" * 32),
        workspace=ROOT,
    )
    sidecar = gateway.build_server(config)
    sidecar_thread = threading.Thread(target=sidecar.serve_forever, daemon=True)
    sidecar_thread.start()
    try:
        yield sidecar.server_address[1], config
    finally:
        sidecar.shutdown()
        sidecar.server_close()
        upstream.shutdown()
        upstream.server_close()
        sidecar_thread.join(timeout=5)
        upstream_thread.join(timeout=5)


def request(port, path, *, method="GET", headers=None, body=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        method=method,
        headers=headers or {},
        data=body,
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def test_gateway_is_a_rapp_component():
    manifest = gateway.__manifest__
    assert manifest["schema"] == "rapp-agent/1.0"
    assert manifest["name"] == "@rapp/scout-workspace-gateway"
    assert "sidecar" in manifest["tags"]


@pytest.mark.parametrize("origin", ["null", "file://"])
def test_gateway_requires_capability_for_opaque_origin(overlay_servers, origin):
    port, config = overlay_servers

    denied = request(port, "/health", headers={"Origin": origin})
    assert denied[0] == 403

    allowed = request(port, "/health", headers={
        "Origin": origin,
        "X-Scout-Gateway-Secret": config.secret,
    })
    assert allowed[0] == 200
    assert allowed[1]["Access-Control-Allow-Origin"] == origin
    assert json.loads(allowed[2])["version"] == "0.6.17"


def test_gateway_preflight_requires_secret_header_name(overlay_servers):
    port, _config = overlay_servers

    denied = request(port, "/chat", method="OPTIONS", headers={
        "Origin": "null",
        "Access-Control-Request-Headers": "content-type",
    })
    assert denied[0] == 403

    allowed = request(port, "/chat", method="OPTIONS", headers={
        "Origin": "null",
        "Access-Control-Request-Headers": (
            "content-type, x-scout-gateway-secret"
        ),
    })
    assert allowed[0] == 204
    assert allowed[1]["Access-Control-Allow-Origin"] == "null"
    assert "X-Scout-Gateway-Secret" in allowed[1][
        "Access-Control-Allow-Headers"
    ]


def test_gateway_rejects_foreign_browser_origin(overlay_servers):
    port, config = overlay_servers
    response = request(port, "/health", headers={
        "Origin": "https://evil.example",
        "X-Scout-Gateway-Secret": config.secret,
    })
    assert response[0] == 403
    assert UpstreamHandler.requests == []


def test_gateway_rejects_dns_rebinding_host_before_serving_secret(overlay_servers):
    port, config = overlay_servers
    response = request(port, "/", headers={
        "Host": "attacker.example",
        "X-Scout-Gateway-Secret": config.secret,
    })
    assert response[0] == 400
    assert b"window.__SCOUT_BRAINSTEM__" not in response[2]


def test_gateway_emits_cors_for_localhost_alias(overlay_servers):
    port, config = overlay_servers
    origin = f"http://localhost:{port}"
    response = request(port, "/health", headers={
        "Origin": origin,
        "X-Scout-Gateway-Secret": config.secret,
    })
    assert response[0] == 200
    assert response[1]["Access-Control-Allow-Origin"] == origin


def test_gateway_forwards_contract_without_forwarding_capability(overlay_servers):
    port, config = overlay_servers
    body = json.dumps({
        "user_input": "hello",
        "conversation_history": [],
    }).encode()
    response = request(port, "/chat", method="POST", headers={
        "Origin": "null",
        "Content-Type": "application/json",
        "X-Scout-Gateway-Secret": config.secret,
    }, body=body)

    assert response[0] == 200
    assert json.loads(response[2])["response"] == "gateway echo"
    forwarded = UpstreamHandler.requests[-1]
    assert forwarded["method"] == "POST"
    assert forwarded["path"] == "/chat"
    assert json.loads(forwarded["body"])["user_input"] == "hello"
    assert "origin" not in forwarded["headers"]
    assert "x-scout-gateway-secret" not in forwarded["headers"]


def test_gateway_forwards_sse_incrementally(overlay_servers):
    port, config = overlay_servers
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request(
        "POST",
        "/chat/stream",
        body=b'{"user_input":"hello","conversation_history":[]}',
        headers={
            "Content-Type": "application/json",
            "X-Scout-Gateway-Secret": config.secret,
        },
    )
    response = connection.getresponse()
    started = time.monotonic()
    first_byte = response.read(1)
    elapsed = time.monotonic() - started
    remaining = response.read()
    connection.close()

    assert response.status == 200
    assert (first_byte + remaining).startswith(b"data:")
    assert elapsed < 0.5


def test_gateway_rejects_chunked_request_bodies(overlay_servers):
    port, config = overlay_servers
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request(
        "POST",
        "/chat",
        body=iter([b'{"user_input":"hello","conversation_history":[]}']),
        headers={
            "Content-Type": "application/json",
            "X-Scout-Gateway-Secret": config.secret,
        },
        encode_chunked=True,
    )
    response = connection.getresponse()
    payload = json.loads(response.read())
    connection.close()

    assert response.status == 501
    assert "Chunked request bodies" in payload["error"]
    assert UpstreamHandler.requests == []


def test_gateway_exposes_only_needed_kernel_routes(overlay_servers):
    port, config = overlay_servers
    response = request(port, "/debug/auth", headers={
        "X-Scout-Gateway-Secret": config.secret,
    })
    assert response[0] == 404
    assert UpstreamHandler.requests == []


def test_gateway_serves_scout_owned_ui(overlay_servers):
    port, _config = overlay_servers
    page = request(port, "/")

    assert page[0] == 200
    assert b"Scout workspace overlay" in page[2]
    assert b"window.__SCOUT_BRAINSTEM__" in page[2]
    assert request(port, "/runtime-config.js")[0] == 403


def test_overlay_files_do_not_patch_grail_sources():
    controller = (SCOUT / "brainstem-workspace.ps1").read_text(encoding="utf-8")
    workspace = (SCOUT / "workspace.html").read_text(encoding="utf-8")
    brainstem = (ROOT / "brainstem.py").read_text(encoding="utf-8")
    grail_ui = (ROOT / "index.html").read_text(encoding="utf-8")

    assert "scout_gateway_agent.py" in controller
    assert '-ArgumentList "brainstem.py"' in controller
    assert "index.html" not in controller
    assert "-EncodedCommand" in controller
    assert "[Text.Encoding]::Unicode" in controller
    assert "gateway_sha256" in controller
    assert "gateway_started_at" in controller
    assert "Get-CimInstance Win32_Process" in controller
    assert "Get-NetTCPConnection" in controller
    assert "X-Scout-Gateway-Secret" in workspace
    assert "../../../.brainstem_data/scout/runtime-config.js" in workspace
    assert "_LOCAL_PREVIEW_ORIGINS" not in brainstem
    assert "__SCOUT_BRAINSTEM__" not in grail_ui


def test_scout_runtime_state_is_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".brainstem_data/" in ignore
