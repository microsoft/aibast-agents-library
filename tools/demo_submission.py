#!/usr/bin/env python3
"""Check and approve demo submissions for the Community agents page.

Colleagues submit a finished demo through the GitHub issue form
`.github/ISSUE_TEMPLATE/demo-submission.yml`. The workflow
`.github/workflows/demo-submission.yml` passes the issue body to this script
as a file (never through the shell) and acts on the JSON result.

    check  --body-file F --result R --comment C [--issue N] [--manifest M] [--offline]
    apply  --body-file F --issue N --manifest community_tools.json --result R [--offline]

Approved demos become `kind: "demo"` entries in community_tools.json, the
existing aibast-community-tools/1.0 manifest. Entries without a kind are
tools, exactly as before. Demo entries stay out of the agent library: the
registry build and the library export both skip them.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

FORM_MARKER = "Submit a demo to Community agents"

TITLE = "Demo title"
VIDEO = "Public video URL"
DESCRIPTION = "Short description"
INDUSTRY = "Industry"
PRODUCTS = "Microsoft products used"
TEAM = "Owning team or channel"
ONEPAGER = "One-pager URL (optional)"
CONFIRMATIONS = "Before you submit"

INDUSTRIES = (
    "B2B Sales",
    "B2C Sales",
    "Cross-Industry",
    "Energy",
    "Financial Services",
    "Healthcare",
    "Human Resources",
    "Manufacturing",
    "Professional Services",
    "Retail & CPG",
    "SLG Government",
    "Software & Digital Products",
    "Telecom, Media & Gaming",
)

PRODUCT_OPTIONS = (
    "Copilot Studio",
    "Microsoft 365 Copilot",
    "Dataverse",
    "Power Apps",
    "Power Automate",
    "Teams",
    "SharePoint",
    "Dynamics 365",
    "Other",
)

REQUIRED_CONFIRMATIONS = (
    "The demo uses synthetic data only.",
    "The demo contains no customer names or customer data.",
    "The video is public and ours to share.",
    "It is built only with Microsoft 365, Power Platform, Dynamics 365 or Copilot Studio (no Azure services).",
)

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
# Microsoft Stream videos live on SharePoint and need a sign-in, so they cannot
# play on a public page. Only public YouTube links are accepted.
# A YouTube video id: 11 letters, digits, hyphens or underscores.
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
# youtube.com paths that name one video in their second segment.
YOUTUBE_VIDEO_PATHS = {"shorts", "embed", "live", "v"}
# Eleven letters long, so it looks like an id, but embed/videoseries?list=...
# plays a whole playlist. It is never a video id.
YOUTUBE_NOT_IDS = {"videoseries"}
ONE_VIDEO_PROBLEM = (
    "The video link must point to one video (a watch, youtu.be or shorts link), "
    "not a playlist or a channel."
)

# Hosts whose pages open only after a work or school sign-in, so public
# visitors cannot open a one-pager stored there. Each entry also covers its
# subdomains.
SIGN_IN_ONLY_HOSTS = (
    "sharepoint.com",
    "sharepoint.us",
    "sharepoint-df.com",
    "teams.microsoft.com",
    "teams.live.com",
    "loop.microsoft.com",
    "cloud.microsoft",
    "web.microsoftstream.com",
    "stream.microsoft.com",
    "login.microsoftonline.com",
    "login.live.com",
    "dynamics.com",
    "make.powerapps.com",
    "apps.powerapps.com",
    "make.powerautomate.com",
    "copilotstudio.microsoft.com",
    "admin.microsoft.com",
)
ONEPAGER_SIGN_IN_PROBLEM = (
    "The one-pager link opens only after a work sign-in, so public visitors "
    "cannot open it. Share it from a public site instead."
)

# Words that must never reach the public page. Matched across every free-text
# field and the one-pager link, after folding case and full-width letters, and
# also when a version number or another word is joined on (see forbidden_terms_in).
FORBIDDEN_TERMS = (
    "rapp factory",
    "confidential",
    "internal only",
    "internal use only",
    "do not share",
    "do not distribute",
    "nda",
    "azure",
)

# Other vendors' AI products. Demo cards describe what was built with
# Microsoft products, so these names are flagged too. The problem text never
# repeats them, because the check comment is public; it names the field instead.
# Everyday English words are listed only with the vendor word that makes them
# a product name ("perplexity ai", "google bard"). A name made of two words is
# listed with a space ("open ai"), so "OpenAI", "Open AI" and "open-ai" all
# match it; see the word-matching rules below. A name the vendor writes as one
# word but that reads as ordinary words when spaced is also listed in
# SPACED_NAMES_NEED_CAPITALS, so "an open AI standard" passes.
OTHER_AI_PRODUCT_TERMS = (
    "chatgpt",
    "open ai",
    "gpt",
    "anthropic",
    "claude",
    "gemini",
    "google bard",
    "llama",
    "mistral",
    "grok",
    # "perplexity" alone is an everyday word.
    "perplexity ai",
    "deep seek",
    "mid journey",
    "qwen",
    # Other vendors' agent and AI platforms.
    "agent force",
    "salesforce einstein",
    "einstein copilot",
    "amazon bedrock",
    "aws bedrock",
    "bedrock agents",
    "amazon lex",
    "amazon q",
    "sage maker",
    "vertex ai",
    "agent space",
    "dialog flow",
    "duet ai",
    "watson x",
    "ibm watson",
)
# Names the vendor writes as one word ("OpenAI", "Dialogflow") whose parts are
# everyday words. Written with a space between the parts, they match only when
# every part starts with a capital ("Open AI", "Dialog Flow"), so prose such as
# "the dialog flow of the agent" passes. Joined forms ("openai", "open-ai",
# "open_ai", "DialogFlow.pdf") still match in any case (GAP_NEEDS_CAPITALS).
SPACED_NAMES_NEED_CAPITALS = frozenset({
    "open ai",
    "deep seek",
    "agent force",
    "sage maker",
    "dialog flow",
    "watson x",
    "agent space",
    "mid journey",
})
OTHER_AI_PRODUCTS_PROBLEM = "Remove the names of AI products from other companies."

# A host a browser URL parser accepts: dot-separated letters, digits and hyphens.
_HOST_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
HOST_RE = re.compile(rf"^{_HOST_LABEL}(?:\.{_HOST_LABEL})*\.?$")
PORT_RE = re.compile(r"^[0-9]{1,5}$")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HANDLE_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9][\w-]*")
NO_RESPONSE = {"", "_no response_", "none"}

MANIFEST_SCHEMA = "aibast-community-tools/1.0"
DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "community_tools.json"


class SubmissionError(Exception):
    pass


# --------------------------------------------------------------------- parse
def parse_issue_form(body: str) -> dict[str, str]:
    """Split a rendered issue form into {heading: raw value}."""
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in (body or "").replace("\r\n", "\n").split("\n"):
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = heading.group(1).strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def _value(sections: dict[str, str], key: str) -> str:
    value = sections.get(key, "").strip()
    return "" if value.lower() in NO_RESPONSE else value


def _checked(raw: str) -> list[str]:
    return [
        m.group(2).strip()
        for m in re.finditer(r"^\s*[-*]\s+\[([xX])\]\s+(.+?)\s*$", raw or "", re.M)
    ]


def normalise(text: str) -> str:
    """Fold full-width and other compatibility letters to plain ones (NFKC)
    and drop invisible format characters such as zero-width spaces."""
    text = unicodedata.normalize("NFKC", text or "")
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalise(text).lower()).strip("-")
    return slug[:60].strip("-")


# ------------------------------------------------------------------ validate
def split_url(url: str) -> tuple[urllib.parse.SplitResult, int | None]:
    """Split a link the way a browser would accept it, or raise ValueError.

    Python's urlsplit accepts hosts and ports that a browser's URL parser
    rejects (spaces, an out-of-range or non-numeric port). Such a link would
    break the public page, so it is refused here.
    """
    if not url or any(ch.isspace() or ord(ch) < 0x20 or ch == "\\" for ch in url):
        raise ValueError("whitespace, control character or backslash")
    parts = urllib.parse.urlsplit(url)
    hostport = parts.netloc.rpartition("@")[2]
    host, colon, port = hostport.rpartition(":") if ":" in hostport else (hostport, "", "")
    if not HOST_RE.match(host):
        raise ValueError("invalid host")
    if colon and port:
        if not PORT_RE.match(port) or int(port) > 65535:
            raise ValueError("invalid port")
    return parts, (int(port) if colon and port else None)


def classify_video_url(url: str) -> str:
    """Return 'youtube', or raise SubmissionError."""
    try:
        parts, port = split_url(url)
    except ValueError as exc:
        if not url.lower().startswith("https://"):
            raise SubmissionError("The video link must start with https://.") from exc
        raise SubmissionError("The video link is not a valid URL.") from exc
    if parts.scheme != "https":
        raise SubmissionError("The video link must start with https://.")
    if parts.username or parts.password or port is not None:
        raise SubmissionError("The video link must be a plain public https link.")
    host = (parts.hostname or "").lower()
    if host in YOUTUBE_HOSTS:
        if not is_single_youtube_video(host, parts):
            raise SubmissionError(ONE_VIDEO_PROBLEM)
        return "youtube"
    raise SubmissionError(
        f"The video must be a public YouTube link (got {host or 'no host'}). "
        "Microsoft Stream videos need a sign-in, so they cannot play on the public page."
    )


def _is_video_id(value: str) -> bool:
    return bool(YOUTUBE_ID_RE.match(value)) and value.lower() not in YOUTUBE_NOT_IDS


def is_single_youtube_video(host: str, parts: urllib.parse.SplitResult) -> bool:
    """True for a link to one video: watch?v=, youtu.be/<id>, shorts/<id>.

    A list= parameter is allowed only next to a real video id, and
    embed/videoseries (a whole playlist) is never one video.
    """
    segments = [s for s in parts.path.split("/") if s]
    if host == "youtu.be":
        return len(segments) == 1 and _is_video_id(segments[0])
    if segments == ["watch"]:
        ids = urllib.parse.parse_qs(parts.query).get("v", [])
        return len(ids) == 1 and _is_video_id(ids[0])
    return (
        len(segments) == 2
        and segments[0] in YOUTUBE_VIDEO_PATHS
        and _is_video_id(segments[1])
    )


def is_sign_in_only_host(host: str) -> bool:
    host = (host or "").lower().rstrip(".")
    return any(host == h or host.endswith("." + h) for h in SIGN_IN_ONLY_HOSTS)


# ------------------------------------------------------------- word matching
# One set of rules for every field, so a fix for one case cannot quietly
# break another. tests/test_community_term_corpus.py holds every case.
#
# The text is read as a list of words (runs of letters and digits). The gap
# before each word is sorted once into one of four kinds:
#
#   tight - nothing, underscores, or one joining mark that sits between two
#           word characters ("RAPP/Factory", "Vertex.AI", "Amazon-Q",
#           "Salesforce·Einstein"). A possessive is tight too ("Google's Bard").
#   space - whitespace only ("Open AI").
#   dash  - one en or em dash with no space around it ("Vertex—AI").
#   break - anything else: a mark with a space before or after it ("Amazon.
#           Q4", "Amazon, Q3", "Amazon - Q4"), an opening bracket or a quote
#           ("perplexity (AI"), or more than one mark.
#
# A listed name is found when consecutive words, joined by gaps that are not
# breaks, spell it. GAP_NEEDS_CAPITALS says when a gap joins only words that
# all start with a capital:
#
#   tight - never; a tight join always reads as one name ("open-ai").
#   space - only for names in SPACED_NAMES_NEED_CAPITALS, whose parts are
#           everyday words: "Open AI" flags, "an open AI standard" passes.
#   dash  - for every name, because a bare dash is also sentence punctuation:
#           "Vertex—AI" and "Open–AI" flag, "perplexity—AI helps" passes.
#
# Further rules:
#
# 1. The text is folded first (NFKC, invisible characters dropped, casefold).
# 2. A name may be spelled in one word or in several, but every place where
#    the text's words divide must be a place where the name's words divide:
#    "vertexai", "Vertex AI" and "open-ai" are names; "Ope nAI" is not.
#    Each name is listed once, with spaces between its words ("open ai").
# 3. A name starts at the start of a word and ends at the end of one. A
#    version number may follow it (GPT4, Claude3, GPT-4o), unless its last
#    word is one letter, so "Amazon Q4" stays a sales quarter.
# 4. Each word is read whole and also split at capitals and digits
#    ("AzureOpenAI" -> "Azure Open AI"); the pieces of one word are tight.
#    One-pager links do not split opaque ids, which have a digit followed by
#    a letter ("AbNDA9xQ").
# 5. A lower-case word built only from listed names ("azureopenai") counts as
#    those names. The word is decomposed with a loop, never recursion, so a
#    word of any length is checked.

# Spaces out joined words: "AzureOpenAI" -> "Azure Open AI", "GPT4o" -> "GPT 4o".
_JOIN_RE = re.compile(
    r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])"
)
_WORD_RE = re.compile(r"[^\W_]+")
_POSSESSIVE_RE = re.compile(r"(?<=[^\W_])['’]s(?![^\W_])")
# Marks that join two words when they sit between two word characters.
_JOINING_MARKS = frozenset("-‐‑/\\.·∙•+:~|")
# Dashes that are also sentence punctuation: they join only capitalised words.
_DASHES = frozenset("–—")
# A run of letters and digits with a digit followed by a letter is an opaque
# id ("AbNDA9xQ", "1aGPT3kz"), so a link never splits it at capitals.
_OPAQUE_RE = re.compile(r"[0-9][A-Za-z]")

TIGHT, SPACE, DASH, BREAK = "tight", "space", "dash", "break"
# For each gap that joins words: the names it joins only when every word of
# the name starts with a capital. "all" means every name.
GAP_NEEDS_CAPITALS = {TIGHT: frozenset(), SPACE: SPACED_NAMES_NEED_CAPITALS, DASH: "all"}

# A stream is a list of (word, gap before it, starts with a capital).
_Stream = list[tuple[str, str, bool]]


def _gap(separator: str) -> str:
    """The kind of gap a separator between two words makes."""
    if not separator.strip(" \t\n\r\f\v_"):
        if separator and separator.isspace():
            return SPACE
        return TIGHT
    if len(separator) == 1 and separator in _JOINING_MARKS:
        return TIGHT
    if len(separator) == 1 and separator in _DASHES:
        return DASH
    return BREAK


def _needs_capitals(gap: str, term: str) -> bool:
    rule = GAP_NEEDS_CAPITALS[gap]
    return rule == "all" or term in rule


def _streams(text: str, keep_ids: bool) -> tuple[_Stream, _Stream]:
    """The text as words read whole, and as words split at capitals."""
    plain = _POSSESSIVE_RE.sub("", normalise(text))
    whole: _Stream = []
    split: _Stream = []
    end = None
    for match in _WORD_RE.finditer(plain):
        gap = BREAK if end is None else _gap(plain[end:match.start()])
        end = match.end()
        word = match.group(0)
        whole.append((word.casefold(), gap, word[0].isupper()))
        pieces = [word] if keep_ids and _OPAQUE_RE.search(word) else _JOIN_RE.sub(" ", word).split()
        split.extend(
            (piece.casefold(), gap if k == 0 else TIGHT, piece[0].isupper())
            for k, piece in enumerate(pieces)
        )
    return whole, split


def _spelled_at(stream: _Stream, start: int, term: str) -> bool:
    """True when the words from stream[start] on spell the term (rules 2, 3
    and GAP_NEEDS_CAPITALS)."""
    words = term.split()
    key = "".join(words)
    divisions = set(itertools.accumulate(len(w) for w in words[:-1]))
    one_letter = len(words[-1]) == 1
    capitals_needed = False
    capitals_all = True
    pos = 0
    for i in range(start, len(stream)):
        word, gap, capital = stream[i]
        if i > start:
            if gap == BREAK:
                return False
            capitals_needed = capitals_needed or _needs_capitals(gap, term)
        capitals_all = capitals_all and capital
        rest = key[pos:]
        if word == rest:
            following = stream[i + 1] if i + 1 < len(stream) else None
            digit_next = bool(following and following[1] != BREAK and following[0][0].isdigit())
            ok = not (one_letter and digit_next)
        elif word.startswith(rest):
            ok = word[len(rest)].isdigit() and not one_letter
        elif rest.startswith(word) and pos + len(word) in divisions:
            pos += len(word)
            continue
        else:
            return False
        return ok and (capitals_all or not capitals_needed)
    return False


def _compound_terms(word: str, terms: list[str]) -> set[str]:
    """Terms that make up a lower-case word built only from terms, such as
    "azureopenai". A version tail ("chatgpt4o") may follow (rule 5).

    Dynamic programming from the end of the word, so a word of any length
    is checked without recursion. Among the ways to read the word, the one
    that takes the longest term first at each step is reported.
    """
    keys = sorted({"".join(t.split()): t for t in terms}.items(),
                  key=lambda kv: len(kv[0]), reverse=True)
    n = len(word)
    # done[i][state]: word[i:] can be read, where state says what came before:
    # 0 nothing yet, 1 a term whose last word is longer than one letter,
    # 2 a term whose last word is one letter (so no version tail may follow).
    done = [[False] * 3 for _ in range(n + 1)]
    done[n] = [True, True, True]
    choice: list[list[tuple[str, str] | None]] = [[None] * 3 for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for state in range(3):
            if state and word[i].isdigit():
                done[i][state] = state == 1
                continue
            for key, term in keys:
                if word.startswith(key, i):
                    after = 2 if len(term.split()[-1]) == 1 else 1
                    if done[i + len(key)][after]:
                        done[i][state] = True
                        choice[i][state] = (key, term)
                        break
    if not n or not done[0][0]:
        return set()
    found: set[str] = set()
    i, state = 0, 0
    while i < n and choice[i][state] is not None:
        key, term = choice[i][state]
        found.add(term)
        i += len(key)
        state = 2 if len(term.split()[-1]) == 1 else 1
    return found


def forbidden_terms_in(
    text: str, terms: tuple[str, ...] = FORBIDDEN_TERMS, keep_ids: bool = False
) -> list[str]:
    """Return the terms found in text, by the rules above.

    keep_ids=True leaves opaque ids whole (rule 6), for one-pager links.
    """
    streams = _streams(text, keep_ids)
    vocabulary = list(dict.fromkeys(FORBIDDEN_TERMS + OTHER_AI_PRODUCT_TERMS + tuple(terms)))
    compounds: set[str] = set()
    for word, *_rest in streams[0]:
        compounds |= _compound_terms(word, vocabulary)
    return [
        term for term in terms
        if term in compounds
        or any(_spelled_at(s, i, term) for s in streams for i in range(len(s)))
    ]


def other_ai_products_in(text: str, keep_ids: bool = False) -> bool:
    return bool(forbidden_terms_in(text, OTHER_AI_PRODUCT_TERMS, keep_ids))


def onepager_words(url: str) -> str:
    """The human-readable part of a one-pager link, ready for
    forbidden_terms_in(..., keep_ids=True).

    The host is read as written and also label by label from the right, the
    way a domain is owned ("bard.google.com" is Google's Bard). The path is
    read with escapes decoded. The query and fragment are left out: they hold
    ids and share tokens, not words a visitor reads. The three parts are
    joined with sentence breaks, so words never join across them.
    """
    try:
        parts = urllib.parse.urlsplit(url)
        host = (parts.hostname or "").rstrip(".")
    except ValueError:
        return ""
    path = urllib.parse.unquote(parts.path)
    reversed_host = ".".join(reversed(host.split(".")))
    return ". ".join([host, path, reversed_host])


def other_ai_products_problem(fields: list[str]) -> str:
    """The public problem text. It names the fields, never the product."""
    where = fields[0] if len(fields) == 1 else ", ".join(fields[:-1]) + " and " + fields[-1]
    return (
        f"{OTHER_AI_PRODUCTS_PROBLEM} Found in {where}. "
        "Describe the demo with the Microsoft products it uses."
    )


def _sentences(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()])


def validate(sections: dict[str, str]) -> tuple[dict, list[str]]:
    """Validate a parsed form. Returns (entry fields, problems)."""
    problems: list[str] = []
    title = _value(sections, TITLE)
    video = _value(sections, VIDEO)
    description = " ".join(_value(sections, DESCRIPTION).split())
    industry = _value(sections, INDUSTRY)
    products = [p for p in _checked(sections.get(PRODUCTS, "")) if p in PRODUCT_OPTIONS]
    team = " ".join(_value(sections, TEAM).split())
    onepager = _value(sections, ONEPAGER)
    confirmed = set(_checked(sections.get(CONFIRMATIONS, "")))

    if not title:
        problems.append("Add a demo title.")
    elif len(title) > 80:
        problems.append("Keep the demo title to 80 characters or fewer.")
    elif not slugify(title):
        problems.append(
            "Use at least one English letter or number in the demo title, "
            "so the demo can have its own web address."
        )

    video_kind = None
    if not video:
        problems.append("Add the public video link.")
    else:
        try:
            video_kind = classify_video_url(video)
        except SubmissionError as exc:
            problems.append(str(exc))

    if not description:
        problems.append("Add a short description.")
    else:
        count = _sentences(description)
        if count < 2 or count > 4:
            problems.append(f"Write the description in 2 to 4 sentences (found {count}).")
        if len(description) > 700:
            problems.append("Keep the description under 700 characters.")

    if industry not in INDUSTRIES:
        problems.append("Pick an industry from the list.")
    if not products:
        problems.append("Tick at least one Microsoft product.")
    if not team:
        problems.append("Add the owning team or channel for credit.")

    onepager_text = ""
    if onepager:
        try:
            parts, _port = split_url(onepager)
            if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
                raise ValueError
        except ValueError:
            problems.append("The one-pager link must be a public https link.")
        else:
            if is_sign_in_only_host(parts.hostname):
                problems.append(ONEPAGER_SIGN_IN_PROBLEM)
        # The link shows on the public card, so the words in its host and
        # path are checked too. Ids are not split at case or digit changes.
        onepager_text = onepager_words(onepager)

    for item in REQUIRED_CONFIRMATIONS:
        if item not in confirmed:
            problems.append(f"Confirm: {item}")

    free_text = "\n".join([title, description, team])
    # Each field is checked on its own, so words never join across fields.
    checked = [
        ("the title", title, False),
        ("the description", description, False),
        ("the team name", team, False),
        ("the one-pager link", onepager_text, True),
    ]
    terms = set()
    for _label, text, keep_ids in checked:
        terms.update(forbidden_terms_in(text, keep_ids=keep_ids))
    if terms:
        problems.append(
            "Remove these words, which cannot appear on the public page: "
            + ", ".join(sorted(terms)) + "."
        )
    vendor_fields = [
        label for label, text, keep_ids in checked
        if other_ai_products_in(text, keep_ids)
    ]
    if vendor_fields:
        problems.append(other_ai_products_problem(vendor_fields))
    if EMAIL_RE.search(free_text) or HANDLE_RE.search(free_text):
        problems.append(
            "Remove email addresses and @handles. Credit a team or channel, not a person."
        )

    entry = {
        "id": slugify(title) if title else "",
        "kind": "demo",
        "name": title,
        "url": video,
        "author": team,
        "description": description,
        "industry": industry,
        "products": products,
    }
    if onepager:
        entry["onepager"] = onepager
    entry["_video_kind"] = video_kind
    return entry, problems


# -------------------------------------------------------------------- network
def _fetch_json(url: str, timeout: float = 15):
    request = urllib.request.Request(url, headers={"User-Agent": "aibast-demo-check"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def widescreen_thumbnail(thumb: str) -> str:
    """Prefer YouTube's 16:9 thumbnail over the 4:3 one with black bars."""
    parts = urllib.parse.urlsplit(thumb)
    if (parts.hostname or "").lower() == "i.ytimg.com" and parts.path.endswith("/hqdefault.jpg"):
        path = parts.path[: -len("hqdefault.jpg")] + "mqdefault.jpg"
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, "", ""))
    return thumb


