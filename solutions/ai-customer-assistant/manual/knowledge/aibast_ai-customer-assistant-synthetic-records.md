# Customer Escalations — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. No record below is a real customer, message,
> account, support case, system reading, or outcome. Use these records exactly;
> do not browse, refresh, supplement, or invent data.

## Inquiry records

| ID | Customer | Contact | Email | Channel | Subject | Description | Category | Priority | Created at | Status | Account tier | Sentiment |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INQ-4001 | Acme Corp | Lisa Park | lisa.park@acmecorp.com | Live Chat | Unable to generate monthly usage report | The export button on the analytics dashboard returns a 500 error when selecting date ranges longer than 30 days. | Technical Issue | High | 2025-11-14T09:23:00Z | Open | Enterprise | Frustrated |
| INQ-4002 | Bright Solutions | Tom Reyes | tom.reyes@brightsol.com | Email | Pricing for additional user seats | We are expanding our team by 15 people next quarter and need pricing for additional seats on the Professional plan. | Billing & Pricing | Medium | 2025-11-14T10:05:00Z | Open | Professional | Neutral |
| INQ-4003 | Greenfield Inc | Maria Santos | maria.santos@greenfield.io | Phone | SSO configuration not working after IdP migration | After migrating from Okta to Azure AD, SSO login redirects to a blank page. SAML assertion looks correct in dev tools. | Technical Issue | Critical | 2025-11-14T08:12:00Z | Open | Enterprise | Urgent |
| INQ-4004 | Summit Partners | Jake Miller | jake.miller@summitpartners.com | Support Portal | Feature request: bulk user import via CSV | Currently we have to add users one at a time. We need CSV import capability for onboarding 200+ users. | Feature Request | Low | 2025-11-13T16:30:00Z | Open | Professional | Positive |

## Knowledge-base records

### KB-101 — How to Export Analytics Reports

- Category: Analytics
- Relevance score: 95%
- Summary: Step-by-step guide for exporting usage and analytics reports in CSV, PDF, and Excel formats.
- Last updated: 2025-10-20
- Views: 1,247
- Helpful votes: 892
- Resolution steps:
  1. Navigate to Analytics > Reports
  2. Select date range (max 90 days per export)
  3. Choose format (CSV, PDF, Excel)
  4. Click Export and wait for download link via email
### KB-102 — SSO Configuration Guide (SAML 2.0)

- Category: Authentication
- Relevance score: 92%
- Summary: Complete guide for configuring SAML-based SSO with supported identity providers.
- Last updated: 2025-11-01
- Views: 2,034
- Helpful votes: 1,567
- Resolution steps:
  1. Go to Admin > Security > SSO Settings
  2. Upload IdP metadata XML or enter values manually
  3. Set Assertion Consumer Service URL to https://app.example.com/sso/callback
  4. Map attributes: email, firstName, lastName, groups
  5. Test with SSO debug mode enabled before enforcing
### KB-103 — User Management and Seat Licensing

- Category: Billing
- Relevance score: 88%
- Summary: Overview of seat-based licensing, adding users, and managing subscriptions.
- Last updated: 2025-09-15
- Views: 3,421
- Helpful votes: 2,890
- Resolution steps:
  1. View current seat count in Admin > Billing > Subscription
  2. Click Add Seats to purchase additional licenses
  3. New seats are prorated for the current billing cycle
  4. Bulk provisioning available via SCIM for Enterprise plans
### KB-104 — Known Issue: Report Export Timeout for Large Date Ranges

- Category: Analytics
- Relevance score: 97%
- Summary: Export fails with 500 error for date ranges exceeding 60 days. Workaround and fix timeline available.
- Last updated: 2025-11-10
- Views: 456
- Helpful votes: 398
- Resolution steps:
  1. Split export into 30-day segments as a workaround
  2. Engineering fix scheduled for v3.8.2 (target: Dec 2025)
  3. Contact support if you need a one-time bulk export

## Exact inquiry-to-knowledge behavior

