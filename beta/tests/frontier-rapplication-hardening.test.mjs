import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";

function runPython(source) {
  const result = spawnSync("python3", ["-c", source], {
    cwd: new URL("..", import.meta.url),
    encoding: "utf8",
  });
  assert.equal(result.status, 0, result.stderr || result.stdout);
}

const importStub = String.raw`
import importlib.util
import sys
import types

agents = types.ModuleType("agents")
basic_agent = types.ModuleType("agents.basic_agent")
class BasicAgent:
    def __init__(self, name=None, metadata=None):
        if name is not None:
            self.name = name
        if metadata is not None:
            self.metadata = metadata
basic_agent.BasicAgent = BasicAgent
agents.basic_agent = basic_agent
sys.modules["agents"] = agents
sys.modules["agents.basic_agent"] = basic_agent

def load(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
`;

test("migration scaffolds encode hostile client strings as inert Python literals", () => {
  runPython(importStub + String.raw`
import pathlib
import tempfile

module = load(
    "frontier/rapplications/agent-migration/agents/agent_migration_agent.py",
    "agent_migration_agent",
)
with tempfile.TemporaryDirectory() as directory:
    marker = pathlib.Path(directory) / "payload-ran"
    payload_name = (
        '"+__import__("pathlib").Path(' + repr(str(marker))
        + ').write_text("owned")+"'
    )
    hostile_names = [payload_name, 'line one\n"""\nline two']
    for hostile_name in hostile_names:
        _, source = module.emit_rapp_agent({
            "name": hostile_name,
            "description": '"; description_payload()',
            "parameters": {"type": "object", "properties": {}},
            "system": '"""\n__import__("os").system("false")',
        }, "openai")
        compile(source, "hostile_agent.py", "exec")
        namespace = {}
        exec(source, namespace)
        generated = next(
            value for key, value in namespace.items()
            if key.endswith("Agent") and key != "BasicAgent"
        )
        result = generated().perform(value="safe")
        assert hostile_name in result
        assert result.startswith("MIGRATION SCAFFOLD for '")
    assert not marker.exists()
`);
});

test("code-app scaffold keeps hostile names inside their generated contexts", () => {
  runPython(importStub + String.raw`
import html
import json
import re

module = load(
    "frontier/rapplications/agentic-app-studio/agents/agentic_app_studio_agent.py",
    "agentic_app_studio_agent",
)
for name in ['</title><script>alert(1)</script>', '"; evil()\nnext line']:
    files = module.code_app_scaffold(name, "safe-slug")
    page = files["index.html"]
    assert page.count("<title>") == 1
    assert page.count("</title>") == 1
    assert f"<title>{html.escape(name)}</title>" in page
    assert "<script>alert(1)</script>" not in page

    app = files["src/App.tsx"]
    literal = re.search(r"^const APP_NAME = (.+);$", app, re.MULTILINE).group(1)
    assert json.loads(literal) == name
    assert "<h1>{APP_NAME}</h1>" in app

    deploy = files["DEPLOY.md"]
    assert f"<code>{html.escape(json.dumps(name))}</code>" in deploy
    assert f'--displayName "{name}"' not in deploy
`);
});

test("code-app deploy pins dependencies and disables npm lifecycle scripts", () => {
  runPython(importStub + String.raw`
import json
import pathlib
import re
import tempfile
import types

module = load(
    "frontier/rapplications/agentic-app-studio/agents/agentic_app_studio_agent.py",
    "agentic_app_studio_agent_dependencies",
)
files = module.code_app_scaffold("Safe App", "safe-app")
package = json.loads(files["package.json"])
dependencies = package["dependencies"] | package["devDependencies"]
assert dependencies
for dependency, version in dependencies.items():
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version), (
        f"{dependency} is not exact-pinned: {version}"
    )

deploy_doc = files["DEPLOY.md"]
assert "npm install --ignore-scripts --no-audit --no-fund" in deploy_doc
assert "lifecycle scripts are disabled during deploy by design" in deploy_doc
assert "package-lock.json" in deploy_doc

with tempfile.TemporaryDirectory() as directory:
    pathlib.Path(directory, "power.config.json").write_text("{}", encoding="utf-8")
    state = {
        "app": {"name": "Safe App", "root": directory},
        "deploys": [],
    }
    module._load_state = lambda: state
    module._save_state = lambda _state: None
    module.shutil.which = lambda command: "/usr/local/bin/pac" if command == "pac" else None
    commands = []

    def run(command, **_kwargs):
        commands.append(command)
        stdout = "Safe App\n" if command[-2:] == ["code", "list"] else "Authenticated\n"
        return types.SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    module.subprocess.run = run
    result = module.AgenticAppStudioAgent()._deploy({})
    assert result.startswith("Deployed AND VERIFIED")
    assert ["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund"] in commands
`);
});

