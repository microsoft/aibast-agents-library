import json
import subprocess

from tools import easy_mode_preflight as preflight


def completed(args, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def official_config(tmp_path, monkeypatch, mutate=None):
    cache = tmp_path / "plugin-cache"
    agents = cache / "agents"
    agents.mkdir(parents=True)
    for name in preflight.CAPABILITY_FILES:
        (agents / name).write_text(f"# {name}\n", encoding="utf-8")
    entry = {
        "name": "mcs-assistant",
        "enabled": True,
        "version": "1.4.0",
        "cache_path": str(cache),
        "source": {
            "source": "github",
            "repo": "microsoft/copilot-studio-plugin",
        },
    }
    if mutate:
        mutate(entry, cache)
    config = tmp_path / "copilot-config.json"
    config.write_text(
        "// Copilot manages this file.\n"
        + json.dumps({"installedPlugins": [entry]}),
        encoding="utf-8",
    )
    monkeypatch.setenv("COPILOT_CONFIG_PATH", str(config))
    return config, cache


def test_accepts_pac_version_output_even_when_command_exits_nonzero(
    monkeypatch, tmp_path
):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(
                args,
                stdout="mcs-assistant 1.4.0\n",
            )
        if args[-1] == "--version":
            return completed(
                args,
                returncode=1,
                stderr=(
                    "Microsoft PowerPlatform CLI\n"
                    "Version: 2.10.1\n"
                ),
            )
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is True
    assert report["copilot"]["installed_plugin"] == preflight.PLUGIN_ID
    assert report["copilot"]["plugin_version"] == "1.4.0"
    assert report["copilot"]["origin_verified"] is True
    assert report["copilot"]["capabilities_verified"] is True
    assert report["pac"]["version"] == "2.10.1"
    assert report["pac"]["version_exit_code"] == 1


def test_pac_parser_prefers_cli_version_over_unrelated_runtime_version():
    parsed = preflight.pac_version(
        "Microsoft PowerPlatform CLI Version: 2.10.1\n"
        "Diagnostic runtime: .NET 8.0.7\n"
    )
    assert parsed == ((2, 10, 1), "2.10.1")


def test_pac_parser_rejects_runtime_version_on_pac_error_line():
    assert (
        preflight.pac_version(
            "PAC CLI failed to start: Framework version: 8.0.7"
        )
        is None
    )


def test_rejects_runtime_version_from_failed_pac(monkeypatch, tmp_path):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(args, stdout="mcs-assistant 1.4.0\n")
        if args[-1] == "--version":
            return completed(
                args,
                returncode=1,
                stderr=(
                    "A fatal error occurred. The required library "
                    "hostfxr.dylib could not be found.\n"
                    "Framework version: 8.0.7\n"
                ),
            )
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is False
    assert report["pac"]["version"] is None
    assert any("PAC-labelled" in failure for failure in report["failures"])


def test_installs_missing_official_plugin_and_rechecks(monkeypatch, tmp_path):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )
    calls = []
    list_count = 0

    def fake_run(args, **_kwargs):
        nonlocal list_count
        calls.append(args)
        if args[-2:] == ["plugin", "list"]:
            list_count += 1
            output = (
                ""
                if list_count == 1
                else "mcs-assistant 1.4.0"
            )
            return completed(args, stdout=output)
        if "marketplace" in args or "install" in args:
            return completed(args, stdout="ok")
        if args[-1] == "--version":
            return completed(
                args,
                stdout="Microsoft Power Platform CLI Version: 2.10.0",
            )
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is True
    assert [
        args[1:] for args in calls if args[0] == "/bin/copilot"
    ] == [
        ["plugin", "list"],
        [
            "plugin",
            "marketplace",
            "add",
            "microsoft/copilot-studio-plugin",
        ],
        [
            "plugin",
            "install",
            "mcs-assistant@copilot-studio-plugin",
        ],
        ["plugin", "list"],
    ]


def test_updates_old_pac_with_dotnet_then_rechecks(monkeypatch, tmp_path):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}",
    )
    pac_checks = 0
    calls = []

    def fake_run(args, **_kwargs):
        nonlocal pac_checks
        calls.append(args)
        if args[-2:] == ["plugin", "list"]:
            return completed(
                args,
                stdout="mcs-assistant 1.4.0",
            )
        if args[-1] == "--version":
            pac_checks += 1
            version = "2.9.3" if pac_checks == 1 else "2.11.0"
            return completed(args, stdout=f"PAC CLI Version: {version}")
        if args[1:4] == ["tool", "update", "--global"]:
            return completed(args, stdout="updated")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is True
    assert report["pac"]["version"] == "2.11.0"
    assert [
        "/bin/dotnet",
        "tool",
        "update",
        "--global",
        "Microsoft.PowerApps.CLI.Tool",
    ] in calls


def test_old_pac_without_dotnet_fails_with_explicit_remediation(
    monkeypatch, tmp_path
):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: (
            f"/bin/{name}" if name in {"copilot", "pac"} else None
        ),
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(
                args,
                stdout="mcs-assistant 1.4.0",
            )
        if args[-1] == "--version":
            return completed(args, stdout="Power Platform CLI 2.9.3")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is False
    assert report["pac"]["supported"] is False
    assert any(
        "dotnet tool update --global Microsoft.PowerApps.CLI.Tool" in failure
        for failure in report["failures"]
    )


