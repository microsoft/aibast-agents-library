---
name: prior-authorization-criteria-evidence
description: Reproduce the deterministic Prior Authorization Agent — criteria evidence workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — criteria evidence

## Locked persona prompt

`Show the synthetic criteria checklist for SYN-AUTH-001 without deciding medical necessity.`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

Use the following finding-body template with the exact request and its referenced fictional policy. Replace every placeholder from retrieved evidence; never emit placeholders or another policy's values.

Render these as complete text lines; do not split them across table cells. Use Markdown headings and a separate paragraph or bullet for each field, not a fenced code block.

```text
# Criteria-to-Evidence Crosswalk
## {request_id}: {policy_title}
Synthetic effective date: {effective_date}
Checklist only; presence does not establish medical necessity or authorization.
## Reviewer checks
Reviewer check: {requirement}
```

Repeat the final line once for every requirement in source order, preserving its exact wording. Keep `Reviewer check:` and the complete requirement together on each line. A shared table-column heading or checkmark is not a replacement for this repeated prefix.

Any supporting evidence association follows its complete reviewer-check line and preserves source missingness; it must not turn a requirement into a finding that it is satisfied. Append citations after complete lines. Retain the global policy's exact terminal safety footer.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
