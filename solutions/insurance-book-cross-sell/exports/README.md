# Export bundle

Build `insurance-book-cross-sell-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/insurance-book-cross-sell/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`insurance-book-cross-sell-copilot-studio-solution.zip`](insurance-book-cross-sell-copilot-studio-solution.zip)
- Deployment settings: [`insurance-book-cross-sell-deployment-settings.json`](insurance-book-cross-sell-deployment-settings.json)
- Export details: [`insurance-book-cross-sell-solution-export.json`](insurance-book-cross-sell-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