def test_plugin_command_failure_is_reported_without_being_swallowed(
    monkeypatch, tmp_path
):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(args, returncode=7, stderr="authentication failed")
        if args[-1] == "--version":
            return completed(args, stdout="PAC CLI Version: 2.10.0")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is False
    assert any(
        "exit 7" in failure and "authentication failed" in failure
        for failure in report["failures"]
    )


def test_rejects_substring_plugin_match(monkeypatch, tmp_path):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(args, stdout="not-mcs-assistant-helper 9.9.9")
        if "marketplace" in args:
            return completed(args, returncode=2, stderr="install blocked")
        if args[-1] == "--version":
            return completed(args, stdout="PAC CLI Version: 2.10.0")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    report = preflight.run_preflight()

    assert report["passed"] is False
    assert report["copilot"]["installed_plugin"] is None


def test_rejects_wrong_plugin_origin(monkeypatch, tmp_path):
    official_config(
        tmp_path,
        monkeypatch,
        lambda entry, _cache: entry.update(
            {"source": {"source": "github", "repo": "someone/fork"}}
        ),
    )
    report = run_with_valid_commands(monkeypatch)
    assert report["passed"] is False
    assert report["copilot"]["origin_verified"] is False


def test_rejects_disabled_plugin(monkeypatch, tmp_path):
    official_config(
        tmp_path,
        monkeypatch,
        lambda entry, _cache: entry.update({"enabled": False}),
    )
    report = run_with_valid_commands(monkeypatch)
    assert report["passed"] is False
    assert report["copilot"]["plugin_enabled"] is False


def test_rejects_missing_capability(monkeypatch, tmp_path):
    official_config(
        tmp_path,
        monkeypatch,
        lambda _entry, cache: (
            cache / "agents" / "copilot-studio-architect.md"
        ).unlink(),
    )
    report = run_with_valid_commands(monkeypatch)
    assert report["passed"] is False
    assert report["copilot"]["capabilities_verified"] is False
    assert report["copilot"]["missing_capability_files"] == [
        "copilot-studio-architect.md"
    ]


def test_rejects_duplicate_plugin_config_entries(monkeypatch, tmp_path):
    config, _cache = official_config(tmp_path, monkeypatch)
    data = json.loads(
        "\n".join(
            line
            for line in config.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("//")
        )
    )
    data["installedPlugins"].append(dict(data["installedPlugins"][0]))
    config.write_text(json.dumps(data), encoding="utf-8")

    report = run_with_valid_commands(monkeypatch)

    assert report["passed"] is False
    assert report["copilot"]["matching_config_entries"] == 2
    assert any("exactly one installedPlugins entry" in item for item in report["failures"])


def test_rejects_cli_and_config_plugin_version_mismatch(
    monkeypatch, tmp_path
):
    official_config(tmp_path, monkeypatch)
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(args, stdout="mcs-assistant 1.4.1")
        if args[-1] == "--version":
            return completed(args, stdout="PAC CLI Version: 2.10.0")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)
    report = preflight.run_preflight()

    assert report["passed"] is False
    assert report["copilot"]["plugin_version_matches_config"] is False
    assert any("does not exactly match" in item for item in report["failures"])


def test_accepts_valid_official_config(monkeypatch, tmp_path):
    config, cache = official_config(tmp_path, monkeypatch)
    report = run_with_valid_commands(monkeypatch)
    assert report["passed"] is True
    assert report["copilot"]["config_path"] == str(config)
    assert report["copilot"]["cache_path"] == str(cache)
    assert report["copilot"]["official_plugin_verified"] is True


def run_with_valid_commands(monkeypatch):
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda name: f"/bin/{name}" if name in {"copilot", "pac"} else None,
    )

    def fake_run(args, **_kwargs):
        if args[-2:] == ["plugin", "list"]:
            return completed(args, stdout="mcs-assistant 1.4.0")
        if args[-1] == "--version":
            return completed(args, stdout="PAC CLI Version: 2.10.0")
        raise AssertionError(args)

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)
    return preflight.run_preflight()


def test_json_cli_reports_versions(monkeypatch, capsys):
    monkeypatch.setattr(
        preflight,
        "run_preflight",
        lambda: {
            "schema": preflight.SCHEMA,
            "passed": True,
            "copilot": {
                "path": "/bin/copilot",
                "installed_plugin": preflight.PLUGIN_ID,
                "plugin_version": "1.5.0",
                "plugin_record": "fixture",
                "config_path": "/config.json",
                "config_loaded": True,
                "matching_config_entries": 1,
                "config_plugin_version": "1.5.0",
                "plugin_version_matches_config": True,
                "plugin_enabled": True,
                "plugin_origin": {
                    "source": "github",
                    "repo": preflight.MARKETPLACE,
                },
                "origin_verified": True,
                "cache_path": "/cache",
                "cache_path_valid": True,
                "capability_files": list(preflight.CAPABILITY_FILES),
                "missing_capability_files": [],
                "capabilities_verified": True,
                "official_plugin_verified": True,
            },
            "pac": {
                "path": "/bin/pac",
                "version": "2.10.0",
                "version_exit_code": 0,
                "minimum_exclusive": "2.9.3",
                "supported": True,
            },
            "actions": [],
            "failures": [],
        },
    )

    assert preflight.main(["--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["copilot"]["installed_plugin"] == preflight.PLUGIN_ID
    assert output["pac"]["version"] == "2.10.0"
