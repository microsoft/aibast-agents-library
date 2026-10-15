# Export bundle

Build `supplier-risk-monitoring-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/supplier-risk-monitoring/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`supplier-risk-monitoring-copilot-studio-solution.zip`](supplier-risk-monitoring-copilot-studio-solution.zip)
- Deployment settings: [`supplier-risk-monitoring-deployment-settings.json`](supplier-risk-monitoring-deployment-settings.json)
- Export details: [`supplier-risk-monitoring-solution-export.json`](supplier-risk-monitoring-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
