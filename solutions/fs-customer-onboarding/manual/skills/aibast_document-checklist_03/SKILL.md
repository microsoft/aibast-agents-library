---
name: document-checklist
description: Mandatory first route for the exact Blackwood business-document prompt; return only the fixed APP-6002 checklist and guardrails.
---

# Document checklist

## Mandatory FCO-03 response contract

For the exact prompt `Give me the business onboarding document list for Blackwood before I call them.`:

1. Load this uploaded skill first.
2. Retrieve the attached synthetic records and cite them with native citations.
3. Return only the following user-facing structure, preserving every line and value:

`APP-6002 — Blackwood Capital Partners LLC`
`Owner: Jessica Nguyen`

`Required documents (6)`
- Articles of Incorporation / Formation
- EIN verification letter
- Certificate of Good Standing
- Operating Agreement / Bylaws
- Beneficial ownership declaration (FinCEN BOI)
- Government ID for all authorized signers

`Optional documents (2)`
- Business license
- Financial statements (last 2 years)

`Verification record: beneficial_ownership = in_progress; this does not establish document receipt or missing status.`

`Packaged snapshot rules (not current legal advice): documents must be current within 90 days, and business-account copies must be certified or notarized.`

`No outreach, communication, or contact with Blackwood Capital Partners LLC has occurred. Any call or correspondence requires authorized action by Jessica Nguyen.`

`Synthetic onboarding evidence only; no identity verification, approval, account opening, provisioning, outreach, or record change occurred. Authorized human review required.`

Do not add a status table, icons, product, risk, account status, other verification checks, talking points, priorities, requests, or inferred document receipt/missing status. Do not claim outreach occurred. Do not narrate internal routing or retrieval in the final answer.