test("agentic app studio refuses unsafe RAR URLs without exposing fetched digests", () => {
  runPython(importStub + String.raw`
import tempfile

module = load(
    "frontier/rapplications/agentic-app-studio/agents/agentic_app_studio_agent.py",
    "agentic_app_studio_agent_urls",
)
assert {type(handler).__name__ for handler in module._NETWORK_OPENER.handlers} == {
    "HTTPHandler", "HTTPSHandler",
}

pin = "0" * 64
for singleton_url in (
    "file:///etc/passwd",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
):
    module._fetch = lambda _url, bad=singleton_url: {
        "rapplications": [{
            "id": "hostile",
            "singleton_url": bad,
            "singleton_sha256": pin,
        }]
    }
    try:
        module._rar_entries("https://catalog.example/index.json")
    except ValueError as error:
        assert "HTTPS or loopback HTTP" in str(error)
    else:
        raise AssertionError(f"unsafe singleton_url was accepted: {singleton_url}")

module._fetch = lambda _url: {"agents": []}
for rar_url in ("file:///tmp/catalog.json", "http://169.254.169.254/catalog.json"):
    try:
        module._rar_entries(rar_url)
    except ValueError as error:
        assert "HTTPS or loopback HTTP" in str(error)
    else:
        raise AssertionError(f"unsafe RAR catalog URL was accepted: {rar_url}")

with tempfile.TemporaryDirectory() as directory:
    module.HOME = directory
    module.STATE_FILE = directory + "/state.json"
    payload = b"content-oracle-probe"
    computed = module.sha256(payload).hexdigest()
    module._rar_entries = lambda _url: [{
        "id": "mismatch",
        "name": "Mismatch",
        "url": "https://catalog.example/mismatch_agent.py",
        "sha256": pin,
        "filename": "mismatch_agent.py",
    }]
    module._fetch = lambda _url, as_bytes=False, timeout=30: payload
    result = module.AgenticAppStudioAgent()._add({
        "source": "rar",
        "name": "mismatch",
        "rar_url": "https://catalog.example/index.json",
    })
    assert "do not match the catalog singleton_sha256" in result
    assert computed[:12] not in result
`);
});

test("agentic app studio rechecks disambiguated filenames until one is free", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/agentic-app-studio/agents/agentic_app_studio_agent.py",
    "agentic_app_studio_agent_filenames",
)
entry = {
    "id": "demo",
    "filename": "demo_agent.py",
    "origin": "rar:https://catalog.example/demo_agent.py",
}
tag = module.sha256(entry["origin"].encode()).hexdigest()[:8]
taken = {
    "demo_agent.py",
    f"demo_agent__{tag}.py",
    f"demo_agent__{tag}_2.py",
}
state = {
    "agents": [
        {"id": str(index), "origin": f"other:{index}", "filename": filename}
        for index, filename in enumerate(sorted(taken))
    ]
}
result = module._unique_filename(state, entry)
assert result == f"demo_agent__{tag}_3.py"
assert result not in taken
`);
});

test("molter verifier accepts a genuine minimal BasicAgent candidate", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_valid_candidate",
)
source = """
from agents.basic_agent import BasicAgent

class MinimalAgent(BasicAgent):
    def __init__(self):
        self.name = "MinimalTool"
        self.metadata = {
            "name": self.name,
            "parameters": {"type": "object", "properties": {}},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        return "ok"
"""
ok, detail = module._verify(source)
assert ok, detail
assert detail == {
    "ok": True,
    "agent_class": "MinimalAgent",
    "tool_name": "MinimalTool",
}
`);
});

