# The library site, rebuilt around the Copilot Studio Gallery

Status: design accepted by Kody on 2026-11-09 ("full rethink and rewrite"), with three picks:
Python static pages, not Astro; land the design-token PR (#501) first; port every page before
anything ships. This document is the contract the rebuild is checked against.

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
