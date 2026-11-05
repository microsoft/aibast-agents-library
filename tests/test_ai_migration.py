"""AI Migration experimental tool: scan, plan, apply, undo on SYNTHETIC setups.

Every fixture lives in a tmp dir. Nothing here reads the real home folder.
"""

import importlib.util
import json
import os
import re
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
TOOL_DIR = ROOT / "docs" / "experimental" / "ai-migration"
AGENT_FILE = TOOL_DIR / "ai_migration_agent.py"
PAGE = TOOL_DIR / "index.html"
MANIFEST = ROOT / "docs" / "experimental" / "tools.json"
GUIDE = ROOT / "docs" / "rapp-guide.html"

NOTICE = (
    "Experimental and not an officially supported Microsoft product or service. "
    "Provided as is under the repository's MIT license"
)
NOTICE_TAIL = "with no support or warranty. Use at your own risk."

# Product and vendor names that must not appear where a person reads.
BANNED_NAMES = re.compile(
    r"\b(Claude|Anthropic|Gemini|Gems?|Google|OpenAI|ChatGPT|Codex|GPTs?|Bard|Antigravity)\b"
)

# Fake secrets. None of these may ever show up in output or staged files.
SECRETS = {
    "mcp_env": "sk-FAKEKEY0000111122223333444455556666",
    "mcp_env_b": "AIzaFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE123",
    "mcp_header": "Bearer FAKEbearerTOKEN99887766554433",
    "mcp_arg": "ghp_FAKEargTOKEN000011112222333344445555",
    "mcp_url": "urlFAKEsecret7777888899990000aaaa",
    "toml_env": "FAKEtomlSECRET123456789012345678901234",
    "cred_file": "CREDENTIAL-FILE-CONTENT-NEVER-READ-42",
    "oauth_file": "OAUTH-FILE-CONTENT-NEVER-READ-43",
    "auth_file": "AUTH-FILE-CONTENT-NEVER-READ-44",
    "dotenv": "DOTENV-CONTENT-NEVER-READ-45",
    "inline": "sk-INLINEfake0000999988887777666655554444",
    "export_user": "USER-JSON-NEVER-COPIED-46",
}