test("molter verifier rejects candidate stdout that asserts success", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_spoofed_stdout",
)
source = """
print('{"ok": true, "loaded": true, "agent_class": "SpoofedAgent", "tool_name": "Spoofed"}')

class SpoofedAgent:
    metadata = {
        "name": "Spoofed",
        "parameters": {"type": "object", "properties": {}},
    }

    def perform(self, **kwargs):
        return "not a BasicAgent"
"""
ok, detail = module._verify(source)
assert not ok
assert "no BasicAgent subclass" in detail["lesson"]
`);
});

test("molter verifier: stdout / an inherited fd / os._exit cannot forge a verdict", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_forged_verdict",
)
# The old bypass wrote a fake 'verified' verdict to an inherited report fd and
# called os._exit(0) before the harness could speak. The verdict is now decided by
# the parent's AST analysis, and this source defines no BasicAgent subclass, so it
# is rejected BEFORE the process is ever run — the forgery code never executes.
source = """
import os
try:
    os.write(3, b'{"loaded": true, "is_basic_agent_subclass": true, "agent_class": "Pwn", "has_perform": true, "error": null}')
except Exception:
    pass
os._exit(0)
"""
ok, detail = module._verify(source)
assert not ok
assert "no BasicAgent subclass" in detail["lesson"]
`);
});

test("molter verifier fails closed when an AST-valid candidate cannot instantiate", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_init_raises",
)
source = """
from agents.basic_agent import BasicAgent

class BoomAgent(BasicAgent):
    def __init__(self):
        raise RuntimeError("kaboom during init")

    def perform(self, **kwargs):
        return "never"
"""
ok, detail = module._verify(source)
assert not ok
assert "failed to load cleanly" in detail["lesson"]
`);
});

test("molter verifier refuses a decoy base named BasicAgent (fake lineage)", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_shadow_base",
)
# 'BasicAgent' is shadowed to object, so the class is not a real kernel subclass,
# and it os._exit(0)s to fake a clean subprocess load. The AST gate refuses it
# because BasicAgent is not imported from the kernel module (and is reassigned) —
# the os._exit never even runs.
source = """
import os
BasicAgent = object

class Pwn(BasicAgent):
    def perform(self, **kwargs):
        return "decoy"

os._exit(0)
"""
ok, detail = module._verify(source)
assert not ok
assert "imported from agents.basic_agent" in detail["lesson"]
`);
});

test("molter verifier refuses a sterile molt with no perform()", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_sterile",
)
# A genuine BasicAgent subclass but with no perform() of its own — it cannot act,
# so it is a sterile molt and is refused at the AST gate (before the os._exit runs).
source = """
import os
from agents.basic_agent import BasicAgent

class Sterile(BasicAgent):
    pass

os._exit(0)
"""
ok, detail = module._verify(source)
assert not ok
assert "does not define perform()" in detail["lesson"]
`);
});

test("molter installs live only in the marked twin's real agents directory", () => {
  runPython(importStub + String.raw`
import os

module = load(
    "frontier/rapplications/molter/agents/molter_agent.py",
    "molter_agent_isolation",
)
prior = os.environ.pop("BRAINSTEM_BETA_TWIN", None)
try:
    assert module.MolterAgent._is_sacred_brainstem("/tmp/frontier/twins/twin-1/agents")
    os.environ["BRAINSTEM_BETA_TWIN"] = "twin-1"
    assert not module.MolterAgent._is_sacred_brainstem("/tmp/frontier/twins/twin-1/agents")
    assert module.MolterAgent._is_sacred_brainstem("/tmp/frontier/twins/other/agents")
    assert module.MolterAgent._is_sacred_brainstem(
        "/tmp/frontier/twins/twin-1/work/rapp_brainstem/agents"
    )
finally:
    if prior is None:
        os.environ.pop("BRAINSTEM_BETA_TWIN", None)
    else:
        os.environ["BRAINSTEM_BETA_TWIN"] = prior
`);
});

test("toaster keeps hostile skill names inert in generated Python", () => {
  runPython(importStub + String.raw`
import pathlib
import tempfile

