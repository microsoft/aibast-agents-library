# Export bundle

Build `resource-utilization-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/resource-utilization/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`resource-utilization-copilot-studio-solution.zip`](resource-utilization-copilot-studio-solution.zip)
- Deployment settings: [`resource-utilization-deployment-settings.json`](resource-utilization-deployment-settings.json)
- Export details: [`resource-utilization-solution-export.json`](resource-utilization-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
