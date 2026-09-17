import html
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "index.html"
FORM_SOLUTION_CHOICES = set(
    """
Account Intelligence Agent
Deal Progression Agent
Proposal Generation Agent
Sales Qualification Agent
Win Loss Analysis Agent
Cart Abandonment Recovery Agent
Customer Loyalty and Rewards Agent
Omnichannel Engagement Agent
Personalized Shopping Agent
Cross Selling Opportunities Agent
Customer Escalations Agent
Discount Finder Agent
Procurement Agent
Asset Maintenance Forecast Agent
Emissions Tracking Agent
Field Service Dispatch Agent
Grid Outage Response Agent
Permit Management Agent
Regulatory Reporting Agent
Claims Processing Agent
Customer Onboarding Agent
Customer Sentiment and Churn Prediction Agent
Financial Advisor Agent
Fraud Detection and Alert Agent
Loan Origination Assistant
Portfolio Rebalancing Agent
Regulatory Compliance Agent
Underwriting Support Agent
Wealth Insights Generator Agent
Care Gap Closure Agent
Clinical Notes Summarizer Agent
Patient Intake and Scheduling Agent
Prior Authorization Agent
Ask HR Agent
Inventory Rebalancing Agent
Maintenance Scheduling Agent
Order Status Communications Agent
Product Line Optimization Agent
Supply Risk Monitoring Agent
Client Health Score Agent
Contract Risk Review Agent
Resource Utilization Agent
Time and Entry Billing Agent
Inventory Visibility Agent
Personalized Marketing Agent
Retail Store Associate Copilot
Returns and Complaints Resolution Agent
Supply Chain Disruption Alert Agent
Building Permit Processing Agent
Utility Billing and Assistance Agent
License Renewal and Expansion Agent
Product Feedback Synthesizer Agent
""".strip().splitlines()
)


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
  pathname: "/index.html",
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


def test_toolbar_links_library_academy_and_industry_workshops():
    text = library_text()
    nav = text[
        text.index('<nav class="nav" aria-label="Primary navigation">'):
        text.index("</nav>", text.index('<nav class="nav" aria-label="Primary navigation">'))
    ]

    assert nav.count("<a ") == 4
    assert ">Agent Library</a>" in nav
    assert 'href="docs/installer.html">Install Brainstem</a>' in nav
    assert 'href="academy.html">Academy</a>' in nav
    assert (
        'href="index.html?view=solutions#workshops">'
        "Industry Workshops</a>"
    ) in nav
    for removed in (
        "Workshop settings",
        "Guide",
        "Achievements",
        "Metrics",
        "GitHub",
        "toggle-theme",
    ):
        assert removed not in nav
    assert '<div class="results-head" id="workshops">' in text


def test_catalog_selector_only_shows_solutions_and_first_party():
    text = library_text()
    tabs = text[
        text.index('<div class="tabs" role="tablist" aria-label="Library type">'):
        text.index(
            "</div>",
            text.index('<div class="tabs" role="tablist" aria-label="Library type">'),
        )
    ]

    assert tabs.count('data-action="view"') == 3
    assert 'data-view="solutions">Industry solutions</button>' in tabs
    assert 'data-view="first-party">Microsoft first-party</button>' in tabs
    assert 'data-view="partners">Partner solutions</button>' in tabs
    assert "Multi-agent stacks" not in tabs
    assert "Building blocks" not in tabs
    assert (
        '["solutions", "first-party", "partners"].includes(params.get("view"))'
        in text
    )


