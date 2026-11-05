---
title: Production Guide Overview
section: Production Guide
status: published
hook: What the 14-step RAPP production process is, who runs each step, and where the six human quality gates sit.
source: "docs/rapp-guide.html#overview; docs/rapp-guide.html#architecture; docs/rapp-guide.html#principles; SPEC.md §1.1, §8, §11.1, §11.2"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Production Guide Overview

The **Rapid Agent Prototype Pattern (RAPP)** turns a customer conversation into a working AI agent in days, not months.
AI does the heavy lifting. People apply judgment at **six quality gates**.
This note maps the 14 steps and shows where the rapp/1 protocol supports them.

## The idea in one line

- **Automation does the volume work:** extracting project data, drafting summaries, generating agent code.
- **Humans keep the judgment:** is this the right problem, is the code safe, is it ready to show?

Each gate takes 15-60 minutes of human time. It prevents days or weeks of wasted work.

## The 14 steps

| Step | Type | Duration | Owner |
|---|---|---|---|
| [[Step 01 Discovery Call\|1. Discovery Call]] | Manual | 30-60 minutes | Field Team |
| [[Step 02 Transcript Analysis\|2. Transcript Analysis]] | Audit (Gate 1) | 15 minutes | Delivery Team |
| [[Step 03 Generate MVP Poke\|3. Generate MVP Poke]] | Manual | 1-2 hours (manual) | Delivery Team |
| [[Step 04 Customer Validation\|4. Customer Validation]] | Audit (Gate 2) | 1-2 days | Field Team |
| [[Step 05 Generate Agent Code\|5. Generate Agent Code]] | Manual | Days-Weeks | Technical Team |
| [[Step 06 Code Quality Review\|6. Code Quality Review]] | Audit (Gate 3) | 30-60 minutes | Technical Team |
| [[Step 07 Deploy Prototype\|7. Deploy Prototype]] | Manual | 1-2 hours | Technical Team |
| [[Step 08 Demo Review\|8. Demo Review]] | Audit (Gate 4) | 30 min | Delivery Lead |
| [[Step 09 Generate Video Demo\|9. Generate Video Demo]] | Manual | 3-4 hours (manual) | Delivery Team |
| [[Step 10 Final Demo Review\|10. Final Demo Review]] | Audit (Gate 5) | 30-60 minutes (review call with customer) | Delivery Lead |
| [[Step 11 Production Planning\|11. Production Planning]] | Manual | 3-7 days (meetings + documentation) | Technical Team |
| [[Step 12 Security Sign-off\|12. Security and Compliance Sign-off]] | Audit (Gate 6) | 1-3 weeks (review process, pen testing, compliance audit) | Customer IT and Security |
| [[Step 13 Production Deployment\|13. Production Deployment]] | Manual | 1 day | Technical Team |
| [[Step 14 Post-Deployment Review\|14. Post-Deployment Review]] | Audit | Ongoing | Success Team |

Durations and owners follow the guide's overview table. Some step sections in the guide give different times; each step note carries its section's figures.

## The six quality gates

1. **Transcript Audit** — did we extract the right problem?
2. **Customer MVP Validation** — does the customer agree this is the MVP?
3. **Code Quality Review** — are the generated agents secure and correct?
4. **Demo Review** — is this ready to show the customer?
5. **Final Demo Review** — is this feedback in scope, or scope creep?
6. **Security and Compliance Sign-off** — will IT, Security and Compliance let this go live?

## Why the order matters: risk elimination

The biggest risk is spending six months on a problem nobody cares about.
RAPP puts customer checkpoints first:

- The **MVP poke** (Step 3) gets feedback before real work begins.
- By Step 6, code exists with **locked scope** and customer sign-off.
- The working demo (Step 8) is the second major checkpoint.

If the customer says no, you have spent days, not months.

## The four architecture layers

| Layer | Responsibility | Technology |
|---|---|---|
| Interface | User channels | M365 Copilot, Teams, Web, Mobile, Voice |
| Orchestration | Conversation, routing, history | Copilot Studio + Power Automate |
| Intelligence | Agent execution, tool calling | RAPP Brainstem locally, or the Azure Function App |
| Storage | Agent code, memory, workflows | Azure File Storage |

Agents **hot-load**. Locally the Brainstem re-reads its agents folder on every request. In Azure, agents in the file share's `agents/` directory refresh on a five-minute cache.

## How rapp/1 underpins the process

The guide describes the delivery process. The upstream RAPP/1 specification defines the bytes the delivered agents speak.

- **One wire.** Every interaction rides `POST /chat` or a signed append-only frame. New capability is a new agent behind `/chat`, never a sibling REST route. See [[The Wire]].
- **Five layers.** Address, identity, wire, frame and egg each name one canonical form. A higher layer must not redefine a lower one. See [[Protocol Layers]].
- **Unchanged kernel.** New behavior lives outside the pinned Grail kernel. See [[The Brainstem Kernel]] and [[Distros and Pinning]].
- **Production operations.** The upstream specification defines two operational profiles: `rapp-cicd/1` (immutable release capsules, qualification evidence, promotion, rollback) and `rapp-deploy/1` (isolated lineages, progressive exposure, quarantine, exact rollback). See [[RAPP CICD]] and [[RAPP Deploy]].

Guide section: [Framework Overview in the production guide](../rapp-guide.html#overview)

## Related

- [[Reading Paths]]
- [[Step 01 Discovery Call]]
- [[The Agent Contract]]
- [[Protocol at a Glance]]
- [[The Brainstem Kernel]]
- [[Sources and Provenance]]
