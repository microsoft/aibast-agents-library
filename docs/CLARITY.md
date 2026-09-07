# Microsoft Clarity on the AIBAST site

[Microsoft Clarity](https://clarity.microsoft.com/) records how visitors move
through the published site (heatmaps, session recordings, rage clicks, scroll
depth). It complements `metrics.html`, which reports downloads, Discussions,
and workshop adoption from GitHub data. Clarity is free and adds no cookie
banner requirement of its own, but see "Privacy posture" below.

## Where the tag lives

- `clarity.json` (repository root) holds the single project ID.
- `scripts/apply_clarity_tag.py` renders the tag from that file and stamps it
  before `</head>` on every published page: root HTML, `docs/`, `reports/`,
  and every `solutions/**` page.
- `tests/test_clarity_tag.py` fails when any page is missing the current tag,
  when two pages disagree, or when installed software is tagged.

Never tagged: `rapp_brainstem/` (installs on user machines), `rapp_ai/`
(bundled with the Azure function), `tools/` (local-first tools), `beta/`.

## Enable it (one time, about five minutes)

1. Sign in at https://clarity.microsoft.com/ with the account that should own
   the analytics for this repository.
2. **Add new project**. Name: `AIBAST Agents Library`. Website:
   `https://microsoft.github.io/aibast-agents-library`. Category: Technology.
3. Open the project, then **Settings > Setup > Install tracking code
   manually**. Copy only the project ID, the short lowercase token that ends
   the `https://www.clarity.ms/tag/<id>` URL in the snippet.
4. Put it in `clarity.json`:

   ```json
   "project_id": "<id>"
   ```

5. Stamp every page and verify:

   ```bash
   python scripts/apply_clarity_tag.py
   python scripts/apply_clarity_tag.py --check
   python -m pytest tests/test_clarity_tag.py -q
   ```

6. Commit, push, and promote through the normal release path. Clarity shows
   the first sessions within a couple of hours of the Pages deploy.

To rotate or revoke: change or blank `project_id`, rerun the script, commit.
A blank ID keeps the block on every page but the loader exits before it
contacts Clarity.

## Privacy posture

The stamped block is a consent-gated Clarity loader:

- **Consent first.** A small bar at the bottom of the page explains that the
  site uses Microsoft Clarity, links the Microsoft Privacy Statement, and
  offers Accept / Decline. Clarity is not loaded, and sets no cookie, until the
  visitor accepts. The choice is stored per browser under
  `localStorage["aibast-clarity-consent"]` ("granted" or "denied") and the bar
  never returns once answered. Accepting also sends Clarity's `consent` signal,
  so the project's **Cookie consent: Required** setting can stay on.
- It only loads on `*.github.io` hosts. Local previews, `file://` opens, and
  forks served elsewhere never report sessions.
- It stays silent, with no bar, when the browser sends Global Privacy Control
  or Do Not Track.
- The bar is drawn with CSS system colours (Canvas, CanvasText, AccentColor),
  so it follows the visitor's light or dark scheme on every page without
  touching any page's theme tokens.

Clarity masks text input by default. Keep **Masking: Strict** and **Cookie
consent: Required** in the project settings.

## Bundles and gates

The block is a hosting artifact, not solution content. Downloadable solution
bundles (`tools/build_solution_export.py`) ship pages without it, and the
workshop rollout audit compares bundle and page bytes with the block removed on
both sides, so changing the tag never rebuilds a bundle. The Academy security
gate likewise scans `academy.html` with the block removed; every other
analytics or tracking pattern remains forbidden there.
