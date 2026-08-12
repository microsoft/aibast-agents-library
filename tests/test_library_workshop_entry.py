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
        "Manual mode — inline manual tutorial",
        "Open workshop",
        "Open interactive demo",
        "Workshop settings",
        "Open field guide",
        "Install RAPP Brainstem Frontier",
        "function workshopPackageFor(",
        "function interactiveDemoUrl(",
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
        "Open Beta workshop",
        "Beta workshop",
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


def test_mobile_agent_modal_prevents_grid_min_content_overflow():
    text = LIBRARY.read_text(encoding="utf-8")

    assert ".detail-body { grid-template-columns: minmax(0, 1fr); }" in text
    assert ".detail-body > * { min-width: 0; }" in text
    assert (
        ".filters, .grid, .detail-body, .journey-grid "
        "{ grid-template-columns: 1fr; }"
    ) not in text
