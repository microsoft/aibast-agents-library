"""Deploy an AIBAST library solution to the user's own Copilot Studio environment.

One file, two front ends:
- Brainstem loads it as an agent (CopilotStudioDeploy).
- GitHub Copilot runs it from the terminal through the skill:
  python3 copilot_studio_deploy_agent.py <check|envs|plan|deploy|undo> ...

It drives the Power Platform CLI (pac) under the user's own sign-in. It never
stores credentials, never overwrites an existing solution without --replace,
and never changes anything unless confirm/--yes is given.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from basic_agent import BasicAgent
except ImportError:  # running as a plain script outside Brainstem
    class BasicAgent:  # type: ignore[no-redef]
        def __init__(self, name=None, metadata=None):
            self.name, self.metadata = name, metadata


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/copilot-studio-deploy",
    "version": "0.1.0",
    "display_name": "Deploy to Copilot Studio",
    "description": (
        "Deploys an AIBAST library solution into the user's own Copilot Studio "
        "environment with their own sign-in: checks first, imports, publishes, "
        "and can undo."
    ),
    "author": "AIBAST",
    "tags": ["copilot-studio", "deploy", "power-platform"],
    "category": "general",
    "quality_tier": "pilot",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

DEFAULT_RAW_BASE = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
PAC_TIMEOUT = 900


class DeployError(Exception):
    pass


# ---------------------------------------------------------------- pac helpers
def _pac() -> str:
    found = shutil.which("pac") or os.path.expanduser("~/.dotnet/tools/pac")
    if not os.path.exists(found):
        raise DeployError(
            "The Power Platform CLI (pac) is not installed. Install it with "
            "'dotnet tool install --global Microsoft.PowerApps.CLI.Tool' or the "
            "Windows installer, then try again."
        )
    return found


def _run(args: list[str], timeout: int = PAC_TIMEOUT) -> str:
    proc = subprocess.run([_pac(), *args], capture_output=True, text=True, timeout=timeout)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or re.search(r"^Error:", out, re.M):
        last = [l for l in out.strip().splitlines() if l.strip()][-3:]
        raise DeployError("pac " + " ".join(args[:2]) + " failed: " + " ".join(last))
    return out


# ---------------------------------------------------------- package handling
def _fetch(rel: str, source: str) -> bytes:
    if source.startswith("http"):
        with urllib.request.urlopen(source.rstrip("/") + "/" + rel, timeout=60) as r:
            return r.read()
    with open(os.path.join(source, rel), "rb") as fh:
        return fh.read()


def load_package(slug: str, source: str = DEFAULT_RAW_BASE) -> dict:
    if not re.fullmatch(r"[a-z0-9-]+", slug or ""):
        raise DeployError("Solution name must look like 'tiered-huddle-board'.")
    base = f"solutions/{slug}/exports/{slug}"
    try:
        zbytes = _fetch(base + "-copilot-studio-solution.zip", source)
        settings = json.loads(_fetch(base + "-deployment-settings.json", source))
    except Exception as exc:  # noqa: BLE001
        raise DeployError(f"No deployable package found for '{slug}' ({exc}).") from exc
    xml = zipfile.ZipFile(io.BytesIO(zbytes)).read("solution.xml").decode("utf-8", "ignore")
    unique = re.search(r"<UniqueName>([^<]+)</UniqueName>", xml).group(1)
    version = re.search(r"<Version>([^<]+)</Version>", xml).group(1)
    return {"slug": slug, "zip": zbytes, "settings": settings,
            "unique_name": unique, "version": version,
            "agents": [a["Name"] for a in settings.get("CopilotAgents", [])],
            "connectors": [c["ConnectorId"].rsplit("/", 1)[-1]
                           for c in settings.get("ConnectionReferences", [])]}


# --------------------------------------------------------------- operations
def check() -> dict:
    who = _run(["auth", "who"], timeout=120)
    user = re.search(r"User:\s*(\S+)", who)
    env = re.search(r"Organization Friendly Name:\s*(.+)", who)
    return {"ok": True, "signed_in_as": user.group(1) if user else "unknown",
            "active_environment": env.group(1).strip() if env else None,
            "summary": "Signed in. Ready to list environments."}


def envs() -> dict:
    rows = []
    for line in _run(["env", "list"], timeout=180).splitlines():
        m = re.search(r"^\s*\*?\s*(.+?)\s{2,}([0-9a-f-]{36})\s+(https://\S+)", line)
        if m:
            rows.append({"name": m.group(1).strip(), "id": m.group(2), "url": m.group(3)})
    return {"ok": True, "environments": rows,
            "summary": f"{len(rows)} environments you can use. Pick one by name."}


def _resolve_env(env: str) -> str:
    if env.startswith("https://") or re.fullmatch(r"[0-9a-f-]{36}", env or ""):
        return env
    for row in envs()["environments"]:
        if row["name"].lower() == (env or "").lower():
            return row["url"]
    raise DeployError(f"No environment named '{env}'. Run 'envs' to see the list.")


def plan(slug: str, env: str, source: str = DEFAULT_RAW_BASE) -> dict:
    url = _resolve_env(env)
    pkg = load_package(slug, source)
    existing = pkg["unique_name"] in _run(["solution", "list", "--environment", url], timeout=300)
    conns = _run(["connection", "list", "--environment", url], timeout=300)
    needs = []
    for c in pkg["connectors"]:
        match = [l.split()[0] for l in conns.splitlines() if f"/apis/{c}" in l and "Connected" in l]
        needs.append({"connector": c, "available_connection": match[0] if match else None})
    missing = [n["connector"] for n in needs if not n["available_connection"]]
    steps = [f"Import solution {pkg['unique_name']} {pkg['version']} (unmanaged)",
             "Publish the agent", "Report the result and how to undo it"]
    notes = []
    if existing:
        notes.append("This solution is already in that environment. Deploying again "
                     "needs replace=true and overwrites your changes to it.")
    if missing:
        notes.append("This is a demo with sample data only. It is not connected to your "
                     "organization's data, and should not be.")
    return {"ok": True, "environment": url, "solution": pkg["unique_name"],
            "version": pkg["version"], "agents": pkg["agents"], "already_installed": existing,
            "connections": needs, "steps": steps, "notes": notes,
            "summary": ("Ready to deploy. " if not existing else "Already installed. ")
                       + " ".join(notes)}


def deploy(slug: str, env: str, confirm: bool = False, replace: bool = False,
           source: str = DEFAULT_RAW_BASE) -> dict:
    p = plan(slug, env, source)
    if not confirm:
        return {**p, "ok": False, "needs_confirmation": True,
                "summary": "Nothing changed. Review the plan, then confirm to deploy."}
    if p["already_installed"] and not replace:
        raise DeployError("Already installed there. Use replace to overwrite it, or pick another environment.")
    pkg = load_package(slug, source)
    settings = pkg["settings"]
    by_conn = {n["connector"]: n["available_connection"] for n in p["connections"]}
    for ref in settings.get("ConnectionReferences", []):
        ref["ConnectionId"] = by_conn.get(ref["ConnectorId"].rsplit("/", 1)[-1]) or ""
    with tempfile.TemporaryDirectory() as tmp:
        zpath, spath = os.path.join(tmp, "solution.zip"), os.path.join(tmp, "settings.json")
        open(zpath, "wb").write(pkg["zip"])
        json.dump(settings, open(spath, "w"))
        args = ["solution", "import", "--path", zpath, "--settings-file", spath,
                "--environment", p["environment"], "--publish-changes", "--async"]
        if replace:
            args.append("--force-overwrite")
        _run(args)
    published = []
    for schema in pkg["agents"]:
        try:
            _run(["copilot", "publish", "--bot", schema, "--environment", p["environment"]])
            published.append(schema)
        except DeployError as exc:
            p["notes"].append(f"Imported, but publishing {schema} needs attention: {exc}")
    return {"ok": True, "environment": p["environment"], "solution": pkg["unique_name"],
            "published": published, "notes": p["notes"],
            "open_in": "https://copilotstudio.microsoft.com/",
            "undo": f"undo {slug} in {env}",
            "summary": (f"Deployed {pkg['unique_name']} {pkg['version']} and published "
                        f"{len(published)} of {len(pkg['agents'])} agent(s). Open Copilot Studio, "
                        "pick this environment, and try the test question. " + " ".join(p["notes"])).strip()}


def undo(slug: str, env: str, confirm: bool = False, source: str = DEFAULT_RAW_BASE) -> dict:
    url = _resolve_env(env)
    pkg = load_package(slug, source)
    if not confirm:
        return {"ok": False, "needs_confirmation": True,
                "summary": f"This removes {pkg['unique_name']} from {env}. Confirm to continue."}
    _run(["solution", "delete", "--solution-name", pkg["unique_name"], "--environment", url])
    return {"ok": True, "summary": f"Removed {pkg['unique_name']} from {env}."}


def test_question(slug: str, source: str = DEFAULT_RAW_BASE) -> str:
    try:
        rec = json.loads(_fetch(f"solutions/{slug}/deployment.json", source))
        return rec.get("smoke_test", {}).get("prompt", "")
    except Exception:  # noqa: BLE001
        return ""


# ------------------------------------------------------------ Brainstem side
class CopilotStudioDeployAgent(BasicAgent):
    def __init__(self):
        self.name = "CopilotStudioDeploy"
        self.metadata = {
            "name": self.name,
            "description": (
                "Deploys an AIBAST library solution (for example tiered-huddle-board) into the "
                "user's own Copilot Studio environment using their own Power Platform sign-in. "
                "Use operation 'envs' to list environments, 'plan' to check before changing "
                "anything, 'deploy' with confirm=true only after the user agrees to the plan, "
                "and 'undo' to remove it."),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["check", "envs", "plan", "deploy", "undo"]},
                    "solution": {"type": "string", "description": "Library solution slug, e.g. tiered-huddle-board"},
                    "environment": {"type": "string", "description": "Environment name or URL"},
                    "confirm": {"type": "boolean", "description": "True only after the user approved the plan"},
                    "replace": {"type": "boolean", "description": "Overwrite an existing install"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kw) -> str:
        return json.dumps(run(kw))


def run(kw: dict) -> dict:
    op, slug, env = kw.get("operation"), kw.get("solution", ""), kw.get("environment", "")
    source = kw.get("source") or os.environ.get("AIBAST_DEPLOY_SOURCE") or DEFAULT_RAW_BASE
    try:
        if op == "check":
            return check()
        if op == "envs":
            return envs()
        if not slug or not env:
            raise DeployError("Say which solution and which environment.")
        if op == "plan":
            out = plan(slug, env, source)
            out["test_question"] = test_question(slug, source)
            return out
        if op == "deploy":
            out = deploy(slug, env, bool(kw.get("confirm")), bool(kw.get("replace")), source)
            out["test_question"] = test_question(slug, source)
            return out
        if op == "undo":
            return undo(slug, env, bool(kw.get("confirm")), source)
        raise DeployError("Unknown operation.")
    except (DeployError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "summary": str(exc)}


# ---------------------------------------------------------------- CLI side
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deploy an AIBAST solution to Copilot Studio.")
    ap.add_argument("operation", choices=["check", "envs", "plan", "deploy", "undo"])
    ap.add_argument("solution", nargs="?", default="")
    ap.add_argument("--env", default="")
    ap.add_argument("--yes", action="store_true", help="confirm the change")
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--source", default="")
    a = ap.parse_args(argv)
    out = run({"operation": a.operation, "solution": a.solution, "environment": a.env,
               "confirm": a.yes, "replace": a.replace, "source": a.source})
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") or out.get("needs_confirmation") else 1


if __name__ == "__main__":
    sys.exit(main())