def load_agent_module():
    spec = importlib.util.spec_from_file_location("ai_migration_agent_under_test", AGENT_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = load_agent_module()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(base):
    home = base / "home"
    project = base / "project"

    # coding-tool-a
    write(home / ".claude/CLAUDE.md", "# My rules\nBe brief.\nAPI_KEY=" + SECRETS["inline"] + "\n")
    write(home / ".claude/skills/release-notes/SKILL.md",
          "---\nname: release-notes\ndescription: Draft release notes from a diff.\n---\nRead the diff. Write notes.\n")
    write(home / ".claude/skills/style-check/SKILL.md",
          "---\nname: style-check\ndescription: Check prose style.\n---\nCheck style.\n")
    write(home / ".claude/agents/reviewer.md",
          "---\nname: reviewer\ndescription: Reviews code.\n---\nReview carefully.\n")
    write(home / ".claude/commands/standup.md", "Summarize yesterday.\n")
    write(home / ".claude/commands/oauth-notes.md", "refresh " + SECRETS["oauth_file"] + "\n")
    write(home / ".claude/.credentials.json", json.dumps({"token": SECRETS["cred_file"]}))
    write(home / ".claude/settings.json", json.dumps({
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}],
                  "Stop": [{"hooks": [{"type": "command", "command": "say done"}]}]},
    }))
    write(home / ".claude.json", json.dumps({
        "oauthAccount": {"accessToken": SECRETS["cred_file"]},
        "mcpServers": {"tickets": {"command": "/usr/local/bin/npx", "args": ["-y", "tickets-mcp", "--api-key", SECRETS["mcp_arg"]],
                                   "env": {"TICKETS_API_KEY": SECRETS["mcp_env"]}}},
        "projects": {"/x": {"mcpServers": {"docs": {"type": "http", "url": "https://docs.example.com/mcp?token=" + SECRETS["mcp_url"],
                                                    "headers": {"Authorization": SECRETS["mcp_header"]}}}}},
    }))
    write(home / ".claude/projects/-work-app/memory/MEMORY.md", "- prefers short answers\n")
    write(project / "CLAUDE.md", "Project rules.\n")
    write(project / ".mcp.json", json.dumps({"mcpServers": {"db": {"command": "db-mcp", "env": {"DB_PASSWORD": SECRETS["mcp_env_b"]}}}}))
    write(project / ".env", "SECRET=" + SECRETS["dotenv"] + "\n")

    # coding-tool-b
    write(home / ".gemini/GEMINI.md", "Use metric units.\n")
    write(home / ".gemini/oauth_creds.json", json.dumps({"refresh": SECRETS["oauth_file"]}))
    write(home / ".gemini/settings.json", json.dumps({"mcpServers": {"weather": {"command": "weather", "env": {"WEATHER_KEY": SECRETS["mcp_env_b"]}}}}))
    write(home / ".gemini/commands/git/commit.toml", 'description = "Write a commit message"\nprompt = "Write a commit message for the staged diff."\n')
    write(home / ".gemini/extensions/notes/gemini-extension.json", json.dumps({
        "name": "notes", "version": "1.0.0",
        "mcpServers": {"notes-server": {"command": "node", "args": ["server.js"], "env": {"NOTES_TOKEN": SECRETS["mcp_env"]}}},
    }))
    write(home / ".gemini/extensions/notes/GEMINI.md", "Notes extension context.\n")

    # coding-tool-c
    write(home / ".codex/AGENTS.md", "Run tests before finishing.\n")
    write(home / ".codex/auth.json", json.dumps({"OPENAI_API_KEY": SECRETS["auth_file"]}))
    write(home / ".codex/config.toml",
          '[mcp_servers.search]\ncommand = "search-mcp"\nargs = ["--port", "9000"]\n\n'
          '[mcp_servers.search.env]\nSEARCH_KEY = "' + SECRETS["toml_env"] + '"\n')
    write(home / ".codex/prompts/explain.md", "Explain this code simply.\n")
    write(home / ".agents/skills/triage/SKILL.md", "---\nname: triage\ndescription: Triage issues.\n---\nTriage.\n")

    # assistant-export
    export = base / "export.zip"
    with zipfile.ZipFile(export, "w") as archive:
        archive.writestr("conversations.json", json.dumps([{"title": "a"}, {"title": "b"}, {"title": "c"}]))
        archive.writestr("chat.html", "<html>chats</html>")
        archive.writestr("user.json", json.dumps({"email": SECRETS["export_user"]}))
        archive.writestr("message_feedback.json", "[]")
    return home, project, export


@pytest.fixture()
def env(tmp_path, monkeypatch):
    home, project, export = build_fixture(tmp_path)
    imports = tmp_path / "imports"
    agents = tmp_path / "brainstem" / "agents"
    agents.mkdir(parents=True)
    soul = tmp_path / "brainstem" / "soul.md"
    soul.write_text("ORIGINAL SOUL\n", encoding="utf-8")
    existing = agents / "imported_reviewer_agent.py"
    existing.write_text("# a file the person already had\n", encoding="utf-8")
    monkeypatch.setenv("AI_MIGRATION_IMPORTS_DIR", str(imports))
    monkeypatch.setenv("AGENTS_PATH", str(agents))
    agent = MODULE.AIMigrationAgent()
    common = {"home_path": str(home), "project_path": str(project), "export_path": str(export)}
    return {"agent": agent, "common": common, "imports": imports, "agents": agents,
            "soul": soul, "existing": existing, "tmp": tmp_path}


def assert_no_secrets(text):
    for label, value in SECRETS.items():
        assert value not in text, f"secret {label} leaked"
        assert value.replace("Bearer ", "") not in text, f"secret {label} leaked"


