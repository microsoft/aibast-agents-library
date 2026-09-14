# Asset Maintenance Forecast Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/asset-maintenance-forecast.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_ASSET_MAINTENANCE_FORECAST_01["ASSET_MAINTENANCE_FORECAST-01: maintenance_forecast<br/><small>Plant Manager</small><br/><small>Which asset is most likely to interrupt operations next, and what evid…</small>"]
    n_ASSET_MAINTENANCE_FORECAST_02["ASSET_MAINTENANCE_FORECAST-02: asset_health<br/><small>Reliability Engineer</small><br/><small>Show me the weakest asset condition and whether this is an operating a…</small>"]
    n_ASSET_MAINTENANCE_FORECAST_03["ASSET_MAINTENANCE_FORECAST-03: budget_projection<br/><small>Finance Business Partner</small><br/><small>What maintenance funding should I reserve for the transformer risk?</small>"]
    n_ASSET_MAINTENANCE_FORECAST_04["ASSET_MAINTENANCE_FORECAST-04: work_order_plan<br/><small>Maintenance Planner</small><br/><small>Draft the maintenance queue for AST-X002, but do not create any work o…</small>"]
    n_ASSET_MAINTENANCE_FORECAST_01 --> n_ASSET_MAINTENANCE_FORECAST_02
    n_ASSET_MAINTENANCE_FORECAST_02 --> n_ASSET_MAINTENANCE_FORECAST_03
    n_ASSET_MAINTENANCE_FORECAST_03 --> n_ASSET_MAINTENANCE_FORECAST_04
```
