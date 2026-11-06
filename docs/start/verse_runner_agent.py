"""VerseRunner: runs a whole RAPP verse end to end in one call, chaining this Brainstem's agents in any order.

Generated from the verse SDK (rapp_verse.py) by build_agent.py. Do not edit here; edit the SDK and rebuild.
"""
from __future__ import annotations
import sys as _sys, types as _types
_sys.modules.setdefault(__name__, _types.ModuleType(__name__))  # dataclasses look their module up by name
from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/verse_runner_agent",
    "version": "1.0.0",
    "display_name": "VerseRunner",
    "description": "Runs a whole RAPP verse end to end in one call, chaining any agents in any order.",
    "author": "kody-w",
    "tags": ["verse", "workflow", "orchestration"],
    "category": "operations",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic_agent"],
}

import dataclasses
import glob
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import urllib.request
from typing import Callable

__version__ = "1.0.0"
SPEC = "rapp-verse/1"

OPEN = re.compile(r"^\s*r\s*,?\s*a\s*,?\s*p\s*,?\s*p\s*,?\s*verse\s*[.,:]?\s*", re.I)
CLOSE = re.compile(r"\s*(?:,?\s*and\s+)?seal\s*[.!]?\s*$", re.I)
VERBS = ("bring", "through", "ask_for", "set_aside", "split", "join", "send", "go_back", "question", "keep", "plain")


# ---------------------------------------------------------------- parse

@dataclasses.dataclass
class Step:
    verb: str                      # one of VERBS
    name: str = ""                 # lens name, frame name, question, side name
    args: dict = dataclasses.field(default_factory=dict)
    branches: list = dataclasses.field(default_factory=list)   # split names
    yes: list = dataclasses.field(default_factory=list)        # question: steps if yes
    no: list = dataclasses.field(default_factory=list)         # question: steps if no
    body: list = dataclasses.field(default_factory=list)       # keep: steps to repeat
    until: str = ""                # keep: stop condition
    target: int = 0                # go back: step number
    text: str = ""                 # the words as said

    def to_dict(self):
        d = {"verb": self.verb, "text": self.text}
        for k in ("name", "args", "branches", "until", "target"):
            if getattr(self, k):
                d[k] = getattr(self, k)
        for k in ("yes", "no", "body"):
            if getattr(self, k):
                d[k] = [s.to_dict() for s in getattr(self, k)]
        return d


class VerseError(ValueError):
    pass


def is_verse(text: str) -> bool:
    return bool(OPEN.match(text or ""))


def _sentences(body: str):
    parts = re.split(r"(?<=[.?!;])\s+|\n+", body)
    out = []
    for p in parts:
        p = p.strip().rstrip(".;,").strip()
        if not p:
            continue
        if re.match(r"(if (yes|no|not|so)|with|using)\b", p, re.I):  # a branch or a leading "with ..." keeps its commas
            out.append(p)
            continue
        # "Bring the call, through Reader" -> two steps
        out.extend(x.strip() for x in re.split(r",\s*(?:then\s+)?(?:and\s+)?(?=(?:through|then through|send|join|split|set|ask for)\b)", p, flags=re.I) if x.strip())
    return out


ARTICLE = re.compile(r"^\s*(?:the|a|an|my|our|your)\s+", re.I)


def _args(text: str) -> dict:
    args = {}
    for raw in re.split(r",\s*(?:and\s+)?", text):
        # "a done note" / "a 'ship it' note": value first, kind last (only with an article or quotes, so
        # "action restart" still means action = restart)
        m = re.match(r"\s*(?:(?:a|an)\s+(?:['\"](.+?)['\"]|(\w+))|['\"](.+?)['\"])\s+(\w+)\s*$", raw, re.I)
        if m:
            args[m.group(4).lower()] = m.group(1) or m.group(2) or m.group(3)
            text = text.replace(raw, "", 1)
    text = re.sub(r"(^|,\s*|\band\s+)(?:the|a|an)\s+", r"\1", text, flags=re.I)
    for part in re.split(r",\s*(?:and\s+)?|\s+and\s+(?=\w+\s+['\"]?\w)", text):
        m = re.match(r"\s*(\w+)\s*(?:[:=]|\s+of\b|\s+saying\b|\s+that says\b)?\s+(.+?)\s*$", part)
        if m:
            args[m.group(1).lower()] = m.group(2).strip(" .'\"")
    return args


def _through(s: str, said: str) -> Step:
    s = ARTICLE.sub("", s.strip().lstrip(":,").strip())
    m = re.match(r"\s*([\w\- ]+?)(?:,?\s+(with|for)\s+(.*))?\s*$", s)
    if not m:
        raise VerseError(f"I couldn't read the lens in: {said!r}")
    name, kw, rest = m.group(1).strip(), m.group(2), (m.group(3) or "").strip()
    args = _args(rest) if kw == "with" else ({"_": rest} if rest else {})
    if kw == "with" and rest and not args:
        args = {"_": rest}
    return Step("through", name=name, args=args, text=said)


