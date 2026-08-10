"""Generic AIBAST workshop engine for RAPP Brainstem."""

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/workshop",
    "version": "1.0.0",
    "display_name": "AIBAST Workshop Engine",
    "description": (
        "Discovers any packaged AIBAST solution, hot-loads and tests its "
        "business agent, prepares its Copilot Studio Draft, and validates the "
        "real Preview evidence."
    ),
    "author": "AIBAST",
    "tags": [
        "workshop",
        "personless-harness",
        "brainstem",
        "copilot-studio",
        "generic",
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
GITHUB_COMMIT_API = (
    "https://api.github.com/repos/kody-w/aibast-agents-library/"
    "commits/easy-mode-copilot-chat-pilot"
)
IMMUTABLE_RAW_PREFIX = (
    "https://raw.githubusercontent.com/kody-w/aibast-agents-library/"
)
REGISTRY_PATH = "registry.json"
PROMOTE_TOOL_PATH = "tools/promote_solution_draft.py"
UUID_PATTERN = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
NAME_STOP_WORDS = {"agent", "and", "the", "mode", "easy"}


class WorkshopError(RuntimeError):
    """The generic workshop engine cannot continue safely."""


def _json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def _normalize(value):
    words = re.findall(r"[a-z0-9]+", str(value).lower())
    return " ".join(word for word in words if word not in NAME_STOP_WORDS)


class AIBASTWorkshopAgent(BasicAgent):
    """Runs any standard AIBAST solution package as a personless workshop."""

    def __init__(self, raw_base=None, state_path=None, agents_dir=None):
        self.name = "AIBASTWorkshopAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Use for AIBAST Easy Mode workshops. When the user says "
                "'give me <solution> using Easy Mode and test it', call "
                "build_and_test. When the user says 'deploy it into Copilot "
                "Studio', call deploy for the persisted active solution. This "
                "single generic engine discovers solution packages from the "
                "registry; never ask for a solution-specific workshop agent. "
                "Never publish."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "build_and_test",
                            "deploy",
                            "complete",
                            "status",
                        ],
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
                            "Optional Copilot Studio environment UUID. The "
                            "active PAC environment is used when omitted."
                        ),
                    },
                    "preview_evidence": {
                        "type": "string",
                        "description": (
                            "For complete, JSON captured from the real Copilot "
                            "Studio Preview front door, including the non-empty "
                            "actual response for every locked case."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)
        configured_base = raw_base or os.getenv("AIBAST_WORKSHOP_RAW_BASE")
        self.raw_base = (
            configured_base or DEFAULT_RAW_BASE
        ).rstrip("/") + "/"
        self._raw_base_explicit = bool(configured_base)
        self.source_revision = None
        self._registry_cache = None
        self.agents_dir = Path(
            agents_dir or Path(__file__).resolve().parent
        ).expanduser().resolve()
        default_state = (
            Path.home()
            / ".brainstem"
            / "workshops"
            / "aibast-workshop-state.json"
        )
        self.state_path = Path(
            state_path
            or os.getenv("AIBAST_WORKSHOP_STATE")
            or default_state
        ).expanduser().resolve()

    def system_context(self):
        state = self._read_state()
        active = state.get("active_solution")
        if active:
            if state.get("status") == "complete":
                visual_note = (
                    " Teaching visuals are not complete: replacement captures "
                    "remain required as supplemental visual remediation, not "
                    "another functional or deployment step."
                    if state.get("visual_remediation_status") == "required"
                    else ""
                )
                return (
                    "AIBAST Workshop Engine has already functionally completed "
                    "and front-door validated "
                    f"{state.get('display_name', active)}."
                    f"{visual_note} "
                    "Summarize the final Draft verdict only. Do not suggest "
                    "deploying again, publishing, or any additional workshop "
                    "step."
                )
            return (
                "AIBAST Workshop Engine has an active solution: "
                f"{state.get('display_name', active)}. Its state is "
                f"{state.get('status', 'unknown')}. When the user says "
                "'deploy it', do not ask what 'it' means: call "
                "AIBASTWorkshopAgent with operation deploy and no solution. "
                "Never publish, and never offer or recommend publication as a "
                "next step. The workshop ends at Draft."
            )
        return (
            "AIBAST Workshop Engine has no active solution. When the user names "
            "a solution and asks to use Easy Mode and test it, call "
            "AIBASTWorkshopAgent with operation build_and_test. Never "
            "offer, recommend, or mention publication as a next step; "
            "every workshop ends at Draft."
        )

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "status")
        try:
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
            previous = self._read_state()
            failure = {
                **previous,
                "schema": "aibast-workshop-state/1.0",
                "status": "blocked",
                "error": str(exc),
                "published": False,
            }
            self._write_state(failure)
            return _json_text(failure)

    def _pin_source_revision(self):
        if self._raw_base_explicit or self.source_revision:
            return
        request = urllib.request.Request(
            GITHUB_COMMIT_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "AIBAST-Workshop/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            document = json.loads(response.read().decode("utf-8"))
        revision = str(document.get("sha") or "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise WorkshopError(
                "GitHub did not return an immutable workshop source revision"
            )
        self.source_revision = revision
        self.raw_base = IMMUTABLE_RAW_PREFIX + revision + "/"

    def _url(self, relative):
        self._pin_source_revision()
        return self.raw_base + relative.lstrip("/")

    def _fetch_bytes(self, relative):
        request = urllib.request.Request(
            self._url(relative),
            headers={"User-Agent": "AIBAST-Workshop/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()

    def _fetch_json(self, relative):
        return json.loads(self._fetch_bytes(relative).decode("utf-8"))

    def _registry(self):
        if self._registry_cache is None:
            self._registry_cache = self._fetch_json(REGISTRY_PATH)
        return self._registry_cache

    def _solution_candidates(self, agent):
        solution = agent.get("_solution") or {}
        demo = agent.get("_demo") or {}
        package = solution.get("package") or {}
        values = {
            agent.get("name"),
            agent.get("display_name"),
            solution.get("advertised_name"),
            solution.get("sharepoint_list_name"),
            demo.get("slug"),
            package.get("slug"),
        }
        values.update(solution.get("aliases") or [])
        return {_normalize(value) for value in values if value}

    def _resolve_solution(self, value):
        requested = _normalize(value)
        if not requested:
            state = self._read_state()
            active = state.get("active_agent")
            if not active:
                raise WorkshopError(
                    "No active solution. Build and test a named solution first."
                )
            requested = _normalize(active)
        matches = []
        for agent in self._registry().get("agents", []):
            demo = agent.get("_demo") or {}
            package = (agent.get("_solution") or {}).get("package") or {}
            if not demo.get("slug") or not package.get("slug"):
                continue
            if requested in self._solution_candidates(agent):
                matches.append(agent)
        if len(matches) != 1:
            raise WorkshopError(
                f"Expected one packaged AIBAST solution for {value!r}; "
                f"found {len(matches)}"
            )
        agent = matches[0]
        solution = agent["_solution"]
        package = solution["package"]
        slug = package["slug"]
        return {
            "agent_name": agent["name"],
            "display_name": solution.get("advertised_name")
            or agent["display_name"],
            "slug": slug,
            "source_path": agent["_file"],
            "source_sha256": agent["_sha256"],
            "deployment_path": f"solutions/{slug}/deployment.json",
            "manifest_path": package.get("export_manifest_url")
            or f"solutions/{slug}/export-manifest.json",
            "cases_path": f"tests/demo_cases/{agent['_demo']['slug']}.json",
        }

    def _load_documents(self, solution):
        deployment = self._fetch_json(solution["deployment_path"])
        manifest = self._fetch_json(solution["manifest_path"])
        cases = self._fetch_json(solution["cases_path"])
        if deployment.get("name") != solution["agent_name"]:
            raise WorkshopError(
                "deployment.json does not match the registry solution"
            )
        if cases.get("agent") != solution["agent_name"]:
            raise WorkshopError(
                "locked cases do not match the registry solution"
            )
        return deployment, manifest, cases

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

    def _install_target_agent(self, solution, deployment):
        payload = self._fetch_bytes(solution["source_path"])
        actual = hashlib.sha256(payload).hexdigest()
        if actual != solution["source_sha256"]:
            raise WorkshopError(
                "Portable agent integrity check failed: "
                f"expected {solution['source_sha256']}, received {actual}"
            )
        target_name = str(
            deployment.get("target_filename")
            or Path(solution["source_path"]).name
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
            f"aibast_workshop_{path.stem}",
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

    def _workshop_home(self, solution):
        return self.state_path.parent / solution["slug"]

    def _prepare_workspace(self, solution, manifest):
        home = self._workshop_home(solution)
        home.mkdir(parents=True, exist_ok=True)
        bundle_relative = manifest.get("bundle", {}).get("path")
        if not bundle_relative:
            raise WorkshopError("export-manifest.json does not define a bundle")
        archive = home / f"{solution['slug']}-source.zip"
        self._atomic_write(archive, self._fetch_bytes(bundle_relative))
        source_root = home / "source"
        if source_root.exists():
            shutil.rmtree(source_root)
        self._safe_extract(archive, source_root)
        self._atomic_write(
            source_root / solution["cases_path"],
            self._fetch_bytes(solution["cases_path"]),
        )
        self._atomic_write(
            source_root / PROMOTE_TOOL_PATH,
            self._fetch_bytes(PROMOTE_TOOL_PATH),
        )
        return source_root

    def _execute_local(self, solution):
        deployment, manifest, cases = self._load_documents(solution)
        target_path, digest = self._install_target_agent(
            solution,
            deployment,
        )
        target = self._load_target_agent(
            target_path,
            str(deployment["expected_tool"]),
        )
        results = self._run_local_cases(target, cases)
        source_root = self._prepare_workspace(solution, manifest)
        return deployment, cases, target_path, digest, results, source_root

    def _build_and_test(self, value):
        solution = self._resolve_solution(value)
        (
            deployment,
            _cases,
            target_path,
            digest,
            results,
            source_root,
        ) = self._execute_local(solution)
        state = {
            "schema": "aibast-workshop-state/1.0",
            "status": "tested",
            "active_agent": solution["agent_name"],
            "active_solution": solution["slug"],
            "display_name": solution["display_name"],
            "source_revision": self.source_revision,
            "target_agent": {
                "tool": deployment["expected_tool"],
                "installed_to": str(target_path),
                "sha256": digest,
                "hot_loaded": True,
            },
            "local_validation": {
                "passed": len(results),
                "total": len(results),
                "cases": results,
            },
            "workspace": str(source_root),
            "next_prompt": "Deploy it into Copilot Studio for me.",
            "published": False,
        }
        self._write_state(state)
        return state

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
            "PAC CLI is unavailable. Install or expose pac, then rerun."
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
            "No active PAC environment was found. Select one profile and rerun."
        )

    def _deploy_draft(
        self,
        solution,
        source_root,
        deployment,
        environment_id,
    ):
        pac = self._find_pac()
        environment, environment_source = self._resolve_environment(
            pac,
            environment_id,
        )
        studio = deployment.get("copilot_studio", {})
        recorded = (
            studio.get("export_agent")
            or studio.get("validated_pilot")
            or {}
        )
        display_name = str(
            recorded.get("display_name")
            or deployment.get("display_name")
            or solution["display_name"]
        )
        home = self._workshop_home(solution)
        project_root = home / "copilot-studio-projects"
        project = project_root / display_name
        connected = (project / ".mcs" / "conn.json").exists()
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
        elif project.exists() and not connected:
            shutil.rmtree(project)
        command = [
            sys.executable,
            str(source_root / PROMOTE_TOOL_PATH),
            solution["slug"],
            "--project-dir",
            str(project),
            "--environment",
            environment,
            "--display-name",
            display_name,
            "--push",
        ]
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

    def _visual_evidence_plan(self, solution, source_root):
        path = (
            source_root
            / "solutions"
            / solution["slug"]
            / "evals"
            / "visual-checkpoints.json"
        )
        if not path.exists():
            return {
                "status": "not_configured",
                "reusable": 0,
                "reshoot_required": 0,
                "reshoot_jobs": [],
                "new_capture_jobs": [],
            }
        document = json.loads(path.read_text(encoding="utf-8"))
        captures = [
            item
            for item in document.get("captures", [])
            if isinstance(item, dict)
        ]
        reshoots = [
            {
                "id": item.get("id"),
                "mode": item.get("mode"),
                "case_id": item.get("case_id"),
                "step": item.get("step"),
                "source": item.get("source"),
                "reason": item.get("reason"),
            }
            for item in captures
            if item.get("status") == "reshoot_required"
        ]
        return {
            "status": (
                "reshoot_required" if reshoots else "ready"
            ),
            "policy": document.get("policy", {}),
            "reusable": sum(
                item.get("status") == "reusable"
                for item in captures
            ),
            "reshoot_required": len(reshoots),
            "reshoot_jobs": reshoots,
            "new_capture_jobs": (
                document.get("reshoot_plan", {})
                .get("new_learn_step_captures", [])
            ),
            "replacement_captures": (
                document.get("reshoot_plan", {})
                .get("replacement_captures", [])
            ),
        }

    def _front_door_handoff(
        self,
        solution,
        cases,
        studio,
        visual_evidence,
    ):
        return {
            "executor": "GitHub Copilot Agent mode",
            "instruction": (
                "Use the real Copilot Studio front door or configured browser "
                "tools. Open the Draft, run every exact case in a fresh Preview "
                "conversation, capture each full non-empty response, then ask "
                "AIBASTWorkshopAgent to complete using that evidence."
            ),
            "solution": solution["agent_name"],
            "draft": studio,
            "workspace": str(self._workshop_home(solution) / "source"),
            "project_root": str(
                self._workshop_home(solution)
                / "copilot-studio-projects"
            ),
            "visual_evidence": visual_evidence,
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
                        "case_id": "CASE-01",
                        "response": "The actual Copilot Studio Preview response.",
                        "must_include": [],
                        "must_not_include": [],
                        "passed": True,
                    }
                ],
            },
        }

    def _deploy(self, value, environment_id):
        solution = self._resolve_solution(value)
        (
            deployment,
            cases,
            target_path,
            digest,
            results,
            source_root,
        ) = self._execute_local(solution)
        studio = self._deploy_draft(
            solution,
            source_root,
            deployment,
            environment_id,
        )
        visual_evidence = self._visual_evidence_plan(
            solution,
            source_root,
        )
        state = {
            "schema": "aibast-workshop-state/1.0",
            "status": "awaiting_front_door_validation",
            "active_agent": solution["agent_name"],
            "active_solution": solution["slug"],
            "display_name": solution["display_name"],
            "source_revision": self.source_revision,
            "target_agent": {
                "tool": deployment["expected_tool"],
                "installed_to": str(target_path),
                "sha256": digest,
                "hot_loaded": True,
            },
            "local_validation": {
                "passed": len(results),
                "total": len(results),
                "cases": results,
            },
            "copilot_studio": studio,
            "workspace": str(source_root),
            "visual_evidence": visual_evidence,
            "copilot_handoff": self._front_door_handoff(
                solution,
                cases,
                studio,
                visual_evidence,
            ),
            "published": False,
        }
        self._write_state(state)
        return state

    def _complete(self, value, preview_evidence):
        if not preview_evidence:
            raise WorkshopError("preview_evidence JSON is required")
        solution = self._resolve_solution(value)
        _deployment, _manifest, cases = self._load_documents(solution)
        evidence = json.loads(preview_evidence)
        if evidence.get("status") != "Draft" or evidence.get("published") is not False:
            raise WorkshopError(
                "Preview evidence must prove status Draft and published false"
            )
        captured = {
            str(item.get("case_id")): item
            for item in evidence.get("cases", [])
            if isinstance(item, dict)
        }
        results = []
        for case in cases.get("cases", []):
            item = captured.get(case["id"], {})
            response = str(item.get("response") or "").strip()
            if response:
                lower = response.lower()
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
                missing = ["non-empty Preview response is required"]
                forbidden = []
                passed = False
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
        visual_evidence = previous.get(
            "visual_evidence",
            {
                "status": "not_configured",
                "reshoot_required": 0,
            },
        )
        visual_reshoots = int(
            visual_evidence.get("reshoot_required", 0) or 0
        )
        state = {
            **previous,
            "status": "complete",
            "functional_status": "complete",
            "visual_remediation_status": (
                "required" if visual_reshoots else "not_required"
            ),
            "front_door_validation": {
                "passed": len(results),
                "total": len(results),
                "cases": results,
            },
            "copilot_handoff": None,
            "published": False,
            "verdict": (
                f"{solution['display_name']} functional workshop complete. "
                "The generic engine discovered, hot-loaded, tested, deployed, "
                "and validated the package; the Copilot Studio agent remains "
                "Draft. "
                + (
                    f"Visual evidence still requires {visual_reshoots} "
                    "replacement captures before the teaching package is "
                    "complete."
                    if visual_reshoots
                    else "The workshop ends here and must not offer publication."
                )
            ),
        }
        self._write_state(state)
        return state

    def _read_state(self):
        if not self.state_path.exists():
            return {
                "schema": "aibast-workshop-state/1.0",
                "status": "not_started",
                "published": False,
            }
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _write_state(self, value):
        self._atomic_write(
            self.state_path,
            (_json_text(value) + "\n").encode("utf-8"),
        )
