# Cart Abandonment Recovery Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/cart-abandonment-recovery.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_CAR_01["CAR-01: abandonment_analysis<br/><small>Marketing Manager</small><br/><small>As Marketing Manager, show where the anonymous synthetic cart journey …</small>"]
    n_CAR_02["CAR-02: recovery_campaign<br/><small>Digital Marketing Lead</small><br/><small>As Digital Marketing Lead, outline a consent-aware draft sequence with…</small>"]
    n_CAR_03["CAR-03: incentive_optimization<br/><small>Growth Manager</small><br/><small>As Growth Manager, compare margin-aware value scenarios and keep every…</small>"]
    n_CAR_04["CAR-04: conversion_tracking<br/><small>Growth Manager</small><br/><small>As Growth Manager, summarize the fixed recovery metrics and separate b…</small>"]
    n_CAR_01 --> n_CAR_02
    n_CAR_02 --> n_CAR_03
    n_CAR_03 --> n_CAR_04
```
