"""AI Review Walkthrough: an experimental, educational rapplication.

Covers the stage order, navigation and answer round-trip, gap checks, the
export packet, the required notice, the public-sources rule, the generic
rule (no internal process names, no vendor names) and the no-attack-content
rule across the agent, its page, its guide card and its manifest entry.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL_DIR = ROOT / "docs" / "experimental" / "ai-review"
AGENT_PATH = TOOL_DIR / "ai_review_walkthrough_agent.py"
PAGE_PATH = TOOL_DIR / "index.html"
GUIDE_PATH = ROOT / "docs" / "rapp-guide.html"
MANIFEST_PATH = ROOT / "docs" / "experimental" / "tools.json"
TOOL_ID = "ai-review-walkthrough"

NOTICE = (
    "Experimental and not an officially supported Microsoft product or service. "
    "Provided as is under the repository's MIT license, with no support or "
    "warranty. Use at your own risk. Trademark use follows the repository's "
    "trademark notice."
)
DISCLAIMER = "Educational. Not legal advice, and not a substitute for your organization's own review."

EXPECTED_ORDER = [
    "Describe the system",
    "Intended and out-of-scope uses",
    "Stakeholders and affected people",
    "Data and privacy",
    "Harms mapping across the principle areas",
    "Threat model, in concept",
    "Evaluation plan and defect rates",
    "Mitigations",
    "Human oversight and escalation",
    "Transparency note",
    "Release decision and sign-off",
    "Monitoring and incident response",
]

# Internal process, form, tool and board names that must never appear.
BANNED_INTERNAL = [
    r"one\s*-?\s*rai",
    r"\bcela\b",
    r"\bdsb\b",
    r"\bsdl\b",
    r"release\s+assessment",
    r"sensitive\s+uses?",
    r"rapp\s+factory",
    r"like we do internally",
    r"this is how microsoft",
    r"microsoft'?s internal",
]
# AI vendor and product names, checked with URLs removed (a public source's
# address may contain a product path; its visible title does not).
BANNED_VENDOR = [
    r"openai", r"chatgpt", r"\bgpt\b", r"\bgpt-", r"anthropic", r"\bclaude\b",
    r"gemini", r"\bllama\b", r"mistral", r"copilot", r"\bazure\b", r"foundry",
]
# Markers of attack strings, jailbreak prompts, exploit or injection payloads.
BANNED_ATTACK = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"jailbreak",
    r"\bDAN\b",
    r"developer mode",
    r"<script>alert",
    r"\bor 1=1\b",
    r"rm -rf",
    r"(\.\./){4,}",  # deep path traversal; the page links three levels up legitimately
    r"/etc/passwd",
    r"pretend (you are|to be)",
    r"system prompt:",
]
URL_RE = re.compile(r"https?://[^\s\"'<>)]+")


def _load_agent_module():
    spec = importlib.util.spec_from_file_location("ai_review_walkthrough_agent", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = _load_agent_module()


class MemStore:
    def __init__(self):
        self.files = {}

    def read_json(self, file_path):
        raw = self.files.get(file_path)
        return json.loads(raw) if raw else {}

    def write_json(self, data, file_path):
        self.files[file_path] = json.dumps(data)

    def write_file(self, file_path, content):
        self.files[file_path] = content


@pytest.fixture()
def agent():
    return MOD.AIReviewWalkthroughAgent(store=MemStore())


def _guide_card() -> str:
    html = GUIDE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<!-- AI Review Walkthrough Tool -->\s*<div class="tool-card" id="tool-ai-review-walkthrough">.*?</a>\s*</div>\s*</div>',
        html, re.S,
    )
    assert match, "the AI Review Walkthrough card is missing from the Experimental tools section"
    return match.group(0)


def _manifest_entry() -> dict:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for entry in data["tools"]:
        if entry.get("name") == "@aibast-agents-library/" + TOOL_ID:
            return entry
    raise AssertionError("no tools.json entry for the AI Review Walkthrough")


def _runtime_output() -> str:
    """Everything the agent itself says or writes, for a full sample review."""
    agent = MOD.AIReviewWalkthroughAgent(store=MemStore())
    parts = [agent.perform(action="start", system_name="Sample"), agent.perform(action="sources")]
    for index, stage in enumerate(MOD.STAGES):
        parts.append(agent.perform(action="check"))
        parts.append(agent.perform(action="answer", answers=dict(stage["example"])))
        if index < len(MOD.STAGES) - 1:
            parts.append(agent.perform(action="next"))
    parts.append(agent.perform(action="status"))
    parts.append(agent.perform(action="export"))
    parts.extend(v for v in agent.store.files.values() if isinstance(v, str))
    parts.append(json.dumps(agent.metadata))
    return "\n".join(parts)


def _surfaces() -> dict[str, str]:
    return {
        "agent": AGENT_PATH.read_text(encoding="utf-8"),
        "agent output": _runtime_output(),
        "page": PAGE_PATH.read_text(encoding="utf-8"),
        "card": _guide_card(),
        "manifest entry": json.dumps(_manifest_entry()),
    }


# ── stages ─────────────────────────────────────────────────────────────────
def test_stage_order():
    assert [s["title"] for s in MOD.STAGES] == EXPECTED_ORDER


def test_every_stage_teaches_asks_shows_an_example_and_cites_sources():
    for stage in MOD.STAGES:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", stage["lesson"].strip()) if s]
        assert 2 <= len(sentences) <= 3, stage["id"]
        assert stage["questions"], stage["id"]
        assert set(stage["example"]) == {q[0] for q in stage["questions"]}, stage["id"]
        assert stage["sources"] and all(k in MOD.SOURCES for k in stage["sources"]), stage["id"]


def test_every_rendered_stage_carries_the_disclaimer_and_learn_more(agent):
    agent.perform(action="start", system_name="Sample")
    for index, stage in enumerate(MOD.STAGES):
        text = agent._render_stage({"stage": index, "answers": {}})
        assert DISCLAIMER in text
        assert "Learn more:" in text
        for key in stage["sources"]:
            assert MOD.SOURCES[key][1] in text
        assert len(text.splitlines()) <= 32, f"stage {index + 1} runs past one screen"


# ── navigation and answers ───────────────────────────────────────────────────
def test_next_back_and_answer_round_trip(agent):
    out = agent.perform(action="start", system_name="Sample")
    assert "Stage 1 of 12" in out
    assert "Stage 2 of 12" in agent.perform(action="next")
    reply = agent.perform(action="answer", answers={"intended": "A\nB", "bogus": "x"})
    assert "`intended`" in reply and "Not recognised: bogus" in reply
    assert "Stage 3 of 12" in agent.perform(action="next")
    back = agent.perform(action="back")
    assert "Stage 2 of 12" in back and "`intended` (done)" in back
    assert "already on stage 1" in (agent.perform(action="back") and agent.perform(action="back"))
    for _ in range(11):
        agent.perform(action="next")
    assert "last stage" in agent.perform(action="next")


def test_free_text_fills_the_next_open_question(agent):
    agent.perform(action="start")
    agent.perform(action="answer", text="Returns Helper answers policy questions.")
    data = agent._load()
    review = data["reviews"][data["current"]]
    assert review["answers"]["describe"]["name"].startswith("Returns Helper")


def test_answer_reply_never_echoes_long_user_text(agent):
    agent.perform(action="start")
    secret = "UNIQUE-LONG-ANSWER " * 40
    reply = agent.perform(action="answer", answers={"name": secret})
    assert "UNIQUE-LONG-ANSWER" not in reply
    assert len(reply) < 400


def test_actions_before_start_are_explained(agent):
    assert "start first" in agent.perform(action="next")
    assert "Unknown action" in agent.perform(action="dance")


# ── check ────────────────────────────────────────────────────────────────────
def test_check_flags_missing_items(agent):
    agent.perform(action="start")
    agent.perform(action="next")
    agent.perform(action="answer", answers={"intended": "One\nTwo"})
    out = agent.perform(action="check")
    assert "You listed no out-of-scope uses" in out
    assert "fewer than two intended uses" not in out
    agent.perform(action="answer", answers={
        "fit": "Saves time.", "out_of_scope": "Legal advice\nRefund decisions",
        "limits": "Rare cases.", "decline": "Points to a manager.",
    })
    assert "No gaps on this stage" in agent.perform(action="check")


def test_check_validates_the_release_decision(agent):
    agent.perform(action="start")
    for _ in range(10):
        agent.perform(action="next")
    agent.perform(action="answer", answers={"decision": "maybe"})
    assert "go, go with conditions, not yet" in agent.perform(action="check")
    agent.perform(action="answer", answers={"decision": "go with conditions"})
    assert "go, go with conditions, not yet" not in agent.perform(action="check")


def test_status_reports_progress(agent):
    agent.perform(action="start", system_name="Sample")
    out = agent.perform(action="status")
    assert "0 of 12 stages complete" in out and "you are here" in out


# ── export ───────────────────────────────────────────────────────────────────
def test_export_writes_the_packet_and_summary(agent):
    agent.perform(action="start", system_name="Returns Helper")
    for index, stage in enumerate(MOD.STAGES):
        agent.perform(action="answer", answers=dict(stage["example"]))
        if index < len(MOD.STAGES) - 1:
            agent.perform(action="next")
    out = agent.perform(action="export")
    assert "written to this folder only" in out and "0 open gap(s)" in out
    packet = next(v for k, v in agent.store.files.items() if k.endswith("review-packet.md"))
    summary = next(v for k, v in agent.store.files.items() if k.endswith("summary.md"))
    for title in EXPECTED_ORDER:
        assert title in packet
    assert NOTICE in packet and DISCLAIMER in packet
    assert "## Sources (checked" in packet
    for _title, url in MOD.SOURCES.values():
        assert url in packet
    assert "**Decision:** go with conditions" in summary
    assert "Stages complete: 12 of 12" in summary
    assert len(summary.splitlines()) < 40
    # Multi-line answers stay inside their bullet.
    assert "**Out of scope:** Legal or consumer-rights advice; Deciding a specific customer's refund;" in summary


def test_export_to_a_real_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_REVIEW_DATA_DIR", str(tmp_path))
    agent = MOD.AIReviewWalkthroughAgent()
    agent.perform(action="start")
    out = agent.perform(action="export")
    assert str(tmp_path) in out
    assert list(tmp_path.rglob("review-packet.md")) and list(tmp_path.rglob("summary.md"))


# ── notice, sources, generic rule, safety ────────────────────────────────────
def test_notice_text_is_present_on_agent_and_page():
    agent_src = AGENT_PATH.read_text(encoding="utf-8")
    doc = MOD.__doc__.replace("\n", " ")
    assert " ".join(NOTICE.split()) in " ".join(doc.split())
    assert MOD.NOTICE == NOTICE
    page = " ".join(re.sub(r"<[^>]+>", " ", PAGE_PATH.read_text(encoding="utf-8")).split())
    page = re.sub(r" ([.,])", r"\1", page)
    assert NOTICE in page and DISCLAIMER in page
    assert "Built from Microsoft's public responsible AI guidance. Educational only." in page
    assert "Built from Microsoft's public responsible AI guidance. Educational only." in agent_src


def test_page_lists_every_stage_and_every_source():
    page = PAGE_PATH.read_text(encoding="utf-8")
    for title in EXPECTED_ORDER:
        assert title in page
    for _title, url in MOD.SOURCES.values():
        assert url in page
    assert MOD.SOURCES_CHECKED in page


def test_sources_are_public_https_pages():
    for title, url in MOD.SOURCES.values():
        assert url.startswith("https://"), url
        host = url.split("/")[2]
        assert host.endswith(("microsoft.com", "thesourcemediaassets.com")), url
        assert "login" not in url and "sharepoint" not in url and "aka.ms" not in url


@pytest.mark.parametrize("pattern", BANNED_INTERNAL)
def test_generic_rule_no_internal_names(pattern):
    for name, text in _surfaces().items():
        assert not re.search(pattern, text, re.I), f"{pattern!r} found in the {name}"


@pytest.mark.parametrize("pattern", BANNED_VENDOR)
def test_generic_rule_no_vendor_names(pattern):
    for name, text in _surfaces().items():
        visible = URL_RE.sub(" ", text)
        if name == "page":
            visible = re.sub(r"<!-- aibast-[a-z]+:start -->.*?<!-- aibast-[a-z]+:end -->", " ", visible, flags=re.S)
        assert not re.search(pattern, visible, re.I), f"{pattern!r} found in the {name}"


@pytest.mark.parametrize("pattern", BANNED_ATTACK)
def test_no_attack_string_content(pattern):
    for name, text in _surfaces().items():
        assert not re.search(pattern, text, re.I), f"{pattern!r} found in the {name}"


def test_agent_is_stdlib_only_and_sends_nothing():
    src = AGENT_PATH.read_text(encoding="utf-8")
    imports = set(re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", src, re.M))
    allowed = {"json", "os", "re", "uuid", "datetime", "agents.basic_agent", "basic_agent", "utils.azure_file_storage"}
    assert imports <= allowed, imports - allowed
    for net in ("urllib", "http.client", "socket", "requests", "urlopen"):
        assert not re.search(rf"^\s*(import|from)\s+{re.escape(net)}\b", src, re.M), net
    assert "urlopen(" not in src


def test_kept_out_of_the_library_catalog():
    assert "ai_review_walkthrough" not in (ROOT / "registry.json").read_text(encoding="utf-8")
    for catalog in ROOT.glob("solutions*.json"):
        assert "ai_review_walkthrough" not in catalog.read_text(encoding="utf-8")


# ── manifest, card and publishing ────────────────────────────────────────────
def test_manifest_entry_is_a_rapplication_in_the_registry_shape():
    import hashlib

    doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = _manifest_entry()
    assert doc["count"] == len(doc["tools"])
    assert entry["kind"] == "rapplication"
    reference = next(t for t in doc["tools"] if t["name"] == "@aibast-agents-library/ai-migration")
    assert set(entry) == set(reference), set(entry) ^ set(reference)
    assert entry["_file"] == "docs/experimental/ai-review/ai_review_walkthrough_agent.py"
    data = (ROOT / entry["_file"]).read_bytes()
    assert entry["_sha256"] == hashlib.sha256(data).hexdigest()
    assert entry["_lines"] == data.decode("utf-8").count("\n")
    assert entry["name"] == MOD.__manifest__["name"]
    assert entry["version"] == MOD.__manifest__["version"]
    assert entry["disclaimer"] == NOTICE
    assert entry["guide_url"] == "docs/experimental/ai-review/index.html"


def test_install_command_matches_the_library_format_everywhere():
    entry = _manifest_entry()
    command = entry["install_command"]
    assert entry["_url"] == "https://microsoft.github.io/aibast-agents-library/" + entry["_file"]
    assert command == (
        "curl -fsSL " + entry["_url"] + " -o ~/.brainstem/src/rapp_brainstem/agents/" + entry["_install_filename"]
    )
    assert command in _guide_card()
    assert command in PAGE_PATH.read_text(encoding="utf-8")


def test_card_links_to_the_page_and_carries_the_framing():
    card = _guide_card()
    assert 'href="experimental/ai-review/index.html"' in card
    assert "Built from Microsoft's public responsible AI guidance. Educational only." in card
    assert 'data-copy-button=""' in card


def test_pages_build_ships_the_agent_and_page_and_each_ring_installs_its_own_copy():
    from pathlib import PurePosixPath

    from scripts import build_pages_site as pages

    for relative in (
        "docs/experimental/ai-review/ai_review_walkthrough_agent.py",
        "docs/experimental/ai-review/index.html",
    ):
        assert pages.classify_source_path(PurePosixPath(relative)) == pages.INCLUDE, relative
    staged_url = "https://example-owner.github.io/aibast-agents-library/docs/experimental/ai-review/ai_review_walkthrough_agent.py"
    for relative in (
        "docs/rapp-guide.html",
        "docs/experimental/tools.json",
        "docs/experimental/ai-review/index.html",
    ):
        # Rewritten while the artifact is built, so the command is right even
        # when it is read without JavaScript or copied as plain text.
        assert relative in pages.RING_PAGES_URL_PATHS, relative
        text = (ROOT / relative).read_text(encoding="utf-8")
        staged = pages.render_pages_base(PurePosixPath(relative), text, "Example-Owner", "aibast-agents-library")
        assert staged_url in staged, relative
        assert "microsoft.github.io/aibast-agents-library/docs/experimental" not in staged, relative
    # The page rewrites its own command to the address that serves it.
    page = PAGE_PATH.read_text(encoding="utf-8")
    assert "new URL(file, window.location.href)" in page


def test_every_experimental_page_with_a_production_address_is_rendered_per_ring():
    from scripts import build_pages_site as pages

    canonical = "https://microsoft.github.io/aibast-agents-library/"
    for path in sorted((ROOT / "docs" / "experimental").rglob("*")):
        if path.suffix.lower() not in {".html", ".json"}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if canonical in path.read_text(encoding="utf-8"):
            assert relative in pages.RING_PAGES_URL_PATHS, relative


# The answers are typed into Brainstem chat, so they go to the model like any
# chat message. Only the saved review and the export stay local. No surface may
# claim otherwise, and the page and the start reply must say so plainly.
FALSE_PRIVACY = re.compile(
    r"(answers? stays? on (?:this|your) device|stays? on your device|sends? nothing anywhere|"
    r"nothing (?:was|is) sent anywhere)",
    re.I,
)
TRUTHFUL_PRIVACY = re.compile(r"sent to the AI model your Brainstem uses", re.I)


def test_no_surface_claims_answers_never_leave_the_device(agent):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(t for t in manifest["tools"] if t["name"].endswith(TOOL_ID))
    start = agent.perform(action="start", system_name="Synthetic helpdesk bot")
    surfaces = {
        "agent source": AGENT_PATH.read_text(encoding="utf-8"),
        "page": PAGE_PATH.read_text(encoding="utf-8"),
        "guide card": _guide_card(),
        "tools.json entry": json.dumps(entry),
        "start reply": start,
    }
    for label, text in surfaces.items():
        assert not FALSE_PRIVACY.search(text), (label, FALSE_PRIVACY.search(text).group(0))
    assert TRUTHFUL_PRIVACY.search(start)
    assert TRUTHFUL_PRIVACY.search(surfaces["page"])
    assert "local storage" in start and "local storage" in surfaces["page"]
