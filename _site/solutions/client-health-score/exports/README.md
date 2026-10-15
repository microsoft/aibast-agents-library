# Export bundle

Build `client-health-score-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/client-health-score/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`client-health-score-copilot-studio-solution.zip`](client-health-score-copilot-studio-solution.zip)
- Deployment settings: [`client-health-score-deployment-settings.json`](client-health-score-deployment-settings.json)
- Export details: [`client-health-score-solution-export.json`](client-health-score-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
