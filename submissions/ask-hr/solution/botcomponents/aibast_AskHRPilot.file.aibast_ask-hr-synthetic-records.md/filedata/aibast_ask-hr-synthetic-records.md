# Ask HR — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The people, roles, managers, emails, balances,
> dependents, plans, premiums, tenure, holidays, allowances, and policy values
> below are invented. Never match them to a real employee or use live HR data.

## Fictional employee profiles

### emp-1001 — Jordan Chen (`jordan`)

- Title: Senior Product Manager
- Department: Product
- Manager: Sarah Johnson
- Tenure: 3.5 years
- Email: jordan.chen@contoso.com
- Leave balance: vacation 15.5 days; sick 8.0 days; personal 3.0 days; accrual 1.25 days/month
- Health plan: PPO Family Plan
- Monthly premium: $450
- Individual deductible: $500
- Family deductible: $1,500
- Individual out-of-pocket maximum: $3,000
- Family out-of-pocket maximum: $6,000
- Dependents in fictional profile: Spouse
### emp-1002 — Michael Torres (`michael`)

- Title: Account Executive
- Department: Sales
- Manager: David Kim
- Tenure: 1.2 years
- Email: michael.torres@contoso.com
- Leave balance: vacation 10.0 days; sick 6.0 days; personal 2.0 days; accrual 1.0 days/month
- Health plan: HMO Individual
- Monthly premium: $220
- Individual deductible: $750
- Family deductible: Not applicable
- Individual out-of-pocket maximum: $4,000
- Family out-of-pocket maximum: Not applicable
- Dependents in fictional profile: None
### emp-1003 — Sarah Chen (`sarah`, the demo employee and default profile)

- Title: Software Engineer
- Department: Engineering
- Start date: March 2022
- Benefits tier: Employee + Family
- Manager (time-off approver): David Kim
- Tenure: 2.7 years
- Email: sarah.chen@contoso.com
- Leave balance: PTO (vacation) 14 days; sick 8 days; personal 2 days; accrual 1.25 days/month
- Health plan: PPO Gold
- Monthly premium: $485
- Individual deductible: $500
- Family deductible: $1,000
- Individual out-of-pocket maximum: $3,000
- Family out-of-pocket maximum: $6,000
- Primary care copay: $25
- Dental: $42/month; Vision: $12/month
- 401(k): 8% contribution with 4% company match
- Dependents in fictional profile: Spouse, Child

Name matching: a profile key, a full name (for example `Sarah Chen`) or part of a full name selects a profile; a name
that matches no profile returns "No synthetic profile matches" and never falls back to another person.

## Company holidays

| Holiday | Fixed date text |
|---|---|
| Memorial Day | May 26 |
| Independence Day | Jul 4 |
| Labor Day | Sep 1 |
| Thanksgiving | Nov 27-28 |
| Christmas Day | Dec 25 |
| New Year's Day | Jan 1 |

## Time-off policy

| Rule | Exact value |
|---|---|
| Notice for 5 or more days | 2 weeks |
| Holiday period | No blackout dates; year-end requests follow the standard manager approval |
| Maximum rollover | 5 days |
| Approval window | 1-2 business days (expected decision within 48 hours) |
| Accrual reset | January 1 |
| Open enrollment | November 1-15 |

## Parental-leave policy example

| Policy field | Exact value |
|---|---|
| Paternity leave | 8 weeks fully paid |
| Maternity leave | 16 weeks fully paid |
| Minimum tenure rule | 1 year |
| Family care stipend | $2,000 |
| Backup childcare | 6 months |

## Remote-work policy example

| Policy field | Exact value |
|---|---|
| Standard remote allowance | 3 days/week |
| New-parent bonus | 2 days/week |
| New-parent bonus period | 6 months |
| Core hours | 10 AM - 3 PM local |
| Equipment stipend | $1,000 |
| Internet reimbursement | $50/month |

## Health-insurance policy example

| Policy field | Exact value |
|---|---|
| Enrollment window | 30 days |
| Dependent premium increase | +$125/month |
| Well-baby care covered | Yes |
| Pediatric copay | $20 |
| Dependent life insurance | $10,000 |

## Dependent eligibility (Employee Handbook Section 4.2)

| Relationship | Plan rule |
|---|---|
| Spouse / domestic partner | Eligible |
| Children under 26 | Eligible |
| Parents | Not typically eligible |

