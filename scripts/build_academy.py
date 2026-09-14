#!/usr/bin/env python3
"""Generate and validate the public Microsoft AI Academy catalog.

The course scope comes only from solutions/catalog.json. Registry package
metadata resolves each canonical agent to its shipped workshop directory.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any


CONFIG_SCHEMA = "aibast-academy-config/1.0"
OUTPUT_SCHEMA = "aibast-academy/1.0"
REGISTRY_SCHEMA = "rapp-registry/1.0"
SOLUTIONS_SCHEMA = "aibast-solution-copy/1.0"
ROLLOUT_SCHEMA = "aibast-workshop-course-rollout-audit/1.0"
EXPECTED_COURSES = 51

EXPECTED_MILESTONES = (
    ("started", "started", 5),
    ("local-proof", "local-proof", 15),
    ("draft-builder", "draft-builder", 20),
    ("preview-proven", "preview-proven", 25),
    ("workshop-complete", "workshop-completed", 35),
    ("hard-mode-complete", "hard-mode-completed", 50),
)
EXPECTED_ECOSYSTEM_TITLES = (
    "Discover a skill",
    "Learn the scenario",
    "Build and test",
    "Prove the outcome",
    "Carry it into Microsoft",
)
EXPECTED_PATH_IDS = {
    "start-here",
    "sales-customer-growth",
    "operations-supply-chain",
    "regulated-public-services",
    "workforce-professional-productivity",
    "cross-industry-ai",
}
EXPECTED_START_HERE = {
    "ai-customer-assistant",
    "ask-hr",
    "building-permit-processing",
    "account-intelligence",
}
INDUSTRY_NAMES = {
    "b2b_sales": "B2B Sales",
    "b2c_sales": "B2C Sales",
    "energy": "Energy",
    "financial_services": "Financial Services",
    "general": "Cross-Industry",
    "healthcare": "Healthcare",
    "human_resources": "Human Resources",
    "manufacturing": "Manufacturing",
    "professional_services": "Professional Services",
    "retail_cpg": "Retail & CPG",
    "slg_government": "State and Local Government",
    "software_digital_products": "Software & Digital Products",
}


class AcademyBuildError(ValueError):
    """A source or configuration violated the academy contract."""


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AcademyBuildError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AcademyBuildError(f"required JSON file does not exist: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AcademyBuildError(f"cannot read {path}: {exc}") from exc
    try:
        value = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except (json.JSONDecodeError, AcademyBuildError) as exc:
        raise AcademyBuildError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AcademyBuildError(f"{path} must contain a JSON object")
    return value


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AcademyBuildError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AcademyBuildError(f"{label} must be an array")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AcademyBuildError(f"{label} must be a non-empty string")
    return value.strip()


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise AcademyBuildError(f"{label} must be a boolean")
    return value


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise AcademyBuildError(
            f"{label} must be an integer greater than or equal to {minimum}"
        )
    return value


def require_string_list(
    value: Any,
    label: str,
    *,
    allow_empty: bool = True,
) -> list[str]:
    values = require_list(value, label)
    result = [require_text(item, f"{label}[{index}]") for index, item in enumerate(values)]
    if not allow_empty and not result:
        raise AcademyBuildError(f"{label} must contain at least one item")
    if len(result) != len(set(result)):
        raise AcademyBuildError(f"{label} must not contain duplicate values")
    return result


def require_keys(
    value: dict[str, Any],
    label: str,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = sorted(required - value.keys())
    extra = sorted(value.keys() - required - optional)
    if missing:
        raise AcademyBuildError(f"{label} is missing required keys: {', '.join(missing)}")
    if extra:
        raise AcademyBuildError(f"{label} has unsupported keys: {', '.join(extra)}")


def normalize_config(document: dict[str, Any]) -> dict[str, Any]:
    require_keys(
        document,
        "academy config",
        {
            "schema",
            "version",
            "title",
            "description",
            "disclaimer",
            "milestones",
            "ecosystem",
            "paths",
        },
    )
    if document["schema"] != CONFIG_SCHEMA:
        raise AcademyBuildError(
            f"academy config schema must be {CONFIG_SCHEMA!r}, got {document['schema']!r}"
        )
    version = require_text(document["version"], "academy config version")
    title = require_text(document["title"], "academy config title")
    if title != "Microsoft AI Academy":
        raise AcademyBuildError("academy config title must be 'Microsoft AI Academy'")
    description = require_text(document["description"], "academy config description")
    disclaimer = require_text(document["disclaimer"], "academy config disclaimer")

    milestone_rows = require_list(document["milestones"], "academy config milestones")
    if len(milestone_rows) != len(EXPECTED_MILESTONES):
        raise AcademyBuildError(
            f"academy config must define exactly {len(EXPECTED_MILESTONES)} milestones"
        )
    milestones: list[dict[str, Any]] = []
    contract: list[tuple[str, str, int]] = []
    for index, raw in enumerate(milestone_rows):
        row = require_mapping(raw, f"academy config milestones[{index}]")
        require_keys(
            row,
            f"academy config milestones[{index}]",
            {"id", "claim_id", "title", "description", "points"},
        )
        milestone = {
            "id": require_text(row["id"], f"academy config milestones[{index}].id"),
            "claim_id": require_text(
                row["claim_id"], f"academy config milestones[{index}].claim_id"
            ),
            "title": require_text(
                row["title"], f"academy config milestones[{index}].title"
            ),
            "description": require_text(
                row["description"], f"academy config milestones[{index}].description"
            ),
            "points": require_int(
                row["points"], f"academy config milestones[{index}].points", 1
            ),
        }
        contract.append(
            (milestone["id"], milestone["claim_id"], milestone["points"])
        )
        milestones.append(milestone)
    if tuple(contract) != EXPECTED_MILESTONES:
        raise AcademyBuildError(
            "academy milestone local IDs, claim IDs, or points do not match the "
            "canonical 150-point achievement contract"
        )

    ecosystem_rows = require_list(document["ecosystem"], "academy config ecosystem")
    if len(ecosystem_rows) != len(EXPECTED_ECOSYSTEM_TITLES):
        raise AcademyBuildError(
            f"academy config must define exactly {len(EXPECTED_ECOSYSTEM_TITLES)} "
            "ecosystem stages"
        )
    ecosystem: list[dict[str, str]] = []
    ecosystem_ids: set[str] = set()
    for index, raw in enumerate(ecosystem_rows):
        row = require_mapping(raw, f"academy config ecosystem[{index}]")
        require_keys(
            row,
            f"academy config ecosystem[{index}]",
            {"id", "title", "description"},
        )
        stage = {
            "id": require_text(row["id"], f"academy config ecosystem[{index}].id"),
            "title": require_text(
                row["title"], f"academy config ecosystem[{index}].title"
            ),
            "description": require_text(
                row["description"], f"academy config ecosystem[{index}].description"
            ),
        }
        if stage["id"] in ecosystem_ids:
            raise AcademyBuildError(f"duplicate ecosystem stage ID: {stage['id']}")
        ecosystem_ids.add(stage["id"])
        ecosystem.append(stage)
    if tuple(stage["title"] for stage in ecosystem) != EXPECTED_ECOSYSTEM_TITLES:
        raise AcademyBuildError(
            "academy ecosystem stages must match the five required learning stages"
        )

    path_rows = require_list(document["paths"], "academy config paths")
    if len(path_rows) != len(EXPECTED_PATH_IDS):
        raise AcademyBuildError(
            f"academy config must define exactly {len(EXPECTED_PATH_IDS)} learning paths"
        )
    paths: list[dict[str, Any]] = []
    path_ids: set[str] = set()
    for index, raw in enumerate(path_rows):
        row = require_mapping(raw, f"academy config paths[{index}]")
        require_keys(
            row,
            f"academy config paths[{index}]",
            {"id", "title", "description", "audience", "level", "categories"},
            {"curated_slugs"},
        )
        path_id = require_text(row["id"], f"academy config paths[{index}].id")
        if path_id in path_ids:
            raise AcademyBuildError(f"duplicate learning path ID: {path_id}")
        path_ids.add(path_id)
        path = {
            "id": path_id,
            "title": require_text(
                row["title"], f"academy config paths[{index}].title"
            ),
            "description": require_text(
                row["description"], f"academy config paths[{index}].description"
            ),
            "audience": require_text(
                row["audience"], f"academy config paths[{index}].audience"
            ),
            "level": require_text(
                row["level"], f"academy config paths[{index}].level"
            ),
            "categories": sorted(
                require_string_list(
                    row["categories"], f"academy config paths[{index}].categories"
                )
            ),
            "curated_slugs": sorted(
                require_string_list(
                    row.get("curated_slugs", []),
                    f"academy config paths[{index}].curated_slugs",
                )
            ),
        }
        paths.append(path)
    if path_ids != EXPECTED_PATH_IDS:
        missing = sorted(EXPECTED_PATH_IDS - path_ids)
        extra = sorted(path_ids - EXPECTED_PATH_IDS)
        raise AcademyBuildError(
            f"academy path IDs do not match the required set; missing={missing}, extra={extra}"
        )

    start_here = next(path for path in paths if path["id"] == "start-here")
    if start_here["categories"]:
        raise AcademyBuildError("start-here must use curated slugs, not categories")
    if set(start_here["curated_slugs"]) != EXPECTED_START_HERE:
        raise AcademyBuildError(
            "start-here curated slugs must be ai-customer-assistant, ask-hr, "
            "building-permit-processing, and account-intelligence"
        )

    return {
        "version": version,
        "title": title,
        "description": description,
        "disclaimer": disclaimer,
        "milestones": milestones,
        "ecosystem": ecosystem,
        "paths": paths,
    }


def parse_skill(path: Path, root: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise AcademyBuildError(f"cannot read packaged skill {path}: {exc}") from exc
    if not lines or lines[0].strip() != "---":
        raise AcademyBuildError(f"{path}: SKILL.md must begin with YAML front matter")
    try:
        closing = next(
            index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise AcademyBuildError(f"{path}: YAML front matter is not closed") from exc

    metadata: dict[str, str] = {}
    for line_number, raw_line in enumerate(lines[1:closing], 2):
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise AcademyBuildError(
                f"{path}:{line_number}: front matter must use simple key: value entries"
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key not in {"name", "description"}:
            raise AcademyBuildError(
                f"{path}:{line_number}: unsupported front matter key {key!r}"
            )
        if key in metadata:
            raise AcademyBuildError(
                f"{path}:{line_number}: duplicate front matter key {key!r}"
            )
        if not value or value in {"|", ">"}:
            raise AcademyBuildError(
                f"{path}:{line_number}: {key} must be a simple non-empty scalar"
            )
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1].strip()
        if not value:
            raise AcademyBuildError(
                f"{path}:{line_number}: {key} must be a non-empty scalar"
            )
        metadata[key] = value

    missing = {"name", "description"} - metadata.keys()
    if missing:
        raise AcademyBuildError(
            f"{path}: missing front matter keys: {', '.join(sorted(missing))}"
        )
    title = next(
        (line[2:].strip() for line in lines[closing + 1 :] if line.startswith("# ")),
        "",
    )
    if not title:
        raise AcademyBuildError(f"{path}: SKILL.md must contain a level-one title")
    try:
        relative_path = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise AcademyBuildError(f"packaged skill is outside the repository root: {path}") from exc
    return {
        "name": metadata["name"],
        "title": title,
        "description": metadata["description"],
        "path": relative_path,
    }


def discover_skills(solution_dir: Path, root: Path) -> list[dict[str, str]]:
    skills_dir = solution_dir / "manual" / "skills"
    if not skills_dir.is_dir():
        raise AcademyBuildError(f"required packaged skills directory is missing: {skills_dir}")
    children = sorted(skills_dir.iterdir(), key=lambda item: item.name.casefold())
    if not children:
        raise AcademyBuildError(f"course must package at least one manual skill: {skills_dir}")

    skill_files: list[Path] = []
    for child in children:
        skill_file = child / "SKILL.md"
        if not child.is_dir() or not skill_file.is_file():
            raise AcademyBuildError(
                f"{skills_dir}: every direct child must be a skill directory containing SKILL.md "
                f"(invalid entry: {child.name})"
            )
        skill_files.append(skill_file)

    skills = [parse_skill(path, root) for path in skill_files]
    skills.sort(key=lambda row: (row["name"].casefold(), row["path"]))
    names = [skill["name"] for skill in skills]
    if len(names) != len(set(names)):
        raise AcademyBuildError(f"{skills_dir}: packaged skill names must be unique")
    return skills


def unique_sorted_strings(values: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    strings = require_string_list(values, label, allow_empty=allow_empty)
    return sorted(strings, key=lambda value: (value.casefold(), value))


def resolve_paths(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def build_academy(
    root: Path,
    config_document: dict[str, Any],
    registry: dict[str, Any],
    solutions_document: dict[str, Any],
    rollout_document: dict[str, Any],
) -> dict[str, Any]:
    config = normalize_config(config_document)

    if registry.get("schema") != REGISTRY_SCHEMA:
        raise AcademyBuildError(
            f"registry schema must be {REGISTRY_SCHEMA!r}, got {registry.get('schema')!r}"
        )
    generated_at = require_text(registry.get("generated_at"), "registry generated_at")
    registry_agents = require_list(registry.get("agents"), "registry agents")
    agents_by_name: dict[str, dict[str, Any]] = {}
    for index, raw_agent in enumerate(registry_agents):
        agent = require_mapping(raw_agent, f"registry agents[{index}]")
        name = require_text(agent.get("name"), f"registry agents[{index}].name")
        if name in agents_by_name:
            raise AcademyBuildError(f"registry contains duplicate agent name: {name}")
        agents_by_name[name] = agent

    if solutions_document.get("schema") != SOLUTIONS_SCHEMA:
        raise AcademyBuildError(
            f"solutions schema must be {SOLUTIONS_SCHEMA!r}, "
            f"got {solutions_document.get('schema')!r}"
        )
    canonical = require_mapping(
        solutions_document.get("solutions"), "solutions catalog solutions"
    )
    if len(canonical) != EXPECTED_COURSES:
        raise AcademyBuildError(
            f"solutions catalog must contain exactly {EXPECTED_COURSES} courses, "
            f"found {len(canonical)}"
        )
    excluded_key = "@aibast-agents-library/grid-outage-response"
    if excluded_key in canonical:
        raise AcademyBuildError(
            "grid-outage-response must remain excluded because it is not an advertised course"
        )

    if rollout_document.get("schema") != ROLLOUT_SCHEMA:
        raise AcademyBuildError(
            f"rollout schema must be {ROLLOUT_SCHEMA!r}, "
            f"got {rollout_document.get('schema')!r}"
        )
    if require_int(rollout_document.get("total"), "rollout total") != EXPECTED_COURSES:
        raise AcademyBuildError(f"rollout total must be exactly {EXPECTED_COURSES}")
    if require_int(rollout_document.get("passed"), "rollout passed") != EXPECTED_COURSES:
        raise AcademyBuildError(f"rollout passed must be exactly {EXPECTED_COURSES}")
    if require_int(rollout_document.get("failed"), "rollout failed") != 0:
        raise AcademyBuildError("rollout failed must be zero")
    rollout_rows = require_list(rollout_document.get("solutions"), "rollout solutions")
    if len(rollout_rows) != EXPECTED_COURSES:
        raise AcademyBuildError(
            f"rollout must contain exactly {EXPECTED_COURSES} solution rows"
        )
    rollout_by_slug: dict[str, dict[str, Any]] = {}
    for index, raw_rollout in enumerate(rollout_rows):
        row = require_mapping(raw_rollout, f"rollout solutions[{index}]")
        slug = require_text(row.get("slug"), f"rollout solutions[{index}].slug")
        if slug in rollout_by_slug:
            raise AcademyBuildError(f"rollout contains duplicate course slug: {slug}")
        if require_bool(row.get("passed"), f"rollout solutions[{index}].passed") is not True:
            raise AcademyBuildError(f"rollout course is not certified: {slug}")
        failures = require_list(
            row.get("failures"), f"rollout solutions[{index}].failures"
        )
        if failures:
            raise AcademyBuildError(
                f"rollout course {slug} has certification failures: {failures}"
            )
        require_mapping(row.get("metrics"), f"rollout solutions[{index}].metrics")
        rollout_by_slug[slug] = row

    course_sources: list[dict[str, Any]] = []
    seen_course_slugs: set[str] = set()
    for agent_name in sorted(canonical):
        catalog_entry = require_mapping(
            canonical[agent_name], f"solutions catalog {agent_name}"
        )
        if not agent_name.startswith("@aibast-agents-library/"):
            raise AcademyBuildError(
                f"solutions catalog key is not an AIBAST agent name: {agent_name}"
            )
        agent = agents_by_name.get(agent_name)
        if agent is None:
            raise AcademyBuildError(
                f"canonical academy agent is missing from registry: {agent_name}"
            )
        solution = require_mapping(
            agent.get("_solution"), f"registry {agent_name}._solution"
        )
        package = require_mapping(
            solution.get("package"), f"registry {agent_name}._solution.package"
        )
        slug = require_text(package.get("slug"), f"registry {agent_name} package slug")
        if slug in seen_course_slugs:
            raise AcademyBuildError(f"duplicate canonical course slug: {slug}")
        seen_course_slugs.add(slug)
        expected_quest = f"solutions/{slug}/quest.html"
        expected_manual = f"solutions/{slug}/manual-tutorial.html"
        if package.get("quest_url") != expected_quest:
            raise AcademyBuildError(
                f"{agent_name}: package quest_url must be {expected_quest!r}"
            )
        if package.get("manual_tutorial_url") != expected_manual:
            raise AcademyBuildError(
                f"{agent_name}: package manual_tutorial_url must be {expected_manual!r}"
            )
        course_sources.append(
            {
                "agent_name": agent_name,
                "catalog": catalog_entry,
                "agent": agent,
                "solution": solution,
                "slug": slug,
            }
        )

    if set(rollout_by_slug) != seen_course_slugs:
        missing = sorted(seen_course_slugs - rollout_by_slug.keys())
        extra = sorted(rollout_by_slug.keys() - seen_course_slugs)
        raise AcademyBuildError(
            f"rollout course scope does not match the solutions catalog; "
            f"missing={missing}, extra={extra}"
        )

    path_specs = config["paths"]
    configured_curated = {
        slug for path in path_specs for slug in path["curated_slugs"]
    }
    unknown_curated = configured_curated - seen_course_slugs
    if unknown_curated:
        raise AcademyBuildError(
            f"academy paths curate unknown course slugs: {sorted(unknown_curated)}"
        )
    category_owners: dict[str, str] = {}
    for path in path_specs:
        if path["id"] == "start-here":
            continue
        if not path["categories"]:
            raise AcademyBuildError(
                f"primary learning path {path['id']} must define at least one category"
            )
        for category in path["categories"]:
            previous = category_owners.get(category)
            if previous is not None:
                raise AcademyBuildError(
                    f"category {category!r} belongs to multiple primary paths: "
                    f"{previous}, {path['id']}"
                )
            category_owners[category] = path["id"]

    courses: list[dict[str, Any]] = []
    skill_paths: set[str] = set()
    for source in sorted(course_sources, key=lambda row: row["slug"]):
        agent_name = source["agent_name"]
        catalog_entry = source["catalog"]
        agent = source["agent"]
        solution = source["solution"]
        slug = source["slug"]
        category = require_text(agent.get("category"), f"registry {agent_name}.category")
        if category not in INDUSTRY_NAMES:
            raise AcademyBuildError(
                f"{agent_name}: category {category!r} has no academy industry label"
            )
        primary_path = category_owners.get(category)
        if primary_path is None:
            raise AcademyBuildError(
                f"{agent_name}: category {category!r} has no non-start-here primary path"
            )
        primary_matches = [
            path["id"]
            for path in path_specs
            if path["id"] != "start-here" and category in path["categories"]
        ]
        if primary_matches != [primary_path]:
            raise AcademyBuildError(
                f"{agent_name}: course must have exactly one non-start-here primary path"
            )
        path_ids = [
            path["id"]
            for path in path_specs
            if (
                path["id"] == "start-here"
                and slug in path["curated_slugs"]
            )
            or (
                path["id"] != "start-here"
                and category in path["categories"]
            )
        ]
        if primary_path not in path_ids:
            raise AcademyBuildError(f"{agent_name}: primary path membership was not resolved")

        solution_dir = root / "solutions" / slug
        required_paths = {
            "quest_url": solution_dir / "quest.html",
            "field_guide_url": solution_dir / "field-guide.html",
            "manual_url": solution_dir / "manual-tutorial.html",
            "evidence_url": solution_dir / "evidence-report.html",
        }
        for label, path in required_paths.items():
            if not path.is_file():
                raise AcademyBuildError(
                    f"{agent_name}: required {label} file does not exist: {path}"
                )
        skills = discover_skills(solution_dir, root)
        for skill in skills:
            if skill["path"] in skill_paths:
                raise AcademyBuildError(
                    f"packaged skill path is not unique: {skill['path']}"
                )
            skill_paths.add(skill["path"])

        rollout = rollout_by_slug[slug]
        metrics = require_mapping(rollout["metrics"], f"rollout {slug}.metrics")
        demo_cases = require_int(
            metrics.get("locked_cases"), f"rollout {slug}.metrics.locked_cases", 1
        )
        manual_steps = require_int(
            metrics.get("manual_steps"), f"rollout {slug}.metrics.manual_steps", 1
        )
        demo = require_mapping(agent.get("_demo"), f"registry {agent_name}._demo")
        if demo.get("slug") != slug:
            raise AcademyBuildError(
                f"{agent_name}: registry demo slug {demo.get('slug')!r} "
                f"does not match package slug {slug!r}"
            )
        if require_int(demo.get("case_count"), f"registry {agent_name} demo case_count", 1) != demo_cases:
            raise AcademyBuildError(
                f"{agent_name}: registry demo case count does not match certified rollout"
            )

        solution_personas = require_string_list(
            solution.get("personas"), f"registry {agent_name} solution personas"
        )
        demo_personas = require_string_list(
            demo.get("personas"), f"registry {agent_name} demo personas"
        )
        personas = sorted(
            set(solution_personas or demo_personas),
            key=lambda value: (value.casefold(), value),
        )
        if not personas:
            raise AcademyBuildError(f"{agent_name}: course must identify at least one persona")
        platforms = sorted(
            set(
                require_string_list(
                    solution.get("featured_tools"),
                    f"registry {agent_name} solution featured_tools",
                )
            )
            | set(
                require_string_list(
                    solution.get("agent_requirements"),
                    f"registry {agent_name} solution agent_requirements",
                )
            ),
            key=lambda value: (value.casefold(), value),
        )
        if not platforms:
            raise AcademyBuildError(f"{agent_name}: course must identify at least one platform")

        courses.append(
            {
                "slug": slug,
                "agent": agent_name,
                "title": require_text(
                    catalog_entry.get("display_name"),
                    f"solutions catalog {agent_name}.display_name",
                ),
                "description": require_text(
                    catalog_entry.get("card_pitch"),
                    f"solutions catalog {agent_name}.card_pitch",
                ),
                "category": category,
                "industry": INDUSTRY_NAMES[category],
                "journey_stage": require_text(
                    catalog_entry.get("journey_stage"),
                    f"solutions catalog {agent_name}.journey_stage",
                ),
                "personas": personas,
                "platforms": platforms,
                "tags": unique_sorted_strings(
                    agent.get("tags"), f"registry {agent_name}.tags", allow_empty=False
                ),
                "outcomes": unique_sorted_strings(
                    solution.get("outcomes"),
                    f"registry {agent_name} solution outcomes",
                    allow_empty=False,
                ),
                "quest_url": f"solutions/{slug}/quest.html",
                "field_guide_url": f"solutions/{slug}/field-guide.html",
                "manual_url": f"solutions/{slug}/manual-tutorial.html",
                "evidence_url": f"solutions/{slug}/evidence-report.html",
                "added_at": require_text(
                    agent.get("_added_at"), f"registry {agent_name}._added_at"
                ),
                "has_demo_video": require_bool(
                    solution.get("has_demo_video"),
                    f"registry {agent_name} solution has_demo_video",
                ),
                "has_onepager": require_bool(
                    solution.get("has_onepager"),
                    f"registry {agent_name} solution has_onepager",
                ),
                "demo_cases": demo_cases,
                "manual_steps": manual_steps,
                "skills": skills,
                "skill_count": len(skills),
                "primary_path": primary_path,
                "path_ids": path_ids,
            }
        )

    if len(courses) != EXPECTED_COURSES:
        raise AcademyBuildError(
            f"academy generated {len(courses)} courses instead of {EXPECTED_COURSES}"
        )
    course_categories = {course["category"] for course in courses}
    configured_categories = set(category_owners)
    if course_categories != configured_categories:
        missing = sorted(course_categories - configured_categories)
        unused = sorted(configured_categories - course_categories)
        raise AcademyBuildError(
            f"learning path category coverage is not exact; missing={missing}, unused={unused}"
        )

    output_paths: list[dict[str, Any]] = []
    for path in path_specs:
        course_slugs = sorted(
            course["slug"] for course in courses if path["id"] in course["path_ids"]
        )
        if not course_slugs:
            raise AcademyBuildError(f"learning path {path['id']} has no courses")
        output_paths.append(
            {
                "id": path["id"],
                "title": path["title"],
                "description": path["description"],
                "audience": path["audience"],
                "level": path["level"],
                "categories": path["categories"],
                "course_slugs": course_slugs,
                "course_count": len(course_slugs),
            }
        )

    skill_count = sum(course["skill_count"] for course in courses)
    if skill_count != len(skill_paths):
        raise AcademyBuildError("academy packaged skill totals do not reconcile")
    points_per_course = sum(milestone["points"] for milestone in config["milestones"])
    if points_per_course != 150:
        raise AcademyBuildError("academy milestones must total exactly 150 points per course")

    return {
        "schema": OUTPUT_SCHEMA,
        "version": config["version"],
        "generated_at": generated_at,
        "title": config["title"],
        "description": config["description"],
        "disclaimer": config["disclaimer"],
        "summary": {
            "courses": len(courses),
            "skills": skill_count,
            "paths": len(output_paths),
            "industries": len({course["industry"] for course in courses}),
            "points_per_course": points_per_course,
        },
        "milestones": config["milestones"],
        "ecosystem": config["ecosystem"],
        "paths": output_paths,
        "courses": courses,
    }


def serialize(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def check_output(path: Path, expected: str) -> bool:
    if not path.is_file():
        raise AcademyBuildError(f"generated academy catalog does not exist: {path}")
    try:
        actual = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AcademyBuildError(f"cannot read generated academy catalog {path}: {exc}") from exc
    if actual == expected:
        return True
    diff = list(
        difflib.unified_diff(
            actual.splitlines(),
            expected.splitlines(),
            fromfile=str(path),
            tofile="generated academy catalog",
            lineterm="",
        )
    )
    preview = "\n".join(diff[:80])
    if len(diff) > 80:
        preview += f"\n... {len(diff) - 80} additional diff lines omitted"
    print(preview, file=sys.stderr)
    return False


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        description="Generate or check the deterministic Microsoft AI Academy catalog."
    )
    argument_parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root (default: inferred from this script).",
    )
    argument_parser.add_argument(
        "--config", default="academy/catalog.json", help="Academy configuration JSON."
    )
    argument_parser.add_argument(
        "--registry", default="registry.json", help="Generated agent registry JSON."
    )
    argument_parser.add_argument(
        "--solutions",
        default="solutions/catalog.json",
        help="Canonical advertised solutions catalog JSON.",
    )
    argument_parser.add_argument(
        "--rollout",
        default="state/workshop_course_rollout.json",
        help="Certified workshop rollout audit JSON.",
    )
    argument_parser.add_argument(
        "--out", default="academy.json", help="Generated public academy catalog JSON."
    )
    argument_parser.add_argument(
        "--check",
        action="store_true",
        help="Compare generated content with --out without writing it.",
    )
    return argument_parser


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root does not exist: {root}", file=sys.stderr)
        return 1
    config_path = resolve_paths(root, args.config)
    registry_path = resolve_paths(root, args.registry)
    solutions_path = resolve_paths(root, args.solutions)
    rollout_path = resolve_paths(root, args.rollout)
    output_path = resolve_paths(root, args.out)
    try:
        document = build_academy(
            root,
            read_json(config_path),
            read_json(registry_path),
            read_json(solutions_path),
            read_json(rollout_path),
        )
        rendered = serialize(document)
        if args.check:
            if not check_output(output_path, rendered):
                print(
                    f"error: {output_path} is out of date; "
                    "run scripts/build_academy.py and commit the result",
                    file=sys.stderr,
                )
                return 1
            action = "Checked"
        else:
            if not output_path.parent.is_dir():
                raise AcademyBuildError(
                    f"output directory does not exist: {output_path.parent}"
                )
            output_path.write_text(rendered, encoding="utf-8")
            action = "Generated"
    except (AcademyBuildError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = document["summary"]
    print(
        f"{action} {output_path}: {summary['courses']} courses, "
        f"{summary['skills']} skills, {summary['paths']} paths, "
        f"{summary['industries']} industries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
