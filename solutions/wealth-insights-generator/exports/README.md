# Export bundle

Build `wealth-insights-generator-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/wealth-insights-generator/export-manifest.json
```

Download the published bundle: [`wealth-insights-generator-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/wealth-insights-generator-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `wealth-insights-generator-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`wealth-insights-generator-copilot-studio-solution.zip`](wealth-insights-generator-copilot-studio-solution.zip)
- Deployment settings: [`wealth-insights-generator-deployment-settings.json`](wealth-insights-generator-deployment-settings.json)
- Export details: [`wealth-insights-generator-solution-export.json`](wealth-insights-generator-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
