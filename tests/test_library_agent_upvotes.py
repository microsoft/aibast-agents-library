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


def run_library_node(probe, hostname=""):
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
globalThis.location = {
  hash: "",
  search: "",
  pathname: "/library.html",
  hostname: __HOSTNAME__
};
globalThis.history = { replaceState() {} };
globalThis.localStorage = { getItem() { return null; } };
globalThis.navigator = {};
"""
    result = subprocess.run(
        ["node"],
        input=harness.replace("__HOSTNAME__", json.dumps(hostname)) + script + "\n" + probe,
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


def test_example_prompts_open_direct_or_inherited_interactive_demo():
    result = run_library_node(
        """
const primary = {
  name: "@aibast-agents-library/account-intelligence",
  _stack: "account_intelligence",
  _stack_vertical: "b2b_sales",
  _solution: {
    package: {
      slug: "account-intelligence",
      quest_url: "solutions/account-intelligence/quest.html"
    }
  }
};
const orchestrator = {
  name: "@aibast-agents-library/account-intelligence-orchestrator",
  _stack: "account_intelligence",
  _stack_vertical: "b2b_sales",
  _solution: {}
};
const unrelated = {
  name: "@aibast-agents-library/unrelated",
  _solution: {}
};
state.agents = [primary, orchestrator, unrelated];
console.log(JSON.stringify({
  curated: interactiveDemoUrl(primary, {
    demo_url: "solutions/_shared/m365-copilot-demo.html?scenario=account"
  }),
  inherited: interactiveDemoUrl(orchestrator, {demo_url: null}),
  unavailable: interactiveDemoUrl(unrelated, {demo_url: null})
}));
"""
    )

    assert result == {
        "curated": (
            "solutions/_shared/m365-copilot-demo.html?scenario=account"
        ),
        "inherited": "solutions/account-intelligence/quest.html",
        "unavailable": "",
    }


def test_metrics_load_is_optional_and_builds_canonical_signal_map():
    text = library_text()
    assert "const [registry, metrics] = await Promise.all([" in text
    assert "state/metrics.json${stamp}" in text
    assert "${SITE}state/metrics.json${stamp}" in text
    assert (
        "state.agentSignals = buildAgentSignalMap(metrics, state.agents);"
        in text
    )
    assert 'if (!registry)' in text
    assert 'if (!metrics)' not in text

    result = run_library_node(
        """
const agents = [{name: "canonical-a"}, {name: "canonical-b"}, {name: "canonical-c"}];
const available = buildAgentSignalMap({
  agent_metrics: [
    {
      name: "canonical-a",
      upvotes: 7,
      acquisitions: 4,
      upvote_discussion_url: "https://github.com/example/repo/discussions/1",
      acquisition_discussion_url: "https://github.com/example/repo/discussions/2"
    },
    {name: "canonical-b", upvotes: null, acquisitions: 0},
    {name: "not-in-registry", upvotes: 99}
  ]
}, agents);
const unavailable = buildAgentSignalMap(null, agents);
console.log(JSON.stringify({
  available: Object.fromEntries(available),
  unavailable: Object.fromEntries(unavailable)
}));
"""
    )
    assert result["available"] == {
        "canonical-a": {
            "upvotes": 7,
            "acquisitions": 4,
            "upvoteUrl": "https://github.com/example/repo/discussions/1",
            "acquisitionUrl": (
                "https://github.com/example/repo/discussions/2"
            ),
        },
        "canonical-b": {
            "upvotes": None,
            "acquisitions": 0,
            "upvoteUrl": "",
            "acquisitionUrl": "",
        },
        "canonical-c": {
            "upvotes": None,
            "acquisitions": None,
            "upvoteUrl": "",
            "acquisitionUrl": "",
        },
    }
    assert result["unavailable"] == {
        name: {
            "upvotes": None,
            "acquisitions": None,
            "upvoteUrl": "",
            "acquisitionUrl": "",
        }
        for name in ("canonical-a", "canonical-b", "canonical-c")
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
state.agentSignals = new Map([[agent.name, {
  upvotes: null,
  acquisitions: null,
  upvoteUrl: "",
  acquisitionUrl: ""
}]]);
const unavailable = agentUpvoteControl(agent);
state.agentSignals = new Map([[agent.name, {
  upvotes: 12,
  acquisitions: 3,
  upvoteUrl: "https://github.com/example/repo/discussions/1",
  acquisitionUrl: "https://github.com/example/repo/discussions/2"
}]]);
const available = agentUpvoteControl(agent);
const acquisition = agentAcquisitionControl(agent);
console.log(JSON.stringify({unavailable, available, acquisition}));
"""
    )
    assert ">—</span>" in result["unavailable"]
    assert ">0</span>" not in result["unavailable"]
    assert ">12</span>" in result["available"]
    assert "Record acquisition" in result["acquisition"]
    assert ">3</span>" in result["acquisition"]


def test_upvote_and_acquisition_open_canonical_discussions():
    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/example",
  display_name: "Example Agent",
  _solution: {}
};
state.agents = [agent];
state.agentSignals = new Map([[agent.name, {
  upvotes: 8,
  acquisitions: 5,
  upvoteUrl: "https://github.com/microsoft/aibast-agents-library/discussions/10",
  acquisitionUrl: "https://github.com/microsoft/aibast-agents-library/discussions/11"
}]]);
openAgentUpvote(agent.name);
const upvoteArgs = openArgs;
openAgentSignal(agent.name, "acquisition");
console.log(JSON.stringify({upvoteArgs, acquisitionArgs: openArgs}));
"""
    )
    url, target, features = result["upvoteArgs"]
    assert url.endswith("/discussions/10")
    assert target == "_blank"
    assert features == "noopener"
    assert result["acquisitionArgs"][0].endswith("/discussions/11")


def test_missing_discussion_url_falls_back_to_current_pages_fork_search():
    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/example",
  display_name: "Example Agent",
  _solution: {}
};
state.agents = [agent];
state.agentSignals = new Map([[agent.name, {
  upvotes: null,
  acquisitions: null,
  upvoteUrl: "",
  acquisitionUrl: ""
}]]);
openAgentUpvote(agent.name);
const upvoteArgs = openArgs;
openAgentSignal(agent.name, "acquisition");
console.log(JSON.stringify({upvoteArgs, acquisitionArgs: openArgs}));
""",
        hostname="kody-w.github.io",
    )

    assert result["upvoteArgs"][0].startswith(
        "https://github.com/kody-w/aibast-agents-library/discussions?"
    )
    assert "%40aibast-agents-library%2Fexample" in result["upvoteArgs"][0]
    assert "%5BAcquisition%5D" in result["acquisitionArgs"][0]


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

    opener = text[text.index("function openAgentSignal"):text.index(
        "function agentCard"
    )]
    assert "state.agentSignals.set" not in opener
    assert ".set(" not in opener
    assert "++" not in opener


def test_library_explains_public_agent_signal_and_snapshot_refresh():
    text = library_text()
    assert "two stable public GitHub Discussions" in text
    assert "signed-in acquisition" in text
    assert "observable CDN and release file transfers" in text
    assert '<a href="achievements.html">Achievements</a>' in text
