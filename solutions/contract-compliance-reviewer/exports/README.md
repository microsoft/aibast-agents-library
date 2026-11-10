# Export bundle

Build `contract-compliance-reviewer-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/contract-compliance-reviewer/export-manifest.json
```

Download the published bundle: [`contract-compliance-reviewer-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/contract-compliance-reviewer-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `contract-compliance-reviewer-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.
