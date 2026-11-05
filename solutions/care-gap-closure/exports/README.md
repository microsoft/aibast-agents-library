# Export bundle

Build `care-gap-closure-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/care-gap-closure/export-manifest.json
```

Download the published bundle: [`care-gap-closure-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/care-gap-closure-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `care-gap-closure-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`care-gap-closure-copilot-studio-solution.zip`](care-gap-closure-copilot-studio-solution.zip)
- Deployment settings: [`care-gap-closure-deployment-settings.json`](care-gap-closure-deployment-settings.json)
- Export details: [`care-gap-closure-solution-export.json`](care-gap-closure-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
