---
title: Step 04 Customer Validation
section: Production Guide
status: published
hook: How the customer signs off on the MVP scope at Quality Gate 2, and what to do for each possible answer.
source: "docs/rapp-guide.html#step4"
---

# Step 04 Customer Validation

**Customer validation** is **Quality Gate 2**.
The customer confirms in writing that the MVP poke describes what they need.
This **locks scope** before any code is written. The guide calls it the most important gate.

Guide section: [Step 4 in the production guide](../rapp-guide.html#step4)

## At a glance

- **Type:** Audit (Quality Gate 2)
- **Duration:** 1-2 days, mostly waiting for the customer
- **Owner:** Field Team, who manages the customer conversation
- **Input:** the poke from [[Step 03 Generate MVP Poke]]
- **Output:** written approval, final poke, updated project JSON, green light to build

## Three possible outcomes

### 1. "Yes, that's exactly right"

- Save the sign-off email and stakeholder names.
- Mark the MVP "Approved - Ready for Development" in the tracker.
- Go straight to [[Step 05 Generate Agent Code]].

### 2. "Close, but here's what needs to change"

- Capture **all** feedback in writing, never only by phone.
- Ask the LLM to update the poke with the corrections.
- Send poke v2. Repeat until you reach outcome 1.

When the customer adds a requirement, choose:

- **Add it to the MVP** and re-send the poke, or
- **Move it to Phase 2** to deliver value faster.

New requirements often change the design. Five agents may become six, with a new focused agent for the new need. The modular shape absorbs this without a rebuild.

### 3. "This isn't what we need"

- Schedule a follow-up discovery call.
- Go back to [[Step 01 Discovery Call]].
- **Do not** start development.

## Watch for scope creep

Warning signs:

- "Can we also add ten more features?"
- "Actually, we need something completely different."
- "My boss says we also need..."

Use the poke as a **scope boundary**: lock this MVP first, then expand.

## Exit checklist

Before moving on, confirm:

- **Written confirmation** of the MVP scope.
- **Stakeholder sign-off** from the budget holder, not only end users.
- **Data access confirmed.**
- **Timeline agreed.**
- **Scope locked** — no "we'll figure it out later" items.

## Output

- **Customer approval email**, saved as proof of scope.
- **Final MVP poke** (v2 or v3) with all feedback included.
- **Updated project JSON** with status `mvp-locked` and the approval date.
- **Green light** to generate agent code.

Time invested so far: about 2 hours of human time plus 1-2 days of waiting. The risk removed: weeks of building the wrong thing.

## How rapp/1 underpins this step

Not directly. Sign-off is a business agreement, outside the upstream RAPP/1 specification.

The modular point in outcome 2 does match the protocol's design. New capability is added as a new agent behind `/chat`, never as a new endpoint. See [[The Wire]] and [[The Agent Contract]].

## Related

- [[Step 03 Generate MVP Poke]]
- [[Step 05 Generate Agent Code]]
- [[Step 01 Discovery Call]]
- [[Production Guide Overview]]
- [[The Wire]]