def test_industry_groups_restore_filter_and_publish_shareable_deep_links():
    result = run_library_node(
        """
state.advertisedSolutions = new Set(["financial", "healthcare"]);
state.agents = [
  {
    name: "financial",
    display_name: "Financial Agent",
    category: "financial_services",
    _catalog_kind: "solution",
    _solution: {}
  },
  {
    name: "healthcare",
    display_name: "Healthcare Agent",
    category: "healthcare",
    _catalog_kind: "solution",
    _solution: {}
  }
];
location.search = "?industry=Financial%20Services";
restoreState();
const fromLabel = state.industry;
const filteredNames = filteredAgents().map(row => row.agent.name);
location.search = "?industry=financial_services";
restoreState();
const fromInternalKey = state.industry;
location.search = "?industry=not-a-real-industry";
restoreState();
const invalid = state.industry;
state.industry = "financial_services";
location.search = "";
location.hash = "#library";
let replaced = "";
history.replaceState = (_state, _title, url) => { replaced = url; };
syncURL();
console.log(JSON.stringify({
  fromLabel,
  fromInternalKey,
  invalid,
  filteredNames,
  replaced,
  deepLink: industryDeepLink("financial_services")
}));
"""
    )

    assert result == {
        "fromLabel": "financial_services",
        "fromInternalKey": "financial_services",
        "invalid": "",
        "filteredNames": ["financial"],
        "replaced": "/index.html?industry=financial-services#library",
        "deepLink": "?industry=financial-services#library",
    }
    text = library_text()
    assert 'class="industry-share-link"' in text
    assert "Share this industry</a>" in text


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
    assert (
        "const [registry, metrics, catalog, exportInventory, architectureLevel2] = await Promise.all(["
        in text
    )
    assert "state/metrics.json${stamp}" in text
    assert "${SITE}state/metrics.json${stamp}" in text
    assert "solutions/catalog.json${stamp}" in text
    assert "state/copilot_studio_solution_exports.json${stamp}" in text
    assert "state/architecture_level2.json${stamp}" in text
    assert (
        "state.agentSignals = buildAgentSignalMap(metrics, state.agents);"
        in text
    )
    assert 'if (!registry || !catalog)' in text
    assert 'if (!metrics)' not in text
    assert 'if (!exportInventory)' not in text

    result = run_library_node(
        """
const agents = [{name: "canonical-a"}, {name: "canonical-b"}, {name: "canonical-c"}];
const available = buildAgentSignalMap({
  agent_metrics: [
    {
      name: "canonical-a",
      upvotes: 7,
      downloads: 142,
      upvote_discussion_url: "https://github.com/microsoft/aibast-agents-library/discussions/1",
    },
    {name: "canonical-b", upvotes: null, downloads: 0},
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
            "downloads": 142,
            "upvoteUrl": (
                "https://github.com/microsoft/"
                "aibast-agents-library/discussions/1"
            ),
        },
        "canonical-b": {
            "upvotes": None,
            "downloads": 0,
            "upvoteUrl": "",
        },
        "canonical-c": {
            "upvotes": None,
            "downloads": None,
            "upvoteUrl": "",
        },
    }
    assert result["unavailable"] == {
        name: {
            "upvotes": None,
            "downloads": None,
            "upvoteUrl": "",
        }
        for name in ("canonical-a", "canonical-b", "canonical-c")
    }


def test_staging_accepts_only_staging_discussion_urls():
    result = run_library_node(
        """
const agents = [{name: "canonical-a"}];
const signals = buildAgentSignalMap({
  agent_metrics: [{
    name: "canonical-a",
    upvotes: 5,
    downloads: 7,
    upvote_discussion_url: "https://github.com/kody-w/aibast-agents-library/discussions/42"
  }]
}, agents);
console.log(JSON.stringify({
  signal: signals.get("canonical-a"),
  productionUrl: canonicalDiscussionUrl(
    "https://github.com/microsoft/aibast-agents-library/discussions/42"
  )
}));
""",
        hostname="kody-w.github.io",
    )

    assert result == {
        "signal": {
            "upvotes": 5,
            "downloads": 7,
            "upvoteUrl": (
                "https://github.com/kody-w/"
                "aibast-agents-library/discussions/42"
            ),
        },
        "productionUrl": "",
    }


def test_card_shows_only_workshop_and_agent_actions():
    text = library_text()
    card = text[text.index("function agentCard"):text.index("function stackCard")]
    detail = text[text.index("function openAgent"):text.index("function openStack")]

    assert ">View workshop</a>" in card
    assert ">View agent</button>" in card
    assert "${agentUpvoteControl(agent)}" not in card
    assert "${agentDownloadCount(agent)}" not in card
    assert "${agentUpvoteControl(agent)}" in detail
    assert "${agentDownloadCount(agent)}" in detail
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
  downloads: null,
  upvoteUrl: "",
}]]);
const unavailable = agentUpvoteControl(agent);
state.agentSignals = new Map([[agent.name, {
  upvotes: 12,
  downloads: 142,
  upvoteUrl: "https://github.com/microsoft/aibast-agents-library/discussions/1",
}]]);
const available = agentUpvoteControl(agent);
const downloads = agentDownloadCount(agent);
console.log(JSON.stringify({unavailable, available, downloads}));
"""
    )
    assert ">—</span>" in result["unavailable"]
    assert ">0</span>" not in result["unavailable"]
    assert 'disabled aria-disabled="true"' in result["unavailable"]
    assert ">12</span>" in result["available"]
    assert 'disabled aria-disabled="true"' not in result["available"]
    assert "↓ 142" in result["downloads"]


