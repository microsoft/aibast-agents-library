# Portfolio Rebalancing r5 manual inputs

Build `portfolio-rebalancing-source.zip` with the existing source bundler:

```text
python3 tools/build_solution_export.py solutions/portfolio-rebalancing/export-manifest.json
```

This archive contains only the explicit `bundle.include_paths` list in
the separately published `export-manifest.json`.

Exactly nine frozen r5 manual inputs, their public SHA256 inventory and the export README. No HTML guide, screenshot, native import archive, runtime, tenant binding or raw browser log is included. Use the separately published guides and reviewed PNG reference set; this ZIP is deliberately not a standalone workshop.

It is not a native
Copilot Studio import package, a complete repository mirror, or certification.

An advertised catalog resource is not necessarily a bundle member; the
manifest's `included_in_bundle` flags distinguish them. Images or guides are
included only when explicitly listed. Historical files still in the repository
are not promoted as current evidence.

The historical native import ZIP is separate and is not proof that the manual
skills or knowledge are included. It is withheld from current-workshop
downloads; the review metadata records its inspected contents. No import,
new tenant export, or publication was performed.
See the separately published `evals/manual-pilot-review.json` for the dated
review findings and remaining gates. Public delivery is a separate gate:
after push/deploy, fetch the published URLs and compare the manifest hashes.
Local existence is not live URL verification.
