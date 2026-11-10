# Invoice Processing solution package

Built on the Copilot Studio Gallery solution `invoice-processing` (MIT). Their package stays theirs and unchanged; this is the AIBAST layered version with synthetic data.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/invoice_processing_stack/invoice_ledger_agent.py` |
| Deployment recipe | `solutions/invoice-processing/deployment.json` |
| Strict isolated transcripts | `solutions/invoice-processing/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/invoice-processing.json` |
| Synthetic knowledge | `solutions/invoice-processing/manual/knowledge/` |
| Uploadable skills | `solutions/invoice-processing/manual/skills/` |

## Scope

Help an accounts payable team decide what to log from this week's invoice attachments: which invoices are complete, which were only partly read, which duplicate a row already in the ledger, and which attachments are not invoices at all.

Hero scenario: a small accounts payable team with four email attachments from Northwind Traders, Contoso Services and Fabrikam Supplies, plus a cover letter.

Implemented operation: `ledger_decisions`. The package contains two locked persona-language cases and one uploadable skill.

## Approval boundary

This package is synthetic and read-only. It does not read a mailbox, write to a ledger, pay, approve or email anyone. Every invoice, vendor and ledger row is fictional evidence rather than a customer outcome.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the `SKILL.md` file in `manual/skills/`. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/invoice-processing/field-guide.html` |
| Evidence report | `solutions/invoice-processing/evidence-report.html` |
| AIBAST Easy Mode skill | `skills/aibast-easy-mode/SKILL.md` |
| Easy Mode guide | `solutions/invoice-processing/EASY-MODE.md` |
| Guided Easy/Manual quest | `solutions/invoice-processing/quest.html` |
| Literal browser tutorial | `solutions/invoice-processing/manual-tutorial.html` |
| Raw export manifest | `solutions/invoice-processing/export-manifest.json` |
| Source bundle | [`invoice-processing-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/invoice-processing-source.zip) (release asset) |
| Manual evidence | `solutions/invoice-processing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/invoice-processing/screenshots/manual/browserfilm.json` |

**Scaffold status:** 71 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
