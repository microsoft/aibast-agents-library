---
title: Step 11 Production Planning
section: Production Guide
status: published
hook: How the prototype's requirements for security, compliance, and rollout are defined before production.
source: docs/rapp-guide.html#step11; protocols/rapp-cicd/1/SPEC.md §1-3; protocols/rapp-deploy/1/SPEC.md §1-4
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 11 Production Planning

**Production Planning** turns a working prototype into a plan for a production system.
You work with the customer's IT, Security, and Compliance teams.
The result is a **requirements document** and a **phased rollout plan**.

Guide section: [Step 11 in the production guide](../rapp-guide.html#step11)

## What this step is

- **Goal:** define production deployment requirements with the customer.
- **Time:** 3-7 days of meetings and documentation.
- **Owner:** Technical Team. In the guide's team setup (Station 4, Steps 11-14) the owner is the customer IT team, with Team Member C for support escalation.

## Inputs

- The locked, approved demo from [[Step 10 Final Demo Review]].
- The prototype and its reviewed agents from [[Step 07 Deploy Prototype]].

## Questions for IT and Security

- **Data residency:** where may data be stored (US, EU, on-prem)?
- **Authentication:** SSO required? Azure AD integration?
- **Network access:** public internet, or private endpoints?
- **Audit logging:** which events must be logged?
- **Encryption:** at rest and in transit.
- **Compliance frameworks:** HIPAA, SOC 2, GDPR, FedRAMP?

## Prototype vs. production

- **Prototype:** one Azure Function App, public endpoints, dev subscription.
- **Production:** redundant deployments, private endpoints, the customer's subscription.

Common security additions:

- Azure AD authentication (no anonymous access)
- Private Link for the Function App
- Azure Key Vault for secrets, not environment variables
- Application Gateway with WAF
- DDoS protection
- Managed Identity for service-to-service auth
- Azure Monitor alerts for security events

## Rollout strategy

| Phase | Users | Duration | Success criteria |
|---|---|---|---|
| 1: Pilot | 5-10 power users | 2 weeks | 80% adoption, no critical bugs |
| 2: Early Adopters | 25-50 users | 4 weeks | Positive NPS, feature requests captured |
| 3: General Availability | All users | 8 weeks | ROI metrics achieved, support tickets low |

## Outputs

- **Production requirements doc:** security, compliance, infrastructure.
- **Rollout plan:** phased schedule with success metrics.
- **Support plan:** who handles questions and bugs.
- **Training materials:** guides, video tutorials, FAQ.

These go to [[Step 12 Security Sign-off]].

## How rapp/1 underpins this step

The upstream RAPP/1 specification has two operational profiles that match this planning work. See [[RAPP CICD]] and [[RAPP Deploy]].

- **Release identity.** In `rapp-cicd/1`, a `rapp-cicd/1-release` payload names the complete candidate before qualification: source commit and tree, the exact artifact, and the pinned Grail kernel. Its identity is its particle hash ([[Content Addressing]]).
- **Promotion policy.** A `rapp-cicd/1-policy` payload declares the ordered promotion path and required evidence. Planning which reviews must pass maps onto this.
- **Rollout plan.** In `rapp-deploy/1`, a `rapp-deploy/1-plan` covers topology, waves, health budgets, state, data, and recovery.
- **Phased waves.** Waves begin with `shadow` at zero traffic, only increase, and end with `global` at 10,000 basis points. The guide's Pilot, Early Adopters, and GA phases are the business view of the same idea.
- **Rollback target.** An authorized plan binds a resolvable, previously authorized rollback release.

Neither profile prescribes a cloud provider, so the Azure controls above are the customer's choice, not protocol requirements.

## Related

- [[Step 10 Final Demo Review]]
- [[Step 12 Security Sign-off]]
- [[RAPP CICD]]
- [[RAPP Deploy]]
- [[Distros and Pinning]]
- [[Security Considerations]]
