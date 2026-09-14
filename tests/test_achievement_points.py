"""Tests for local and verified workshop achievements."""

import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tests.test_scaffold_solution_journey import build_fixture
from tools.scaffold_solution_journey import (
    ACHIEVEMENT_LABELS,
    ACHIEVEMENT_POINTS,
    ACHIEVEMENT_PROFILE_KEY,
    DARK_THEME_VARIABLES,
    THEME_SCRIPT,
    THEME_VARIABLES,
    WORKSHOP_ENGINE_SCRIPT,
    scaffold,
)


ROOT = Path(__file__).resolve().parent.parent


class StructureParser(HTMLParser):
    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack, f"unexpected closing tag </{tag}>"
        assert self.stack.pop() == tag


class InputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.mode_buttons = []

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.inputs.append(dict(attrs))
        elif tag == "button":
            attributes = dict(attrs)
            if "data-mode" in attributes:
                self.mode_buttons.append(attributes)


@pytest.fixture()
def achievement_pages(tmp_path):
    package, _frames = build_fixture(tmp_path)
    scaffold("demo-journey", root=tmp_path)
    return {
        "root": tmp_path,
        "quest": (package / "quest.html").read_text(encoding="utf-8"),
        "manual": (package / "manual-tutorial.html").read_text(encoding="utf-8"),
    }


def scripts(page):
    return re.findall(r"<script>(.*?)</script>", page, re.DOTALL)


