import re
import shutil
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "metrics-admin-setup.html"
HTML = PAGE.read_text(encoding="utf-8")

FIRST_THEME_SCRIPT = """(() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();"""

EXACT_THEME = """:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}"""


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if self.hidden_depth == 0:
            self.parts.append(data)


def visible_text():
    parser = VisibleTextParser()
    parser.feed(HTML)
    return " ".join(" ".join(parser.parts).split())


def inline_scripts():
    return re.findall(r"<script\b[^>]*>(.*?)</script>", HTML, re.DOTALL)


def test_page_is_self_contained_and_inline_scripts_parse_with_node():
    assert PAGE.is_file()
    assert shutil.which("node"), "Node.js is required to validate inline scripts"
    assert "<script src=" not in HTML
    assert not re.search(r"<link\b[^>]*rel=[\"']stylesheet", HTML, re.IGNORECASE)

    scripts = inline_scripts()
    assert len(scripts) == 2
    for script in scripts:
        result = subprocess.run(
            ["node", "--check"],
            input=script,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_exact_theme_script_is_the_first_script():
    scripts = inline_scripts()
    assert scripts[0].strip() == FIRST_THEME_SCRIPT
    assert HTML.index("<script>") < HTML.index("<meta charset=")


def test_exact_cp_theme_tokens_and_required_fonts():
    assert EXACT_THEME in HTML
    assert HTML.count(":root {") == 1
    assert HTML.count('html[data-theme="dark"] {') == 1

    expected_names = re.findall(r"(--cp-[\w-]+):", EXACT_THEME)
    actual_names = re.findall(r"(--cp-[\w-]+)\s*:", HTML)
    assert Counter(actual_names) == Counter(expected_names)

    assert (
        'font-family: "Segoe UI", Aptos, Calibri, -apple-system, '
        "BlinkMacSystemFont, sans-serif;"
    ) in HTML
    assert 'font-family: Consolas, "Courier New", Courier, monospace;' in HTML


def test_component_css_uses_cp_tokens_without_hardcoded_colors():
    style = re.search(r"<style>(.*?)</style>", HTML, re.DOTALL).group(1)
    component_css = style.replace(EXACT_THEME, "", 1)

    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", component_css)
    assert not re.search(r"\b(?:rgb|rgba|hsl|hsla)\s*\(", component_css)
    assert "linear-gradient" not in component_css

    color_properties = {
        "accent-color",
        "background",
        "background-color",
        "border",
        "border-bottom",
        "border-left",
        "border-right",
        "border-top",
        "box-shadow",
        "color",
        "outline",
    }
    for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", component_css):
        if name in color_properties and value.strip() != "0":
            assert "var(--cp-" in value, f"{name} bypasses cp tokens: {value}"


def test_aibast_topbar_has_required_links_in_order_and_theme_toggle():
    nav = re.search(
        r'<nav class="topnav".*?</nav>',
        HTML,
        re.DOTALL,
    ).group(0)
    labels = ["Library", "Metrics", "Production Guide", "Report an issue"]
    positions = [nav.index(f">{label}<") for label in labels]
    assert positions == sorted(positions)
    assert 'id="themeToggle"' in nav
    assert 'aria-label="Toggle color theme"' in nav


def test_has_exactly_ten_numbered_administrator_steps():
    assert re.findall(r'data-step="(\d+)"', HTML) == [str(number) for number in range(1, 11)]
    assert HTML.count('class="step-card"') == 10
    assert '<ol class="steps"' in HTML


def test_required_setup_permissions_commands_and_acceptance_checks_are_present():
    text = visible_text()
    required_visible_phrases = (
        "dedicated administrator or service account",
        "write or admin access",
        "token owner",
        "expiration date",
        "Repository Administration: Read-only",
        "Metadata read",
        "Issues read-only",
        "required Issues: Read-only",
        "workshop-feedback and opt-in achievement progress issues",
        "no Contents write is needed for the PAT itself",
        "Authorize the token for Microsoft SAML/SSO",
        "Settings → Secrets and variables → Actions",
        "Read and write permissions",
        "workflow GITHUB_TOKEN",
        "Authorize the autonomous compiler workflows",
        "repository default branch",
        "receives issue events for opened, edited, closed, and reopened activity",
        "manage feedback and achievement labels",
        "dispatch metrics.yml",
        "discussions: write",
        "scripts/sync_agent_discussions.py",
        "state/agent_discussions.json",
        "traffic read live",
        "workshop scope is 51",
        "Grid Outage excluded",
        "no unavailable_reason",
        "traffic.live",
        "traffic.as_of",
        "aibast-agent-discussion:v1",
        "aibast-agent-discussion/1.0",
        "aibast-workshop-feedback:v1",
        "aibast-workshop-feedback/1.0",
        "aibast-achievement-progress:v1",
        "aibast-achievement-progress/1.0",
        "Achievement progress signal",
        "Submitting the public issue explicitly opts the GitHub login",
        "maximum of 150 per workshop",
        "never infers missing prerequisite IDs",
        "Claims containing a",
        "achievement-progress",
        "achievements.totals",
        "achievements.profiles",
        "achievements.workshops",
        "achievements.achievements",
        "one active upvote per signed-in GitHub account",
        "publishes only the aggregate upvoteCount",
        "never combines duplicate mirror threads",
        "totals.agent_upvotes",
        "totals.agent_acquisitions",
        "agent_metrics",
        "leaderboards.most_upvoted",
        "leaderboards.most_acquired",
        "agent_upvotes",
        "usage_events",
        "exactly 51 rows",
        "Download totals reconcile",
        "source and coverage caveats",
        "Refresh",
        "Record acquisition",
        "Most upvoted",
        "Most acquired",
        "workshop leaderboard",
        "Rotate before expiry",
        "revoke the credential immediately",
        "snapshots reuse the last authorized traffic read instead of zeroing",
        "aibast-impact-report",
        "weekly/monthly impact exports",
        "Baseline pending",
        "impact-report-email.txt",
        "RAR is intentionally excluded",
        "never commit a token",
    )
    for phrase in required_visible_phrases:
        assert phrase.lower() in text.lower(), phrase

    required_commands = (
        "gh secret set METRICS_TOKEN --repo microsoft/aibast-agents-library",
        "contents: write",
        "discussions: write",
        "issues: read",
        "actions: write",
        "issues: write",
        "gh workflow run metrics.yml --repo microsoft/aibast-agents-library --ref main",
        'read -s -p "Fine-grained PAT: " GH_TOKEN',
        "export GH_TOKEN",
        "gh api repos/microsoft/aibast-agents-library/traffic/clones",
        "unset GH_TOKEN",
        "python3 -m json.tool state/metrics.json",
    )
    for command in required_commands:
        assert command in HTML


def test_issues_read_is_required_for_all_structured_issue_sources():
    text = visible_text()
    assert "Issues Read-only (required)" in text
    assert "required Issues: Read-only" in text
    assert "workshop-feedback and opt-in achievement progress issues" in text
    assert "opt-in achievement progress issues" in text
    assert "required issues: read" in text.lower()
    assert not re.search(r"\boptional\b.{0,80}\bIssues\b", text, re.IGNORECASE)
    assert not re.search(r"\bIssues\b.{0,80}\boptional\b", text, re.IGNORECASE)


def test_autonomous_compiler_permissions_and_marker_removal_go_live_are_checked():
    text = visible_text()
    for workflow_path in (
        ".github/workflows/workshop-feedback.yml",
        ".github/workflows/metrics.yml",
    ):
        assert workflow_path in HTML
    for permission in (
        "actions: write",
        "issues: write",
        "issues: read",
        "discussions: write",
        "contents: write",
    ):
        assert f"<code>{permission}</code>" in HTML or permission in HTML
    for phrase in (
        "exists on the repository default branch",
        "receives issue events for opened, edited, closed, and reopened activity",
        "dispatch metrics.yml on the repository default branch",
        "synchronizes the canonical agent Discussions",
        "runs before scripts/build_metrics.py",
        "GitHub does not emit an Actions event for native Discussion upvotes",
        "next scheduled or manually dispatched metrics run",
    ):
        assert phrase.lower() in text.lower(), phrase


def test_per_agent_discussion_ingestion_deduplication_and_privacy_are_checked():
    text = visible_text()
    for phrase in (
        "<!-- aibast-agent-discussion:v1 -->",
        "aibast-agent-discussion/1.0",
        "Signal: upvote",
        "Signal: acquisition",
        "<!-- aibast-workshop-feedback:v1 -->",
        "aibast-workshop-feedback/1.0",
        "one active upvote per signed-in GitHub account",
        "publishes only the aggregate upvoteCount",
        "never combines duplicate mirror threads",
        "never GitHub logins",
        "never GitHub logins, account identifiers, or voter lists",
    ):
        assert phrase.lower() in text.lower(), phrase


def test_achievement_marker_schema_consent_dedupe_scoring_aggregates_and_privacy_are_checked():
    text = visible_text()
    assert "aibast-achievements-achievement" not in HTML
    for phrase in (
        "<!-- aibast-achievement-progress:v1 -->",
        "aibast-achievement-progress/1.0",
        "canonical 51 with Grid Outage excluded",
        "canonical primary agent",
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
        "workshop-completed",
        "hard-mode-completed",
        "case-insensitive GitHub login + workshop + achievement",
        "Re-sync adds new badges without duplicating points",
        "maximum of 150 per workshop",
        "Claims containing a",
        "explicitly opts the GitHub login into a public profile",
        "Invalid, quoted, duplicate-field, conflicting, pull-request, unknown-user",
        "only the achievement-progress label",
        "persists no issue body, free text, source issue ID",
        "Offline runs carry forward that prior block",
    ):
        assert phrase.lower() in text.lower(), phrase
    canonical_ids = (
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
        "workshop-completed",
        "hard-mode-completed",
    )
    positions = [HTML.index(f"<code>{value}</code>") for value in canonical_ids]
    assert positions == sorted(positions)
    for forbidden in ("Points", "Point", "Score"):
        assert f"<code>{forbidden}</code>" in HTML
    assert (
        "GitHub verification confirms authenticated issue authorship and canonical "
        "claim format only; achievement completion remains self-reported and is "
        "not independently proven."
    ) in text


def test_achievement_snapshot_and_page_checks_keep_all_other_metrics_separate():
    for field in (
        "achievements.status",
        "achievements.as_of",
        "achievements.coverage",
        "achievements.caveat",
        "achievements.totals",
        "achievements.profiles",
        "achievements.workshops",
        "achievements.achievements",
        "usage_events",
        "totals.agent_upvotes",
        "totals.agent_acquisitions",
        "repo.stars",
    ):
        assert field in HTML
    text = visible_text().lower()
    assert "maximum of 150 per workshop" in text
    assert "fixed server points" in text
    assert "independently from" in text
    for metric in (
        "usage_events",
        "agent upvotes",
        "signed-in acquisitions",
        "downloads",
        "repository stars",
    ):
        assert metric in text
    assert "without cross-metric double counting" in text
    assert "local self-paced achievements" in text
    assert "verified public achievements" in text


def test_snapshot_contract_uses_per_agent_upvotes_not_repository_stars():
    for field in (
        "totals.agent_upvotes",
        "totals.agent_acquisitions",
        "agent_metrics",
        "leaderboards.most_upvoted",
        "leaderboards.most_acquired",
        "agent_upvotes",
        "usage_events",
    ):
        assert field in HTML

    text = visible_text().lower()
    assert "agent_upvotes separately from usage_events" in text
    assert "agent_acquisitions" in HTML
    assert "repo.stars" in HTML
    assert "never counted as an agent upvote" in text
    for forbidden in (
        "repo.upvotes",
        "repository-level community upvotes",
        "upvotes are repository stars",
        "public github stars",
    ):
        assert forbidden not in HTML.lower()


def test_no_token_literal_examples_or_secret_in_command_history_patterns():
    forbidden_patterns = (
        r"github_pat_",
        r"\bgh[pousr]_[A-Za-z0-9]",
        r"METRICS_TOKEN\s*=\s*[\"'][^\"']+",
        r"gh secret set[^\n<]*--body",
        r"(?:echo|printf)[^\n<]*\|\s*gh secret set",
        r"Authorization:\s*(?:token|Bearer)\s+\S+",
    )
    for pattern in forbidden_patterns:
        assert not re.search(pattern, HTML, re.IGNORECASE), pattern


def test_completion_persists_only_boolean_values_under_required_key():
    assert '"aibast:metrics-admin-checklist"' in HTML
    assert HTML.count("localStorage.setItem") == 1
    assert (
        "JSON.stringify(checklist.map((item) => Boolean(item.checked)))"
        in HTML
    )
    assert 'typeof value === "boolean"' in HTML
    assert "localStorage.removeItem(STORAGE_KEY)" in HTML
    assert "token" not in re.search(
        r"function persistChecklist\(\).*?\n}",
        HTML,
        re.DOTALL,
    ).group(0).lower()


def test_troubleshooting_expected_outcomes_and_go_live_gate_are_complete():
    text = visible_text()
    for phrase in (
        "Expected outcomes",
        "Troubleshooting",
        "401 Unauthorized",
        "403, SAML/SSO, or push-access error",
        "Workflow cannot push state/metrics.json",
        "Issue feedback metrics are missing",
        "Discussion counts are inflated, missing, or voter identities appear",
        "Zeros appear where data should be unavailable",
        "Final go-live checklist",
    ):
        assert phrase in text
    assert HTML.count('class="go-live-item"') == 6


def test_contextual_feedback_marker_schema_and_prefilled_issue_are_wired():
    assert "<!-- aibast-workshop-feedback:v1 -->" in HTML
    assert '"aibast-workshop-feedback/1.0"' in HTML
    assert "https://github.com/microsoft/aibast-agents-library/issues/new" in HTML
    assert 'issueUrl.searchParams.set("title", "[Metrics admin setup] Feedback")' in HTML
    assert 'issueUrl.searchParams.set(' in HTML
    assert "Page: docs/metrics-admin-setup.html" in HTML
    assert "Section: ${section}" in HTML
    assert "What needs correction or clarification?" in HTML
    assert "does not submit automatically" in visible_text()
    assert 'window.addEventListener("hashchange", updateReportIssueLinks)' in HTML


def test_forbidden_brand_terms_fonts_and_raw_document_links_are_absent():
    for forbidden in ("Beta", "Clawpilot", "Inter"):
        assert not re.search(rf"\b{re.escape(forbidden)}\b", HTML)

    assert "raw.githubusercontent.com" not in HTML
    assert not re.search(r"github\.com/[^\"']+/raw/", HTML)
    assert "?raw=1" not in HTML


def test_accessible_responsive_controls_and_copy_buttons_are_present():
    assert 'class="skip-link"' in HTML
    assert 'role="progressbar"' in HTML
    assert 'aria-live="polite"' in HTML
    assert ":focus-visible" in HTML
    assert "@media (max-width: 900px)" in HTML
    assert "@media (max-width: 600px)" in HTML
    assert "@media (prefers-reduced-motion: reduce)" in HTML
    assert HTML.count('data-copy-target="') >= 5
    assert "navigator.clipboard.writeText(text)" in HTML
