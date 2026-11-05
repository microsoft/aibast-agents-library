# Export bundle

Build `win-loss-analysis-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/win-loss-analysis/export-manifest.json
```

Download the published bundle: [`win-loss-analysis-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/win-loss-analysis-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `win-loss-analysis-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`win-loss-analysis-copilot-studio-solution.zip`](win-loss-analysis-copilot-studio-solution.zip)
- Deployment settings: [`win-loss-analysis-deployment-settings.json`](win-loss-analysis-deployment-settings.json)
- Export details: [`win-loss-analysis-solution-export.json`](win-loss-analysis-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
