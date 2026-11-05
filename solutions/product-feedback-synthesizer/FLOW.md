# Product Feedback Synthesizer Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/product-feedback-synthesizer.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PFS_01["PFS-01: feedback_summary<br/><small>Product Manager</small><br/><small>Aggregate and analyze feedback from multiple sources to provide a unif…</small>"]
    n_PFS_02["PFS-02: feature_requests<br/><small>Engineering Lead</small><br/><small>Apply AI-driven sentiment and pattern recognition to identify critical…</small>"]
    n_PFS_03["PFS-03: sentiment_analysis<br/><small>Director of Product</small><br/><small>Apply AI-driven sentiment and pattern recognition to identify critical…</small>"]
    n_PFS_04["PFS-04: roadmap_impact<br/><small>Product Manager</small><br/><small>Automate prioritization and workflow orchestration to convert insights…</small>"]
    n_PFS_01 --> n_PFS_02
    n_PFS_02 --> n_PFS_03
    n_PFS_03 --> n_PFS_04
```
