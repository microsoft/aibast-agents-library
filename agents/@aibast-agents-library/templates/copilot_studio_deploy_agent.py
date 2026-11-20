"""Deploy an AIBAST library solution to the user's own Copilot Studio environment.

One file, two front ends:
- Brainstem loads it as an agent (CopilotStudioDeploy).
- GitHub Copilot runs it from the terminal through the skill:
  python3 copilot_studio_deploy_agent.py <check|envs|look|probe|plan|deploy|undo> ...

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


def undo(slug: str, env: str, confirm: bool = False, source: str = DEFAULT_RAW_BASE, shape: str = "sample") -> dict:
    url = _resolve_env(env)
    pkg = {"unique_name": _shaped_names(slug, "")[0]} if shape == "yours" else load_package(slug, source)
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


# ------------------------------------------- shaped to the person's own system
# Sample data is the default. "yours" builds the same agent on the system the person already runs, read with their own
# sign-in through a standard connector: no Azure, no app registration, nothing leaves their device and their tenant.
DISCLAIMER = ("This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications "
              "Specialist Team (AIBAST), not an officially supported Microsoft product.")
SYSTEMS = {"shared_commondataserviceforapps": "Dynamics 365", "shared_salesforce": "Salesforce",
           "shared_service-now": "ServiceNow", "shared_sharepointonline": "SharePoint", "shared_sql": "SQL Server"}
# The deploy standard: every target answers these verbs, and every fit guide has this form (docs/deploy-standard.md).
VERBS = ("check", "look", "probe", "plan", "deploy", "undo")
HELPERS = ("envs",)
FIT_SCHEMA = "aibast-fit-guide/1.0"
MAPPING_FORM = {
    "system": "the system's everyday name, for example Dynamics 365 Sales",
    "connector": "shared_commondataserviceforapps", "operation_id": "ListRecordsWithOrganization",
    "fixed_inputs": {"organization": "current"}, "query_input": "fetchXml",
    "rule": "One sentence, in business words, for how the agent decides. The agent says it in every answer.",
    "preview": "<fetch aggregate=\"true\">one small count query that proves the data is there</fetch>",
    "expect_says": "You should see {deals} open deals.",
    "test_question": "A first question the person can ask.",
    "operations": {"operation_name": {"when": "what it answers", "queries": [
        {"set": {"entityName": "opportunities"}, "query": "<fetch aggregate=\"true\">counts and sums come from the query, never from the model</fetch>"}]}}}
_ADDRESS = ["City", "County", "Country", "Fax", "FreightTermsCode", "ImportSequenceNumber", "Latitude", "Line1", "Line2",
            "Line3", "Longitude", "Name", "PostalCode", "PostOfficeBox", "PrimaryContactName", "*ShippingMethodCode",
            "StateOrProvince", "Telephone1", "Telephone2", "Telephone3", "TimeZoneRuleVersionNumber", "UPSZone", "UTCOffset",
            "UTCConversionTimeZoneCode"]


def load_fit(slug: str, source: str = DEFAULT_RAW_BASE) -> dict:
    """The solution's fit guide: what it needs in business words, and ready mappings for the systems it knows."""
    try:
        return json.loads(_fetch(f"solutions/{slug}/deployment.json", source)).get("fit") or {}
    except Exception:  # noqa: BLE001
        return {}


def _connected(url: str) -> dict:
    out = {}
    for line in _run(["connection", "list", "--environment", url], timeout=300).splitlines():
        m = re.search(r"^(\S+)\s.*?/apis/(\S+)\s+Connected", line)
        if m:
            out.setdefault(m.group(2), m.group(1))
    return out


def _rows(url: str, fetch_xml: str) -> list[dict]:
    """Runs one read-only FetchXML query with the person's own sign-in and returns the rows shown."""
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "q.xml")
        open(f, "w").write(fetch_xml)
        lines = _run(["env", "fetch", "--xmlFile", f, "--environment", url], timeout=300).splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("Connected to")), -1) + 1
    body = [l for l in lines[start:] if l.strip()]
    if len(body) < 2:
        return []
    cols = [(m.start(), m.group()) for m in re.finditer(r"\S+", body[0])]
    ends = [c[0] for c in cols[1:]] + [None]
    return [{name: row[a:b].strip() for (a, name), b in zip(cols, ends)} for row in body[1:]]


