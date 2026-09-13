# Prior Authorization r4 manual inputs and locked cases

Build `prior-authorization-source.zip` with the existing source bundler:

```text
python3 tools/build_solution_export.py solutions/prior-authorization/export-manifest.json
```

This archive contains only the explicit `bundle.include_paths` list in
the separately published `export-manifest.json`.

Seven frozen r4 native inputs, the unchanged canonical case file, their public SHA256 inventory and the export README. Use the separately published current guides and reviewed PNG references. No HTML guide, screenshot, runtime, tenant binding, raw browser log or historical native import archive is bundled.

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
