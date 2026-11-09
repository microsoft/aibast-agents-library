# Design system: one source, zero copies

Every published page carries one stamped block of design tokens, generated from
`tools/design_tokens.py`. Pages **use** the tokens (`var(--cp-bg)`) and never
**declare** them. That single rule is what makes a retheme cheap: the palette
exists in one file, and the stamper deletes any page-local copy a generator
might put back.

## Retheme in three steps

1. In `tools/design_tokens.py`, add a palette to `PALETTES` (or edit one) and set
   `PALETTE` to its name. Keep every token name. If the palette renders one
   scheme only, add it to `SINGLE_SCHEME`; the theme toggle then hides itself.
2. Run `bash scripts/retheme.sh`. It stamps all pages, regenerates
   `docs/design-system.html`, the metrics contract, the impact report and the
   solution export bundles, then runs the audits and the token tests.
3. Open `docs/design-system.html` and a few real pages. Open a pull request to
   staging.

## What the gates enforce

- `tests/test_design_tokens.py`: every text token reads at 4.5:1 or better on
  every surface, the focus ring at 3:1; the ground is neutral or a committed
  cool colour, never warm paper; one accent; every palette defines the same
  token set; **no page declares a palette token outside the stamped block**.
- `tools/audit_metrics_page.py` and `tools/audit_rapp_guide.py`: the page's own
  CSS uses tokens only, no colour literals, no local palette declarations.
- The scaffold (`tools/scaffold_solution_journey.py`), the impact report builder
  and the film tool import the palette from the module; none of them hold a copy.

## Pages that keep their own colours on purpose

`solutions/_shared/surfaces/*` reproduce the real Microsoft 365 and Copilot
Studio look for demos, `docs/practice/windows.html` reproduces a Windows 11
desktop, and `docs/installer.html` shows a VS Code window. They are not themed
by design, and the stamper leaves their colours alone.

## Palettes on file

- `gallery` (active): the library gallery look. Navy ground, white ink, one cyan
  signal. Dark only.
- `signal`: cool neutral ground with the crimson accent (2026-09 to 2026-11).
- `fluent`: Microsoft neutrals and brand blue, no crimson.
