# Partner Solutions — Working Decision Log

Status: **RESOLVED / LIVE.** All open decisions below have been made and
implemented. See "RESOLUTION" section for the final state.

## Origin ask

Add agents from a Microsoft partner's public agent library to AIBAST's own
library as a "Partner solutions" showcase, so visitors can see the variety
of Copilot/Dynamics 365 patterns partners ship — distinct from AIBAST's own
first-party and demo-proven agents. Explicit instruction: even where a
partner's agent resembles something AIBAST has, we want **variety**, not
1:1 duplication dressed up differently.

First partner: **CongruentX** — https://congruentx.com/ai-agents-library/
(publicly lists 40+ Copilot-based agents across four categories: **Core**,
**Insurance**, **Distribution**, **Professional Services**).

## What has been built so far

- `partners.json` (repo root) — schema `aibast-partners/1.0`. Contains a
  `partners` registry (id/name/url/description, extensible to more partners
  later) and an `agents` array. Each partner agent entry:
  `id, partner_id, name, category, product, description, source_url`, plus
  optional `aibast_equivalent`, `partner_reported_outcome`, `what_it_does`,
  `problem_it_solves`, `who_it_helps`.
- `build_registry.py` — `load_partners()` validates the file and adds
  `partners` / `partner_agents` to `registry.json`, fully separate from
  `agents` (repo-owned code count stays honest). Also validates that any
  `aibast_equivalent` resolves to a real registry agent name.
- `library.html` — new **"Partner solutions"** tab: filters, cards, and a
  detail modal. Cards/modal show partner attribution, source link,
  paraphrased description, and (where present) a "Partner-reported outcome"
  badge and a "Compare to / Build it yourself with AIBAST" section that
  opens the mapped AIBAST agent via the existing `openAgent()`.
- `tests/test_partners.py` — contract tests: schema, required fields,
  no verbatim marketing headlines, `aibast_equivalent` resolves and is
  unique per agent, `partner_reported_outcome` values locked to source
  wording, library.html exposes the required tokens/functions.
- Deployed twice to `kody-w/aibast-agents-library:staging` (see workflow
  note below). Live at:
  https://kody-w.github.io/aibast-agents-library/library.html → "Partner solutions"

## Standing workflow rule (user-mandated)

> Before pushing any update to kody-w's staging branch, always sync it with
> `microsoft/aibast-agents-library` (upstream/main) first.

Process used: fetch `upstream/main` + `origin/staging`, create an isolated
git worktree tracking `origin/staging`, merge `upstream/main` in, then layer
the feature commit on top, run the full test suite, push as a fast-forward
to `origin staging`. (Also stored as a repository memory.)

## Mistake made twice — watch for this

Copying `library.html` / test files **wholesale** from the working checkout
into the synced worktree silently clobbered upstream-only additions that
exist on `staging` but not in the local working branch (specifically the
**Academy** nav link — `academy.html`, added on staging independently).
Fix: diff/patch or manually reapply only the specific edited functions
against the *current* synced base, then verify (`grep -c "academy.html"
library.html` should stay 2) before committing/pushing. Do this again on
every future sync.

## Academy is fork-only — not upstream

Confirmed via `git ls-tree -r upstream/main --name-only | grep -i academy`
→ no results. Academy (`academy.html`, `academy.json`, `academy/catalog.json`,
`Deploy Academy Pages` workflow, `tests/test_academy.py`, etc.) exists only
on `kody-w`'s fork/staging branch, not in `microsoft/aibast-agents-library`.
It is unrelated to the Partner Solutions work — it must simply not be
deleted as a side effect of unrelated edits (see mistake above), but it is
out of scope and won't be part of what eventually promotes upstream.

## Partner review loop

Before this promotes from `kody-w:staging` to `microsoft/aibast-agents-library`
main, CongruentX (contacts: **Chuck and Marty**) need to review and sign off
on: which agents are featured, accuracy of our paraphrased descriptions, and
attribution. A review-request email (HTML, with a copy-to-clipboard button)
was drafted for this — see chat history / session files for
`congruentx-review-email.html`.

## RESOLUTION — selection strategy pivot (2026-09-06)

User pushback (correct call): picking CongruentX agents that **overlap**
with something AIBAST already has just creates "us vs. them" redundancy —
and no partner wants to be featured as a target for a competitive pitch.
With ~40 CongruentX agents available, we should prefer ones that **don't
overlap** with our own catalog, to show genuine breadth/variety instead of
duplicating our own lineup under a different label. Related feedback:

