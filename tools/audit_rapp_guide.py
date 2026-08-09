#!/usr/bin/env python3
"""Fail-closed preservation and workshop-theme gate for the RAPP guide."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Comment, Tag


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GUIDE = ROOT / "docs" / "rapp-guide.html"
DEFAULT_CONTRACT = ROOT / "state" / "rapp_guide_content_contract.json"
AUDIT_SCHEMA = "aibast-rapp-guide-audit/1.0"
CONTRACT_SCHEMA = "aibast-rapp-guide-content-contract/1.0"
TRUSTED_SOURCE_COMMIT = "57685f2cabfe06a8c7df72ab8da58dfab70a838c"
TRUSTED_SOURCE_BLOB_OID = "6ec2da0cfc01e819af22ce0dd01f6257a6789317"
TRUSTED_SOURCE_PATH = "docs/rapp-guide.html"
CONTENT_SECTION_IDS = (
    "overview",
    "architecture",
    "principles",
    *(f"step{number}" for number in range(1, 15)),
    "team-setup",
    "scaling",
    "roadmap",
    "tools",
)
PRESERVED_FUNCTIONS = (
    "navigateToSection",
    "nextSection",
    "previousSection",
    "updateProgress",
    "toggleSidebar",
    "syncSidebarForViewport",
    "copyCode",
    "toggleFallback",
    "toggleQuiz",
    "selectQuizOption",
    "submitQuiz",
    "scrollToSection",
    "initializeQuizzes",
    "handleHashNavigation",
)
LIGHT_THEME_VARIABLES = {
    "--cp-bg": "#f7f4ef",
    "--cp-bg-elevated": "#fcfbf8",
    "--cp-surface": "#ffffff",
    "--cp-surface-soft": "#f5f5f5",
    "--cp-border": "#dedede",
    "--cp-border-strong": "#919191",
    "--cp-text": "#242424",
    "--cp-text-muted": "#5c5c5c",
    "--cp-text-soft": "#6f6f6f",
    "--cp-accent": "#b11f4b",
    "--cp-accent-hover": "#9a1a41",
    "--cp-accent-soft": "rgba(177, 31, 75, 0.08)",
    "--cp-accent-fg": "#ffffff",
    "--cp-success": "#16a34a",
    "--cp-danger": "#dc2626",
    "--cp-warning": "#f59e0b",
    "--cp-link": "#0078d4",
    "--cp-shadow": "0 18px 48px rgba(0, 0, 0, 0.12)",
    "--cp-overlay": "rgba(255, 255, 255, 0.8)",
    "--cp-panel": "rgba(255, 255, 255, 0.86)",
    "--cp-panel-strong": "rgba(255, 255, 255, 0.96)",
    "--cp-sheen": "rgba(255, 255, 255, 0.55)",
    "--cp-highlight": "rgba(177, 31, 75, 0.12)",
}
DARK_THEME_VARIABLES = {
    "--cp-bg": "#3d3b3a",
    "--cp-bg-elevated": "#343231",
    "--cp-surface": "#292929",
    "--cp-surface-soft": "#2e2e2e",
    "--cp-border": "#474747",
    "--cp-border-strong": "#5f5f5f",
    "--cp-text": "#dedede",
    "--cp-text-muted": "#919191",
    "--cp-text-soft": "#b0b0b0",
    "--cp-accent": "#fd8ea1",
    "--cp-accent-hover": "#fb7b91",
    "--cp-accent-soft": "rgba(253, 142, 161, 0.14)",
    "--cp-accent-fg": "#1a1a1a",
    "--cp-success": "#4ade80",
    "--cp-danger": "#f87171",
    "--cp-warning": "#fbbf24",
    "--cp-link": "#4da6ff",
    "--cp-shadow": "0 18px 48px rgba(0, 0, 0, 0.32)",
    "--cp-overlay": "rgba(41, 41, 41, 0.88)",
    "--cp-panel": "rgba(41, 41, 41, 0.72)",
    "--cp-panel-strong": "rgba(41, 41, 41, 0.96)",
    "--cp-sheen": "rgba(255, 255, 255, 0.04)",
    "--cp-highlight": "rgba(253, 142, 161, 0.12)",
}
LEGACY_VARIABLES = {
    "--primary",
    "--primary-dark",
    "--secondary",
    "--accent",
    "--success",
    "--danger",
    "--warning",
    "--info",
    "--bg-light",
    "--bg-white",
    "--text-dark",
    "--text-medium",
    "--text-light",
    "--border",
    "--shadow",
    "--shadow-lg",
}
DEAD_TRACK_MARKERS = (
    "track-selector",
    "track-btn",
    "track-badge",
    "technical-only",
    "non-technical-only",
    "setTrack",
    "showTrackNotification",
    "initializeTrack",
    "framework-track",
    "data-track",
)
COLOR_KEYWORDS = {
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgreen",
    "darkgrey",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkslategrey",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "gray",
    "green",
    "greenyellow",
    "grey",
    "honeydew",
    "hotpink",
    "indianred",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lemonchiffon",
    "lightblue",
    "lightcoral",
    "lightcyan",
    "lightgoldenrodyellow",
    "lightgray",
    "lightgreen",
    "lightgrey",
    "lightpink",
    "lightsalmon",
    "lightseagreen",
    "lightskyblue",
    "lightslategray",
    "lightslategrey",
    "lightsteelblue",
    "lightyellow",
    "lime",
    "limegreen",
    "linen",
    "magenta",
    "maroon",
    "mediumaquamarine",
    "mediumblue",
    "mediumorchid",
    "mediumpurple",
    "mediumseagreen",
    "mediumslateblue",
    "mediumspringgreen",
    "mediumturquoise",
    "mediumvioletred",
    "midnightblue",
    "mintcream",
    "mistyrose",
    "moccasin",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orange",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "paleturquoise",
    "palevioletred",
    "papayawhip",
    "peachpuff",
    "peru",
    "pink",
    "plum",
    "powderblue",
    "purple",
    "rebeccapurple",
    "red",
    "rosybrown",
    "royalblue",
    "saddlebrown",
    "salmon",
    "sandybrown",
    "seagreen",
    "seashell",
    "sienna",
    "silver",
    "skyblue",
    "slateblue",
    "slategray",
    "slategrey",
    "snow",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "transparent",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowgreen",
}
COLOR_FUNCTION_RE = re.compile(
    r"(?i)\b(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color|color-mix)\s*\("
)
HEX_COLOR_RE = re.compile(
    r"(?i)(?<![\w-])#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{4}|[0-9a-f]{3})\b"
)
FUNCTION_RE = re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(")
STORAGE_RE = re.compile(
    r"""localStorage\.(?:getItem|setItem)\(\s*['"]([^'"]+)""",
    re.IGNORECASE,
)
SHELL_INTERNAL_LINK_ALLOWLIST = {
    ("Library", "../library.html"),
    ("Workshop settings", "../solutions/_shared/workshop-settings.html"),
}
SHELL_GITHUB_ISSUES_PATHS = {
    "/microsoft/aibast-agents-library/issues",
    "/microsoft/aibast-agents-library/issues/new",
}


class CssParseError(ValueError):
    pass


@dataclass(frozen=True)
class CssDeclaration:
    contexts: tuple[str, ...]
    property: str
    value: str
    source: str


class FailureCollector:
    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []

    def add(self, category: str, message: str) -> None:
        item = {"category": category, "message": message}
        if item not in self.items:
            self.items.append(item)


def normalized_visible_text(node: Tag | BeautifulSoup) -> str:
    clone = BeautifulSoup(str(node), "html.parser")
    for hidden in clone.select("script, style, template"):
        hidden.decompose()
    for comment in clone.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    return " ".join(clone.get_text(" ", strip=True).split())


def _script_text(script: Tag) -> str:
    if script.string is not None:
        return str(script.string)
    return html.unescape(script.decode_contents())


def _copy_button_count(soup: BeautifulSoup) -> int:
    return len(
        soup.select(
            "button.copy-btn, button.copy-button, [data-copy-button]"
        )
    )


def _persistent_storage_keys(text: str) -> list[str]:
    return sorted(set(STORAGE_RE.findall(text)))


def _normalized_text_sha256(node: Tag) -> str:
    return sha256(normalized_visible_text(node).encode("utf-8")).hexdigest()


def _extract_sidebar_links(soup: BeautifulSoup) -> list[dict[str, Any]]:
    sidebar = soup.select_one("#sidebar")
    if sidebar is None:
        return []
    return [
        {
            "href": link.get("href"),
            "label": normalized_visible_text(link),
        }
        for link in sidebar.select("a[href]")
    ]


def _extract_content_external_links(
    soup: BeautifulSoup,
) -> list[dict[str, str | None]]:
    links: list[dict[str, str | None]] = []
    for section in soup.select(".content-section"):
        for link in section.select("a[href]"):
            href = link.get("href", "")
            if re.match(r"(?i)^https?://", href):
                links.append(
                    {
                        "section_id": section.get("id"),
                        "href": href,
                    }
                )
    return links


def _call_argument_id(source: str, function_name: str) -> str | None:
    match = re.search(
        rf"""{re.escape(function_name)}\(\s*['"]([^'"]+)['"]""",
        source,
    )
    return match.group(1) if match else None


def _copy_target(button: Tag, soup: BeautifulSoup) -> Tag | None:
    explicit_id = button.get("data-copy-target") or button.get("aria-controls")
    if explicit_id:
        return soup.find(id=explicit_id)

    onclick = button.get("onclick", "")
    by_id = re.search(
        r"""copyCode\(\s*document\.getElementById\(\s*['"]([^'"]+)['"]""",
        onclick,
    )
    if by_id:
        return soup.find(id=by_id.group(1))
    if "parentElement.nextElementSibling" in onclick:
        return button.parent.find_next_sibling(["pre", "code"])
    if re.search(r"\bcopyCode\(\s*this\s*\)", onclick):
        block = button.find_parent(class_="code-block")
        return block.find(["pre", "code"]) if block else None
    return None


def _extract_copy_mappings(soup: BeautifulSoup) -> list[dict[str, Any]]:
    mappings = []
    for button in soup.select(
        "button.copy-btn, button.copy-button, [data-copy-button]"
    ):
        target = _copy_target(button, soup)
        mappings.append(
            {
                "button_label": normalized_visible_text(button),
                "target_id": target.get("id") if target else None,
                "target_tag": target.name if target else None,
                "target_tag_ordinal": (
                    soup.find_all(target.name).index(target) if target else None
                ),
                "target_normalized_text_sha256": (
                    _normalized_text_sha256(target) if target else None
                ),
            }
        )
    return mappings


def _fallback_toggles(soup: BeautifulSoup) -> list[Tag]:
    explicit = list(soup.select("[data-fallback-toggle]"))
    if explicit:
        return explicit
    return [
        node
        for node in soup.select('[onclick*="toggleFallback"]')
        if _call_argument_id(node.get("onclick", ""), "toggleFallback")
    ]


def _is_initially_hidden(node: Tag | None) -> bool:
    if node is None:
        return False
    return node.has_attr("hidden") or bool(
        re.search(
            r"(?:^|;)\s*display\s*:\s*none(?:\s*!important)?\s*(?:;|$)",
            node.get("style", ""),
            re.IGNORECASE,
        )
    )


def _extract_fallback_mappings(soup: BeautifulSoup) -> list[dict[str, Any]]:
    mappings = []
    for toggle in _fallback_toggles(soup):
        target_id = toggle.get("aria-controls") or _call_argument_id(
            toggle.get("onclick", ""), "toggleFallback"
        )
        target = soup.find(id=target_id) if target_id else None
        label_node = toggle.select_one(".code-language") or toggle
        mappings.append(
            {
                "toggle_label": normalized_visible_text(label_node),
                "aria_controls": target_id,
                "target_id": target_id,
                "target_normalized_text_sha256": (
                    _normalized_text_sha256(target) if target else None
                ),
                "initial_hidden": _is_initially_hidden(target),
            }
        )
    return mappings


def _extract_quizzes(
    text: str,
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    storage_keys = _persistent_storage_keys(text)
    completion_key = storage_keys[0] if len(storage_keys) == 1 else None
    quizzes = []
    for quiz in soup.select(".gut-check[id], .quiz[id]"):
        quiz_id = quiz.get("id")
        submit = quiz.select_one(".quiz-submit")
        correct_index = None
        if submit:
            call = re.search(
                rf"""submitQuiz\(\s*['"]{re.escape(quiz_id or '')}['"]\s*,\s*(\d+)""",
                submit.get("onclick", ""),
            )
            if call:
                correct_index = int(call.group(1))
        quizzes.append(
            {
                "id": quiz_id,
                "option_visible_texts": [
                    normalized_visible_text(option)
                    for option in quiz.select(".quiz-option")
                ],
                "submit_quiz_correct_index": correct_index,
                "data_correct": submit.get("data-correct") if submit else None,
                "data_incorrect": (
                    submit.get("data-incorrect") if submit else None
                ),
                "data_review_section": (
                    submit.get("data-review-section") if submit else None
                ),
                "persistent_completion_key": completion_key,
            }
        )
    return quizzes


def build_content_contract_from_text(
    text: str,
    source: str = "docs/rapp-guide.html",
    *,
    trusted_source_commit: str = TRUSTED_SOURCE_COMMIT,
    trusted_source_blob_oid: str = TRUSTED_SOURCE_BLOB_OID,
) -> dict[str, Any]:
    soup = BeautifulSoup(text, "html.parser")
    sections = soup.select(".content-section")
    section_records = []
    for section in sections:
        normalized = normalized_visible_text(section)
        section_records.append(
            {
                "id": section.get("id"),
                "normalized_visible_text_sha256": sha256(
                    normalized.encode("utf-8")
                ).hexdigest(),
            }
        )
    sidebar_links = _extract_sidebar_links(soup)
    external_hrefs = [
        link.get("href")
        for link in soup.select("a[href]")
        if re.match(r"(?i)^https?://", link.get("href", ""))
    ]
    functions = set(FUNCTION_RE.findall(text))
    quizzes = _extract_quizzes(text, soup)
    copy_mappings = _extract_copy_mappings(soup)
    fallback_mappings = _extract_fallback_mappings(soup)
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 1,
        "source": source,
        "trusted_source_commit": trusted_source_commit,
        "trusted_source_blob_oid": trusted_source_blob_oid,
        "normalization": (
            "Remove script, style, template, and comments; join rendered text "
            "with spaces; collapse Unicode whitespace."
        ),
        "content_section_ids": [
            record["id"] for record in section_records
        ],
        "content_sections": section_records,
        "sidebar_links": sidebar_links,
        "external_hrefs": external_hrefs,
        "content_external_links": _extract_content_external_links(soup),
        "quiz_ids": [quiz["id"] for quiz in quizzes],
        "quizzes": quizzes,
        "copy_button_count": len(copy_mappings),
        "copy_button_mappings": copy_mappings,
        "fallback_toggle_mappings": fallback_mappings,
        "interactive_functions": [
            name for name in PRESERVED_FUNCTIONS if name in functions
        ],
        "persistent_local_storage_keys": _persistent_storage_keys(text),
    }


def _strip_css_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote:
            result.append(char)
            if char == "\\" and index + 1 < len(text):
                index += 1
                result.append(text[index])
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            result.append(char)
            index += 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise CssParseError("unclosed CSS comment")
            result.append(" ")
            index = end + 2
            continue
        result.append(char)
        index += 1
    if quote:
        raise CssParseError("unclosed CSS string")
    return "".join(result)


def _matching_brace(text: str, start: int) -> int:
    depth = 1
    quote: str | None = None
    paren = 0
    bracket = 0
    index = start + 1
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\" and index + 1 < len(text):
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "(":
            paren += 1
        elif char == ")":
            if paren == 0:
                raise CssParseError("unmatched CSS parenthesis")
            paren -= 1
        elif char == "[":
            bracket += 1
        elif char == "]":
            if bracket == 0:
                raise CssParseError("unmatched CSS bracket")
            bracket -= 1
        elif char == "{" and paren == 0 and bracket == 0:
            depth += 1
        elif char == "}" and paren == 0 and bracket == 0:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise CssParseError("unclosed CSS block")


def _split_declarations(
    text: str,
    contexts: tuple[str, ...],
    source: str,
) -> list[CssDeclaration]:
    declarations: list[CssDeclaration] = []
    start = 0
    quote: str | None = None
    paren = 0
    bracket = 0
    index = 0

    def add_segment(segment: str) -> None:
        value = segment.strip()
        if not value:
            return
        if value.startswith("@"):
            return
        if ":" not in value:
            raise CssParseError(f"declaration lacks a colon: {value[:80]!r}")
        property_name, property_value = value.split(":", 1)
        property_name = property_name.strip()
        if not re.fullmatch(r"(?:--)?[-_a-zA-Z][-\w]*", property_name):
            raise CssParseError(
                f"invalid CSS property name: {property_name[:80]!r}"
            )
        if not property_value.strip():
            raise CssParseError(f"empty CSS value for {property_name}")
        declarations.append(
            CssDeclaration(
                contexts,
                property_name.lower(),
                property_value.strip(),
                source,
            )
        )

    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\" and index + 1 < len(text):
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "(":
            paren += 1
        elif char == ")":
            if paren == 0:
                raise CssParseError("unmatched CSS parenthesis")
            paren -= 1
        elif char == "[":
            bracket += 1
        elif char == "]":
            if bracket == 0:
                raise CssParseError("unmatched CSS bracket")
            bracket -= 1
        elif char in "{}" and paren == 0 and bracket == 0:
            raise CssParseError("unexpected CSS brace in declaration list")
        elif char == ";" and paren == 0 and bracket == 0:
            add_segment(text[start:index])
            start = index + 1
        index += 1
    if quote or paren or bracket:
        raise CssParseError("unclosed CSS string, parenthesis, or bracket")
    add_segment(text[start:])
    return declarations


def parse_css_stylesheet(text: str, source: str) -> list[CssDeclaration]:
    clean = _strip_css_comments(text)

    def walk(block: str, contexts: tuple[str, ...]) -> list[CssDeclaration]:
        declarations: list[CssDeclaration] = []
        plain_start = 0
        quote: str | None = None
        paren = 0
        bracket = 0
        index = 0
        while index < len(block):
            char = block[index]
            if quote:
                if char == "\\" and index + 1 < len(block):
                    index += 2
                    continue
                if char == quote:
                    quote = None
                index += 1
                continue
            if char in {'"', "'"}:
                quote = char
            elif char == "(":
                paren += 1
            elif char == ")":
                if paren == 0:
                    raise CssParseError("unmatched CSS parenthesis")
                paren -= 1
            elif char == "[":
                bracket += 1
            elif char == "]":
                if bracket == 0:
                    raise CssParseError("unmatched CSS bracket")
                bracket -= 1
            elif char == "}" and paren == 0 and bracket == 0:
                raise CssParseError("unmatched CSS closing brace")
            elif char == "{" and paren == 0 and bracket == 0:
                prelude = block[plain_start:index].strip()
                if not prelude:
                    raise CssParseError("CSS block has no selector or at-rule")
                close = _matching_brace(block, index)
                before = block[plain_start:index]
                if ";" in before:
                    last_semicolon = before.rfind(";")
                    declaration_text = before[: last_semicolon + 1]
                    declarations.extend(
                        _split_declarations(
                            declaration_text, contexts, source
                        )
                    )
                    prelude = before[last_semicolon + 1 :].strip()
                declarations.extend(
                    walk(block[index + 1 : close], contexts + (prelude,))
                )
                index = close + 1
                plain_start = index
                continue
            index += 1
        trailing = block[plain_start:].strip()
        if trailing:
            if contexts:
                declarations.extend(
                    _split_declarations(trailing, contexts, source)
                )
            elif not trailing.startswith("@"):
                raise CssParseError(
                    f"unexpected top-level CSS text: {trailing[:80]!r}"
                )
        if quote or paren or bracket:
            raise CssParseError("unclosed CSS string, parenthesis, or bracket")
        return declarations

    return walk(clean, ())


def parse_style_attribute(text: str, source: str) -> list[CssDeclaration]:
    clean = _strip_css_comments(text)
    return _split_declarations(clean, ("@style-attribute",), source)


def _normalize_css_value(value: str) -> str:
    normalized = " ".join(value.strip().lower().split())
    normalized = re.sub(r"\s*([(),/])\s*", r"\1", normalized)
    return normalized


def _last_selector(declaration: CssDeclaration) -> str:
    for context in reversed(declaration.contexts):
        if not context.lstrip().startswith("@"):
            return " ".join(context.split()).lower()
    return ""


def _theme_scope(declaration: CssDeclaration) -> str | None:
    if len(declaration.contexts) != 1:
        return None
    selector = " ".join(declaration.contexts[0].split()).lower()
    if selector == ":root":
        return "light"
    if re.fullmatch(
        r"""html\[data-theme\s*=\s*(['"])dark\1\]""", selector
    ):
        return "dark"
    return None


def _has_color_literal(value: str) -> bool:
    if HEX_COLOR_RE.search(value) or COLOR_FUNCTION_RE.search(value):
        return True
    words = set(re.findall(r"(?i)\b[a-z]+\b", value))
    return bool({word.lower() for word in words} & COLOR_KEYWORDS)


def _validate_contract(
    contract: Any,
    failures: FailureCollector,
) -> dict[str, Any] | None:
    if not isinstance(contract, dict):
        failures.add("contract.schema", "contract root must be an object")
        return None
    if contract.get("schema") != CONTRACT_SCHEMA:
        failures.add(
            "contract.schema",
            f"expected schema {CONTRACT_SCHEMA!r}",
        )
    if contract.get("version") != 1:
        failures.add("contract.schema", "expected contract version 1")
    if contract.get("trusted_source_commit") != TRUSTED_SOURCE_COMMIT:
        failures.add(
            "baseline.metadata",
            "trusted_source_commit does not match the immutable approved commit",
        )
    if contract.get("trusted_source_blob_oid") != TRUSTED_SOURCE_BLOB_OID:
        failures.add(
            "baseline.metadata",
            "trusted_source_blob_oid does not match the immutable approved blob",
        )
    sections = contract.get("content_sections")
    if not isinstance(sections, list) or len(sections) != 21:
        failures.add(
            "contract.sections",
            "contract must contain exactly 21 content section records",
        )
        return contract
    ids = [record.get("id") for record in sections if isinstance(record, dict)]
    if ids != list(CONTENT_SECTION_IDS):
        failures.add(
            "contract.sections",
            "contract section IDs are not the required ordered 21-section set",
        )
    explicit_ids = contract.get("content_section_ids")
    if explicit_ids is not None and explicit_ids != ids:
        failures.add(
            "contract.sections",
            "content_section_ids does not match content_sections order",
        )
    for record in sections:
        digest = (
            record.get("normalized_visible_text_sha256")
            if isinstance(record, dict)
            else None
        )
        if not isinstance(digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", digest
        ):
            failures.add(
                "contract.sections",
                "every content section requires a lowercase SHA-256 digest",
            )
            break
    for key in (
        "sidebar_links",
        "external_hrefs",
        "content_external_links",
        "quiz_ids",
        "quizzes",
        "copy_button_mappings",
        "fallback_toggle_mappings",
        "interactive_functions",
        "persistent_local_storage_keys",
    ):
        if not isinstance(contract.get(key), list):
            failures.add("contract.schema", f"{key} must be an array")
    if not isinstance(contract.get("copy_button_count"), int):
        failures.add(
            "contract.schema", "copy_button_count must be an integer"
        )
    elif contract.get("copy_button_count") != len(
        contract.get("copy_button_mappings", [])
    ):
        failures.add(
            "contract.schema",
            "copy_button_count must equal copy_button_mappings length",
        )
    return contract


def _check_contract_against_baseline(
    contract: dict[str, Any],
    baseline_text: str | None,
    failures: FailureCollector,
) -> None:
    if baseline_text is None:
        failures.add(
            "baseline.source",
            "the immutable trusted source blob was not provided; failing closed",
        )
        return
    source = contract.get("source")
    if not isinstance(source, str) or not source:
        failures.add(
            "contract.schema",
            "source must identify the trusted guide path",
        )
        return
    expected = build_content_contract_from_text(
        baseline_text,
        source,
        trusted_source_commit=TRUSTED_SOURCE_COMMIT,
        trusted_source_blob_oid=TRUSTED_SOURCE_BLOB_OID,
    )
    if contract != expected:
        mismatches = [
            key
            for key in sorted(set(contract) | set(expected))
            if contract.get(key) != expected.get(key)
        ]
        failures.add(
            "baseline.contract",
            "checked-in contract does not exactly match evidence reconstructed "
            "from the trusted blob; mismatched fields: "
            + ", ".join(mismatches[:12]),
        )


def _git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def _load_trusted_baseline(
    guide_path: Path,
    contract: dict[str, Any],
    failures: FailureCollector,
) -> str | None:
    if shutil.which("git") is None:
        failures.add(
            "baseline.source",
            "git is unavailable; the trusted source blob cannot be verified",
        )
        return None
    if contract.get("source") != TRUSTED_SOURCE_PATH:
        failures.add(
            "baseline.metadata",
            f"contract source must be {TRUSTED_SOURCE_PATH!r}",
        )
        return None
    try:
        repo_text = _git_output(
            guide_path.parent,
            "rev-parse",
            "--show-toplevel",
        ).strip()
        if not repo_text:
            raise RuntimeError("repository root was empty")
        repo = Path(repo_text)
        resolved_oid = _git_output(
            repo,
            "rev-parse",
            f"{TRUSTED_SOURCE_COMMIT}:{TRUSTED_SOURCE_PATH}",
        ).strip()
        if resolved_oid != TRUSTED_SOURCE_BLOB_OID:
            raise RuntimeError(
                "trusted commit:path resolved to "
                f"{resolved_oid!r}, expected {TRUSTED_SOURCE_BLOB_OID!r}"
            )
        object_type = _git_output(
            repo,
            "cat-file",
            "-t",
            TRUSTED_SOURCE_BLOB_OID,
        ).strip()
        if object_type != "blob":
            raise RuntimeError(
                f"trusted object type is {object_type!r}, expected 'blob'"
            )
        baseline_text = _git_output(
            repo,
            "cat-file",
            "blob",
            TRUSTED_SOURCE_BLOB_OID,
        )
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        failures.add(
            "baseline.source",
            f"trusted source baseline could not be verified: {exc}",
        )
        return None
    return baseline_text


def _check_inline_scripts(
    soup: BeautifulSoup,
    failures: FailureCollector,
    node_path: str | None,
) -> int:
    scripts = [
        script
        for script in soup.find_all("script")
        if not script.get("src")
        and (
            not script.get("type")
            or script.get("type", "").lower()
            in {
                "text/javascript",
                "application/javascript",
                "module",
            }
        )
        and _script_text(script).strip()
    ]
    if not node_path:
        failures.add(
            "behavior.javascript",
            "node is unavailable; inline scripts cannot be parsed",
        )
        return 0
    checked = 0
    for index, script in enumerate(scripts, start=1):
        checked += 1
        try:
            result = subprocess.run(
                [node_path, "--check", "-"],
                input=_script_text(script),
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            failures.add(
                "behavior.javascript",
                f"inline script {index} could not be checked: {exc}",
            )
            continue
        if result.returncode != 0:
            detail = next(
                (
                    line.strip()
                    for line in result.stderr.splitlines()
                    if line.strip()
                ),
                f"node exited {result.returncode}",
            )
            failures.add(
                "behavior.javascript",
                f"inline script {index} is malformed: {detail}",
            )
    return checked


def _check_shell_links(
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    allowed_fragments = {"#mainContent"} | {
        f"#{section_id}" for section_id in CONTENT_SECTION_IDS
    }
    unexpected = []
    for link in soup.select("a[href]"):
        if link.find_parent(class_="content-section") or link.find_parent(
            id="sidebar"
        ):
            continue
        href = link.get("href", "")
        label = normalized_visible_text(link)
        if href in allowed_fragments:
            continue
        if (label, href) in SHELL_INTERNAL_LINK_ALLOWLIST:
            continue
        parsed = urlsplit(href)
        if (
            parsed.scheme == "https"
            and parsed.netloc == "github.com"
            and parsed.path in SHELL_GITHUB_ISSUES_PATHS
        ):
            continue
        unexpected.append(f"{label!r} -> {href!r}")
    if unexpected:
        failures.add(
            "content.shell_links",
            "shell links are limited to guide fragments, Library, Workshop "
            "settings, and GitHub issues feedback: "
            + "; ".join(unexpected[:4]),
        )


def _check_content(
    text: str,
    soup: BeautifulSoup,
    contract: dict[str, Any],
    failures: FailureCollector,
) -> dict[str, Any]:
    section_nodes = soup.select(".content-section")
    section_ids = [section.get("id") for section in section_nodes]
    expected_records_value = contract.get("content_sections")
    expected_records = (
        expected_records_value
        if isinstance(expected_records_value, list)
        else []
    )
    expected_ids = [
        record.get("id")
        for record in expected_records
        if isinstance(record, dict)
    ]
    if section_ids != expected_ids or len(section_ids) != 21:
        failures.add(
            "content.sections",
            "content sections must exactly match the contracted 21 IDs in order",
        )
    expected_hashes = {
        record.get("id"): record.get("normalized_visible_text_sha256")
        for record in expected_records
        if isinstance(record, dict)
    }
    drifted = []
    for section in section_nodes:
        section_id = section.get("id")
        digest = sha256(
            normalized_visible_text(section).encode("utf-8")
        ).hexdigest()
        if section_id in expected_hashes and digest != expected_hashes[section_id]:
            drifted.append(section_id)
    if drifted:
        failures.add(
            "content.text",
            "normalized visible text drifted in: " + ", ".join(drifted),
        )
    steps = [section_id for section_id in section_ids if re.fullmatch(
        r"step\d+", section_id or ""
    )]
    expected_steps = [f"step{number}" for number in range(1, 15)]
    if steps != expected_steps:
        failures.add(
            "content.steps",
            "the complete ordered step1 through step14 sequence is required",
        )

    actual_sidebar = _extract_sidebar_links(soup)
    sidebar_value = contract.get("sidebar_links")
    sidebar_records = sidebar_value if isinstance(sidebar_value, list) else []
    if actual_sidebar != sidebar_records:
        failures.add(
            "content.sidebar",
            "sidebar link labels and hrefs must exactly match the trusted "
            "ordered list",
        )

    actual_content_external = _extract_content_external_links(soup)
    expected_content_external_value = contract.get("content_external_links")
    expected_content_external = (
        expected_content_external_value
        if isinstance(expected_content_external_value, list)
        else []
    )
    if actual_content_external != expected_content_external:
        failures.add(
            "content.external_links",
            "external hrefs inside content sections must exactly match the "
            "trusted ordered list",
        )
    _check_shell_links(soup, failures)

    functions = set(FUNCTION_RE.findall(text))
    functions_value = contract.get("interactive_functions")
    required_functions = set(
        functions_value if isinstance(functions_value, list) else []
    )
    missing_functions = sorted(required_functions - functions)
    if missing_functions:
        failures.add(
            "behavior.functions",
            "contracted functions are missing: " + ", ".join(missing_functions),
        )

    expected_quizzes_value = contract.get("quizzes")
    expected_quizzes = (
        expected_quizzes_value
        if isinstance(expected_quizzes_value, list)
        else []
    )
    actual_quizzes = _extract_quizzes(text, soup)
    if actual_quizzes != expected_quizzes:
        failures.add(
            "behavior.quiz",
            "quiz IDs, option order/text, correct index, feedback attributes, "
            "review target, and completion key must exactly match the trusted "
            "semantics",
        )
    expected_quiz_ids = [
        quiz.get("id")
        for quiz in expected_quizzes
        if isinstance(quiz, dict)
    ]
    actual_quiz_ids = [
        quiz.get("id")
        for quiz in actual_quizzes
        if isinstance(quiz, dict)
    ]
    if contract.get("quiz_ids") != expected_quiz_ids:
        failures.add(
            "contract.schema",
            "quiz_ids must match the ordered quizzes records",
        )

    actual_storage = _persistent_storage_keys(text)
    storage_value = contract.get("persistent_local_storage_keys")
    expected_storage = (
        storage_value if isinstance(storage_value, list) else []
    )
    if actual_storage != expected_storage:
        failures.add(
            "behavior.storage",
            "persistent localStorage keys must exactly match the trusted list",
        )

    actual_copy_mappings = _extract_copy_mappings(soup)
    expected_copy_mappings_value = contract.get("copy_button_mappings")
    expected_copy_mappings = (
        expected_copy_mappings_value
        if isinstance(expected_copy_mappings_value, list)
        else []
    )
    copy_count = len(actual_copy_mappings)
    expected_copy_count = contract.get("copy_button_count", 0)
    if (
        not isinstance(expected_copy_count, int)
        or copy_count != expected_copy_count
        or actual_copy_mappings != expected_copy_mappings
    ):
        failures.add(
            "behavior.copy",
            "copy buttons and their ordered code/pre target text hashes must "
            "exactly match the trusted mappings",
        )

    actual_fallback_mappings = _extract_fallback_mappings(soup)
    expected_fallback_mappings_value = contract.get(
        "fallback_toggle_mappings"
    )
    expected_fallback_mappings = (
        expected_fallback_mappings_value
        if isinstance(expected_fallback_mappings_value, list)
        else []
    )
    if actual_fallback_mappings != expected_fallback_mappings:
        failures.add(
            "behavior.fallback",
            "fallback toggle labels, aria-controls/targets, text hashes, and "
            "initial hidden states must exactly match the trusted mappings",
        )

    noscript = soup.find("noscript")
    noscript_text = normalized_visible_text(noscript) if noscript else ""
    if not re.search(r"\b21\s+sections?\b", noscript_text, re.IGNORECASE):
        failures.add(
            "behavior.noscript",
            "no-JS content must explicitly say all 21 sections are visible",
        )

    if not (
        {"navigateToSection", "handleHashNavigation"} <= functions
        and "hashchange" in text
        and re.search(r"(?:window\.)?location\.hash", text)
    ):
        failures.add(
            "behavior.hash",
            "hash/deep-link navigation handlers are not measurable",
        )
    if not (
        {"nextSection", "previousSection"} <= functions
        and soup.select('[onclick*="nextSection"]')
        and soup.select('[onclick*="previousSection"]')
    ):
        failures.add(
            "behavior.previous_next",
            "previous/next controls and handlers are required",
        )
    if not (
        "keydown" in text
        and "ArrowLeft" in text
        and "ArrowRight" in text
        and {"nextSection", "previousSection"} <= functions
    ):
        failures.add(
            "behavior.keyboard",
            "left/right keyboard navigation is not measurable",
        )
    if not (
        "toggleSidebar" in functions
        and soup.select_one("#sidebar")
        and soup.select(
            '[onclick*="toggleSidebar"], [data-sidebar-toggle], '
            '[aria-controls="sidebar"]'
        )
    ):
        failures.add(
            "behavior.sidebar",
            "sidebar markup, control, and handler are required",
        )
    if not (
        {"toggleQuiz", "selectQuizOption", "submitQuiz"} <= functions
        and actual_quizzes == expected_quizzes
        and soup.select('[onclick*="toggleQuiz"], [data-quiz-toggle]')
    ):
        failures.add(
            "behavior.quiz",
            "quiz controls and handlers are not measurable",
        )
    if not (
        "copyCode" in functions
        and copy_count == expected_copy_count
        and soup.select(
            '[onclick*="copyCode"], [data-copy-button]'
        )
    ):
        failures.add(
            "behavior.copy",
            "copy controls and handler are not measurable",
        )
    if not (
        "toggleFallback" in functions
        and soup.select(
            '[onclick*="toggleFallback"], [data-fallback-toggle]'
        )
    ):
        failures.add(
            "behavior.fallback",
            "fallback controls and handler are not measurable",
        )
    return {
        "content_sections": len(section_nodes),
        "sidebar_links": len(actual_sidebar),
        "content_external_hrefs": len(actual_content_external),
        "quiz_ids": actual_quiz_ids,
        "copy_buttons": copy_count,
        "fallback_toggles": len(actual_fallback_mappings),
        "functions": sorted(functions),
        "persistent_local_storage_keys": actual_storage,
    }


def _collect_css(
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> list[CssDeclaration]:
    declarations: list[CssDeclaration] = []
    for index, style in enumerate(soup.find_all("style"), start=1):
        try:
            declarations.extend(
                parse_css_stylesheet(
                    style.get_text(),
                    f"style block {index}",
                )
            )
        except CssParseError as exc:
            failures.add(
                "css.parse",
                f"style block {index} cannot be measured: {exc}",
            )
    for index, node in enumerate(soup.select("[style]"), start=1):
        description = node.name
        if node.get("id"):
            description += f"#{node.get('id')}"
        try:
            declarations.extend(
                parse_style_attribute(
                    node.get("style", ""),
                    f"style attribute {index} on {description}",
                )
            )
        except CssParseError as exc:
            failures.add(
                "css.parse",
                f"style attribute {index} cannot be measured: {exc}",
            )
    if not soup.find("style"):
        failures.add("css.parse", "no inline stylesheet was found")
    return declarations


def _css_value_without_important(value: str) -> str:
    return re.sub(r"\s*!important\s*$", "", value, flags=re.IGNORECASE).strip()


def _last_no_js_value(
    declarations: list[CssDeclaration],
    selector_marker: str,
    property_name: str,
) -> str | None:
    values = [
        declaration.value
        for declaration in declarations
        if declaration.property == property_name
        and "body:not(.js-enabled)" in _last_selector(declaration)
        and selector_marker in _last_selector(declaration)
    ]
    return values[-1] if values else None


def _no_js_values_for_node(
    soup: BeautifulSoup,
    node: Tag,
    declarations: list[CssDeclaration],
    property_name: str,
) -> list[str]:
    values = []
    for declaration in declarations:
        if declaration.property != property_name:
            continue
        selector_group = _last_selector(declaration)
        for selector in selector_group.split(","):
            if "body:not(.js-enabled)" not in selector:
                continue
            measurable_selector = selector.replace(
                "body:not(.js-enabled)",
                "body",
            ).strip()
            try:
                if node in soup.select(measurable_selector):
                    values.append(declaration.value)
                    break
            except Exception:
                continue
    return values


def _check_no_js_semantics(
    soup: BeautifulSoup,
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    content_display = _last_no_js_value(
        declarations, ".content-section", "display"
    )
    if _css_value_without_important(content_display or "") != "block":
        failures.add(
            "behavior.no_js",
            "no-JS CSS must make every content section display:block",
        )
    hidden_sections = [
        section.get("id")
        for section in soup.select(".content-section")
        if any(
            _css_value_without_important(value) == "none"
            for value in _no_js_values_for_node(
                soup,
                section,
                declarations,
                "display",
            )
        )
    ]
    if hidden_sections:
        failures.add(
            "behavior.no_js",
            "no-JS CSS contains contradictory display:none rules for content "
            "sections: "
            + ", ".join(str(section_id) for section_id in hidden_sections[:4]),
        )

    fallback_display = _last_no_js_value(
        declarations, ".fallback-content[hidden]", "display"
    )
    if (
        _css_value_without_important(fallback_display or "") != "block"
        or "!important" not in (fallback_display or "").lower()
    ):
        failures.add(
            "behavior.no_js",
            "no-JS CSS must override hidden fallback content with "
            "display:block !important",
        )
    hidden_fallbacks = [
        node.get("id")
        for node in soup.select(".fallback-content[hidden]")
        if any(
            _css_value_without_important(value) == "none"
            for value in _no_js_values_for_node(
                soup,
                node,
                declarations,
                "display",
            )
        )
    ]
    if hidden_fallbacks:
        failures.add(
            "behavior.no_js",
            "no-JS CSS contains contradictory hidden fallback rules: "
            + ", ".join(str(node_id) for node_id in hidden_fallbacks[:4]),
        )

    hidden_controls = (
        ".js-control",
        ".nav-controls",
        ".copy-btn",
        ".fallback-header",
        ".gut-check-toggle",
        ".quiz-submit",
        ".sidebar-close",
        ".sidebar-scrim",
    )
    visible_controls = [
        marker
        for marker in hidden_controls
        if _css_value_without_important(
            _last_no_js_value(declarations, marker, "display") or ""
        )
        != "none"
    ]
    if visible_controls:
        failures.add(
            "behavior.no_js",
            "no-JS CSS must hide navigation/copy/quiz/sidebar controls: "
            + ", ".join(visible_controls),
        )
    controls = soup.select(
        ".js-control, .nav-controls, .copy-btn, .fallback-header, "
        ".gut-check-toggle, .quiz-submit, .sidebar-close, .sidebar-scrim"
    )
    contradicted_controls = [
        normalized_visible_text(control)[:40] or control.name
        for control in controls
        if any(
            _css_value_without_important(value) != "none"
            for value in _no_js_values_for_node(
                soup,
                control,
                declarations,
                "display",
            )
        )
    ]
    if contradicted_controls:
        failures.add(
            "behavior.no_js",
            "no-JS CSS contains contradictory visible control rules: "
            + ", ".join(contradicted_controls[:4]),
        )

    sidebar_position = _last_no_js_value(
        declarations, "#sidebar", "position"
    )
    sidebar_transform = _last_no_js_value(
        declarations, "#sidebar", "transform"
    )
    sidebar_width = _last_no_js_value(declarations, "#sidebar", "width")
    if (
        _css_value_without_important(sidebar_position or "") != "static"
        or _css_value_without_important(sidebar_transform or "") != "none"
        or _css_value_without_important(sidebar_width or "")
        not in {"auto", "100%"}
    ):
        failures.add(
            "behavior.no_js",
            "no-JS sidebar must be static, non-offscreen, and use an "
            "in-flow width",
        )
    contradictory_sidebar = [
        f"{declaration.property}: {declaration.value}"
        for declaration in declarations
        if "body:not(.js-enabled)" in _last_selector(declaration)
        and "#sidebar" in _last_selector(declaration)
        and (
            (
                declaration.property in {"left", "right", "inset", "inset-inline"}
                and re.search(r"-\s*\d", declaration.value)
            )
            or (
                declaration.property == "transform"
                and "translate" in declaration.value.lower()
            )
        )
    ]
    if contradictory_sidebar:
        failures.add(
            "behavior.no_js",
            "no-JS sidebar has contradictory offscreen declarations: "
            + "; ".join(contradictory_sidebar[:3]),
        )


def _matching_javascript_delimiter(
    text: str,
    start: int,
    opening: str,
    closing: str,
) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = start
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        if char in {"'", '"', "`"}:
            quote = char
            index += 1
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _matching_javascript_brace(text: str, start: int) -> int | None:
    return _matching_javascript_delimiter(text, start, "{", "}")


def _javascript_function_source(text: str, name: str) -> str:
    match = re.search(
        rf"\bfunction\s+{re.escape(name)}\s*\(",
        text,
    )
    if not match:
        return ""
    parameter_start = text.find("(", match.start())
    depth = 0
    quote: str | None = None
    escaped = False
    parameter_end = None
    for index in range(parameter_start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                parameter_end = index
                break
    if parameter_end is None:
        return ""
    start = text.find("{", parameter_end)
    if start < 0:
        return ""
    end = _matching_javascript_brace(text, start)
    return text[match.start() : end + 1] if end is not None else ""


def _split_javascript_arguments(source: str) -> list[str]:
    arguments: list[str] = []
    start = 0
    depths = {"(": 0, "[": 0, "{": 0}
    pairs = {")": "(", "]": "[", "}": "{"}
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = 0
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char in depths:
            depths[char] += 1
        elif char in pairs:
            depths[pairs[char]] -= 1
        elif char == "," and not any(depths.values()):
            arguments.append(source[start:index].strip())
            start = index + 1
        index += 1
    tail = source[start:].strip()
    if tail:
        arguments.append(tail)
    return arguments


def _javascript_function_parameters(source: str) -> list[str]:
    declaration = re.search(r"\bfunction\s+[A-Za-z_$][\w$]*\s*\(", source)
    if not declaration:
        return []
    start = source.find("(", declaration.start())
    end = _matching_javascript_delimiter(source, start, "(", ")")
    if end is None:
        return []
    return _split_javascript_arguments(source[start + 1 : end])


def _javascript_calls(
    source: str,
    call_name: str,
) -> list[tuple[int, int, list[str]]]:
    calls: list[tuple[int, int, list[str]]] = []
    pattern = re.compile(
        rf"(?<![\w$]){re.escape(call_name)}\s*\("
    )
    position = 0
    while match := pattern.search(source, position):
        start = source.find("(", match.start())
        end = _matching_javascript_delimiter(source, start, "(", ")")
        if end is None:
            break
        calls.append(
            (
                match.start(),
                end + 1,
                _split_javascript_arguments(source[start + 1 : end]),
            )
        )
        position = end + 1
    return calls


def _javascript_block_after_pattern(
    source: str,
    pattern: str,
) -> tuple[int, int, str] | None:
    match = re.search(pattern, source)
    if not match:
        return None
    start = source.find("{", match.end())
    if start < 0:
        return None
    end = _matching_javascript_brace(source, start)
    if end is None:
        return None
    return start, end + 1, source[start : end + 1]


def _javascript_identifier(parameter: str) -> str | None:
    match = re.match(r"\s*([A-Za-z_$][\w$]*)", parameter)
    return match.group(1) if match else None


def _compact_javascript(source: str) -> str:
    return re.sub(r"\s+", "", source)


def _javascript_array_values(
    text: str,
    variable_name: str,
) -> list[str] | None:
    match = re.search(
        rf"\b(?:const|let|var)\s+{re.escape(variable_name)}\s*=\s*\[",
        text,
    )
    if not match:
        return None
    start = text.find("[", match.start())
    end = _matching_javascript_delimiter(text, start, "[", "]")
    if end is None:
        return None
    literal = text[start + 1 : end]
    values = [
        string.group(2)
        for string in re.finditer(r"""(['"])([^'"]*)\1""", literal)
    ]
    residue = re.sub(r"""(['"])([^'"]*)\1""", "", literal)
    if re.sub(r"[\s,]", "", residue):
        return None
    return values


def _check_copy_semantics(
    text: str,
    failures: FailureCollector,
) -> None:
    source = _javascript_function_source(text, "copyCode")
    parameters = _javascript_function_parameters(source)
    parameter = _javascript_identifier(parameters[0]) if parameters else None
    receivers = set(re.findall(
        r"\b([A-Za-z_$][\w$]*)\.textContent\b",
        source,
    ))
    target_receivers = {
        receiver
        for receiver in receivers
        if parameter
        and (
            receiver == parameter
            or re.search(
                rf"\b{re.escape(receiver)}\s*=\s*[^;]*"
                rf"\b{re.escape(parameter)}\b",
                source,
            )
        )
    }
    payloads = {
        f"{receiver}.textContent" for receiver in target_receivers
    }
    for alias, receiver in re.findall(
        r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
        r"([A-Za-z_$][\w$]*)\.textContent\s*;",
        source,
    ):
        if receiver in target_receivers:
            payloads.add(alias)

    write_calls = _javascript_calls(source, "navigator.clipboard.writeText")
    fallback_calls = _javascript_calls(source, "fallbackCopy")
    copy_calls = write_calls + fallback_calls
    exact_payload = bool(payloads and write_calls and fallback_calls)
    for _, _, arguments in copy_calls:
        if (
            not arguments
            or _compact_javascript(arguments[0])
            not in {_compact_javascript(payload) for payload in payloads}
        ):
            exact_payload = False

    success_calls = [
        call
        for call in _javascript_calls(source, "announceStatus")
        if call[2]
        and re.search(r"cop(?:y|ied)", call[2][0], re.IGNORECASE)
        and not re.search(r"fail", call[2][0], re.IGNORECASE)
    ]
    success_after_copy = bool(
        copy_calls
        and success_calls
        and all(
            start > max(call[1] for call in copy_calls)
            for start, _, _ in success_calls
        )
    )
    if not exact_payload or not success_after_copy:
        failures.add(
            "behavior.copy",
            "copyCode must derive one payload from the targeted code block's "
            "textContent, pass that exact payload to clipboard and fallback "
            "copy paths, and announce success only after copying",
        )


def _check_fallback_semantics(
    text: str,
    failures: FailureCollector,
) -> None:
    source = _javascript_function_source(text, "toggleFallback")
    parameters = _javascript_function_parameters(source)
    parameter = _javascript_identifier(parameters[0]) if parameters else None
    target_match = (
        re.search(
            rf"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
            rf"document\.getElementById\(\s*{re.escape(parameter)}\s*\)",
            source,
        )
        if parameter
        else None
    )
    target = target_match.group(1) if target_match else None
    state_match = (
        re.search(
            rf"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
            rf"{re.escape(target)}\.hidden\s*;",
            source,
        )
        if target
        else None
    )
    state = state_match.group(1) if state_match else None
    toggle_match = re.search(
        r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
        r"document\.querySelector\(",
        source,
    )
    toggle = toggle_match.group(1) if toggle_match else None
    compact = _compact_javascript(source)
    changes_hidden = bool(
        target
        and state
        and f"{target}.hidden=!{state};" in compact
    )
    synchronizes_aria = bool(
        toggle
        and state
        and re.search(
            rf"""{re.escape(toggle)}\.setAttribute\(\s*['"]aria-expanded"""
            rf"""['"]\s*,\s*String\(\s*{re.escape(state)}\s*\)\s*\)""",
            source,
        )
    )
    updates_label = bool(
        toggle
        and f"{toggle}.textContent" in compact
        and "Click to expand" in source
        and "Click to collapse" in source
        and state
        and re.search(rf"\b{re.escape(state)}\b", source)
    )
    if not (changes_hidden and synchronizes_aria and updates_label):
        failures.add(
            "behavior.fallback",
            "toggleFallback must invert the target hidden state, synchronize "
            "aria-expanded, and switch the expand/collapse label",
        )


def _check_quiz_semantics(
    text: str,
    failures: FailureCollector,
) -> None:
    source = _javascript_function_source(text, "submitQuiz")
    correct_expression = bool(re.search(
        r"\b(?:const|let|var)\s+isCorrect\s*=\s*"
        r"selectedIndex\s*===\s*correctAnswer\s*;",
        source,
    ))
    correct_class = bool(re.search(
        r"""if\s*\(\s*index\s*===\s*correctAnswer\s*\)"""
        r"""[\s\S]{0,160}?classList\.add\(\s*['"]correct['"]\s*\)""",
        source,
    ))
    incorrect_class = bool(re.search(
        r"""if\s*\(\s*index\s*===\s*selectedIndex\s*&&\s*!isCorrect\s*\)"""
        r"""[\s\S]{0,160}?classList\.add\(\s*['"]incorrect['"]\s*\)""",
        source,
    ))
    correct_block = _javascript_block_after_pattern(
        source,
        r"if\s*\(\s*isCorrect\s*\)",
    )
    persistence_ok = False
    if correct_block:
        block_start, block_end, block_source = correct_block
        completion_assignment = re.search(
            r"\b[A-Za-z_$][\w$]*\s*\[\s*quizId\s*\]\s*=\s*true\s*;",
            block_source,
        )
        persistence_calls = (
            _javascript_calls(source, "saveQuizCompletion")
            + _javascript_calls(source, "localStorage.setItem")
        )
        calls_are_guarded = bool(persistence_calls) and all(
            block_start <= start and end <= block_end
            for start, end, _ in persistence_calls
        )
        direct_key = any(
            arguments
            and arguments[0].strip().strip("'\"") == "quiz-completed"
            for _, _, arguments in _javascript_calls(
                block_source,
                "localStorage.setItem",
            )
        )
        save_source = _javascript_function_source(
            text,
            "saveQuizCompletion",
        )
        helper_key = bool(
            _javascript_calls(block_source, "saveQuizCompletion")
            and re.search(
                r"""localStorage\.setItem\(\s*['"]quiz-completed['"]""",
                save_source,
            )
        )
        persistence_ok = bool(
            completion_assignment
            and calls_are_guarded
            and (direct_key or helper_key)
        )
    if not (
        correct_expression
        and correct_class
        and incorrect_class
        and persistence_ok
    ):
        failures.add(
            "behavior.quiz",
            "submitQuiz must use selectedIndex === correctAnswer, mark the "
            "correct and selected incorrect options, and persist "
            "quiz-completed only inside the correct branch",
        )


def _first_call_argument(source: str, call_name: str) -> str | None:
    calls = _javascript_calls(source, call_name)
    if not calls or not calls[0][2]:
        return None
    return _compact_javascript(calls[0][2][0])


def _check_mobile_inert_semantics(
    text: str,
    failures: FailureCollector,
) -> None:
    inert_source = _javascript_function_source(
        text,
        "setMobileBackgroundInert",
    )
    parameters = _javascript_function_parameters(inert_source)
    parameter = _javascript_identifier(parameters[0]) if parameters else None
    assignments = re.findall(
        r"\b[A-Za-z_$][\w$]*\.inert\s*=\s*([^;\n}]+)",
        inert_source,
    )
    assigns_argument = bool(
        parameter
        and assignments
        and all(
            _compact_javascript(value) == parameter
            for value in assignments
        )
    )
    toggle_source = _javascript_function_source(text, "toggleSidebar")
    close_source = _javascript_function_source(text, "closeMobileSidebar")
    sync_source = _javascript_function_source(
        text,
        "syncSidebarForViewport",
    )
    paths_are_synchronized = (
        _first_call_argument(
            toggle_source,
            "setMobileBackgroundInert",
        )
        == "shouldOpen"
        and _first_call_argument(
            close_source,
            "setMobileBackgroundInert",
        )
        == "false"
        and _first_call_argument(
            sync_source,
            "setMobileBackgroundInert",
        )
        == "false"
    )
    if not (assigns_argument and paths_are_synchronized):
        failures.add(
            "behavior.mobile_drawer",
            "setMobileBackgroundInert must assign target.inert from its "
            "argument, with open, close, and viewport-sync paths passing the "
            "current drawer state or false",
        )


def _check_feedback_context_semantics(
    text: str,
    failures: FailureCollector,
) -> None:
    update_source = _javascript_function_source(
        text,
        "updateReportIssueLink",
    )
    parameters = _javascript_function_parameters(update_source)
    default_is_current = bool(
        parameters
        and re.fullmatch(
            r"\s*sectionId\s*=\s*sections\s*\[\s*currentSectionIndex\s*\]\s*",
            parameters[0],
        )
    )
    body_has_section = False
    for _, _, arguments in _javascript_calls(
        update_source,
        "issueUrl.searchParams.set",
    ):
        if (
            len(arguments) >= 2
            and arguments[0].strip().strip("'\"") == "body"
            and re.search(r"\bsectionId\b", arguments[1])
        ):
            body_has_section = True
            break
    navigate_source = _javascript_function_source(
        text,
        "navigateToSection",
    )
    destination_context = (
        _first_call_argument(
            navigate_source,
            "updateReportIssueLink",
        )
        == "sectionId"
    )
    if not (default_is_current and body_has_section and destination_context):
        failures.add(
            "theme.feedback",
            "feedback must default to the current section, include sectionId "
            "in the issue body, and refresh with navigateToSection's "
            "destination",
        )


def _check_navigation_reachability(
    text: str,
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    array_values = _javascript_array_values(text, "sections")
    next_source = _javascript_function_source(text, "nextSection")
    previous_source = _javascript_function_source(text, "previousSection")
    next_compact = _compact_javascript(next_source)
    previous_compact = _compact_javascript(previous_source)
    next_is_adjacent = (
        "currentSectionIndex<sections.length-1" in next_compact
        and "navigateToSection(sections[currentSectionIndex+1])"
        in next_compact
    )
    previous_is_adjacent = (
        "currentSectionIndex>0" in previous_compact
        and "navigateToSection(sections[currentSectionIndex-1])"
        in previous_compact
    )
    global_navigation = any(
        control.find_parent(class_="content-section") is None
        and control.select_one('[onclick*="previousSection"]')
        and control.select_one('[onclick*="nextSection"]')
        for control in soup.select(".global-nav-controls, .nav-controls")
    )
    if not (
        array_values == list(CONTENT_SECTION_IDS)
        and next_is_adjacent
        and previous_is_adjacent
        and global_navigation
    ):
        failures.add(
            "behavior.previous_next",
            "previous/next navigation must use bounded adjacent entries from "
            "the complete 21-section array, including global controls",
        )


def _check_progress_semantics(
    text: str,
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    source = _javascript_function_source(text, "updateProgress")
    width_match = re.search(
        r"""querySelectorAll\(\s*(['"])\.progress-fill\1\s*\)"""
        r"""\.forEach\(\s*([A-Za-z_$][\w$]*)\s*=>\s*\{"""
        r"""[\s\S]*?\2\.style\.width\s*=\s*([^;]+)""",
        source,
    )
    aria_match = re.search(
        r"""querySelectorAll\(\s*(['"])\[role=["']progressbar["']\]\1\s*\)"""
        r"""\.forEach\(\s*([A-Za-z_$][\w$]*)\s*=>\s*\{"""
        r"""[\s\S]*?\2\.setAttribute\(\s*['"]aria-valuenow['"]\s*,"""
        r"""\s*([^)]+\([^;]+|[^;]+)\);""",
        source,
    )
    width_is_progress = bool(
        width_match
        and "progress" in width_match.group(3)
        and "%" in width_match.group(3)
    )
    aria_is_progress = bool(
        aria_match and "progress" in aria_match.group(3)
    )
    if not (
        soup.select_one('[role="progressbar"]')
        and width_is_progress
        and aria_is_progress
    ):
        failures.add(
            "behavior.progress",
            "updateProgress must set progress-fill width and aria-valuenow on "
            "role=progressbar elements from the computed progress",
        )


def _check_static_behavior_semantics(
    text: str,
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    _check_copy_semantics(text, failures)
    _check_fallback_semantics(text, failures)
    _check_quiz_semantics(text, failures)
    _check_mobile_inert_semantics(text, failures)
    _check_feedback_context_semantics(text, failures)
    _check_navigation_reachability(text, soup, failures)
    _check_progress_semantics(text, soup, failures)


def _keydown_handler_source(text: str) -> str:
    match = re.search(
        r"""document\.addEventListener\(\s*['"]keydown['"]\s*,""",
        text,
    )
    if not match:
        return ""
    start = text.find("{", match.end())
    if start < 0:
        return ""
    end = _matching_javascript_brace(text, start)
    return text[match.start() : end + 1] if end is not None else ""


def _check_post_migration_interactions(
    text: str,
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    hash_source = _javascript_function_source(text, "handleHashNavigation")
    main_content_branch = re.search(
        r"""if\s*\(\s*hash\s*===\s*['"]mainContent['"]\s*\)"""
        r"""[\s\S]*?getElementById\(\s*['"]mainContent['"]\s*\)"""
        r"""[\s\S]*?\breturn\b""",
        hash_source,
    )
    if not main_content_branch:
        failures.add(
            "behavior.skip_link",
            "hash handling must exempt #mainContent and focus it without "
            "redirecting to a content section",
        )

    navigation_source = _javascript_function_source(text, "navigateToSection")
    if not (
        re.search(r"historyMode\s*=\s*['\"]push['\"]", navigation_source)
        and "history.pushState" in navigation_source
    ):
        failures.add(
            "behavior.history",
            "user section navigation must default to history.pushState",
        )
    for event_name in ("hashchange", "popstate"):
        if not re.search(
            rf"""addEventListener\(\s*['"]{event_name}['"]\s*,\s*handleHashNavigation""",
            text,
        ):
            failures.add(
                "behavior.history",
                f"{event_name} must invoke handleHashNavigation",
            )

    topbar = _find_topbar(soup)
    sidebar = soup.select_one("#sidebar")
    if (
        topbar is None
        or topbar.find_parent(class_="content-section") is not None
        or sidebar is None
        or sidebar.find_parent(class_="content-section") is not None
    ):
        failures.add(
            "behavior.global_navigation",
            "global topbar and sidebar navigation must remain outside content "
            "sections",
        )

    inert_source = _javascript_function_source(text, "setMobileBackgroundInert")
    toggle_source = _javascript_function_source(text, "toggleSidebar")
    close_source = _javascript_function_source(text, "closeMobileSidebar")
    keydown_source = _keydown_handler_source(text)
    if not (
        "mainContent" in inert_source
        and ".inert" in inert_source
        and "setMobileBackgroundInert(shouldOpen)" in toggle_source
        and "setMobileBackgroundInert(false)" in close_source
        and re.search(
            r"""event\.key\s*===\s*['"]Tab['"]""",
            keydown_source,
        )
        and "sidebar-open" in keydown_source
        and "event.preventDefault()" in keydown_source
    ):
        failures.add(
            "behavior.mobile_drawer",
            "mobile drawer must inert the background and trap focus while open",
        )
    escape_match = re.search(
        r"""if\s*\(\s*event\.key\s*===\s*['"]Escape['"]\s*\)\s*\{""",
        keydown_source,
    )
    escape_source = ""
    if escape_match:
        escape_start = keydown_source.find("{", escape_match.start())
        escape_end = _matching_javascript_brace(
            keydown_source,
            escape_start,
        )
        if escape_end is not None:
            escape_source = keydown_source[
                escape_match.start() : escape_end + 1
            ]
    if not (
        re.search(
            r"""classList\.contains\(\s*['"]sidebar-open['"]\s*\)""",
            escape_source,
        )
        and "closeMobileSidebar" in escape_source
    ):
        failures.add(
            "behavior.mobile_drawer",
            "Escape may close the drawer only when sidebar-open is active",
        )
    if not (
        ".table-wrap" in keydown_source
        and '[role="region"]' in keydown_source
        and "ArrowRight" in keydown_source
        and "ArrowLeft" in keydown_source
    ):
        failures.add(
            "behavior.keyboard",
            "arrow section shortcuts must exclude table-wrap and role=region "
            "interaction regions",
        )


def _check_theme_script(
    soup: BeautifulSoup,
    failures: FailureCollector,
) -> None:
    head = soup.find("head")
    scripts = head.find_all("script") if head else []
    if not scripts:
        failures.add(
            "theme.scout_script",
            "the first script in head must be the scoutTheme detector",
        )
        return
    script = scripts[0]
    source = _script_text(script)
    required = (
        "URLSearchParams",
        'get("scoutTheme")',
        "prefers-color-scheme: dark",
        'setAttribute("data-theme", theme)',
    )
    if script.get("src") or any(marker not in source for marker in required):
        failures.add(
            "theme.scout_script",
            "the first script in head is not the mandatory scoutTheme detector",
        )


def _check_theme_tokens(
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    scoped: dict[str, dict[str, list[str]]] = {
        "light": {},
        "dark": {},
    }
    misplaced = []
    for declaration in declarations:
        if not declaration.property.startswith("--cp-"):
            continue
        scope = _theme_scope(declaration)
        if scope is None:
            misplaced.append(
                f"{declaration.property} in {_last_selector(declaration)!r}"
            )
            continue
        scoped[scope].setdefault(declaration.property, []).append(
            declaration.value
        )
    for scope, expected in (
        ("light", LIGHT_THEME_VARIABLES),
        ("dark", DARK_THEME_VARIABLES),
    ):
        actual = scoped[scope]
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        duplicate = sorted(
            name for name, values in actual.items() if len(values) != 1
        )
        wrong = sorted(
            name
            for name, expected_value in expected.items()
            if name in actual
            and len(actual[name]) == 1
            and _normalize_css_value(actual[name][0])
            != _normalize_css_value(expected_value)
        )
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("extra " + ", ".join(extra))
        if duplicate:
            details.append("duplicated " + ", ".join(duplicate))
        if wrong:
            details.append("wrong value " + ", ".join(wrong))
        if details:
            failures.add(
                "theme.tokens",
                f"{scope} theme variables: " + "; ".join(details),
            )
    if misplaced:
        failures.add(
            "theme.tokens",
            "--cp-* declarations are only allowed in exact light/dark scopes: "
            + "; ".join(misplaced[:4]),
        )


def _check_colors(
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    hardcoded = []
    expected_by_scope = {
        "light": LIGHT_THEME_VARIABLES,
        "dark": DARK_THEME_VARIABLES,
    }
    for declaration in declarations:
        if not _has_color_literal(declaration.value):
            continue
        scope = _theme_scope(declaration)
        expected = expected_by_scope.get(scope or "", {}).get(
            declaration.property
        )
        if (
            expected is not None
            and _normalize_css_value(declaration.value)
            == _normalize_css_value(expected)
        ):
            continue
        hardcoded.append(
            f"{declaration.source}: {declaration.property}: "
            f"{declaration.value[:70]}"
        )
    if hardcoded:
        failures.add(
            "theme.colors",
            "hardcoded color literals outside exact --cp-* declarations: "
            + "; ".join(hardcoded[:5]),
        )


def _check_fonts_and_forbidden(
    text: str,
    soup: BeautifulSoup,
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    body_fonts = [
        declaration.value
        for declaration in declarations
        if declaration.property == "font-family"
        and re.search(r"(^|,)\s*body(?:\s|,|$)", _last_selector(declaration))
    ]
    if not any(
        re.search(r"segoe\s+ui", value, re.IGNORECASE)
        and re.search(r"\baptos\b", value, re.IGNORECASE)
        for value in body_fonts
    ):
        failures.add(
            "theme.fonts",
            "body must use a Segoe UI and Aptos system-font stack",
        )
    code_fonts = [
        declaration.value
        for declaration in declarations
        if declaration.property == "font-family"
        and re.search(
            r"(^|[\s,>+~])(code|pre)(?=$|[\s,.:#\[>+~])",
            _last_selector(declaration),
        )
    ]
    if not any("consolas" in value.lower() for value in code_fonts):
        failures.add(
            "theme.fonts",
            "code and pre elements must use a Consolas font stack",
        )

    lowered = text.lower()
    forbidden = []
    for marker in ("fonts.googleapis.com", "jetbrains mono"):
        if marker in lowered:
            forbidden.append(marker)
    if re.search(r"\binter\b", lowered):
        forbidden.append("Inter")
    declared_properties = {declaration.property for declaration in declarations}
    legacy = sorted(LEGACY_VARIABLES & declared_properties)
    if legacy:
        forbidden.append("legacy variables " + ", ".join(legacy))
    visible = normalized_visible_text(soup)
    if re.search(r"\bclawpilot\b", visible, re.IGNORECASE):
        forbidden.append("Clawpilot branding")
    gradient_shell = []
    for declaration in declarations:
        if declaration.property not in {"background", "background-image"}:
            continue
        selector = _last_selector(declaration)
        if (
            "gradient(" in declaration.value.lower()
            and re.search(
                r"(^|,)\s*(?:html|body|header|\.topbar|\.top-bar|"
                r"\.shell|\.page-shell)(?:[\s,:.#\[]|$)",
                selector,
            )
        ):
            gradient_shell.append(selector)
    if gradient_shell:
        forbidden.append(
            "gradient shell on " + ", ".join(sorted(set(gradient_shell)))
        )
    if forbidden:
        failures.add(
            "theme.forbidden",
            "forbidden legacy theme material found: " + "; ".join(forbidden),
        )


def _control_has_label(control: Tag | None) -> bool:
    return bool(
        control
        and (
            control.get("aria-label")
            or control.get("aria-labelledby")
        )
    )


def _find_topbar(soup: BeautifulSoup) -> Tag | None:
    for candidate in soup.select("header.topbar, header.top-bar, header"):
        text = normalized_visible_text(candidate)
        if "AIBAST" in text and "Production Guide" in text:
            return candidate
    return None


def _check_topbar_feedback_accessibility(
    text: str,
    soup: BeautifulSoup,
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    topbar = _find_topbar(soup)
    required_labels = (
        "Library",
        "Production Guide",
        "Workshop settings",
        "Report an issue",
    )
    topbar_text = normalized_visible_text(topbar) if topbar else ""
    theme_control: Tag | None = None
    report_control: Tag | None = None
    sidebar_control: Tag | None = None
    if topbar:
        for control in topbar.select("button, a, input"):
            control_text = normalized_visible_text(control)
            identity = " ".join(
                str(control.get(attribute, ""))
                for attribute in (
                    "id",
                    "class",
                    "data-theme-toggle",
                    "aria-label",
                    "onclick",
                )
            )
            if (
                re.search(r"theme", control_text, re.IGNORECASE)
                or re.search(r"theme", identity, re.IGNORECASE)
            ):
                theme_control = control
            if "Report an issue" in control_text:
                report_control = control
            if (
                "toggleSidebar" in control.get("onclick", "")
                or control.has_attr("data-sidebar-toggle")
                or control.get("aria-controls") == "sidebar"
            ):
                sidebar_control = control
    if not topbar or any(label not in topbar_text for label in required_labels):
        failures.add(
            "theme.topbar",
            "visible AIBAST top bar must include Library, Production Guide, "
            "Workshop settings, and Report an issue",
        )
    theme_wired = False
    if theme_control:
        control_id = theme_control.get("id")
        theme_wired = bool(
            theme_control.get("onclick")
            or theme_control.has_attr("data-theme-toggle")
            or (
                control_id
                and len(re.findall(re.escape(control_id), text)) > 1
            )
        )
    if not theme_control or not theme_wired:
        failures.add(
            "theme.topbar",
            "the top bar requires a measurable, wired theme toggle",
        )

    feedback_requirements = (
        "<!-- aibast-workshop-feedback:v1 -->",
        "aibast-workshop-feedback/1.0",
        "https://github.com/microsoft/aibast-agents-library/issues/new",
    )
    if any(requirement not in text for requirement in feedback_requirements):
        failures.add(
            "theme.feedback",
            "contextual feedback marker, schema, and GitHub issues/new wiring "
            "are required",
        )
    if text.count("<!-- aibast-workshop-feedback:v1 -->") < 2:
        failures.add(
            "theme.feedback",
            "the feedback marker must be present in both the page source and "
            "the prefilled GitHub issue body",
        )
    if report_control is None:
        failures.add(
            "theme.feedback",
            "a visible Report an issue control is required",
        )
    visible = normalized_visible_text(soup)
    if re.search(r"\bbeta\b", visible, re.IGNORECASE):
        failures.add("theme.beta", "visible Beta labels are forbidden")

    for landmark in ("header", "nav", "main", "aside"):
        if soup.find(landmark) is None:
            failures.add(
                "accessibility.landmarks",
                f"missing {landmark} landmark",
            )
    skip = soup.select_one('a.skip-link[href^="#"], a[href^="#"][class*="skip"]')
    skip_target = None
    if skip:
        skip_target = soup.find(id=skip.get("href", "")[1:])
    if not skip or skip_target is None:
        failures.add(
            "accessibility.landmarks",
            "a working skip link is required",
        )
    sidebar = soup.select_one("aside#sidebar, aside.sidebar")
    if not _control_has_label(sidebar):
        failures.add(
            "accessibility.controls",
            "the sidebar landmark requires an aria label",
        )
    for name, control in (
        ("sidebar", sidebar_control),
        ("theme", theme_control),
        ("report", report_control),
    ):
        if not _control_has_label(control):
            failures.add(
                "accessibility.controls",
                f"the {name} control requires an aria label",
            )

    selectors = " ".join(
        declaration.contexts[-1]
        for declaration in declarations
        if declaration.contexts
    )
    if ":focus-visible" not in selectors:
        failures.add(
            "accessibility.focus",
            "CSS must define focus-visible styles",
        )
    reduced = [
        declaration
        for declaration in declarations
        if any(
            "prefers-reduced-motion" in context
            for context in declaration.contexts
            if context.lstrip().startswith("@")
        )
    ]
    if not reduced:
        failures.add(
            "accessibility.motion",
            "CSS must handle prefers-reduced-motion",
        )


def _check_components_and_tracks(
    text: str,
    soup: BeautifulSoup,
    declarations: list[CssDeclaration],
    failures: FailureCollector,
) -> None:
    css_selectors = " ".join(
        context
        for declaration in declarations
        for context in declaration.contexts
        if not context.lstrip().startswith("@")
    ).lower()
    responsive_sidebar = any(
        "sidebar" in _last_selector(declaration)
        and any(
            context.lstrip().lower().startswith("@media")
            and ("max-width" in context.lower() or "width <" in context.lower())
            for context in declaration.contexts
        )
        for declaration in declarations
    )
    checks = {
        "responsive sidebar": bool(soup.select_one("#sidebar"))
        and responsive_sidebar,
        "progress": bool(
            soup.select_one(
                "progress, .progress, .progress-bar, .progress-fill"
            )
        )
        and "progress" in css_selectors,
        "table": bool(soup.find("table"))
        and bool(re.search(r"(?:^|[-_.#\s,>+~])table(?:$|[-_.#\s,:[>+~])", css_selectors)),
        "card": bool(soup.select_one('[class*="card"]'))
        and bool(re.search(r"(?:^|[-_.#\s,>+~])card(?:$|[-_.#\s,:[>+~])", css_selectors)),
        "code": bool(soup.find(["code", "pre"]))
        and bool(
            re.search(
                r"(?:^|[-_.#\s,>+~])(code|pre)(?:$|[-_.#\s,:[>+~])",
                css_selectors,
            )
        ),
        "quiz": bool(soup.select_one('[id^="quiz-"], .quiz, .gut-check'))
        and ("quiz" in css_selectors or "gut-check" in css_selectors),
    }
    missing = [name for name, present in checks.items() if not present]
    if missing:
        failures.add(
            "theme.components",
            "required workshop components are not measurable: "
            + ", ".join(missing),
        )
    dead = [marker for marker in DEAD_TRACK_MARKERS if marker in text]
    if dead:
        failures.add(
            "theme.dead_track",
            "dead track-selector material remains: " + ", ".join(dead),
        )


def audit_text(
    text: str,
    contract: dict[str, Any],
    *,
    guide_label: str = "docs/rapp-guide.html",
    contract_label: str = "state/rapp_guide_content_contract.json",
    node_path: str | None = None,
    baseline_text: str | None = None,
) -> dict[str, Any]:
    failures = FailureCollector()
    validated_contract = _validate_contract(contract, failures) or {}
    _check_contract_against_baseline(
        validated_contract,
        baseline_text,
        failures,
    )
    soup = BeautifulSoup(text, "html.parser")
    measurements = _check_content(
        text, soup, validated_contract, failures
    )
    checked_scripts = _check_inline_scripts(
        soup,
        failures,
        shutil.which("node") if node_path is None else node_path,
    )
    declarations = _collect_css(soup, failures)
    _check_no_js_semantics(soup, declarations, failures)
    _check_theme_script(soup, failures)
    _check_theme_tokens(declarations, failures)
    _check_colors(declarations, failures)
    _check_fonts_and_forbidden(text, soup, declarations, failures)
    _check_topbar_feedback_accessibility(
        text, soup, declarations, failures
    )
    _check_components_and_tracks(text, soup, declarations, failures)
    _check_post_migration_interactions(text, soup, failures)
    _check_static_behavior_semantics(text, soup, failures)
    measurements.update(
        {
            "inline_scripts_checked": checked_scripts,
            "css_declarations_measured": len(declarations),
        }
    )
    categories = sorted(
        {failure["category"] for failure in failures.items}
    )
    return {
        "schema": AUDIT_SCHEMA,
        "ok": not failures.items,
        "guide": guide_label,
        "contract": contract_label,
        "failure_count": len(failures.items),
        "failure_categories": categories,
        "failures": failures.items,
        "measurements": measurements,
    }


def audit_paths(
    guide_path: Path,
    contract_path: Path,
    *,
    node_path: str | None = None,
) -> dict[str, Any]:
    failures = FailureCollector()
    try:
        text = guide_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.add("input.guide", f"guide cannot be read: {exc}")
        text = ""
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.add("input.contract", f"contract cannot be read: {exc}")
        contract = {}
    baseline_text = None
    if not failures.items:
        baseline_text = _load_trusted_baseline(
            guide_path,
            contract,
            failures,
        )
    if failures.items:
        return {
            "schema": AUDIT_SCHEMA,
            "ok": False,
            "guide": str(guide_path),
            "contract": str(contract_path),
            "failure_count": len(failures.items),
            "failure_categories": sorted(
                {item["category"] for item in failures.items}
            ),
            "failures": failures.items,
            "measurements": {},
        }
    return audit_text(
        text,
        contract,
        guide_label=str(guide_path),
        contract_label=str(contract_path),
        node_path=node_path,
        baseline_text=baseline_text,
    )


def _human_output(report: dict[str, Any]) -> str:
    status = "PASS" if report["ok"] else "FAIL"
    lines = [
        f"{status}: {report['guide']}",
        f"Contract: {report['contract']}",
    ]
    if report["ok"]:
        measurements = report.get("measurements", {})
        lines.append(
            "Verified 21 content sections, "
            f"{measurements.get('inline_scripts_checked', 0)} inline scripts, "
            f"and {measurements.get('css_declarations_measured', 0)} CSS "
            "declarations."
        )
        return "\n".join(lines)
    grouped: dict[str, list[str]] = {}
    for failure in report["failures"]:
        grouped.setdefault(failure["category"], []).append(failure["message"])
    for category in sorted(grouped):
        lines.append(f"[{category}]")
        lines.extend(f"  - {message}" for message in grouped[category])
    lines.append(
        f"Summary: {report['failure_count']} failure(s) in "
        f"{len(report['failure_categories'])} categor{'y' if len(report['failure_categories']) == 1 else 'ies'}."
    )
    return "\n".join(lines)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit RAPP guide content preservation, behavior, theme, and "
            "accessibility."
        )
    )
    parser.add_argument(
        "--guide",
        type=Path,
        default=DEFAULT_GUIDE,
        help=f"guide HTML path (default: {DEFAULT_GUIDE})",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT,
        help=f"content contract path (default: {DEFAULT_CONTRACT})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable audit report",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    report = audit_paths(args.guide, args.contract)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(_human_output(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