def check_mapping(m: dict) -> dict:
    """A mapping says how one system answers this solution's questions. It may come from the library or from the AI."""
    need = ["system", "connector", "operation_id", "query_input", "rule", "operations"]
    missing = [k for k in need if not m.get(k)]
    if missing:
        raise DeployError("The mapping is missing: " + ", ".join(missing) + ".")
    if not re.fullmatch(r"shared_[a-z0-9_-]+", m["connector"]) or not re.fullmatch(r"[A-Za-z0-9_]+", m["operation_id"]):
        raise DeployError("The mapping's connector or operation name is not valid.")
    for k in list(m.get("fixed_inputs") or {}) + [m["query_input"]]:
        if not re.fullmatch(r"[$A-Za-z0-9_]+", k):
            raise DeployError(f"The mapping's input name '{k}' is not valid.")
    if not re.match(r"(?i)(list|get|search|execute|query|read)", m["operation_id"]):
        raise DeployError("Only read operations are allowed here. This one does not look like a read.")
    for name, op in m["operations"].items():
        if not re.fullmatch(r"[a-z0-9_]+", name) or not op.get("queries"):
            raise DeployError(f"Operation '{name}' needs a plain name and at least one query.")
        for q in op["queries"]:
            if not isinstance(q, str) and not (isinstance(q, dict) and isinstance(q.get("query"), str) and all(
                    re.fullmatch(r"[$A-Za-z0-9_]+", k) and re.fullmatch(r"[A-Za-z0-9_ .-]+", str(v)) for k, v in (q.get("set") or {}).items())):
                raise DeployError(f"Operation '{name}' has a query that is not text, or sets an input that is not a plain value.")
    return m


def check_fit(fit: dict, operations=None) -> dict:
    """A fit guide: what the solution needs in business words, and a mapping for each system it knows."""
    if fit.get("schema") != FIT_SCHEMA:
        raise DeployError(f"The fit guide must say schema: {FIT_SCHEMA}.")
    if not fit.get("needs") or not all(isinstance(n, str) and n.strip() for n in fit["needs"]):
        raise DeployError("The fit guide needs a 'needs' list in plain business words.")
    if not fit.get("systems"):
        raise DeployError("The fit guide needs at least one system mapping.")
    for m in fit["systems"]:
        check_mapping(m)
        if not m.get("preview") or not m.get("test_question"):
            raise DeployError(f"The mapping for {m['system']} needs a preview query and a test question.")
        extra = sorted(set(m["operations"]) - set(operations)) if operations else []
        if extra:
            raise DeployError(f"The mapping for {m['system']} names operations the solution does not have: {', '.join(extra)}.")
    return fit


def _shaped_names(slug: str, title: str) -> tuple[str, str]:
    return "aibast_" + re.sub(r"[^A-Za-z0-9]+", "", slug.title()) + "YourData", f"{title} (your data)"


