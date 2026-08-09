# Inventory Rebalancing — customer field guide

Use this guide with the customer at the keyboard. The goal is to exercise the
portable source, inspect the Copilot Studio pilot, and identify production
integration seams without presenting synthetic figures as customer outcomes.

## Evidence already established

- Strict-isolation Brainstem: IR-01 through IR-04 passed (4/4).
- Easy Copilot Studio Preview: IR-01 through IR-04 passed in kodyv8.
- Easy identity: `Inventory Rebalancing Pilot`,
  `aibast_InventoryRebalancingPilot`, bot
  `236a0c04-ea66-46e8-b461-1e2b68291c92`.
- Easy configuration: Sonnet46, four skills, two knowledge files, seven changes
  pushed; **Draft, not published**.
- Manual identity: `Inventory Manual Build`, bot
  `05b62fa7-0327-4626-b9db-8c9de02de91a`.
- Manual configuration: Sonnet46, web search removed, four skills, and two
  reviewed full knowledge files; **Draft, not published**.
- Manual Preview passed IR-01 through IR-04 after correcting knowledge parity
  and routing the planning-meeting question to cost analysis.

The source transcript, Easy evidence, and Hard evidence live in `evals/`.

## Easy mode — Copilot-assisted

The customer pastes the Easy prompt from `quest.html` into GitHub Copilot Agent
mode. Copilot owns setup, source verification, Brainstem health, the smoke
prompt, and the Draft-only Copilot Studio promotion workflow.

Do not continue until evidence shows:

1. Brainstem health is `ok`.
2. `InventoryRebalancingAgent` is the loaded tool.
3. The smoke prompt called that tool.
4. The response names Dallas Fulfillment Center and SKU-4406.

Then replay:

- IR-01: “Which distribution centers are tight on space, and which SKU positions should my team review first?”
- IR-02: “Where do we have forecast-relative shortages or excess that deserve a rebalancing review?”
- IR-03: “Show me the proposed warehouse moves, but do not move or reserve anything.”
- IR-04: “Where is inventory exposure concentrated, and what trade-offs should I take to the planning meeting?”

State that every figure is synthetic planning evidence and not a customer KPI.

## Hard mode — literal browser construction

Hard mode uses no PAC CLI, YAML import, or plugin architect. Open
`manual-tutorial.html` and reproduce the agent in the Copilot Studio browser:

1. Create `Inventory Manual Build`, enter the reviewed instructions, and save.
2. Remove web search.
3. Upload both complete Markdown knowledge files. They are byte-identical to
   the reviewed Easy knowledge source.
4. Upload the four `SKILL.md` files individually. Each is the complete
   frontmatter-plus-body extracted from the matching Easy `content: |` block.
5. Select Claude Sonnet 4.6 and audit the complete inventory.
6. Run IR-01 through IR-04 in fresh Preview turns.
7. Record the Draft state and do not publish.

The 22-frame sequence in `screenshots/manual/browserfilm.json` is rendered as a
GIF and contact sheet. Frame 15 is reused truthfully for model confirmation and
frame 16 inventory review because the same capture proves both conditions.

## Production replacement seams

Replace synthetic evidence with approved, governed connections:

- Dynamics 365 Supply Chain Management or another ERP for inventory, demand,
  reorder policy, and lifecycle state;
- warehouse and transportation systems for approved availability, routes, and
  transfer execution;
- Power BI semantic models for governed portfolio and capacity reporting;
- Microsoft Teams or an approved workflow for human review and authorization.

Keep all movement, reservation, reorder, return, liquidation, disposition, and
policy changes behind explicit authorized tools. The pilot recommends only.

## Failure recovery

| Symptom | Recovery |
| --- | --- |
| Brainstem health is unavailable | Rerun the official installer and launcher from `deployment.json`. |
| Source verification fails | Stop and recheck the registry source and SHA-256. |
| Wrong operation answers | Isolate the agent and fix routing; do not retry blindly. |
| Knowledge is missing or incomplete | Upload both full reviewed files, wait for ingestion, and start a fresh Preview conversation. |
| Cost question routes incorrectly | Confirm the cost-analysis skill explicitly covers total annual holding cost and planning-meeting trade-offs. |
| A skill upload fails | Redownload the raw `SKILL.md` and upload the file, not its folder or `.mcs.yml`. |
| Required Preview identifier is missing | Treat the case as failed; recheck instructions, knowledge, skills, model, and web-search removal. |
| Model is unavailable | Record the approved substitute and do not claim model parity. |
| Publish is offered | Stop at Draft unless a separate governance record explicitly approves publication. |

## Evidence gates

Retain source identity, transcripts, environment ID, schema, bot IDs, model,
component inventory, Easy push result, four Preview responses, 22 manual
screenshots, both Draft states, and unresolved connector and authorization work.
Do not call the pilot production-ready or convert synthetic costs and deltas
into customer KPI claims.
