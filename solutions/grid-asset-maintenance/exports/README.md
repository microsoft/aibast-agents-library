# Export bundle

Build `grid-asset-maintenance-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/grid-asset-maintenance/export-manifest.json
```

Download the published bundle: [`grid-asset-maintenance-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/grid-asset-maintenance-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `grid-asset-maintenance-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`grid-asset-maintenance-copilot-studio-solution.zip`](grid-asset-maintenance-copilot-studio-solution.zip)
- Deployment settings: [`grid-asset-maintenance-deployment-settings.json`](grid-asset-maintenance-deployment-settings.json)
- Export details: [`grid-asset-maintenance-solution-export.json`](grid-asset-maintenance-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