def all_text_under(folder):
    chunks = []
    for path in Path(folder).rglob("*"):
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def test_scan_sees_the_right_items_and_names_only(env):
    out = env["agent"].perform(action="scan", **env["common"])
    for name in ("release-notes", "style-check", "reviewer", "standup", "tickets", "docs", "db",
                 "weather", "git:commit", "notes", "notes/notes-server", "search", "explain", "triage"):
        assert name in out, name
    assert "skill: 2" in out and "skill: 1" in out  # per folder
    assert "conversations: 3" in out
    assert "hooks: 2" in out
    # A command named oauth-notes is an ordinary command: carried, with key-looking values redacted.
    assert "oauth-notes" in out and "Skipped" not in out
    # names and counts only: no file bodies
    for body in ("Be brief.", "Read the diff", "Use metric units", "Run tests before finishing", "prefers short answers"):
        assert body not in out
    assert_no_secrets(out)


def test_skill_count_per_source(env):
    out = env["agent"].perform(action="scan", source="coding-tool-a", **env["common"])
    assert "skill: 2" in out
    assert "subagent: 1" in out
    assert "tool servers (MCP): 3" in out
    assert "~/.gemini" not in out


def test_plan_maps_items_and_says_what_does_not_carry(env):
    out = env["agent"].perform(action="plan", **env["common"])
    assert "soul addition" in out
    assert "generated single-file agent" in out
    assert "needs a bridge" in out
    assert "Hooks are not carried" in out
    assert "memory entries" in out
    assert "read-only archive" in out
    assert_no_secrets(out)


def test_apply_is_a_dry_run_by_default(env):
    out = env["agent"].perform(action="apply", **env["common"])
    assert "dry run" in out
    assert not env["imports"].exists()
    assert_no_secrets(out)


def test_apply_stages_without_touching_soul_or_existing_agents(env):
    before_existing = env["existing"].read_bytes()
    before_agents = sorted(p.name for p in env["agents"].iterdir())
    out = env["agent"].perform(action="apply", dry_run=False, include_conversations=True, **env["common"])
    assert "Apply done" in out
    assert env["soul"].read_text(encoding="utf-8") == "ORIGINAL SOUL\n"
    assert env["existing"].read_bytes() == before_existing
    # without confirm, nothing goes into agents/
    assert sorted(p.name for p in env["agents"].iterdir()) == before_agents
    staging = next(env["imports"].iterdir())
    names = {p.relative_to(staging).as_posix() for p in staging.rglob("*") if p.is_file()}
    assert {"soul.import.md", "memory.import.md", "mcp.bridge.json", "REVIEW.md", "manifest.json"} <= names
    assert "archive/conversations.json" in names
    assert not any(n.endswith("user.json") for n in names)
    assert not (staging / "soul.md").exists()
    soul_import = (staging / "soul.import.md").read_text(encoding="utf-8")
    assert "Be brief." in soul_import and "Use metric units." in soul_import
    assert "Notes extension context." in soul_import
    bridge = json.loads((staging / "mcp.bridge.json").read_text(encoding="utf-8"))
    assert {s["name"] for s in bridge["servers"]} >= {"tickets", "docs", "db", "weather", "search", "notes/notes-server"}
    assert all(s["status"] == "needs a bridge" for s in bridge["servers"])
    assert_no_secrets(out)
    assert_no_secrets(all_text_under(env["tmp"] / "imports"))


def test_generated_agents_load_and_run(env):
    env["agent"].perform(action="apply", dry_run=False, **env["common"])
    staging = next(env["imports"].iterdir())
    generated = sorted((staging / "agents").glob("imported_*_agent.py"))
    assert len(generated) >= 7
    for path in generated:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls = next(v for k, v in vars(module).items() if k.startswith("Imported") and k.endswith("Agent"))
        instance = cls()
        assert re.fullmatch(r"[A-Za-z0-9_\-]{1,64}", instance.name)
        assert "imported instructions" in instance.perform(task="x")


