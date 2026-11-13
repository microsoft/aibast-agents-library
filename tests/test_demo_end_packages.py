"""The Cowork and Copilot Studio demo views end on their own counted download."""
from pathlib import Path

PAGE = (Path(__file__).resolve().parents[1] / "solutions/_shared/m365-copilot-demo.html").read_text(encoding="utf-8")


def test_each_product_view_ends_on_its_own_package():
    assert "Try it in your own Cowork" in PAGE
    assert "Try it in your own Copilot Studio" in PAGE
    assert "file: 'cowork-plugin'" in PAGE
    assert "file: 'copilot-studio-solution'" in PAGE
    # The Microsoft 365 Copilot view keeps the setup card.
    assert "END_PACKS[id]" in PAGE and "m365:" not in PAGE.split("END_PACKS = {")[1].split("};")[0]


def test_end_downloads_come_from_the_counted_release():
    assert "/releases/download/solution-bundles/${solution.slug}-${pack.file}.zip" in PAGE
    assert "location.hostname.endsWith('.github.io')" in PAGE


def test_each_ending_has_three_steps():
    block = PAGE.split("END_PACKS = {")[1].split("function endFor")[0]
    for part in block.split("steps: [")[1:]:
        assert part.split("],")[0].count("', '") == 2
