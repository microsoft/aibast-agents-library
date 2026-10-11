"""The model door: one function that asks a Brainstem's /chat and returns the text.

PM_BRAINSTEM_URL (default http://localhost:7096) picks the Brainstem. Locally it's the dedicated
prototype Brainstem; in the cloud, the Azure Function Brainstem. Same call either way.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request


class ModelError(RuntimeError):
    pass


def complete(prompt: str, timeout: int = 300) -> str:
    url = os.environ.get("PM_BRAINSTEM_URL", "http://localhost:7096").rstrip("/") + "/chat"
    # Ask for a direct answer so the orchestrator doesn't route the prompt into a tool.
    body = json.dumps({"user_input": prompt + "\n\nAnswer directly. Do not call any tools."}).encode()
    for attempt in range(3):
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return (json.loads(r.read()).get("response") or "").split("|||VOICE|||")[0]
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < 2:
                time.sleep(3 * 2 ** attempt)
                continue
            raise ModelError(f"Brainstem /chat returned {e.code}") from None
        except urllib.error.URLError as e:
            raise ModelError(f"No Brainstem at {url} ({e.reason})") from None
    raise ModelError("Brainstem kept failing")


def extract_json(text: str, kind: type = dict):
    """The JSON a model returned, wherever it sits in the reply (fences, prose, placeholders)."""
    for block in re.findall(r"```(?:json)?\s*(.*?)```", text, re.S):
        try:
            v = json.loads(block)
            if isinstance(v, kind):
                return v
        except json.JSONDecodeError:
            pass
    dec, best, size = json.JSONDecoder(), None, -1
    for i, ch in enumerate(text):
        if ch == ("{" if kind is dict else "["):
            try:
                v, end = dec.raw_decode(text, i)
            except json.JSONDecodeError:
                continue
            if isinstance(v, kind) and end - i > size:
                best, size = v, end - i
    if best is None:
        raise ValueError("no JSON in the reply")
    return best


def agent_result(chat_reply: dict, agent: str) -> dict | None:
    """An agent's own JSON from a /chat reply's agent_logs ('[Agent] {json}'). Exact data, not prose."""
    m = re.search(r"\[" + re.escape(agent) + r"\] (\{.*\})", chat_reply.get("agent_logs") or "", re.S)
    if not m:
        return None
    try:
        return extract_json(m.group(1), dict)
    except ValueError:
        return None
