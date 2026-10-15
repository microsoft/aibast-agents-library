# Export bundle

Build `energy-regulatory-reporting-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/energy-regulatory-reporting/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`energy-regulatory-reporting-copilot-studio-solution.zip`](energy-regulatory-reporting-copilot-studio-solution.zip)
- Deployment settings: [`energy-regulatory-reporting-deployment-settings.json`](energy-regulatory-reporting-deployment-settings.json)
- Export details: [`energy-regulatory-reporting-solution-export.json`](energy-regulatory-reporting-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
