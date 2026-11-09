# The library site, rebuilt around the Copilot Studio Gallery

Status: design accepted by Kody on 2026-11-09 ("full rethink and rewrite"), with three picks:
Python static pages, not Astro; land the design-token PR (#501) first; port every page before
anything ships. This document is the contract the rebuild is checked against.

Built (2026-11-09, branch `feat/gallery-site`): `tools/build_site.py` generates the whole site into
`dist/` (never committed) from `submissions/<slug>/` plus the section modules in `tools/site_pages/`
(learn, install, about, docs). `scripts/build_pages_site.py` runs the generator when the Pages
artifact is built; a generated page wins over the repository copy at the same address, so the old
pages stay in git until their tests retire. Every old address has a redirect stub (`REDIRECTS`).
Four reference pages keep their address and ride inside the shell with their own styles
(`tools/site_pages/docs.py`: the Brainstem start page, the AIBAST RAPP pattern, the design system,
the metrics administrator setup). Deliberately left as they are: `docs/practice/windows.html` (a
Windows replica) and `docs/experimental/` (the experimental tools, their own surface). Run locally:
`python tools/build_site.py --out dist && python -m http.server -d dist 8000`.

Who built this before, and what they paid for: Astro, Hugo and Jekyll (commit the inputs, build the
HTML, validate every record at the door with a schema); app stores and Docker Hub (a card shows the
same few real facts in the same place, one action, details behind it); the Linux `/usr` merge (an
old path keeps working and says where the thing went). The Copilot Studio Gallery is all three
applied to Copilot Studio solutions, which is why we copy its structure rather than its code.

## 1. What changes

| Today | After |
| --- | --- |
| 340 hand-authored or scaffolded HTML pages committed to the tree; a retheme touched 319 of them | HTML is built, never committed. One generator, `tools/build_site.py`, writes `dist/` from the inputs below. `scripts/build_pages_site.py` runs it for the Pages artifact. |
| A solution's facts live in nine places (registry `_solution`, `solutions.json`, `deployment.json`, `academy.json`, `field-notes.json`, the scaffold, four page files…) | One folder per solution, `submissions/<slug>/`, in the gallery's exact submission shape plus one AIBAST sidecar. Everything on a solution page comes from that folder. |
| 15 root pages with 15 different shells, navs and footers | One shell (header, nav, footer, tokens) for every page. Five sections. |
| `solution.html?slug=` and 4 scaffolded pages per solution | `/solutions/<slug>/` with Overview / How it works / What's inside / Set it up tabs; demo first, download second (gallery rail, our order). The scaffolded pages become tabs or supporting files on that page and keep their URLs. |
| Hand-written JS per page | One `site.js`: search, type and facet filters, tabs, copy buttons. No framework. |

What does not change: `rapp_brainstem/`, the installers and their `docs/install.*` mirrors, `registry.json`
and `build_registry.py`, `api/` (rapp-static-api/1.1), the staging ring and gates, the Grail boundary.

## 2. The one input: `submissions/<slug>/`

Built by `tools/build_gallery_submissions.py` from the native Copilot Studio export (PR #500's
design, now for all 72). Verified 2026-11-09: 72 of 72 pass the gallery's own `npm run check:submissions`
and the gallery site builds with them (475 pages, exit 0).

```
submissions/<slug>/
  metadata.json      gallery metadata, gallery schema, nothing else
  README.md          the visitor overview (becomes the Overview tab)
  solution/          the exploded unmanaged export (the download)
  supporting/        up to 5 files the gallery allows (sample data CSV/JSON/TXT)
  screenshots/       the recorded demo frames (gallery-tolerated; verified it passes the checker)
  library.json       AIBAST sidecar (verified the checker ignores it)
```

**Two-way contract (locked 2026-11-09, Kody: "anything that we add to our library is completely compatible
and vice versa").** The folder is the unit and the gallery's shape is the law in both directions:

- *Inbound.* `gallery_docs` discovers every `submissions/<slug>/` that has `metadata.json` and a
  `solution/` (or `app/`) folder. No list to keep in step; `tools/gallery_submissions.json` only adds
  AIBAST overrides (`featured`, `category`). Forms our own exports never use are read as the gallery
  writes them: an `authors` list as well as `author`/`authorUrl`, flows-only packages (no agent),
  several agents in one package (components attributed by their `<agent schema>.<kind>.` prefix),
  `submissionType: managed-app`. A folder without a committed export zip gets its download built from
  `solution/` at build time (`downloads/<slug>.zip`, byte-stable), the way the gallery builds its own.
  Provenance comes from `library.json` → `origin: {name, url}`; a folder we did not author never links
  to the AIBAST contributor page. Gate: `tests/test_gallery_shape_compat.py` (fixtures under
  `tests/fixtures/gallery_shape/`).
- *Outbound.* Every one of our folders must pass the gallery's own checker, unchanged. Gate:
  `tools/check_gallery_shape.sh` clones `microsoft/copilot-studio-gallery` at the commit pinned in
  `tools/gallery_contract.json` and runs `importSubmissions({check: true})` against this tree (72 of 72
  on 2026-11-09). Read-only toward the gallery: nothing is ever pushed there.
- *Content.* The gallery's five publication checks (sample + regulated-use wording, no credential
  files, declared connections and flows named in the README, no production or certification claims,
  prerequisites) run mechanically in `tools/check_gallery_content.py`: strict for folders we author,
  advisory for inbound ones (their reviewer judges "equivalent wording" by reading; their own tree
  reads 1 of 36 under this strictness). Every README the builder writes carries a standard
  "Before you rely on it" section and lists the connections the package declares (72 of 72 pass).
- *Import proof.* `tools/attest_gallery_imports.py` imports every download ZIP into a named fresh
  environment with the Power Platform CLI (no skipped dependency checks) and records the result per
  slug in `state/gallery_import_attestation.json`; `library.json` carries it and the page shows
  "Import proof". This is the attestation the gallery's pull-request template asks for.
- *Carrying their entries.* `tools/aggregate_gallery.py` copies the slugs listed in
  `tools/gallery_inbound.json` (empty until Kody names them) from the pinned gallery commit into
  `submissions/<slug>/` byte for byte, plus a `library.json` whose `origin` names the Copilot Studio
  Gallery, its commit and MIT licence; `--check` verifies the copies. Our own slugs are refused.

`library.json` (schema `aibast-library-solution/1.0`) carries what the gallery shape has no field for and
what the detail page needs beyond the export: `industries`, `personas`, `products`, `sample_prompts`,
`capabilities`, `outcomes`, `try` (recorded demo page + scenarios), `assets` (one-pager / demo video
availability, never the files), `learn` (academy course, field guide, manual tutorial, evidence report),
`install` (Brainstem one-liner, AI prompt), `tests` (passed / cases from the locked demo cases). It is
written by the builder from the catalog; nobody hands-edits it.

## 3. Routes (the gallery's, plus our sections)

| Route | Gallery equivalent | Source |
| --- | --- | --- |
| `/` | `/` gallery: search, type radio, category chips, Filters dialog (contains / categories / tags / contributors), community grid | all submissions |
| `/built-by-aibast/` | `/built-by-microsoft` | `featured: true` submissions |
| `/solutions/<slug>/` | `/solutions/[slug]` | the folder |
| `/solutions/<slug>/{quest,field-guide,manual-tutorial,evidence-report}.html` | supporting pages | same folder; same URLs as today |
| `/tags/<tag>/`, `/categories/<category>/` | `/tags/[tag]`, `?category=` | derived |
| `/contributors/`, `/contributors/<key>/` | same | AIBAST, partners (`partners.json`), community authors (`community_tools.json`) |
| `/solutions.json` | same | alias of `api/v1/gallery/index.json` |
| `/install/` | — | `docs/installer.html` content |
| `/learn/` (+ `/learn/academy/`, `/learn/practice/`, `/learn/tutorial/`, `/learn/guide/`, `/learn/vault/…`) | — | academy, practice, tutorial, rapp-guide, vault |
| `/metrics/`, `/blog/`, `/why/`, `/releases/`, `/request/`, `/partners/`, `/pitch/` | — | today's pages, in the shell |
| `/404.html` | same | — |

Nav: Solutions · Industries (category pages) · Learn · Install · About (why, partners, metrics, blog, releases).

## 4. Delete by aliasing

Every HTML path in today's tree (340) is emitted by the generator as a redirect stub to its new home,
with a one-line "this page is now at …". `tests/test_site.py` fails if any old path is missing. Nothing
is deleted until a measured check shows zero traffic (Clarity), on a dated schedule.

## 5. Theme

The one-source tokens from PR #501 (`tools/design_tokens.py`, palette `gallery`, dark only). The generator
calls `render_tokens()` once into the shell; no page declares a palette token. The gallery mockup
(`aibast-rapp/docs/mockups/library-gallery.html`) is the visual reference: 52px header with the four
squares, 1200px wrap, chips, 8px cards, cyan tab underline, 320px rail.

## 6. Gates

`tests/test_site.py`: build is idempotent; every route in §3 exists; every old path in §4 exists; no
page-local palette declarations; every internal link resolves inside `dist/`; `submissions/` passes
the gallery checker (pinned gallery commit, run in CI with Node); `tools/build_library_api.py --check`
still green; browser audit (`npm run academy`) on the new routes. Existing gates for installers,
registry, API and metrics are untouched. Tests that pinned the shape of retired pages retire with them.

## 7. Build order (one PR to staging, nothing partial ships)

1. Shell + home + 72 detail pages + tags/categories/contributors + 404 + `solutions.json` (the spine).
2. Supporting pages (quest, field guide, manual tutorial, evidence) rendered by the generator inside the shell.
3. Learn (academy, practice, tutorial, guide, vault), Install, About pages ported into the shell.
4. Redirect stubs, link check, old page tests retired, `build_pages_site.py` switched to `dist/`.
5. Screenshots of every route, browser audit, promotion check, PR.