def resolve_video(url: str, kind: str, fetch=_fetch_json) -> dict:
    """Confirm the video is publicly reachable. Returns oEmbed facts."""
    if kind != "youtube":
        raise SubmissionError("The video must be a public YouTube link.")
    oembed = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
    try:
        data = fetch(oembed)
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        raise SubmissionError(
            "The YouTube video could not be found or is not public."
        ) from exc
    thumb = data.get("thumbnail_url", "")
    result = {"title": data.get("title", "")}
    if isinstance(thumb, str) and thumb.startswith("https://"):
        result["thumbnail"] = widescreen_thumbnail(thumb)
    return result


# ------------------------------------------------------------------- manifest
def id_problems(manifest: dict, entry_id: str, issue: int | None) -> list[str]:
    """Problems with using entry_id for the demo from this issue.

    An id may be reused only by the issue that first claimed it, so a new
    submission can never replace another team's demo or take its credit.
    """
    if not entry_id:
        return []
    for existing in manifest.get("tools") or []:
        if not isinstance(existing, dict) or existing.get("id") != entry_id:
            continue
        if existing.get("kind") != "demo":
            return ["This title is already used by a related resource. Choose a different title."]
        if issue is None or existing.get("submission_issue") != int(issue):
            return ["This title is already used by another demo. Choose a different title."]
    return []


