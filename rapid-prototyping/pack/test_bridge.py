"""Security tests for the guide bridge: each guard, attacked directly. Standard library only:
  ~/.brainstem/venv/bin/python -m unittest pack/test_bridge.py
"""
import http.client
import json
import os
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge  # noqa: E402

GOOD = "http://127.0.0.1:7090"  # the origin of the guide page the bridge serves


class BridgeSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = bridge.make_server(0)
        cls.port = cls.srv.server_address[1]
        bridge.ALLOWED_ORIGINS.clear()
        bridge.ALLOWED_ORIGINS.add(GOOD)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def req(self, method, path, body=None, origin=GOOD, host="127.0.0.1", token=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        h = {"Host": f"{host}:{self.port}", "Content-Type": "application/json"}
        if origin:
            h["Origin"] = origin
        if token:
            h["Authorization"] = f"Bearer {token}"
        c.request(method, path, body=json.dumps(body) if body is not None else None, headers=h)
        r = c.getresponse()
        data = r.read()
        return r.status, (json.loads(data) if data else {}), dict(r.getheaders())

    def pair(self):
        bridge.STATE["pair"] = "test-code"
        code, j, _ = self.req("POST", "/pair", {"code": "test-code"})
        self.assertEqual(code, 200)
        return j["token"]

    def test_other_sites_are_refused(self):
        for origin in ("https://evil.example", "https://microsoft.github.io", "http://127.0.0.1:7090.evil.example", "null", None):
            code, _, _ = self.req("GET", "/hello", origin=origin)
            self.assertEqual(code, 403, origin)

    def test_dns_rebinding_host_is_refused(self):
        code, _, _ = self.req("GET", "/hello", host="attacker.example")
        self.assertEqual(code, 403)

    def test_same_origin_without_pairing_gets_nothing(self):
        """Pairing is required even for the guide page's own origin."""
        for path in ("/status",):
            self.assertEqual(self.req("GET", path)[0], 401)
        for path in ("/prototype", "/check", "/chat"):
            self.assertEqual(self.req("POST", path, {})[0], 401)

    def test_pairing_code_is_one_time_and_must_match(self):
        bridge.STATE["pair"] = "right-code"
        self.assertEqual(self.req("POST", "/pair", {"code": "wrong"})[0], 403)
        code, j, _ = self.req("POST", "/pair", {"code": "right-code"})
        self.assertEqual(code, 200)
        self.assertEqual(self.req("POST", "/pair", {"code": "right-code"})[0], 403)  # already used
        self.assertEqual(self.req("GET", "/status", token=j["token"])[0], 200)

    def test_forged_or_expired_token_is_refused(self):
        tok = self.pair()
        self.assertEqual(self.req("GET", "/status", token="forged")[0], 401)
        bridge.STATE["tokens"][tok] = 0  # expire it
        self.assertEqual(self.req("GET", "/status", token=tok)[0], 401)

    def test_preflight_allows_private_network_only_for_the_guide(self):
        _, _, h = self.req("OPTIONS", "/status")
        self.assertEqual(h.get("Access-Control-Allow-Private-Network"), "true")
        self.assertEqual(h.get("Access-Control-Allow-Origin"), GOOD)
        code, _, h2 = self.req("OPTIONS", "/status", origin="https://evil.example")
        self.assertEqual(code, 403)
        self.assertNotIn("Access-Control-Allow-Origin", h2)

    def test_only_this_sessions_prototypes_and_no_paths(self):
        tok = self.pair()
        code, j, _ = self.req("POST", "/check", {"prototype": "../../etc"}, token=tok)
        self.assertEqual(code, 404)
        code, j, _ = self.req("POST", "/chat", {"prototype": "anything", "message": "hi"}, token=tok)
        self.assertEqual(code, 404)

    def test_oversized_body_is_refused(self):
        tok = self.pair()
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        c.request("POST", "/prototype", body=b"x" * (bridge.MAX_BODY + 1),
                  headers={"Host": f"127.0.0.1:{self.port}", "Origin": GOOD, "Authorization": f"Bearer {tok}"})
        self.assertEqual(c.getresponse().status, 413)


class LocalModeSecurity(unittest.TestCase):
    """Local mode: the bridge serves the guide page itself at http://127.0.0.1:<port>/guide."""
    @classmethod
    def setUpClass(cls):
        cls.srv = bridge.make_server(0)
        cls.port = cls.srv.server_address[1]
        bridge.LOCAL.update(on=True, origin=f"http://127.0.0.1:{cls.port}")
        bridge.ALLOWED_ORIGINS.add(bridge.LOCAL["origin"])
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        bridge.LOCAL.update(on=False, origin="")

    def get(self, path, host="127.0.0.1", headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        c.request("GET", path, headers={"Host": f"{host}:{self.port}", **(headers or {})})
        r = c.getresponse()
        return r.status, r.read(), dict(r.getheaders())

    def test_guide_page_served_with_frame_protection(self):
        code, _, h = self.get("/guide")
        self.assertEqual(code, 200)
        self.assertEqual(h.get("X-Frame-Options"), "DENY")

    def test_guide_page_refuses_rebinding_host(self):
        self.assertEqual(self.get("/guide", host="attacker.example")[0], 403)

    def test_missing_origin_accepted_only_as_same_origin(self):
        self.assertEqual(self.get("/hello", headers={"Sec-Fetch-Site": "same-origin"})[0], 200)
        self.assertEqual(self.get("/hello", headers={"Sec-Fetch-Site": "cross-site"})[0], 403)
        self.assertEqual(self.get("/hello")[0], 403)  # no browser signal at all

    def test_same_origin_still_needs_pairing(self):
        self.assertEqual(self.get("/status", headers={"Sec-Fetch-Site": "same-origin"})[0], 401)


if __name__ == "__main__":
    unittest.main()
