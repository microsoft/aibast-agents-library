"""AIBAST Easy Mode — reusable Brainstem workshop bootstrap and router."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/easy-mode",
    "version": "1.0.0",
    "display_name": "AIBAST Easy Mode",
    "description": (
        "Turns a named AIBAST workshop into a personless Brainstem + Copilot "
        "run: fetch the task cartridge, test the solution, deploy its Draft, "
        "and return the evidence verdict."
    ),
    "author": "AIBAST",
    "tags": [
        "easy-mode",
        "personless-harness",
        "brainstem",
        "workshops",
        "copilot-studio",
    ],
    "category": "general",
    "quality_tier": "pilot",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


DEFAULT_RAW_BASE = (
    "https://raw.githubusercontent.com/kody-w/"
    "aibast-agents-library/easy-mode-copilot-chat-pilot/"
)
WORKSHOPS = {
    "time-entry-billing": {
        "display_name": "Time Entry and Billing",
        "agent_path": (
            "solutions/time-entry-billing/easy/"
            "time_entry_billing_workshop_agent.py"
        ),
        "agent_filename": "time_entry_billing_workshop_agent.py",
        "agent_class": "TimeEntryBillingWorkshop",
        "sha256": (
            "a73a61cefc506f17e8ec23829d9d9377"
            "8019d9e2904716482d8ee9536ec22d4f"
        ),
        "aliases": {
            "time entry billing",
            "time entry and billing",
            "time and entry billing",
            "billing",
        },
    },
}


class EasyModeError(RuntimeError):
    """The reusable Easy Mode engine cannot continue safely."""


def _json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


class AIBASTEasyModeAgent(BasicAgent):
    """Routes simple workshop requests into task-specific Brainstem agents."""

    def __init__(self, raw_base=None, state_path=None, agents_dir=None):
        self.name = "AIBASTEasyModeAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Use for AIBAST Easy Mode requests. When the user says "
                "'give me <solution> using the easy mode agent and test it', "
                "call build_and_test. When the user says 'deploy it into "
                "Copilot Studio', call deploy for the active solution. This "
                "agent installs the task-specific workshop cartridge, invokes "
                "it through Brainstem, and continues the personless harness. "
                "Never publish."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "prepare",
                            "build_and_test",
                            "deploy",
                            "complete",
                            "status",
                        ],
                        "description": (
                            "prepare fetches the task cartridge; build_and_test "
                            "runs local proof; deploy prepares or pushes the "
                            "active Copilot Studio Draft; complete validates "
                            "front-door evidence; status returns current state."
                        ),
                    },
                    "solution": {
                        "type": "string",
                        "description": (
                            "AIBAST solution name, such as Time Entry and Billing."
                        ),
                    },
                    "environment_id": {
                        "type": "string",
                        "description": (
                            "Optional Copilot Studio environment UUID. The active "
                            "PAC environment is used when omitted."
                        ),
                    },
                    "preview_evidence": {
                        "type": "string",
                        "description": (
                            "For complete, JSON captured from the real Copilot "
                            "Studio Preview front door."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)
        base = raw_base or os.getenv("AIBAST_EASY_MODE_RAW_BASE") or DEFAULT_RAW_BASE
        self.raw_base = base.rstrip("/") + "/"
        self.agents_dir = Path(
            agents_dir or Path(__file__).resolve().parent
        ).expanduser().resolve()
        default_state = (
            Path.home()
            / ".brainstem"
            / "workshops"
            / "easy-mode-state.json"
        )
        self.state_path = Path(
            state_path or os.getenv("AIBAST_EASY_MODE_STATE") or default_state
        ).expanduser().resolve()

    def system_context(self):
        state = self._read_state()
        active = state.get("active_solution")
        if active in WORKSHOPS:
            display_name = WORKSHOPS[active]["display_name"]
            return (
                "AIBAST Easy Mode has an active workshop: "
                f"{display_name}. Its current state is "
                f"{state.get('status', 'unknown')}. When the user says "
                "'deploy it into Copilot Studio', 'deploy it', or equivalent, "
                "do not ask what 'it' means: call AIBASTEasyModeAgent with "
                "operation deploy and no solution so it resumes the active "
                "workshop. Never publish."
            )
        return (
            "AIBAST Easy Mode is installed with no active workshop. When the "
            "user names a supported solution and asks to use Easy Mode and test "
            "it, call AIBASTEasyModeAgent with operation build_and_test."
        )

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "status")
        try:
            if operation == "prepare":
                return _json_text(
                    self._prepare(str(kwargs.get("solution") or ""))
                )
            if operation == "build_and_test":
                return _json_text(
                    self._build_and_test(
                        str(kwargs.get("solution") or "")
                    )
                )
            if operation == "deploy":
                return _json_text(
                    self._deploy(
                        str(kwargs.get("solution") or ""),
                        str(kwargs.get("environment_id") or ""),
                    )
                )
            if operation == "complete":
                return _json_text(
                    self._complete(
                        str(kwargs.get("solution") or ""),
                        str(kwargs.get("preview_evidence") or ""),
                    )
                )
            if operation == "status":
                return _json_text(self._read_state())
            raise EasyModeError(f"Unsupported operation: {operation}")
        except (
            EasyModeError,
            OSError,
            ValueError,
            urllib.error.URLError,
            json.JSONDecodeError,
        ) as exc:
            failure = {
                "schema": "aibast-easy-mode-state/1.0",
                "status": "blocked",
                "error": str(exc),
                "published": False,
            }
            self._write_state(failure)
            return _json_text(failure)

    def _url(self, relative):
        return self.raw_base + relative.lstrip("/")

    def _fetch(self, relative):
        request = urllib.request.Request(
            self._url(relative),
            headers={"User-Agent": "AIBAST-Easy-Mode/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()

    def _resolve_solution(self, value):
        normalized = _normalize(value)
        if not normalized:
            state = self._read_state()
            slug = state.get("active_solution")
            if slug in WORKSHOPS:
                return slug, WORKSHOPS[slug]
            raise EasyModeError(
                "No active solution. Name an AIBAST solution first."
            )
        for slug, workshop in WORKSHOPS.items():
            candidates = {
                _normalize(slug),
                _normalize(workshop["display_name"]),
                *(_normalize(alias) for alias in workshop["aliases"]),
            }
            if normalized in candidates:
                return slug, workshop
        raise EasyModeError(
            f"No Easy Mode workshop cartridge is registered for {value!r}"
        )

    def _atomic_write(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(path)

    def _install_workshop(self, slug, workshop):
        payload = self._fetch(workshop["agent_path"])
        actual = hashlib.sha256(payload).hexdigest()
        if actual != workshop["sha256"]:
            raise EasyModeError(
                f"{slug} workshop integrity check failed: "
                f"expected {workshop['sha256']}, received {actual}"
            )
        target = self.agents_dir / workshop["agent_filename"]
        self._atomic_write(target, payload)
        compile(payload, str(target), "exec")
        return target

    def _load_workshop(self, slug, workshop):
        path = self._install_workshop(slug, workshop)
        if str(path.parent) not in sys.path:
            sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(
            f"aibast_easy_mode_{slug.replace('-', '_')}",
            path,
        )
        if spec is None or spec.loader is None:
            raise EasyModeError(f"Cannot import workshop cartridge: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        workshop_class = getattr(module, workshop["agent_class"], None)
        if not isinstance(workshop_class, type):
            raise EasyModeError(
                f"{path.name} does not define {workshop['agent_class']}"
            )
        home = (
            self.state_path.parent
            / slug
        )
        return path, workshop_class(
            raw_base=self.raw_base,
            workshop_home=home,
            agents_dir=self.agents_dir,
        )

    def _prepare(self, solution):
        if not _normalize(solution):
            result = {
                "schema": "aibast-easy-mode-state/1.0",
                "status": "ready",
                "active_solution": None,
                "available_solutions": [
                    workshop["display_name"]
                    for workshop in WORKSHOPS.values()
                ],
                "next_prompt": (
                    "Give me Time Entry and Billing using the Easy Mode agent "
                    "and test it for me."
                ),
                "published": False,
            }
            self._write_state(result)
            return result
        slug, workshop = self._resolve_solution(solution)
        path = self._install_workshop(slug, workshop)
        result = {
            "schema": "aibast-easy-mode-state/1.0",
            "status": "ready",
            "active_solution": slug,
            "display_name": workshop["display_name"],
            "workshop_agent": str(path),
            "hot_loaded": True,
            "next_prompt": (
                f"Give me {workshop['display_name']} using the Easy Mode agent "
                "and test it for me."
            ),
            "published": False,
        }
        self._write_state(result)
        return result

    def _build_and_test(self, solution):
        slug, workshop = self._resolve_solution(solution)
        path, runner = self._load_workshop(slug, workshop)
        result = json.loads(
            runner.perform(
                operation="run_workshop",
                deploy_to_studio=False,
            )
        )
        if result.get("status") != "local_proof_passed":
            raise EasyModeError(
                "Task workshop did not pass local proof: " + _json_text(result)
            )
        state = {
            "schema": "aibast-easy-mode-state/1.0",
            "status": "tested",
            "active_solution": slug,
            "display_name": workshop["display_name"],
            "workshop_agent": str(path),
            "local_validation": result["local_validation"],
            "target_agent": result["target_agent"],
            "next_prompt": "Deploy it into Copilot Studio for me.",
            "published": False,
        }
        self._write_state(state)
        return state

    def _deploy(self, solution, environment_id):
        slug, workshop = self._resolve_solution(solution)
        path, runner = self._load_workshop(slug, workshop)
        result = json.loads(
            runner.perform(
                operation="run_workshop",
                deploy_to_studio=True,
                environment_id=environment_id,
            )
        )
        if result.get("status") != "awaiting_front_door_validation":
            raise EasyModeError(
                "Task workshop did not reach front-door validation: "
                + _json_text(result)
            )
        state = {
            "schema": "aibast-easy-mode-state/1.0",
            "status": "awaiting_front_door_validation",
            "active_solution": slug,
            "display_name": workshop["display_name"],
            "workshop_agent": str(path),
            "target_agent": result["target_agent"],
            "local_validation": result["local_validation"],
            "copilot_studio": result["copilot_studio"],
            "copilot_handoff": result["copilot_handoff"],
            "continue_until": (
                "Execute the returned front-door handoff, send its Preview "
                "evidence back through complete, and do not stop until this "
                "agent reports status complete."
            ),
            "published": False,
        }
        self._write_state(state)
        return state

    def _complete(self, solution, preview_evidence):
        slug, workshop = self._resolve_solution(solution)
        path, runner = self._load_workshop(slug, workshop)
        result = json.loads(
            runner.perform(
                operation="complete_workshop",
                preview_evidence=preview_evidence,
            )
        )
        if result.get("status") != "complete":
            raise EasyModeError(
                "Task workshop did not return a complete verdict: "
                + _json_text(result)
            )
        state = {
            "schema": "aibast-easy-mode-state/1.0",
            "status": "complete",
            "active_solution": slug,
            "display_name": workshop["display_name"],
            "workshop_agent": str(path),
            "verdict": result["verdict"],
            "front_door_validation": result["front_door_validation"],
            "published": False,
        }
        self._write_state(state)
        return state

    def _read_state(self):
        if not self.state_path.exists():
            return {
                "schema": "aibast-easy-mode-state/1.0",
                "status": "not_started",
                "available_solutions": [
                    workshop["display_name"]
                    for workshop in WORKSHOPS.values()
                ],
                "published": False,
            }
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _write_state(self, value):
        self._atomic_write(
            self.state_path,
            (_json_text(value) + "\n").encode("utf-8"),
        )
