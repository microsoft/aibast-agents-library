"""Standing answers: questions the Brainstem asks itself on a schedule, so the answer is waiting.

One file, two front ends:
- Brainstem loads it as an agent (StandingAnswers): add, list, remove, latest, run.
- Anything that can run a command on a timer wakes it:
  python3 standing_answers_agent.py run

It talks to the Brainstem only through /health and /chat. It keeps its own small
record on the person's device. It never sends anything off the device.
Each question is asked once per period; a missed period is caught up once, not replayed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from basic_agent import BasicAgent
except ImportError:  # running as a plain script outside Brainstem
    class BasicAgent:  # type: ignore[no-redef]
        def __init__(self, name=None, metadata=None):
            self.name, self.metadata = name, metadata


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/standing-answers",
    "version": "0.1.0",
    "display_name": "Standing Answers",
    "description": (
        "Keeps a short list of questions and asks them on a schedule through the Brainstem's own chat, "
        "so the answer is waiting before the person asks. Runs on the person's device only."
    ),
    "author": "AIBAST",
    "tags": ["automation", "schedule", "brainstem"],
    "category": "general",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

OPERATIONS = ("add", "list", "remove", "latest", "run")
EVERY = ("daily", "weekdays", "weekly")
NOTE = ("Asked automatically on this device. Experimental, not an officially supported Microsoft product. "
        "Check an answer before acting on it.")
KEEP = 20  # answers kept per question


def _folder() -> str:
    path = os.environ.get("AIBAST_STANDING_DIR") or os.path.join(os.path.expanduser("~"), ".brainstem", "standing-answers")
    os.makedirs(path, exist_ok=True)
    return path


def _load() -> dict:
    try:
        with open(os.path.join(_folder(), "standing.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) and isinstance(data.get("items"), list) else {"items": []}
    except (OSError, ValueError):
        return {"items": []}


def _save(data: dict) -> None:
    path = os.path.join(_folder(), "standing.json")
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(path + ".tmp", path)  # all or nothing


def period(every: str, now: dt.datetime) -> str:
    """The name of the period a question belongs to now. Empty means: not due in this period."""
    if every == "weekly":
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"
    if every == "weekdays" and now.weekday() >= 5:
        return ""
    return now.strftime("%Y-%m-%d")


def _find(data: dict, key: str):
    key = (key or "").strip().lower()
    for item in data["items"]:
        if key and (item["id"] == key or item["label"].lower() == key):
            return item
    return None


def add(question: str, every: str = "weekly", label: str = "") -> dict:
    question = (question or "").strip()
    if not question:
        return {"ok": False, "summary": "Say the question to ask."}
    if every not in EVERY:
        return {"ok": False, "summary": f"Say how often: {', '.join(EVERY)}."}
    data = _load()
    label = (label or "").strip() or re.sub(r"\s+", " ", question)[:40]
    if _find(data, label):
        return {"ok": False, "summary": f"There is already a standing question called '{label}'. Remove it first or use another name."}
    item = {"id": uuid.uuid4().hex[:8], "label": label, "question": question, "every": every, "answers": []}
    data["items"].append(item)
    _save(data)
    return {"ok": True, "id": item["id"], "label": label, "every": every,
            "summary": f"'{label}' will be asked {every}. The answer will be waiting here.", "undo": f"remove {label}"}


def list_items() -> dict:
    items = _load()["items"]
    return {"ok": True, "count": len(items),
            "items": [{"id": i["id"], "label": i["label"], "every": i["every"], "question": i["question"],
                       "answered": len(i["answers"]), "last": (i["answers"][-1]["period"] if i["answers"] else "")} for i in items],
            "summary": f"{len(items)} standing question(s)." if items else "No standing questions yet."}


def remove(key: str, confirm: bool = False) -> dict:
    data = _load()
    item = _find(data, key)
    if not item:
        return {"ok": True, "summary": "It was not there. Nothing changed."}
    if not confirm:
        return {"ok": False, "needs_confirmation": True,
                "summary": f"This removes '{item['label']}' and its {len(item['answers'])} saved answer(s). Confirm to remove."}
    data["items"] = [i for i in data["items"] if i["id"] != item["id"]]
    _save(data)
    return {"ok": True, "summary": f"Removed '{item['label']}'."}


def latest(key: str = "") -> dict:
    data = _load()
    items = [_find(data, key)] if key else data["items"]
    out = [{"label": i["label"], "period": i["answers"][-1]["period"], "asked_at": i["answers"][-1]["asked_at"],
            "answer": i["answers"][-1]["answer"]} for i in items if i and i["answers"]]
    return {"ok": True, "note": NOTE, "answers": out,
            "summary": f"{len(out)} answer(s) waiting." if out else "Nothing has been answered yet."}


def _ask(base: str, question: str, timeout: int = 300) -> str:
    req = urllib.request.Request(base + "/chat", data=json.dumps({"user_input": question, "conversation_history": []}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (the person's own Brainstem)
        return (json.loads(resp.read().decode("utf-8")).get("response") or "").strip()


def run(base: str = "http://localhost:7071", now: dt.datetime | None = None, ask=_ask) -> dict:
    """Asks every question that is due and not yet answered for its period. Safe to call as often as you like."""
    now = now or dt.datetime.now()
    base = (base or "http://localhost:7071").rstrip("/")
    data, asked, failed, skipped = _load(), [], [], 0
    for item in data["items"]:
        name = period(item["every"], now)
        if not name or any(a["period"] == name for a in item["answers"]):
            skipped += 1
            continue
        try:
            answer = ask(base, item["question"])
        except (urllib.error.URLError, OSError, ValueError) as exc:
            failed.append({"label": item["label"], "why": str(exc)[:160]})
            continue
        if not answer:
            failed.append({"label": item["label"], "why": "The Brainstem gave no answer. It may not be signed in."})
            continue
        item["answers"] = (item["answers"] + [{"period": name, "asked_at": now.isoformat(timespec="seconds"), "answer": answer}])[-KEEP:]
        asked.append(item["label"])
        _save(data)  # after each answer, so a stop half way loses nothing
    return {"ok": not failed, "asked": asked, "failed": failed, "already_done_or_not_due": skipped,
            "summary": f"Asked {len(asked)}, {skipped} not due or already answered, {len(failed)} failed."}


def dispatch(kw: dict) -> dict:
    op = kw.get("operation")
    if op == "add":
        return add(kw.get("question", ""), kw.get("every") or "weekly", kw.get("label", ""))
    if op == "list":
        return list_items()
    if op == "remove":
        return remove(kw.get("label") or kw.get("id") or "", bool(kw.get("confirm")))
    if op == "latest":
        return latest(kw.get("label") or kw.get("id") or "")
    if op == "run":
        return run(kw.get("url") or os.environ.get("BRAINSTEM_URL") or "http://localhost:7071")
    return {"ok": False, "summary": f"Unknown step. Use one of: {', '.join(OPERATIONS)}."}


class StandingAnswersAgent(BasicAgent):
    def __init__(self):
        self.name = "StandingAnswers"
        self.metadata = {
            "name": self.name,
            "description": (
                "Keeps questions the person wants answered on a schedule without asking again, for example "
                "'every Monday, which deals are stalled?'. Use 'add' to keep a question (every: daily, weekdays "
                "or weekly), 'latest' to show the answers that are waiting, 'list' to show what is kept, and "
                "'remove' with confirm=true only after the person agrees."),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": list(OPERATIONS)},
                    "question": {"type": "string", "description": "For add: the question, in the person's own words."},
                    "every": {"type": "string", "enum": list(EVERY), "description": "For add: how often. Default weekly."},
                    "label": {"type": "string", "description": "A short name for the question. For remove and latest: which one."},
                    "confirm": {"type": "boolean", "description": "For remove: true only after the person agrees."},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        return json.dumps(dispatch(kwargs), indent=2)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Standing answers for a Brainstem.")
    p.add_argument("operation", choices=OPERATIONS)
    p.add_argument("--question", default="")
    p.add_argument("--every", default="weekly", choices=EVERY)
    p.add_argument("--label", default="")
    p.add_argument("--url", default="")
    p.add_argument("--yes", action="store_true")
    a = p.parse_args(argv)
    out = dispatch({"operation": a.operation, "question": a.question, "every": a.every, "label": a.label,
                    "url": a.url, "confirm": a.yes})
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") or out.get("needs_confirmation") else 1


if __name__ == "__main__":
    sys.exit(main())
