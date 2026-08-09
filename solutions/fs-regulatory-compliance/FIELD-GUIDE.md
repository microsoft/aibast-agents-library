# Regulatory Compliance Agent — customer field guide

This guide is for a seller, specialist, architect, or customer champion running
the Regulatory Compliance Agent with the customer at the keyboard.

The goal is to show a governed compliance workflow, not to make a legal
determination. The pilot uses synthetic records to expose control gaps,
evidence, owners, and approval points. It cannot determine whether an audit
will pass or fail and does not provide legal or regulatory advice.

## What is proven

The approved one-pager promises:

1. Transaction-reporting and best-execution surveillance.
2. Missing or outdated algorithm-documentation review.
3. Correction and submission preparation.
4. Trader-certification readiness and enrollment planning.

Those promises are mapped in `evals/onepager-map.json`.

The Python agent was loaded by itself into Brainstem and all five locked
persona-language cases passed. The exact responses are stored in
`evals/transcripts.json`.

The Easy and manual Copilot Studio builds are complete in Draft. The evidence
contract is stored in `evals/manual-build-evidence.json` and
`screenshots/manual/browserfilm.json`.

- Easy agent: `Regulatory Compliance Pilot`,
  `aibast_RegulatoryCompliancePilot`, bot
  `1a5fb3de-2e07-4415-89f9-40c5620c0cc5`.
- Easy inventory: Sonnet46, five skills, two knowledge files, eight changes
  pushed, 5/5 Preview cases passed, Draft.
- Manual agent: `Regulatory Manual Build`, bot
  `ad9993c3-ea7a-4ecf-a86b-40a9d39a4fa3`.
- Manual inventory: Sonnet46, five skills, two knowledge files, no web search,
  5/5 Preview cases passed, 26 screenshots, Draft.

## Customer session: Easy mode

**Audience:** nontechnical customer participants and account teams.

**Customer requirement:** GitHub Copilot Agent mode in VS Code and a browser for
the supported GitHub/Copilot authentication step.

### Facilitation sequence

1. Open `deployment.json`.
2. Give the customer control of the keyboard.
3. Ask GitHub Copilot Agent mode to own the recipe end to end.
4. Intervene only if a browser asks the customer to approve authentication.
5. Do not continue until Copilot reports:
   - Brainstem health is `ok`;
   - the downloaded source matches the registry SHA-256;
   - `FSRegulatoryCompliance` is loaded; and
   - the smoke prompt fired that exact agent.
6. Replay all five locked prompts and compare the live answers with
   `evals/transcripts.json`.
7. Inspect the validated Copilot Studio Draft and its five-case evidence.
8. Stop before connecting customer systems or publishing anything.

### Conversation starters

- “Are we going to fail our next MiFID audit? What's actually broken on the
  desk right now?”
- “Which of my traders can't legally trade today, and who do I have to call?”
- “We executed a few hundred trades this week. Which ones will the regulator
  reject, and why exactly?”
- “Is anything about to go live that shouldn't?”
- “My head of trading says the reporting is fine. Prove him wrong with
  specifics I can take to the board.”

### What to say while it runs

- “The exact records and figures are synthetic evidence, not customer claims.”
- “Audit readiness is reported as control gaps and at-risk areas, not a
  predicted audit outcome.”
- “Remediation prepares payloads for authorized review; it does not transmit a
  filing.”
- “Production connectors and approval policy remain customer decisions.”

## Customer session: true manual Hard mode

Open `manual-tutorial.html`. The walkthrough is intentionally literal and uses
one expected screenshot per browser action:

1. Create a blank Copilot Studio agent.
2. Name the manual build.
3. Enter and save the reviewed global instructions.
4. Remove default web search.
5. Upload the two synthetic Markdown knowledge files.
6. Upload five `SKILL.md` files individually.
7. Select Claude Sonnet 4.6.
8. Review the complete inventory.
9. Run all five locked cases in Preview.
10. Stop at the explicit no-publish gate.

All 26 screenshots exist under `screenshots/manual/` and are rendered as
`screenshots/manual/manual-build-walkthrough.gif`.

## Production replacement seams

For production:

- replace synthetic trade records with approved order-management and
  transaction-reporting data;
- replace static reference data with governed instrument and venue sources;
- connect remediation to an Approved Reporting Mechanism only behind an
  authenticated approval workflow;
- replace synthetic certification records with the approved learning system;
- use Microsoft Teams for role-based review and escalation where appropriate.

The agent must never claim a side effect occurred unless the production tool
returns evidence that it succeeded.

## Failure recovery

| Symptom | Response |
| --- | --- |
| Brainstem health is unavailable | Have Copilot rerun the official installer and launcher from the deployment recipe. |
| Downloaded hash differs | Stop. Refresh `registry.json`; do not install an unverified source file. |
| The wrong agent answers | Restore strict isolation and fix routing metadata rather than retrying blindly. |
| A knowledge file remains processing | Wait for indexing to finish before Preview. |
| A skill upload fails | Download the raw file again and upload the file literally named `SKILL.md`. |
| Web answers appear | Confirm the default web-search capability was removed. |
| Preview predicts an audit outcome | Recheck global instructions and the compliance-dashboard skill boundary. |
| Remediation claims a filing was sent | Treat the build as failed; the pilot may only prepare payloads for authorized review. |

## Evidence that must leave the session

- source-agent and one-pager SHA-256 values;
- isolated Brainstem transcripts;
- environment and manual-agent identity;
- model selection;
- two knowledge-source confirmations;
- five skill confirmations;
- all five Preview responses;
- 26 browser screenshots and browserfilm manifest;
- explicit Draft/no-publish confirmation;
- unresolved connector or governance work.

The Copilot Studio path is validated for this synthetic Draft pilot; production
connectors, security review, legal review, and publication remain separate.
