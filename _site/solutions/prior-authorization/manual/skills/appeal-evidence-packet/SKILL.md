---
name: prior-authorization-appeal-evidence-packet
description: Reproduce the deterministic Prior Authorization Agent — reconsideration evidence workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — reconsideration evidence

## Locked persona prompt

`Prepare a minimum-necessary reconsideration evidence outline for SYN-AUTH-001.`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

Use the following finding-body template with the exact fields from the requested synthetic record. Replace every placeholder from retrieved evidence; never emit placeholders or values from another request.

Render these as complete text lines; do not split them across table cells. Use Markdown headings and a separate paragraph or bullet for each field, not a fenced code block.

```text
# Reconsideration Evidence Draft
## {request_id}: {service}
A reviewer must confirm that reconsideration or appeal is appropriate and permitted.
Source-recorded workflow state: {source_status} ({source_date})
Referenced policy to verify: {policy_reference}
Include only authorized, minimum-necessary evidence.
## Evidence items
{evidence_item}: {source_value}
Human utilization reviewer owns rationale, completeness, and submission.
```

Repeat the evidence-item line for every item in source order. Keep each complete item name and its exact source value together, including every not-found or human-review qualifier. These lines inventory source evidence, not actions to perform. Append citations after complete lines. Retain the global policy's exact terminal safety footer.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Source-grounding boundary

Treat workflow state and evidence presence as independent recorded facts. Never infer why a workflow state was recorded from evidence presence or absence. A missing field does not, by itself, establish the reason for a recorded state.

Quote a workflow-state reason only when the matched record explicitly provides it. Otherwise include this source-limit line exactly once: `The synthetic source does not state why this workflow state was recorded.`

Do not append advice, action requirements, or judgments to source-reported evidence values. Do not label missing evidence as a cause, a required corrective action, or a reason to seek reconsideration. Do not add a reviewer rationale or a recommended next-steps section.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