def _one(s: str) -> Step:
    low = s.lower()
    m = re.match(r"(?:from now on,?\s*)?when(?:ever)? i say ['\"“]?([\w' ]+?)['\"”]?,\s*(.+)$", s, re.I)
    if m:
        parts = [x for x in re.split(r",\s*(?:and\s+|then\s+)?|\s+and then\s+|\s+then\s+|\s+and\s+(?=(?:check|see|save|send|text|press|find|turn|tell|remind|show|lock|close)\b)", m.group(2)) if x.strip()]
        return Step("teach", name=m.group(1).strip().lower(), body=[_one(x.strip().rstrip(".")) for x in parts], text=s)
    if low.startswith("then "):
        s, low = s[5:], low[5:]
    if low.startswith("bring"):
        return Step("bring", name=re.sub(r"^bring(ing)?\s*", "", s, flags=re.I), text=s)
    if low.startswith("send"):
        return Step("send", name=re.sub(r"^send\s*", "", s, flags=re.I), text=s)
    if re.match(r"(text|email|e-mail|message|post|tweet|call|pay|order|buy|share)\s+\S", low):
        return Step("send", name=s, args={"how": low.split()[0]}, text=s)
    if low.startswith("through"):
        return _through(s[7:], s)
    # any word order: "With a note of 'done', put it through the saver" / "Put it through the saver, with a note ..."
    m = re.match(r"(?:(?:with|using)\s+(?P<pre>.+?),?\s+)?(?:then\s+)?(?:(?:put|run|pass|take|send)\s+(?:it|this|that|them|the work)\s+)?"
                 r"through\s+(?P<rest>.+)$", s, re.I)
    if m and (m.group("pre") or re.match(r"(put|run|pass|take|send)\b", low)):
        step = _through(m.group("rest"), s)
        if m.group("pre"):
            step.args = {**_args(m.group("pre")), **step.args}
        return step
    if low.startswith("set aside") or low.startswith("set the"):
        return Step("set_aside", name=re.sub(r"^set (the )?(.*?)\s*aside$|^set aside\s*", r"\2", s, flags=re.I).strip() or "aside", text=s)
    m = re.match(r"(?:at the same time|all at once|side by side)[,:]?\s+(.+)$", s, re.I)
    if m:
        names = [n.strip() for n in re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group(1)) if n.strip()]
        lead = re.match(r"(\w+)\s+(?:the\s+)?", names[0]) if names else None
        if lead and len(names) > 1:  # "check the risk, the margin and the asks" -> check each
            verb = lead.group(1)
            names = [names[0]] + [n if n.split()[0].lower() == verb.lower() else f"{verb} {n}" for n in names[1:]]
        return Step("split", branches=names, text=s)
    if re.match(r"(put|bring) (those|them|it all|these) together$", s, re.I):
        return Step("join", text=s)
    if low.startswith("split"):
        names = [n.strip() for n in re.split(r",|\band\b", re.sub(r"^split( to)?:?", "", s, flags=re.I)) if n.strip()]
        if not names:
            raise VerseError(f"Split needs names: {s!r}")
        return Step("split", branches=names, text=s)
    if low.startswith("join"):
        return Step("join", text=s)
    if low.startswith("send") or low.startswith("then send"):
        return Step("send", name=re.sub(r"^send\s*", "", s, flags=re.I), text=s)
    m = re.match(r"(?:find|look for|spot)\s+(?:the\s+|a\s+)?(.+?)(?:\s+button)?(?:\s+(?:on|in)\s+(.+))?$", s, re.I)
    if m:
        return Step("find", name=m.group(1).strip(), args={"on": m.group(2)} if m.group(2) else {}, text=s)
    m = re.match(r"(?:fill in|fill out|type|enter|put)\s+(?:the\s+)?(\w+)\s+(?:with|as|field with)\s+['\"]?(.+?)['\"]?$", s, re.I) \
        or re.match(r"(?:type|enter|put)\s+['\"]?(.+?)['\"]?\s+(?:into|in)\s+(?:the\s+)?(\w+)(?:\s+(?:box|field))?$", s, re.I)
    if m:
        field, value = (m.group(1), m.group(2)) if s.lower().startswith("fill") or " with " in s.lower() else (m.group(2), m.group(1))
        return Step("fill", name=field.lower(), args={field.lower(): value.strip(" .")}, text=s)
    m = re.match(r"(?:press|hit|click|tap)\s+(?:the\s+)?(\w[\w ]*?)(?:\s+button)?(?:\s+(?:on|in)\s+(?:the\s+)?([^,]+?))?(?:,?\s+(?:and\s+)?(.*))?$", s, re.I)
    if m:
        args = _args(re.sub(r"^(?:(?:and|then|with|using|add|adding|put|attach)\s+)+", "", m.group(3) or "", flags=re.I)) if m.group(3) else {}
        if m.group(2):
            args["on"] = m.group(2).strip()
        return Step("press", name=m.group(1).strip(), args=args, text=s)
    m = re.match(r"go back to step (\d+)(?:,?\s*with\s+(.*))?", s, re.I)
    if m:
        return Step("go_back", target=int(m.group(1)), name=(m.group(2) or "").strip(), text=s)
    m = re.match(r"ask for (.+)", s, re.I)
    if m:
        return Step("ask_for", name=m.group(1).strip(), text=s)
    m = re.match(r"keep\s+(?:bringing\s+.*?\s+through\s+|through\s+)?(.+?)\s*,?\s+until\s+(.+)", s, re.I)
    if m:
        return Step("keep", body=[_through(m.group(1), s)], until=m.group(2).strip(), text=s)
    m = re.match(r"keep\s+(.+?)\s*,?\s+until\s+(.+)", s, re.I)
    if m:
        return Step("keep", body=[Step("plain", name=m.group(1), text=m.group(1))], until=m.group(2).strip(), text=s)
    return Step("plain", name=s, text=s)


