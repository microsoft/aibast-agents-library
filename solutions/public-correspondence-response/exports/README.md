# Export bundle

Build `public-correspondence-response-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/public-correspondence-response/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`public-correspondence-response-copilot-studio-solution.zip`](public-correspondence-response-copilot-studio-solution.zip)
- Deployment settings: [`public-correspondence-response-deployment-settings.json`](public-correspondence-response-deployment-settings.json)
- Export details: [`public-correspondence-response-solution-export.json`](public-correspondence-response-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
