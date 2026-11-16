import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "solution.html").read_text(encoding="utf-8")
SKILL = "https://microsoft.github.io/aibast-agents-library/skills/aibast-meeting-prep/SKILL.md"


def test_solution_page_offers_the_meeting_prep_line():
    assert 'id="prepare-meeting"' in PAGE
    assert "Prepare a meeting with this" in PAGE
    # The line names the site that serves the page (staging or production), with production as the fallback.
    assert "const PREP_SKILL_PATH = 'skills/aibast-meeting-prep/SKILL.md';" in PAGE
    assert "new URL(PREP_SKILL_PATH, location.href.split(/[?#]/)[0]).href" in PAGE
    assert "'https://microsoft.github.io/aibast-agents-library/' + PREP_SKILL_PATH" in PAGE
    assert SKILL == "https://microsoft.github.io/aibast-agents-library/" + "skills/aibast-meeting-prep/SKILL.md"
    assert "Get ${PREP_SKILL} and do it. Use the ${LIB_NAME || sol.advertised_display || sol.advertised_name} example." in PAGE
    assert "LIB_NAME = rec?.name" in PAGE
    assert (ROOT / "skills" / "aibast-meeting-prep" / "SKILL.md").is_file()
    assert "kody-w" not in re.search(r"function prepLine[\s\S]*?\n}\n", PAGE).group(0)


def test_every_library_solution_page_names_its_own_example():
    listing = json.loads((ROOT / "api" / "v1" / "search.json").read_text(encoding="utf-8"))["solutions"]
    assert len(listing) == 72
    for row in listing:
        record = json.loads((ROOT / "api" / "v1" / "solutions" / (row["slug"] + ".json")).read_text(encoding="utf-8"))
        assert record["name"] == row["name"], row["slug"]