- `INQ-4001`: `KB-104` is the top result, followed by `KB-101`.
- `INQ-4002`: `KB-103` is the matching licensing article.
- `INQ-4003`: `KB-102` is the matching SAML SSO article.
- `INQ-4004`: `KB-103` is the matching user-management article.
- Never create a knowledge result that is not one of `KB-101` through `KB-104`.

## Routing matrix

| Category | Priority | Recommended team | SLA target | Escalation rule triggered |
|---|---|---|---|---|
| Technical Issue | Critical | Tier 2 Engineering | 2 hours | Yes |
| Technical Issue | High | Tier 1 Technical Support | 4 hours | No |
| Technical Issue | Medium | General Support | 8 hours | No |
| Technical Issue | Low | General Support | 24 hours | No |
| Billing & Pricing | Critical | Billing Escalations | 2 hours | Yes |
| Billing & Pricing | High | Account Management | 4 hours | No |
| Billing & Pricing | Medium | Account Management | 8 hours | No |
| Billing & Pricing | Low | Self-Service Billing | 24 hours | No |
| Feature Request | Critical | Product Management | 8 hours | No |
| Feature Request | High | Product Management | 24 hours | No |
| Feature Request | Medium | Product Backlog | 72 hours | No |
| Feature Request | Low | Product Backlog | 168 hours | No |

## Satisfaction snapshot

| Metric | Exact value |
|---|---|
| Overall CSAT | 4.3/5.0 |
| NPS score | 42 |
| Average response time | 12 minutes |
| First-contact resolution | 78% |
| Week-over-week trend | +0.2 |
| Month-over-month trend | +0.1 |

### Recent fictional surveys

| Inquiry | Score | Comment | Date |
|---|---|---|---|
| INQ-3990 | 5 | Resolved quickly, great experience. | 2025-11-13 |
| INQ-3988 | 4 | Helpful but took a while to connect. | 2025-11-13 |
| INQ-3985 | 3 | Issue resolved but had to explain problem multiple times. | 2025-11-12 |
| INQ-3982 | 5 | Agent was knowledgeable and proactive. | 2025-11-12 |
| INQ-3979 | 2 | Still waiting for follow-up on my SSO issue. | 2025-11-11 |
| INQ-3975 | 4 | Good resolution, would prefer faster initial response. | 2025-11-11 |

### Score distribution

| Rating | Count | Share |
|---|---|---|
| 5 | 2 | 33% |
| 4 | 2 | 33% |
| 3 | 1 | 17% |
| 2 | 1 | 17% |
| 1 | 0 | 0% |

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| CES-01 | Back-Office Agent | handle_inquiry | I just inherited the export-error escalation. Give me the full brief before I respond. | INQ-4001; KB-104; No customer message is sent |
| CES-02 | Back-Office Agent | knowledge_search | What approved guidance should I review for the customer who cannot export a long analytics range? | KB-104; Resolution Steps; No customer message is sent |
| CES-03 | Escalation Manager | escalation_routing | The SSO migration case is urgent. Which queue and response target does our rulebook recommend? | Tier 2 Engineering; 2 hours; does not execute |
| CES-04 | Quality Analyst | satisfaction_survey | What does the latest service-quality snapshot say, and which signals need human review? | 4.3/5.0; Recent Surveys; fictional pilot records |

## Required response headings and phrases

- Inquiry brief: `Customer Inquiry: <ID>`, `Subject`, `Description`,
  `Recommended Response`, and `Review gate`.
- Knowledge search: `Knowledge Base Search Results`, `Top Match`, `Summary`,
  `Resolution Steps`, and `Review gate`.
- Routing: `Escalation Routing: <ID>`, `Routing Matrix`, and `Review gate`.
- Satisfaction: `Customer Satisfaction Dashboard`, `Score Distribution`,
  `Recent Surveys`, and `Trends`.
- Every substantive result must state: `No customer message is sent, no case is
  changed` and must not imply that a route was executed.
