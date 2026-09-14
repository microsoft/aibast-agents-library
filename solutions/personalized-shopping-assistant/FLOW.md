# Personalized Shopping Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/personalized-shopping-assistant.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PSA_01["PSA-01: product_recommendations<br/><small>Personal Shopper</small><br/><small>As Personal Shopper, suggest transparent options for Synthetic Shopper…</small>"]
    n_PSA_02["PSA-02: style_profile<br/><small>Clienteling Specialist</small><br/><small>As Clienteling Specialist, summarize Synthetic Shopper B's opt-in pref…</small>"]
    n_PSA_03["PSA-03: inventory_check<br/><small>Retail Manager</small><br/><small>As Retail Manager, show the synthetic size-level availability and veri…</small>"]
    n_PSA_04["PSA-04: outfit_builder<br/><small>Personal Shopper</small><br/><small>As Personal Shopper, draft coordinated outfit options and transparent …</small>"]
    n_PSA_01 --> n_PSA_02
    n_PSA_02 --> n_PSA_03
    n_PSA_03 --> n_PSA_04
```
