# Product Line Optimization Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. Every line, station, defect figure, shift, operator
> count, and derived number below is fictional and packaged with this pilot.
> These are stable pilot facts, not a live reading. Do not recalculate them
> from any other source and do not invent lines or stations beyond this set.

There are exactly three synthetic production lines: Electronics Assembly
Line A (LINE-A), Metal Fabrication Line B (LINE-B), and Polymer Molding Line C
(LINE-C). Never reference any other line.

## Line operating summary

Operating score is `availability% × performance% × quality% / 10000`. The
operating-attention threshold is 75%: a line below 75% is flagged BELOW TARGET.

| Line ID | Line | Product | Design (uph) | Actual (uph) | Availability | Performance | Quality | Operating score (OEE) | Flag |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| LINE-A | Electronics Assembly Line A | Industrial Control Module ICM-400 | 180 | 142 | 87.0% | 82.0% | 99.4% | 70.9% | BELOW TARGET |
| LINE-B | Metal Fabrication Line B | Structural Bracket SB-220 | 300 | 261 | 92.0% | 94.5% | 98.7% | 85.8% | On target |
| LINE-C | Polymer Molding Line C | Enclosure Housing EH-150 | 240 | 168 | 78.0% | 89.7% | 97.2% | 68.0% | BELOW TARGET |

- Line C has the lowest operating score (68.0%); its main driver is
  availability at 78% (unplanned downtime). Performance 89.7% and quality
  97.2% are comparatively solid.
- Line A is second (70.9%); its loss is split between availability (87%) and
  performance (82%), with excellent quality (99.4%).
- Line B is healthy (85.8%) and needs no immediate action.

## Daily output and loss summary

Output/Day uses actual output over the full 24 scheduled hours
(`actual_uph × 24`). Gap vs Design is `(design_uph − actual_uph) × 24` units
lost per day. Annual quality cost is `actual_uph × 24 × 250 days ×
((100 − quality%) / 100) × $12.50` scrap/rework per unit.

| Line | Output/Day | Gap vs Design (units lost/day) | Annual Quality Cost |
|---|---:|---:|---:|
| Electronics Assembly Line A | 3,408 | 912 | $63,900.00 |
| Metal Fabrication Line B | 6,264 | 936 | $254,475.00 |
| Polymer Molding Line C | 4,032 | 1,728 | $352,800.00 |

## Station cycle-time and defect records

Delta is `cycle_time − takt_time`; a positive delta means the station runs
over takt. The bottleneck (BN) of each line is the station with the longest
cycle time. Bottlenecks: LINE-A → Functional Test (A5); LINE-B → Robotic
Welding (B3); LINE-C → Injection Molding (C2).

### Electronics Assembly Line A (takt 20.0s) — Bottleneck: Functional Test (A5), +5.3s over takt (26.5%)

| Station | ID | Cycle (s) | Takt (s) | Delta | Defect % |
|---|---|---:|---:|---:|---:|
| SMT Placement | A1 | 18.5 | 20.0 | -1.5 | 0.12% |
| Reflow Soldering | A2 | 22.1 | 20.0 | +2.1 | 0.08% |
| AOI Inspection | A3 | 15.0 | 20.0 | -5.0 | 0.01% |
| Through-Hole Insert | A4 | 19.8 | 20.0 | -0.2 | 0.15% |
| Functional Test (BN) | A5 | 25.3 | 20.0 | +5.3 | 0.04% |
| Conformal Coating | A6 | 16.2 | 20.0 | -3.8 | 0.02% |
| Final Assembly | A7 | 19.0 | 20.0 | -1.0 | 0.18% |

Highest-defect station on LINE-A: Final Assembly (A7) at 0.18%.

### Metal Fabrication Line B (takt 12.0s) — Bottleneck: Robotic Welding (B3), +2.2s over takt (18.3%)

| Station | ID | Cycle (s) | Takt (s) | Delta | Defect % |
|---|---|---:|---:|---:|---:|
| Laser Cutting | B1 | 10.8 | 12.0 | -1.2 | 0.05% |
| CNC Bending | B2 | 11.4 | 12.0 | -0.6 | 0.22% |
| Robotic Welding (BN) | B3 | 14.2 | 12.0 | +2.2 | 0.30% |
| Grinding/Deburr | B4 | 9.5 | 12.0 | -2.5 | 0.06% |
| Powder Coating | B5 | 11.0 | 12.0 | -1.0 | 0.10% |
| QC Measurement | B6 | 8.2 | 12.0 | -3.8 | 0.00% |

Highest-defect station on LINE-B: Robotic Welding (B3) at 0.30% (also the bottleneck).

### Polymer Molding Line C (takt 15.0s) — Bottleneck: Injection Molding (C2), +3.4s over takt (22.7%)

| Station | ID | Cycle (s) | Takt (s) | Delta | Defect % |
|---|---|---:|---:|---:|---:|
| Material Drying | C1 | 12.0 | 15.0 | -3.0 | 0.02% |
| Injection Molding (BN) | C2 | 18.4 | 15.0 | +3.4 | 0.45% |
| Trim/Deflash | C3 | 10.5 | 15.0 | -4.5 | 0.08% |
| Ultrasonic Weld | C4 | 13.8 | 15.0 | -1.2 | 0.12% |
| Dimensional Check | C5 | 9.0 | 15.0 | -6.0 | 0.00% |
| Packaging | C6 | 7.5 | 15.0 | -7.5 | 0.05% |

Highest-defect station on LINE-C: Injection Molding (C2) at 0.45% (also the bottleneck).

## Defect category mix (share of defects per line)

| Line | Defect categories |
|---|---|
| Electronics Assembly Line A | solder_bridge 38%, component_shift 22%, missing_part 15%, cosmetic 14%, functional 11% |
| Metal Fabrication Line B | weld_porosity 42%, dimensional_oor 28%, surface_scratch 18%, bend_angle 12% |
| Polymer Molding Line C | short_shot 35%, flash 25%, sink_mark 20%, weld_line 12%, warpage 8% |

## Shift schedule

| Shift | Hours | Operators | Premium | Start | End |
|---|---:|---:|---:|---|---|
| Day | 8 | 24 | 1.0x | 06:00 | 14:00 |
| Swing | 8 | 22 | 1.0x | 14:00 | 22:00 |
| Night | 8 | 18 | 1.15x | 22:00 | 06:00 |

Total operators across shifts: 64. Lines running: 3. Average operators per
line per shift: 7.1.

## Planned output by line and shift

Day and Swing each run `actual_uph × 8`. Night runs at 90% efficiency:
`round(actual_uph × 8 × 0.9)`. The shift-plan Daily Total therefore differs
from the full-24-hour Output/Day figure above.

| Line | Day Shift | Swing Shift | Night Shift | Daily Total |
|---|---:|---:|---:|---:|
| Electronics Assembly Line A | 1,136 | 1,136 | 1,022 | 3,294 |
| Metal Fabrication Line B | 2,088 | 2,088 | 1,879 | 6,055 |
| Polymer Molding Line C | 1,344 | 1,344 | 1,210 | 3,898 |

## Weekly capacity summary

Weekly output uses the full-24-hour daily figure `actual_uph × 24` times the
number of operating days.

| Line | Weekly (5 days) | Weekly (6 days) | Weekly (7 days) |
|---|---:|---:|---:|
| Electronics Assembly Line A | 17,040 | 20,448 | 23,856 |
| Metal Fabrication Line B | 31,320 | 37,584 | 43,848 |
| Polymer Molding Line C | 20,160 | 24,192 | 28,224 |
