# Export bundle

Build `field-service-dispatch-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/field-service-dispatch/export-manifest.json
```

Download the published bundle: [`field-service-dispatch-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/field-service-dispatch-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `field-service-dispatch-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`field-service-dispatch-copilot-studio-solution.zip`](field-service-dispatch-copilot-studio-solution.zip)
- Deployment settings: [`field-service-dispatch-deployment-settings.json`](field-service-dispatch-deployment-settings.json)
- Export details: [`field-service-dispatch-solution-export.json`](field-service-dispatch-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
