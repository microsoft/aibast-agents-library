# Export bundle

Build `product-feedback-synthesizer-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/product-feedback-synthesizer/export-manifest.json
```

Download the published bundle: [`product-feedback-synthesizer-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/product-feedback-synthesizer-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `product-feedback-synthesizer-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`product-feedback-synthesizer-copilot-studio-solution.zip`](product-feedback-synthesizer-copilot-studio-solution.zip)
- Deployment settings: [`product-feedback-synthesizer-deployment-settings.json`](product-feedback-synthesizer-deployment-settings.json)
- Export details: [`product-feedback-synthesizer-solution-export.json`](product-feedback-synthesizer-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