def build_shaped(slug: str, title: str, mapping: dict) -> dict:
    """The solution package for the shaped agent: one read-only connector tool, one skill, one connection reference."""
    from xml.sax.saxutils import escape
    m = check_mapping(mapping)
    bot, name = _shaped_names(slug, title)
    api = "/providers/Microsoft.PowerApps/apis/" + m["connector"]
    cr, tool_name, skill_name = f"{bot}.cr.{m['connector']}", f"Read {m['system']} (your data)", f"{slug}-your-data"
    note = f"Your own {m['system']} data, read with your sign-in. Experimental AIBAST project, not an officially supported Microsoft product."
    def _say(q):
        if isinstance(q, str):
            return f"`{q}`"
        return "".join(f"set `{k}` to `{v}`, " for k, v in (q.get("set") or {}).items()) + f"`{q['query']}`"
    steps = "".join(f"   - `{op}` ({d.get('when', op.replace('_', ' '))}): " + "; then ".join(_say(q) for q in d["queries"]) + "\n"
                    for op, d in m["operations"].items())
    skill = (f"---\nname: {skill_name}\ndescription: \"{title}, on this organization's own {m['system']} data. Read-only.\"\n---\n# {skill_name}\n\n"
             f"**Your data.** {DISCLAIMER}\n\n## When to use this skill\nAny question this agent is for: {', '.join(m['operations'])}.\n\n"
             f"Never answer from model knowledge. Every number comes from the tool `{tool_name}`, which reads with the signed-in "
             "person's own permissions. It never writes.\n\n## Procedure\n1. Pick the one operation that fits the request.\n"
             f"2. Call `{tool_name}` and put that operation's query in `{m['query_input']}`, exactly as written below. Where a query has a word in curly braces, put the person's own words there (for example the account they named) and change nothing else. Leave other optional inputs empty.\n"
             f"{steps}3. Report the counts, sums and names the tool returned as they are. Do not add, round, estimate or work out day counts yourself. Never state a total, subtotal, share, average or difference that the tool did not return as a number, and never add a Total row to a table yourself: if a query did not return it, it is not available. Show amounts exactly as returned.\n"
             f"4. The rule in use: {m['rule']} Say it in the answer.\n5. No emoji. Do not say a date is past, overdue or upcoming: you do not know today's date.\n"
             f"6. Begin EVERY answer, every turn, with this line exactly: \"{note}\"\n")
    fixed = "".join(f"  - name: {k}\n    value:\n      kind: ValueReference\n      type: \"{{\\\"type\\\":\\\"string\\\"}}\"\n"
                    f"      defaultValue: {json.dumps(json.dumps(str(v)))}\n\n" for k, v in (m.get("fixed_inputs") or {}).items())
    tool = (f"kind: ConnectorTool\nauthMode: Invoker\nconnectionReference: {cr}\nconnectorId: {api}\noperationId: {m['operation_id']}\n"
            + ("toolInputs:\n" + fixed.rstrip("\n") + "\n" if fixed else ""))
    skill_data = "kind: InlineAgentSkill\ncontent: |\n" + "\n".join(("  " + l) if l else "" for l in skill.split("\n"))
    sk, tk = f"{bot}.skill.aibast_{skill_name}", f"{bot}.tool.Read{re.sub(r'[^A-Za-z0-9]+', '', m['system'])}"

    def part(schema, nm, desc):
        return (f'<botcomponent schemaname="{schema}">\n  <componenttype>9</componenttype>\n  <description>{escape(desc)}</description>\n'
                f'  <iscustomizable>0</iscustomizable>\n  <name>{escape(nm)}</name>\n  <parentbotid>\n    <schemaname>{bot}</schemaname>\n'
                '  </parentbotid>\n  <statecode>0</statecode>\n  <statuscode>1</statuscode>\n</botcomponent>')
    nil = ' xsi:nil="true"'
    addr = "".join(f"        <Address>\n          <AddressNumber>{n}</AddressNumber>\n          <AddressTypeCode>1</AddressTypeCode>\n"
                   + "".join(f"          <{f[1:]}>1</{f[1:]}>\n" if f[0] == "*" else f"          <{f}{nil}></{f}>\n" for f in _ADDRESS)
                   + "        </Address>\n" for n in (1, 2))
    solution = ('<ImportExportXml version="9.2.26031.139" SolutionPackageVersion="9.2" languagecode="1033" generatedBy="CrmLive" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <SolutionManifest>\n'
                f'    <UniqueName>{bot}</UniqueName>\n    <LocalizedNames>\n      <LocalizedName description="{bot}" languagecode="1033" />\n'
                '    </LocalizedNames>\n    <Descriptions />\n    <Version>1.0</Version>\n    <Managed>0</Managed>\n    <Publisher>\n'
                '      <UniqueName>aibast</UniqueName>\n      <LocalizedNames>\n        <LocalizedName description="aibast" languagecode="1033" />\n'
                '      </LocalizedNames>\n      <Descriptions>\n        <Description description="aibast" languagecode="1033" />\n      </Descriptions>\n'
                f'      <EMailAddress{nil}></EMailAddress>\n      <SupportingWebsiteUrl{nil}></SupportingWebsiteUrl>\n'
                '      <CustomizationPrefix>aibast</CustomizationPrefix>\n      <CustomizationOptionValuePrefix>85464</CustomizationOptionValuePrefix>\n'
                f'      <Addresses>\n{addr}      </Addresses>\n    </Publisher>\n    <RootComponents />\n    <MissingDependencies />\n'
                '  </SolutionManifest>\n</ImportExportXml>').replace("\n", "\r\n")
    customizations = ('<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <Entities></Entities>\n  <Roles></Roles>\n'
                      '  <Workflows></Workflows>\n  <FieldSecurityProfiles></FieldSecurityProfiles>\n  <Templates />\n  <EntityMaps />\n'
                      '  <EntityRelationships />\n  <OrganizationSettings />\n  <optionsets />\n  <CustomControls />\n  <EntityDataProviders />\n'
                      '  <Languages>\n    <Language>1033</Language>\n  </Languages>\n'
                      f'  <connectionreferences>\n    <connectionreference connectionreferencelogicalname="{cr}">\n'
                      f'      <connectionreferencedisplayname>{escape(name)} - {escape(m["system"])}</connectionreferencedisplayname>\n'
                      f'      <connectorid>{api}</connectorid>\n      <iscustomizable>1</iscustomizable>\n      <statecode>0</statecode>\n'
                      '      <statuscode>1</statuscode>\n    </connectionreference>\n  </connectionreferences>\n</ImportExportXml>')
    config = {"$kind": "BotConfiguration", "recognizer": {"$kind": "CLICopilotRecognizer"}, "agentSettings": {
        "$kind": "AgentSettings", "model": {"$kind": "ModelConfig", "series": "Sonnet46"}, "instructions": {"$kind": "Instructions", "segments": [
            {"$kind": "StaticSegment", "value":
             f"# {name}\n\nAnswer every question by following the skill `{skill_name}`, which calls the tool `{tool_name}`. Report the tool's "
             f"numbers as they are; never do arithmetic yourself. No emoji. Begin EVERY answer, every turn, with this line exactly: \"{note}\"\n\n"
             + DISCLAIMER}]}},
        "authoringModel": "CliCopilot", "syntax": {"Elements": [{"PropertyName": "recognizer"}, {"PropertyName": "agentSettings"}, {"PropertyName": "authoringModel"}]}}
    bot_xml = (f'<bot schemaname="{bot}">\n  <authenticationmode>2</authenticationmode>\n  <authenticationtrigger>1</authenticationtrigger>\n'
               f'  <iconbase64></iconbase64>\n  <iscustomizable>0</iscustomizable>\n  <language>1033</language>\n  <name>{escape(name)}</name>\n'
               '  <runtimeprovider>0</runtimeprovider>\n  <template>cliagent-1.0.0</template>\n  <timezoneruleversionnumber>4</timezoneruleversionnumber>\n</bot>').replace("\n", "\r\n")
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                               '<Default Extension="xml" ContentType="application/octet-stream" /><Default Extension="json" ContentType="application/octet-stream" />'
                               + "".join(f'<Override PartName="/botcomponents/{k}/data" ContentType="application/octet-stream" />' for k in (sk, tk)) + '</Types>',
        "solution.xml": solution, "customizations.xml": customizations,
        f"bots/{bot}/bot.xml": bot_xml, f"bots/{bot}/configuration.json": json.dumps(config, indent=2),
        f"botcomponents/{sk}/botcomponent.xml": part(sk, skill_name, f"{title}, on this organization's own {m['system']} data. Read-only."),
        f"botcomponents/{sk}/data": skill_data,
        f"botcomponents/{tk}/botcomponent.xml": part(tk, tool_name, f"Reads {m['system']} with the signed-in person's own permissions. Read-only."),
        f"botcomponents/{tk}/data": tool,
        # the stored link from the tool to its connection; without it the tool has no connection after import
        "Assets/botcomponent_connectionreferenceset.xml": "<botcomponent_connectionreferenceset>\n"
            f'  <botcomponent_connectionreference botcomponentid.schemaname="{tk}" connectionreferenceid.connectionreferencelogicalname="{cr}">\n'
            "    <iscustomizable>1</iscustomizable>\n  </botcomponent_connectionreference>\n</botcomponent_connectionreferenceset>"}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n, body in files.items():
            z.writestr(zipfile.ZipInfo(n, (2026, 1, 1, 0, 0, 0)), body, zipfile.ZIP_DEFLATED)
    return {"zip": buf.getvalue(), "unique_name": bot, "agent_name": name, "connection_reference": cr, "api": api, "note": note}


