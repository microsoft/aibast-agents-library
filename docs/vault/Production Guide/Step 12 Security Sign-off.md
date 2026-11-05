---
title: Step 12 Security Sign-off
section: Production Guide
status: published
hook: How IT, Security, and Compliance formally approve production deployment at Quality Gate 6.
source: docs/rapp-guide.html#step12; protocols/rapp-cicd/1/SPEC.md §1-5; SPEC.md §14
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 12 Security Sign-off

**Security Sign-off** is **Quality Gate #6**, the last human gate before production.
The customer's IT, Security, and Compliance teams formally approve that the system meets every production requirement.
Nothing goes live without **written approval**.

Guide section: [Step 12 in the production guide](../rapp-guide.html#step12)

## What this step is

- **Goal:** formal production approval from the customer's IT, Security, and Compliance teams.
- **Time:** 1-3 weeks (review process, pen testing, compliance audit).
- **Note:** the guide says production is "mostly waiting for security and compliance approvals." It runs async and does not consume delivery team time.

## Inputs

- The production requirements doc, rollout plan, and support plan from [[Step 11 Production Planning]].
- The reviewed agent code from [[Step 06 Code Quality Review]].

## Security review checklist

- **Penetration testing:** third-party audit completed.
- **Vulnerability scan:** no critical or high-severity issues.
- **Code review:** security team reviewed the agent code.
- **Access controls:** RBAC configured, least privilege enforced.
- **Secrets management:** all credentials in Azure Key Vault.
- **Logging and monitoring:** security events captured and alerted.

## Compliance review checklist

- **Data classification:** PII/PHI handling documented.
- **Data retention:** policies set for user memory and logs.
- **Audit trail:** every agent action logged with user context.
- **Frameworks:** SOC 2, HIPAA, GDPR requirements met.
- **Third parties:** vendor BAAs signed where needed.

## The gate: three outcomes

- **APPROVED.** Proceed to [[Step 13 Production Deployment]].
- **CONDITIONAL APPROVAL.** Fix the minor issues and re-submit.
- **BLOCKED.** Major issues. Back to [[Step 11 Production Planning]] for redesign.

## Outputs

- **Security sign-off:** written approval from the CISO or Security team.
- **Compliance sign-off:** approval from Compliance or Legal.
- **Pen test report** from the third-party audit.
- **Production deployment authorization:** go-live approval.

## How rapp/1 underpins this step

- **Approval bound to exact bytes.** In [[RAPP CICD]], evidence records (`rapp-cicd/1-evidence`) and the decision (`rapp-cicd/1-promotion`) refer to one exact release candidate. A changed payload has a new particle hash, so it is a different release. An approval cannot silently carry over to changed code.
- **Signed, not just recorded.** Authoritative payloads travel in signed RAPP/1 frames. A local unsigned file is a draft and cannot authorize promotion. See [[The Frame]] and [[Trust and Signatures]].
- **Kernel drift is a blocker.** The release-shaped artifact must contain the pinned Grail bytes before its tests and approval. A digest mismatch is a blocking `kernel-drift` finding. See [[Security Considerations]] and [[Distros and Pinning]].

The upstream specification does not replace pen tests or compliance audits. It makes the approved candidate unambiguous.

## Related

- [[Step 11 Production Planning]]
- [[Step 13 Production Deployment]]
- [[Security Considerations]]
- [[RAPP CICD]]
- [[Trust and Signatures]]
