"""Place evidence boxes from what is actually visible in a frame (tesseract word boxes), with placement rules:

- step frames: panel items (model, knowledge files, skills) only in the right-hand panel (x >= PANEL_X); the agent
  name and the Draft badge only in the header area;
- case frames: never inside the user's question bubble, and only below the agent's reasoning line;
- an anchor that is not visible gets no box (and no legend entry).
"""
import re, subprocess
from functools import lru_cache
from pathlib import Path

PANEL_X = 1000


def _tsv(image, scale=1, dx=0, min_conf=30, psm="11"):
    out = subprocess.run(["tesseract", str(image), "-", "--psm", psm, "tsv"], capture_output=True, text=True).stdout
    ws = []
    for line in out.splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 12 or not p[11].strip():
            continue
        try:
            if float(p[10]) < min_conf:
                continue
        except ValueError:
            continue
        ws.append({"x": int(int(p[6]) / scale) + dx, "y": int(int(p[7]) / scale), "w": int(int(p[8]) / scale),
                   "h": int(int(p[9]) / scale), "t": p[11].strip()})
    return ws


@lru_cache(maxsize=512)
def words(image):
    """Full-frame words, plus the right-hand panel read again at 3x (skill/knowledge chips with icons are often missed
    at 1x); both reads are kept."""
    import tempfile
    from PIL import Image
    ws = _tsv(image)
    im = Image.open(image)
    if im.width > PANEL_X:
        crop = im.crop((PANEL_X, 0, im.width, im.height))
        from PIL import ImageOps
        crop = ImageOps.autocontrast(ImageOps.grayscale(crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)))
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            crop.save(tmp.name)
            panel = _tsv(tmp.name, scale=3, dx=PANEL_X, min_conf=10)
            # block mode reads a focused (blue-outlined) chip that sparse mode skips
            panel += _tsv(tmp.name, scale=3, dx=PANEL_X, min_conf=10, psm="6")
        ws = ws + panel
    ws.sort(key=lambda w: (round(w["y"] / 8), w["x"]))
    return tuple(tuple(sorted(w.items())) for w in ws)


def _norm(t):
    # dots survive only inside numbers (6.5, 7.6%): OCR drops the one in ".md" often enough to matter
    t = re.sub(r"[^a-z0-9$%.,/:-]", "", t.lower())
    return re.sub(r"(?<!\d)\.|\.(?!\d)", "", t).strip(",:")


LINE_TOL = 10      # px: words whose tops are this close share a line
GAP_STRUCT = 9     # px: a prose space is ~4-6 px; a table cell, code chip or standalone line has more room either side
ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:[-_][A-Z0-9]+)+\b")


def _loose(first, target, single):
    """The old, forgiving first-word rule: a truncated chip or an OCR slip still matches."""
    return (first.startswith(target[:max(3, len(target) - 2)]) or target in first
            or (len(first) >= 8 and target.startswith(first.rstrip(".")))
            or (single and len(first) >= 9 and target.endswith(first)))


def _line(ws, w):
    return sorted((x for x in ws if abs(x["y"] - w["y"]) <= LINE_TOL), key=lambda x: x["x"])


def _structure(ws, run):
    """0 prose; 1 starts its line (a heading or a list label); 2 stands apart from its neighbours on both sides
    (a table cell, a code chip, a heading line of its own)."""
    line = _line(ws, run[0])
    x0 = run[0]["x"]; x1 = run[-1]["x"] + run[-1]["w"]
    left = [x for x in line if x["x"] + x["w"] <= x0 + 1 and x not in run]
    right = [x for x in line if x["x"] >= x1 - 1 and x not in run]
    gl = x0 - max(x["x"] + x["w"] for x in left) if left else None
    gr = min(x["x"] for x in right) - x1 if right else None
    if (gl is None or gl >= GAP_STRUCT) and (gr is None or gr >= GAP_STRUCT):
        return 2
    if gl is None:
        return 1
    return 0