def test_confirm_installs_new_agents_but_never_overwrites(env):
    before_existing = env["existing"].read_bytes()
    out = env["agent"].perform(action="apply", dry_run=False, confirm=True, **env["common"])
    assert "Installed into your agents folder" in out
    assert env["existing"].read_bytes() == before_existing
    staging = next(env["imports"].iterdir())
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    assert "imported_reviewer_agent.py" in manifest["skipped_existing"]
    installed = {Path(e["path"]).name for e in manifest["installed"]}
    assert "imported_release_notes_agent.py" in installed
    assert "imported_reviewer_agent.py" not in installed
    assert_no_secrets(all_text_under(env["agents"]))


def test_undo_removes_exactly_the_manifest(env):
    unrelated = env["imports"] / "keep-me.txt"
    env["imports"].mkdir(parents=True)
    unrelated.write_text("not ours", encoding="utf-8")
    before = {p for p in env["agents"].iterdir()}
    env["agent"].perform(action="apply", dry_run=False, confirm=True, **env["common"])
    staging = next(p for p in env["imports"].iterdir() if p.is_dir())
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    listed = [Path(e["path"]) for e in manifest["files"] + manifest["installed"]]
    assert all(p.exists() for p in listed)
    dry = env["agent"].perform(action="undo")
    assert "dry run" in dry and all(p.exists() for p in listed)
    out = env["agent"].perform(action="undo", dry_run=False)
    assert "Undo done" in out
    assert not any(p.exists() for p in listed)
    assert not staging.exists()
    assert {p for p in env["agents"].iterdir()} == before
    assert env["existing"].exists()
    assert unrelated.read_text(encoding="utf-8") == "not ours"
    assert env["soul"].read_text(encoding="utf-8") == "ORIGINAL SOUL\n"


def test_undo_keeps_files_the_person_changed(env):
    env["agent"].perform(action="apply", dry_run=False, **env["common"])
    staging = next(env["imports"].iterdir())
    edited = staging / "soul.import.md"
    edited.write_text("my edits", encoding="utf-8")
    out = env["agent"].perform(action="undo", dry_run=False)
    assert "Kept 1" in out
    assert edited.read_text(encoding="utf-8") == "my edits"


def test_compare_and_no_vendor_names_in_any_output(env):
    outputs = [env["agent"].perform(action=a, **env["common"]) for a in ("scan", "plan", "apply", "compare")]
    outputs.append(env["agent"].perform(action="undo"))
    compare = outputs[3]
    for row in ("Architecture", "Plugins / extensions", "Where your data lives", "Cost model"):
        assert row in compare
    for text in outputs:
        assert not BANNED_NAMES.search(text), BANNED_NAMES.search(text)


def test_redaction_patterns():
    text = "token=abcd1234efgh and sk-abcdefghijklmnop1234 and Bearer abcdefghijklmnop12"
    redacted = MODULE.redact_text(text)
    assert "abcd1234efgh" not in redacted and "sk-abcdef" not in redacted and "abcdefghijklmnop12" not in redacted
    server = MODULE.redact_server("x", {"command": "/home/person/bin/tool", "args": ["--token=abc123456"],
                                       "env": {"K": "v"}, "url": "https://u:p@h.example/p?q=1"})
    blob = json.dumps(server)
    assert "abc123456" not in blob and '"v"' not in blob and "u:p" not in blob and "q=1" not in blob
    assert server["command"] == "tool"


def test_agent_never_points_tests_at_the_real_home():
    # The scan resolves "~" against home_path when given.
    scan = MODULE._Scan("/nonexistent-fixture-home", None, None).run(list(MODULE.SOURCE_IDS))
    assert scan.items == []


# ── Pages, manifest and notices ──────────────────────────────────────────────

def test_no_vendor_names_on_page_manifest_agent_or_card():
    texts = {
        "page": PAGE.read_text(encoding="utf-8"),
        "tools.json": MANIFEST.read_text(encoding="utf-8"),
        "agent": AGENT_FILE.read_text(encoding="utf-8"),
    }
    guide = GUIDE.read_text(encoding="utf-8")
    start = guide.index('<div class="content-section" id="tools">')
    end = guide.index('<div aria-label="Production guide navigation"', start)
    texts["guide tools section"] = guide[start:end]
    for label, text in texts.items():
        match = BANNED_NAMES.search(text)
        assert match is None, f"{label} names {match.group(0)!r}"


