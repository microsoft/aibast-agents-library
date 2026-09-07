#!/usr/bin/env python3
"""Microsoft Clarity tag: the one rendering shared by the stamper and the scaffold.

The Clarity project ID lives in one place, ``clarity.json`` at the repository
root. ``render_tag`` turns it into the block every published page carries;
``scripts/apply_clarity_tag.py`` stamps or checks that block on the committed
pages and ``tools/scaffold_solution_journey.py`` emits it in fresh workshop
pages, so both paths produce byte-identical heads.

The rendered block is a consent-gated Clarity loader:

* it only runs on ``*.github.io`` hosts, so local previews and file:// opens
  never report sessions;
* it stays silent when the browser sends Global Privacy Control or Do Not Track;
* it shows a small cookie-consent bar and loads Clarity only after the visitor
  accepts; the choice is remembered per browser under
  ``localStorage["aibast-clarity-consent"]`` ("granted" or "denied").

The block is a hosting artifact, not solution content: ``strip_tag`` removes it
so downloadable solution bundles and their audit compare pages without it.

While ``project_id`` is empty the block is still stamped (so every page carries
the same bytes) but the loader returns before doing anything.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "clarity.json"

START_MARK = "<!-- clarity:start -->"
END_MARK = "<!-- clarity:end -->"
BLOCK_RE = re.compile(
    re.escape(START_MARK) + r".*?" + re.escape(END_MARK) + r"\n?", re.DOTALL
)
BLOCK_BYTES_RE = re.compile(BLOCK_RE.pattern.encode("ascii"), re.DOTALL)
HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)
PROJECT_ID_RE = re.compile(r"^[a-z0-9]{6,20}$")
CONSENT_STORAGE_KEY = "aibast-clarity-consent"
PRIVACY_STATEMENT_URL = "https://go.microsoft.com/fwlink/?LinkId=521839"

# Published site pages: root HTML plus these directories (see
# scripts/build_pages_site.py for what GitHub Pages actually serves).
PUBLIC_DIRECTORIES = ("docs", "reports", "solutions")
# Never tagged: the Brainstem UI that installs on users' machines, the
# Hippocampus docs bundled with the Azure function, local-first tools, and the
# beta Electron renderer.
EXCLUDED_PREFIXES = ("rapp_brainstem/", "rapp_ai/", "tools/", "beta/", "node_modules/")

TAG_TEMPLATE = """<!-- clarity:start -->
<script data-clarity-project="__PROJECT_ID__">
(function (w, d, id) {
  if (!id || !/\\.github\\.io$/i.test(d.location.hostname)) return;
  var n = w.navigator || {};
  if (n.globalPrivacyControl || n.doNotTrack === "1" || w.doNotTrack === "1") return;
  var KEY = "__CONSENT_KEY__";
  function read() { try { return w.localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { w.localStorage.setItem(KEY, v); } catch (e) {} }
  function load() {
    w.clarity = w.clarity || function () { (w.clarity.q = w.clarity.q || []).push(arguments); };
    var t = d.createElement("script"); t.async = 1; t.src = "https://www.clarity.ms/tag/" + id;
    var y = d.getElementsByTagName("script")[0]; y.parentNode.insertBefore(t, y);
    w.clarity("consent");
  }
  function el(tag, css, text) { var e = d.createElement(tag); e.style.cssText = css; if (text) e.textContent = text; return e; }
  function banner() {
    if (d.getElementById(KEY)) return;
    var bar = el("div", "position:fixed;left:0;right:0;bottom:0;z-index:2147483000;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px 16px;padding:12px 16px;background:Canvas;color:CanvasText;border-top:1px solid GrayText;font:14px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif");
    bar.id = KEY; bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Cookie consent");
    var text = el("span", "max-width:62ch", "This site uses Microsoft Clarity to understand how visitors use it. Typed text is masked. ");
    var link = el("a", "color:LinkText;text-decoration:underline", "Microsoft Privacy Statement");
    link.href = "__PRIVACY_URL__"; link.target = "_blank"; link.rel = "noopener";
    text.appendChild(link);
    var btn = "cursor:pointer;border-radius:6px;padding:7px 14px;font:inherit;font-weight:600;";
    var accept = el("button", btn + "border:1px solid AccentColor;background:AccentColor;color:AccentColorText", "Accept");
    var decline = el("button", btn + "border:1px solid GrayText;background:ButtonFace;color:ButtonText", "Decline");
    accept.type = "button"; decline.type = "button";
    accept.onclick = function () { write("granted"); bar.remove(); load(); };
    decline.onclick = function () { write("denied"); bar.remove(); };
    bar.appendChild(text); bar.appendChild(accept); bar.appendChild(decline);
    d.body.appendChild(bar);
  }
  var choice = read();
  if (choice === "granted") { load(); return; }
  if (choice === "denied") return;
  if (d.body) banner(); else d.addEventListener("DOMContentLoaded", banner);
})(window, document, "__PROJECT_ID__");
</script>
<!-- clarity:end -->
"""


def load_config(path: Path = CONFIG_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    project_id = data.get("project_id", "")
    if not isinstance(project_id, str):
        raise ValueError("clarity.json project_id must be a string")
    if project_id and not PROJECT_ID_RE.match(project_id):
        raise ValueError(
            f"clarity.json project_id {project_id!r} is not a Clarity project ID"
        )
    return data


def render_tag(project_id: str) -> str:
    return (
        TAG_TEMPLATE.replace("__PROJECT_ID__", project_id)
        .replace("__CONSENT_KEY__", CONSENT_STORAGE_KEY)
        .replace("__PRIVACY_URL__", PRIVACY_STATEMENT_URL)
    )


def current_tag(root: Path = ROOT) -> str:
    """The tag every published page must carry right now (from clarity.json)."""
    return render_tag(load_config(root / "clarity.json")["project_id"])


def strip_tag(text: str) -> str:
    """Return ``text`` without any Clarity block."""
    return BLOCK_RE.sub("", text)


def strip_tag_bytes(data: bytes) -> bytes:
    """Byte-level ``strip_tag`` for bundle and audit comparisons."""
    return BLOCK_BYTES_RE.sub(b"", data)


def is_public_page(relative: str) -> bool:
    if not relative.endswith(".html"):
        return False
    if relative.startswith(EXCLUDED_PREFIXES):
        return False
    if "/" not in relative:
        return True
    return relative.split("/", 1)[0] in PUBLIC_DIRECTORIES


def public_pages(root: Path = ROOT) -> list[Path]:
    pages = []
    for path in root.rglob("*.html"):
        relative = path.relative_to(root).as_posix()
        if "/node_modules/" in f"/{relative}" or relative.startswith(".git/"):
            continue
        if is_public_page(relative):
            pages.append(path)
    return sorted(pages)


def stamp(html: str, tag: str) -> str:
    """Return ``html`` carrying exactly one copy of ``tag`` before ``</head>``."""
    stripped = strip_tag(html)
    match = HEAD_CLOSE_RE.search(stripped)
    if match is None:
        raise ValueError("page has no </head>")
    # Nothing is added outside the block, so strip_tag(stamp(x)) == x exactly;
    # bundles and the rollout audit rely on that.
    return stripped[: match.start()] + tag + stripped[match.start() :]