def apply_entry(manifest: dict, entry: dict, issue: int, today: str) -> dict:
    """Add or replace a demo entry in the community manifest."""
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise SubmissionError(f"Manifest schema must be {MANIFEST_SCHEMA}.")
    tools = manifest.get("tools")
    if not isinstance(tools, list):
        raise SubmissionError("Manifest tools must be a list.")
    clean = {k: v for k, v in entry.items() if not k.startswith("_")}
    clean["submission_issue"] = int(issue)
    if not clean.get("id"):
        raise SubmissionError("The demo needs a title to build its id.")
    clash = id_problems(manifest, clean["id"], clean["submission_issue"])
    if clash:
        raise SubmissionError(clash[0])
    for existing in tools:
        if (
            existing.get("kind") == "demo"
            and existing.get("submission_issue") == clean["submission_issue"]
            and existing.get("id") != clean["id"]
        ):
            # A retitled resubmission replaces its earlier entry.
            existing["_drop"] = True
    kept = [
        t for t in tools
        if not t.get("_drop") and not (t.get("kind") == "demo" and t.get("id") == clean["id"])
    ]
    for t in kept:
        t.pop("_drop", None)
    # The earlier entry from this issue: the same id, or the one a retitled
    # resubmission replaces. Its library link (graduated_to) carries over.
    own = [
        t for t in tools
        if t.get("kind") == "demo" and t.get("submission_issue") == clean["submission_issue"]
    ]
    previous = next((t for t in own if t.get("id") == clean["id"]), None) or next(
        (t for t in own if t.get("graduated_to")), None
    )
    if previous and previous.get("graduated_to"):
        clean["graduated_to"] = previous["graduated_to"]
    kept.append(clean)
    manifest["tools"] = kept
    manifest["count"] = len(kept)
    manifest["snapshot_date"] = today
    return manifest


