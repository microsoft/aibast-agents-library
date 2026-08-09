# AI BAST solution packages

`solutions/` contains the customer-facing and deployment assets that sit beside
the portable Python agents under `agents/@aibast-agents-library/`.

## Structure

```text
solutions/
├── catalog.json                         # Hand-authored business and architecture copy
├── _shared/
│   ├── m365-copilot-demo.html           # Shared M365 Copilot-style transcript player
│   └── workshop-settings.html           # Global persisted Easy-mode harness setting
└── <solution-slug>/
    ├── README.md                        # Package map and quality status
    ├── deployment.json                  # Machine-readable no-terminal deployment recipe
    ├── quest.html                       # Guided Easy/Hard workshop
    ├── field-guide.html                 # Styled facilitator and learner guide
    ├── evidence-report.html             # Styled deterministic/visual evidence summary
    ├── manual-tutorial.html             # Screenshot-by-screenshot no-assistance build
    ├── export-manifest.json             # Raw GitHub file and bundle contract
    ├── manual/skills/*/SKILL.md          # Directly uploadable Copilot Studio skills
    ├── exports/*.zip                    # Complete customer download bundle
    ├── evals/
    │   ├── onepager-map.json            # Advertised promise -> operation -> prompt
    │   ├── transcripts.json             # Exact isolated Brainstem transcript corpus
    │   └── visual-checkpoints.json       # Reusable-versus-hidden screenshot contract
    └── screenshots/                     # Copilot-assisted and manual browser evidence
```

## Source-of-truth boundaries

- `agents/.../<solution>_agent.py` owns portable runtime behavior and synthetic
  domain data.
- `state/onepager_content.json` is generated evidence extracted from the
  approved PowerPoint one-pagers.
- `solutions/catalog.json` is deliberately hand-authored. PowerPoint extraction
  may inform it, but never publishes directly.
- `tests/demo_cases/*.json` is the executable routing and behavior gate.
- `solutions/<slug>/evals/transcripts.json` is the canonical source for static
  demos and downstream Copilot Studio acceptance tests.
- `solutions/<slug>/deployment.json` is the machine-readable contract used by
  GitHub Copilot Agent mode to install without asking the user to open a
  terminal.
- Easy mode uses Copilot to author, review, push, and validate the
  source-controlled Copilot Studio project. GitHub Copilot-only is the global
  default; the optional Brainstem harness is selected once in
  `solutions/_shared/workshop-settings.html` and persists across workshops on
  that browser and device.
- Hard mode recreates the same agent manually in the Copilot Studio browser:
  instructions, knowledge, every skill, model selection, and Preview.
- Generated quests award self-paced local **Agent Growth & Impact (AGI) Points**
  for idempotent workshop milestones. Progress remains in the browser under
  `aibast:agi-profile:v1`; `achievements.html` provides privacy-filtered
  export/import/reset controls and clearly separates local progress from
  optional GitHub-verified sync. A single opt-in AGI progress issue carries the
  workshop's canonical earned badge IDs; later submissions merge newly earned
  IDs without duplicating server-defined score.

## Release gate

A solution is not ready merely because an agent file imports.

1. Every advertised one-pager capability maps to implemented behavior.
2. The synthetic data contains the customer problem the slide describes.
3. Persona-language prompts route to the agent in an isolated Brainstem.
4. The deterministic output proves the expected entities and decisions.
5. Canonical transcripts are captured from those exact live runs.
6. Static demos render the captured transcripts rather than invented replies.
7. Copilot Studio replays the same corpus before publishing.

Run the end-to-end coverage audit at any time:

```text
python3 tools/audit_solution_rollout.py
python3 tools/audit_solution_rollout.py --json > state/solution_rollout.json
```

A journey is complete only when the audit finds curated copy, locked cases,
isolated transcripts, deployment assets, Easy evidence, a real assisted
browserfilm, a literal manual tutorial and browserfilm, and a complete export
bundle.

## Claims policy

Public sales copy uses qualitative claims such as *improves*, *reduces*,
*accelerates*, *strengthens*, and *protects*. Synthetic figures may appear
inside clearly labeled demos as operational evidence, but are never presented
as customer results or performance commitments.
