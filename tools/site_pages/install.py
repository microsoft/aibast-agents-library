"""Installer content in the shared shell; installer scripts remain at their root URLs."""

from tools.site_pages._content import section_page, source_body


def build(site, page):
    body = source_body(site, "docs/installer.html", 1)
    return {"install/index.html": section_page(
        site, page, "install/", "Install the RAPP Brainstem",
        "Install locally, follow the manual steps, and advance through the three tiers.",
        body, active="Install")}
