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
### emp-1003 — Sarah Williams (`sarah`)

- Title: Engineering Lead
- Department: Engineering
- Manager: Alex Rivera
- Tenure: 5.0 years
- Email: sarah.williams@contoso.com
- Leave balance: vacation 22.0 days; sick 10.0 days; personal 3.0 days; accrual 1.5 days/month
- Health plan: PPO Family Plan
- Monthly premium: $450
- Individual deductible: $500
- Family deductible: $1,500
- Individual out-of-pocket maximum: $3,000
- Family out-of-pocket maximum: $6,000
- Dependents in fictional profile: Spouse, Child (age 4)

## Company holidays

| Holiday | Fixed date text |
|---|---|
| Memorial Day | May 26 |
| Independence Day | Jul 4 |
| Labor Day | Sep 1 |
| Thanksgiving | Nov 27-28 |
| Year-End | Dec 24-25, Dec 31-Jan 1 |

## Time-off policy

| Rule | Exact value |
|---|---|
| Notice for 5 or more days | 2 weeks |
| Holiday period | Dec 15 - Jan 5 requires manager pre-approval |
| Maximum rollover | 5 days |

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

## Exact time-off preview contract

- Source default when dates are omitted: `Sep 14, 2026` to `Sep 18, 2026`,
  `5` vacation days.
- Locked transcript invocation: `2025-09-14` to `2025-09-18`, `5` days.
- For Jordan Chen, projected vacation balance after five days is `10.5 days`.
- Required heading: `Time Off Request Preview — Not Submitted`.
- Required status: `Draft for employee review`.
- Required sentence: `No notification was sent.`
- A preview is never a transaction; the date strings supplied to the skill are
  echoed exactly and must not be recalculated from the current date.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| HR-01 | Employee | leave_balance | What does my fictional leave snapshot show, and what notice rules should I review? | 15.5 days; Upcoming Company Holidays; Synthetic HRIS |
| HR-02 | Employee | submit_time_off | Preview five vacation days for September 14 through September 18; do not submit anything. | Not Submitted; Draft for employee review; No notification was sent |
| HR-03 | Employee | parental_leave | Explain the published parental-leave example without deciding whether I qualify or asking for family details. | Eligibility Rule; Verify tenure; does not determine eligibility |
| HR-04 | Employee | health_insurance | Summarize the fictional health-plan snapshot and tell me what the benefits administrator must verify. | Enrollment window; Verify plan rules; does not determine eligibility |
| HR-05 | Manager | remote_work | What does the sample remote-work policy say, without inferring why an employee asked? | Standard Allowance; Requires role, location; Do not infer caregiver |
| HR-06 | HR Operations Specialist | benefits_summary | Show the fictional benefits snapshot without estimating compensation or making an eligibility decision. | No salary; total-compensation value is inferred; Synthetic Profile |

## Required response headings and phrases

- Leave: `Leave Balance: Jordan Chen`, `Upcoming Company Holidays`, `Time Off
  Guidelines`, `15.5 days`, and `Synthetic HRIS`.
- Time off: `Time Off Request Preview — Not Submitted`, `Draft for employee
  review`, `10.5 days remaining`, and `No notification was sent`.
- Parental leave: `Parental Leave Policy Guidance`, `Eligibility Rule`, `Verify
  tenure`, and `does not determine eligibility`.
- Health: `Health Insurance`, `Adding a Dependent`, `New Baby Benefits (100%
  Covered)`, `Enrollment window`, and `Verify plan rules`.
- Remote work: `Remote Work Policy Guidance`, `Standard Allowance`, `Requires
  role, location`, and `Do not infer caregiver`.
- Benefits: `Benefits Summary`, `Synthetic Profile`, `No salary`, and
  `total-compensation value is inferred` only as part of the sentence stating
  that no such value is inferred.
