from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = (
    ROOT
    / "skills"
    / "scout-optimized-install-and-brainstem-use"
    / "SKILL.md"
)


def test_scout_skill_owns_install_start_and_browser_work():
    text = SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    assert text.startswith(
        "---\nname: scout-optimized-install-and-brainstem-use\n"
    )
    for marker in (
        "https://aka.ms/rappinstall",
        "http://localhost:7071/health",
        "microsoft.github.io/aibast-agents-library/install.sh",
        "raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1",
        "~/.copilot/bin/brainstem start",
        "open http://localhost:7071",
        "POST http://localhost:7071/chat",
        "user_input",
        "response",
    ):
        assert marker in compact

    assert "Do not ask the user to open Terminal" in text
    assert "automation-only browser context" in compact


def test_scout_skill_separates_auth_and_never_deploys_azure():
    text = SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for marker in (
        "GitHub Copilot authentication and Microsoft 365 authentication as separate domains",
        "does not grant MSX or Microsoft 365 access",
        "do not run the Azure deployment commands",
        "no Azure resources were provisioned",
    ):
        assert marker in compact


def test_scout_skill_requires_live_health_chat_and_rar_proof():
    text = SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for marker in (
        'status: "ok"',
        "a non-empty `response` field",
        "copilot plugin marketplace add kody-w/RAR",
        "copilot plugin install rapp@rar",
        "new conversation discovers `rapp-skills`",
        "installer exit code without a healthy endpoint is not success",
    ):
        assert marker in compact
