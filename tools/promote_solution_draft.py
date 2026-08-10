#!/usr/bin/env python3
"""Create and push a synthetic Copilot Studio Draft from a reviewed package."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STUDIO_DISPLAY_NAME_OVERRIDES = {
    "@aibast-agents-library/asset-maintenance-forecast": "Asset Maintenance Pilot",
    "@aibast-agents-library/cart-abandonment-recovery": "Cart Recovery Pilot",
    "@aibast-agents-library/clinical-notes-summarizer": "Clinical Notes Pilot",
    "@aibast-agents-library/cross-selling": "Cross-Selling Pilot",
    "@aibast-agents-library/customer-loyalty-rewards": "Customer Loyalty Pilot",
    "@aibast-agents-library/customer-sentiment-churn": "Customer Sentiment Pilot",
    "@aibast-agents-library/fraud-detection-alert": "Fraud Detection Pilot",
    "@aibast-agents-library/license-renewal-expansion": "License Renewal Pilot",
    "@aibast-agents-library/loan-origination-assistant": "Loan Origination Pilot",
    "@aibast-agents-library/order-status-communication": "Order Status Pilot",
    "@aibast-agents-library/patient-intake": "Patient Intake Pilot",
    "@aibast-agents-library/product-feedback-synthesizer": "Product Feedback Pilot",
    "@aibast-agents-library/returns-complaints-resolution": "Returns Resolution Pilot",
    "@aibast-agents-library/store-associate-copilot": "Retail Store Associate Pilot",
    "@aibast-agents-library/supply-chain-disruption-alert": "Supply Chain Alert Pilot",
    "@aibast-agents-library/utility-billing-assistance": "Utility Billing Pilot",
    "@aibast-agents-library/wealth-insights-generator": "Wealth Insights Pilot",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def display_name(recipe):
    if recipe.get("name") in STUDIO_DISPLAY_NAME_OVERRIDES:
        return STUDIO_DISPLAY_NAME_OVERRIDES[recipe["name"]]
    name = recipe["display_name"]
    if name.endswith(" Agent"):
        name = name[:-6]
    candidate = f"{name} Pilot"
    if len(candidate) <= 30:
        return candidate
    if len(name) <= 30:
        return name
    return name[:30].rsplit(" ", 1)[0].rstrip()


def parse_yaml_scalar(text, key):
    match = re.search(rf'^{re.escape(key)}:\s*(.+)$', text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith('"'):
        return json.loads(value)
    return value


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def indent_block(value, spaces):
    prefix = " " * spaces
    return "\n".join(prefix + line if line else prefix for line in value.splitlines())


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    if not fields.get("name") or not fields.get("description"):
        raise ValueError(f"{path}: frontmatter needs name and description")
    return text, fields


def render_settings(name, schema, instructions):
    return (
        f"displayName: {quote(name)}\n"
        f"schemaName: {quote(schema)}\n"
        "accessControlPolicy: GroupMembership\n"
        "authenticationMode: Integrated\n"
        "authenticationTrigger: Always\n"
        "configuration:\n"
        "  authoringModel: CliCopilot\n"
        "  recognizer:\n"
        "    kind: CLICopilotRecognizer\n"
        "  agentSettings:\n"
        "    model:\n"
        "      series: Sonnet46\n"
        "    instructions:\n"
        "      segments:\n"
        "        - kind: StaticSegment\n"
        "          value: |\n"
        f"{indent_block(instructions.rstrip(), 12)}\n"
        "template: cliagent-1.0.0\n"
        "language: 1033\n"
    )


def render_skill(path):
    text, fields = parse_frontmatter(path)
    return (
        "mcs.metadata:\n"
        f"  componentName: {quote(fields['name'])}\n"
        f"  description: {quote(fields['description'])}\n"
        "kind: InlineAgentSkill\n"
        "content: |\n"
        f"{indent_block(text.rstrip(), 2)}\n"
    ), fields


def render_knowledge_sidecar(filename):
    return (
        "mcs.metadata:\n"
        f"  componentName: {filename}\n"
        f"  description: This knowledge source searches information contained in {filename}\n"
    )


def reviewed_knowledge_files(package):
    manual = sorted(
        path
        for path in (package / "manual" / "knowledge").glob("*.md")
        if path.is_file()
    )
    if manual:
        return manual
    return sorted(
        path
        for path in (
            package
            / "copilot-studio"
            / "capabilities"
            / "knowledge"
            / "files"
        ).glob("*.md")
        if path.is_file()
    )


def run(command):
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(command)} failed ({result.returncode})\n"
            f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
        )
    return result.stdout + result.stderr


def copy_project(project, package):
    destination = package / "copilot-studio"
    destination.mkdir(parents=True, exist_ok=True)
    for relative in ("settings.mcs.yml", "agent.sync.yaml"):
        shutil.copy2(project / relative, destination / relative)
    for folder in ("behaviors", "capabilities"):
        source = project / folder
        target = destination / folder
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)


def promote(
    slug,
    project,
    environment,
    prefix,
    push,
    update_existing=False,
    rename_existing=False,
    display_name_override=None,
):
    package = ROOT / "solutions" / slug
    recipe = read_json(package / "deployment.json")
    name = display_name_override or display_name(recipe)
    if project.exists() and not update_existing:
        raise FileExistsError(project)
    instructions = (package / "manual" / "GLOBAL-INSTRUCTIONS.md").read_text(
        encoding="utf-8"
    )
    initialized = not project.exists()
    if initialized:
        init_output = run([
            "pac",
            "copilot",
            "init",
            "--name",
            name,
            "--publisher-prefix",
            prefix,
            "--authoring-mode",
            "cli-copilot",
            "--project-dir",
            str(project),
            "--environment",
            environment,
        ])
    else:
        init_output = "Reused existing Copilot Studio project."
    settings = project / "settings.mcs.yml"
    identity = settings.read_text(encoding="utf-8")
    schema = parse_yaml_scalar(identity, "schemaName")
    if not schema:
        raise ValueError("initialized settings omit schemaName")
    if not initialized and not rename_existing:
        name = parse_yaml_scalar(identity, "displayName") or name
    settings.write_text(
        render_settings(name, schema, instructions),
        encoding="utf-8",
    )

    behaviors = project / "behaviors"
    if behaviors.exists():
        shutil.rmtree(behaviors)
    behaviors.mkdir()
    skills = sorted((package / "manual" / "skills").glob("*/SKILL.md"))
    for path in skills:
        content, fields = render_skill(path)
        filename = f"{prefix}_{re.sub(r'[^a-z0-9-]+', '-', fields['name'].lower())}.mcs.yml"
        if len(filename) >= 100:
            raise ValueError(f"behavior filename is too long: {filename}")
        (behaviors / filename).write_text(content, encoding="utf-8")

    knowledge = [
        (path.name, path.read_bytes())
        for path in reviewed_knowledge_files(package)
    ]
    knowledge_target = project / "capabilities" / "knowledge" / "files"
    if knowledge_target.exists():
        shutil.rmtree(knowledge_target)
    knowledge_target.mkdir(parents=True)
    for filename, content in knowledge:
        (knowledge_target / filename).write_bytes(content)
        (knowledge_target / f"{filename}.mcs.yml").write_text(
            render_knowledge_sidecar(filename),
            encoding="utf-8",
        )

    push_output = ""
    if push:
        push_output = run([
            "pac",
            "copilot",
            "push",
            "--project-dir",
            str(project),
        ])
    copy_project(project, package)
    return {
        "slug": slug,
        "display_name": name,
        "schema_name": schema,
        "project_dir": str(project),
        "skills": len(skills),
        "knowledge_files": len(knowledge),
        "initialized": initialized,
        "updated": not initialized,
        "pushed": push,
        "init_output": init_output.strip().splitlines()[-1],
        "push_output": push_output.strip().splitlines()[-1] if push_output else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--publisher-prefix", default="aibast")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--update-existing", action="store_true")
    parser.add_argument("--rename-existing", action="store_true")
    parser.add_argument("--display-name")
    args = parser.parse_args()
    result = promote(
        args.slug,
        args.project_dir.expanduser().resolve(),
        args.environment,
        args.publisher_prefix,
        args.push,
        args.update_existing,
        args.rename_existing,
        args.display_name,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
