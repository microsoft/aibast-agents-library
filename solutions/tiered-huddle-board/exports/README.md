# Export bundle

Build `tiered-huddle-board-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \
  solutions/tiered-huddle-board/export-manifest.json
```

Download the published bundle: [`tiered-huddle-board-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/tiered-huddle-board-source.zip).
It is a release asset built from this repository on every change, not a
committed file. A local build writes `tiered-huddle-board-source.zip` to this folder,
which Git ignores.

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.


## Import the Copilot Studio solution

- Solution ZIP: [`tiered-huddle-board-copilot-studio-solution.zip`](tiered-huddle-board-copilot-studio-solution.zip)
- Deployment settings: [`tiered-huddle-board-deployment-settings.json`](tiered-huddle-board-deployment-settings.json)
- Export details: [`tiered-huddle-board-solution-export.json`](tiered-huddle-board-solution-export.json)

The ZIP is an unmanaged solution for manual review. Importing it does not
publish the agent. Review connection references and environment variables
before enabling any integration.

- Import as an unmanaged solution for manual review.
- Map connection references and environment variables before enabling integrations.
- The exported agent remains unpublished unless the target administrator explicitly publishes it.