def comment_for(problems: list[str]) -> str:
    if not problems:
        return (
            "Thank you. This demo passed the automatic checks and is ready for "
            "review by a library maintainer.\n\n"
            "Checked: required confirmations, a public YouTube video link, a "
            "title no other demo uses, and wording that is safe for the public page."
        )
    lines = [
        "Thank you. This demo needs a few changes before review. Edit the "
        "issue to fix them and the checks run again.",
        "",
    ]
    lines += [f"- {p}" for p in problems]
    return "\n".join(lines)


def run_check(body: str, offline: bool, fetch=_fetch_json,
              manifest: dict | None = None, issue: int | None = None) -> tuple[dict, list[str]]:
    entry, problems = validate(parse_issue_form(body))
    if manifest is not None:
        problems += id_problems(manifest, entry.get("id", ""), issue)
    if not problems and not offline:
        try:
            facts = resolve_video(entry["url"], entry["_video_kind"], fetch=fetch)
            if facts.get("thumbnail"):
                entry["thumbnail"] = facts["thumbnail"]
        except SubmissionError as exc:
            problems.append(str(exc))
    return entry, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--body-file", required=True, type=Path)
    check.add_argument("--result", required=True, type=Path)
    check.add_argument("--comment", required=True, type=Path)
    check.add_argument("--issue", type=int)
    check.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    check.add_argument("--offline", action="store_true")
    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("--body-file", required=True, type=Path)
    apply_cmd.add_argument("--issue", required=True, type=int)
    apply_cmd.add_argument("--manifest", required=True, type=Path)
    apply_cmd.add_argument("--result", required=True, type=Path)
    apply_cmd.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)

    body = args.body_file.read_text(encoding="utf-8")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entry, problems = run_check(body, args.offline, manifest=manifest, issue=args.issue)
    result = {"ok": not problems, "problems": problems, "id": entry.get("id", ""),
              "name": entry.get("name", "")}

    if args.command == "check":
        args.comment.write_text(comment_for(problems) + "\n", encoding="utf-8")
    elif not problems:
        try:
            apply_entry(manifest, entry, args.issue, date.today().isoformat())
        except SubmissionError as exc:
            result.update(ok=False, problems=[str(exc)])
        else:
            args.manifest.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
    args.result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