def parse(text: str) -> list[Step]:
    """Verse text -> steps. Raises VerseError when the words don't form a verse."""
    if not is_verse(text):
        raise VerseError('A verse starts with "R, A, P, P, verse" and ends with "seal".')
    body = OPEN.sub("", text, count=1)
    if not CLOSE.search(body):
        raise VerseError('This verse is not sealed yet: end it with "seal".')
    body = CLOSE.sub("", body)
    raw = _sentences(body)
    steps, i = [], 0
    while i < len(raw):
        s = raw[i]
        q = re.match(r"(?:ask a question:?\s*|ask:?\s*)?(.+\?)\s*(.*)$", s, re.I)
        if q and not s.lower().startswith("ask for"):
            step = Step("question", name=q.group(1).strip(), text=s)
            tail = [q.group(2)] if q.group(2) else []
            j = i + 1
            tail = [re.sub(r"^if not\b", "If no", re.sub(r"^if so\b", "If yes", t, flags=re.I), flags=re.I) for t in tail]
            while j < len(raw) and re.match(r"if (yes|no|not|so)\b", raw[j], re.I):
                raw[j] = re.sub(r"^if not\b", "If no", re.sub(r"^if so\b", "If yes", raw[j], flags=re.I), flags=re.I)
                tail.append(raw[j]); j += 1
            for t in tail:
                m = re.match(r"if (yes|no),?\s*(.*)", t, re.I)
                if not m:
                    continue
                branch = [_one(x) for x in re.split(r",\s*(?:then\s+)?|\s+then\s+|\s+and\s+(?=send\b)", m.group(2)) if x.strip()]
                (step.yes if m.group(1).lower() == "yes" else step.no).extend(b for b in branch if b.text.lower() != "seal")
            steps.append(step)
            i = j
            continue
        k = re.match(r"keep (?:going|at it|doing that|asking)\s*,?\s+until\s+(.+)$", s, re.I)
        if k and steps:
            prev = steps.pop()
            steps.append(Step("keep", name="again", body=[prev], until=k.group(1).strip(), text=s))
            i += 1
            continue
        b = re.match(r"(bring(?:ing)?\s+.+?)\s+and\s+(\w+\s+(?:it|them|that)\b.*)$", s, re.I)
        if b:
            steps += [_one(b.group(1)), _one(b.group(2))]
        else:
            steps.append(_one(s))
        i += 1
    if not steps:
        raise VerseError("This verse has no steps.")
    return steps


# ---------------------------------------------------------------- plan (read-back)

def _short(step: Step) -> str:
    v = step.verb
    if v == "bring":
        return "F0"
    if v == "through":
        return f"▷ {step.name}"
    if v == "ask_for":
        return f"?{step.name.replace(' ', '_')}"
    if v == "set_aside":
        return f"⇢ side:{step.name.replace(' ', '_')}"
    if v == "split":
        return f"⟨{', '.join(step.branches)}⟩"
    if v == "join":
        return "⟩Join⟨"
    if v == "send":
        return "⊣Send"
    if v == "find":
        return f"▷ Find({step.name})"
    if v == "fill":
        return "▷ Fill(" + ", ".join(f"{k}={a}" for k, a in step.args.items()) + ")"
    if v == "press":
        return f"⊣Press({step.name})"
    if v == "go_back":
        return f"↺F{step.target}" + (f"+{step.name.replace(' ', '_')}" if step.name else "")
    if v == "question":
        q = re.sub(r"^(is|are|does|do|did|has|have)\s+", "", step.name.rstrip("?"), flags=re.I).replace(" ", "_")
        return f"{q}? [{' '.join(_short(s) for s in step.yes)}] : [{' '.join(_short(s) for s in step.no)}]"
    if v == "keep":
        return f"⟳[F {' '.join(_short(s) for s in step.body)}]⇥{step.until.replace(' ', '_')}"
    return f"▷ ({step.name})"


def names(steps: list[Step]) -> list[str]:
    out = []
    for s in steps:
        if s.verb == "through":
            out.append(s.name)
        elif s.verb == "split":
            out.extend(s.branches)
        elif s.verb == "join":
            out.append("Join")
        elif s.verb == "send":
            out.append(s.args.get("how", "send").capitalize())
        elif s.verb in ("find", "fill", "press"):
            out.append(f"{s.verb.capitalize()} {s.name}")
        elif s.verb == "question":
            out.append(s.name)
            out.extend(names(s.yes) + names(s.no))
        elif s.verb == "keep":
            out.extend(names(s.body))
        elif s.verb == "teach":
            out.append(f"Learn '{s.name}'")
        elif s.verb == "plain" and s.name.lower().strip(" .") not in ("stop", "stop there", "that's it"):
            out.append(s.name)
    return out


def shorthand(steps: list[Step]) -> str:
    text = " ".join(_short(s) for s in steps)
    if not text.startswith("F0"):
        text = "F0 " + text
    return text.replace("F0 ▷", "F0 ▷", 1)


def plan(steps: list[Step]) -> str:
    """The read-back: count, names, chain. Say it before running and wait for go."""
    n = names(steps)
    word = "step" if len(n) == 1 else "steps"
    return f"{len(n)} {word} ({', '.join(n)}), sealed: {shorthand(steps)}"


NUMBERS = ["Nothing", "One thing", "Two things", "Three things", "Four things", "Five things", "Six things",
           "Seven things", "Eight things", "Nine things", "Ten things"]


def _spoken(step: Step) -> list[str]:
    v = step.verb
    if v == "through":
        extra = " ".join(f"with the {k} '{a}'" if k != "_" else a for k, a in step.args.items())
        return [f"{step.name.lower()} {extra}".strip()]
    if v == "plain":
        return [step.name[0].lower() + step.name[1:]]
    if v == "split":
        b = [x[0].lower() + x[1:] for x in step.branches]
        return ["at the same time, " + (", ".join(b[:-1]) + " and " + b[-1] if len(b) > 1 else b[0])]
    if v == "join":
        return ["put those together"]
    if v == "send":
        if step.args.get("how"):
            said = re.sub(r"\bme\b", "you", step.name[0].lower() + step.name[1:])
            return [f"{said}, once you say yes"]
        what = re.sub(r"\bme\b", "you", step.name or "it")
        return [f"send {what}, once you say yes"]
    if v == "find":
        return [f"find the {step.name} button" + (f" on {step.args['on']}" if step.args.get("on") else "")]
    if v == "fill":
        return [f"fill in the {k} with '{a}'" for k, a in step.args.items()]
    if v == "press":
        extra = "".join(f", with the {k} '{a}'" for k, a in step.args.items() if k != "on")
        return [f"press {step.name}{extra}, once you say yes"]
    if v == "ask_for":
        return [f"ask you {step.name}" if re.match(r"(who|what|where|when|which|how|whether)\b", step.name, re.I) else f"ask you for {step.name}"]
    if v == "set_aside":
        return [f"keep the {re.sub(r'^the ', '', step.name)} for later"]
    if v == "question":
        yes = " and ".join(x for s in step.yes for x in _spoken(s)) or "nothing more"
        no = " and ".join(x for s in step.no for x in _spoken(s)) or "stop"
        q = step.name[0].lower() + step.name[1:]
        m = re.match(r"^(is|are)\s+(anything|everything|something|nothing|it|he|she|they|this|that|there)\s+(.+)\?$", q)
        q = f"whether {m.group(2)} {m.group(1)} {m.group(3)}" if m else f"“{step.name}”"
        return [f"ask {q}; if so, {yes}; if not, {no}"]
    if v == "keep":
        body = " and ".join(x for s in step.body for x in _spoken(s))
        if step.name == "again":
            return [f"{body}, and keep going until {step.until}"]
        return [f"keep {body} until {step.until}"]
    if v == "go_back":
        return [f"go back to step {step.target}"]
    if v == "teach":
        inner = [x for b in step.body for x in _spoken(b)]
        inner = inner[0] if len(inner) == 1 else ", ".join(inner[:-1]) + " and " + inner[-1]
        return [f"remember that when you say “{step.name}”, I'll {inner}"]
    return []