def test_available_field_assets_open_the_solution_prefilled_request_form():
    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/ai-customer-assistant",
  display_name: "Customer Escalations Agent",
  _solution: {}
};
const aliased = {
  name: "@aibast-agents-library/win-loss-analysis",
  display_name: "Win/Loss Analysis Agent",
  _solution: {}
};
const careGap = {
  name: "@aibast-agents-library/care-gap-closure",
  display_name: "Care Gap Closure Agent",
  _solution: {}
};
const formUrl = requestFormUrl(agent);
console.log(JSON.stringify({
  formUrl,
  aliasedUrl: requestFormUrl(aliased),
  careGapUrl: requestFormUrl(careGap),
  onePager: fieldAssetRow("One-pager", "Customer Escalations one-pager.pdf", true, formUrl),
  demo: fieldAssetRow("Demo video", "Customer Escalations demo.mp4", true, formUrl),
  unavailable: fieldAssetRow("Demo video", "", false, formUrl)
}));
"""
    )

    form_prefix = (
        "https://forms.cloud.microsoft/Pages/ResponsePage.aspx"
        "?id=v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-"
        "hUOEY3QjQ3V1RJUk43OEs4WEkzTDZQUVdNMC4u"
        "&r2c6c3672a0d9465d8f24e5caf6f21619="
    )
    assert result["formUrl"] == form_prefix + "%22Customer%20Escalations%20Agent%22"
    assert result["aliasedUrl"] == form_prefix + "%22Win%20Loss%20Analysis%20Agent%22"
    assert result["careGapUrl"] == form_prefix + "%22Care%20Gap%20Closure%20Agent%22"

    for key in ("onePager", "demo"):
        row = result[key]
        assert f'href="{result["formUrl"]}"' in html.unescape(row)
        assert 'target="_blank"' in row
        assert 'rel="noopener"' in row
        assert 'data-action="stop"' in row
        assert 'class="asset asset-request-link"' in row
        assert "Open the access request form" in row

    assert "Customer Escalations one-pager.pdf" in result["onePager"]
    assert "Customer Escalations demo.mp4" in result["demo"]
    assert 'href="' not in result["unavailable"]
    assert 'class="asset"' in result["unavailable"]
    assert "Not listed" in result["unavailable"]

    text = library_text()
    detail = text[text.index("function openAgent(name)"):text.index("function openStack")]
    assert detail.count("fieldAssetRow(") == 2
    assert "const formUrl = requestFormUrl(agent);" in detail


def test_every_library_solution_maps_to_an_exact_microsoft_forms_choice():
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    agents = [
        {
            "name": agent["name"],
            "display_name": agent["display_name"],
            "_solution": agent.get("_solution") or {},
        }
        for agent in registry["agents"]
        if agent.get("_catalog_kind") == "solution"
    ]
    result = run_library_node(
        "const agents = "
        + json.dumps(agents)
        + ";\nconsole.log(JSON.stringify(agents.map(requestFormSolutionName)));"
    )

    assert len(result) == 52
    assert len(set(result)) == len(result)
    assert set(result) == FORM_SOLUTION_CHOICES


def test_library_supports_top_downloaded_sort():
    text = library_text()
    assert '<option value="downloads">Top downloaded</option>' in text
    assert 'downloads: (a, b) =>' in text
    assert 'aggregateAgentSignal(a.agent.name, "downloads")' in text


def test_agent_detail_downloads_python_file_instead_of_showing_one_liner():
    text = library_text()
    detail = text[text.index("function openAgent"):text.index("function openStack")]

    assert "<h3>Download agent.py</h3>" in detail
    assert 'download="${esc(download.filename)}"' in detail
    assert ">Download agent.py</a>" in detail
    assert ">Download Copilot Studio solution</a>" in detail
    assert ">Deployment settings</a>" in detail
    assert "Record acquisition" not in detail
    assert "agentAcquisitionControl" not in detail
    assert "releases/download" in text
    assert "const AGENT_RELEASE" in text
    assert 'href: `${AGENT_RELEASE}/${encodeURIComponent(filename)}`' in text
    assert "curl -fsSL ${AGENT_RELEASE}/" in text
    assert "the imported agent remains unpublished" in detail
    assert "Copy install command" not in detail
    assert '<pre class="code">${esc(install)}</pre>' not in detail

    result = run_library_node(
        """