- Remove all competitive/comparison framing entirely (no "compare
  approaches", no "buy vs. build", no "see AIBAST's agent" links). Partners
  should never feel pitted against AIBAST's own catalog.
- Provide real explanatory value on the intro copy and per-card, not just
  "click through to the partner's site" — explain what these are and why
  they're worth knowing, in plain language.

**Decisions made (both confirmed by user):**
1. Selection strategy: **replaced all 12** with zero-AIBAST-overlap agents
   — pure gap-filling variety, cross-checked against every existing AIBAST
   agent name in the current catalog (`b2b_sales`, `financial_services`,
   `retail_cpg`, `professional_services`) to confirm no direct duplicate.
2. Buy-vs-build feature: **removed entirely.** No `aibast_equivalent`
   field, no `aibastEquivalentOf()`, no "Build it yourself with AIBAST" /
   "See AIBAST's agent" UI anywhere in `library.html`.

**Final 12 (all confirmed non-overlapping with AIBAST's catalog):**

| Agent | Category | Partner-reported outcome |
|---|---|---|
| Buyer Intent Enrichment (web + CRM) | b2b_sales | 20–50% higher campaign ROI vs broad programs |
| Hyper-Targeted Market Segmentation | b2b_sales | +5–15% marketing ROI, reduced spend on low-impact segments |
| Dynamic Journey Orchestration (CI Journeys Copilot) | b2b_sales | 10–15% lift in journey revenue |
| Event/Webinar Persona Journeys | b2b_sales | +10–20% higher MQL→SQL conversion on event leads |
| First-Impact: Claims Setup & Portal | financial_services | +5–10 NPS points post-claim, better retention |
| ICP Targeting by Line (P&C/Life) | financial_services | 10–15% higher win rate |
| Risk & Loss Ratio Storytelling | financial_services | (none stated on source) |
| Loyalty Tier Triggers → Offers | retail_cpg | (none stated on source) |
| Dormant Account Reactivation (Leads) | retail_cpg | 10–20% of dormant accounts reactivated |
| Service Contracts & Attach Rate Signals | retail_cpg | 10–30% higher attach rate |
| Target Accounts by Buying Committee | professional_services | Higher win rate, larger average deal size (5–15%) |
| Thought Leadership Orchestration | professional_services | Strong influence on pipeline; higher engagement, 5–10% more opps sourced |

Each entry now carries `what_it_does`, `problem_it_solves`, and
`who_it_helps` (paraphrased arrays, rendered as real bullet lists in the
card and detail modal) instead of a single one-line summary, so the
listing explains the agent on its own merits rather than relying on a
link-out.

Intro copy for the Partner solutions tab now reads: *"Ideas from across the
Microsoft partner ecosystem"* / *"Microsoft partners are building and
shipping their own Copilot Studio and Dynamics 365 agents in production.
This is a curated set of those agents, each explained in plain terms —
what it does, the problem it solves, and who it's for — as a source of
ideas and patterns for your own AI roadmap. Every card links to the
partner's own listing for the full picture."*

### Candidates considered but excluded (overlap with AIBAST catalog)

For future reference if re-curating: Deal Health (→ `deal-health-score`),
Field Seller AI Agent Copilot (→ `next-best-action`), Sunday Stress Buster
(→ `pipeline-velocity`), Generate POV Agent (→ `proposal-generation`),
Meeting Prep (→ `meeting-prep`), Sales Process Optimization Agent (→
`stalled-deal-detection`), Policy Issuance Checklist Agent (→
`fs-customer-onboarding`), RFP/Submission Triage & Quote Copilot (→
`underwriting-support`), Territory Route & Visit Copilot (→
`store-associate-copilot`), Churn Risk: Price/Stock/Service Deltas (→
`client-health-score`), Account Research Copilot (→ `account-intelligence`),
Stakeholder Map + Success Plan (→ `deal-stakeholder-engagement`), Intelligent
CLM & Redline Review (→ `contract-risk-review`), Proactive Churn Prevention
(→ `client-health-score`).

Full raw scrape of the CongruentX page (all ~40 accordion entries with
"What does it do / Problem it Solves / Who it helps / Typical Outcomes")
is in this session's conversation history and was used to source both the
current 12 and this candidate list. If a future session needs the raw
content again, re-fetch https://congruentx.com/ai-agents-library/ with
`raw: true` and paginate via `start_index` (page is large, ~160KB+).

## Files touched by this feature (for a future session's orientation)

- `partners.json` (new; agents rewritten once for the no-overlap pivot)
- `build_registry.py` (added `load_partners()`, `PARTNERS_*` constants;
  the `aibast_equivalent` cross-check was added then removed when that
  feature was reversed)
- `library.html` (new "Partner solutions" tab: state, filters,
  `partnerAgentCard`, `openPartnerAgent`, `partnerName`,
  `filteredPartnerAgents`. No `aibastEquivalentOf` — removed.)
- `tests/test_partners.py` (new)
- `tests/test_library_agent_upvotes.py` (updated tab-count assertion for the
  3rd tab)
- `docs/partner-solutions-notes.md` (this file)

## Separate, NOT-YET-DONE follow-up request (do not conflate with the above)

User also asked that the **Academy** page (`academy.html`, fork-only, not in
`microsoft/aibast-agents-library` — see "Academy is fork-only" above) be
re-themed to visually match the rest of the site (light, card-based
Library theme) instead of its current dark/purple theme. This is a
distinct, unstarted task — has not been scoped or touched yet.
