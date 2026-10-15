import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "solution.html", "metrics.html")


def test_pages_read_their_data_same_origin_without_cache_busting():
    for name in PAGES:
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "cache: 'no-store'" not in text and 'cache: "no-store"' not in text, name
        assert "Date.now()}" not in text and "'?t=' + Date.now()" not in text, name
        assert "api.github.com/repos/${OWNER}" not in text, name


def test_solution_page_has_no_leftover_stamp_variable():
    # solution.html once lost its ?t= stamp but kept a use of it, which broke the page.
    text = (ROOT / "solution.html").read_text(encoding="utf-8")
    assert not re.search(r"\+ t\b(?!\w)", text), "solution.html still appends the removed stamp variable"


def test_solution_page_keeps_reading_sample_output_from_raw():
    # samples/ is not published on Pages; dropping the raw source hid every solution's sample output.
    text = (ROOT / "solution.html").read_text(encoding="utf-8")
    assert "getJSON([RAW + '/' + sol.sample_output])" in text
