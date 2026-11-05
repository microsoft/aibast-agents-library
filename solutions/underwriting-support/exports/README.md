# Export bundle

Build `underwriting-support-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/underwriting-support/export-manifest.json
```

Download the published bundle: [`underwriting-support-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/underwriting-support-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `underwriting-support-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`underwriting-support-copilot-studio-solution.zip`](underwriting-support-copilot-studio-solution.zip)
- Deployment settings: [`underwriting-support-deployment-settings.json`](underwriting-support-deployment-settings.json)
- Export details: [`underwriting-support-solution-export.json`](underwriting-support-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
