# Export bundle

Build `content-launch-clearance-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/content-launch-clearance/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`content-launch-clearance-copilot-studio-solution.zip`](content-launch-clearance-copilot-studio-solution.zip)
- Deployment settings: [`content-launch-clearance-deployment-settings.json`](content-launch-clearance-deployment-settings.json)
- Export details: [`content-launch-clearance-solution-export.json`](content-launch-clearance-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