module = load(
    "frontier/rapplications/toaster/agents/toaster_agent.py",
    "toaster_agent_literals",
)
with tempfile.TemporaryDirectory() as directory:
    marker = pathlib.Path(directory) / "payload-ran"
    hostile_name = (
        '"+__import__("pathlib").Path(' + repr(str(marker))
        + ').write_text("owned")+"'
    )
    source = module._wrap_skill_as_agent(
        hostile_name,
        '"; __import__("os").system("false")',
        "Follow the safe instructions.",
    )
    compile(source, "toasted_agent.py", "exec")
    namespace = {}
    exec(source, namespace)
    generated = next(
        value for key, value in namespace.items()
        if key.endswith("Agent") and key != "BasicAgent"
    )
    result = generated().perform()
    assert hostile_name in result
    assert not marker.exists()
`);
});

test("toaster exports one authoritative embedded block despite sentinel text", () => {
  runPython(importStub + String.raw`
import base64
import pathlib
import tempfile

module = load(
    "frontier/rapplications/toaster/agents/toaster_agent.py",
    "toaster_agent_sentinels",
)
decoy = base64.b64encode(b"print('decoy')\n").decode("ascii")
description = (
    module._EMBED_OPEN + "\n" + decoy + "\n" + module._EMBED_CLOSE
)
source = (
    "__manifest__ = " + repr({
        "name": "@test/sentinel",
        "display_name": "Sentinel test",
        "description": description,
    }) + "\n"
    "class SentinelAgent(BasicAgent):\n"
    "    def __init__(self):\n"
    "        self.name = 'Sentinel'\n"
    "        self.metadata = {'name': self.name, 'parameters': {}}\n"
    "        super().__init__(name=self.name, metadata=self.metadata)\n"
    "    def perform(self, **kwargs):\n"
    "        return 'safe'\n"
)
with tempfile.TemporaryDirectory() as directory:
    module.OUT = directory
    result = module.ToasterAgent()._export({"source": source})
    assert result.startswith("Exported ")
    skill = next(pathlib.Path(directory).glob("*_skill.md")).read_text(encoding="utf-8")
    assert skill.count(module._EMBED_OPEN) == 1
    assert skill.count(module._EMBED_CLOSE) == 1
    assert module._extract_embedded_agent(skill) == source
`);
});

test("UI Smith escapes script literals, rejects markup, and verifies escaped names", () => {
  runPython(importStub + String.raw`
module = load(
    "frontier/rapplications/ui-smith/agents/ui_smith_agent.py",
    "ui_smith_agent_script_safety",
)
hostile = {
    "tool": 'Bad</script><img src=1 onerror=alert(1)>',
    "display": "Bad tool",
    "description": "Hostile tool name",
    "params": [],
}
html = module._render_ui(hostile)
assert html.count("</script>") == 1
assert "</script><img" not in html
assert "\\u003c/script>" in html
ok, lesson = module._verify_ui(html, hostile)
assert not ok
assert "unsafe HTML markup" in lesson

escaped = {
    "tool": 'Quoted"\\Tool',
    "display": "Quoted tool",
    "description": "Safe punctuation",
    "params": [],
}
escaped_html = module._render_ui(escaped)
assert module._verify_ui(escaped_html, escaped) == (True, "ok")
assert "const TOOL = " + module._script_string(escaped["tool"]) + ";" in escaped_html
`);
});

test("UI Smith replaces the archived schema when an agent schema changes", () => {
  runPython(importStub + String.raw`
import json
import tempfile

module = load(
    "frontier/rapplications/ui-smith/agents/ui_smith_agent.py",
    "ui_smith_agent_schema_refresh",
)
schemas = iter([
    {
        "tool": "ChangingTool",
        "display": "Changing",
        "description": "First",
        "params": [{"name": "old", "type": "string", "enum": None,
                    "required": True, "description": "", "long": False}],
    },
    {
        "tool": "ChangingTool",
        "display": "Changing",
        "description": "Second",
        "params": [{"name": "current", "type": "string", "enum": None,
                    "required": True, "description": "", "long": False}],
    },
])
module._agent_schema = lambda _source: next(schemas)
with tempfile.TemporaryDirectory() as directory:
    module.HOME = directory
    module.UIS = directory + "/uis"
    module.STATE_FILE = directory + "/state.json"
    agent = module.UiSmithAgent()
    agent._generate({"agent_source": "first"})
    agent._generate({"agent_source": "second"})
    state = json.loads(open(module.STATE_FILE, encoding="utf-8").read())
    entry = state["uis"]["changingtool"]
    assert entry["schema"]["params"][0]["name"] == "current"
    assert len(entry["gens"]) == 2
`);
});
