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


def find(image, text):
    """Occurrences of `text` as a run of OCR words on one line (a truncated chip still matches by prefix)."""
    ws = [dict(w) for w in words(str(image))]
    target = [_norm(t) for t in re.split(r"\s+", text.strip()) if _norm(t)]
    if not target:
        return []
    hits = []
    for i, w in enumerate(ws):
        first = _norm(w["t"])
        if not (first.startswith(target[0][:max(3, len(target[0]) - 2)]) or target[0] in first
                or (len(first) >= 8 and target[0].startswith(first.rstrip(".")))
                or (len(target) == 1 and len(first) >= 9 and target[0].endswith(first))):  # a chip read only as its tail
            continue
        run, j, k = [w], i + 1, 1
        while k < len(target) and j < len(ws):
            nxt = ws[j]
            if abs(nxt["y"] - w["y"]) > 10 or nxt["x"] < run[-1]["x"]:
                break
            if target[k] in _norm(nxt["t"]) or _norm(nxt["t"]).startswith(target[k][:4]):
                run.append(nxt); k += 1
            j += 1
        whole = "".join(target)
        joined = _norm("".join(x["t"] for x in run)).rstrip(".")
        if k == len(target) or (len(joined) >= 8 and whole.startswith(joined[: max(8, int(len(whole) * 0.6))])):
            x0 = min(r["x"] for r in run); y0 = min(r["y"] for r in run)
            x1 = max(r["x"] + r["w"] for r in run); y1 = max(r["y"] + r["h"] for r in run)
            hits.append({"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})
    return hits


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
    boxes = []
    for a in anchors:
        cands = find(image, a)
        if kind == "step":
            if a in ("Draft", "Untitled Agent") or (name is not None and a == name):
                cands = [c for c in cands if c["y"] < 200]
            elif "instructions" in image.name:
                cands = [c for c in cands if c["y"] >= 120]      # the instructions heading in the editor canvas
            else:
                cands = [c for c in cands if c["x"] >= PANEL_X]
        else:
            if answer_top is not None:
                cands = [c for c in cands if c["y"] > answer_top] or cands
            if prompt_rows:
                cands = [c for c in cands if not (prompt_rows[0] <= c["y"] <= prompt_rows[1])]
                cands = [c for c in cands if c["y"] > prompt_rows[1]] or cands
        if not cands:
            continue
        c = cands[0]
        x = max(0, c["x"] - 6); y = max(0, c["y"] - 4)
        boxes.append({"x": x, "y": y, "width": min(c["width"] + 12, W - x - 1),
                      "height": min(c["height"] + 8, H - y - 1), "label": a[:48]})
    return boxes