def find(image, text, ranked=False):
    """Occurrences of `text` as a run of consecutive OCR words on one line (a truncated chip still matches by prefix).

    Match preference (best first): an exact, full-phrase match (case-insensitive) beats a partial or prefix match;
    among equals a heading, table cell or code chip (room on both sides, or the start of its line) beats a word in
    prose; then reading order. Each hit carries `exact`, `structure` and `text` (what the screen says)."""
    ws = [dict(w) for w in words(str(image))]
    target = [_norm(t) for t in re.split(r"\s+", text.strip()) if _norm(t)]
    if not target:
        return []
    hits = []
    for i, w in enumerate(ws):
        first = _norm(w["t"])
        if not _loose(first, target[0], len(target) == 1):
            continue
        run, exact = [w], first == target[0] or (len(target) > 1 and first.endswith(target[0]) and len(first) - len(target[0]) <= 1)
        cur_y = w["y"]
        reach = 600 if "\n" in text else 90    # "Model\nClaude Opus 5.5": a label and its value across one row
        for k in range(1, len(target)):
            # the next word is the nearest word to its right on the same line, within a normal word gap (no skipping:
            # "Tier 1 to Tier 2" is not "Tier 2"); OCR's reading order is not left-to-right, so search by position
            end = run[-1]["x"] + run[-1]["w"]
            right = [x for x in ws if abs(x["y"] - cur_y) <= LINE_TOL and end - 2 <= x["x"] <= end + reach
                     and x not in run and _norm(x["t"])]
            nxt = min(right, key=lambda x: x["x"], default=None)
            if nxt is None:
                # a heading that wraps: the phrase continues at the start of the next line
                # (only when the run reached the end of its line); the continuation is the leftmost word of the next
                # line, which starts at the paragraph's margin
                below = [x for x in ws if cur_y + 8 < x["y"] <= cur_y + 2.4 * w["h"] and _norm(x["t"])
                         and x["x"] < run[-1]["x"] and x["x"] <= w["x"] + 20]
                if below and not any(abs(x["y"] - cur_y) <= LINE_TOL and x["x"] > end + 2 and x["x"] - end < 300
                                     and _norm(x["t"]) for x in ws if x not in run):
                    top = min(x["y"] for x in below)
                    nxt = min((x for x in below if x["y"] - top <= LINE_TOL), key=lambda x: x["x"])
                else:
                    nxt = None
                if nxt is not None:
                    cur_y = nxt["y"]
            if nxt is None:
                break
            nt = _norm(nxt["t"])
            if nt == target[k]:
                pass
            elif target[k] in nt or nt.startswith(target[k][:4]):
                exact = exact and k == len(target) - 1 and nt.startswith(target[k]) and len(nt) - len(target[k]) <= 1
            else:
                break
            run.append(nxt)
        k = len(run)
        whole = "".join(target)
        joined = _norm("".join(x["t"] for x in run)).rstrip(".")
        if not (k == len(target) or (len(joined) >= 8 and whole.startswith(joined[: max(8, int(len(whole) * 0.6))]))):
            continue
        exact = exact and k == len(target)
        tail_only = len(target) == 1 and not target[0].startswith(first[:3]) and target[0].endswith(first.rstrip("."))
        if tail_only and _structure(ws, run) == 0:
            continue    # a chip read only as its tail is a chip, not the same word in a sentence ("about settlement or")
        shown_run = run
        later = [r for r in run if abs(r["y"] - run[0]["y"]) > LINE_TOL]
        if later and abs(later[0]["x"] - run[0]["x"]) > 20:
            # wrapped mid-paragraph: one rectangle over both lines would swallow the sentence around it, so box the
            # part on the first line (a heading that wraps at its own margin keeps both lines)
            shown_run = [r for r in run if abs(r["y"] - run[0]["y"]) <= LINE_TOL]
        x0 = min(r["x"] for r in shown_run); y0 = min(r["y"] for r in shown_run)
        x1 = max(r["x"] + r["w"] for r in shown_run); y1 = max(r["y"] + r["h"] for r in shown_run)
        line = _line(ws, run[0])
        lg = [x0 - (x["x"] + x["w"]) for x in line if x["x"] + x["w"] <= x0 + 1 and x not in run]
        rg = [x["x"] - x1 for x in line if x["x"] >= x1 - 1 and x not in run]
        lw = max((x for x in line if x["x"] + x["w"] <= x0 + 1 and x not in run), key=lambda x: x["x"], default=None)
        hits.append({"left_word": (lw["x"], lw["w"], lw["t"]) if lw else None, "x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0, "exact": exact,
                     "structure": _structure(ws, run), "text": " ".join(r["t"] for r in run),
                     "gap_left": min(lg) if lg else None, "gap_right": min(rg) if rg else None})
    if ranked:
        hits = rank(hits)
    return hits


def rank(hits):
    """Stable sort: exact full phrase first, then structure (cell/code/heading over prose), then reading order."""
    return sorted(hits, key=lambda h: (not h.get("exact"), -h.get("structure", 0)))


def split_ids(anchor):
    """A legend that lists several record IDs ("HB-2027 and HB-2031") is boxed once per ID."""
    ids = ID_RE.findall(anchor)
    return ids if len(ids) > 1 else [anchor]


