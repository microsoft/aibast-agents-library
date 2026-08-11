import json
import shutil
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent


def test_landing_page_keeps_two_primary_actions():
    soup = BeautifulSoup(
        (ROOT / "index.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    actions = soup.select(".hero-actions a")
    assert [(link.get_text(" ", strip=True), link.get("href")) for link in actions] == [
        ("Open Production Guide", "docs/rapp-guide.html"),
        ("Browse Agent Library", "library.html"),
    ]


def install_commands(hostname, base):
    text = (ROOT / "index.html").read_text(encoding="utf-8")
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


def test_landing_page_installer_uses_current_pages_host():
    assert shutil.which("node"), "Node.js is required to validate install commands"
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "const publishedBase" in text
    assert "new URL('.', location.href).href" in text
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


def test_staging_install_commands_pin_the_staging_repository_and_ref():
    staging = install_commands(
        "kody-w.github.io",
        "https://kody-w.github.io/aibast-agents-library/",
    )
    for command in (
        staging["bash"],
        staging["windows"],
        staging["macManual"],
        staging["windowsManual"],
    ):
        assert "kody-w/aibast-agents-library" in command
        assert "easy-mode-copilot-chat-pilot" in command
    assert "BRAINSTEM_REPO_URL" in staging["bash"]
    assert "BRAINSTEM_REPO_REF" in staging["bash"]
    assert "BRAINSTEM_VERSION_URL" in staging["bash"]
    assert "$env:BRAINSTEM_REPO_URL" in staging["windows"]


def test_staging_download_wrappers_embed_the_same_pinned_commands():
    text = (ROOT / "index.html").read_text(encoding="utf-8")
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
    for platform in ("macOS/Linux", "Windows"):
        payload = downloads[platform]["href"]
        assert "kody-w/aibast-agents-library" in payload
        assert "easy-mode-copilot-chat-pilot" in payload
