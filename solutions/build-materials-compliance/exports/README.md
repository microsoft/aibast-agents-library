# Export bundle

Build `build-materials-compliance-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/build-materials-compliance/export-manifest.json
```

Download the published bundle: [`build-materials-compliance-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/build-materials-compliance-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `build-materials-compliance-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`build-materials-compliance-copilot-studio-solution.zip`](build-materials-compliance-copilot-studio-solution.zip)
- Deployment settings: [`build-materials-compliance-deployment-settings.json`](build-materials-compliance-deployment-settings.json)
- Export details: [`build-materials-compliance-solution-export.json`](build-materials-compliance-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
