# Export bundle

`building-permit-processing-source.zip` is generated from
`../export-manifest.json`:

```text
python3 tools/build_solution_export.py \
  solutions/building-permit-processing/export-manifest.json
```

The bundle includes the portable agent, deployment recipe, field guide,
Copilot Studio YAML, uploadable knowledge, uploadable `SKILL.md` files,
evaluation evidence, tutorial, screenshots, GIFs, and source manifests.
