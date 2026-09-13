# Export bundle

Build `care-gap-closure-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/care-gap-closure/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Historical export — not current source

Historical export predates the SYN-COL — 182 records repair. Do not use it as the repaired source; synchronize the reviewed native files, rerun Preview, and create a fresh unmanaged export before import.

- Historical ZIP (audit only): [`care-gap-closure-copilot-studio-solution.zip`](care-gap-closure-copilot-studio-solution.zip)
- Historical deployment settings: [`care-gap-closure-deployment-settings.json`](care-gap-closure-deployment-settings.json)
- Export details and source-contract warning: [`care-gap-closure-solution-export.json`](care-gap-closure-solution-export.json)

The original ZIP and export timestamp are preserved. The repaired native source
is in `../copilot-studio/`; the regenerated source bundle includes it and the
explicit evidence gaps. No new live export or publication is claimed.