def say(steps: list[Step]) -> str:
    """The read-back a person would say out loud: 'Three things: check the battery, see which computers are on,
    then save it with the note done. Go?'"""
    parts = [f"start with {s.name}" if s.verb == "bring" else None for s in steps]
    parts = [p for s, b in zip(steps, parts) for p in ([b] if b else _spoken(s))]
    if not parts:
        return "Nothing to do."
    count = len(parts)
    n = NUMBERS[count] if count < len(NUMBERS) else f"{count} things"
    body = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + ", then " + parts[-1]
    return f"{n}: {body}. Go?"


def _mine_to_yours(t: str) -> str:
    swap = {"my": "your", "me": "you", "I": "you", "you": "I", "your": "my", "yours": "mine", "mine": "yours"}
    t = t.replace("once you say yes", "\x00")
    return re.sub(r"\b(my|me|I|you|your|yours|mine)\b", lambda m: swap[m.group(1)], t).replace("\x00", "once you say yes")


def _thought(st: Step) -> list[str]:
    if st.verb == "teach":
        inner = [x for b in st.body for x in _thought(b)]
        inner = [x.replace(", once you say yes", "") for x in inner]
        inner = inner[0] if len(inner) == 1 else ", ".join(inner[:-1]) + " and " + inner[-1]
        return [f"remember that whenever you say “{st.name}”, I'll {inner}"]
    if st.verb == "send":
        said = st.name if st.args.get("how") else f"send {st.name or 'it'}"
        return [_mine_to_yours(said[0].lower() + said[1:]) + ", once you say yes"]
    if st.verb == "bring":
        return [f"start with {_mine_to_yours(st.name)}"]
    if st.verb == "question":
        q = st.name.rstrip("?")
        m = re.match(r"(?i)^(is|are)\s+(anything|everything|something|it|he|she|they|this|that|there)\s+(.+)$", q)
        check = f"check whether {m.group(2)} {m.group(1).lower()} {m.group(3)}" if m else f"check, “{_mine_to_yours(q)}?”"
        yes = " and ".join(x for b in st.yes for x in _thought(b))
        no = " and ".join(x for b in st.no for x in _thought(b) if x.strip(". ") != "stop")
        out, sep = check, (" " if check.endswith(("?", "?”")) else ". ")
        if yes:
            out += f"{sep}If so, I'll {yes}"; sep = ". "
        if no:
            out += f"{sep}If not, I'll {no}"
        return [out]
    return [_mine_to_yours(x) for x in _spoken(st)]


def think(steps: list[Step]) -> str:
    """The read-back as the AI's own thoughts out loud: "I'll check the battery. Sound good?"
    Anything that acts in the world ends with "but I'll ask you before I do that"."""
    parts = [x for st in steps for x in _thought(st)]
    if not parts:
        return "There's nothing for me to do there."
    ask = any("once you say yes" in x for x in parts)
    parts = [x.replace(", once you say yes", "").replace(" once you say yes", "") for x in parts]
    body = f"I'll {parts[0]}" if len(parts) == 1 else "First I'll " + ", then ".join(parts[:-1]) + ", and then " + parts[-1]
    body = body.replace("you you", "you")
    return body + (". I'll ask you before anything goes out. Sound good?" if ask else ". Sound good?")


def lint(verse_text: str) -> list[str]:
    """The bar every verse has to clear, checked without any AI: it must sound like a person talking.
    Returns plain-words problems; an empty list means it reads aloud cleanly."""
    problems = []
    try:
        steps = parse(verse_text)
    except VerseError as e:
        return [str(e)]
    words = OPEN.sub("", CLOSE.sub("", verse_text))
    for m in re.finditer(r"\bthrough\s+(?:the\s+)?([A-Z][\w]*)", words):
        problems.append(f"'through {m.group(1)}' names a helper; say the job instead (\"check the battery\", \"press save\").")
    for m in re.finditer(r"(?<![.?!]\s)(?<!^)\b([A-Z][a-z]+[A-Z]\w*)\b", words):
        problems.append(f"'{m.group(1)}' is a code name; nobody says that out loud.")
    def walk(seq):
        for st in seq:
            yield st
            for sub in (st.yes, st.no, st.body):
                yield from walk(sub)
    for st in walk(steps):
        if st.verb == "send" and not re.search(r"\b(to|it|them|the)\b", st.name or ""):
            problems.append("A bare 'send' doesn't say what goes where; say \"send it to me\" or \"send the reply to Sam\".")
        if len(st.text.split()) > 22:
            problems.append(f"'{st.text[:40]}...' is too long to say in one breath; split it into two lines.")
    return problems


