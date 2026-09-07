#!/usr/bin/env python3
"""Hermetic tests for agents/claude_compat_agent.py.

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

AGENT_PATH = os.path.join(BRAINSTEM_DIR, "agents", "claude_compat_agent.py")

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


class TestClaudeCompat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="claude_compat_")
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

        os.environ["CLAUDE_COMPAT_HOME"] = cls.home
        os.environ["CLAUDE_COMPAT_PROJECT"] = cls.proj
        os.environ["CLAUDE_COMPAT_STORE"] = cls.store
        os.environ["CLAUDE_COMPAT_TIMEOUT"] = "20"
        os.environ.pop("CLAUDE_COMPAT_ROOTS", None)
        os.environ.pop("CLAUDE_COMPAT_CONTEXT_CHARS", None)

        import importlib.util
        spec = importlib.util.spec_from_file_location("claude_compat_agent_under_test", AGENT_PATH)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.agent = cls.mod.ClaudeCompatAgent()
        cls.mod._get_catalog(force=True)

    @classmethod
    def tearDownClass(cls):
        for k in ("CLAUDE_COMPAT_HOME", "CLAUDE_COMPAT_PROJECT", "CLAUDE_COMPAT_STORE", "CLAUDE_COMPAT_TIMEOUT",
                  "CLAUDE_COMPAT_CONTEXT_CHARS"):
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
                       "## Slash commands (2)", "/greet", "/toolbox:nail",
                       "## Subagent personas (2)", "reviewer", "toolbox:carpenter",
                       "## Plugins (", "toolbox v1.0.0", "skills=1 commands=1 agents=1 hooks=2 mcp=1", "- broken v?",
                       "## Hooks (2)", "PreToolUse[Bash]",
                       "## MCP servers (", "fake [plugin:toolbox]", "projfake [project]",
                       "## Parse errors", "invalid JSON"):
            self.assertIn(needle, out, needle)

    def test_list_filters(self):
        out = self.agent.perform(action="list", kind="skills", query="nail")
        self.assertIn("toolbox:hammer", out)
        self.assertNotIn("blueprint", out)
        self.assertNotIn("## Plugins", out)

    def test_system_context_catalog_and_cap(self):
        ctx = self.agent.system_context()
        self.assertTrue(ctx.startswith("<claude_compat>") and ctx.rstrip().endswith("</claude_compat>"))
        self.assertIn("- blueprint: Draw a blueprint of a system", ctx)
        self.assertIn("MCP servers (", ctx)
        self.assertIn("fake, projfake", ctx)
        os.environ["CLAUDE_COMPAT_CONTEXT_CHARS"] = "700"
        try:
            # tight budget: every entry survives in names-only form before anything is dropped
            small = self.agent.system_context()
            self.assertLessEqual(len(small), 700)
            self.assertNotIn("more entries", small)
            self.assertIn("Skills (", small)
            for name in ("blueprint", "folded", "projskill", "toolbox:hammer", "toolbox:carpenter"):
                self.assertIn(name, small)
            os.environ["CLAUDE_COMPAT_CONTEXT_CHARS"] = "520"
            tiny = self.agent.system_context()
            self.assertLessEqual(len(tiny), 520)
            self.assertIn("more entries", tiny)
            os.environ["CLAUDE_COMPAT_CONTEXT_CHARS"] = "0"
            self.assertIsNone(self.agent.system_context())
        finally:
            os.environ.pop("CLAUDE_COMPAT_CONTEXT_CHARS")

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

    # -- misc ----------------------------------------------------------------
    def test_doctor_and_unknown_action(self):
        out = self.agent.perform(action="doctor")
        self.assertIn("ClaudeCompat doctor", out)
        self.assertIn(self.home, out)
        self.assertIn("Unknown action", self.agent.perform(action="explode"))
        self.assertIn("Catalog rebuilt", self.agent.perform(action="refresh"))

    def test_agent_passes_brainstem_loader(self):
        import brainstem
        loaded = brainstem._load_agent_from_file(AGENT_PATH)
        self.assertEqual(list(loaded), ["ClaudeCompat"])
        self.assertIsNone(brainstem._validate_agent_instance(loaded["ClaudeCompat"]))
        tool = loaded["ClaudeCompat"].to_tool()
        self.assertEqual(tool["function"]["name"], "ClaudeCompat")


if __name__ == "__main__":
    unittest.main()
