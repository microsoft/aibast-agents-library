# Export bundle

Build `reporting-package-validation-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/reporting-package-validation/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`reporting-package-validation-copilot-studio-solution.zip`](reporting-package-validation-copilot-studio-solution.zip)
- Deployment settings: [`reporting-package-validation-deployment-settings.json`](reporting-package-validation-deployment-settings.json)
- Export details: [`reporting-package-validation-solution-export.json`](reporting-package-validation-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
