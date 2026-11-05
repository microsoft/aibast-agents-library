---
title: Step 01 Discovery Call
section: Production Guide
status: published
hook: How to run the discovery call whose transcript becomes the foundation for every later step.
source: "docs/rapp-guide.html#step1"
---

# Step 01 Discovery Call

The **discovery call** captures the customer's biggest problems in their own words.
Its **transcript** is the input to everything that follows.
Lead with business pain, not with AI.

Guide section: [Step 1 in the production guide](../rapp-guide.html#step1)

## At a glance

- **Type:** Manual
- **Duration:** 30-60 minutes, one focused conversation with the decision makers
- **Owner:** Field Team, anyone who works with customers
- **Output:** recording, transcript, named stakeholders

## The three critical questions

### 1. What are your biggest problems?

This keeps the focus on business value, not technology.
A good answer is specific and measurable.
Example: field sales reps ask every day where to go, in what order, and what to do on arrival.
A bad answer is "we need AI".

### 2. What data sources do you have?

AI without data is useless. State this caveat up front: without data access, the project is severely limited.
Typical sources:

- **CRM systems:** Dynamics 365, Salesforce, custom systems
- **Document repositories:** SharePoint, OneDrive, file shares
- **Operational systems:** inventory, scheduling, ticketing
- **External APIs:** weather, traffic, market data

### 3. How do you solve this manually today?

The **manual process is the blueprint** for automation.
You scale what they already do. You do not invent a new workflow.
Users recognize their familiar process, just faster.

## How to run the call

**Before:**

- Enable recording (Teams auto-transcribe, or another transcription tool).
- Tell participants the call is recorded.
- Invite 1-2 key decision makers, not ten people.

**During:**

- Let them talk. Extract knowledge; do not pitch.
- Ask "walk me through exactly what the end user does".
- Get specific numbers ("20 hours per week"), not "inefficiencies".
- Note competing solutions they mention.
- Confirm data access.

## Red flags

- "We just want to try AI" — no specific problem, so no MVP.
- "We can't share any data" — AI needs data.
- "We have 50 different problems" — you need **one** focused MVP.
- "We're not sure who the decision maker is" — get the right person.

## Output and exit criteria

- **Recording file:** MP4 or audio
- **Transcript file:** plain text is ideal; a Teams `.vtt` works
- **Key stakeholders:** names and roles mentioned on the call

**Litmus test:** "If I had 6 Python agents and access to their data, could I build a prototype that solves this?"

- Yes → go to [[Step 02 Transcript Analysis]].
- No → schedule a follow-up call.

## How rapp/1 underpins this step

It does not, directly. The discovery call is a human conversation. The upstream RAPP/1 specification governs bytes, identity and the wire, not meetings.

The link comes later. The "6 Python agents" in the litmus test become files that follow [[The Agent Contract]] in [[Step 05 Generate Agent Code]].

## Related

- [[Production Guide Overview]]
- [[Step 02 Transcript Analysis]]
- [[Step 03 Generate MVP Poke]]
- [[The Agent Contract]]
- [[Glossary]]
