# Export bundle

Build `building-permit-processing-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/building-permit-processing/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`building-permit-processing-copilot-studio-solution.zip`](building-permit-processing-copilot-studio-solution.zip)
- Deployment settings: [`building-permit-processing-deployment-settings.json`](building-permit-processing-deployment-settings.json)
- Export details: [`building-permit-processing-solution-export.json`](building-permit-processing-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
