# Account Intelligence Agent solution package

## Purpose
Consolidates account, stakeholder, competitor, risk, and meeting-preparation views so sellers can prepare consistently without automating customer engagement.

## Architecture
Single-file portable agent with allow-listed account routing, six deterministic operations, synthetic-only source selection, and a common no-side-effect evidence boundary.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2b_sales_stacks/account_intelligence_stack/account_intelligence_agent.py` |
| Deployment recipe | `solutions/account-intelligence/deployment.json` |
| Canonical capture contract | `tests/demo_cases/account-intelligence.json` |
| Package case mirror | `solutions/account-intelligence/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/account-intelligence/evals/transcripts.json` |
| Approved one-pager map | `solutions/account-intelligence/evals/onepager-map.json` |
| Synthetic records | `solutions/account-intelligence/manual/knowledge/aibast_account-intelligence-synthetic-records.md` |
| Operating rules | `solutions/account-intelligence/manual/knowledge/aibast_account-intelligence-operating-rules.md` |
| Uploadable operation skills | `solutions/account-intelligence/manual/skills/*/SKILL.md` |

## Operations
- `account_overview` — Create a synthetic Acme account overview and identify evidence that merits seller attention.
- `stakeholder_map` — Map the synthetic buying committee and relationship gaps without creating outreach tasks.
- `competitive_intel` — Compare synthetic competitor signals and positioning considerations for Acme.
- `value_messaging` — Draft persona-specific talking points for human review; do not send messages.
- `risk_assessment` — Assess synthetic deal risks and mitigation options without changing a forecast or CRM record.
- `executive_briefing` — Prepare a concise synthetic pre-meeting briefing and review checklist.

## Package state
- Source routing is locked to bundled synthetic evidence.
- There is one locked persona demo case and one uploadable skill per operation.
- All six locked cases passed in strict Brainstem isolation with only `AccountIntelligenceAgent` loaded.
- The package includes a source-controlled Copilot Studio Draft, recorded assisted and manual browser evidence, and a literal-browser tutorial.
- Recorded Copilot Studio evidence is dated workshop evidence, not a claim of a current live deployment, remote revalidation, customer proof, or production readiness.
- No production connector or customer-system write is configured, and publication remains off.
- Human approval remains required before any pricing, proposal, outreach, CRM write, task, alert, forecast, or customer communication action.

## Seller starting paths

- **No-install guided replay:** inspect the approved annotated checkpoints and
  practice the six prompts without creating an agent. This is the lowest-friction
  orientation path and is not deployment proof.
- **Facilitator-assisted Easy mode:** a facilitator or IT owner provides the
  supported Copilot Studio plugin and PAC CLI; the seller sends two short
  messages and reviews the six case and Draft gates.
- **Manual mode:** a reviewer reconstructs the Draft in the browser and stops
  before Publish.

## Evidence boundary
All exact names, dates, counts, values, scores, percentages, pricing, ARR, margins, conversion assumptions, and projections are synthetic. They demonstrate deterministic package behavior and do not represent measured customer outcomes, realized revenue, or commitments.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/account-intelligence/field-guide.html` |
| Evidence report | `solutions/account-intelligence/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/account-intelligence/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/account-intelligence/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/account-intelligence/quest.html` |
| Literal browser tutorial | `solutions/account-intelligence/manual-tutorial.html` |
| Raw export manifest | `solutions/account-intelligence/export-manifest.json` |
| Source bundle | `solutions/account-intelligence/exports/account-intelligence-source.zip` |
| Manual evidence | `solutions/account-intelligence/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/account-intelligence/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/account-intelligence/exports/account-intelligence-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/account-intelligence/exports/account-intelligence-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/account-intelligence/exports/account-intelligence-solution-export.json` |

**Scaffold status:** 99 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
