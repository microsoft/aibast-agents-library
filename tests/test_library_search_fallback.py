from pathlib import Path

from tests.test_library_agent_upvotes import run_library_node


ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library.html"
BRAINSTEM_UI = ROOT / "rapp_brainstem/index.html"


def test_search_supports_synonyms_stems_and_typo_tolerance():
    result = run_library_node(
        """
const agent = {
  name: "@aibast-agents-library/example",
  display_name: "Greenwashing Analysis",
  description: "Analyze sustainability claims and governance risk",
  category: "general",
  tags: ["compliance"],
  _solution: {personas: ["Analyst"], capabilities: ["Analyze claims"]}
};
console.log(JSON.stringify({
  exact: scoreAgent(agent, "greenwashing analysis"),
  typo: scoreAgent(agent, "greenwashing analyser"),
  synonym: scoreAgent(agent, "audit sustainability claims")
}));
"""
    )
    assert result["exact"] > 0
    assert result["typo"] > 0
    assert result["synonym"] > 0


def test_failed_search_offers_learn_new_and_prefills_without_sending():
    result = run_library_node(
        """
state.query = "build a customs tariff classifier";
const html = emptyState();
const url = learnNewBrainstemUrl(state.query);
console.log(JSON.stringify({html, url, prompt: learnNewPrompt(state.query)}));
"""
    )
    assert "No library match" in result["html"]
    assert "Download Learn New agent.py" in result["html"]
    assert "Open Brainstem with this request" in result["html"]
    assert "VS Code" in result["html"]
    assert "Brain Surgeon" in result["html"]
    assert result["url"].startswith("http://localhost:7071/?prompt=")
    assert "customs+tariff+classifier" in result["url"]
    assert "preview, create, self-test, and hot-load" in result["prompt"]

    brainstem = BRAINSTEM_UI.read_text(encoding="utf-8")
    assert "new URLSearchParams(window.location.search).get('prompt')" in brainstem
    assert "input.value = prefilledPrompt.slice(0, 4000)" in brainstem
    assert "history.replaceState" in brainstem
    assert "handleSendButton()" not in brainstem[
        brainstem.index("const prefilledPrompt"):
        brainstem.index("input.addEventListener('input'")
    ]


def test_library_displays_and_sorts_observed_agent_downloads():
    text = LIBRARY.read_text(encoding="utf-8")
    assert '<option value="downloads">Top downloaded</option>' in text
    assert 'const downloads = row.downloads;' in text
    assert 'function agentDownloadCount(agent)' in text
    assert "observed agent.py download" in text
    assert "${agentDownloadCount(agent)}" in text
