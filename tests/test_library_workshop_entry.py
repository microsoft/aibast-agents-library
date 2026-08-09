import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library.html"


def test_library_routes_architecture_into_the_beta_workshop():
    text = LIBRARY.read_text(encoding="utf-8")

    for required in (
        "Learn and build",
        "Guided Easy mode",
        "Hard mode — inline manual tutorial",
        "Open Beta workshop",
        "Workshop settings",
        "Open field guide",
        'localStorage.getItem("aibast:workshop-engine")',
        "GitHub Copilot + Brainstem",
        "GitHub Copilot",
    ):
        assert required in text

    for obsolete in (
        "Implementation modes",
        "Try locally — one prompt, no terminal",
        "Promote to Copilot Studio — one prompt",
        "Copy Brainstem setup prompt",
        "Copy Copilot Studio prompt",
        'data-action="deploy-mode"',
        "PAC command sequence",
    ):
        assert obsolete not in text


def test_library_scripts_parse_after_workshop_entry_change(tmp_path):
    text = LIBRARY.read_text(encoding="utf-8")
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", text, re.DOTALL)
    assert scripts
    for index, script in enumerate(scripts):
        path = tmp_path / f"library-{index}.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
