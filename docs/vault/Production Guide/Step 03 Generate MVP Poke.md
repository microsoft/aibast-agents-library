---
title: Step 03 Generate MVP Poke
section: Production Guide
status: published
hook: What an MVP poke is, what goes in it, and how it is sent to the customer before any code is written.
source: "docs/rapp-guide.html#step3"
---

# Step 03 Generate MVP Poke

The **MVP poke** is a short, plain-language summary of what we think the customer needs.
It asks one question: "This is what I heard — is it correct?"
It is sent **before any code is written**.

Guide section: [Step 3 in the production guide](../rapp-guide.html#step3)

## At a glance

- **Type:** Manual (automation planned)
- **Duration:** 1-2 hours
- **Owner:** Delivery Team drafts; the Field Team sends it
- **Input:** the validated project JSON from [[Step 02 Transcript Analysis]]
- **Output:** a 1-2 page poke document and the email that carries it

## Why a poke, not a requirements document

- **Lightweight:** 1-2 pages, not 20.
- **Plain language:** written for business stakeholders.
- **Invites feedback:** "Did we hear you right?", not "Sign off on these requirements".
- **Fast:** sent within 24 hours of the discovery call.

The poke is both a validation checkpoint and the **specification** that guides prototype generation.

## The five sections

1. **Problem statement** — 2-3 sentences in the customer's terms, with numbers.
2. **Proposed MVP solution** — what it does, 3-4 key capabilities, and **scope boundaries** (what it does not do).
3. **Data requirements** — a simple list of the data access needed.
4. **Success metrics** — measurable targets, such as planning time from 2-3 hours a day to 5 minutes.
5. **Timeline and next steps** — a simple week-by-week roadmap.

## The generation prompt

The guide drafts the poke from the project JSON with this prompt:

```
Generate an MVP "poke" document based on this customer project JSON:
[Insert validated project JSON from Step 2]
The document should be:
- 1-2 pages maximum
- Written in plain business language (not technical jargon)
- Structured as: Problem Statement, Proposed Solution, Data Requirements, Success Metrics, Timeline
- Specific and measurable (not vague "improve efficiency")
- Include scope boundaries (what we're NOT building)
- End with clear next steps for customer to respond
Tone: Professional but approachable. We're confirming we heard them correctly, not pitching a solution.
```

## Sending it

Whoever ran the discovery call emails the poke. The email asks:

- Did we capture the problem correctly?
- Is this MVP scope right, or should we adjust?
- Are the data sources accessible?
- Any concerns before we proceed?

## Output and exit criteria

- **MVP poke document:** 1-2 pages, Word or PDF
- **Email to customer:** sent with the document attached
- **Timeline started:** the customer response window, usually 2-3 days

Total human time so far is about 1.25 hours. If the customer says "that's not what we meant", you have saved 3-6 weeks.
Any detail the customer adds is the **first feedback cycle**, before a line of code exists.

Next: [[Step 04 Customer Validation]].

## How rapp/1 underpins this step

Not directly. The poke is a business document, and the upstream RAPP/1 specification does not govern it.

Its scope boundaries do shape the build later. Each capability listed becomes an agent behind the single `/chat` endpoint, not a new API route. See [[The Wire]] and [[The Agent Contract]].

## Related

- [[Step 02 Transcript Analysis]]
- [[Step 04 Customer Validation]]
- [[Step 05 Generate Agent Code]]
- [[Production Guide Overview]]
- [[The Wire]]