def _title(slug: str, source: str) -> str:
    try:
        return json.loads(_fetch(f"solutions/{slug}/deployment.json", source)).get("display_name") or slug.replace("-", " ").title()
    except Exception:  # noqa: BLE001
        return slug.replace("-", " ").title()


def look(slug: str, env: str, source: str = DEFAULT_RAW_BASE) -> dict:
    """Looks before anyone is asked: which systems the person already has connected, and what this solution can do with them."""
    url, fit = _resolve_env(env), load_fit(slug, source)
    have = _connected(url)
    ready, preview = None, []
    for m in fit.get("systems", []):
        if m.get("connector") in have:
            try:
                preview = _rows(url, m["preview"]) if m.get("preview") and m["connector"] == "shared_commondataserviceforapps" else []
            except DeployError:
                preview = []
            if preview or not m.get("preview"):
                ready = m
                break
    others = [SYSTEMS[c] for c in have if c in SYSTEMS and c not in {m.get("connector") for m in fit.get("systems", [])}]
    try:
        recipe = json.loads(_fetch(f"solutions/{slug}/deployment.json", source))
    except Exception:  # noqa: BLE001
        recipe = {}
    out = {"ok": True, "environment": url, "recommend": "yours" if ready else "sample", "found_system": ready["system"] if ready else None,
           "preview": preview[:5], "other_systems_connected": others, "needs": fit.get("needs", []), "defaults": fit.get("defaults", {}),
           "disclaimer": DISCLAIMER}
    if ready:
        out["summary"] = (f"Found {ready['system']} with data in this environment. Recommended: shape the agent to their own data "
                          "(shape=yours). Sample data stays available (shape=sample). Ask one question: go ahead?")
    elif others:
        out["write_your_own"] = {
            "connected": {SYSTEMS[c]: c for c in have if c in SYSTEMS},
            "template_agent": recipe.get("source_path", ""), "operations": recipe.get("operations", []),
            "mapping_form": MAPPING_FORM,
            "how": ("Read the template agent to learn what each operation answers. Write a mapping in mapping_form for a connected system "
                    "that really holds that data. Check it with the probe operation. Cover only the operations the data can answer "
                    "honestly; leave the rest out. If probe fails or the data is not there, use sample data. "
                    "Name each operation after one in 'operations'. 'set' fixes a tool input for that one query: for Dynamics 365 "
                    "set entityName to the table's plural name (opportunities, accounts, contacts, incidents) and write the query "
                    "as FetchXML on the singular name (opportunity). probe shows only the first row of each query.")}
        out["summary"] = (f"Found {', '.join(others)}. The library has no ready mapping for this solution. You may write one "
                          "(see write_your_own), check it with probe, and pass it as mapping. If unsure, use sample data and say so.")
    else:
        out["summary"] = "Nothing here that this solution can be shaped to. Use sample data (shape=sample) and say so."
    return out