def test_notice_on_both_pages_and_in_the_agent():
    for path in (PAGE, GUIDE):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", path.read_text(encoding="utf-8")))
        assert NOTICE in text, path
        assert NOTICE_TAIL in text, path
        assert "Frontier" not in text.split("Experimental tools")[1][:400] if path == GUIDE else True
    raw_guide = GUIDE.read_text(encoding="utf-8")
    raw_page = PAGE.read_text(encoding="utf-8")
    assert "LICENSE" in raw_guide and "LICENSE" in raw_page
    assert "not an officially supported Microsoft product or service" in AGENT_FILE.read_text(encoding="utf-8")


def test_guide_section_is_renamed_and_keeps_its_id():
    guide = GUIDE.read_text(encoding="utf-8")
    assert '<div class="content-section" id="tools">' in guide
    assert '<h1 class="section-title">Experimental tools</h1>' in guide
    assert "Tool Browser" not in guide
    assert "Frontier experimental tools" not in guide
    assert 'href="experimental/ai-migration/index.html"' in guide


def test_tools_manifest_uses_the_registry_entry_shape():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    sample = registry["agents"][0]
    assert doc["count"] == len(doc["tools"])
    kinds = {t["kind"] for t in doc["tools"]}
    assert kinds <= {"agent", "rapplication", "web-tool"}
    agent = next(t for t in doc["tools"] if t["kind"] == "agent")
    for key in ("schema", "name", "version", "display_name", "description", "author", "tags",
                "category", "quality_tier", "requires_env", "dependencies", "_file", "_size_kb",
                "_lines", "_sha256", "_install_filename"):
        assert key in sample or key == "dependencies"
        assert key in agent, key
    assert agent["_file"] == "docs/experimental/ai-migration/ai_migration_agent.py"
    assert (ROOT / agent["_file"]).is_file()
    import hashlib
    assert agent["_sha256"] == hashlib.sha256((ROOT / agent["_file"]).read_bytes()).hexdigest()
    assert agent["name"] == MODULE.__manifest__["name"]
    assert agent["version"] == MODULE.__manifest__["version"]
    for tool in doc["tools"]:
        assert tool["disclaimer"].startswith("Experimental and not an officially supported Microsoft product")
    # Kept out of the library catalog.
    assert all(a["name"] != agent["name"] for a in registry["agents"])
    assert agent["_install_filename"] == "ai_migration_agent.py"


def test_install_command_matches_the_library_format():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    agent = next(t for t in doc["tools"] if t["kind"] == "agent")
    command = agent["install_command"]
    assert command == (
        "curl -fsSL " + agent["_url"] + " -o ~/.brainstem/src/rapp_brainstem/agents/" + agent["_install_filename"]
    )
    assert agent["_url"] == "https://microsoft.github.io/aibast-agents-library/" + agent["_file"]
    assert command in GUIDE.read_text(encoding="utf-8")
    assert command in PAGE.read_text(encoding="utf-8")


def test_page_has_no_sideways_scroll_hazards():
    page = PAGE.read_text(encoding="utf-8")
    assert 'name="viewport"' in page
    assert "overflow-x: auto" in page  # tables and code scroll inside their box, never the page


# ── Publishing ───────────────────────────────────────────────────────────────

def test_pages_build_ships_the_agent_page_and_manifest():
    from pathlib import PurePosixPath
    from scripts import build_pages_site as pages

    for relative in (
        "docs/experimental/ai-migration/ai_migration_agent.py",
        "docs/experimental/ai-migration/index.html",
        "docs/experimental/tools.json",
    ):
        assert pages.classify_source_path(PurePosixPath(relative)) == pages.INCLUDE, relative


