#!/usr/bin/env python3
"""Fail-closed local prerequisite check for AIBAST Easy Mode."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


SCHEMA = "aibast-easy-mode-preflight/1.0"
PLUGIN_ID = "mcs-assistant@copilot-studio-plugin"
PLUGIN_NAME = "mcs-assistant"
MARKETPLACE = "microsoft/copilot-studio-plugin"
MINIMUM_PAC = (2, 9, 3)
CAPABILITY_FILES = (
    "copilot-studio-manage.md",
    "copilot-studio-describer.md",
    "copilot-studio-init.md",
    "copilot-studio-architect.md",
)
SEMVER = re.compile(
    r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?(?!\d)"
)
PAC_LABEL = re.compile(
    r"\b(?:microsoft\s+power\s*platform|power\s+platform|pac)\s+cli\b",
    re.IGNORECASE,
)


@dataclass
class Command:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        return "\n".join(
            value.strip() for value in (self.stdout, self.stderr) if value.strip()
        )


def run_command(args: Sequence[str]) -> Command:
    completed = subprocess.run(
        list(args),
        text=True,
        capture_output=True,
        check=False,
    )
    return Command(
        args=list(args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def command_error(command: Command) -> str:
    detail = command.output or "no output"
    return (
        f"{shlex.join(command.args)} failed with exit "
        f"{command.returncode}: {detail}"
    )


def plugin_record(output: str) -> str | None:
    for line in output.splitlines():
        tokens = re.findall(r"[A-Za-z0-9_.-]+(?:@[A-Za-z0-9_.-]+)?", line)
        if any(token.lower() == PLUGIN_NAME for token in tokens):
            return line.strip()
    return None


def plugin_version(record: str | None) -> str | None:
    if not record:
        return None
    match = SEMVER.search(record)
    return match.group(0) if match else None


def pac_version(output: str) -> tuple[tuple[int, int, int], str] | None:
    lines = output.splitlines()
    for index, line in enumerate(lines):
        label = PAC_LABEL.search(line)
        if label is None:
            continue
        remainder = line[label.end() :].strip()
        remainder = re.sub(
            r"^(?:version\s*[:=]?\s*|[:=]\s*|v(?=\d))",
            "",
            remainder,
            flags=re.IGNORECASE,
        )
        match = SEMVER.match(remainder)
        if match is None:
            next_index = index + 1
            while next_index < len(lines) and not lines[next_index].strip():
                next_index += 1
            if next_index < len(lines) and re.match(
                r"^\s*version\s*:", lines[next_index], re.IGNORECASE
            ):
                match = SEMVER.search(lines[next_index])
        if match is not None:
            return (
                tuple(int(match.group(part)) for part in range(1, 4)),
                match.group(0),
            )
    return None


def copilot_config_path() -> Path:
    configured = os.environ.get("COPILOT_CONFIG_PATH")
    return (
        Path(configured).expanduser()
        if configured
        else Path.home() / ".copilot" / "config.json"
    )


def _installed_plugin_entries(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    installed = data.get("installedPlugins")
    if isinstance(installed, list):
        return [item for item in installed if isinstance(item, dict)]
    if isinstance(installed, dict):
        return [item for item in installed.values() if isinstance(item, dict)]
    return []


def inspect_plugin_config(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "config_path": str(path),
        "config_loaded": False,
        "matching_entry_count": 0,
        "name": None,
        "enabled": False,
        "version": None,
        "origin": None,
        "origin_verified": False,
        "cache_path": None,
        "cache_path_valid": False,
        "capability_files": list(CAPABILITY_FILES),
        "missing_capability_files": list(CAPABILITY_FILES),
        "capabilities_verified": False,
        "verified": False,
        "failure": None,
    }
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(
            re.sub(r"(?m)^\s*//.*$", "", raw)
        )
    except (OSError, json.JSONDecodeError) as exc:
        result["failure"] = f"cannot read Copilot config {path}: {exc}"
        return result
    result["config_loaded"] = True
    entries = [
        item
        for item in _installed_plugin_entries(data)
        if item.get("name") == PLUGIN_NAME
    ]
    result["matching_entry_count"] = len(entries)
    if not entries:
        result["failure"] = (
            f"Copilot config {path} has no installedPlugins entry named "
            f"{PLUGIN_NAME}"
        )
        return result
    if len(entries) != 1:
        result["failure"] = (
            f"Copilot config {path} must have exactly one installedPlugins "
            f"entry named {PLUGIN_NAME}; found {len(entries)}"
        )
        return result

    entry = entries[0]
    source = entry.get("source")
    origin = source if isinstance(source, dict) else {}
    result.update(
        {
            "name": entry.get("name"),
            "enabled": entry.get("enabled") is True,
            "version": (
                entry.get("version")
                if isinstance(entry.get("version"), str)
                and entry["version"].strip()
                else None
            ),
            "origin": {
                "source": origin.get("source"),
                "repo": origin.get("repo"),
            },
            "origin_verified": (
                origin.get("source") == "github"
                and origin.get("repo") == MARKETPLACE
            ),
        }
    )
    raw_cache = entry.get("cache_path")
    if isinstance(raw_cache, str) and raw_cache.strip():
        cache_path = Path(raw_cache).expanduser()
        if not cache_path.is_absolute():
            cache_path = path.parent / cache_path
        cache_path = cache_path.resolve()
        result["cache_path"] = str(cache_path)
        result["cache_path_valid"] = cache_path.is_dir()
        missing = [
            name
            for name in CAPABILITY_FILES
            if not (cache_path / "agents" / name).is_file()
        ]
        result["missing_capability_files"] = missing
        result["capabilities_verified"] = not missing

    problems = []
    if not result["enabled"]:
        problems.append("plugin is not enabled")
    if result["version"] is None:
        problems.append("plugin version is empty")
    if not result["origin_verified"]:
        problems.append(
            "plugin origin is not github microsoft/copilot-studio-plugin"
        )
    if not result["cache_path_valid"]:
        problems.append("plugin cache_path is missing or invalid")
    if not result["capabilities_verified"]:
        problems.append(
            "plugin capabilities are missing: "
            + ", ".join(result["missing_capability_files"])
        )
    result["verified"] = not problems
    result["failure"] = "; ".join(problems) if problems else None
    return result


def inspect_pac(
    path: str,
) -> tuple[
    Command | None,
    tuple[int, int, int] | None,
    str | None,
    str | None,
]:
    try:
        command = run_command([path, "--version"])
    except OSError as exc:
        return None, None, None, f"pac --version could not run: {exc}"
    parsed = pac_version(command.output)
    if parsed is None:
        return (
            command,
            None,
            None,
            "pac --version did not report a PAC-labelled semantic version "
            f"(exit {command.returncode}; output: {command.output or 'none'})",
        )
    version_tuple, version_text = parsed
    return command, version_tuple, version_text, None


def run_preflight() -> dict[str, Any]:
    failures: list[str] = []
    actions: list[str] = []
    copilot_path = shutil.which("copilot")
    plugin_line: str | None = None
    plugin_config = inspect_plugin_config(copilot_config_path())

    if copilot_path is None:
        failures.append(
            "copilot is unavailable; install GitHub Copilot CLI and ensure it "
            "is on PATH"
        )
    else:
        try:
            listed = run_command([copilot_path, "plugin", "list"])
        except OSError as exc:
            failures.append(f"copilot plugin list could not run: {exc}")
        else:
            if listed.returncode != 0:
                failures.append(command_error(listed))
            else:
                plugin_line = plugin_record(listed.output)
                if plugin_line is None:
                    setup_commands = (
                        [
                            copilot_path,
                            "plugin",
                            "marketplace",
                            "add",
                            MARKETPLACE,
                        ],
                        [
                            copilot_path,
                            "plugin",
                            "install",
                            PLUGIN_ID,
                        ],
                    )
                    for command_args in setup_commands:
                        try:
                            command = run_command(command_args)
                        except OSError as exc:
                            failures.append(
                                f"{shlex.join(command_args)} could not run: {exc}"
                            )
                            break
                        if command.returncode != 0:
                            failures.append(command_error(command))
                            break
                        actions.append(shlex.join(command_args[1:]))
                    if not failures:
                        try:
                            listed = run_command(
                                [copilot_path, "plugin", "list"]
                            )
                        except OSError as exc:
                            failures.append(
                                f"copilot plugin list recheck could not run: {exc}"
                            )
                        else:
                            if listed.returncode != 0:
                                failures.append(command_error(listed))
                            else:
                                plugin_line = plugin_record(listed.output)
                                if plugin_line is None:
                                    failures.append(
                                        f"{PLUGIN_ID} is still absent after installation"
                                    )
                                plugin_config = inspect_plugin_config(
                                    copilot_config_path()
                                )
            if plugin_line is not None and not plugin_config["verified"]:
                failures.append(str(plugin_config["failure"]))

    cli_plugin_version = plugin_version(plugin_line)
    plugin_version_matches_config = (
        plugin_line is not None
        and plugin_config["verified"]
        and cli_plugin_version == plugin_config["version"]
    )
    if (
        plugin_line is not None
        and plugin_config["verified"]
        and not plugin_version_matches_config
    ):
        failures.append(
            "CLI-listed mcs-assistant plugin version "
            f"{cli_plugin_version or 'unknown'} does not exactly match "
            f"official config version {plugin_config['version']}"
        )

    pac_path = shutil.which("pac")
    pac_text: str | None = None
    pac_tuple: tuple[int, int, int] | None = None
    pac_exit: int | None = None
    if pac_path is None:
        failures.append(
            "pac is unavailable; install Microsoft Power Platform CLI "
            "version newer than 2.9.3 (for example: dotnet tool install "
            "--global Microsoft.PowerApps.CLI.Tool)"
        )
    else:
        command, pac_tuple, pac_text, pac_failure = inspect_pac(pac_path)
        pac_exit = command.returncode if command is not None else None
        if pac_failure:
            failures.append(pac_failure)
        elif pac_tuple is not None and pac_tuple <= MINIMUM_PAC:
            dotnet_path = shutil.which("dotnet")
            if dotnet_path is None:
                failures.append(
                    f"PAC {pac_text} is too old; install a version newer than "
                    "2.9.3 with `dotnet tool update --global "
                    "Microsoft.PowerApps.CLI.Tool`"
                )
            else:
                update_args = [
                    dotnet_path,
                    "tool",
                    "update",
                    "--global",
                    "Microsoft.PowerApps.CLI.Tool",
                ]
                try:
                    update = run_command(update_args)
                except OSError as exc:
                    failures.append(
                        f"{shlex.join(update_args)} could not run: {exc}"
                    )
                else:
                    if update.returncode != 0:
                        failures.append(command_error(update))
                    else:
                        actions.append(shlex.join(update_args[1:]))
                        command, pac_tuple, pac_text, pac_failure = inspect_pac(
                            pac_path
                        )
                        pac_exit = (
                            command.returncode if command is not None else None
                        )
                        if pac_failure:
                            failures.append(
                                "PAC recheck failed after update: " + pac_failure
                            )
                        elif pac_tuple is not None and pac_tuple <= MINIMUM_PAC:
                            failures.append(
                                f"PAC remains {pac_text} after update; version "
                                "must be newer than 2.9.3"
                            )

    return {
        "schema": SCHEMA,
        "passed": not failures,
        "copilot": {
            "path": copilot_path,
            "installed_plugin": PLUGIN_ID if plugin_line else None,
            "plugin_version": cli_plugin_version,
            "plugin_record": plugin_line,
            "config_path": plugin_config["config_path"],
            "config_loaded": plugin_config["config_loaded"],
            "matching_config_entries": plugin_config[
                "matching_entry_count"
            ],
            "config_plugin_version": plugin_config["version"],
            "plugin_version_matches_config": plugin_version_matches_config,
            "plugin_enabled": plugin_config["enabled"],
            "plugin_origin": plugin_config["origin"],
            "origin_verified": plugin_config["origin_verified"],
            "cache_path": plugin_config["cache_path"],
            "cache_path_valid": plugin_config["cache_path_valid"],
            "capability_files": plugin_config["capability_files"],
            "missing_capability_files": plugin_config[
                "missing_capability_files"
            ],
            "capabilities_verified": plugin_config[
                "capabilities_verified"
            ],
            "official_plugin_verified": (
                plugin_line is not None
                and plugin_config["verified"]
                and plugin_version_matches_config
            ),
        },
        "pac": {
            "path": pac_path,
            "version": pac_text,
            "version_exit_code": pac_exit,
            "minimum_exclusive": "2.9.3",
            "supported": pac_tuple is not None and pac_tuple > MINIMUM_PAC,
        },
        "actions": actions,
        "failures": failures,
    }


def print_human(report: dict[str, Any]) -> None:
    state = "PASS" if report["passed"] else "FAIL"
    print(
        f"{state} Easy Mode preflight: "
        f"plugin={report['copilot']['installed_plugin'] or 'missing'} "
        f"plugin_version={report['copilot']['plugin_version'] or 'unknown'} "
        f"pac={report['pac']['version'] or 'missing'}"
    )
    for action in report["actions"]:
        print(f"  action: {action}")
    for failure in report["failures"]:
        print(f"  - {failure}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable preflight report",
    )
    args = parser.parse_args(argv)
    report = run_preflight()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
