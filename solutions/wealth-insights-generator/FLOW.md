# Wealth Insights Generator Agent — flow diagram

Auto-generated from the ordered case contract at `tests/demo_cases/wealth-insights-generator.json`. Each node is one locked case, in file order, labeled with its persona and operation. This is a process-flow view of the scenario, not an implementation architecture diagram (see `README.md` for architecture).

```mermaid
flowchart TD
    n_WIG_01["WIG-01: market_brief<br/><small>Advisory Director</small><br/><small>Fixed market snapshot</small>"]
    n_WIG_02["WIG-02: client_insights<br/><small>Wealth Advisor</small><br/><small>Analyze client portfolios and surface held-away wealth to uncover expa…</small>"]
    n_WIG_03["WIG-03: opportunity_alerts<br/><small>Relationship Manager</small><br/><small>Detect planning gaps and risk exposures to support proactive client co…</small>"]
    n_WIG_04["WIG-04: performance_attribution<br/><small>Portfolio Strategist</small><br/><small>Detect planning gaps and risk exposures to support proactive client co…</small>"]
    n_WIG_05["WIG-05: meeting_brief<br/><small>Wealth Advisor</small><br/><small>Produce personalized engagement materials instantly</small>"]
    n_WIG_01 --> n_WIG_02
    n_WIG_02 --> n_WIG_03
    n_WIG_03 --> n_WIG_04
    n_WIG_04 --> n_WIG_05
```
