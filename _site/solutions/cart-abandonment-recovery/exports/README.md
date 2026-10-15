# Export bundle

Build `cart-abandonment-recovery-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/cart-abandonment-recovery/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`cart-abandonment-recovery-copilot-studio-solution.zip`](cart-abandonment-recovery-copilot-studio-solution.zip)
- Deployment settings: [`cart-abandonment-recovery-deployment-settings.json`](cart-abandonment-recovery-deployment-settings.json)
- Export details: [`cart-abandonment-recovery-solution-export.json`](cart-abandonment-recovery-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
