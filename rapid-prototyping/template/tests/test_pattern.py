"""Offline tests (standard library only, so they run on the one-liner's Python as is):
  ~/.brainstem/venv/bin/python -m unittest discover -s tests
"""
import json
import sys
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import llm, server  # noqa: E402


class FakeBrainstem(BaseHTTPRequestHandler):
    """Stands in for the kernel: refuses browser-style cross-origin POSTs, like the real one."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        self._reply(200, {"status": "ok", "agents": ["Idea"]})

    def do_POST(self):
        if self.headers.get("Origin"):
            return self._reply(403, {"error": "cross-origin browser requests need a secret"})
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ideas = [{"title": "A", "why": "b"}]
        self._reply(200, {"response": "Here you go ```json\n" + json.dumps(ideas) + "\n```|||VOICE|||Done.",
                          "agent_logs": "[Idea] " + json.dumps({"ok": True, "ideas": ideas, "asked": body["user_input"][:20]})})

    def _reply(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(handler_server):
    t = threading.Thread(target=handler_server.serve_forever, daemon=True)
    t.start()
    return handler_server


class PatternTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bs = serve(ThreadingHTTPServer(("127.0.0.1", 0), FakeBrainstem))
        cls.bs_url = f"http://127.0.0.1:{cls.bs.server_address[1]}"
        cls.app = serve(server.make_server(0, cls.bs_url))
        cls.app_url = f"http://127.0.0.1:{cls.app.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.bs.shutdown()
        cls.app.shutdown()

    def post(self, url, obj, headers=None):
        req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def test_browser_cannot_call_the_brainstem_directly(self):
        code, _ = self.post(self.bs_url + "/chat", {"user_input": "x"}, {"Origin": "http://localhost:7097"})
        self.assertEqual(code, 403)

    def test_sidecar_forwards_server_side(self):
        code, reply = self.post(self.app_url + "/api/chat", {"user_input": "hello"}, {"Origin": "http://localhost:7097"})
        self.assertEqual(code, 200)
        self.assertEqual(llm.agent_result(reply, "Idea")["ideas"][0]["title"], "A")

    def test_model_door_strips_voice_and_finds_json(self):
        import os
        os.environ["PM_BRAINSTEM_URL"] = self.bs_url
        text = llm.complete("ideas please")
        self.assertNotIn("|||VOICE|||", text)
        self.assertEqual(llm.extract_json(text, list), [{"title": "A", "why": "b"}])

    def test_query_string_still_serves_the_app_and_source_stays_private(self):
        with urllib.request.urlopen(self.app_url + "/?from=email", timeout=5) as r:
            self.assertIn(b"<title>Prototype", r.read())
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(self.app_url + "/server.py", timeout=5)

    def test_extract_json_ignores_placeholder_braces_in_prose(self):
        self.assertEqual(llm.extract_json('use {name} then {"ok": 1}'), {"ok": 1})


if __name__ == "__main__":
    unittest.main()
