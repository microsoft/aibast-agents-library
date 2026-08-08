# Time Entry and Billing solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/time_entry_billing_stack/time_entry_billing_agent.py` |
| Deployment recipe | `solutions/time-entry-billing/deployment.json` |
| Live behavior gate | `tests/demo_cases/time-entry-billing.json` |
| PowerPoint evidence map | `solutions/time-entry-billing/evals/onepager-map.json` |
| Manual knowledge | `solutions/time-entry-billing/manual/knowledge/` |
| Manual skills | `solutions/time-entry-billing/manual/skills/` |

## Implemented scope

The package covers unbilled-work triage, billing rollups, time-entry audit,
approval-gated invoice preparation, and disputed-hour evidence briefs.
Fictional records make every response repeatable. Fixed-fee time is retained as
delivery evidence and is never converted into an invoice amount without a
milestone schedule.

The agent never changes time, grants approval, recognizes revenue, posts to an
accounting system, contacts clients, or sends invoices.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/time-entry-billing/FIELD-GUIDE.md` |
| Easy-mode GitHub Copilot Chat prompts | `solutions/time-entry-billing/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/time-entry-billing/quest.html` |
| Literal browser tutorial | `solutions/time-entry-billing/manual-tutorial.html` |
| Raw export manifest | `solutions/time-entry-billing/export-manifest.json` |
| Source bundle | `solutions/time-entry-billing/exports/time-entry-billing-source.zip` |
| Manual evidence | `solutions/time-entry-billing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/time-entry-billing/screenshots/manual/browserfilm.json` |

**Scaffold status:** 65 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