def _mapping_for(slug: str, url: str, source: str, mapping) -> dict:
    if mapping:
        return check_mapping(json.loads(mapping) if isinstance(mapping, str) else mapping)
    have = _connected(url)
    for m in load_fit(slug, source).get("systems", []):
        if m.get("connector") in have:
            return check_mapping(m)
    raise DeployError("No mapping fits what is connected in this environment. Use sample data, or pass a mapping.")


def probe(env: str, mapping=None, slug: str = "", source: str = DEFAULT_RAW_BASE) -> dict:
    """Runs each query in a mapping, read-only, so a mapping is proven before it is installed. Dataverse only."""
    url = _resolve_env(env)
    m = _mapping_for(slug, url, source, mapping)
    if m["connector"] != "shared_commondataserviceforapps":
        return {"ok": False, "checked": False, "summary": f"Queries for {m['system']} cannot be checked from here. Use sample data unless you are sure."}
    results, bad = [], 0
    todo = [("preview", m["preview"])] if m.get("preview") else []
    todo += [(op, q if isinstance(q, str) else q["query"]) for op, d in m["operations"].items() for q in d["queries"]]
    for name, q in todo:
        q = re.sub(r'\s+top="\d+"', "", re.sub(r"\{[a-z_ ]+\}", "", q))
        try:
            rows = _rows(url, q)
            results.append({"for": name, "ok": True, "rows": len(rows), "first": rows[0] if rows else None})
        except DeployError as exc:
            bad += 1
            results.append({"for": name, "ok": False, "error": str(exc)[-300:]})
    empty = sum(1 for r in results if r["ok"] and not r["rows"])
    return {"ok": bad == 0, "checked": True, "results": results,
            "summary": (f"{len(results) - bad} of {len(results)} queries ran; {empty} returned nothing. "
                        + ("Fix the failing queries or use sample data." if bad else
                           "Queries that return nothing mean the data is not there: drop those operations, or use sample data."
                           if empty else "The mapping reads real data."))}

