# Export bundle

Build `engineering-standards-advisor-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/engineering-standards-advisor/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`engineering-standards-advisor-copilot-studio-solution.zip`](engineering-standards-advisor-copilot-studio-solution.zip)
- Deployment settings: [`engineering-standards-advisor-deployment-settings.json`](engineering-standards-advisor-deployment-settings.json)
- Export details: [`engineering-standards-advisor-solution-export.json`](engineering-standards-advisor-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
