import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "audit_rapp_guide.py"


def load_audit():
    spec = importlib.util.spec_from_file_location("audit_rapp_guide", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_audit()


def render_variables(variables):
    return "\n".join(
        f"  {name}: {value};" for name, value in variables.items()
    )


def valid_fixture():
    section_ids = list(AUDIT.CONTENT_SECTION_IDS)
    scout_script = """
<script>
(() => {
  const param = new URLSearchParams(window.location.search).get("scoutTheme");
  const theme =
    param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
})();
</script>
"""
    styles = f"""
<style>
:root {{
  color-scheme: light;
{render_variables(AUDIT.LIGHT_THEME_VARIABLES)}
}}
html[data-theme="dark"] {{
  color-scheme: dark;
{render_variables(AUDIT.DARK_THEME_VARIABLES)}
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--cp-bg);
  color: var(--cp-text);
  font-family: "Segoe UI", Aptos, Calibri, sans-serif;
}}
code, pre {{
  font-family: Consolas, "Courier New", monospace;
  background: var(--cp-surface-soft);
  color: var(--cp-text);
}}
a {{ color: var(--cp-link); }}
.skip-link {{ position: absolute; background: var(--cp-surface); }}
.topbar {{
  display: flex;
  background: var(--cp-panel-strong);
  border-bottom: 1px solid var(--cp-border);
}}
.layout {{ display: grid; }}
.sidebar {{ background: var(--cp-surface); border: 1px solid var(--cp-border); }}
.progress {{ background: var(--cp-border); }}
.progress-fill {{ background: var(--cp-accent); }}
table {{ background: var(--cp-surface); border: 1px solid var(--cp-border); }}
.card {{ background: var(--cp-surface); border: 1px solid var(--cp-border); }}
.quiz {{ background: var(--cp-surface-soft); border: 1px solid var(--cp-border); }}
button:focus-visible, a:focus-visible {{
  outline: 3px solid var(--cp-highlight);
  outline-offset: 2px;
}}
body:not(.js-enabled) #sidebar {{
  position: static;
  width: auto;
  height: auto;
  transform: none;
}}
body:not(.js-enabled) .content-section {{ display: block; }}
body:not(.js-enabled) .fallback-content[hidden] {{
  display: block !important;
}}
body:not(.js-enabled) .js-control,
body:not(.js-enabled) .nav-controls,
body:not(.js-enabled) .copy-btn,
body:not(.js-enabled) .fallback-header,
body:not(.js-enabled) .gut-check-toggle,
body:not(.js-enabled) .quiz-submit,
body:not(.js-enabled) .sidebar-close,
body:not(.js-enabled) .sidebar-scrim {{
  display: none;
}}
@media (max-width: 800px) {{
  .layout {{ display: block; }}
  .sidebar {{ width: 100%; transform: translateX(-105%); }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    scroll-behavior: auto;
    transition-duration: 0s;
    animation-duration: 0s;
  }}
}}
</style>
"""
    sidebar_links = "\n".join(
        f'<a href="#{section_id}">Link {section_id}</a>'
        for section_id in section_ids
    )
    sections = "\n".join(
        (
            f'<section class="content-section" id="{section_id}">'
            f"<h2>{section_id}</h2><p>Preserved {section_id}</p></section>"
        )
        for section_id in section_ids
    )
    section_array = json.dumps(section_ids)
    behavior_script = f"""
<script>
const sections = {section_array};
let currentSectionIndex = 0;
const feedbackSchema = "aibast-workshop-feedback/1.0";
const feedbackBody = "<!-- aibast-workshop-feedback:v1 -->";
function announceStatus(message) {{
  document.getElementById("liveStatus").textContent = message;
}}
function updateReportIssueLink(sectionId = sections[currentSectionIndex]) {{
  const reportLink = document.getElementById("reportIssue");
  const issueUrl = new URL("https://github.com/microsoft/aibast-agents-library/issues/new");
  issueUrl.searchParams.set(
    "body",
    `${{feedbackBody}}\\nFeedback schema: ${{feedbackSchema}}\\nSection: ${{sectionId}}`
  );
  reportLink.href = issueUrl.toString();
}}
function closeMobileSidebar() {{
  document.body.classList.remove("sidebar-open");
  setMobileBackgroundInert(false);
}}
function setMobileBackgroundInert(inert) {{
  const main = document.getElementById("mainContent");
  if (main) main.inert = inert;
}}
function navigateToSection(sectionId, {{ historyMode = "push" }} = {{}}) {{
  currentSectionIndex = sections.indexOf(sectionId);
  if (historyMode === "push") history.pushState(null, "", `#${{sectionId}}`);
  window.location.hash = sectionId;
  updateReportIssueLink(sectionId);
}}
function nextSection() {{
  if (currentSectionIndex < sections.length - 1) {{
    navigateToSection(sections[currentSectionIndex + 1]);
  }}
}}
function previousSection() {{
  if (currentSectionIndex > 0) {{
    navigateToSection(sections[currentSectionIndex - 1]);
  }}
}}
function updateProgress() {{
  const progress = ((currentSectionIndex + 1) / sections.length) * 100;
  document.querySelectorAll(".progress-fill").forEach(fill => {{
    fill.style.width = `${{progress}}%`;
  }});
  document.querySelectorAll('[role="progressbar"]').forEach(bar => {{
    bar.setAttribute("aria-valuenow", String(Math.round(progress)));
  }});
}}
function toggleSidebar() {{
  const shouldOpen = !document.body.classList.contains("sidebar-open");
  document.body.classList.toggle("sidebar-open", shouldOpen);
  setMobileBackgroundInert(shouldOpen);
}}
function syncSidebarForViewport() {{
  setMobileBackgroundInert(false);
  return window.matchMedia("(max-width: 800px)").matches;
}}
function fallbackCopy(text) {{
  document.body.dataset.fallbackCopy = text;
}}
async function copyCode(codeBlock) {{
  const payload = codeBlock.textContent;
  if (navigator.clipboard && window.isSecureContext) {{
    await navigator.clipboard.writeText(payload);
  }} else {{
    fallbackCopy(payload);
  }}
  announceStatus("Copied to clipboard.");
}}
function toggleFallback(fallbackId) {{
  const fallbackElement = document.getElementById(fallbackId);
  const toggle = document.querySelector(
    `[data-fallback-toggle][aria-controls="${{fallbackId}}"]`
  );
  const expanded = fallbackElement.hidden;
  fallbackElement.hidden = !expanded;
  toggle.setAttribute("aria-expanded", String(expanded));
  toggle.textContent = toggle.textContent.replace(
    expanded ? "Click to expand" : "Click to collapse",
    expanded ? "Click to collapse" : "Click to expand"
  );
}}
function toggleQuiz(id) {{
  document.getElementById(id).classList.toggle("open");
}}
function selectQuizOption(id, index) {{
  document.getElementById(id).dataset.answer = index;
}}
function saveQuizCompletion(completed) {{
  localStorage.setItem("quiz-completed", JSON.stringify(completed));
}}
function submitQuiz(quizId, correctAnswer) {{
  const quiz = document.getElementById(quizId);
  const options = quiz.querySelectorAll(".quiz-option");
  const selectedInput = quiz.querySelector(
    '.quiz-option input[type="radio"]:checked'
  );
  if (!selectedInput) return;
  const selectedIndex = Number(selectedInput.value);
  const isCorrect = selectedIndex === correctAnswer;
  options.forEach((option, index) => {{
    option.classList.remove("correct", "incorrect");
    if (index === correctAnswer) option.classList.add("correct");
    if (index === selectedIndex && !isCorrect) {{
      option.classList.add("incorrect");
    }}
  }});
  if (isCorrect) {{
    const completed = {{}};
    completed[quizId] = true;
    saveQuizCompletion(completed);
  }}
}}
function scrollToSection(id) {{
  document.getElementById(id).scrollIntoView();
}}
function initializeQuizzes() {{
  return localStorage.getItem("quiz-completed");
}}
function handleHashNavigation() {{
  const hash = window.location.hash.slice(1);
  if (hash === "mainContent") {{
    document.getElementById("mainContent")?.focus();
    return;
  }}
  navigateToSection(hash || "overview", {{historyMode: "none"}});
}}
function toggleTheme() {{
  document.documentElement.setAttribute(
    "data-theme",
    document.documentElement.dataset.theme === "dark" ? "light" : "dark"
  );
}}
document.addEventListener("keydown", (event) => {{
  if (event.key === "Escape") {{
    if (document.body.classList.contains("sidebar-open")) {{
      closeMobileSidebar();
    }}
    return;
  }}
  if (event.key === "Tab" && document.body.classList.contains("sidebar-open")) {{
    event.preventDefault();
    document.getElementById("sidebar").focus();
    return;
  }}
  if (event.target.closest('.table-wrap, [role="region"]')) return;
  if (event.key === "ArrowRight") nextSection();
  if (event.key === "ArrowLeft") previousSection();
}});
window.addEventListener("hashchange", handleHashNavigation);
window.addEventListener("popstate", handleHashNavigation);
</script>
"""
    return f"""<!doctype html>
<html lang="en">
<head>
{scout_script}
<meta charset="utf-8">
<title>AIBAST RAPP Production Guide</title>
{styles}
</head>
<body>
<a class="skip-link" href="#mainContent">Skip to content</a>
<header class="topbar">
  <strong>AIBAST Production Guide</strong>
  <a href="../library.html">Library</a>
  <a href="../solutions/_shared/workshop-settings.html">Workshop settings</a>
  <a class="report-control" id="reportIssue"
     aria-label="Report an issue"
     href="https://github.com/microsoft/aibast-agents-library/issues/new?template=workshop.md">Report an issue</a>
  <button class="js-control" id="theme-toggle" aria-label="Toggle theme" onclick="toggleTheme()">Theme toggle</button>
  <button class="js-control" data-sidebar-toggle aria-label="Toggle sidebar" aria-controls="sidebar"
          onclick="toggleSidebar()">Menu</button>
</header>
<noscript>JavaScript is disabled. All 21 sections are visible below.</noscript>
<div class="layout">
  <aside class="sidebar" id="sidebar" aria-label="Production Guide sections">
    <nav aria-label="Guide navigation">{sidebar_links}</nav>
  </aside>
  <main id="mainContent" tabindex="-1">
    <div class="progress" role="progressbar" aria-valuenow="0"
         aria-valuemin="0" aria-valuemax="100">
      <div class="progress-fill"></div>
    </div>
    <div class="nav-controls global-nav-controls">
      <button onclick="previousSection()">Previous</button>
      <button onclick="nextSection()">Next</button>
    </div>
    {sections}
    <article class="card">Workshop card</article>
    <table><tr><th>Gate</th></tr><tr><td>Pass</td></tr></table>
    <div class="code-block">
      <button class="copy-btn" data-copy-button
              onclick="copyCode(document.getElementById('code-one'))">Copy</button>
      <pre id="code-one"><code>echo pass</code></pre>
    </div>
    <div class="code-block">
      <button class="copy-btn" data-copy-button
              onclick="copyCode(document.getElementById('code-two'))">Copy</button>
      <pre id="code-two"><code>echo second</code></pre>
    </div>
    <div class="fallback-header">
      <button data-fallback-toggle aria-controls="fallback"
              aria-expanded="false" onclick="toggleFallback('fallback')">
        Fallback — Click to expand
      </button>
    </div>
    <pre class="fallback-content" id="fallback" hidden>Fallback prompt</pre>
    <div class="quiz gut-check" id="quiz-principles">
      <button class="gut-check-toggle" data-quiz-toggle
              onclick="toggleQuiz('quiz-principles')">Take quiz</button>
      <label class="quiz-option"><input type="radio" value="0">First answer</label>
      <label class="quiz-option"><input type="radio" value="1">Correct answer</label>
      <label class="quiz-option"><input type="radio" value="2">Third answer</label>
      <label class="quiz-option"><input type="radio" value="3">Fourth answer</label>
      <button class="quiz-submit" data-correct="Correct feedback"
              data-incorrect="Incorrect feedback"
              data-review-section="principles"
              onclick="submitQuiz('quiz-principles', 1)">Submit</button>
      <div class="quiz-feedback"></div>
    </div>
    <div id="liveStatus" role="status" aria-live="polite"></div>
  </main>
</div>
<!-- aibast-workshop-feedback:v1 -->
{behavior_script}
</body>
</html>
"""


def fixture_contract(text):
    return AUDIT.build_content_contract_from_text(text, "fixture.html")


def run_audit(text, contract=None):
    assert shutil.which("node"), "node is required by the fail-closed gate"
    return AUDIT.audit_text(
        text,
        contract or fixture_contract(valid_fixture()),
        guide_label="fixture.html",
        contract_label="fixture-contract.json",
        baseline_text=valid_fixture(),
    )


def categories(report):
    return set(report["failure_categories"])


def test_minimal_valid_fixture_passes():
    text = valid_fixture()
    report = run_audit(text, fixture_contract(text))
    assert report["ok"], report["failures"]
    assert json.loads(json.dumps(report))["schema"] == AUDIT.AUDIT_SCHEMA
    assert AUDIT._human_output(report).startswith("PASS:")


def test_real_guide_contract_is_reconstructed_from_trusted_git_blob():
    report = AUDIT.audit_paths(
        ROOT / "docs" / "rapp-guide.html",
        ROOT / "state" / "rapp_guide_content_contract.json",
    )
    assert report["ok"], report["failures"]


def test_gate_fails_closed_without_verified_baseline():
    text = valid_fixture()
    report = AUDIT.audit_text(text, fixture_contract(text))
    assert "baseline.source" in categories(report)


def test_joint_guide_contract_and_metadata_corruption_cannot_bypass_baseline():
    original = valid_fixture()
    changed = original.replace(
        "Preserved overview", "Jointly corrupted overview", 1
    )
    changed_contract = fixture_contract(changed)
    changed_contract["trusted_source_commit"] = "0" * 40
    changed_contract["trusted_source_blob_oid"] = "1" * 40
    report_categories = categories(run_audit(changed, changed_contract))
    assert "baseline.metadata" in report_categories
    assert "baseline.contract" in report_categories


def test_gate_catches_quiz_correct_index_mutation():
    original = valid_fixture()
    changed = original.replace(
        "submitQuiz('quiz-principles', 1)",
        "submitQuiz('quiz-principles', 2)",
        1,
    )
    assert "behavior.quiz" in categories(run_audit(changed))


def test_gate_catches_quiz_feedback_mutation():
    original = valid_fixture()
    changed = original.replace(
        'data-incorrect="Incorrect feedback"',
        'data-incorrect="Altered feedback"',
        1,
    )
    assert "behavior.quiz" in categories(run_audit(changed))


def test_gate_catches_copy_button_retargeted_to_another_block():
    original = valid_fixture()
    changed = original.replace(
        "copyCode(document.getElementById('code-one'))",
        "copyCode(document.getElementById('code-two'))",
        1,
    )
    assert "behavior.copy" in categories(run_audit(changed))


def test_gate_catches_copy_payload_replaced_with_empty_string():
    original = valid_fixture()
    changed = original.replace(
        "const payload = codeBlock.textContent;",
        'const payload = "";',
        1,
    )
    assert "behavior.copy" in categories(run_audit(changed))


def test_gate_catches_fallback_toggle_retargeted_to_another_block():
    original = valid_fixture()
    changed = original.replace(
        'aria-controls="fallback"',
        'aria-controls="code-two"',
        1,
    )
    assert "behavior.fallback" in categories(run_audit(changed))


def test_gate_catches_fallback_hidden_state_no_op():
    original = valid_fixture()
    changed = original.replace(
        "fallbackElement.hidden = !expanded;",
        "fallbackElement.hidden = fallbackElement.hidden;",
        1,
    )
    assert "behavior.fallback" in categories(run_audit(changed))


def test_gate_catches_quiz_correctness_inversion():
    original = valid_fixture()
    changed = original.replace(
        "const isCorrect = selectedIndex === correctAnswer;",
        "const isCorrect = selectedIndex !== correctAnswer;",
        1,
    )
    assert "behavior.quiz" in categories(run_audit(changed))


def test_gate_catches_disabled_mobile_background_inerting():
    original = valid_fixture()
    changed = original.replace(
        "if (main) main.inert = inert;",
        "if (main) main.inert = false;",
        1,
    )
    assert "behavior.mobile_drawer" in categories(run_audit(changed))


def test_gate_catches_feedback_context_hardcoded_to_overview():
    original = valid_fixture()
    changed = original.replace(
        "sectionId = sections[currentSectionIndex]",
        'sectionId = "overview"',
        1,
    )
    assert "theme.feedback" in categories(run_audit(changed))


def test_gate_catches_tools_made_unreachable_by_next_bound():
    original = valid_fixture()
    changed = original.replace(
        "currentSectionIndex < sections.length - 1",
        "currentSectionIndex < sections.length - 2",
        1,
    )
    assert "behavior.previous_next" in categories(run_audit(changed))


@pytest.mark.parametrize(
    ("old", "new"),
    (
        (
            'fill.style.width = `${progress}%`;',
            'fill.style.height = `${progress}%`;',
        ),
        (
            'bar.setAttribute("aria-valuenow", String(Math.round(progress)));',
            'bar.setAttribute("aria-valuetext", String(Math.round(progress)));',
        ),
    ),
)
def test_gate_catches_progress_accessibility_mutations(old, new):
    original = valid_fixture()
    assert old in original
    changed = original.replace(old, new, 1)
    assert "behavior.progress" in categories(run_audit(changed))


def test_gate_catches_sidebar_order_mutation():
    original = valid_fixture()
    first = '<a href="#step5">Link step5</a>'
    second = '<a href="#step6">Link step6</a>'
    changed = original.replace(first, "__FIRST__", 1)
    changed = changed.replace(second, first, 1).replace("__FIRST__", second, 1)
    assert "content.sidebar" in categories(run_audit(changed))


def test_gate_catches_added_content_section_external_url():
    original = valid_fixture()
    changed = original.replace(
        "Preserved overview</p>",
        'Preserved overview <a href="https://example.invalid/new">new</a></p>',
        1,
    )
    assert "content.external_links" in categories(run_audit(changed))


def test_gate_catches_no_js_offscreen_sidebar_mutation():
    original = valid_fixture()
    changed = original.replace(
        "body:not(.js-enabled) #sidebar {\n"
        "  position: static;\n"
        "  width: auto;\n"
        "  height: auto;\n"
        "  transform: none;",
        "body:not(.js-enabled) #sidebar {\n"
        "  position: static;\n"
        "  width: auto;\n"
        "  height: auto;\n"
        "  transform: translateX(-105%);",
        1,
    )
    assert "behavior.no_js" in categories(run_audit(changed))


def test_gate_catches_contradictory_no_js_content_rule():
    original = valid_fixture()
    changed = original.replace(
        "</style>",
        "body:not(.js-enabled) #overview { display: none; }\n</style>",
        1,
    )
    assert "behavior.no_js" in categories(run_audit(changed))


def test_gate_rejects_unallowlisted_shell_link():
    original = valid_fixture()
    changed = original.replace(
        "</header>",
        '<a href="https://example.invalid/shell">Unexpected</a></header>',
        1,
    )
    assert "content.shell_links" in categories(run_audit(changed))


@pytest.mark.parametrize(
    ("old", "new", "category"),
    (
        (
            'if (hash === "mainContent")',
            'if (hash === "not-main-content")',
            "behavior.skip_link",
        ),
        (
            "history.pushState(null, \"\", `#${sectionId}`)",
            "history.replaceState(null, \"\", `#${sectionId}`)",
            "behavior.history",
        ),
        (
            'window.addEventListener("popstate", handleHashNavigation)',
            'window.addEventListener("pageshow", handleHashNavigation)',
            "behavior.history",
        ),
        (
            "setMobileBackgroundInert(shouldOpen);",
            "setMobileBackgroundInert(false);",
            "behavior.mobile_drawer",
        ),
        (
            'if (document.body.classList.contains("sidebar-open")) {\n'
            "      closeMobileSidebar();",
            "if (true) {\n      closeMobileSidebar();",
            "behavior.mobile_drawer",
        ),
        (
            "'.table-wrap, [role=\"region\"]'",
            "'.table-wrap'",
            "behavior.keyboard",
        ),
    ),
)
def test_gate_catches_post_migration_interaction_mutations(
    old, new, category
):
    original = valid_fixture()
    assert old in original
    changed = original.replace(old, new, 1)
    assert category in categories(run_audit(changed))


def test_gate_catches_content_section_text_drift():
    original = valid_fixture()
    changed = original.replace(
        "Preserved overview", "Preserved overview with drift", 1
    )
    assert "content.text" in categories(run_audit(changed))


def test_gate_catches_missing_section():
    original = valid_fixture()
    changed = original.replace(
        '<section class="content-section" id="step7">'
        "<h2>step7</h2><p>Preserved step7</p></section>",
        "",
        1,
    )
    report_categories = categories(run_audit(changed))
    assert "content.sections" in report_categories
    assert "content.steps" in report_categories


def test_gate_catches_missing_sidebar_deep_link():
    original = valid_fixture()
    changed = original.replace(
        '<a href="#step6">Link step6</a>', "", 1
    )
    assert "content.sidebar" in categories(run_audit(changed))


def test_gate_catches_missing_interactive_function():
    original = valid_fixture()
    changed = original.replace(
        "async function copyCode(codeBlock)",
        "async function removedCopyCode(codeBlock)",
        1,
    )
    assert "behavior.functions" in categories(run_audit(changed))


def test_gate_catches_malformed_inline_javascript():
    original = valid_fixture()
    changed = original.replace(
        "</body>", "<script>function malformed( {</script></body>", 1
    )
    assert "behavior.javascript" in categories(run_audit(changed))


def test_gate_catches_google_fonts_and_inter():
    original = valid_fixture()
    changed = original.replace(
        "</style>",
        '@import url("https://fonts.googleapis.com/css2?family=Inter");\n'
        ".legacy-font { font-family: Inter, sans-serif; }\n</style>",
        1,
    )
    assert "theme.forbidden" in categories(run_audit(changed))


def test_gate_catches_missing_dark_theme_token():
    original = valid_fixture()
    changed = original.replace("  --cp-link: #4da6ff;\n", "", 1)
    assert "theme.tokens" in categories(run_audit(changed))


def test_gate_catches_hardcoded_component_color():
    original = valid_fixture()
    changed = original.replace(
        ".card { background: var(--cp-surface);",
        ".card { background: #123456;",
        1,
    )
    assert "theme.colors" in categories(run_audit(changed))


def test_gate_fails_closed_on_unparseable_css():
    original = valid_fixture()
    changed = original.replace(
        ".card { background: var(--cp-surface);",
        ".card { background var(--cp-surface);",
        1,
    )
    assert "css.parse" in categories(run_audit(changed))


def test_gate_catches_missing_contextual_feedback():
    original = valid_fixture()
    changed = original.replace(
        "<!-- aibast-workshop-feedback:v1 -->", ""
    )
    assert "theme.feedback" in categories(run_audit(changed))


def test_gate_catches_feedback_issue_body_without_marker():
    original = valid_fixture()
    changed = original.replace(
        'const feedbackBody = "<!-- aibast-workshop-feedback:v1 -->";',
        'const feedbackBody = "Workshop feedback";',
    )
    assert "theme.feedback" in categories(run_audit(changed))


def test_gate_catches_wrong_noscript_section_count():
    original = valid_fixture()
    changed = original.replace("All 21 sections", "All 19 sections", 1)
    assert "behavior.noscript" in categories(run_audit(changed))


@pytest.mark.parametrize(
    "insertion",
    (
        '<div class="track-selector">Legacy tracks</div>',
        "<script>function setTrack(track) { return track; }</script>",
        "<script>localStorage.removeItem('framework-track');</script>",
    ),
)
def test_gate_catches_dead_track_selector_leftovers(insertion):
    original = valid_fixture()
    changed = original.replace("</main>", f"{insertion}</main>", 1)
    assert "theme.dead_track" in categories(run_audit(changed))


def test_cli_argument_contract_supports_json_and_optional_paths():
    args = AUDIT.parse_args(
        [
            "--json",
            "--guide",
            "custom-guide.html",
            "--contract",
            "custom-contract.json",
        ]
    )
    assert args.json is True
    assert args.guide == Path("custom-guide.html")
    assert args.contract == Path("custom-contract.json")