CONVERT = """Rewrite this prompt as a RAPP verse: a short plan a person could say out loud.
Rules: start with "R, A, P, P, verse." and end with "Seal." One step per sentence, each short enough to say in one
breath. Say the job in everyday words (never a tool or helper name, no code names, no capitals mid-sentence).
Use these words when they fit: bring (the starting material), at the same time (things in parallel), put those
together, ask for (something only the person knows), set aside, keep ... until, a yes/no question with
"If yes, ... If no, ...". Anything that acts in the world says what goes where: "send it to me", "press save on the
form". Keep every detail and number from the prompt. Reply with only the verse.
Prompt:
"""


def convert(prompt: str, model: Model, tries: int = 3) -> dict:
    """Any old prompt -> a true verse that clears the bar. The model writes it, lint checks it, and it is
    rewritten with the problems named until it reads cleanly (at most `tries` times)."""
    task, verse_text, problems = CONVERT + prompt.strip(), "", ["not tried"]
    for _ in range(tries):
        verse_text = model(task, "").strip().strip("`").strip()
        m = re.search(r"R\s*,\s*A\s*,\s*P\s*,\s*P\s*,\s*verse.*?seal\.?", verse_text, re.I | re.S)
        verse_text = re.sub(r"\s+", " ", m.group(0)) if m else verse_text
        problems = lint(verse_text)
        if not problems:
            break
        task = (CONVERT + prompt.strip() + "\n\nYour last try was:\n" + verse_text +
                "\nFix these problems:\n- " + "\n- ".join(problems))
    out = {"prompt": prompt, "verse": verse_text, "clean": not problems, "problems": problems}
    if not problems:
        out["read_back"] = say(parse(verse_text))
    return out


def cold_ear(verse_text: str, model: Model) -> dict:
    """Would a stranger understand this verse said out loud? A model with no context hears it, says what will happen,
    and is scored against the read-back. The name test for every helper: if a stranger can't follow it, rename it."""
    steps = parse(verse_text)
    words = OPEN.sub("", CLOSE.sub("", verse_text)).strip()
    heard = model("You overheard someone say this to their computer. You know nothing else about them. In one plain "
                  "sentence, what do you think will happen? If a word makes no sense to you, say which.", words)
    verdict = model(f"Answer only YES or NO, then why. Does this guess match the plan?\nPlan: {say(steps)}",
                    heard)
    lost = model("Answer only YES or NO: does this listener say some word or name made no sense to them, or that they "
                 "had to guess what a named thing is?", heard)
    clear = verdict.strip().upper().startswith("YES") and not lost.strip().upper().startswith("YES")
    return {"said": words, "heard": heard, "plan": say(steps), "understood": clear,
            "why": verdict if not verdict.strip().upper().startswith("YES") else "A word lost them: " + heard}


# ---------------------------------------------------------------- lenses

Lens = Callable[..., str]       # lens(frame, **args) -> tile
Model = Callable[[str, str], str]  # model(task, frame) -> tile


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower()).removesuffix("agent")


def load_agents(folder: str) -> dict[str, Lens]:
    """Brainstem agent files (*_agent.py) in `folder` become lenses. Each agent's frame goes in its
    first text-like parameter; `with key value` arguments go in by name."""
    folder = os.path.abspath(os.path.expanduser(folder))
    parent = os.path.dirname(folder)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    found: dict[str, Lens] = {}
    for path in sorted(glob.glob(os.path.join(folder, "*_agent.py"))):
        if path.endswith(("basic_agent.py", "verse_runner_agent.py", "verse_agent.py")):
            continue
        try:
            spec = importlib.util.spec_from_file_location("rv_" + os.path.basename(path)[:-3], path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception:
            continue
        for obj in vars(mod).values():
            if isinstance(obj, type) and hasattr(obj, "perform") and obj.__name__ != "BasicAgent" \
                    and obj.__module__ == mod.__name__:
                try:
                    agent = obj()
                except Exception:
                    continue
                lens = agent_lens(agent)
                manifest = getattr(mod, "__manifest__", {}) or {}
                MANIFESTS[path] = (manifest, (getattr(agent, "metadata", {}) or {}).get("parameters", {}))
                for entry in (manifest.get("say", []) or []) + button_phrases(manifest.get("button")):
                    phrase, fixed = (entry, {}) if isinstance(entry, str) else (entry.get("phrase", ""), entry.get("args", {}))
                    PHRASES[_norm(phrase)] = ((lambda f, _l=lens, _a=fixed, **a: _l(f, **{**_a, **a})) if fixed else lens, phrase)
                for n in [getattr(agent, "name", obj.__name__), manifest.get("display_name", "")] + \
                        list(manifest.get("aliases", [])):
                    if n:
                        found.setdefault(_key(n), lens)
    return found


MANIFESTS: dict = {}  # agent file -> (its __manifest__, its parameters), filled by load_agents
PHRASES: dict = {}   # "save it" -> (lens, "save it"), filled by load_agents from each agent's __manifest__["say"]


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (t or "").lower())).strip()


def button_phrases(button) -> list:
    """A helper shown as a button people already know from screens: {"label": "Save", "action": {...}}.
    It answers to every way people say pressing it, and the same label is what computer use clicks."""
    if not button:
        return []
    buttons = button if isinstance(button, list) else [button]
    out = []
    for b in buttons:
        label = b if isinstance(b, str) else b.get("label", "")
        args = {} if isinstance(b, str) else b.get("args", {})
        low = label.lower()
        for form in (f"press {low}", f"hit {low}", f"click {low}", f"tap {low}", f"press the {low} button",
                     f"hit the {low} button", f"click the {low} button", f"tap the {low} button"):
            out.append({"phrase": form, "args": args} if args else form)
    return out


