# Export bundle

Build `team-ideas-board-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/team-ideas-board/export-manifest.json
```

Download the published bundle: [`team-ideas-board-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/team-ideas-board-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `team-ideas-board-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.
