---
title: Step 13 Production Deployment
section: Production Guide
status: published
hook: How the approved system is deployed to the customer's environment and rolled out to pilot users.
source: docs/rapp-guide.html#step13; protocols/rapp-deploy/1/SPEC.md §1-5
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 13 Production Deployment

**Production Deployment** moves the system from prototype to production.
It runs in the customer's Azure subscription with every security and compliance control.
Then a **phased rollout** begins with pilot users.

Guide section: [Step 13 in the production guide](../rapp-guide.html#step13)

## What this step is

- **Goal:** deploy the approved system and start the pilot.
- **Time:** 2-3 days of deployment, then a 2-4 week pilot.
- **Owner:** Technical Team.

## Inputs

- **Production deployment authorization** from [[Step 12 Security Sign-off]].
- The rollout and support plans from [[Step 11 Production Planning]].
- The reviewed agents from [[Step 06 Code Quality Review]].

## Deployment steps

**1. Infrastructure**

1. Run the production ARM template (with the Step 11 security additions).
2. Configure Azure AD authentication.
3. Set up Private Link endpoints.
4. Configure Application Gateway and WAF.
5. Enable Azure Monitor alerts.
6. Configure backup and disaster recovery.

**2. Agents**

1. Copy reviewed agents from prototype to production File Storage.
2. Verify agents load in the production Function App.
3. Test one agent call with production data.
4. Configure production data source connections.
5. Validate memory persistence in production Azure Storage.

**3. M365 integration**

1. Import the Copilot Studio solution to production.
2. Configure the production Azure Function URL.
3. Enable the Teams channel for the pilot group.
4. Test end to end: Teams → Copilot → Function → Agents → data sources.
5. Verify SSO works.

**4. Pilot onboarding**

- Send a welcome email with access instructions.
- Run a 30-minute training session.
- Provide a Teams support channel.
- Set expectations: this is Phase 1, and feedback shapes improvements.

## Monitoring during the pilot (weeks 1-2)

- **Daily check-ins** on Application Insights errors.
- **Weekly survey** to pilot users (NPS, issues, feature requests).
- **Performance metrics:** response time, success rate, usage frequency.
- **Hot fixes:** critical bugs within 24 hours.

## Outputs

- **Production system** with all security controls.
- **Pilot users active:** 5-10 people using agents daily.
- **Monitoring dashboard** for usage and performance.
- **Support process** with a defined escalation path.

## How rapp/1 underpins this step

[[RAPP Deploy]] (`rapp-deploy/1`) describes this step in protocol terms.

- **No in-place changes.** `candidate_isolated` must be true and `in_place_mutation` must be false. Any behavior-affecting change creates a new release. A pilot hot fix is therefore a new release, not an edit to the running one.
- **Serving and candidate lineages.** The release receiving traffic and the release under exposure are kept separate.
- **Cells.** Every deployment uses `topology.mode: "cellular"`: independently observable, isolatable failure domains.
- **Health is evidence.** A `rapp-deploy/1-health` record is one candidate-bound observation window in one cell. It cannot label itself healthy when a budget failed.
- **Decisions.** A `rapp-deploy/1-decision` is advance, complete, hold, rollback, or quarantine.
- **User work is kept.** Acknowledged user work must not be discarded by rollback.

The kernel under the agents stays pinned. See [[The Brainstem Kernel]] and [[Distros and Pinning]].

## Related

- [[Step 12 Security Sign-off]]
- [[Step 14 Post-Deployment Review]]
- [[RAPP Deploy]]
- [[RAPP CICD]]
- [[The Brainstem Kernel]]
- [[Failure Atlas]]