_WHY_FAILED = ('<fetch><entity name="asyncoperation"><attribute name="message"/><order attribute="createdon" descending="true"/>'
               '<filter><condition attribute="createdon" operator="last-x-hours" value="1"/>'
               '<condition attribute="statuscode" operator="eq" value="31"/>'
               '<condition attribute="name" operator="eq" value="ImportSolution"/></filter></entity></fetch>')


def _import(args: list, url: str, tries: int = 4, wait: int = 90) -> None:
    """An environment installs one solution at a time. When it is busy with someone else's, wait and try again."""
    import time
    for n in range(tries):
        try:
            _run(args)
            return
        except DeployError as exc:
            why = ""
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    f = os.path.join(tmp, "q.xml")
                    open(f, "w").write(_WHY_FAILED)
                    out = _run(["env", "fetch", "--xmlFile", f, "--environment", url], timeout=300)
                why = next((l[9:].strip() for l in out.splitlines() if l.startswith("Message: ")), "")
            except DeployError:
                pass
            busy = "another" in why.lower() and "import" in why.lower()
            if busy and n < tries - 1:
                time.sleep(wait)
                continue
            if busy:
                raise DeployError("The environment is busy installing something else. Nothing was changed. Try again in a few minutes.")
            raise DeployError(f"The install did not finish. Nothing was changed. {why[:300] or exc}")

def deploy_shaped(slug: str, env: str, confirm: bool = False, replace: bool = False, source: str = DEFAULT_RAW_BASE, mapping=None) -> dict:
    url = _resolve_env(env)
    m = _mapping_for(slug, url, source, mapping)
    pkg = build_shaped(slug, _title(slug, source), m)
    conn = _connected(url).get(m["connector"])
    existing = pkg["unique_name"] in _run(["solution", "list", "--environment", url], timeout=300)
    plan_ = {"environment": url, "solution": pkg["unique_name"], "agent": pkg["agent_name"], "system": m["system"], "rule": m["rule"],
             "reads_only": True, "already_installed": existing, "connection_found": bool(conn), "disclaimer": DISCLAIMER,
             "steps": [f"Import {pkg['agent_name']} (reads {m['system']} with each person's own sign-in; writes nothing)", "Publish the agent",
                       "Report the result and how to undo it"]}
    if not conn:
        raise DeployError(f"There is no {m['system']} connection in this environment yet. Create one in Power Automate > Connections, then try again.")
    if not confirm:
        return {**plan_, "ok": False, "needs_confirmation": True,
                "summary": "Nothing changed. Review the plan, then confirm to deploy."
                           + (" It is already installed: after a yes, deploy with replace." if existing else "")}
    if existing and not replace:
        raise DeployError("Already installed there. Use replace to overwrite it, or pick another environment.")
    settings = {"EnvironmentVariables": [], "ConnectionReferences": [
        {"LogicalName": pkg["connection_reference"], "ConnectionId": conn, "ConnectorId": pkg["api"]}]}
    with tempfile.TemporaryDirectory() as tmp:
        zpath, spath = os.path.join(tmp, "solution.zip"), os.path.join(tmp, "settings.json")
        open(zpath, "wb").write(pkg["zip"])
        json.dump(settings, open(spath, "w"))
        args = ["solution", "import", "--path", zpath, "--settings-file", spath, "--environment", url, "--publish-changes", "--async"]
        _import(args + (["--force-overwrite"] if replace else []), url)
    notes = []
    try:
        _run(["copilot", "publish", "--bot", pkg["unique_name"], "--environment", url])
    except DeployError as exc:
        notes.append(f"Imported, but publishing needs attention: {exc}")
    expect = []
    if m["connector"] == "shared_commondataserviceforapps" and m.get("preview"):
        try:
            expect = _rows(url, m["preview"])[:5]
        except DeployError:
            pass
    says = ""
    if expect and m.get("expect_says"):
        try:
            says = m["expect_says"].format(**expect[0])
        except (KeyError, IndexError, ValueError):
            says = ""
    return {**plan_, "ok": True, "notes": notes, "expect": expect, "expect_says": says, "open_in": "https://copilotstudio.microsoft.com/",
            "test_question": m.get("test_question", ""), "undo": f"undo {slug} in {env} with shape=yours",
            "summary": (f"Deployed {pkg['agent_name']} on their own {m['system']} data. Every answer starts with: \"{pkg['note']}\" "
                        + " ".join(notes)).strip()}


