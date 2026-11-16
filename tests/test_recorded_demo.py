import hashlib
import importlib.util
import json
import re
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-recorded-demo" / "SKILL.md"
AGENT = ROOT / "agents" / "@aibast-agents-library" / "templates" / "recorded_demo_agent.py"
PAGE = ROOT / "rapp_brainstem" / "index.html"


def _agent():
    spec = importlib.util.spec_from_file_location("recorded_demo_agent", AGENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_pins_the_agent_file_it_fetches():
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\nname: aibast-recorded-demo\n")
    pinned = re.search(r"SHA-256 must be `([0-9a-f]{64})`", text).group(1)
    assert pinned == hashlib.sha256(AGENT.read_bytes()).hexdigest()
    assert "Never describe it as a live agent" in text


def test_every_solution_with_recorded_answers_becomes_a_walkthrough():
    agent = _agent()
    rows = json.loads((ROOT / "api/v1/search.json").read_text(encoding="utf-8"))["solutions"]
    assert [r["solution"] for r in agent.catalog(str(ROOT))] == [r["slug"] for r in rows]
    for row in rows:
        record = json.loads((ROOT / row["doc"]).read_text(encoding="utf-8"))
        recorded = [s for s in record["try"]["scenarios"] if s.get("recorded") and s.get("doc")]
        walk = agent.walkthrough(row["slug"], str(ROOT))
        assert len(walk["steps"]) == len(recorded) > 0, row["slug"]
        assert all(step["prompt"] and step["recorded_answer"] for step in walk["steps"])


def test_the_page_gets_one_addition_and_replies_are_marked_recorded():
    agent = _agent()
    walk = agent.walkthrough("first-time-fix", str(ROOT))
    original = PAGE.read_bytes()
    server = agent.http.server.ThreadingHTTPServer(("127.0.0.1", 0), agent.make_handler(walk, original))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        page = urllib.request.urlopen(base + "/", timeout=10).read()
        cut = original.rfind(b"</body>")
        assert page.startswith(original[:cut]) and page.endswith(original[cut:])
        assert b"window.__WALKTHROUGH__" in page[cut:]
        assert b"recorded_answer" not in page[cut:len(page) - len(original) + cut]

        def ask(text):
            request = urllib.request.Request(
                base + "/chat", data=json.dumps({"user_input": text}).encode(),
                headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(request, timeout=10))

        first = walk["steps"][0]
        reply = ask(first["prompt"])
        assert reply["response"].startswith(first["recorded_answer"].rstrip())
        assert reply["response"].endswith("*Recorded answer. Sample data only.*")
        assert "Nothing was sent to an AI" in reply["agent_logs"]
        assert "only answers its recorded questions" in ask("something else")["response"]
        health = json.load(urllib.request.urlopen(base + "/health", timeout=10))
        assert health["agents"] == [walk["agent"]] and health["model"] == "recorded"
    finally:
        server.shutdown()
