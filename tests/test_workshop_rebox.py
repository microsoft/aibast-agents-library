"""The workshop annotator's match-preference rule (tools/workshop_reshoot/rebox.py), on fake OCR words."""
import pytest

from tools.workshop_reshoot import rebox as R


def _line(y, *spec):
    """spec: (x, text) pairs; each word is 8 px per character wide, 16 px tall."""
    return [{"x": x, "y": y, "w": 8 * len(t), "h": 16, "t": t} for x, t in spec]


@pytest.fixture
def ocr(monkeypatch):
    def use(ws):
        frozen = tuple(tuple(sorted(w.items())) for w in ws)
        monkeypatch.setattr(R, "words", lambda image: frozen)
    return use


def test_exact_full_phrase_beats_a_prefix_in_prose(ocr):
    ocr(_line(300, (100, "I've"), (138, "drafted"), (198, "the"), (230, "escalation"), (314, "for"))
        + _line(340, (100, "Escalation"), (184, "Draft:"), (236, "HB-2041")))
    best = R.find("x.png", "Escalation Draft", ranked=True)[0]
    assert (best["y"], best["exact"]) == (340, True)


def test_words_must_be_consecutive(ocr):
    ocr(_line(300, (100, "Tier"), (140, "1"), (152, "to"), (172, "Tier"), (212, "2")))
    hits = R.find("x.png", "Tier 2", ranked=True)
    assert hits[0]["x"] == 172 and hits[0]["exact"]
    assert all(h["width"] < 60 for h in hits)


def test_a_table_cell_beats_the_same_words_in_prose(ocr):
    ocr(_line(200, (100, "send"), (140, "to"), (160, "Substation"), (244, "Crew"), (280, "B"), (292, "today"))
        + _line(400, (100, "Substation"), (184, "Crew"), (220, "B"), (400, "Tap")))
    best = R.find("x.png", "Substation Crew B", ranked=True)[0]
    assert best["y"] == 400 and best["structure"] == 2


def test_close_number_is_not_an_exact_match(ocr):
    ocr(_line(200, (100, "opens"), (150, "10:00")) + _line(240, (100, "issue"), (150, "10:30")))
    best = R.find("x.png", "10:30", ranked=True)[0]
    assert best["y"] == 240 and best["exact"]


def test_several_ids_are_boxed_one_each(ocr, tmp_path):
    from PIL import Image
    img = tmp_path / "17-thb-04.png"
    Image.new("RGB", (1424, 863), "white").save(img)
    ocr(_line(300, (100, "HB-2031"), (300, "Tier"), (340, "3")) + _line(340, (100, "HB-2027"), (300, "Executive")))
    boxes = R.rebox(img, ["HB-2027 and HB-2031"], kind="case")
    assert sorted(b["label"] for b in boxes) == ["HB-2027", "HB-2031"]
    assert len({(b["x"], b["y"]) for b in boxes}) == 2


def test_padding_never_covers_the_neighbouring_word(ocr, tmp_path):
    from PIL import Image
    img = tmp_path / "f.png"
    Image.new("RGB", (1424, 863), "white").save(img)
    ocr(_line(300, (100, "The"), (130, "daily"), (174, "Leadership"), (258, "Huddle"), (312, "has")))
    box = R.rebox(img, ["Leadership Huddle"], kind="case")[0]
    assert box["x"] > 130 + 8 * len("daily")


def test_legend_takes_the_screen_case_and_sign():
    assert R.screen_label("MISSING", {"text": "Missing"}) == "Missing"
    assert R.screen_label("9,846.90", {"text": "-9,846.90"}) == "-9,846.90"
    assert R.screen_label("Draft", {"text": "Drafts"}) == "Draft"


def test_a_time_pressed_against_the_phrase_goes_inside_the_box(ocr, tmp_path):
    from PIL import Image
    img = tmp_path / "f.png"
    Image.new("RGB", (1424, 863), "white").save(img)
    ocr(_line(300, (100, "The"), (130, "10:30"), (174, "Leadership"), (258, "Huddle"), (312, "has")))
    box = R.rebox(img, ["Leadership Huddle"], kind="case")[0]
    assert box["x"] < 130 and box["x"] + box["width"] < 312
    assert box["label"] == "Leadership Huddle"


def test_a_wrapped_heading_is_one_full_match(ocr):
    ocr(_line(280, (180, "Predictive"), (270, "Asset"), (320, "Manual"))
        + _line(300, (180, "Asset"), (230, "Maintenance"), (330, "Global"))
        + _line(322, (180, "Instructions"), (400, "You")))
    best = R.find("x.png", "Asset Maintenance Global Instructions", ranked=True)[0]
    assert best["exact"] and best["y"] == 300 and best["height"] == 322 + 16 - 300


def test_reading_order_does_not_matter(ocr):
    # tesseract can list a short word after the rest of its line; the em dash reads as its own token
    ocr(_line(282, (282, "Field"), (339, "Permit"), (444, "Work"), (508, "Agent"), (612, "Manual"))
        + _line(284, (415, "to")) + _line(290, (566, "—")))
    best = R.find("x.png", "Field Permit to Work Agent — Manual", ranked=True)[0]
    assert best["exact"] and best["width"] == 612 + 8 * 6 - 282


def test_a_label_and_its_value_span_one_row(ocr):
    ocr(_line(96, (1023, "Model"), (1260, "Claude"), (1310, "Opus"), (1350, "5.5")))
    best = R.find("x.png", "Model\nClaude Opus 5.5", ranked=True)[0]
    assert best["exact"] and best["x"] == 1023


def test_a_cell_whose_first_word_ocr_dropped_beats_a_lone_first_word(ocr, tmp_path):
    from PIL import Image
    img = tmp_path / "f.png"
    Image.new("RGB", (1424, 863), "white").save(img)
    ocr(_line(300, (296, "confirmed"), (376, "by"), (396, "the"), (424, "control"), (484, "room"), (700, "No"))
        + _line(500, (300, "1."), (320, "Isolation"), (400, "(control"), (470, "room)")))
    box = R.rebox(img, ["Isolation confirmed by the control room"], kind="case")[0]
    assert box["y"] < 300 and box["x"] < 296


def test_a_tail_inside_prose_is_not_a_truncated_chip(ocr):
    ocr(_line(80, (670, "when"), (700, "someone"), (750, "asks"), (782, "about"), (820, "settlement"), (900, "or"))
        + _line(160, (672, "settlement"), (900, "x")))
    hits = R.find("x.png", "reconcile-settlement", ranked=True)
    assert [h["y"] for h in hits] == [160]


def test_a_phrase_that_wraps_mid_paragraph(ocr):
    ocr(_line(300, (288, "After"), (330, "the"), (360, "call,"), (400, "the"), (430, "payments"))
        + _line(326, (288, "analyst"), (350, "decides"), (420, "whether"))
        + _line(400, (288, "the"), (320, "payment"), (390, "instruction.")))
    best = R.find("x.png", "the payments analyst decides", ranked=True)[0]
    # exact, and boxed on its first line only (a two-line rectangle would cover "After the call," and "whether")
    assert best["exact"] and best["y"] == 300 and best["height"] == 16 and best["x"] == 400
