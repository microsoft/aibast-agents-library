---
name: privacy-safe-complaint-classification
description: Classifies a complaint for a Customer Service Agent without repeating personal or sensitive content.
---
# Privacy-safe complaint classification

Return category, rationale, severity context, and an authorized-review next
step. Do not echo names, contacts, account details, payment data, or free-text
personal information. Send no response.

For the locked Customer Service Agent request, use the packaged synthetic
complaint text `The synthetic item stopped working after a week.` Do not ask
the user to provide more detail.

Return the exact heading `Draft Complaint Classification`, include the
`Product Quality` row from the complaint-category reference, and end with the
exact no-side-effect phrase `no return, refund`.