def test_each_ring_serves_its_own_install_command():
    from pathlib import PurePosixPath
    from scripts import build_pages_site as pages

    staged_url = "https://example-owner.github.io/aibast-agents-library/docs/experimental/ai-migration/ai_migration_agent.py"
    for relative in sorted(pages.RING_PAGES_URL_PATHS):
        text = (ROOT / relative).read_text(encoding="utf-8")
        path = PurePosixPath(relative)
        assert pages.render_pages_base(path, text, "microsoft", "aibast-agents-library") == text
        staged = pages.render_pages_base(path, text, "Example-Owner", "aibast-agents-library")
        assert "microsoft.github.io/aibast-agents-library/docs/experimental" not in staged, relative
    # Every page that carries this tool's install command serves its own ring's copy.
    for relative in ("docs/rapp-guide.html", "docs/experimental/tools.json", "docs/experimental/ai-migration/index.html"):
        assert relative in pages.RING_PAGES_URL_PATHS, relative
        text = (ROOT / relative).read_text(encoding="utf-8")
        staged = pages.render_pages_base(PurePosixPath(relative), text, "Example-Owner", "aibast-agents-library")
        assert staged_url in staged, relative
    with pytest.raises(pages.BuildError):
        pages.render_pages_base(PurePosixPath("docs/rapp-guide.html"), "no address", "fork", "aibast-agents-library")


def test_scan_plan_apply_label_setups_by_folder_and_carry_the_naming_rule(env):
    """A chat model must have nothing to rename: neutral labels plus an explicit rule."""
    outputs = {
        "scan": env["agent"].perform(action="scan", **env["common"]),
        "plan": env["agent"].perform(action="plan", **env["common"]),
        "apply (dry run)": env["agent"].perform(action="apply", **env["common"]),
        "apply": env["agent"].perform(action="apply", dry_run=False, **env["common"]),
    }
    for label, text in outputs.items():
        match = BANNED_NAMES.search(text)
        assert match is None, f"{label} names {match.group(0)!r}"
        assert MODULE.NAMING_RULE in text, label
    scan = outputs["scan"]
    assert "Setup in ~/.claude (an AI coding tool):" in scan
    assert "Setup in ~/.gemini (an AI coding tool):" in scan
    assert "Setup in ~/.codex and ~/.agents (an AI coding tool):" in scan
    assert "(a hosted AI assistant export):" in scan
    assert "Found in" not in scan
    for label, text in outputs.items():
        assert text.startswith(MODULE.REPLY_RULE), label
    assert env["agent"].perform(action="compare").startswith(MODULE.REPLY_RULE)
    description = MODULE.AIMigrationAgent().metadata["description"]
    assert MODULE.NAMING_RULE in description
    assert BANNED_NAMES.search(description) is None
    for spec in MODULE.DETECTION.values():
        assert BANNED_NAMES.search(spec["label"]) is None


# ── Innocent names are carried; only real key files and key content are skipped ──
INNOCENT_SKILLS = ("authoring-guide", "design-tokens", "session-notes", "cookiecutter-template", "blog-author")


def _innocent_home(base):
    home = base / "innocent-home"
    for name in INNOCENT_SKILLS + ("pdf",):
        write(home / ".claude/skills" / name / "SKILL.md",
              "---\nname: " + name + "\ndescription: Synthetic skill " + name + ".\n---\nDo the " + name + " steps.\n")
    write(home / ".claude/projects/-Users-me-code-auth-service/memory/MEMORY.md", "- uses short commit messages\n")
    # Content that really is a key: skipped by content, and named in the reply.
    write(home / ".claude/skills/deploy-box/SKILL.md",
          "Deploy with this.\n-----BEGIN OPENSSH PRIVATE KEY-----\nFAKEKEYMATERIALnotreal000\n-----END OPENSSH PRIVATE KEY-----\n")
    return home


def test_innocent_names_are_carried_and_real_key_content_is_named_when_skipped(tmp_path):
    home = _innocent_home(tmp_path)
    out = MODULE.AIMigrationAgent().perform(action="scan", home_path=str(home))
    for name in INNOCENT_SKILLS + ("pdf",):
        assert name in out, name
    assert "skill: 6" in out
    assert "auth-service/MEMORY.md" in out
    # The skipped file is listed with a plain reason, and its value never shows.
    assert "Skipped 1 file(s)" in out
    assert "~/.claude/skills/deploy-box/SKILL.md" in out and "private key" in out
    assert "FAKEKEYMATERIAL" not in out