# ------------------------------------------------------------ Brainstem side
class CopilotStudioDeployAgent(BasicAgent):
    def __init__(self):
        self.name = "CopilotStudioDeploy"
        self.metadata = {
            "name": self.name,
            "description": (
                "Deploys an AIBAST library solution (for example tiered-huddle-board) into the "
                "user's own Copilot Studio environment using their own Power Platform sign-in. "
                "Use operation 'envs' to list environments, 'look' to see which of the user's own systems "
                "it can be shaped to, 'plan' to check before changing anything, 'deploy' with confirm=true "
                "only after the user agrees to the plan, and 'undo' to remove it. shape=sample is the "
                "library's sample data; shape=yours reads the user's own system, read-only."),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": list(VERBS + HELPERS)},
                    "solution": {"type": "string", "description": "Library solution slug, e.g. tiered-huddle-board"},
                    "environment": {"type": "string", "description": "Environment name or URL"},
                    "confirm": {"type": "boolean", "description": "True only after the user approved the plan"},
                    "replace": {"type": "boolean", "description": "Overwrite an existing install"},
                    "shape": {"type": "string", "enum": ["sample", "yours"],
                              "description": "sample = the library's sample data (default). yours = the user's own system, read-only."},
                    "mapping": {"type": "string", "description": "Only for shape=yours on a system the library has no mapping for: "
                                "a JSON mapping you wrote, in the same form as the solution's fit guide."},
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
        shape = kw.get("shape") or "sample"
        if op == "look":
            return look(slug, env, source)
        if op == "probe":
            return probe(env, kw.get("mapping"), slug, source)
        if shape == "yours" and op in ("plan", "deploy"):
            return deploy_shaped(slug, env, op == "deploy" and bool(kw.get("confirm")), bool(kw.get("replace")), source, kw.get("mapping"))
        if op == "plan":
            out = plan(slug, env, source)
            out["test_question"] = test_question(slug, source)
            return out
        if op == "deploy":
            out = deploy(slug, env, bool(kw.get("confirm")), bool(kw.get("replace")), source)
            out["test_question"] = test_question(slug, source)
            return out
        if op == "undo":
            return undo(slug, env, bool(kw.get("confirm")), source, shape)
        raise DeployError("Unknown operation.")
    except (DeployError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "summary": str(exc)}


# ---------------------------------------------------------------- CLI side
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deploy an AIBAST solution to Copilot Studio.")
    ap.add_argument("operation", choices=list(VERBS + HELPERS))
    ap.add_argument("solution", nargs="?", default="")
    ap.add_argument("--env", default="")
    ap.add_argument("--yes", action="store_true", help="confirm the change")
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--source", default="")
    ap.add_argument("--shape", choices=["sample", "yours"], default="sample")
    ap.add_argument("--mapping", default="", help="JSON mapping, or a path to one")
    a = ap.parse_args(argv)
    out = run({"operation": a.operation, "solution": a.solution, "environment": a.env,
               "confirm": a.yes, "replace": a.replace, "source": a.source, "shape": a.shape,
               "mapping": open(a.mapping).read() if a.mapping and os.path.exists(a.mapping) else a.mapping})
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") or out.get("needs_confirmation") else 1


if __name__ == "__main__":
    sys.exit(main())
