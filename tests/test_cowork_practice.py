"""The Cowork walk-through on start.html: its own steps, no code editor, and the real download link."""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("first_minute_check", ROOT / "tools/first_minute_check.py")
judge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(judge)
SLUG = "account-intelligence"
RELEASE = "https://github.com/{owner}/aibast-agents-library/releases/download/solution-bundles/{slug}-cowork-plugin.zip"


@pytest.fixture
def stage_page():
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith(base) else route.abort("blockedbyclient"))
            yield page, base
        finally:
            browser.close()


def test_download_link_names_the_owner_serving_the_library():
    script = (ROOT / "solutions/_shared/solution-journey.js").read_text(encoding="utf-8")
    hosts = ["microsoft.github.io", "example-owner.github.io", "localhost", "127.0.0.1", "example.com"]
    probe = ("globalThis.window = {};\n" + script +
             f"\nconsole.log(JSON.stringify({json.dumps(hosts)}.map(host => "
             f"window.AibastJourney.coworkPluginUrl({json.dumps(SLUG)}, host))));")
    result = subprocess.run(["node"], input=probe, text=True, capture_output=True, check=True)
    owners = ["microsoft", "example-owner", "microsoft", "microsoft", "microsoft"]
    assert json.loads(result.stdout) == [RELEASE.format(owner=owner, slug=SLUG) for owner in owners]


def test_cowork_guide_is_plain_and_separate_from_the_setup_line():
    page = BeautifulSoup((ROOT / "start.html").read_text(encoding="utf-8"), "html.parser")
    guide = page.select_one("#cowork-guide")
    assert [item.h2.get_text() for item in guide.select("ol > li")] == [
        "Download the plugin.", "Upload it to Cowork.", "Publish for yourself.", "Ask your first question.",
    ]
    assert guide.select_one("a#cowork-download-link").get_text() == "Download Cowork plugin"
    assert "Customize, then Manage all, then Add, then Upload" in guide.get_text()
    assert "Keep Only you selected and choose Publish" in guide.get_text()
    for word in ("Visual Studio Code", "VS Code", "GitHub Copilot", "setup line"):
        assert word not in guide.get_text()
    assert not guide.select("pre, code, details, [data-step]")
    switch = page.select_one("#path-switch-link")
    assert switch["href"] == "start.html?surface=cowork"
    assert switch.get_text() == "Put this agent into your Cowork."


def test_cowork_path_walks_four_steps_with_no_code_editor(stage_page):
    page, base = stage_page
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    judge.load(page, base + f"start.html?solution={SLUG}&surface=cowork")
    assert page.locator("h1").inner_text() == "Put this agent into your Cowork"
    assert page.locator(".lede").inner_text() == (
        "This is a pretend computer with sample data, never connected to your organization's data.")
    assert page.locator("#practice-computer").get_attribute("data-journey") == "cowork"
    assert page.locator("#c-n").inner_text() == "Step 1 of 4"
    assert page.locator("#c-prog h3").all_text_contents() == ["Add it to your Cowork"]
    assert page.locator("#c-prog section > div").all_text_contents() == [
        "1. Download the plugin", "2. Upload it to Cowork", "3. Publish for yourself", "4. Ask your first question",
    ]
    assert not page.locator("#your-path").count()
    assert not page.locator(".vsc").count()
    assert "Visual Studio Code" not in page.locator("#pc").evaluate("e => e.textContent")
    text = page.locator("body").inner_text()
    assert "Visual Studio Code" not in text and "GitHub Copilot" not in text
    assert page.locator("#cowork-guide").is_visible()
    assert not page.locator("#setup-line").is_visible()
    assert not page.locator("[data-what-you-need]").is_visible()
    assert page.locator("#cowork-download-link").get_attribute("href") == RELEASE.format(owner="microsoft", slug=SLUG)
    assert page.locator("#path-switch-link").get_attribute("href") == f"start.html?solution={SLUG}"
    for name in ("Watch", "Step by step", "Unmute", "Show me where", "Start over"):
        assert page.get_by_role("button", name=name, exact=True).is_visible()
    assert page.get_by_role("link", name="Get help", exact=True).is_visible()

    page.get_by_role("button", name="Step by step", exact=True).click()
    page.evaluate("""() => { window.__targets = []; new MutationObserver(() => {
        const t = document.querySelector('#hint').dataset.target;
        if (t && window.__targets.at(-1) !== t) window.__targets.push(t);
    }).observe(document.querySelector('#hint'), {attributes:true}); }""")
    assert judge.highlighted_clickthrough(page) == [1, 2, 3, 4]
    targets = page.evaluate("window.__targets")
    assert [t for t in targets if t != "#cowork-download"] == [
        "#cowork-customize", "#cowork-manage", "#cowork-add", "#cowork-upload", "#cowork-file",
        "#cowork-publish", "#cowork-new-task", "#cowork-send",
    ]
    assert page.locator("#c-n").inner_text() == "Done"
    samples = json.loads((ROOT / f"solutions/{SLUG}/evals/transcripts.json").read_text())["transcripts"]
    assert page.locator("#cowork-question").inner_text() == samples[0]["prompt"]
    assert page.locator("#cowork-sample-question").inner_text() == samples[0]["prompt"]
    assert page.locator("#cowork-skill").inner_text() == (
        "Reviewed custom skill " + page.locator("#solution option:checked").inner_text())
    assert judge.studio_answer_words(page.locator("#cowork-answer").inner_text()) == (
        judge.studio_answer_words(samples[0]["assistant_response"] + "\n\nSample data."))
    assert "Visual Studio Code" not in page.locator("body").inner_text()
    assert not errors


def test_cowork_publish_keeps_only_you_and_lists_the_plugin(stage_page):
    page, base = stage_page
    judge.load(page, base + f"start.html?solution={SLUG}&surface=cowork&step=3")
    assert page.locator("#c-n").inner_text() == "Step 3 of 4"
    assert page.locator('.cowork-who [aria-checked="true"]').all_text_contents() == ["Only you"]
    assert not page.locator("#cowork-plugin").count()
    page.locator("#cowork-publish").click()
    page.wait_for_function("document.querySelector('#c-n').textContent === 'Step 4 of 4'")
    assert page.locator("#cowork-plugin strong").inner_text() == page.locator("#solution option:checked").inner_text()
    assert page.locator("#cowork-plugin span").inner_text() == "Published · Only you"


def test_default_path_is_still_the_copilot_studio_setup(stage_page):
    page, base = stage_page
    judge.load(page, base + f"start.html?solution={SLUG}")
    assert page.locator("h1").inner_text() == "Get an agent into Copilot Studio"
    assert page.title() == "Get an agent running - AI BAST Agent Library"
    assert page.locator("#practice-computer").get_attribute("data-journey") == "express"
    assert page.locator("#c-prog section > div").all_text_contents() == [
        "1. Open Copilot chat", "2. Send the setup line", "3. Review and agree", "4. Test your agent",
    ]
    assert page.locator("#c-say").inner_text() == (
        "Open GitHub Copilot chat in Visual Studio Code. This is where you ask it to set up your agent.")
    assert page.locator(".vsc").count() == 1 and not page.locator(".sample-cowork").count()
    assert not page.locator("#cowork-guide").is_visible()
    assert page.locator("#setup-line").is_visible()
    assert page.locator("[data-what-you-need]").is_visible()
    assert page.locator(".journey-link").is_visible()
    assert page.locator("#path-switch-link").get_attribute("href") == f"start.html?solution={SLUG}&surface=cowork"
    assert page.locator("#path-switch-link").inner_text() == "Put this agent into your Cowork."
