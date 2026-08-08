"""Personless Time Entry and Billing workshop harness for RAPP Brainstem."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/time-entry-billing-workshop",
    "version": "1.0.0",
    "display_name": "Time Entry and Billing Workshop Harness",
    "description": (
        "Runs the Time Entry and Billing workshop as a Brainstem + Copilot "
        "personless harness."
    ),
    "author": "AIBAST",
    "tags": ["workshop", "personless-harness", "billing", "copilot-studio"],
    "category": "professional_services",
    "quality_tier": "pilot",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


SLUG = "time-entry-billing"
PACKAGE = f"solutions/{SLUG}"
DEFAULT_RAW_BASE = (
    "https://raw.githubusercontent.com/kody-w/"
    "aibast-agents-library/easy-mode-copilot-chat-pilot/"
)
DEPLOYMENT_PATH = f"{PACKAGE}/deployment.json"
TRANSCRIPTS_PATH = f"{PACKAGE}/evals/transcripts.json"
CASES_PATH = f"tests/demo_cases/{SLUG}.json"
BUNDLE_PATH = f"{PACKAGE}/exports/{SLUG}-source.zip"
PROMOTE_TOOL_PATH = "tools/promote_solution_draft.py"
UUID_PATTERN = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)


class WorkshopError(RuntimeError):
    """A workshop step failed and must be reported as a blocker."""


def _json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


class TimeEntryBillingWorkshop(BasicAgent):
    """Runs the workshop engine and returns front-door actions to Copilot."""

    def __init__(self, raw_base=None, workshop_home=None, agents_dir=None):
        self.name = "TimeEntryBillingWorkshop"
        self.metadata = {
            "name": self.name,
            "description": (
                "Use whenever the user asks to run the Time Entry and Billing "
                "workshop, Easy mode, or personless harness. run_workshop "
                "downloads the reviewed GitHub assets, hot-loads the business "
                "agent into Brainstem, proves every local case, and prepares or "
                "pushes a Copilot Studio Draft. complete_workshop validates the "
                "real Preview evidence and Draft gate. Never publish."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "run_workshop",
                            "complete_workshop",
                            "status",
                        ],
                        "description": (
                            "run_workshop starts or resumes the personless run; "
                            "complete_workshop verifies Preview evidence; status "
                            "returns the persisted run."
                        ),
                    },
                    "environment_id": {
                        "type": "string",
                        "description": (
                            "Optional Copilot Studio environment UUID. When "
                            "omitted, use the active PAC environment."
                        ),
                    },
                    "deploy_to_studio": {
                        "type": "boolean",
                        "description": (
                            "Whether Brainstem should prepare and push the "
                            "Copilot Studio Draft. Defaults to true."
                        ),
                    },
                    "preview_evidence": {
                        "type": "string",
                        "description": (
                            "For complete_workshop, JSON containing status, "
                            "published, and exact case responses captured through "
                            "the Copilot Studio front door."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)
        base = raw_base or os.getenv("AIBAST_WORKSHOP_RAW_BASE") or DEFAULT_RAW_BASE
        self.raw_base = base.rstrip("/") + "/"
        home = (
            workshop_home
            or os.getenv("AIBAST_WORKSHOP_HOME")
            or Path.home() / ".brainstem" / "workshops" / SLUG
        )
        self.workshop_home = Path(home).expanduser().resolve()
        self.agents_dir = Path(
            agents_dir or Path(__file__).resolve().parent
        ).expanduser().resolve()
        self.state_path = self.workshop_home / "state.json"

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "run_workshop")
        try:
            if operation == "run_workshop":
                return self._run_workshop(
                    environment_id=str(kwargs.get("environment_id") or ""),
                    deploy_to_studio=kwargs.get("deploy_to_studio", True)
                    is not False,
                )
            if operation == "complete_workshop":
                return self._complete_workshop(
                    str(kwargs.get("preview_evidence") or "")
                )
            if operation == "status":
                return _json_text(self._read_state())
            raise WorkshopError(f"Unsupported operation: {operation}")
        except (
            WorkshopError,
            OSError,
            ValueError,
            subprocess.SubprocessError,
            urllib.error.URLError,
            zipfile.BadZipFile,
            json.JSONDecodeError,
        ) as exc:
            failure = {
                "schema": "aibast-personless-workshop-result/1.0",
                "workshop": SLUG,
                "status": "blocked",
                "error": str(exc),
                "published": False,
            }
            self._write_state(failure)
            return _json_text(failure)

    def _url(self, relative):
        return self.raw_base + relative.lstrip("/")

    def _fetch_bytes(self, relative):
        request = urllib.request.Request(
            self._url(relative),
            headers={"User-Agent": "AIBAST-Personless-Workshop/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()

    def _fetch_json(self, relative):
        return json.loads(self._fetch_bytes(relative).decode("utf-8"))

    def _atomic_write(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(path)

    def _safe_extract(self, archive_path, destination):
        destination.mkdir(parents=True, exist_ok=True)
        root = destination.resolve()
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if target != root and root not in target.parents:
                    raise WorkshopError(
                        f"Bundle contains an unsafe path: {member.filename}"
                    )
            archive.extractall(destination)

    def _source_relative_path(self, deployment):
        source_url = str(deployment.get("source_url") or "")
        if "/main/" not in source_url:
            raise WorkshopError("deployment.json does not expose a main-branch source URL")
        return source_url.split("/main/", 1)[1]

    def _source_digest(self, transcripts, source_relative):
        for source in transcripts.get("agent_sources", []):
            if source.get("path") == source_relative and source.get("sha256"):
                return str(source["sha256"])
        raise WorkshopError("transcripts.json does not pin the portable source SHA-256")

    def _install_target_agent(self, deployment, transcripts):
        source_relative = self._source_relative_path(deployment)
        payload = self._fetch_bytes(source_relative)
        expected = self._source_digest(transcripts, source_relative)
        actual = hashlib.sha256(payload).hexdigest()
        if actual != expected:
            raise WorkshopError(
                "Portable agent integrity check failed: "
                f"expected {expected}, received {actual}"
            )
        target_name = str(
            deployment.get("target_filename") or Path(source_relative).name
        )
        if not target_name.endswith("_agent.py"):
            raise WorkshopError("Target filename must end in _agent.py")
        target = self.agents_dir / target_name
        self._atomic_write(target, payload)
        return target, actual

    def _load_target_agent(self, path, class_name):
        if str(path.parent) not in sys.path:
            sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(
            "aibast_time_entry_billing_hotload",
            path,
        )
        if spec is None or spec.loader is None:
            raise WorkshopError(f"Cannot import hot-loaded agent: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        target_class = getattr(module, class_name, None)
        if not isinstance(target_class, type):
            raise WorkshopError(f"Hot-loaded source does not define {class_name}")
        return target_class()

    def _run_local_cases(self, agent, cases):
        results = []
        for case in cases.get("cases", []):
            output = agent.perform(
                operation=case["operation"],
                **(case.get("arguments") or {}),
            )
            lower = output.lower()
            missing = [
                marker
                for marker in case.get("must_include", [])
                if marker.lower() not in lower
            ]
            forbidden = [
                marker
                for marker in case.get("must_not_include", [])
                if marker.lower() in lower
            ]
            results.append(
                {
                    "case_id": case["id"],
                    "prompt": case["prompt"],
                    "passed": not missing and not forbidden,
                    "missing": missing,
                    "forbidden": forbidden,
                }
            )
        if not results or not all(result["passed"] for result in results):
            raise WorkshopError(
                "Hot-loaded local agent failed locked cases: "
                + _json_text(results)
            )
        return results

    def _prepare_workspace(self):
        self.workshop_home.mkdir(parents=True, exist_ok=True)
        archive = self.workshop_home / f"{SLUG}-source.zip"
        self._atomic_write(archive, self._fetch_bytes(BUNDLE_PATH))
        source_root = self.workshop_home / "source"
        if source_root.exists():
            shutil.rmtree(source_root)
        self._safe_extract(archive, source_root)
        self._atomic_write(
            source_root / CASES_PATH,
            self._fetch_bytes(CASES_PATH),
        )
        promote = source_root / PROMOTE_TOOL_PATH
        self._atomic_write(promote, self._fetch_bytes(PROMOTE_TOOL_PATH))
        return source_root

    def _find_pac(self):
        configured = os.getenv("AIBAST_PAC_BIN")
        candidates = [
            configured,
            shutil.which("pac"),
            "/opt/homebrew/bin/pac",
            "/usr/local/bin/pac",
            str(Path.home() / ".dotnet" / "tools" / "pac"),
        ]
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate).resolve())
        raise WorkshopError(
            "PAC CLI is unavailable. Install or expose pac, then rerun the workshop."
        )

    def _run_command(self, command, cwd=None, env=None, timeout=900):
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip()
            raise WorkshopError(
                f"{' '.join(command)} failed ({result.returncode}): "
                f"{detail[-2000:]}"
            )
        return result.stdout + result.stderr

    def _resolve_environment(self, pac, explicit):
        if explicit:
            if not UUID_PATTERN.fullmatch(explicit):
                raise WorkshopError("environment_id must be a UUID")
            return explicit, "explicit"
        configured = os.getenv("AIBAST_COPILOT_STUDIO_ENVIRONMENT", "")
        if configured:
            if not UUID_PATTERN.fullmatch(configured):
                raise WorkshopError(
                    "AIBAST_COPILOT_STUDIO_ENVIRONMENT must be a UUID"
                )
            return configured, "environment"
        output = self._run_command([pac, "env", "list"], timeout=180)
        for line in output.splitlines():
            if not line.lstrip().startswith("*"):
                continue
            match = UUID_PATTERN.search(line)
            if match:
                return match.group(0), "active-pac-profile"
        raise WorkshopError(
            "No active PAC environment was found. Select one PAC profile and rerun."
        )

    def _deploy_draft(self, source_root, environment_id):
        pac = self._find_pac()
        environment, environment_source = self._resolve_environment(
            pac,
            environment_id,
        )
        recipe = json.loads(
            (
                source_root
                / "solutions"
                / SLUG
                / "deployment.json"
            ).read_text(encoding="utf-8")
        )
        recorded = recipe.get("copilot_studio", {}).get(
            "validated_pilot",
            {},
        )
        display_name = str(
            recorded.get("display_name")
            or recipe.get("display_name")
            or "Time Entry and Billing Pilot"
        )
        project_root = self.workshop_home / "copilot-studio-projects"
        project = project_root / display_name
        connected = (project / ".mcs" / "conn.json").exists()
        command = [
            sys.executable,
            str(source_root / PROMOTE_TOOL_PATH),
            SLUG,
            "--project-dir",
            str(project),
            "--environment",
            environment,
            "--push",
        ]
        child_env = os.environ.copy()
        child_env["PATH"] = (
            str(Path(pac).parent)
            + os.pathsep
            + child_env.get("PATH", "")
        )
        if (
            not connected
            and recorded.get("environment_id") == environment
            and recorded.get("schema_name")
        ):
            if project.exists():
                shutil.rmtree(project)
            project_root.mkdir(parents=True, exist_ok=True)
            self._run_command(
                [
                    pac,
                    "copilot",
                    "clone",
                    "--bot",
                    str(recorded["schema_name"]),
                    "--environment",
                    environment,
                    "--output-dir",
                    str(project_root),
                ],
                env=child_env,
                timeout=600,
            )
            connected = (project / ".mcs" / "conn.json").exists()
            if not connected:
                raise WorkshopError(
                    f"PAC cloned the recorded Draft but {project} is not connected"
                )
        if connected:
            command.append("--update-existing")
        output = self._run_command(
            command,
            cwd=source_root,
            env=child_env,
        )
        start = output.find("{")
        if start < 0:
            raise WorkshopError("Draft promotion did not return its JSON result")
        result = json.loads(output[start:])
        result["environment_source"] = environment_source
        result["environment_id"] = environment
        result["published"] = False
        return result

    def _front_door_handoff(self, cases, studio):
        return {
            "executor": "GitHub Copilot Agent mode",
            "instruction": (
                "Use the real Copilot Studio front door or configured browser "
                "tools. Open the Draft identified below, start a fresh Preview "
                "conversation for every case, capture the exact response, then "
                "send the evidence JSON back to Brainstem and ask "
                "TimeEntryBillingWorkshop to complete_workshop."
            ),
            "draft": studio,
            "cases": [
                {
                    "case_id": case["id"],
                    "prompt": case["prompt"],
                    "must_include": case.get("must_include", []),
                    "must_not_include": case.get("must_not_include", []),
                }
                for case in cases.get("cases", [])
            ],
            "callback_schema": {
                "status": "Draft",
                "published": False,
                "cases": [
                    {
                        "case_id": "TEB-01",
                        "response": "Exact Preview response text",
                    }
                ],
            },
        }

    def _run_workshop(self, environment_id, deploy_to_studio):
        deployment = self._fetch_json(DEPLOYMENT_PATH)
        transcripts = self._fetch_json(TRANSCRIPTS_PATH)
        cases = self._fetch_json(CASES_PATH)
        target_path, digest = self._install_target_agent(
            deployment,
            transcripts,
        )
        target = self._load_target_agent(
            target_path,
            str(deployment["expected_tool"]),
        )
        local_results = self._run_local_cases(target, cases)
        source_root = self._prepare_workspace()
        studio = {
            "status": "not_requested",
            "published": False,
        }
        status = "local_proof_passed"
        handoff = None
        if deploy_to_studio:
            studio = self._deploy_draft(source_root, environment_id)
            status = "awaiting_front_door_validation"
            handoff = self._front_door_handoff(cases, studio)
        result = {
            "schema": "aibast-personless-workshop-result/1.0",
            "workshop": SLUG,
            "status": status,
            "engine": "RAPP Brainstem",
            "target_agent": {
                "tool": deployment["expected_tool"],
                "installed_to": str(target_path),
                "sha256": digest,
                "hot_loaded": True,
            },
            "local_validation": {
                "passed": len(local_results),
                "total": len(local_results),
                "cases": local_results,
            },
            "workspace": str(source_root),
            "copilot_studio": studio,
            "copilot_handoff": handoff,
            "published": False,
        }
        self._write_state(result)
        return _json_text(result)

    def _complete_workshop(self, preview_evidence):
        if not preview_evidence:
            raise WorkshopError("preview_evidence JSON is required")
        evidence = json.loads(preview_evidence)
        if evidence.get("status") != "Draft" or evidence.get("published") is not False:
            raise WorkshopError(
                "Preview evidence must prove status Draft and published false"
            )
        cases = self._fetch_json(CASES_PATH)
        captured = {
            str(item.get("case_id")): item
            for item in evidence.get("cases", [])
            if isinstance(item, dict)
        }
        results = []
        for case in cases.get("cases", []):
            item = captured.get(case["id"], {})
            response = str(item.get("response") or "")
            lower = response.lower()
            if response:
                missing = [
                    marker
                    for marker in case.get("must_include", [])
                    if marker.lower() not in lower
                ]
                forbidden = [
                    marker
                    for marker in case.get("must_not_include", [])
                    if marker.lower() in lower
                ]
                passed = not missing and not forbidden
            else:
                recorded_include = item.get("must_include") or []
                recorded_exclude = item.get("must_not_include") or []
                missing = (
                    []
                    if recorded_include == case.get("must_include", [])
                    else ["captured must_include contract differs"]
                )
                forbidden = (
                    []
                    if recorded_exclude == case.get("must_not_include", [])
                    else ["captured must_not_include contract differs"]
                )
                passed = (
                    item.get("passed") is True
                    and not missing
                    and not forbidden
                )
            results.append(
                {
                    "case_id": case["id"],
                    "passed": passed,
                    "missing": missing,
                    "forbidden": forbidden,
                }
            )
        if not results or not all(result["passed"] for result in results):
            raise WorkshopError(
                "Front-door Preview evidence failed: " + _json_text(results)
            )
        previous = self._read_state()
        result = {
            **previous,
            "status": "complete",
            "front_door_validation": {
                "passed": len(results),
                "total": len(results),
                "cases": results,
            },
            "copilot_handoff": None,
            "published": False,
            "verdict": (
                "Personless workshop complete. Brainstem hot-loaded and proved "
                "the agent; Copilot pulled through the real Preview front door; "
                "the Copilot Studio agent remains Draft and unpublished."
            ),
        }
        self._write_state(result)
        return _json_text(result)

    def _read_state(self):
        if not self.state_path.exists():
            return {
                "schema": "aibast-personless-workshop-result/1.0",
                "workshop": SLUG,
                "status": "not_started",
                "published": False,
            }
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _write_state(self, value):
        self._atomic_write(
            self.state_path,
            (_json_text(value) + "\n").encode("utf-8"),
        )