def run_node(source, path):
    path.write_text(source, encoding="utf-8")
    result = subprocess.run(
        ["node", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def extract_function(source, name):
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", source)
    assert match, f"missing JavaScript function {name}"
    opening = source.find("{", match.end())
    assert opening >= 0, f"missing body for JavaScript function {name}"
    depth = 0
    index = opening
    state = "code"
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char in {"'", '"', "`"}:
                state = char
            elif char == "/" and next_char == "/":
                state = "line-comment"
                index += 1
            elif char == "/" and next_char == "*":
                state = "block-comment"
                index += 1
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[match.start() : index + 1]
        elif state in {"'", '"', "`"}:
            if char == "\\":
                index += 1
            elif char == state:
                state = "code"
        elif state == "line-comment":
            if char == "\n":
                state = "code"
        elif state == "block-comment":
            if char == "*" and next_char == "/":
                state = "code"
                index += 1
        index += 1
    raise AssertionError(f"unterminated JavaScript function {name}")


def extract_const(source, name):
    match = re.search(rf"\bconst\s+{re.escape(name)}\s*=", source)
    assert match, f"missing JavaScript const {name}"
    end = source.find(";", match.end())
    assert end >= 0, f"unterminated JavaScript const {name}"
    return source[match.start() : end + 1]


def checkpoint_records(page):
    parser = InputParser()
    parser.feed(page)
    records = []
    for attrs in parser.inputs:
        if "data-checkpoint" not in attrs:
            continue
        dataset = {}
        for name, value in attrs.items():
            if not name.startswith("data-"):
                continue
            parts = name[5:].split("-")
            dataset[parts[0] + "".join(part.title() for part in parts[1:])] = value
        records.append({"checked": False, "dataset": dataset})
    return records


def mode_button_records(page):
    parser = InputParser()
    parser.feed(page)
    return [
        {
            "attributes": {
                "aria-selected": attrs.get("aria-selected"),
            },
            "dataset": {
                "mode": attrs["data-mode"],
            },
        }
        for attrs in parser.mode_buttons
    ]


def run_easy_runtime(page, path):
    quest_script = scripts(page)[-1]
    start = quest_script.index("const ACHIEVEMENT_PROFILE_KEY")
    end = quest_script.index("const ACHIEVEMENT_CANONICAL_AGENT")
    runtime = quest_script[start:end]
    behavior = "\n".join(
        extract_function(quest_script, name)
        for name in (
            "currentEasyPath",
            "requiredEasyBoxes",
            "achievementGroupComplete",
            "activeDisplayMode",
            "evaluateAchievement",
        )
    )
    buttons_declaration = extract_const(quest_script, "buttons")
    records = checkpoint_records(page)
    button_records = mode_button_records(page)
    assert button_records
    expected_total = sum(
        record["dataset"]["achievementsPath"] in {"brainstem", "shared"}
        for record in records
    )
    probe = f"""
const values = new Map();
global.localStorage = {{
  getItem(key) {{ return values.has(key) ? values.get(key) : null; }},
  setItem(key, value) {{ values.set(key, value); }},
}};
function readWorkshopStorage(key, fallback = null) {{
  try {{
    const value = localStorage.getItem(key);
    return value === null ? fallback : value;
  }} catch (_error) {{
    return fallback;
  }}
}}
const globalEngineKey = "aibast:workshop-engine";
const modeKey = "aibast:demo-journey:quest-mode";
const boxes = {json.dumps(records)};
const modeButtons = {json.dumps(button_records)}.map((record) => ({{
  dataset: record.dataset,
  getAttribute(name) {{ return record.attributes[name] ?? null; }},
}}));
global.document = {{
  querySelectorAll(selector) {{
    return selector === "[data-mode]" ? modeButtons : [];
  }},
}};
{buttons_declaration}
function renderAchievementPanel() {{}}
function announceAchievementBadge() {{}}
{behavior}
function snapshot() {{
  const profile = readAchievementProfile();
  const workshop = profile.workshops[ACHIEVEMENT_WORKSHOP_SLUG] || {{}};
  return {{
    score: profile.score,
    achievements: Object.keys(workshop.achievements || {{}}).sort(),
    progress: workshop.progress || {{}},
  }};
}}
function markGroup(group) {{
  boxes
    .filter((box) =>
      box.dataset.achievementsGroup === group &&
      ["brainstem", "shared"].includes(box.dataset.achievementsPath))
    .forEach((box) => {{ box.checked = true; }});
  evaluateAchievement(false, true);
  return snapshot();
}}
const stages = {{
  local: markGroup("local-proof"),
  draft: markGroup("draft-builder"),
  preview: markGroup("preview-proven"),
}};
boxes
  .filter((box) => ["brainstem", "shared"].includes(box.dataset.achievementsPath))
  .forEach((box) => {{ box.checked = true; }});
evaluateAchievement(false, true);
stages.complete = snapshot();
console.log(JSON.stringify(stages));
"""
    return json.loads(run_node(runtime + probe, path)), expected_total


def assert_easy_runtime_complete(result, expected_total):
    assert {"started", "local-proof"}.issubset(result["local"]["achievements"])
    assert "draft-builder" in result["draft"]["achievements"]
    assert "preview-proven" in result["preview"]["achievements"]
    complete = result["complete"]
    assert {
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
        "workshop-complete",
    }.issubset(complete["achievements"])
    assert complete["score"] == 100
    assert complete["progress"]["easyChecked"] == expected_total
    assert complete["progress"]["easyTotal"] == expected_total
    assert complete["progress"]["easyComplete"] is True


def test_fixed_points_and_runtime_awards_are_idempotent_and_private(
    achievement_pages, tmp_path
):
    assert ACHIEVEMENT_PROFILE_KEY == "aibast:achievement-profile:v1"
    assert ACHIEVEMENT_POINTS == {
        "started": 5,
        "local-proof": 15,
        "draft-builder": 20,
        "preview-proven": 25,
        "workshop-complete": 35,
        "hard-mode-complete": 50,
    }
    assert ACHIEVEMENT_LABELS["hard-mode-complete"] == "Manual mode complete"

    quest_script = scripts(achievement_pages["quest"])[-1]
    start = quest_script.index("const ACHIEVEMENT_PROFILE_KEY")
    end = quest_script.index("const ACHIEVEMENT_CANONICAL_AGENT")
    runtime = quest_script[start:end]
    probe = (
        """
const values = new Map();
global.localStorage = {
  getItem(key) { return values.has(key) ? values.get(key) : null; },
  setItem(key, value) { values.set(key, value); },
};
localStorage.setItem(ACHIEVEMENT_PROFILE_KEY, "{");
const malformed = readAchievementProfile();
localStorage.setItem(ACHIEVEMENT_PROFILE_KEY, JSON.stringify({
  score: 999,
  name: "do not keep",
  email: "private@example.test",
  token: "secret",
  workshops: {
    "demo-journey": {
      slug: "demo-journey",
      mode: "easy",
      name: "also remove",
      achievements: {},
      progress: {},
    },
  },
}));
let profile = readAchievementProfile();
for (const badge of ACHIEVEMENT_BADGES) {
  let result = awardAchievement(profile, badge.id, "easy");
  profile = result.profile;
  result = awardAchievement(profile, badge.id, "easy");
  profile = result.profile;
}
const stored = localStorage.getItem(ACHIEVEMENT_PROFILE_KEY);
console.log(JSON.stringify({ malformed, profile: JSON.parse(stored), stored }));
"""
    )
    result = json.loads(run_node(runtime + probe, tmp_path / "achievements-runtime.js"))
    assert result["malformed"] == {"score": 0, "workshops": {}, "updatedAt": None}
    assert result["profile"]["score"] == 150
    assert set(result["profile"]) == {"score", "workshops", "updatedAt"}
    assert set(result["profile"]["workshops"]["demo-journey"]) == {
        "slug",
        "mode",
        "progress",
        "achievements",
    }
    for forbidden in ("private@example.test", "secret", '"name"', '"email"', '"token"'):
        assert forbidden not in result["stored"]


def test_generated_achievement_attributes_use_exact_plural_dataset_properties(
    achievement_pages,
):
    quest = achievement_pages["quest"]
    records = checkpoint_records(quest)
    assert records
    assert all(record["dataset"].get("achievementsPath") for record in records)
    assert all(record["dataset"].get("achievementsGroup") for record in records)
    assert "dataset.achievementsPath" in quest
    assert "dataset.achievementsGroup" in quest
    assert "dataset.achievementPath" not in quest
    assert "dataset.achievementGroup" not in quest


def test_easy_runtime_executes_checkpoint_groups_and_completion(
    achievement_pages,
    tmp_path,
):
    result, expected_total = run_easy_runtime(
        achievement_pages["quest"],
        tmp_path / "easy-achievement-runtime.js",
    )
    assert_easy_runtime_complete(result, expected_total)


def test_visual_and_achievement_engines_fail_closed_to_brainstem(
    achievement_pages,
    tmp_path,
):
    quest_script = scripts(achievement_pages["quest"])[-1]
    current_easy_path = extract_function(quest_script, "currentEasyPath")
    visual_source = WORKSHOP_ENGINE_SCRIPT
    safe_alias = "const localStorage = globalThis.aibastWorkshopStorage;"
    if (
        safe_alias in achievement_pages["quest"]
        and safe_alias not in visual_source
    ):
        visual_source = f"{safe_alias}\n{visual_source}"
    probe = f"""
const visualSource = {json.dumps(visual_source)};
function visual(value, denied = false) {{
  let selected = null;
  global.document = {{
    documentElement: {{
      setAttribute(name, next) {{
        if (name === "data-workshop-engine") selected = next;
      }},
    }},
  }};
  global.localStorage = {{
    getItem() {{
      if (denied) throw new Error("storage denied");
      return value;
    }},
  }};
  global.aibastWorkshopStorage = {{
    getItem() {{ return value; }},
    setItem() {{ return true; }},
  }};
  let error = null;
  try {{
    Function(visualSource)();
  }} catch (caught) {{
    error = caught.message;
  }}
  return {{ selected, error }};
}}
function readWorkshopStorage(key, fallback = null) {{
  try {{
    const value = localStorage.getItem(key);
    return value === null ? fallback : value;
  }} catch (_error) {{
    return fallback;
  }}
}}
const globalEngineKey = "aibast:workshop-engine";
{current_easy_path}
function achievement(value) {{
  global.localStorage = {{ getItem() {{ return value; }} }};
  return currentEasyPath();
}}
const values = [null, "brainstem", "invalid", "copilot"];
console.log(JSON.stringify({{
  visual: values.map((value) => visual(value)),
  visualDenied: visual(null, true),
  achievement: values.map((value) => achievement(value)),
}}));
"""
    result = json.loads(
        run_node(probe, tmp_path / "achievement-engine-defaults.js")
    )

    assert result["visual"] == [
        {"selected": "brainstem", "error": None},
        {"selected": "brainstem", "error": None},
        {"selected": "brainstem", "error": None},
        {"selected": "copilot", "error": None},
    ]
    assert result["visualDenied"] == {"selected": "brainstem", "error": None}
    assert result["achievement"] == [
        "brainstem",
        "brainstem",
        "brainstem",
        "copilot",
    ]


def test_named_checkpoint_conditions_and_existing_persistence(achievement_pages):
    quest = achievement_pages["quest"]
    manual = achievement_pages["manual"]

    for group in (
        "local-proof",
        "draft-builder",
        "preview-proven",
        "final-verdict",
    ):
        assert f'data-achievements-group="{group}"' in quest
    assert 'data-achievements-path="copilot"' in quest
    assert 'data-achievements-path="brainstem"' in quest
    assert 'data-achievements-path="shared"' in quest
    assert "dataset.achievementsPath" in quest
    assert "dataset.achievementsGroup" in quest
    assert "dataset.achievementPath" not in quest
    assert "dataset.achievementGroup" not in quest
    assert '["started", hasCheckpoint]' in quest
    assert '["local-proof", achievementGroupComplete("local-proof")]' in quest
    assert '["draft-builder", achievementGroupComplete("draft-builder")]' in quest
    assert '["preview-proven", achievementGroupComplete("preview-proven")]' in quest
    assert "easyChecked === easyRequired.length" in quest
    assert "boxes.length > 0 && done.length === boxes.length" in manual

    assert 'const progressKey = "aibast:demo-journey:quest-progress"' in quest
    assert 'parsed && typeof parsed === "object" && !Array.isArray(parsed)' in quest
    assert "box.checked = saved[box.dataset.checkpoint] === true" in quest
    assert "saved[box.dataset.checkpoint] = box.checked" in quest
    assert 'const key = "aibast:demo-journey:manual-progress"' in manual
    assert "saved = Array.isArray(parsed)" in manual
    assert 'parsed.filter((step) => typeof step === "string")' in manual
    assert "saved.includes(box.dataset.step)" in manual
    assert re.search(
        r'===\s*"copilot"\s*\?\s*"copilot"\s*:\s*"brainstem"',
        quest,
    )


def test_quest_syncs_all_earned_ids_without_automatic_submission(achievement_pages):
    quest = achievement_pages["quest"]
    assert "Workshop achievements" in quest
    assert "self-reported workshop progress" in quest
    assert 'id="achievements-total-score"' in quest
    assert 'id="achievements-workshop-score"' in quest
    assert 'id="achievements-badge-list"' in quest
    assert 'href="../../achievements.html"' in quest
    assert 'role="status" aria-live="polite" aria-atomic="true"' in quest
    assert 'data-achievements-sync hidden' in quest
    assert "Sync achievements to GitHub" in quest
    assert "Sync start to GitHub" not in quest
    assert "Claim verified completion" not in quest
    assert "data-achievements-claim" not in quest
    assert "earnedAchievementSyncIds(achievements).length === 0" in quest

    marker = "const body = `<!-- aibast-achievement-progress:v1 -->"
    assert marker in quest
    claim_body = quest.split(marker, 1)[1].split("`;", 1)[0]
    assert "aibast-achievement-progress/1.0" in claim_body
    assert "Workshop: \\`${ACHIEVEMENT_WORKSHOP_SLUG}\\`" in claim_body
    assert "Agent: \\`${ACHIEVEMENT_CANONICAL_AGENT}\\`" in claim_body
    assert claim_body.count("- Achievements: ") == 1
    assert "- Achievements: ${earnedIds.join(\", \")}" in claim_body
    assert "- Source: ${source.toString()}" in claim_body
    assert "- Event:" not in claim_body
    assert "- Achievement:" not in claim_body
    assert "points" not in claim_body.lower()
    assert "Opening this form does not sync anything" in claim_body
    assert "Resubmitting later merges newly earned IDs without duplicate score" in claim_body
    assert "server computes the verified score" in claim_body
    assert "One public GitHub issue submission opts this account" in claim_body
    assert "aibast-obsolete-achievement" not in quest
    assert "workshop-started" not in quest
    assert 'document.querySelector("[data-achievements-sync]").addEventListener("click"' in quest
    assert "window.open(url.toString(), \"_blank\", \"noopener\")" in quest
    assert "aibastSignalIssueUrl()" in quest
    assert "globalThis.location?.hostname" in quest
    assert "fetch(" not in quest
    assert ".submit(" not in quest
    assert "sendBeacon" not in quest
    assert "Report an issue" in quest

    canonical = [
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
        "workshop-completed",
        "hard-mode-completed",
    ]
    sync_order = quest.split("const ACHIEVEMENT_SYNC_ORDER", 1)[1].split("]);", 1)[0]
    positions = [sync_order.index(f'claimId: "{badge_id}"') for badge_id in canonical]
    assert positions == sorted(positions)
    assert len(re.findall(r"claimId:", sync_order)) == len(canonical)


def test_structured_signals_target_the_current_github_pages_owner(
    achievement_pages, tmp_path
):
    quest_script = scripts(achievement_pages["quest"])[-1]
    start = quest_script.index("function aibastSignalIssueUrl")
    end = quest_script.index("const ACHIEVEMENT_CANONICAL_AGENT")
    runtime = quest_script[start:end]
    probe = """
globalThis.location = { hostname: "kody-w.github.io" };
console.log(aibastSignalIssueUrl().toString());
"""

    assert run_node(runtime + probe, tmp_path / "achievements-signal-target.js") == (
        "https://github.com/kody-w/aibast-agents-library/issues/new"
    )


def test_manual_and_quest_share_direct_local_hard_progress(achievement_pages):
    manual = achievement_pages["manual"]
    quest = achievement_pages["quest"]
    assert ACHIEVEMENT_PROFILE_KEY in manual
    assert 'const key = "aibast:demo-journey:manual-progress"' in manual
    assert 'badgeIds.push("started")' in manual
    assert 'badgeIds.push("hard-mode-complete")' in manual
    assert "hardComplete: complete" in manual
    assert "fetch(" not in manual
    assert "postMessage" not in manual

    assert (
        'const hardProgressKey = "aibast:demo-journey:manual-progress"'
        in quest
    )
    assert 'document.querySelectorAll(".complete[data-step]")' in quest
    assert "function updateHardProgress" in quest
    assert "hardBoxes.length > 0 && done.length === hardBoxes.length" in quest
    assert "hardProgressActivated" in quest
    assert '"hard-mode-complete"' in quest
    assert "postMessage" not in quest
    assert "hardFrame" not in quest


def test_hard_progress_activation_and_persistence_are_guarded(achievement_pages):
    quest = achievement_pages["quest"]
    start = quest.index("function updateHardProgress")
    end = quest.index("function earnedAchievementSyncIds", start)
    handler = quest[start:end]

    assert re.search(
        r"if\s*\([^)]*(?:done\.length|\.checked)[^)]*\)"
        r"\s*(?:\{\s*)?hardProgressActivated\s*=\s*true",
        quest,
        re.DOTALL,
    )
    positive_guard = re.search(
        r"if\s*\([^)]*(?:hardProgressActivated|persist)[^)]*\)"
        r"\s*\{?[\s\S]{0,500}hardProgressKey",
        handler,
    )
    negative_guard = re.search(
        r"if\s*\(\s*!\s*hardProgressActivated\s*\)"
        r"\s*(?:\{\s*)?return[\s\S]{0,500}hardProgressKey",
        handler,
    )
    assert positive_guard or negative_guard


def test_manual_transition_truth_is_measured_in_browser():
    gate = (
        ROOT / "browser-audit" / "academy-course-audit.mjs"
    ).read_text(encoding="utf-8")
    assert "zero Hard progress is not persisted at startup" in gate
    assert "opening Manual does not change achievement mode" in gate
    assert "opening Manual preserves Easy completion" in gate
    assert "first real Hard check switches achievement mode" in gate
    assert "first real Hard check persists progress" in gate


def test_achievements_page_theme_accessibility_and_explanations(tmp_path):
    page = (ROOT / "achievements.html").read_text(encoding="utf-8")
    assert THEME_SCRIPT in page
    assert THEME_VARIABLES in page
    assert DARK_THEME_VARIABLES in page
    assert "Workshop Achievements" in page
    assert ("Agent " + "Growth") not in page
    assert "".join(("A", "G", "I")) not in page
    assert "not an evaluation of agent capability" in page
    assert "local points are private, self-reported checkpoint progress" in page
    assert "No local progress is sent automatically" in page
    assert "Local unsynced" in page
    assert "Verified synced" in page
    assert "Opening the prefilled form is not a sync until it is submitted" in page
    assert "Resubmitting later merges newly earned canonical badge IDs" in page
    assert "One public GitHub issue submission opts that account" in page
    assert "aibast-obsolete-achievement" not in page
    assert "state/metrics.json" in page
    assert "verified_achievements" in page
    assert "does not authenticate the account, prove ownership" in page
    assert "third-party" not in page.lower()
    assert "sendBeacon" not in page
    assert "XMLHttpRequest" not in page
    assert page.count("fetch(") == 1
    assert 'fetch("state/metrics.json", {' in page
    assert 'cache: "no-store"' in page
    assert re.search(r"\bBeta\b", page) is None
    assert 'class="skip-link"' in page
    assert 'aria-live="polite"' in page
    assert 'aria-busy="true"' in page
    assert 'aria-current="page"' in page

    parser = StructureParser()
    parser.feed(page)
    parser.close()
    assert parser.stack == []
    for index, script in enumerate(scripts(page)):
        result = subprocess.run(
            ["node", "--check", "-"],
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, f"script {index}: {result.stderr}"


def test_verified_sync_matching_uses_canonical_deduplicated_ids(tmp_path):
    page = (ROOT / "achievements.html").read_text(encoding="utf-8")
    main_script = scripts(page)[-1]
    start = main_script.index("const PROFILE_KEY")
    end = main_script.index("function renderPublic")
    sync_runtime = main_script[start:end]
    probe = """
const values = new Map();
global.localStorage = {
  getItem(key) { return values.has(key) ? values.get(key) : null; },
  setItem(key, value) { values.set(key, value); },
};
const canonical = canonicalClaimIds([
  "hard-mode-completed",
  "started",
  "started",
  "unknown",
  "workshop-completed",
  "local-proof",
]);
collectVerifiedForHighlight([
  {
    github_username: "octocat",
    workshops: {
      "demo-journey": {
        achievements: [
          "preview-proven",
          "started",
          "preview-proven",
          "not-canonical",
        ],
      },
    },
  },
], "octocat");
const verified = CLAIM_ORDER.filter((id) =>
  verifiedByWorkshop.get("demo-journey")?.has(id),
);
console.log(JSON.stringify({ canonical, verified }));
"""
    result = json.loads(
        run_node(sync_runtime + probe, tmp_path / "achievements-verified-sync.js")
    )
    assert result["canonical"] == [
        "started",
        "local-proof",
        "workshop-completed",
        "hard-mode-completed",
    ]
    assert result["verified"] == ["started", "preview-proven"]


def test_verified_sync_matching_consumes_server_badge_rows(tmp_path):
    page = (ROOT / "achievements.html").read_text(encoding="utf-8")
    main_script = scripts(page)[-1]
    start = main_script.index("const PROFILE_KEY")
    end = main_script.index("function renderPublic")
    sync_runtime = main_script[start:end]
    probe = """
const values = new Map();
global.localStorage = {
  getItem(key) { return values.has(key) ? values.get(key) : null; },
  setItem(key, value) { values.set(key, value); },
};
collectVerifiedForHighlight([
  {
    login: "OctoCat",
    points: 55,
    achievement_count: 3,
    starts: 1,
    workshop_completions: 1,
    hard_completions: 0,
    badges: [
      { workshop: "demo-journey", achievement: "started", points: 5 },
      { workshop: "demo-journey", achievement: "local-proof", points: 15 },
      {
        workshop: "demo-journey",
        achievement: "workshop-completed",
        points: 35,
      },
    ],
    achievement_ids: [
      "demo-journey:started",
      "demo-journey:local-proof",
      "demo-journey:workshop-completed",
    ],
    completed_workshops: ["demo-journey"],
  },
  {
    login: "octocat",
    badges: [
      null,
      { workshop: "../invalid", achievement: "started", points: 5 },
      { workshop: "demo-journey", achievement: "unknown", points: 999 },
      { workshop: 42, achievement: "preview-proven", points: 25 },
      { workshop: "demo-journey", achievement: null, points: 25 },
    ],
    achievement_ids: ["demo-journey:hard-mode-completed"],
  },
], "octocat");
const verified = CLAIM_ORDER.filter((id) =>
  verifiedByWorkshop.get("demo-journey")?.has(id),
);
const counts = {
  canonical: verifiedWorkshopCompletionCount({
    workshop_completions: 1,
    completed_workshops: ["wrong-precedence"],
  }),
  slugList: verifiedWorkshopCompletionCount({
    completed_workshops: ["one", "two"],
  }),
  invalid: verifiedWorkshopCompletionCount({
    workshop_completions: "not-a-number",
  }),
};
console.log(JSON.stringify({
  verified,
  workshopCount: verifiedByWorkshop.size,
  counts,
}));
"""
    result = json.loads(
        run_node(sync_runtime + probe, tmp_path / "achievements-server-badges.js")
    )
    assert result == {
        "verified": ["started", "local-proof", "workshop-completed"],
        "workshopCount": 1,
        "counts": {"canonical": 1, "slugList": 2, "invalid": 0},
    }


def test_achievements_reset_export_import_sanitize_secrets(tmp_path):
    page = (ROOT / "achievements.html").read_text(encoding="utf-8")
    assert f'const PROFILE_KEY = "{ACHIEVEMENT_PROFILE_KEY}"' in page
    assert 'const HIGHLIGHT_KEY = "aibast:achievement-highlight:v1"' in page
    assert "localStorage.removeItem(PROFILE_KEY)" in page
    assert "JSON.stringify(readProfile(), null, 2)" in page
    assert "writeProfile(JSON.parse(await file.text()))" in page
    assert "unknown and sensitive fields were discarded" in page
    assert "link.download = \"aibast-achievement-profile.json\"" in page
    assert "localStorage.setItem(HIGHLIGHT_KEY, username)" in page

    main_script = scripts(page)[-1]
    start = main_script.index("const PROFILE_KEY")
    end = main_script.index("function displaySlug")
    sanitizer = main_script[start:end]
    probe = """
const values = new Map();
global.localStorage = {
  getItem(key) { return values.has(key) ? values.get(key) : null; },
  setItem(key, value) { values.set(key, value); },
};
localStorage.setItem(PROFILE_KEY, JSON.stringify({
  name: "Private Person",
  email: "private@example.test",
  token: "secret-token",
  score: 9000,
  workshops: {
    "demo-journey": {
      slug: "demo-journey",
      mode: "easy",
      github_username: "not-exported",
      progress: { easyChecked: 1, easyTotal: 3 },
      achievements: { started: { earned: true, earnedAt: "2026-08-09T12:00:00Z" } },
    },
  },
}));
writeProfile(readProfile());
console.log(localStorage.getItem(PROFILE_KEY));
"""
    stored = run_node(sanitizer + probe, tmp_path / "achievements-sanitize.js")
    profile = json.loads(stored)
    assert profile["score"] == 5
    assert set(profile) == {"score", "workshops", "updatedAt"}
    for forbidden in (
        "Private Person",
        "private@example.test",
        "secret-token",
        "not-exported",
        '"name"',
        '"email"',
        '"token"',
        '"github_username"',
    ):
        assert forbidden not in stored