def match_phrase(text: str, phrases: dict | None = None):
    """'Save it with a done note' -> (lens, 'save it', 'with a done note'). Longest phrase said at the start wins."""
    phrases = PHRASES if phrases is None else phrases
    said = _norm(re.sub(r"^(then|and|now|please)\s+", "", text.strip(), flags=re.I))
    said = re.sub(r"^(?:then |and |now |please )+", "", said)
    best = None
    for key, (lens, phrase) in phrases.items():
        if said == key or said.startswith(key + " "):
            if not best or len(key) > len(best[0]):
                best = (key, lens, phrase)
    if not best:  # forgiving: the helper whose words overlap most ("list the open apps" -> "what's still open")
        stop = {"the", "a", "my", "me", "what", "s", "is", "are", "still", "on", "of", "and", "to", "tell", "check", "see", "show", "which", "how"}
        said_w = set(said.split()) - stop
        scored = []
        for key, (lens, phrase) in phrases.items():
            kw = set(key.split()) - stop
            hit = len(said_w & {w.rstrip("s") for w in kw} | said_w & kw)
            if hit:
                scored.append((hit, len(key), lens, phrase))
        if not scored:
            return None
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return scored[0][2], scored[0][3], ""
    words = len(best[0].split())
    rest = " ".join(re.sub(r"^(then|and|now|please)\s+", "", text.strip(), flags=re.I).split()[words:])
    return best[1], best[2], rest.strip(" ,.")


FRAME_KEYS = ("input", "text", "frame", "query", "data", "content", "request")


def agent_lens(agent) -> Lens:
    params = (getattr(agent, "metadata", {}) or {}).get("parameters", {}) or {}
    props, required = params.get("properties", {}) or {}, params.get("required", []) or []

    def lens(frame: str, **args) -> str:
        kw = {k: v for k, v in args.items() if k in props}
        if "_" in args and props:
            kw.setdefault(next(iter(props)), args["_"])
        for k in FRAME_KEYS:
            if k in props and k not in kw and frame:
                kw[k] = frame
        for k in required:
            kw.setdefault(k, "")
        return str(agent.perform(**kw))
    lens.__name__ = getattr(agent, "name", "agent")
    return lens


def brainstem_model(url: str = "http://127.0.0.1:7071", timeout: int = 240) -> Model:
    """A Brainstem's own model does any step that has no lens (join, questions, plain steps)."""
    def model(task: str, frame: str) -> str:
        prompt = ("Do this one step yourself in plain words. Do not call any agent or tool. Under 80 words.\n"
                  f"Step: {task}\nMaterial:\n{(frame or '')[:6000]}")
        out = chat(url, prompt, timeout=timeout)
        return (out.get("response") or "").split("|||VOICE|||")[0].strip()
    return model


