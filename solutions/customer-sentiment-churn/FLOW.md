# Customer Sentiment and Churn Prediction Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/customer-sentiment-churn.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CSC_01["CSC-01: sentiment_dashboard<br/><small>Customer Success Lead</small><br/><small>Aggregate sentiment across touchpoints to track trends before churn si…</small>"]
    n_CSC_02["CSC-02: churn_prediction<br/><small>Retention Specialist</small><br/><small>Predict churn risk to pinpoint critical and high-risk customers</small>"]
    n_CSC_03["CSC-03: retention_actions<br/><small>Relationship Manager</small><br/><small>Generate tailored retention and outreach plans</small>"]
    n_CSC_04["CSC-04: segment_analysis<br/><small>Head of Customer Experience</small><br/><small>Aggregate sentiment across touchpoints to track trends before churn si…</small>"]
    n_CSC_01 --> n_CSC_02
    n_CSC_02 --> n_CSC_03
    n_CSC_03 --> n_CSC_04
```
