# Export bundle

Build `loan-origination-assistant-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/loan-origination-assistant/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.