def chat(url: str, text: str, history=None, session_id=None, timeout: int = 300) -> dict:
    """POST a Brainstem's /chat. Returns its JSON ({response, voice_response, agent_logs})."""
    body = {"user_input": text, "conversation_history": history or []}
    if session_id:
        body["session_id"] = session_id
    req = urllib.request.Request(url.rstrip("/") + "/chat", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def sing(url: str, verse_text: str, go: bool = True, timeout: int = 300) -> str:
    """Hand a whole verse to a Brainstem through /chat, the way a person would say it."""
    if not is_verse(verse_text):
        verse_text = f"R, A, P, P, verse. {verse_text.strip()} Seal."
    out = chat(url, verse_text + (" Go." if go else ""), timeout=timeout)
    return (out.get("voice_response") or out.get("response") or "").split("|||VOICE|||")[0].strip()


def interview(url: str, live: bool = False) -> dict:
    """Trust but verify a Brainstem before using it: tell it something to remember, start a clean chat with no
    history, ask what it remembers, and (optionally) ask for the top Hacker News story to prove it reaches a live API."""
    import random
    word = random.choice(["lighthouse", "pinecone", "marigold", "harbor", "saffron", "lantern"]) + str(random.randint(10, 99))
    checks = []
    chat(url, f"Please remember this: my test word is {word}.", session_id="interview-a")
    back = chat(url, "What is my test word? Answer with just the word.", history=[], session_id="interview-b")
    said = (back.get("response") or "").split("|||VOICE|||")[0]
    checks.append({"check": "remembers across a clean chat", "ok": word.lower() in said.lower(), "said": said.strip()[:200]})
    if live:
        hn = chat(url, "What is the top story on Hacker News right now? One line.", history=[], session_id="interview-c")
        txt = (hn.get("response") or "").split("|||VOICE|||")[0]
        used = json.dumps(hn.get("agent_logs", "")).lower()
        checks.append({"check": "reaches a live API (Hacker News)", "ok": "hacker" in used or "hn" in used or "news" in used,
                       "said": txt.strip()[:200]})
    return {"url": url, "ok": all(c["ok"] for c in checks), "checks": checks}


# ---------------------------------------------------------------- run

@dataclasses.dataclass
class Result:
    tile: str
    trail: list
    trace: list
    stopped: str = ""          # why it stopped early ("" when it ran to the end)
    needs: str = ""            # what it needs from the person (ask for x / send yes)

    @property
    def ok(self):
        return not self.stopped

    def to_dict(self):
        return dataclasses.asdict(self) | {"ok": self.ok}

    def say(self):
        head = f"Ran {len(self.trail)} step{'s' if len(self.trail) != 1 else ''}: {' > '.join(self.trail) or 'none'}."
        shown = [e for e in self.trace if e["verb"] in ("through", "say", "split", "press", "send", "find", "fill") and e["tile"]]
        if len(shown) > 1:  # every step's answer, not just the last one
            body = "\n".join(f"- {e['name']}: {e['tile'].strip()}" for e in shown)
            return f"{head}\n\n{body}" + (f"\n\n{self.stopped}" if self.stopped else "")
        tail = f"\n\n{self.stopped}" if self.stopped else ""
        return f"{head}\n\n{self.tile}{tail}".strip()


def _h(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def verify_trace(trace: list) -> bool:
    """True when every entry's hash is right and each points at the one before it."""
    prev = "0" * 64
    for e in trace:
        body = {k: v for k, v in e.items() if k != "hash"}
        if e.get("prev") != prev or _h(body) != e.get("hash"):
            return False
        prev = e["hash"]
    return True


def _no_model(task, frame):
    raise VerseError(f"No lens named for '{task}' and no model to do it.")


def run(steps, lenses: dict | None = None, model: Model | None = None, *,
        confirm: Callable[[str, str], bool] | None = None, ask: Callable[[str], str] | None = None,
        source: str = "live", frame: str = "", max_rounds: int = 5, on_step: Callable | None = None,
        phrases: dict | None = None) -> Result:
    """Run parsed steps (or verse text). lenses: name -> lens(frame, **args). model: does unnamed steps.
    confirm(what, frame) must return True for each send; it is asked fresh every time. ask(x) fills ask-for."""
    if isinstance(steps, str):
        steps = parse(steps)
    lenses = {_key(k): v for k, v in (lenses or {}).items()}
    phrases = PHRASES if phrases is None else phrases
    model = model or _no_model
    trace, trail, side, branches = [], [], {}, []
    state = {"frame": frame}

    def log(verb, name, tile):
        prev = trace[-1]["hash"] if trace else "0" * 64
        e = {"n": len(trace) + 1, "verb": verb, "name": name, "frame_in": _h(state["frame"])[:16],
             "tile": tile, "at": round(time.time(), 3), "prev": prev}
        e["hash"] = _h(e)
        trace.append(e)
        if on_step:
            on_step(e)

    def through(name, args, fr):
        lens = lenses.get(_key(name))
        if lens:
            try:
                tile = str(lens(fr, **args))
            except Exception as e:  # a lens failing is a tile, never a crash
                tile = f"{name} failed: {e}"
            trail.append(name)
        else:
            extra = " ".join(f"{k} {v}" for k, v in args.items() if k != "_") or args.get("_", "")
            tile = model(f"{name} {extra}".strip(), fr)
            trail.append(f"{name} (model)")
        return tile

    def go(seq, depth=0):
        i = 0
        while i < len(seq):
            s = seq[i]
            if s.verb == "bring":
                key = s.name.lower()
                state["frame"] = next((v for k, v in side.items() if k in key), state["frame"] or s.name)
                log("bring", s.name, state["frame"][:500])
            elif s.verb == "through":
                state["frame"] = through(s.name, s.args, state["frame"])
                log("through", s.name, state["frame"])
            elif s.verb == "ask_for":
                if not ask:
                    return f"Needs {s.name} from you.", s.name
                ans = ask(s.name)
                state["frame"] = f"{state['frame']}\n{s.name}: {ans}".strip()
                log("ask_for", s.name, ans)
            elif s.verb == "set_aside":
                side[s.name.lower()] = state["frame"]
                log("set_aside", s.name, "")
            elif s.verb == "split":
                branches[:] = [(b, through(b, {}, state["frame"])) for b in s.branches]
                for b, t in branches:
                    log("split", b, t)
            elif s.verb == "join":
                joined = "\n\n".join(f"{n}:\n{t}" for n, t in branches) or state["frame"]
                lens = lenses.get("join")
                state["frame"] = str(lens(joined)) if lens else model("Join these results into one short answer", joined)
                trail.append("Join")
                log("join", "Join", state["frame"])
            elif s.verb in ("find", "fill"):
                screen = lenses.get("screen")
                on = s.args.get("on", "")
                if screen:
                    tile = str(screen(state["frame"], do=s.verb, target=s.name, **{k: v for k, v in s.args.items() if k != "on"}, on=on))
                else:
                    tile = model(s.text + " (only look and describe; change nothing)", state["frame"])
                state["frame"] = tile
                trail.append(f"{s.verb} {s.name}")
                state["screen"] = on or state.get("screen") or "the screen"
                log(s.verb, s.name, tile)
            elif s.verb == "press":
                on_screen = s.args.get("on") or state.get("screen")
                hit = None if on_screen else match_phrase(f"press {s.name}", phrases)
                if hit:  # a button of your own helpers: your own button, runs like any helper
                    lens, phrase, _ = hit
                    state["frame"] = str(lens(state["frame"], **{k: v for k, v in s.args.items() if k != "on"}))
                    trail.append(phrase)
                    log("press", s.name, state["frame"])
                else:  # a button on someone else's screen acts in the world: say what you see, ask, every time
                    on = on_screen if on_screen and on_screen != "the screen" else None
                    question = f"I see a {s.name} button{' on ' + on if on else ''}. Should I press it?"
                    if source != "live":
                        return f"Read-only: this verse came from {source}, so I won't press {s.name}.", ""
                    if not confirm or not confirm(question, state["frame"]):
                        return question, "yes"
                    screen = lenses.get("screen")
                    tile = str(screen(state["frame"], do="press", target=s.name, on=on or "")) if screen else f"Pressed {s.name}."
                    state["frame"] = tile
                    trail.append(f"press {s.name}")
                    log("press", s.name, tile)
            elif s.verb == "send":
                what = s.name or "send"
                if source != "live":
                    return f"Read-only: this verse came from {source}, so it will not send.", ""
                if not confirm or not confirm(what, state["frame"]):
                    return f"Stopped before send: sending needs your yes.", "yes"
                lens = lenses.get("send")
                tile = str(lens(state["frame"], what=what)) if lens else "Sent."
                trail.append("Send")
                log("send", what, tile)
            elif s.verb == "question":
                verdict = model(f"Answer only YES or NO, then the reason: {s.name}", state["frame"])
                yes = verdict.strip().upper().startswith("YES")
                trail.append(f"{s.name} ({'yes' if yes else 'no'})")
                log("question", s.name, verdict)
                r = go(s.yes if yes else s.no, depth + 1)
                if r:
                    return r
            elif s.verb == "keep":
                for _ in range(max_rounds):
                    r = go(s.body, depth + 1)
                    if r:
                        return r
                    if model(f"Answer only YES or NO: is this true? {s.until}", state["frame"]).strip().upper().startswith("YES"):
                        break
            elif s.verb == "go_back":
                if depth > 2 or not (1 <= s.target <= len(trace)):
                    log("go_back", str(s.target), "skipped")
                else:
                    state["frame"] = f"{trace[s.target - 1]['tile']}\n{s.name}".strip()
                    log("go_back", str(s.target), state["frame"])
            elif s.verb == "teach":  # remembering is the Brainstem's own memory's job; the runner only says it back
                state["frame"] = think([s])
                trail.append(f"phrase '{s.name}'")
                log("teach", s.name, state["frame"])
            else:
                hit = match_phrase(s.name, phrases)
                if hit:
                    lens, phrase, rest = hit
                    try:
                        state["frame"] = str(lens(state["frame"], **(_args(re.sub(r"^(?:(?:and|then|with|using|add|adding|put|attach)\s+)+", "", rest, flags=re.I)) if rest else {})))
                    except Exception as e:
                        state["frame"] = f"{phrase} failed: {e}"
                    trail.append(phrase)
                    log("say", phrase, state["frame"])
                else:
                    state["frame"] = model(s.name, state["frame"])
                    trail.append(s.name)
                    log("plain", s.name, state["frame"])
            i += 1
        return None

    stop = go(steps)
    stopped, needs = stop if stop else ("", "")
    return Result(tile=state["frame"], trail=trail, trace=trace, stopped=stopped, needs=needs)


# ---------------------------------------------------------------- the screen (same meaning, drawn as buttons)

def panel(folder: str) -> list[dict]:
    """Every helper in `folder` as a button: its label, the words people say, and the details it takes."""
    folder = os.path.abspath(os.path.expanduser(folder))
    load_agents(folder)
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*_agent.py"))):
        man, params = MANIFESTS.get(path, ({}, {}))
        say_ = [e if isinstance(e, str) else e.get("phrase", "") for e in man.get("say", [])]
        b = man.get("button")
        label = (b if isinstance(b, str) else (b or {}).get("label")) if b else (say_[0].capitalize() if say_ else "")
        if not label:
            continue
        fields = [k for k, v in (params.get("properties") or {}).items()
                  if (v or {}).get("type") == "string" and k not in ("action", "verse", "feature", "value")]
        out.append({"label": label, "says": say_[:3], "fields": fields,
                    "sentence": f"Press {label.lower()}" if b else (say_[0].capitalize() if say_ else label)})
    return out


PAGE = r"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Your buttons</title><style>
body{font:17px -apple-system,system-ui,sans-serif;margin:0;background:#f6f5f2;color:#1d1d1f}
main{max-width:640px;margin:0 auto;padding:28px 18px}h1{font-size:26px;margin:0 0 4px}p.sub{color:#666;margin:0 0 22px}
.b{background:#fff;border-radius:14px;padding:14px 16px;margin:0 0 12px;box-shadow:0 1px 3px #0001;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{font:600 17px inherit;border:0;border-radius:10px;padding:10px 18px;background:#0a7cff;color:#fff;cursor:pointer}
input{font:16px inherit;border:1px solid #ccc;border-radius:8px;padding:9px;flex:1;min-width:140px}
.say{width:100%;color:#888;font-size:14px}#out{white-space:pre-wrap;background:#fff;border-radius:14px;padding:14px 16px;min-height:40px}
</style><main><h1>Your buttons</h1><p class=sub>Press one, or just say it. Every button is a sentence.</p>
<div id=bs></div><h2 style="font-size:18px">What happened</h2><div id=out>Nothing yet.</div></main><script>
const bs=__BUTTONS__;const el=document.getElementById('bs'),out=document.getElementById('out');
bs.forEach(b=>{const d=document.createElement('div');d.className='b';const btn=document.createElement('button');btn.textContent=b.label;d.append(btn);
const ins=b.fields.map(f=>{const i=document.createElement('input');i.placeholder=f;d.append(i);return [f,i]});
const s=document.createElement('div');s.className='say';s.textContent='Or say: "'+(b.says[0]||b.sentence)+'"';d.append(s);
btn.onclick=async()=>{let t=b.sentence;ins.forEach(([f,i])=>{if(i.value)t+=', and add the '+f+' '+i.value});
out.textContent='"'+t+'"  ...';const r=await fetch('/v1/run',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({verse:'R, A, P, P, verse. '+t+'. Seal.'})});const j=await r.json();
out.textContent='"'+t+'"\n\n'+(j.tile||j.error||'')+(j.stopped?'\n\n'+j.stopped:'')};el.append(d)});
</script>"""


class VerseRunnerAgent(BasicAgent):
    def __init__(self):
        self.name = "VerseRunner"
        self.metadata = {
            "name": self.name,
            "description": ("Runs a whole RAPP verse end to end in ONE call: give it the full verse text and it runs "
                            "every step in order (through, split, join, set aside, ask/if yes/if no, keep until), "
                            "calling the named agents itself. Use whenever the person says 'go' on a verse with more "
                            "than one step. Set yes=true only when the person said yes to sending in this message."),
            "parameters": {"type": "object", "properties": {
                "verse": {"type": "string", "description": "The full verse, from 'R, A, P, P, verse' to 'seal'."},
                "yes": {"type": "boolean", "description": "The person said yes to sending, live, in this message."}},
                "required": ["verse"]},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def system_context(self):
        return ("<plans>When the person teaches you a phrase (When I say goodnight, check the battery and ...), save it "
                "with your own memory, then say back in one warm plain sentence what you'll do whenever they say it. "
                "When they later say a phrase you remember, or any plan with several steps, call VerseRunner once with "
                "the steps as plain sentences, then answer in one or two warm sentences that cover every step's result.</plans>")

    def perform(self, verse="", yes=False, **_):
        if not is_verse(verse):
            verse = f"R, A, P, P, verse. {verse.strip()} Seal."
        try:
            steps = parse(verse)
        except VerseError as e:
            return str(e)
        port = int((os.getenv("PORT") or "7071").strip() or 7071)
        here = os.path.dirname(os.path.abspath(__file__))
        r = run(steps, load_agents(here), brainstem_model(f"http://127.0.0.1:{port}"),
                confirm=lambda what, frame: yes is True)
        return r.say()
