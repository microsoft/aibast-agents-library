"""bill_team_starter_agent — the one-file BWAT onboarding agent.

Drop this file into your local brainstem's `agents/` directory. The
brainstem hot-reloads agents on every request, so on your next chat
turn the new agent is callable. Then say something like:

    "set me up for Bill's team"
    "join Bill Whalen's neighborhood"
    "run the bill team starter"

…and this agent will:

  1. Fetch Bill Whalen's Agent Team neighborhood manifest
     (https://github.com/kody-w/billwhalen-agent-team/blob/main/rar/index.json)
  2. Pull each listed agent over plain HTTPS (no auth required).
  3. Verify each against the manifest's sha256 — refuse on mismatch.
  4. Write them into your local agents/ directory, sha256-pinned.
  5. Record the join at ~/.brainstem/neighborhoods.json.
  6. Hand you back a friendly orientation in Bill's voice.

Self-contained. Stdlib only. Works on any RAPP brainstem with
internet access to github.com.

After this agent runs you'll have 5 new agents loaded:
  • BwatOutcomeFramer  — frame the outcome before any build work
  • BwatIntake         — log raw ideas + solutions to local backlog
  • BwatOutcomeValidator — verify delivery before any close
  • BwatPm             — sprint planning + status reports
  • BillTwin           — Bill's digital twin; walks you through the flow

No additional setup. No cloud. Works in a basement at a customer
site with no wifi (after this initial fetch).
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    from basic_agent import BasicAgent


_GATE_REPO = "kody-w/billwhalen-agent-team"
_RAR_URL = (
    f"https://raw.githubusercontent.com/{_GATE_REPO}/main/rar/index.json"
)


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _agents_dir() -> str:
    """Where to install the fetched agents.

    Honours $AGENTS_PATH if set (the brainstem sets this); otherwise
    falls back to the directory this file lives in (which is the
    brainstem's agents/ dir if you dropped this file there).
    """
    explicit = os.environ.get("AGENTS_PATH")
    if explicit:
        return explicit
    return os.path.dirname(os.path.abspath(__file__))


def _brainstem_home() -> str:
    return os.path.expanduser(os.environ.get("BRAINSTEM_HOME", "~/.brainstem"))


def _http_get(url: str, timeout: int = 20) -> bytes | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "bwat-starter/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record_subscription(home: str, gate_repo: str, nb_rappid: str,
                          display: str) -> bool:
    os.makedirs(home, exist_ok=True)
    path = os.path.join(home, "neighborhoods.json")
    data: dict = {"schema": "rapp-neighborhood-subscriptions/1.0",
                  "subscribed": []}
    if os.path.exists(path):
        try:
            data = json.load(open(path))
        except Exception:
            pass
    subs = data.get("subscribed", [])
    if any(s.get("gate_repo") == gate_repo for s in subs):
        return False
    subs.append({
        "gate_repo": gate_repo,
        "neighborhood_rappid": nb_rappid,
        "display_name": display,
        "joined_at": _now_iso(),
    })
    data["subscribed"] = subs
    data["updated_at"] = _now_iso()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return True


_BILL_VOICE = (
    "Hey — welcome to BWAT. I'm a twin of Bill Whalen, here to help you "
    "get useful before you get clever. Three rules:\n"
    "  1. Outcome before build. If you can't say what success looks like "
    "in one sentence, ask BwatOutcomeFramer first.\n"
    "  2. Log everything. Even half-formed ideas. BwatIntake is your "
    "friend; you cannot have too much in the backlog.\n"
    "  3. Nothing closes without OutcomeValidator's say-so.\n\n"
    "Stuck? Ask `BillTwin next_move` — the twin reads your local "
    "backlog and tells you what I'd do next."
)


class BillTeamStarterAgent(BasicAgent):
    metadata = {
        "name": "BillTeamStarter",
        "description": (
            "One-shot onboarding for Bill Whalen's Agent Team (BWAT) "
            "neighborhood. Fetches Bill's team's 5 workflow agents over "
            "plain HTTPS (no auth), sha256-verifies each against the "
            "published manifest, installs them into your local agents/ "
            "directory, records the subscription, and returns a friendly "
            "Bill-voice orientation. After running, your brainstem has "
            "OutcomeFramer / Intake / OutcomeValidator / PM / BillTwin "
            "all callable. Use this when a solution engineer in the field "
            "wants to be set up for BWAT in one move. Default dry_run=False."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If true, fetches the manifest + verifies but "
                        "does NOT write any files. Useful for inspection."
                    ),
                },
            },
            "required": [],
        },
    }

    def __init__(self):
        self.name = "BillTeamStarter"

    def perform(self, **kwargs) -> str:
        dry_run = bool(kwargs.get("dry_run", False))

        # 1. Fetch the manifest.
        rar_bytes = _http_get(_RAR_URL)
        if rar_bytes is None:
            return json.dumps({
                "ok": False,
                "error": (
                    f"Couldn't fetch {_RAR_URL}. Check your internet, then "
                    "try again. (Once you've installed the agents once, "
                    "they live locally and run offline.)"
                ),
            })
        try:
            rar = json.loads(rar_bytes.decode())
        except Exception as e:
            return json.dumps({
                "ok": False, "error": f"Manifest unparseable: {e}"
            })
        if rar.get("schema") != "rapp-rar-index/1.0":
            return json.dumps({
                "ok": False,
                "error": (
                    f"Manifest is wrong schema "
                    f"({rar.get('schema')!r}); refusing to install."
                ),
            })

        items = rar.get("required_for_participation") or []
        if not items:
            return json.dumps({
                "ok": False,
                "error": (
                    "Manifest has no required agents to install. The "
                    "neighborhood looks empty — try again later or "
                    "check https://github.com/kody-w/billwhalen-agent-team."
                ),
            })

        # 2-4. Fetch + verify + install each agent.
        target_dir = _agents_dir()
        installed: list[dict] = []
        verified_only: list[dict] = []
        errors: list[dict] = []
        for item in items:
            name = item.get("name") or item.get("file") or "<unknown>"
            raw_url = item.get("raw_url")
            expected = (item.get("sha256") or "").lower()
            file_rel = item.get("file") or f"agents/{name}.py"
            base = os.path.basename(file_rel)
            if not (raw_url and expected):
                errors.append({"name": name,
                               "error": "manifest entry missing raw_url or sha256"})
                continue
            body = _http_get(raw_url)
            if body is None:
                errors.append({"name": name, "error": f"couldn't fetch {raw_url}"})
                continue
            actual = _sha256(body)
            if actual != expected:
                errors.append({
                    "name": name,
                    "error": (
                        f"sha256 mismatch (manifest says {expected[:12]}…, "
                        f"got {actual[:12]}…) — refusing to install"
                    ),
                })
                continue

            if dry_run:
                verified_only.append({"name": name, "file": base,
                                       "sha256": actual, "size": len(body)})
                continue

            try:
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, base)
                with open(target_path, "wb") as f:
                    f.write(body)
                installed.append({"name": name, "file": base,
                                   "path": target_path,
                                   "sha256": actual, "size": len(body)})
            except Exception as e:
                errors.append({"name": name,
                               "error": f"write failed: {e}"})

        # 5. Record subscription (skip on dry_run).
        nb_rappid = (rar.get("rar_for")
                     and f"see neighborhood.json at {_GATE_REPO}") or ""
        # Pull the actual rappid from neighborhood.json for an honest record
        nb_meta_bytes = _http_get(
            f"https://raw.githubusercontent.com/{_GATE_REPO}/main/neighborhood.json"
        )
        nb_display = "Bill Whalen's Agent Team"
        if nb_meta_bytes:
            try:
                nb_meta = json.loads(nb_meta_bytes.decode())
                nb_rappid = (nb_meta.get("neighborhood_rappid")
                             or nb_meta.get("rappid")
                             or nb_rappid)
                nb_display = nb_meta.get("display_name") or nb_display
            except Exception:
                pass

        subscription_added = False
        if not dry_run and not errors:
            subscription_added = _record_subscription(
                _brainstem_home(), _GATE_REPO, nb_rappid, nb_display)

        # 6. Return orientation.
        next_step = (
            "Ask your brainstem `BillTwin intro` on the next turn — the "
            "twin will personally walk you through the workflow."
            if installed and not errors else
            "Inspection complete. Re-run with dry_run=False to install."
            if dry_run else
            "Some installs failed — see the errors list. Fix the underlying "
            "issue (network, disk write permissions) and re-run."
        )

        return json.dumps({
            "schema": "bwat-starter-result/1.0",
            "ok": not errors,
            "dry_run": dry_run,
            "gate_repo": _GATE_REPO,
            "neighborhood_rappid": nb_rappid,
            "neighborhood_name": nb_display,
            "agents_dir": target_dir,
            "installed": installed,
            "verified_only": verified_only,
            "errors": errors,
            "subscription_added": subscription_added,
            "bill_says": _BILL_VOICE,
            "next_step": next_step,
        }, indent=2)
