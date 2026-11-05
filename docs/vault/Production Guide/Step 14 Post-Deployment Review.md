---
title: Step 14 Post-Deployment Review
section: Production Guide
status: published
hook: How the pilot is measured against the MVP targets and how Phase 2 is planned.
source: docs/rapp-guide.html#step14; docs/rapp-guide.html#scaling; protocols/rapp-deploy/1/SPEC.md §4-5
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 14 Post-Deployment Review

**Post-Deployment Review** closes the loop.
After 2-4 weeks of pilot use, you compare real results against the MVP targets.
You validate **ROI** and plan **Phase 2**.

Guide section: [Step 14 in the production guide](../rapp-guide.html#step14)

## What this step is

- **Goal:** measure success, gather lessons, plan the next phase.
- **Time:** 1-2 hours (a review meeting with the customer).
- **When:** 2-4 weeks after pilot launch in [[Step 13 Production Deployment]].

## Inputs

- Pilot monitoring data and weekly survey results from Step 13.
- The target metrics agreed in the MVP ([[Step 04 Customer Validation]]).
- The projected savings shown in the demo ([[Step 09 Generate Video Demo]]).

## Quantitative review

| Metric | Target (from MVP) |
|---|---|
| Time saved per user per day | 45 minutes |
| Agent accuracy | 95% |
| User adoption rate | 80% |
| Agent calls per day | 20+ per user |

Each row is filled with the measured value and marked met, partial, or missed.

## Qualitative review

- **User satisfaction (NPS)** from pilot surveys.
- **Top feature requests** for Phase 2.
- **Pain points:** what is not working.
- **Unexpected use cases.**

## Lessons learned

- **What worked:** most-used agents, training that landed, smooth integrations.
- **What needs work:** accuracy issues, where users got stuck, unreliable data connections.

## Phase 2 options

- **Wider rollout,** for example from 10 pilot users to 50+.
- **New agents** from user requests.
- **More integrations.**
- **Advanced features:** multi-agent workflows, proactive alerts, scheduled tasks.

## Worked example from the guide

A field sales pilot after 4 weeks:

- 10 pilot users × 42 min saved per day (target was 45).
- 4 weeks × 5 days = 20 days.
- Total: 140 hours saved across 10 users.
- Extrapolated to 200 users: 35,000 hours per year (close to the 37,500 target).
- **Decision:** proceed with Phase 2 to all 200 reps.

## Outputs

- **Success metrics report.**
- **User feedback summary:** NPS, quotes, requests.
- **ROI validation:** actual vs. projected savings.
- **Phase 2 proposal:** a 3-6 month roadmap.
- **Case study** (optional) for similar projects.

## The whole framework

The guide's summary: production deployment takes 3-5 weeks, mostly waiting for approvals.
Steps 11-14 run async and do not block the delivery team, which is how a small team runs many projects at once.
Phase 2 requests that need new capability start a new cycle at [[Step 01 Discovery Call]].

## How rapp/1 underpins this step

- **Expanding the rollout** maps onto later waves in [[RAPP Deploy]]. Traffic only increases, previously exposed cells are never removed, and the last wave is `global` at 10,000 basis points.
- **Each advance needs fresh evidence.** A decision cannot advance until every selected cell meets its observation duration and healthy windows.
- **New agents are new releases.** Any behavior-affecting change creates a new [[RAPP CICD]] release, so Phase 2 work goes back through qualification and promotion.

## Related

- [[Step 13 Production Deployment]]
- [[Step 01 Discovery Call]]
- [[RAPP Deploy]]
- [[RAPP CICD]]
- [[Production Guide Overview]]
