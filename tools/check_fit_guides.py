#!/usr/bin/env python3
"""Check every solution's fit guide against the deploy standard. No network, no sign-in.

    python3 tools/check_fit_guides.py          # exit 1 if any fit guide breaks the standard

A fit guide is the `fit` key in solutions/<slug>/deployment.json. The form and the
rules live in one place, the deploy agent; this tool only runs them over the library.
"""
from __future__ import annotations

import glob
import importlib.util
import io
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = os.path.join(ROOT, "agents", "@aibast-agents-library", "templates", "copilot_studio_deploy_agent.py")
# pictographs only; the arrows and box glyphs the site uses are not in these ranges
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿✀-➿]")


def load_agent():
    spec = importlib.util.spec_from_file_location("copilot_studio_deploy_agent", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_one(agent, recipe: dict, slug: str) -> list[str]:
    """Returns the problems found in one solution's fit guide; an empty list means it meets the standard."""
    problems = []
    try:
        fit = agent.check_fit(recipe["fit"], recipe.get("operations"))
    except agent.DeployError as exc:
        return [str(exc)]
    title = recipe.get("display_name") or slug
    for m in fit["systems"]:
        try:
            pkg = agent.build_shaped(slug, title, m)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{m['system']}: the package could not be built: {exc}")
            continue
        names = zipfile.ZipFile(io.BytesIO(pkg["zip"])).namelist()
        z = zipfile.ZipFile(io.BytesIO(pkg["zip"]))
        for need in ("solution.xml", "customizations.xml", "[Content_Types].xml", "Assets/botcomponent_connectionreferenceset.xml"):
            if need not in names:
                problems.append(f"{m['system']}: the package is missing {need}")
        skill = next((z.read(n).decode() for n in names if ".skill." in n and n.endswith("/data")), "")
        tool = next((z.read(n).decode() for n in names if ".tool." in n and n.endswith("/data")), "")
        if "kind: ConnectorTool" not in tool or "authMode: Invoker" not in tool:
            problems.append(f"{m['system']}: the tool must be a connector tool that runs as the signed-in person")
        for op, d in m["operations"].items():
            for q in d["queries"]:
                text = q if isinstance(q, str) else q["query"]
                if text not in skill:
                    problems.append(f"{m['system']}: operation {op} has a query the skill does not carry")
        if agent.DISCLAIMER not in skill or pkg["note"] not in skill:
            problems.append(f"{m['system']}: the skill must carry the disclaimer and the opening note")
        words = json.dumps(m, ensure_ascii=False) + skill
        if EMOJI.search(words):
            problems.append(f"{m['system']}: no emoji in a fit guide or its skill")
        if m.get("expect_says"):
            fields = set(re.findall(r"\{([a-z_]+)\}", m["expect_says"]))
            aliases = set(re.findall(r'alias="([a-z_]+)"', m.get("preview", "")))
            if not fields <= aliases:
                problems.append(f"{m['system']}: expect_says uses {sorted(fields - aliases)}, which the preview query does not return")
    return problems


def main(argv=None) -> int:
    agent = load_agent()
    recipes = sorted(glob.glob(os.path.join(ROOT, "solutions", "*", "deployment.json")))
    checked = bad = 0
    for path in recipes:
        recipe = json.load(open(path, encoding="utf-8"))
        if "fit" not in recipe:
            continue
        checked += 1
        slug = os.path.basename(os.path.dirname(path))
        problems = check_one(agent, recipe, slug)
        if problems:
            bad += 1
            for p in problems:
                print(f"error: {slug}: {p}")
    print(f"fit guides: {checked - bad} of {checked} meet {agent.FIT_SCHEMA} ({len(recipes) - checked} solutions have none and deploy the sample)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
