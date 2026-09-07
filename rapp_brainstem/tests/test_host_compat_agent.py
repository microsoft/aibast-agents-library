#!/usr/bin/env python3
"""Hermetic tests for agents/host_compat_agent.py.

Builds a fake Claude home (skills, plugins with commands/agents/hooks/MCP, a
project .claude/) in a temp dir and exercises every action, including a real
JSON-RPC round trip against a tiny stdio MCP server, promotion of a skill into a
native agent that the Brainstem loader accepts, and export of an agent into a
SKILL.md folder that runs standalone.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

BRAINSTEM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BRAINSTEM_DIR not in sys.path:
    sys.path.insert(0, BRAINSTEM_DIR)

AGENT_PATH = os.path.join(BRAINSTEM_DIR, "agents", "host_compat_agent.py")

FAKE_MCP_SERVER = textwrap.dedent('''
    import json, sys
    def send(o):
        sys.stdout.write(json.dumps(o) + "\\n"); sys.stdout.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        msg = json.loads(line)
        m, i = msg.get("method"), msg.get("id")
        if m == "initialize":
            send({"jsonrpc": "2.0", "id": i, "result": {"protocolVersion": msg["params"]["protocolVersion"],
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "fake-mcp", "version": "0.1"}}})
        elif m == "notifications/initialized":
            send({"jsonrpc": "2.0", "method": "notifications/message", "params": {"level": "info", "data": "hi"}})
        elif m == "tools/list":
            send({"jsonrpc": "2.0", "id": i, "result": {"tools": [{"name": "echo", "description": "Echo text back",
                  "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}}}]}})
        elif m == "tools/call":
            a = msg["params"]["arguments"]
            if msg["params"]["name"] != "echo":
                send({"jsonrpc": "2.0", "id": i, "error": {"code": -32602, "message": "no such tool"}}); continue
            send({"jsonrpc": "2.0", "id": i, "result": {"content": [{"type": "text", "text": "echo:" + a.get("text", "")}]}})
        else:
            send({"jsonrpc": "2.0", "id": i, "error": {"code": -32601, "message": "unknown " + str(m)}})
''')


def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class TestHostCompat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="host_compat_")
        cls.home = os.path.join(cls.tmp, "claude_home")
        cls.proj = os.path.join(cls.tmp, "proj")
        cls.store = os.path.join(cls.tmp, "store")
        os.makedirs(cls.proj)
        # user skill with a script and a reference
        _w(os.path.join(cls.home, "skills", "blueprint", "SKILL.md"), textwrap.dedent('''\
            ---
            name: blueprint
            description: Draw a blueprint of a system. Use when the user says "blueprint this" or asks for an architecture sketch.
            allowed-tools: Bash, Read
            metadata:
              version: "1.2"
            ---
            # Blueprint

            Step 1: read references/rules.md. Step 2: run scripts/draw.py.
            '''))
        _w(os.path.join(cls.home, "skills", "blueprint", "references", "rules.md"), "RULE: keep it simple\n")
        _w(os.path.join(cls.home, "skills", "blueprint", "scripts", "draw.py"),
           "import sys, os\nprint('drawn', sys.argv[1:], os.environ.get('CLAUDE_SKILL_DIR', '')[-9:])\n")
        # a second skill with no frontmatter name (falls back to dir name) and a folded description
        _w(os.path.join(cls.home, "skills", "folded", "SKILL.md"), textwrap.dedent('''\
            ---
            description: >
              A folded multi-line
              description here.
            ---
            body of folded
            '''))
        # project skill shadows nothing but exists
        _w(os.path.join(cls.proj, ".claude", "skills", "projskill", "SKILL.md"),
           "---\nname: projskill\ndescription: Project-local skill.\n---\nproject body\n")
        # user slash command with $ARGUMENTS and $1
        _w(os.path.join(cls.home, "commands", "greet.md"),
           "---\ndescription: Greet someone\nargument-hint: <name>\n---\nSay hello to $1. Full args: $ARGUMENTS\n")
        # user subagent persona
        _w(os.path.join(cls.home, "agents", "reviewer.md"),
           "---\nname: reviewer\ndescription: Harsh code reviewer persona\ntools: Read, Grep\n---\nYou are a reviewer.\n")
        # a plugin in the cache with skill, command, agent, hooks and an MCP server
        pdir = os.path.join(cls.home, "plugins", "cache", "mkt", "toolbox", "1.0.0")
        _w(os.path.join(pdir, ".claude-plugin", "plugin.json"),
           json.dumps({"name": "toolbox", "version": "1.0.0", "description": "A test plugin"}))
        _w(os.path.join(pdir, "skills", "hammer", "SKILL.md"), "---\nname: hammer\ndescription: Hit nails.\n---\nhit\n")
        _w(os.path.join(pdir, "commands", "nail.md"), "---\ndescription: Nail it\n---\nnail $ARGUMENTS\n")
        _w(os.path.join(pdir, "agents", "carpenter.md"), "---\nname: carpenter\ndescription: Builds things\n---\nYou build.\n")
        _w(os.path.join(pdir, "hooks", "hooks.json"), json.dumps({"hooks": {"Stop": [{"matcher": "", "hooks": [
            {"type": "command", "command": "cat > /dev/null; echo hooked-from-${CLAUDE_PLUGIN_ROOT}"}]}],
            "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo bash-only"}]}]}}))
        _w(os.path.join(pdir, "fake_mcp.py"), FAKE_MCP_SERVER)
        _w(os.path.join(pdir, ".mcp.json"), json.dumps({"mcpServers": {"fake": {
            "command": sys.executable, "args": ["${CLAUDE_PLUGIN_ROOT}/fake_mcp.py"]}}}))
        _w(os.path.join(cls.home, "plugins", "installed_plugins.json"),
           json.dumps({"version": 2, "plugins": {"toolbox@mkt": [{"scope": "user", "installPath": pdir}]}}))
        # project-level MCP server (also stdio, same fake) and a broken JSON file to exercise error reporting
        _w(os.path.join(cls.proj, ".mcp.json"), json.dumps({"mcpServers": {"projfake": {
            "command": sys.executable, "args": [os.path.join(pdir, "fake_mcp.py")]}}}))
        _w(os.path.join(cls.home, "plugins", "cache", "mkt", "broken", "0.1", "plugin.json"), "{not json")

        # ── GitHub Copilot CLI home: skills, installed plugin, mcp-config with type "local", hooks
        cls.cop = os.path.join(cls.tmp, "copilot_home")
        _w(os.path.join(cls.cop, "skills", "ledger", "SKILL.md"),
           "---\nname: ledger\ndescription: Balance the books. Use when the user says \"ledger this\".\n---\nledger body\n")
        _w(os.path.join(cls.cop, "installed-plugins", "mkt", "cop-tools", "plugin.json"),
           json.dumps({"name": "cop-tools", "version": "3.1", "description": "Copilot plugin"}))
        _w(os.path.join(cls.cop, "installed-plugins", "mkt", "cop-tools", "skills", "saw", "SKILL.md"),
           "---\nname: saw\ndescription: Cut wood.\n---\ncut\n")
        _w(os.path.join(cls.cop, "installed-plugins", "_direct", "solo", "plugin.json"), json.dumps({"name": "solo", "version": "0.1"}))
        _w(os.path.join(cls.cop, "installed-plugins", "_direct", "solo", "agents", "helper.agent.md"),
           "---\nname: helper\ndescription: Copilot helper persona\n---\nYou help.\n")
        _w(os.path.join(cls.cop, "mcp-config.json"), json.dumps({"mcpServers": {"copfake": {
            "type": "local", "tools": ["*"], "command": sys.executable, "args": [os.path.join(pdir, "fake_mcp.py")]}}}))
        _w(os.path.join(cls.cop, "hooks", "audit.json"), json.dumps({"hooks": {"sessionStart": [
            {"type": "command", "command": "echo copilot-session-start"}]}}))
        # project-level copilot conventions
        _w(os.path.join(cls.proj, ".github", "skills", "ghskill", "SKILL.md"), "---\nname: ghskill\ndescription: Repo skill for Copilot.\n---\ngh body\n")
        _w(os.path.join(cls.proj, ".github", "agents", "planner.agent.md"), "---\nname: planner\ndescription: Plans work\nmodel: gpt-5\n---\nYou plan.\n")
        _w(os.path.join(cls.proj, ".github", "prompts", "release.prompt.md"),
           "---\ndescription: Cut a release\nmode: agent\n---\nRelease version ${input:version} now. Args: $ARGUMENTS\n")
        _w(os.path.join(cls.proj, ".github", "copilot-instructions.md"), "Always be terse.\n")
        _w(os.path.join(cls.proj, "AGENTS.md"), "# Agents\nRepo agent rules.\n")
        _w(os.path.join(cls.proj, "CLAUDE.md"), "# Claude\nClaude rules.\n")
        # the same skill folder reachable from two hosts must collapse to one entry
        os.symlink(os.path.join(cls.home, "skills", "blueprint"), os.path.join(cls.proj, ".agents", "skills", "blueprint") if os.makedirs(os.path.join(cls.proj, ".agents", "skills"), exist_ok=True) is None else "")
        # ── transcripts: one Claude Code session, two Copilot CLI sessions (one old, outside the window)
        def jl(rows):
            return "\n".join(json.dumps(r) for r in rows) + "\n"
        _w(os.path.join(cls.home, "projects", "-proj", "aaaa1111-0000-0000-0000-000000000001.jsonl"), jl([
            {"type": "summary", "summary": "Zebra migration plan"},
            {"type": "user", "cwd": "/work/zebra", "timestamp": "2026-09-01T10:00:00Z", "sessionId": "aaaa1111",
             "message": {"role": "user", "content": "Plan the zebra database migration with pelican rollback"}},
            {"type": "assistant", "cwd": "/work/zebra", "timestamp": "2026-09-01T10:00:05Z",
             "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "secret"},
                                                          {"type": "text", "text": "Zebra migration: three phases, pelican rollback last."},
                                                          {"type": "tool_use", "name": "Bash", "input": {}}]}},
            {"type": "user", "isMeta": True, "message": {"role": "user", "content": "pelican meta noise"}},
        ]))
        sdir = os.path.join(cls.cop, "session-state", "bbbb2222-0000-0000-0000-000000000002")
        _w(os.path.join(sdir, "workspace.yaml"), "id: bbbb2222\ncwd: /work/zebra-cli\nname: Zebra CLI fixes\n")
        _w(os.path.join(sdir, "events.jsonl"), jl([
            {"type": "session.start", "timestamp": "2026-09-02T09:00:00Z", "data": {"context": {"cwd": "/work/zebra-cli"}}},
            {"type": "user.message", "timestamp": "2026-09-02T09:00:01Z", "data": {"content": "copilot please fix the zebra CLI flag parsing"}},
            {"type": "tool.execution_start", "timestamp": "2026-09-02T09:00:02Z", "data": {"content": "zebra should not be indexed from tools"}},
            {"type": "assistant.message", "timestamp": "2026-09-02T09:00:03Z", "data": {"content": "", "toolRequests": [{"name": "bash"}]}},
            {"type": "assistant.message", "timestamp": "2026-09-02T09:00:09Z", "data": {"content": "Fixed the zebra flag parser; pelican untouched."}},
        ]))
        old_dir = os.path.join(cls.cop, "session-state", "cccc3333-0000-0000-0000-000000000003")
        _w(os.path.join(old_dir, "events.jsonl"), jl([
            {"type": "user.message", "timestamp": "2025-01-01T00:00:00Z", "data": {"content": "ancient zebra talk"}}]))
        old_t = 1735689600  # 2025-01-01
        os.utime(os.path.join(old_dir, "events.jsonl"), (old_t, old_t))

        os.environ["HOST_COMPAT_COPILOT_HOME"] = cls.cop
        os.environ["HOST_COMPAT_AGENTS_HOME"] = os.path.join(cls.tmp, "no_agents_home")
        os.environ["HOST_COMPAT_CLAUDE_HOME"] = cls.home
        os.environ["HOST_COMPAT_PROJECT"] = cls.proj
        os.environ["HOST_COMPAT_STORE"] = cls.store
        os.environ["HOST_COMPAT_TIMEOUT"] = "20"
        os.environ.pop("HOST_COMPAT_ROOTS", None)
        os.environ.pop("HOST_COMPAT_CONTEXT_CHARS", None)

        import importlib.util
        spec = importlib.util.spec_from_file_location("host_compat_agent_under_test", AGENT_PATH)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.agent = cls.mod.HostCompatAgent()
        cls.mod._get_catalog(force=True)

    @classmethod
    def tearDownClass(cls):
        for k in ("HOST_COMPAT_CLAUDE_HOME", "HOST_COMPAT_COPILOT_HOME", "HOST_COMPAT_AGENTS_HOME", "HOST_COMPAT_PROJECT",
                  "HOST_COMPAT_STORE", "HOST_COMPAT_TIMEOUT", "HOST_COMPAT_CONTEXT_CHARS"):
            os.environ.pop(k, None)
        shutil.rmtree(cls.tmp, ignore_errors=True)
        # remove any promoted agent we wrote into the real agents dir
        for fn in ("skill_blueprint_agent.py",):
            p = os.path.join(BRAINSTEM_DIR, "agents", fn)
            if os.path.exists(p):
                os.remove(p)

    # -- discovery -----------------------------------------------------------
    def test_frontmatter_parser(self):
        meta, body = self.mod._parse_frontmatter('---\nname: "x"\ndescription: >\n  a\n  b\nmetadata:\n  k: v\nlist:\n  - one\n  - two\nflag: true\n---\nBODY\n')
        self.assertEqual(meta["name"], "x")
        self.assertEqual(meta["description"], "a b")
        self.assertEqual(meta["metadata"], {"k": "v"})
        self.assertEqual(meta["list"], ["one", "two"])
        self.assertIs(meta["flag"], True)
        self.assertEqual(body, "BODY\n")
        self.assertEqual(self.mod._parse_frontmatter("no frontmatter"), ({}, "no frontmatter"))

    def test_list_all_sections(self):
        out = self.agent.perform(action="list")
        for needle in ("## Skills (", "blueprint", "folded", "projskill", "toolbox:hammer",
                       "## Slash commands / prompts (", "/greet", "/toolbox:nail",
                       "## Subagent personas (", "reviewer", "toolbox:carpenter",
                       "## Plugins (", "toolbox v1.0.0", "skills=1 commands=1 agents=1 hooks=2 mcp=1", "- broken v?",
                       "## Hooks (", "PreToolUse[Bash]",
                       "## MCP servers (", "fake [claude-code/plugin:toolbox]", "projfake [claude-code/project]",
                       "## Parse errors", "invalid JSON"):
            self.assertIn(needle, out, needle)

    def test_list_filters(self):
        out = self.agent.perform(action="list", kind="skills", query="nail")
        self.assertIn("toolbox:hammer", out)
        self.assertNotIn("blueprint", out)
        self.assertNotIn("## Plugins", out)

    def test_system_context_catalog_and_cap(self):
        ctx = self.agent.system_context()
        self.assertTrue(ctx.startswith("<host_compat>") and ctx.rstrip().endswith("</host_compat>"))
        self.assertIn("- blueprint: Draw a blueprint of a system", ctx)
        self.assertIn("MCP servers (", ctx)
        self.assertIn("fake, projfake", ctx)
        base = ctx.index("Skills (")  # fixed header length; budgets below are relative to it
        os.environ["HOST_COMPAT_CONTEXT_CHARS"] = str(base + 420)
        try:
            # tight budget: every entry survives in names-only form before anything is dropped
            small = self.agent.system_context()
            self.assertLessEqual(len(small), base + 420)
            self.assertNotIn("more entries", small)
            self.assertIn("Skills (", small)
            for name in ("blueprint", "folded", "projskill", "toolbox:hammer", "toolbox:carpenter"):
                self.assertIn(name, small)
            os.environ["HOST_COMPAT_CONTEXT_CHARS"] = str(base + 150)
            tiny = self.agent.system_context()
            self.assertLessEqual(len(tiny), base + 150)
            self.assertIn("more entries", tiny)
            os.environ["HOST_COMPAT_CONTEXT_CHARS"] = "0"
            self.assertIsNone(self.agent.system_context())
        finally:
            os.environ.pop("HOST_COMPAT_CONTEXT_CHARS")

    # -- load / read / run ---------------------------------------------------
    def test_load_skill_with_resources(self):
        out = self.agent.perform(action="load", name="blueprint")
        self.assertIn("# Skill: blueprint", out)
        self.assertIn("allowed-tools: Bash, Read", out)
        self.assertIn("references/rules.md", out)
        self.assertIn("scripts/draw.py", out)
        self.assertIn("Step 1: read references/rules.md", out)

    def test_load_plugin_qualified_and_short_names(self):
        self.assertIn("# Skill: toolbox:hammer", self.agent.perform(action="load", name="toolbox:hammer"))
        self.assertIn("# Skill: toolbox:hammer", self.agent.perform(action="load", name="hammer"))
        self.assertIn("Close matches", self.agent.perform(action="load", name="blue"))

    def test_load_command_substitutes_arguments(self):
        out = self.agent.perform(action="load", name="/greet", args="Kody and friends")
        self.assertIn("Say hello to Kody.", out)
        self.assertIn("Full args: Kody and friends", out)
        self.assertIn("argument-hint: <name>", out)

    def test_load_persona(self):
        out = self.agent.perform(action="load", name="reviewer")
        self.assertIn("Use this as a persona", out)
        self.assertIn("tools: Read, Grep", out)
        self.assertIn("You are a reviewer.", out)

    def test_read_confined(self):
        self.assertEqual(self.agent.perform(action="read", name="blueprint", path="references/rules.md").strip(),
                         "RULE: keep it simple")
        self.assertIn("Directory", self.agent.perform(action="read", name="blueprint", path="scripts"))
        out = self.agent.perform(action="read", name="blueprint", path="../../commands/greet.md")
        self.assertIn("escapes", out)
        self.assertNotIn("Say hello", out)

    def test_run_script(self):
        out = json.loads(self.agent.perform(action="run", name="blueprint", path="scripts/draw.py", args="a 'b c'"))
        self.assertEqual(out["exit"], 0)
        self.assertIn("drawn ['a', 'b c'] blueprint", out["stdout"])
        self.assertIn("Runnable files: scripts/draw.py", self.agent.perform(action="run", name="blueprint"))
        self.assertIn("escapes", self.agent.perform(action="run", name="blueprint", path="../../../etc/passwd"))

    def test_run_timeout(self):
        _w(os.path.join(self.home, "skills", "blueprint", "scripts", "slow.py"), "import time; time.sleep(5)\n")
        out = json.loads(self.agent.perform(action="run", name="blueprint", path="scripts/slow.py", timeout=1))
        self.assertIsNone(out["exit"])
        self.assertIn("timed out", out["stderr"])

    # -- hooks ---------------------------------------------------------------
    def test_hook_fires_with_plugin_root_and_matcher(self):
        out = json.loads(self.agent.perform(action="hook", name="Stop"))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["exit"], 0)
        self.assertIn("hooked-from-", out[0]["stdout"])
        self.assertIn("toolbox/1.0.0", out[0]["stdout"])
        self.assertIn("No hooks", self.agent.perform(action="hook", name="PreToolUse", args="Read"))
        out = json.loads(self.agent.perform(action="hook", name="PreToolUse", args="Bash"))
        self.assertIn("bash-only", out[0]["stdout"])

    # -- MCP -----------------------------------------------------------------
    def test_mcp_tools_and_call_over_stdio(self):
        out = self.agent.perform(action="mcp_tools", name="fake")
        self.assertIn("fake-mcp 0.1", out)
        self.assertIn("- echo: Echo text back  args: text", out)
        out = self.agent.perform(action="mcp_call", name="fake", tool="echo", arguments={"text": "ping"})
        self.assertEqual(out, "echo:ping")
        out = self.agent.perform(action="mcp_call", name="projfake", tool="echo", arguments='{"text": "pong"}')
        self.assertEqual(out, "echo:pong")
        self.assertIn("No MCP server named", self.agent.perform(action="mcp_tools", name="nope"))
        out = self.agent.perform(action="mcp_call", name="fake", tool="missing", arguments={})
        self.assertIn("MCP error", out)

    def test_mcp_server_that_dies_is_reported(self):
        _w(os.path.join(self.proj, ".mcp.json"), json.dumps({"mcpServers": {
            "projfake": {"command": sys.executable, "args": [os.path.join(self.home, "plugins", "cache", "mkt", "toolbox", "1.0.0", "fake_mcp.py")]},
            "dead": {"command": sys.executable, "args": ["-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"]}}}))
        self.mod._get_catalog(force=True)
        try:
            out = self.agent.perform(action="mcp_tools", name="dead")
            self.assertIn("exited", out)
            self.assertIn("boom", out)
        finally:
            _w(os.path.join(self.proj, ".mcp.json"), json.dumps({"mcpServers": {"projfake": {
                "command": sys.executable, "args": [os.path.join(self.home, "plugins", "cache", "mkt", "toolbox", "1.0.0", "fake_mcp.py")]}}}))
            self.mod._get_catalog(force=True)

    # -- install / uninstall -------------------------------------------------
    def test_install_plugin_and_bare_skill(self):
        src = os.path.join(self.tmp, "newplug")
        _w(os.path.join(src, "plugin.json"), json.dumps({"name": "newplug", "version": "2.0"}))
        _w(os.path.join(src, "skills", "wrench", "SKILL.md"), "---\nname: wrench\ndescription: Turn bolts.\n---\nturn\n")
        out = self.agent.perform(action="install", source=src)
        self.assertIn("Installed plugin 'newplug' v2.0", out)
        self.assertIn("skills=1", out)
        self.assertIn("# Skill: newplug:wrench", self.agent.perform(action="load", name="wrench"))
        bare = os.path.join(self.tmp, "bare-skill")
        _w(os.path.join(bare, "SKILL.md"), "---\nname: bare\ndescription: Bare.\n---\nbare body\n")
        out = self.agent.perform(action="install", source=bare)
        self.assertIn("Installed bare skill 'bare' as plugin 'bare'", out)
        self.assertIn("bare body", self.agent.perform(action="load", name="bare:bare"))
        self.assertIn("Removed plugin 'bare'", self.agent.perform(action="uninstall", name="bare"))
        self.assertIn("No skill", self.agent.perform(action="load", name="bare:bare"))
        self.assertIn("not a directory", self.agent.perform(action="install", source="/definitely/not/here"))
        self.assertIn("Removed plugin 'newplug'", self.agent.perform(action="uninstall", name="newplug"))

    # -- promote / export ----------------------------------------------------
    def test_promote_skill_to_native_agent_loads_in_brainstem(self):
        out = self.agent.perform(action="promote", name="blueprint")
        self.assertIn("SkillBlueprint", out)
        path = os.path.join(BRAINSTEM_DIR, "agents", "skill_blueprint_agent.py")
        self.assertTrue(os.path.exists(path))
        import brainstem
        loaded = brainstem._load_agent_from_file(path)
        self.assertIn("SkillBlueprint", loaded)
        inst = loaded["SkillBlueprint"]
        self.assertIsNone(brainstem._validate_agent_instance(inst))
        body = inst.perform(task="sketch the auth flow")
        self.assertIn("User task: sketch the auth flow", body)
        self.assertIn("Step 1: read references/rules.md", body)
        self.assertIn("Bundled files", body)
        self.assertEqual(inst.perform(read="references/rules.md").strip(), "RULE: keep it simple")
        res = json.loads(inst.perform(script="scripts/draw.py", args="z"))
        self.assertEqual(res["exit"], 0)
        self.assertIn("drawn ['z']", res["stdout"])
        self.assertIn("escapes", inst.perform(read="../../commands/greet.md"))

    def test_export_agent_to_skill_runs_standalone(self):
        out = self.agent.perform(action="export", name="hacker_news_agent", path=os.path.join(self.tmp, "exported"))
        self.assertIn("Exported", out)
        sdir = [d for d in os.listdir(os.path.join(self.tmp, "exported"))][0]
        sd = os.path.join(self.tmp, "exported", sdir)
        skill_md = open(os.path.join(sd, "SKILL.md")).read()
        meta, body = self.mod._parse_frontmatter(skill_md)
        self.assertEqual(meta["name"], sdir)
        self.assertTrue(meta["description"])
        self.assertIn("agent-sha256", meta["metadata"])
        # byte-identical carry
        self.assertEqual(open(os.path.join(sd, "scripts", "agent.py"), "rb").read(),
                         open(os.path.join(BRAINSTEM_DIR, "agents", "hacker_news_agent.py"), "rb").read())
        # the exported skill is itself discoverable and loadable
        self.assertIn("Installed bare skill", self.agent.perform(action="install", source=sd))
        self.assertIn("scripts/run.py", self.agent.perform(action="load", name=sdir))
        # and the standalone runner imports the agent without a Brainstem
        p = subprocess.run([sys.executable, os.path.join(sd, "scripts", "run.py"), "--json", "{}"],
                           capture_output=True, text=True, timeout=60, cwd=sd)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(p.stdout.strip())
        self.assertIn("Removed plugin", self.agent.perform(action="uninstall", name=sdir))

    # -- copilot cli host ----------------------------------------------------
    def test_copilot_catalog_discovered_and_host_filter(self):
        out = self.agent.perform(action="list", host="copilot-cli")
        for needle in ("- ledger [copilot-cli/user]", "- ghskill [copilot-cli/project]", "cop-tools:saw [copilot-cli/plugin:cache]",
                       "- /release [copilot-cli/project] — Cut a release", "- planner [copilot-cli/project]",
                       "solo:helper [copilot-cli/plugin:cache]", "cop-tools v3.1 [copilot-cli/cache]",
                       "- sessionStart (copilot-cli/", "- copfake [copilot-cli/user:copilot-cli] local:",
                       "copilot-instructions.md [copilot-cli]", "AGENTS.md [copilot-cli]"):
            self.assertIn(needle, out, needle)
        self.assertNotIn("blueprint", out)          # claude-only skill filtered out
        self.assertNotIn("CLAUDE.md", out)
        both = self.agent.perform(action="list", kind="skills")
        self.assertIn("blueprint", both)
        self.assertIn("ledger", both)
        # symlinked duplicate reachable via .agents/skills collapses to one entry
        self.assertEqual(both.count("- blueprint ["), 1)

    def test_copilot_prompt_input_substitution_and_persona(self):
        out = self.agent.perform(action="load", name="release", args="1.2.3 --dry")
        self.assertIn("Release version 1.2.3 --dry now.", out)
        self.assertIn("Args: 1.2.3 --dry", out)
        self.assertIn("mode: agent", out)
        out = self.agent.perform(action="load", name="planner")
        self.assertIn("Host: copilot-cli", out)
        self.assertIn("model: gpt-5", out)
        self.assertIn("Use this as a persona", out)

    def test_copilot_mcp_local_type_is_stdio(self):
        self.assertEqual(self.agent.perform(action="mcp_call", name="copfake", tool="echo", arguments={"text": "cop"}), "echo:cop")

    def test_copilot_hook_and_instructions(self):
        out = json.loads(self.agent.perform(action="hook", name="sessionStart"))
        self.assertEqual(out[0]["host"], "copilot-cli")
        self.assertIn("copilot-session-start", out[0]["stdout"])
        out = self.agent.perform(action="instructions")
        self.assertIn("Always be terse.", out)
        self.assertIn("Repo agent rules.", out)
        self.assertIn("Claude rules.", out)
        only = self.agent.perform(action="instructions", host="copilot-cli")
        self.assertNotIn("Claude rules.", only)

    def test_promote_copilot_skill(self):
        out = self.agent.perform(action="promote", name="ledger")
        self.assertIn("(copilot-cli)", out)
        path = os.path.join(BRAINSTEM_DIR, "agents", "skill_ledger_agent.py")
        try:
            import brainstem
            loaded = brainstem._load_agent_from_file(path)
            self.assertIn("ledger body", loaded["SkillLedger"].perform(task="go"))
        finally:
            os.remove(path)

    # -- transcripts (both hosts) --------------------------------------------
    def test_transcripts_search_across_both_hosts(self):
        out = self.agent.perform(action="transcripts", query="zebra")
        self.assertIn("[claude-code]", out)
        self.assertIn("[copilot-cli]", out)
        self.assertIn("session=aaaa1111", out)
        self.assertIn("session=bbbb2222", out)
        self.assertIn("title='Zebra CLI fixes'", out)
        self.assertNotIn("ancient", out)             # outside the 30-day window
        self.assertNotIn("indexed from tools", out)  # tool events are not messages
        self.assertNotIn("secret", out)              # thinking blocks never indexed
        self.assertNotIn("pelican meta noise", out)  # isMeta rows skipped
        self.assertIn("Zebra migration plan", out)   # claude summary becomes the title
        # AND semantics + role + host + cwd filters
        both = self.agent.perform(action="transcripts", query="zebra rollback")
        self.assertIn("2 hit(s)", both)                # both aaaa1111 messages carry both words
        self.assertNotIn("[copilot-cli]", both)        # the copilot session never says "rollback"
        self.assertIn("0 hit(s)", self.agent.perform(action="transcripts", query="zebra pelican untouched rollback"))
        self.assertIn("0 hit(s)", self.agent.perform(action="transcripts", query="zebra", host="copilot-cli", role="user", cwd="nomatch"))
        one = self.agent.perform(action="transcripts", query="zebra", host="copilot-cli", role="user")
        self.assertIn("1 hit(s)", one)
        self.assertIn("CLI flag parsing", one)
        self.assertIn("Pass query=", self.agent.perform(action="transcripts"))

    def test_transcript_read_and_index_is_incremental(self):
        out = self.agent.perform(action="transcript", name="bbbb2222")
        self.assertIn("cwd=/work/zebra-cli", out)
        self.assertIn("USER: copilot please fix", out)
        self.assertIn("ASSISTANT: Fixed the zebra flag parser", out)
        self.assertNotIn("toolRequests", out)
        out = self.agent.perform(action="transcript", name="aaaa1111")
        self.assertIn("ASSISTANT: Zebra migration: three phases", out)
        self.assertNotIn("secret", out)
        self.assertIn("No indexed session", self.agent.perform(action="transcript", name="zzzz"))
        first = self.agent.perform(action="index")
        self.assertIn("indexed 0 session file(s)", first)   # already indexed by the searches above
        self.assertIn("Index is complete", first)
        # a new session shows up on the next search without a manual index
        sdir = os.path.join(self.cop, "session-state", "dddd4444-0000-0000-0000-000000000004")
        _w(os.path.join(sdir, "events.jsonl"), json.dumps({"type": "user.message", "timestamp": "2026-09-05T00:00:00Z",
                                                            "data": {"content": "brand new okapi question"}}) + "\n")
        self.assertIn("session=dddd4444", self.agent.perform(action="transcripts", query="okapi"))
        wide = self.agent.perform(action="transcripts", query="ancient", days=2000)
        self.assertIn("session=cccc3333", wide)

    # -- misc ----------------------------------------------------------------
    def test_doctor_and_unknown_action(self):
        out = self.agent.perform(action="doctor")
        self.assertIn("HostCompat doctor", out)
        self.assertIn(self.home, out)
        self.assertIn("[copilot-cli]: home=" + self.cop, out)
        self.assertIn("transcript index: FTS5", out)
        self.assertIn("Unknown action", self.agent.perform(action="explode"))
        self.assertIn("Catalog rebuilt", self.agent.perform(action="refresh"))

    def test_agent_passes_brainstem_loader(self):
        import brainstem
        loaded = brainstem._load_agent_from_file(AGENT_PATH)
        self.assertEqual(list(loaded), ["HostCompat"])
        self.assertIsNone(brainstem._validate_agent_instance(loaded["HostCompat"]))
        tool = loaded["HostCompat"].to_tool()
        self.assertEqual(tool["function"]["name"], "HostCompat")


if __name__ == "__main__":
    unittest.main()