def test_known_key_files_are_skipped_by_name_and_listed(tmp_path):
    export = tmp_path / "export"
    write(export / "conversations.json", json.dumps([{"title": "a"}]))
    write(export / "auth.json", json.dumps({"k": SECRETS["auth_file"]}))
    write(export / "tokens.json", json.dumps({"k": SECRETS["oauth_file"]}))
    write(export / "session-notes" / "conversations.json", json.dumps([{"title": "b"}]))
    out = MODULE.AIMigrationAgent().perform(action="scan", home_path=str(tmp_path / "nohome"), export_path=str(export))
    assert "conversations: 2" in out  # a folder named session-notes is not a key file
    assert "Skipped 2 file(s)" in out
    assert "- export/auth.json (it is a key or sign-in file)" in out
    assert "- export/tokens.json (it is a key or sign-in file)" in out
    assert_no_secrets(out)


def test_name_filter_judges_known_key_files_not_words():
    check = getattr(MODULE, "_is_secret_name")
    for innocent in ("authoring-guide", "design-tokens", "session-notes", "cookiecutter-template",
                     "blog-author", "SKILL.md", "MEMORY.md", "-Users-me-code-auth-service", "token-budget.md"):
        assert not check(innocent), innocent
    for secret in (".env", ".env.local", "auth.json", ".credentials.json", "credentials.json",
                   "oauth_creds.json", "server.pem", "id_rsa", "id_ed25519", "cert.p12", "tls.key", ".netrc"):
        assert check(secret), secret


def test_redaction_leaves_ordinary_words_alone():
    text = "Author: Jane Smith\nPrimary key: customer_id\nAuthorization flow: read the docs"
    assert MODULE.redact_text(text) == text
    for secret in ("api_key: abcd1234efgh5678", "password = hunter22x", "AUTH_TOKEN=abc123def456", "auth: xyz123abc456"):
        assert "[REDACTED]" in MODULE.redact_text(secret), secret



# Joined and camel-case setting names still hide their values, even letters-only
# ones. Every value here is a fake placeholder; a failure names the setting only.
JOINED_SECRET_SETTINGS = [
    "DBPASSWORD=placeholderpass", "APIKEY=Fakefakefake", "OPENAI_APIKEY: placeholderkey",
    "accesstoken: fakeaccessvalue", "MYAPP_AUTH=fakeauthvalue", "auth: fakeauthvalue",
    "dbPassword: placeholderpass", "accessToken=fakeaccessvalue", "apiKey: fakeplaceholder",
    "clientSecret=fakesecretvalue", "SMTP_PASSWD=fakepassword", "db_pwd: fakepassword",
    "AWS_ACCESSKEY=fakeaccessvalue", "privatekey: fakeprivatevalue", "github_token=placeholdervalue",
    "ConnectionString=fakeconnectionvalue", "connection_string: fakeconnectionvalue",
    "authToken = 'fakeauthvalue'", "SIGNINGKEY=fakesigningvalue",
]


def test_redaction_hides_joined_and_camel_case_setting_names():
    for setting in JOINED_SECRET_SETTINGS:
        value = setting.replace("'", "").split("=" if "=" in setting else ":", 1)[1].strip()
        redacted = MODULE.redact_text(setting)
        assert value not in redacted and "[REDACTED]" in redacted, setting.split("=")[0].split(":")[0]


def test_redaction_keeps_ordinary_words_and_names():
    text = ("Author: Jane Smith\nPrimary key: customer_id\nprimaryKey: customer_id\n"
            "Authorization flow: read the docs\nkeyboard: qwerty\nauthoring: drafts first")
    assert MODULE.redact_text(text) == text
    check = MODULE._is_secret_name
    for innocent in ("auth-helper", "token-budget.md", "session-notes", "design-tokens", "authoring"):
        assert not check(innocent), innocent


