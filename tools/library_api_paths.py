"""Path data and generated navigation, built by build_library_api.py only."""

import hashlib
import json
import posixpath
import re
from html import escape
from urllib.parse import urlsplit


NAVIGATION_BYTES_RE = re.compile(
    rb'<script src="[^"]*path-route\.js" data-path-strip defer></script>\n?'
)


def strip_navigation_bytes(data):
    """Keep site-only return navigation out of downloadable solution bundles."""
    return NAVIGATION_BYTES_RE.sub(b"", data)


def stamp_navigation(text, src):
    text = strip_navigation_bytes(text.encode("utf-8")).decode("utf-8")
    marker = "<!-- aibast-design:start -->" if "<!-- aibast-design:start -->" in text else "</head>"
    tag = f'<script src="{src}" data-path-strip defer></script>'
    return text.replace(marker, tag + "\n" + marker, 1)


def paths_document(root, solutions):
    source = json.loads((root / "paths/paths.source.json").read_text(encoding="utf-8"))
    destinations = {}
    for slug, solution in solutions.items():
        learn = solution["learn"]
        destinations[slug] = {
            "name": solution["name"],
            "industries": solution["industries"],
            "personas": solution["personas"],
            "demo": solution["try"]["page"],
            "setup": f"start.html?solution={slug}",
            **{key: learn.get(key) for key in ("workshop", "manual_tutorial", "field_guide")},
        }
    doc = {**source, "source": {"path": "paths/paths.source.json",
                              "sha256": hashlib.sha256((root / "paths/paths.source.json").read_bytes()).hexdigest()},
           "solutions": destinations}
    for route in doc["routes"]:
        keys = {step["destination"] for step in route["steps"] if "destination" in step}
        route["solutions"] = [slug for slug, item in destinations.items()
                              if all(item.get(key) for key in keys)] if route["area"] else []
        if route["area"] and not route["solutions"]:
            raise ValueError(f"No complete destinations for {route['id']}")
    for url in destination_urls(doc):
        parsed = urlsplit(url)
        if (parsed.scheme or parsed.netloc or parsed.path.startswith("/")
                or "\\" in parsed.path or ".." in parsed.path.split("/")):
            raise ValueError(f"Path destination must be site-relative: {url}")
        target = root / parsed.path
        if not target.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Path destination escapes the site: {url}")
        if not target.is_file():
            raise ValueError(f"Missing path destination: {url}")
    return doc


def destination_urls(doc):
    urls = {doc["something_else"]["destination"]}
    urls.add(doc["help"]["url"])
    urls.update(item["url"] for item in doc["prerequisites"])
    for route in doc["routes"]:
        for step in route["steps"]:
            if "url" in step:
                urls.add(step["url"])
            else:
                urls.update(doc["solutions"][slug][step["destination"]]
                            for slug in route["solutions"])
    return sorted(urls)


def page_outputs(root, doc):
    """Keep the no-script list and destination script references in the same build."""
    outputs = {}
    items = "\n".join(f'<li><a href="{escape(url, quote=True)}">{escape(label)}</a></li>'
                      for url, label in destination_labels(doc))
    block = "<!-- paths-list:start -->\n<ul>\n" + items + "\n</ul>\n<!-- paths-list:end -->"
    page = root / "paths.html"
    text = page.read_text(encoding="utf-8")
    updated, count = re.subn(r"<!-- paths-list:start -->.*?<!-- paths-list:end -->",
                             lambda _: block, text, flags=re.S)
    if count != 1:
        raise ValueError("paths.html must contain one generated paths-list block")
    outputs["paths.html"] = updated.encode("utf-8")
    for url in destination_urls(doc):
        name = urlsplit(url).path
        text = (root / name).read_text(encoding="utf-8")
        src = posixpath.relpath("solutions/_shared/path-route.js",
                               posixpath.dirname(name) or ".")
        outputs[name] = stamp_navigation(text, src).encode("utf-8")
    return outputs


def destination_labels(doc):
    labels = {}
    for route in doc["routes"]:
        for step in route["steps"]:
            if "url" in step:
                labels[step["url"]] = step["label"]
            else:
                for slug in route["solutions"]:
                    item = doc["solutions"][slug]
                    labels[item[step["destination"]]] = f"{item['name']}: {step['label']}"
    for item in doc["prerequisites"]:
        labels[item["url"]] = item["label"]
    labels[doc["something_else"]["destination"]] = "Tell us what you were looking for"
    labels[doc["help"]["url"]] = doc["help"]["label"]
    return sorted(labels.items())
