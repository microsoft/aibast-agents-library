# Product Line Optimization Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/product-line-optimization.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_PLO_01["PLO-01<br/><small>Plant Manager</small><br/><small>Analyze production line performance in real time to identify bottlenec…</small>"]
    n_PLO_02["PLO-02<br/><small>Production Engineer</small><br/><small>Analyze production line performance in real time to identify bottlenec…</small>"]
    n_PLO_03["PLO-03<br/><small>Operations Director</small><br/><small>Recommend targeted equipment and process improvements to improve outpu…</small>"]
    n_PLO_04["PLO-04<br/><small>Plant Manager</small><br/><small>Plan and coordinate implementation while minimizing disruption</small>"]
    n_PLO_01 --> n_PLO_02
    n_PLO_02 --> n_PLO_03
    n_PLO_03 --> n_PLO_04
```
