# Manual workshop review source bundle

Build `fs-customer-onboarding-source.zip` with the existing source bundler:

```text
python3 tools/build_solution_export.py solutions/fs-customer-onboarding/export-manifest.json
```

This archive contains only the explicit `bundle.include_paths` list in
`../export-manifest.json`: the manual policy, all manual skills and knowledge,
the learner guide, and public-safe review metadata. It is not a native
Copilot Studio import package, a complete repository mirror, or certification.

Raw browser logs, tenant bindings, native import archives, screenshots,
annotations, recordings, and unrelated source files are excluded. Historical
files still in the repository are not promoted as current evidence.

The historical native import ZIP is separate and is not proof that the manual
skills or knowledge are included. It is withheld from current-workshop
downloads; the review metadata records its inspected contents. No import,
new tenant export, or publication was performed.
See `../evals/manual-pilot-review.json` for exact source and live-evidence limits.