def test_apply_does_not_copy_joined_setting_values(tmp_path, monkeypatch):
    home = tmp_path / "home"
    skill = home / ".claude" / "skills" / "db-setup"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "Connect with DBPASSWORD=placeholderpass and OPENAI_APIKEY: placeholderkey\naccesstoken: fakeaccessvalue\n",
        encoding="utf-8")
    imports = tmp_path / "imports"
    agents = tmp_path / "agents"
    agents.mkdir()
    monkeypatch.setenv("AI_MIGRATION_IMPORTS_DIR", str(imports))
    monkeypatch.setenv("AGENTS_PATH", str(agents))
    MODULE.AIMigrationAgent().perform(action="apply", home_path=str(home), project_path=str(tmp_path / "none"),
                                      export_path=str(tmp_path / "none"), dry_run=False)
    written = [f for f in imports.rglob("*") if f.is_file()]
    assert written
    for f in written:
        body = f.read_text(encoding="utf-8", errors="ignore")
        for fake in ("placeholderpass", "placeholderkey", "fakeaccessvalue"):
            assert fake not in body, f.name


# ── Generated agents compile for every name and on every OS ──
TRICKY_NAMES = ["update-docs", "xlsx", "Notes", "1st-pass", "42", "név-ünnep", "日本語", "a b\tc", 'say "hi"',
                "back\\slash", "N", "u1234", "class", "def", "__init__", "-", "x" * 200, "..", "Ünïcode Ñame"]


@pytest.mark.parametrize("separator,home", [("/", "/home/person"), ("\\", "C:\\Users\\person")])
def test_generated_agents_compile_for_tricky_names_and_windows_paths(tmp_path, separator, home):
    import warnings
    warnings.simplefilter("error", SyntaxWarning)
    warnings.simplefilter("error", DeprecationWarning)
    body = tmp_path / "SKILL.md"
    body.write_text("---\ndescription: Synthetic \"\"\" quote test\n---\nSay \\N{BULLET} and \\x41.\n", encoding="utf-8")

    class FakeScan:
        def display(self, path):
            return "~" + separator + separator.join([".claude", "skills", self.name, "SKILL.md"])

    used = set()
    for kind in ("skill", "subagent", "command"):
        for name in TRICKY_NAMES:
            scan = FakeScan()
            scan.name = name
            item = {"kind": kind, "name": name, "path": str(body)}
            filename, source = MODULE._generated_agent(item, scan, used, "2026-01-01")
            assert filename.endswith("_agent.py") and filename.isascii(), filename
            assert filename[: -len(".py")].isidentifier(), filename
            compile(source, filename, "exec")
            namespace = {}
            exec(compile(source, filename, "exec"), namespace)
            classes = [v for k, v in namespace.items() if k.startswith("Imported") and isinstance(v, type)]
            assert len(classes) == 1 and classes[0].__name__.isidentifier()
            agent = classes[0]()
            assert agent.metadata["name"].isidentifier()
            assert "Synthetic" in agent.metadata["description"]
    # Outside the home folder a Windows path keeps its drive letter; still compiles.
    class OutsideScan:
        def display(self, path):
            return "C:\\Users\\Nobody\\x\\N\\u\\SKILL.md"
    _, source = MODULE._generated_agent({"kind": "skill", "name": "outside", "path": str(body)}, OutsideScan(), set(), "2026-01-01")
    compile(source, "outside.py", "exec")


def test_guide_tool_development_describes_both_tool_shapes():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(GUIDE.read_text(encoding="utf-8"), "html.parser")
    block = next(h.find_parent("div") for h in soup.select("#tools h3") if h.get_text(strip=True) == "Tool Development")
    text = " ".join(block.get_text(" ").split())
    # The section lists agent.py tools, so it must not say every tool is an HTML file.
    assert "standalone HTML files" not in text
    assert not re.search(r"All tools follow", text)
    assert "agent.py" in text and "docs/experimental/" in text and "tools.json" in text
    assert "HTML file" in text and "tools/" in text