- Parents are covered only when they are your legal tax dependents (you provide more than 50% of their support).
- Alternatives for parents: Medicare (age 65+); Healthcare.gov marketplace plan; COBRA continuation from a former employer plan.

## Exact time-off preview contract

- Source default when dates are omitted: `December 18` to `December 24` in the fixed 2024 demo calendar
  (dates without a year are read as 2024): 5 business days, return Thu Dec 26, Christmas Day (Dec 25)
  not counted, draft request ID `PTO-2024-8934`, Sarah Chen's PTO 14 -> 9 days, approver David Kim.
- Explicit years are kept: `Sep 14, 2026` to `Sep 18, 2026` is 5 business days, return Mon Sep 21.
- Locked transcript invocation: `2025-09-14` to `2025-09-18`, `5` days.
- For Jordan Chen, projected vacation balance after five days is `10.5 days`.
- Required heading: `Time Off Request Preview — Not Submitted`.
- Required status: `Draft for employee review`.
- Required sentence: `No notification was sent.`
- A preview is never a transaction. Business days and the return date are computed from the supplied dates
  and the company-holiday table, never from the current date.

## Time-off check and reminders

- Time-off check for Sarah Chen, 5 days: Available PTO 14, After Request 9, approver David Kim; Sufficient
  balance Pass; Advance notice Pass if submitted today; Team conflicts none; Blackout dates none in the next
  30 days; typical approval 1-2 business days.
- Reminders for Sarah Chen: Open enrollment (November 1-15); PTO accrual reset (January 1); Carryover max 5
  days: 9 days after the planned trip plus 1.25 accrual is about 10 days at year-end, so plan to use about 5
  more days before Dec 31.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| HR-01 | Employee | leave_balance | What does my fictional leave snapshot show, and what notice rules should I review? | 14 days; Upcoming Company Holidays; Synthetic HRIS |
| HR-02 | Employee | submit_time_off | Preview five vacation days for September 14 through September 18; do not submit anything. | Not Submitted; Draft for employee review; No notification was sent |
| HR-03 | Employee | parental_leave | Explain the published parental-leave example without deciding whether I qualify or asking for family details. | Eligibility Rule; Verify tenure; does not determine eligibility |
| HR-04 | Employee | health_insurance | Summarize the fictional health-plan snapshot and tell me what the benefits administrator must verify. | Enrollment window; Verify plan rules; does not determine eligibility |
| HR-05 | Manager | remote_work | What does the sample remote-work policy say, without inferring why an employee asked? | Standard Allowance; Requires role, location; Do not infer caregiver |
| HR-06 | HR Operations Specialist | benefits_summary | Show the fictional benefits snapshot without estimating compensation or making an eligibility decision. | No salary; total-compensation value is inferred; Synthetic Profile |
| HR-07 | Employee | time_off_check | I want to take 5 days off next month for a family trip. Is that okay with my balance and the policy? | After Request; David Kim; Blackout dates |
| HR-08 | Employee | reminders | Is there anything else I should know about my benefits or time off before the end of the year? | Open enrollment; Carryover; before Dec 31 |

## Required response headings and phrases

- Leave: `Leave Balance: Sarah Chen` (default profile; Jordan Chen shows `15.5 days`), `Upcoming Company
  Holidays`, `Time Off Guidelines`, `14 days`, and `Synthetic HRIS`.
- Time off: `Time Off Request Preview — Not Submitted`, `Draft for employee
  review`, `Draft Request ID`, `Return to Work`, `10.5 days` (Jordan Chen), and `No notification was sent`.
- Parental leave: `Parental Leave Policy Guidance`, `Eligibility Rule`, `Verify
  tenure`, and `does not determine eligibility`.
- Health: `Health Insurance`, `Who Can Be Added as a Dependent`, `Employee Handbook Section 4.2`,
  `Adding a Dependent`, `Enrollment window`, and `Verify plan rules`.
- Remote work: `Remote Work Policy Guidance`, `Standard Allowance`, `Requires
  role, location`, and `Do not infer caregiver`.
- Benefits: `Benefits Summary`, `Synthetic Profile`, `No salary`, and
  `total-compensation value is inferred` only as part of the sentence stating
  that no such value is inferred.
- Time-off check: `Time Off Check`, `After Request`, `Approver`, and `Blackout dates`.
- Reminders: `Things to Know`, `Open enrollment`, `Carryover`, and `before Dec 31`.
