import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library.html"


def library_text():
    return LIBRARY.read_text(encoding="utf-8")


def library_script():
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", library_text(), re.DOTALL)
    assert scripts
    return scripts[-1]


def run_library_node(probe):
    assert shutil.which("node"), "Node.js is required to validate library scripts"
    script = library_script()
    script = re.sub(r"\ninit\(\);\s*$", "\n", script)
    harness = """
const stubElement = {
  addEventListener() {},
  classList: { add() {}, remove() {}, toggle() {} },
  dataset: {},
  style: {}
};
globalThis.document = {
  addEventListener() {},
  getElementById() { return stubElement; },
  documentElement: { getAttribute() { return "light"; }, setAttribute() {} },
  activeElement: { tagName: "BODY", dataset: {} }
};
globalThis.window = {
  isSecureContext: false,
  open(...args) { globalThis.openArgs = args; }
};
globalThis.location = { hash: "", search: "", pathname: "/library.html" };
globalThis.history = { replaceState() {} };
globalThis.localStorage = { getItem() { return null; } };
globalThis.navigator = {};
"""
    result = subprocess.run(
        ["node"],
        input=harness + script + "\n" + probe,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_library_scripts_parse_with_node():
    assert shutil.which("node"), "Node.js is required to validate library scripts"
    result = subprocess.run(
        ["node", "--check"],
        input=library_script(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_metrics_load_is_optional_and_builds_canonical_map():
    text = library_text()
    assert "const [registry, metrics] = await Promise.all([" in text
    assert "state/metrics.json${stamp}" in text
    assert "${SITE}state/metrics.json${stamp}" in text
    assert "state.agentUpvotes = buildAgentUpvoteMap(metrics, state.agents);" in text
    assert 'if (!registry)' in text
    assert 'if (!metrics)' not in text

    result = run_library_node(
        """
const agents = [{name: "canonical-a"}, {name: "canonical-b"}, {name: "canonical-c"}];
const available = buildAgentUpvoteMap({
  agent_metrics: [
    {name: "canonical-a", upvotes: 7},
    {name: "canonical-b", upvotes: null},
    {name: "not-in-registry", upvotes: 99}
  ]
}, agents);
const unavailable = buildAgentUpvoteMap(null, agents);
console.log(JSON.stringify({
  available: Object.fromEntries(available),
  unavailable: Object.fromEntries(unavailable)
}));
"""
    )
    assert result["available"] == {
        "canonical-a": 7,
        "canonical-b": None,
        "canonical-c": None,
    }
    assert result["unavailable"] == {
        "canonical-a": None,
        "canonical-b": None,
        "canonical-c": None,
    }


def test_card_and_detail_render_upvote_action_and_read_only_count():
    text = library_text()
    card = text[text.index("function agentCard"):text.index("function stackCard")]
    detail = text[text.index("function openAgent"):text.index("function openStack")]

    assert "${agentUpvoteControl(agent)}" in card
    assert "${agentUpvoteControl(agent)}" in detail
    assert 'data-action="upvote-agent"' in text
    assert 'data-agent-name="${enc(agent.name)}"' in text
    assert "Aggregate upvotes unavailable" in text
    assert 'count === null ? "—"' in text
    assert "aria-label=" in text

    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/example",
  display_name: "Example Agent",
  description: "Example",
  category: "general",
  _solution: {}
};
state.agentUpvotes = new Map([[agent.name, null]]);
const unavailable = agentUpvoteControl(agent);
state.agentUpvotes = new Map([[agent.name, 12]]);
const available = agentUpvoteControl(agent);
console.log(JSON.stringify({unavailable, available}));
"""
    )
    assert ">—</span>" in result["unavailable"]
    assert ">0</span>" not in result["unavailable"]
    assert ">12</span>" in result["available"]


def test_upvote_issue_is_exact_structured_signal_and_only_opens_form():
    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/example",
  display_name: "Example Agent",
  _solution: {}
};
state.agents = [agent];
const body = agentUpvoteIssueBody(agent.name);
openAgentUpvote(agent.name);
console.log(JSON.stringify({body, openArgs}));
"""
    )
    body = result["body"]
    assert body.startswith("<!-- aibast-agent-upvote:v1 -->")
    assert body.count("- Schema: `aibast-agent-upvote/1.0`") == 1
    assert body.count("- Agent: `@aibast-agents-library/example`") == 1
    assert body.count("\n- Agent: ") == 1
    assert body.count("- Source: library.html") == 1
    assert "Submit this issue to count" in body
    assert "One GitHub account counts once per agent." in body
    assert "Duplicate issues from the same account/agent are deduped." in body
    assert "No free-text or sensitive information is needed." in body
    assert "star" not in body.lower()

    url, target, features = result["openArgs"]
    assert url.startswith(
        "https://github.com/microsoft/aibast-agents-library/issues/new?"
    )
    assert "title=%5BAgent%20upvote%5D%20Example%20Agent" in url
    assert target == "_blank"
    assert features == "noopener"


def test_upvote_action_stops_card_open_and_never_increments_count():
    text = library_text()
    handler = text[text.index('document.addEventListener("click"'):text.index(
        '$("modal-root").addEventListener("click"'
    )]
    assert handler.index('action === "upvote-agent"') < handler.index(
        'action === "open-agent"'
    )
    upvote_branch = handler[
        handler.index('action === "upvote-agent"'):
        handler.index('action === "open-agent"')
    ]
    assert "event.preventDefault();" in upvote_branch
    assert "event.stopPropagation();" in upvote_branch
    assert "openAgentUpvote(dec(target.dataset.agentName));" in upvote_branch

    opener = text[text.index("function openAgentUpvote"):text.index(
        "function agentCard"
    )]
    assert "state.agentUpvotes" not in opener
    assert ".set(" not in opener
    assert "++" not in opener


def test_library_explains_public_agent_signal_and_snapshot_refresh():
    text = library_text()
    assert "public structured GitHub issue signals, not repository stars" in text
    assert "Metrics refresh after the scheduled snapshot." in text
