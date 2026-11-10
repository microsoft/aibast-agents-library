# Export bundle

Build `invoice-processing-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/invoice-processing/export-manifest.json
```

Download the published bundle: [`invoice-processing-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/invoice-processing-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `invoice-processing-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.
