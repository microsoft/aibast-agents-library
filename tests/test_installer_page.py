import json
import shutil
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent


def test_installer_page_keeps_two_primary_actions():
    soup = BeautifulSoup(
        (ROOT / "docs" / "installer.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    actions = soup.select(".hero-actions a")
    assert [(link.get_text(" ", strip=True), link.get("href")) for link in actions] == [
        ("Open Production Guide", "rapp-guide.html"),
        ("Browse Agent Library", "../index.html"),
    ]


def install_commands(hostname, base):
    text = (ROOT / "docs" / "installer.html").read_text(encoding="utf-8")
    start = text.index("function buildInstallCommands")
    end = text.index("const installCommands")
    script = text[start:end]
    result = subprocess.run(
        ["node"],
        input=(
            script
            + "\nconsole.log(JSON.stringify(buildInstallCommands("
            + json.dumps(hostname)
            + ", "
            + json.dumps(base)
            + ")));\n"
        ),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_installer_page_installer_uses_current_pages_host():
    assert shutil.which("node"), "Node.js is required to validate install commands"
    text = (ROOT / "docs" / "installer.html").read_text(encoding="utf-8")
    assert "const publishedBase" in text
    assert "new URL('..', location.href).href" in text  # docs/ -> site root
    assert "id=\"brainstem-win-cmd\"" in text

    production = install_commands(
        "microsoft.github.io",
        "https://microsoft.github.io/aibast-agents-library/",
    )
    assert production["bash"] == (
        "curl -fsSL https://microsoft.github.io/aibast-agents-library/"
        "install.sh | bash"
    )
    assert production["windows"] == (
        "irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex"
    )


def test_hero_matches_production_shape():
    soup = BeautifulSoup(
        (ROOT / "docs" / "installer.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    hero = soup.select_one(".hero")
    assert hero.select(".academy-action") == []
    assert hero.select(".academy-copy") == []
    paragraphs = [p.get_text(" ", strip=True) for p in hero.select("p:not(.why-link)")]
    assert len(paragraphs) == 1
    assert hero.select_one("p.why-link a")["href"] == "../why.html"
    assert paragraphs[0].startswith("A local frontier learning and rapid prototyping tool")


def test_brainstem_is_positioned_as_a_learning_platform_not_a_first_party_competitor():
    text = (ROOT / "docs" / "installer.html").read_text(encoding="utf-8")
    compact = " ".join(text.split())
    assert "local frontier learning and rapid prototyping tool" in compact
    assert "graduates into GitHub Copilot, Copilot Studio, and Microsoft 365 Copilot" in compact
    assert "Local frontier learning and rapid prototyping tool — learn the pattern here, then graduate it" in compact
    assert "It is a learning and prototyping tool, not a product you ship" in compact
    assert "Your local learning platform. Installs everything." in compact
    assert 'href="../why.html"' in text
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    assert "local frontier learning and rapid prototyping tool" in readme
    assert "not a product you ship" in readme


def test_installer_page_carries_only_the_brainstem_lanes():
    soup = BeautifulSoup((ROOT / "docs" / "installer.html").read_text(encoding="utf-8"), "html.parser")
    tabs = [b.get("data-tab") for b in soup.select(".install-tab")]
    assert tabs == ["one-liner", "manual"]
    text = (ROOT / "docs" / "installer.html").read_text(encoding="utf-8")
    assert "buildCopilotLane" not in text and "Copilot-only" not in text


def test_staging_ring_uses_the_same_short_one_liner_as_production():
    staging = install_commands(
        "kody-w.github.io",
        "https://kody-w.github.io/aibast-agents-library/",
    )
    assert staging["bash"] == (
        "curl -fsSL https://kody-w.github.io/aibast-agents-library/install.sh | bash"
    )
    assert staging["windows"] == (
        "irm https://kody-w.github.io/aibast-agents-library/install.ps1 | iex"
    )
    for command in (staging["macManual"], staging["windowsManual"]):
        assert "--branch staging https://github.com/kody-w/aibast-agents-library.git" in command
    for command in staging.values():
        assert "BRAINSTEM_" not in str(command)
        assert "easy-mode-copilot-chat-pilot" not in str(command)


def test_staging_download_wrappers_embed_the_short_ring_commands():
    text = (ROOT / "docs" / "installer.html").read_text(encoding="utf-8")
    commands_start = text.index("function buildInstallCommands")
    commands_end = text.index("const installCommands")
    downloads_start = text.index("function buildInstallerDownloads")
    downloads_end = text.index("const downloads = buildInstallerDownloads")
    script = (
        text[commands_start:commands_end]
        + text[downloads_start:downloads_end]
    )
    probe = r"""
globalThis.Blob = class {
  constructor(parts) { this.payload = parts.join(""); }
};
globalThis.URL = { createObjectURL(blob) { return blob.payload; } };
const commands = buildInstallCommands(
  "kody-w.github.io",
  "https://kody-w.github.io/aibast-agents-library/"
);
console.log(JSON.stringify(buildInstallerDownloads(commands)));
"""
    result = subprocess.run(
        ["node"],
        input=script + probe,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    downloads = json.loads(result.stdout)
    assert "https://kody-w.github.io/aibast-agents-library/install.sh | bash" in downloads["macOS/Linux"]["href"]
    assert "irm https://kody-w.github.io/aibast-agents-library/install.ps1 | iex" in downloads["Windows"]["href"]
    for platform in ("macOS/Linux", "Windows"):
        assert "BRAINSTEM_" not in downloads[platform]["href"]
