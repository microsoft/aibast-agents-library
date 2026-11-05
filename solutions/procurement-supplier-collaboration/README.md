# Procurement and Supplier Collaboration Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/energy_stacks/procurement_supplier_collaboration_stack/procurement_supplier_collaboration_agent.py` |
| Deployment recipe | `solutions/procurement-supplier-collaboration/deployment.json` |
| Approved-slide map | `solutions/procurement-supplier-collaboration/evals/onepager-map.json` |
| Source audit | `solutions/procurement-supplier-collaboration/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/procurement-supplier-collaboration/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/procurement-supplier-collaboration.json` |
| Synthetic knowledge | `solutions/procurement-supplier-collaboration/manual/knowledge/` |
| Uploadable skills | `solutions/procurement-supplier-collaboration/manual/skills/` |

## Scope

Help an electricity distribution company run source-to-pay for its network materials with suppliers in one portal:
- turn demand from the maintenance plan, capital projects and stock replenishment into requisitions;
- recommend the procurement route (framework direct award, mini-competition or open tender) and the eligible supplier shortlist;
- draft answers to supplier questions from the published request for quotation (RFQ) pack;
- score bids on price, lead time, quality and sustainability;
- flag unacknowledged orders and advance shipping notices that miss the committed date;
- run the three-way match of purchase order, goods receipt and invoice.

Hero scenario: A distribution company's category managers, buyers, expediters and accounts payable team. Power Automate brings ERP requisitions, orders, receipts and invoices into Dataverse. Suppliers work in a Power Apps supplier portal. Copilot Studio recommends, scores and drafts.

Implemented operations: `sourcing_plan`, `supplier_query`, `bid_evaluation`, `delivery_tracking`, `invoice_match`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

How it differs from the other procurement templates:
- The Purchase Order Management and Procurement Savings agents cover software and vendor-contract buying.
- The Supplier Claim Engagement Agent recovers retail supplier claims.
- This template covers competitive sourcing and delivery of network materials, through to invoice match.

## Approval boundary

This package is synthetic and read-only. It does not connect to procurement systems, the supplier portal or the finance module, and it executes no external actions. The utility, requisitions, suppliers, bids, orders, invoices and amounts are fictional evidence rather than customer outcomes. Bid scores are decision support.

Production connections require least-privilege access, authenticated supplier portal users and bidder data separation. They also require a human approval step:
- the category manager confirms every route and shortlist;
- the buyer approves every supplier reply and clarification;
- the award panel decides every award;
- accounts payable approves every payment.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 5 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/procurement-supplier-collaboration/field-guide.html` |
| Evidence report | `solutions/procurement-supplier-collaboration/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/procurement-supplier-collaboration/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/procurement-supplier-collaboration/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/procurement-supplier-collaboration/quest.html` |
| Literal browser tutorial | `solutions/procurement-supplier-collaboration/manual-tutorial.html` |
| Raw export manifest | `solutions/procurement-supplier-collaboration/export-manifest.json` |
| Source bundle | [`procurement-supplier-collaboration-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/procurement-supplier-collaboration-source.zip) (release asset) |
| Manual evidence | `solutions/procurement-supplier-collaboration/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/procurement-supplier-collaboration/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/procurement-supplier-collaboration/exports/procurement-supplier-collaboration-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/procurement-supplier-collaboration/exports/procurement-supplier-collaboration-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/procurement-supplier-collaboration/exports/procurement-supplier-collaboration-solution-export.json` |

**Scaffold status:** 106 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
