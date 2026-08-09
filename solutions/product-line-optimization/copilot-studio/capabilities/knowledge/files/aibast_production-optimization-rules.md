# Product Line Optimization Pilot — Rules, Thresholds, and Response Framing

> SYNTHETIC PILOT DATA. These are fictional calculation rules and planning
> figures for a self-contained pilot. Every number produced with them is a
> synthetic planning estimate, never a live plant reading or a commitment.

## Core formulas

- Operating score (OEE) = `availability% × performance% × quality% / 10000`,
  rounded to one decimal.
- Throughput gap (uph) = `design_capacity_uph − actual_output_uph`.
- Daily output (full schedule) = `actual_output_uph × 24 hours`.
- Daily loss vs design = `throughput_gap_uph × 24`.
- Station delta = `cycle_time_s − takt_time_s`. Positive = over takt.
- Over-takt percentage = `(cycle_time − takt_time) / takt_time × 100`.
- Bottleneck station = the station with the longest cycle time on the line.
- Highest-defect station = the station with the largest defect_rate on the line.
- Annual quality cost = `daily_output × 250 days × ((100 − quality%) / 100) ×
  $12.50` scrap/rework per unit.

## Thresholds and rankings

- Operating-attention threshold: a line with an operating score below **75%**
  is BELOW TARGET and needs attention.
- Rank lines needing attention by ascending operating score. Fixed ranking:
  1) Polymer Molding Line C at 68.0%, 2) Electronics Assembly Line A at 70.9%,
  3) Metal Fabrication Line B at 85.8% (healthy, no action).
- When explaining a line's loss, lead with the weakest of its three factors:
  Line C → availability (78%); Line A → performance (82%) plus availability
  (87%); Line B → none, it is on target.

## Bottleneck reference

| Line | Bottleneck station | Over takt |
|---|---|---|
| Electronics Assembly Line A | Functional Test (A5) | +5.3s (26.5%) |
| Metal Fabrication Line B | Robotic Welding (B3) | +2.2s (18.3%) |
| Polymer Molding Line C | Injection Molding (C2) | +3.4s (22.7%) |

When ranking which station to address first across the plant, use the
largest over-takt percentage: Functional Test (A5) first at 26.5%, then
Injection Molding (C2) at 22.7%, then Robotic Welding (B3) at 18.3%.

## Improvement-option framing

Always present three options per line and keep the quality tradeoff visible.
Gains are synthetic estimates derived from each line's throughput gap.

- **Option 1 — Reduce the bottleneck cycle time.** Target cycle time =
  `takt × 0.95`. Method: process re-engineering, tooling upgrade.
  Expected gain = `round(gap × 0.6)` uph.
- **Option 2 — Add a parallel station at the bottleneck.** Effective cycle
  time = `bottleneck_cycle / 2`. Expected gain = `round(gap × 0.85)` uph.
  Investment estimate: $45,000 – $120,000.
- **Option 3 — Quality improvement.** Target the highest-defect station;
  reduce rework loop time and scrap. Expected gain = `round(gap × 0.2)` uph.
- **Combined projected operating score** = `round(current_OEE × 1.12, 1)`.

### Precomputed option figures

**Electronics Assembly Line A** (gap 38 uph):
- Option 1 — Functional Test: 25.3s → 19.0s; gain +23 uph.
- Option 2 — parallel Functional Test: effective 12.7s; gain +32 uph; $45,000 – $120,000.
- Option 3 — quality at Final Assembly (0.18% defect); gain +8 uph.
- Combined projected operating score: 79.4% (from 70.9%).

**Metal Fabrication Line B** (gap 39 uph):
- Option 1 — Robotic Welding: 14.2s → 11.4s; gain +23 uph.
- Option 2 — parallel Robotic Welding: effective 7.1s; gain +33 uph; $45,000 – $120,000.
- Option 3 — quality at Robotic Welding (0.30% defect); gain +8 uph.
- Combined projected operating score: 96.1% (from 85.8%).

**Polymer Molding Line C** (gap 72 uph):
- Option 1 — Injection Molding: 18.4s → 14.2s; gain +43 uph.
- Option 2 — parallel Injection Molding: effective 9.2s; gain +61 uph; $45,000 – $120,000.
- Option 3 — quality at Injection Molding (0.45% defect); gain +14 uph.
- Combined projected operating score: 76.2% (from 68.0%).

## Shift-planning rules

- Three shifts: Day (24 operators, 1.0x), Swing (22 operators, 1.0x), Night
  (18 operators, 1.15x premium). Each shift is 8 hours.
- Day and Swing planned output = `actual_uph × 8`.
- Night planned output = `round(actual_uph × 8 × 0.9)` (90% efficiency).
- Daily Total (shift plan) = Day + Swing + Night. This is intentionally lower
  than the full-24-hour Output/Day figure because Night runs at 90%.
- Operator totals: 64 across shifts, 3 lines, 7.1 average operators per line
  per shift.
- Night premium (1.15x) is a labor-cost multiplier; surface it when discussing
  the cost or tradeoff of running the night shift.

## Safety and response rules

1. Lead with the operational decision or most important finding, then the
   supporting facts (line, station, and figures).
2. Report analysis and recommendations only. Never start, stop, throttle,
   reschedule, or reconfigure a line, station, or shift; never dispatch
   maintenance; never commit an investment or a headcount change. Use
   "Recommended," "Suggested next step," and "Projected."
3. Keep the quality tradeoff visible in every throughput recommendation; never
   present a throughput gain while hiding its quality or defect impact.
4. Label every estimate, projection, gain, cost, and investment range as a
   synthetic planning figure, not a measured result or a commitment.
5. Do not invent lines, stations, products, defects, shifts, operators, or
   numbers beyond the packaged synthetic records. If asked about something not
   in the data, say what is missing and list the known records.
6. Never claim or imply access to a live ERP (Dynamics 365), IoT/telemetry
   (Azure IoT Hub), MES, or Power BI system. Never say you lack access either;
   simply work from the packaged synthetic records.
7. Work across all three lines by default. Never ask the user to provide or
   name a line before answering — the three lines are already known.

## Response style

Use concise Markdown suited to a plant floor: a short decision statement first,
then a compact table or tight bullets. Use uph for rate, seconds for cycle and
takt, and currency with separators. Avoid filler and generic preambles. End
substantive answers with:
`> Synthetic pilot data; figures are planning estimates, not a live ERP, IoT, or Power BI reading.`

## Production seams (future only)

If this pilot is promoted, the packaged synthetic records could be replaced by
Dynamics 365 ERP production context, Azure IoT Hub equipment telemetry, and
Power BI reporting surfaces. These are future integration seams only. No live
connector is configured in this pilot.
