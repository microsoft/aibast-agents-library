# Export bundle

Build `permit-license-management-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/permit-license-management/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`permit-license-management-copilot-studio-solution.zip`](permit-license-management-copilot-studio-solution.zip)
- Deployment settings: [`permit-license-management-deployment-settings.json`](permit-license-management-deployment-settings.json)
- Export details: [`permit-license-management-solution-export.json`](permit-license-management-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
