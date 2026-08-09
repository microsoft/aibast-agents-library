# Inventory Rebalancing solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/manufacturing_stacks/inventory_rebalancing_stack/inventory_rebalancing_agent.py` |
| Deployment recipe | `solutions/inventory-rebalancing/deployment.json` |
| Customer field guide | `solutions/inventory-rebalancing/FIELD-GUIDE.md` |
| Guided field quest | `solutions/inventory-rebalancing/quest.html` |
| Literal browser tutorial | `solutions/inventory-rebalancing/manual-tutorial.html` |
| Raw export manifest | `solutions/inventory-rebalancing/export-manifest.json` |
| Current source bundle | `solutions/inventory-rebalancing/exports/inventory-rebalancing-source.zip` |
| Copilot Studio source | `solutions/inventory-rebalancing/copilot-studio/` |
| Uploadable manual assets | `solutions/inventory-rebalancing/manual/` |
| Source transcripts | `solutions/inventory-rebalancing/evals/transcripts.json` |
| Easy Preview evidence | `solutions/inventory-rebalancing/evals/copilot-studio-preview-evidence.json` |
| Manual evidence | `solutions/inventory-rebalancing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/inventory-rebalancing/screenshots/manual/manual-build-walkthrough.gif` |
| Assisted browserfilm | `solutions/inventory-rebalancing/screenshots/assisted/copilot-assisted-walkthrough.gif` |

## Proven now

- Portable source: IR-01 through IR-04 passed in strict Brainstem isolation.
- Easy agent: `Inventory Rebalancing Pilot`.
- Schema: `aibast_InventoryRebalancingPilot`.
- Bot ID: `236a0c04-ea66-46e8-b461-1e2b68291c92`.
- Environment: kodyv8 (`ee67a404-325c-e726-a18a-886fe708ca0b`).
- Model: Claude Sonnet 4.6 (`Sonnet46`).
- Easy inventory: four skills and two knowledge files; seven changes pushed.
- Easy Preview: IR-01 through IR-04 passed (4/4).
- Easy status: **Draft; not published**.
- Manual agent: `Inventory Manual Build`, bot
  `05b62fa7-0327-4626-b9db-8c9de02de91a`.
- Manual inventory: web search removed, four skills, and two complete reviewed
  knowledge files.
- Manual source parity: both knowledge downloads are byte-identical to the
  reviewed Easy knowledge, and each `SKILL.md` is the exact full `content: |`
  body from its reviewed Easy behavior YAML, including frontmatter.
- Manual Preview: IR-01 through IR-04 passed after knowledge parity and cost
  routing were corrected.
- Manual status: **Draft; not published**.

## Evidence boundary

Every warehouse, SKU, quantity, classification, utilization, cost, and proposed
move is synthetic pilot evidence. The journey proves routing and review
behavior; it does not prove a customer KPI, live-system access, or an inventory
side effect.
