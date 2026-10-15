#!/usr/bin/env python3
"""Generate the static scenario index that the M365 Copilot demo page plays.

Every sample prompt in solutions/catalog.json links to
solutions/_shared/m365-copilot-demo.html?scenario=<id>. This build step resolves each id to the
recorded transcript that answers that prompt (solutions/<folder>/evals/transcripts.json) and
writes solutions/_shared/demo-scenarios.json. The page reads only that file and the transcript,
both same-origin, so a visit makes no GitHub API call.

A prompt with no recorded answer is listed with "recorded": false; the page says so in plain words
and never plays a different agent's demo.

Usage: python tools/build_demo_scenarios.py [--check]
"""

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "solutions" / "catalog.json"
REGISTRY = ROOT / "registry.json"
OUTPUT = ROOT / "solutions" / "_shared" / "demo-scenarios.json"
SCHEMA = "aibast-demo-scenarios/1.0"
SCENARIO = re.compile(r"[?&]scenario=([a-z0-9-]+)")
ROLE_PREFIX = re.compile(r"^as (?:an? |the )?[a-z][a-z &/-]{0,40}, ")

# Scenario ids that shipped before the catalog named every prompt. Kept so old links still play.
LEGACY = {
    "permit-backlog": ("building-permit-processing", "BPP-01", "Permit backlog and complaint risk"),
    "permit-intake": ("building-permit-processing", "BPP-02", "Front-counter intake triage"),
    "permit-routing": ("building-permit-processing", "BPP-03", "Review routing and due date"),
    "permit-updates": ("building-permit-processing", "BPP-04", "Proactive applicant updates"),
    "permit-inspections": ("building-permit-processing", "BPP-05", "Inspector assignment board"),
    "permit-coordination": ("building-permit-processing", "BPP-03", "Review routing and due date"),
}


def question(text):
    """The question itself: case-, space- and quote-insensitive, without a leading 'As <role>, '."""
    text = re.sub(r"\s+", " ", text.replace("’", "'")).strip().lower()
    return ROLE_PREFIX.sub("", text)


def folder_for(agent_id, registry):
    demo = registry.get(agent_id, {}).get("_demo") or {}
    return demo.get("slug") or agent_id.split("/")[-1]


def load_transcripts(folder):
    path = ROOT / "solutions" / folder / "evals" / "transcripts.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("transcripts", [])


def build():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["solutions"]
    registry = {agent["name"]: agent for agent in json.loads(REGISTRY.read_text(encoding="utf-8"))["agents"]}
    scenarios = {}
    agents = {}
    for agent_id, entry in sorted(catalog.items()):
        folder = folder_for(agent_id, registry)
        transcripts = load_transcripts(folder)
        by_question = {question(item["prompt"]): item["case_id"] for item in transcripts}
        ids = []
        for prompt in entry.get("sample_prompts", []):
            match = SCENARIO.search(prompt.get("demo_url", ""))
            if not match:
                continue
            scenario_id = match.group(1)
            case_id = by_question.get(question(prompt["prompt"]))
            if scenario_id in scenarios and scenarios[scenario_id]["agent_id"] != agent_id:
                raise SystemExit(f"scenario {scenario_id} is claimed by two agents")
            scenarios[scenario_id] = {
                "agent_id": agent_id,
                "title": prompt["label"],
                "prompt": prompt["prompt"],
                "folder": folder,
                "case_id": case_id,
                "recorded": case_id is not None,
            }
            if scenario_id not in ids:
                ids.append(scenario_id)
        agents[agent_id] = {"name": entry["display_name"], "scenarios": ids}
    for scenario_id, (folder, case_id, title) in LEGACY.items():
        if scenario_id in scenarios:
            continue
        agent_id = f"@aibast-agents-library/{folder}"
        recorded = case_id in {item["case_id"] for item in load_transcripts(folder)}
        scenarios[scenario_id] = {
            "agent_id": agent_id,
            "title": title,
            "prompt": "",
            "folder": folder,
            "case_id": case_id if recorded else None,
            "recorded": recorded,
        }
        agents.setdefault(agent_id, {"name": catalog.get(agent_id, {}).get("display_name", ""), "scenarios": []})
    recorded = sum(1 for item in scenarios.values() if item["recorded"])
    return {
        "schema": SCHEMA,
        "source": ["solutions/catalog.json", "registry.json", "solutions/*/evals/transcripts.json"],
        "summary": {"scenarios": len(scenarios), "recorded": recorded, "not_recorded": len(scenarios) - recorded},
        "agents": agents,
        "scenarios": dict(sorted(scenarios.items())),
    }


def render(index):
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the committed index is stale")
    args = parser.parse_args()
    text = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            print(f"{OUTPUT.relative_to(ROOT)} is stale; run python tools/build_demo_scenarios.py", file=sys.stderr)
            return 1
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    summary = json.loads(text)["summary"]
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {summary['recorded']} of {summary['scenarios']} scenarios recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
