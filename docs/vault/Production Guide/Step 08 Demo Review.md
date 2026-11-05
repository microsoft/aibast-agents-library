---
title: Step 08 Demo Review
section: Production Guide
status: published
hook: How the customer first sees the working prototype, and how Quality Gate 4 decides what happens next.
source: docs/rapp-guide.html#step8
---

# Step 08 Demo Review

**Demo Review** is the first time the customer sees their agents actually working.
You record the live prototype solving the agreed MVP scenarios and send it for feedback.
This step is **Quality Gate #4**: approve, iterate, or stop scope creep.

Guide section: [Step 8 in the production guide](../rapp-guide.html#step8)

## What this step is

- **Goal:** film the working prototype solving the MVP scenarios, then collect the customer's verdict.
- **Rule:** no slides, no mockups. Real execution only.
- **Time:** 2-4 hours in total.
  - Record demo: 30-60 minutes.
  - Optional edit: 30 minutes.
  - Customer review: 1-2 days.
  - Feedback session: 30-60 minutes.

## Who does it

- **Human:** records the screen, narrates, and collects customer feedback.
- **Automation:** the agents run the MVP scenarios in real time.

## Inputs (from Step 07)

- **Live prototype**, deployed and tested ([[Step 07 Deploy Prototype]]).
- **M365 Copilot access** through Teams, Outlook, or web.
- **Rehearsal notes** on which scenarios work.
- **Approved MVP doc**, signed by the customer in [[Step 04 Customer Validation]].

## How to record

1. **Prepare.** Open M365 Copilot (Teams or web, whichever is cleaner). Load the approved scenarios. Start a screen recorder.
2. **Record each MVP scenario.** Show the agent being called and the real answer.
3. **Show behind the scenes (optional).** Briefly show agent calls in Application Insights. This proves it is not a mockup.
4. **Narrate the value.** Before: name the business problem. During: say what the agent is doing. After: state the result.

### The "waiter" pattern

The customer sees a simple conversation.
Behind it, the LLM takes the request, calls the right agent with parameters, and returns a clean answer.
The user never needs to see the orchestration.

## Sending the demo

The guide gives an email template. It lists each scenario with timestamps and asks **two questions**:

1. Do these agents solve the business problem as you described it?
2. Is there anything you'd like adjusted before we move to production?

Then hold a 30-60 minute feedback call. Useful questions:

- "Did the agents solve the problem as you described it?" (scope alignment)
- "Were the results accurate and useful?" (data integration quality)
- "Is there anything you'd change or add?" (scope creep detector)
- "Can you see this being used by your team?" (adoption readiness)
- "What would production deployment look like?" (sets up Steps 11-14)

## Outputs

- **Demo video:** a 10-15 minute recording showing all MVP scenarios.
- **Customer feedback notes.**
- **Approval email:** written confirmation to proceed.
- **Iteration log** (if needed).
- **Green light for production:** a customer-approved prototype ready for final polish.

Checklist before [[Step 09 Generate Video Demo]]:

- The customer watched the full demo.
- All MVP scenarios were demonstrated.
- Written approval was received.
- No major scope changes.
- The production timeline was discussed.

## The gate: three outcomes

- **APPROVED.** Proceed to [[Step 09 Generate Video Demo]].
- **ITERATE.** Loop back to [[Step 05 Generate Agent Code]], regenerate the affected agents, redeploy, re-record.
- **SCOPE CREEP.** Stop. Explain it is outside MVP scope. Keep the original scope or restart at [[Step 01 Discovery Call]].

**The "while we're at it" trap:** new capabilities mean new discovery, new MVP, and new testing. Log them for the next phase and finish this MVP first.

## How rapp/1 underpins this step

- The "waiter" pattern is the **agent contract** at work: the model chooses an agent and calls it through one chat surface. See [[The Agent Contract]] and [[The Brainstem Kernel]].
- An ITERATE loop goes back to [[Step 05 Generate Agent Code]] to regenerate the affected agents, then redeploys and re-records.

## Related

- [[Step 07 Deploy Prototype]]
- [[Step 09 Generate Video Demo]]
- [[Step 04 Customer Validation]]
- [[The Agent Contract]]
- [[Production Guide Overview]]
