---
title: Step 09 Generate Video Demo
section: Production Guide
status: published
hook: How to turn the approved prototype into a produced, narrated demo for executives.
source: docs/rapp-guide.html#step9
---

# Step 09 Generate Video Demo

**Generate Video Demo** produces a polished, shareable video of the solution.
It is for executives, sales decks, and internal evangelism.
Unlike the raw screen recording in Step 08, this is a **produced demo** with scripted narration and polished visuals.

Guide section: [Step 9 in the production guide](../rapp-guide.html#step9)

## What this step is

- **Goal:** a self-contained demo video with Azure TTS narration.
- **Time (manual):** 3-4 hours.
  - Build the demo JSON in the Local-First Chat Animation Studio: 1-2 hours.
  - Script narration and timing: 1 hour.
  - Test and refine: 1 hour.
- **Automation vision:** a Video Demo Generator creates the demo JSON from a prototype walkthrough, cutting the time to about 30 minutes.

## Who does it

- **Human:** builds the demo structure, writes the script and narration, and adjusts timing.
- **Tool:** the **Video Demo Generator**, a Copilot Studio declarative agent. The guide also includes a copy-paste fallback prompt if the agent link is not working.

## Inputs (from Step 08)

- **Customer-approved prototype** from [[Step 08 Demo Review]].
- **Screen recording** of real agent execution.
- **MVP documentation:** business value, metrics, use cases.
- **Project JSON:** customer, stakeholders, timeline (from [[Step 02 Transcript Analysis]]).

## The demo JSON

The generator returns one JSON document with four parts:

- `demoMetadata` - title, customer, industry, `totalDuration`, `voiceName`, `createdDate`.
- `demoSteps` - 7-10 steps, each with `id`, `name`, `duration`, `voiceText`, and a `narrator` overlay.
- `chatInteractions` - the user, system, and agent messages shown per step.
- `agentCards` - an agent `title`, `status`, and `details` per step.

A fragment of the required structure, as given in the guide:

```json
{
  "demoMetadata": {
    "title": "[Customer Name] AI Agent Demo",
    "customer": "[Customer Name]",
    "industry": "[Industry: legal, sales, hr, it, etc.]",
    "totalDuration": "[Total seconds, e.g., 75]",
    "voiceName": "en-US-GuyNeural",
    "createdDate": "[YYYY-MM-DD]"
  }
}
```

## The narrative arc

Every demo follows the same three-part story:

1. **Problem hook (8-10 s):** the painful manual process.
2. **Solution demo (40-50 s):** 3-4 agent capabilities with specific examples.
3. **Business impact (10-15 s):** ROI, metrics, scale.

Writing rules from the prompt:

- `voiceText` is written for speech, about 150 words per minute.
- `duration` matches the narration (20 words is about 8000 ms).
- Overlays carry specific metrics: time saved, accuracy, cost reduction.
- Use the real agent names from the implementation.

## Output and exit

- **Demo JSON file:** `demos/[customer-name]-demo.json`
- **Standalone HTML demo:** a self-contained file with narration.
- **Hosted URL** (optional): GitHub Pages or an internal server link.
- **MP4 video** (optional): a recorded playthrough for PowerPoint.
- **Usage instructions:** how to view, navigate, and share.

Quality check before sharing:

- Metrics match the project JSON.
- Narration timing is natural.
- Agent cards appear at the right steps.
- The customer name is spelled correctly.
- The demo works on mobile.

These go to the customer for sign-off in [[Step 10 Final Demo Review]].

## How rapp/1 underpins this step

This step is presentation work. The upstream RAPP/1 specification does not define the demo JSON format.
The link to the protocol is indirect: the agent names and behavior shown must match the real agents that passed [[Step 06 Code Quality Review]] and run under [[The Agent Contract]].

## Related

- [[Step 08 Demo Review]]
- [[Step 10 Final Demo Review]]
- [[Step 07 Deploy Prototype]]
- [[The Agent Contract]]
- [[Production Guide Overview]]
