"""Reference pages under docs/ that had no section of their own: the Brainstem start page, the AIBAST
RAPP pattern, the design system and the metrics administrator setup. They keep their address and
their own stylesheet and scripts; the site puts them inside its shell the way it does the workshop
pages (header above, footer below, their own site header removed)."""
import re
import sys

PAGES = [
    # (page, nav section)
    ("docs/start/index.html", "Learn"),
    ("docs/aibast-rapp-pattern.html", "Learn"),
    ("docs/design-system.html", "About"),
    ("docs/metrics-admin-setup.html", "About"),
]
OWN_HEADER_RE = re.compile(r"<header(?: class=\"topbar\")?>.*?</header>", re.S)


def build(site, page):
    build_site = sys.modules[page.__module__]
    out = {}
    for path, active in PAGES:
        depth = path.count("/")
        base = build_site.rel(depth)
        text = (site.root / path).read_text(encoding="utf-8")
        head = OWN_HEADER_RE.search(text)
        if head and "<nav" in head.group(0):
            text = text[:head.start()] + text[head.end():]
        text = re.sub(r"<body(?=[\s>])", '<body data-shell="wrapped"', text, count=1)
        text = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + build_site.shell_header(base, active), text, count=1)
        text = text.replace("</head>", f'<link rel="stylesheet" href="{base}assets/shell.css">\n</head>', 1)
        text = text.replace("</body>", build_site.shell_footer(base) + "\n</body>", 1)
        out[path] = text
    return out
