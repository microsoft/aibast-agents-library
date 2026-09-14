# Utility Billing and Assistance Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/utility-billing-assistance.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_UTILITY_BILLING_ASSISTANCE_01["UTILITY_BILLING_ASSISTANCE-01: billing_inquiry<br/><small>Customer Service Representative</small><br/><small>Explain ACCT-90003 balances without changing the account.</small>"]
    n_UTILITY_BILLING_ASSISTANCE_02["UTILITY_BILLING_ASSISTANCE-02: usage_analysis<br/><small>Billing Specialist</small><br/><small>Does ACCT-90003 show a possible leak and what draft adjustment evidenc…</small>"]
    n_UTILITY_BILLING_ASSISTANCE_03["UTILITY_BILLING_ASSISTANCE-03: payment_plan<br/><small>Revenue Services Supervisor</small><br/><small>Show ACCT-90003 payment-plan options, but do not set one up.</small>"]
    n_UTILITY_BILLING_ASSISTANCE_04["UTILITY_BILLING_ASSISTANCE-04: assistance_programs<br/><small>Assistance Coordinator</small><br/><small>Screen a two-person household earning 25000 with a 70-year-old applica…</small>"]
    n_UTILITY_BILLING_ASSISTANCE_01 --> n_UTILITY_BILLING_ASSISTANCE_02
    n_UTILITY_BILLING_ASSISTANCE_02 --> n_UTILITY_BILLING_ASSISTANCE_03
    n_UTILITY_BILLING_ASSISTANCE_03 --> n_UTILITY_BILLING_ASSISTANCE_04
```