def screen_label(anchor, hit):
    """The legend names what the screen shows: keep the anchor's wording, but take the screen's letter case and a
    leading sign (MISSING vs Missing, 9,846.90 vs -9,846.90)."""
    shown = (hit.get("text") or "").strip(" ,;:.()*")
    if not shown:
        return anchor
    sign = re.match(r"^[-\u2212+]", shown)
    core = shown[1:] if sign and not re.match(r"^[-\u2212+]", anchor) else shown
    if _norm(core) == _norm(anchor) and core.lower() == anchor.lower():
        return (sign.group(0) if sign and not re.match(r"^[-\u2212+]", anchor) else "") + core
    return anchor


def rebox(image, anchors, kind="step", prompt=None, name=None):
    image = Path(image)
    from PIL import Image
    W, H = Image.open(image).size
    prompt_rows = None
    if kind == "case" and prompt:
        ph = find(image, " ".join(prompt.split()[:6]))
        if ph:
            top = ph[0]["y"]
            pb = find(image, " ".join(prompt.split()[-4:]))
            # the bubble's last words: the nearest loose match at or below its first line (a bubble is at most ~3 lines;
            # loose matches further down the answer must not swallow it)
            ends = [h["y"] + h["height"] for h in pb if top <= h["y"] <= top + 90]
            bottom = min(ends) if ends else top + 60
            prompt_rows = (top - 12, bottom + 12)
    answer_top = None
    if kind == "case":
        marks = [h for t in ("Thought for", "Reasoned through", "Called", "Used skill") for h in find(image, t)]
        if prompt_rows:
            marks = [m for m in marks if m["y"] > prompt_rows[1]]
        if marks:
            first = min(m["y"] for m in marks)
            answer_top = max(m["y"] for m in marks if m["y"] < first + 400)
    boxes, used = [], []
    for a in [x for anchor in anchors for x in split_ids(anchor)]:
        cands = find(image, a)
        if kind == "step":
            if a in ("Draft", "Untitled Agent") or (name is not None and a == name):
                cands = [c for c in cands if c["y"] < 200]
            elif "instructions" in image.name:
                cands = [c for c in cands if c["y"] >= 200]      # the instructions heading in the editor canvas, not the name
            else:
                cands = [c for c in cands if c["x"] >= PANEL_X]
        else:
            if answer_top is not None:
                cands = [c for c in cands if c["y"] > answer_top] or cands
            if prompt_rows:
                cands = [c for c in cands if not (prompt_rows[0] <= c["y"] <= prompt_rows[1])]
                cands = [c for c in cands if c["y"] > prompt_rows[1]] or cands
        # two anchors never share one box ("HB-2027" must not reuse the HB-2031 hit)
        cands = [c for c in cands if not any(abs(c["x"] - u["x"]) < 6 and abs(c["y"] - u["y"]) < 6 for u in used)]
        cands = rank(cands)
        parts = a.split()
        if (not cands or not cands[0].get("exact")) and len(parts) >= 4:
            # OCR often drops the first word of a table cell: an exact hit on the rest, widened back over the missing
            # word, beats a partial hit on the first word alone
            rest = [dict(h) for h in find(image, " ".join(parts[1:])) if h.get("exact")]
            rest = [h for h in rest if not any(abs(h["x"] - u["x"]) < 6 and abs(h["y"] - u["y"]) < 6 for u in used)]
            if rest:
                h = rank(rest)[0]
                per_char = h["width"] / max(1, len(" ".join(parts[1:])))
                grow = int(per_char * (len(parts[0]) + 1))
                h.update({"x": h["x"] - grow, "width": h["width"] + grow, "gap_left": None, "left_word": None,
                          "text": a})
                cands = [h] + cands
        if not cands:
            continue
        c = dict(cands[0])
        used.append(cands[0])
        lw = c.get("left_word")
        if lw and c.get("gap_left") is not None and c["gap_left"] < 8 and len(lw[2]) <= 6 and re.search(r"\d", lw[2]):
            # a time or number pressed against the phrase ("The 10:30 Leadership Huddle") goes inside the box, readable,
            # instead of under its outline
            c["width"] += c["x"] - lw[0]; c["x"] = lw[0]
            c["gap_left"] = None if lw[0] < 1 else 99
        # pad 6 px, but never into the neighbouring word ("The 10:30 Leadership Huddle" keeps 10:30 readable)
        pl = 6 if c.get("gap_left") is None else max(2, min(6, c["gap_left"] // 2 - 1))
        pr = 6 if c.get("gap_right") is None else max(2, min(6, c["gap_right"] // 2 - 1))
        x = max(0, c["x"] - pl); y = max(0, c["y"] - 4)
        boxes.append({"x": x, "y": y, "width": min(c["width"] + pl + pr, W - x - 1),
                      "height": min(c["height"] + 8, H - y - 1), "label": screen_label(a, c)[:96]})
    return boxes
