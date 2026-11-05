# Export bundle

Build `personalized-marketing-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/personalized-marketing/export-manifest.json
```

Download the published bundle: [`personalized-marketing-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/personalized-marketing-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `personalized-marketing-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`personalized-marketing-copilot-studio-solution.zip`](personalized-marketing-copilot-studio-solution.zip)
- Deployment settings: [`personalized-marketing-deployment-settings.json`](personalized-marketing-deployment-settings.json)
- Export details: [`personalized-marketing-solution-export.json`](personalized-marketing-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