const direct = agentDownload({
  _install_filename: "example__aaaaaaaaaaaa_agent.py"
});
const renamed = agentDownload({
  _install_filename: "orchestrator__bbbbbbbbbbbb_agent.py"
});
state.exportedSolutionSlugs = new Set(["account-intelligence"]);
const solution = copilotSolutionDownloads({
  _solution: {package: {slug: "account-intelligence"}}
});
console.log(JSON.stringify({direct, renamed, solution}));
"""
    )
    assert result == {
        "direct": {
            "href": (
                "https://github.com/microsoft/aibast-agents-library/"
                "releases/download/agent-downloads/"
                "example__aaaaaaaaaaaa_agent.py"
            ),
            "filename": "example__aaaaaaaaaaaa_agent.py",
        },
        "renamed": {
            "href": (
                "https://github.com/microsoft/aibast-agents-library/"
                "releases/download/agent-downloads/"
                "orchestrator__bbbbbbbbbbbb_agent.py"
            ),
            "filename": "orchestrator__bbbbbbbbbbbb_agent.py",
        },
        "solution": {
            "zip": (
                "solutions/account-intelligence/exports/"
                "account-intelligence-copilot-studio-solution.zip"
            ),
            "settings": (
                "solutions/account-intelligence/exports/"
                "account-intelligence-deployment-settings.json"
            ),
        },
    }


def test_solution_cards_are_limited_to_advertised_catalog_scope():
    result = run_library_node(
        """
state.advertisedSolutions = new Set([
  "@aibast-agents-library/account-intelligence"
]);
state.agents = [
  {
    name: "@aibast-agents-library/account-intelligence",
    _catalog_kind: "solution"
  },
  {
    name: "@aibast-agents-library/grid-outage-response",
    _catalog_kind: "solution"
  }
];
let opened = false;
openModal = () => { opened = true; };
openAgent("@aibast-agents-library/grid-outage-response");
console.log(JSON.stringify({
  names: solutionAgents().map(agent => agent.name),
  excludedDeepLinkOpened: opened
}));
"""
    )
    assert result == {
        "names": ["@aibast-agents-library/account-intelligence"],
        "excludedDeepLinkOpened": False,
    }


def test_upvote_opens_canonical_discussion():
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
  upvoteUrl: "https://github.com/microsoft/aibast-agents-library/discussions/10"
}]]);
openAgentUpvote(agent.name);
console.log(JSON.stringify({upvoteArgs: openArgs}));
"""
    )
    url, target, features = result["upvoteArgs"]
    assert url.endswith("/discussions/10")
    assert target == "_blank"
    assert features == "noopener"


def test_missing_discussion_url_disables_external_action():
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
  upvoteUrl: ""
}]]);
globalThis.openArgs = null;
openAgentUpvote(agent.name);
console.log(JSON.stringify({upvoteArgs: openArgs}));
"""
    )

    assert result == {"upvoteArgs": None}


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
    assert "one public GitHub rating Discussion" in text
    assert "Signed-in GitHub users" in text
    assert "Upvotes are community preference" in text
    assert "acquisition" not in text.lower()
    assert '<a href="achievements.html">Achievements</a>' in text
