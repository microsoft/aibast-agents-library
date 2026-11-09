# Gallery submissions

Each folder here is one AIBAST industry solution laid out exactly the way the
[Copilot Studio Gallery](https://github.com/microsoft/copilot-studio-gallery)
accepts a contribution:

```text
submissions/<slug>/
├── metadata.json   gallery metadata (name, description, tags, category, author)
├── README.md       visitor overview written from the solution catalog
└── solution/       the exported, unmanaged Copilot Studio solution, unpacked
```

The payload is the native Copilot Studio export already kept under
`solutions/<slug>/exports/`. `tools/build_gallery_submissions.py` unpacks it, sets the
agent and solution display names to the advertised solution name, adds a greeting
that lists the sample prompts when the export has none, sets the model series to
`Auto` so the sample imports into any tenant, and writes the two sidecar files.
Nothing else in the export is changed.

## Workflow

1. Add the slug and its gallery category to `tools/gallery_submissions.json`.
2. Run `python tools/build_gallery_submissions.py`, then `python tools/build_library_api.py`,
   and commit the output. The first writes the folder, its page shell (`index.html`) and the
   deterministic download `solutions/<slug>/exports/<slug>-gallery-solution.zip`; the second
   publishes `api/v1/gallery/<slug>.json`, which the page renders. `--check` on both (also run
   by the tests) fails on any drift.
3. Verify the folder with the gallery's own tooling: copy it into a clone of the
   gallery and run `npm run check:submissions`, then `npm run build`.
4. Import the solution into a fresh environment and send the first sample prompt
   in the Copilot Studio test pane.
On the site, `submissions/` is the gallery view: a grid, and one page per solution with
Overview, Agents and Files, the recorded demo first and the download second.

The folders are kept in the gallery's shape so any of them could be contributed
later without rework; nothing here is submitted to the gallery.

Everything here is synthetic. No customer data, connections, or credentials.
