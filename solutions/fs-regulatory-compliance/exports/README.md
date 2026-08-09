# Export bundle

`fs-regulatory-compliance-source.zip` is generated from
`../export-manifest.json`:

```text
python3 tools/build_solution_export.py \
  solutions/fs-regulatory-compliance/export-manifest.json
```

The bundle includes every reviewed source, uploadable knowledge and skill file,
evaluation evidence, all 26 screenshots, the browserfilm, contact sheet, and
the explicit Draft/no-publish gate.
