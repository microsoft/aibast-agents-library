# Product Line Optimization Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. Every line, station, defect figure, shift, operator
> count, and derived number below is fictional and packaged with this pilot.
> These are stable pilot facts, not a live reading. Do not recalculate them
> from any other source and do not invent lines or stations beyond this set.

There are exactly four synthetic production lines: Production Line 3
(LINE-3, the demo line), Electronics Assembly Line A (LINE-A), Metal
Fabrication Line B (LINE-B), and Polymer Molding Line C (LINE-C). Never
reference any other line.

## Production Line 3 holiday surge plan (the demo scenario)

Asked as: "Analyze production line 3 performance and optimize for the upcoming
holiday demand surge expecting 40% volume increase", then "Show optimization
plan", "Show implementation details", "Show risk mitigation", "Show financial
analysis", "Show monitoring plan".

### Line analysis

- Line: Consumer electronics assembly; output 2,400 units/day (100 uph x 24 h)
- OEE: 71% (87% x 82% x 99.4% = 70.9%; world-class: 85%)
- Availability: 87% | Performance: 82% | Quality: 99.4%
- Holiday requirement: target 3,360 units/day (2,400 x 1.40, 40% increase);
  timeline 4 weeks to ramp; production days: 45 days (holiday season)
- Primary bottleneck: SMT Placement Station 3B (limiting to 2,450 units/day);
  second constraint: Functional Test

### Production optimization plan (bottleneck solutions)

| Optimization | Output Gain | Investment | Timeline |
|---|---|---|---|
| SMT reprogram | +180 units/day | $5K | 3 days |
| 4th shift overlap | +400 units/day | $18K/week | Immediate |
| 2nd test station | +200 units/day | $85K | Week 1-2 |
| Packaging robots (2) | +150 units/day | $240K | Week 1-2 |
| Preventive maint blitz | +100 units/day | $12K | Week 1 |

Total capacity gain +1,030 units/day. Baseline 2,400 units/day; after
optimization 3,430 units/day; target needed 3,360 units/day; safety margin
102% of target (3,430 / 3,360).

### 4-week implementation plan

- Week 1: Quick Wins - SMT placement sequence optimization (Engineering: 3
  days); 4th shift staffing: hire 12 operators (recruiting active); preventive
  maintenance blitz; parts staging: $2.3M inventory secured. Expected output:
  2,700 units/day.
- Week 2: Equipment Installation - test station #2 delivery and install; robot
  integration team on-site; operator training 40 hours (all shifts); trial
  production runs. Expected output: 3,000 units/day.
- Week 3: Optimization - robots deployed to packaging line; material flow
  optimization; buffer stock positioning; performance tuning. Expected output:
  3,200 units/day.
- Week 4: Full Capacity - system integration complete; full production
  testing; quality systems validated; go-live at week 4 end. Expected output:
  3,430 units/day (target 3,360).
- Weekly outputs are ramp milestones (new crew and equipment run below full
  efficiency until week 4).

### Risk mitigation strategy

| Risk | Concern | Mitigation | Backup / monitoring | Confidence / target |
|---|---|---|---|---|
| 1 Component Supply Chain | Semiconductor lead times | 45-day safety stock secured | 3 alternative suppliers qualified | Confidence 94% |
| 2 Labor Availability | Holiday hiring competition | 12 temps hired + 8 backup | Cross-trained existing staff | Confidence 92% |
| 3 Quality Maintenance | Speed vs. quality trade-off | Additional QC station added | Real-time defect tracking | Target 99.4% maintained |
| 4 Equipment Reliability | Increased wear at higher output | Preventive maintenance schedule | Critical spare parts on-site | MTBF target >1,200 hours |

### Financial analysis (synthetic finance model)

- One-time investment: $342,000 ($5K + $85K + $240K + $12K)
- 4th shift overlap: $18,000/week x 9 weeks (45 production days at 5 days/week) = $162,000
- Total investment: $504,000
- Incremental output: 960 units/day (3,360 - 2,400) x 45 days = 43,200 units
- Contribution margin: $45/unit (synthetic); incremental contribution $1,944,000
- Net benefit: $1,440,000; ROI: 286%; payback: 11.7 production days
- Parts staging ($2.3M inventory) is working capital, not part of the investment.

### Real-time monitoring plan

- Dashboards: hourly output tracking (target: 140 units/hr = 3,360 / 24); OEE by
  station; quality metrics (real-time defect rate); cycle time variance (+/-5%
  threshold); material consumption vs. plan.
- Alert thresholds: output <90% target: supervisor notification; quality <99%:
  QC immediate review; equipment anomaly: predictive maint alert; material
  shortage warning: 4-hour buffer.
- Daily stand-ups: output vs. target; bottleneck identification; quality
  issues; labor efficiency; next-day planning.
- Success metrics (holiday season): units produced 151,200 target (3,360 x 45
  days); quality 99.4% maintained; OEE from 71% toward 85% world-class.
- All of this is a recommendation: no hiring, purchase, schedule change or
  equipment order is executed by the agent.

## Line operating summary

Operating score is `availability% × performance% × quality% / 10000`. The
operating-attention threshold is 75%: a line below 75% is flagged BELOW TARGET.

| Line ID | Line | Product | Design (uph) | Actual (uph) | Availability | Performance | Quality | Operating score (OEE) | Flag |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| LINE-3 | Production Line 3 | Consumer electronics assembly | 120 | 100 | 87.0% | 82.0% | 99.4% | 70.9% | BELOW TARGET |
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
| Production Line 3 | 2,400 | 480 | $45,000.00 |
| Electronics Assembly Line A | 3,408 | 912 | $63,900.00 |
| Metal Fabrication Line B | 6,264 | 936 | $254,475.00 |
| Polymer Molding Line C | 4,032 | 1,728 | $352,800.00 |

## Station cycle-time and defect records

Delta is `cycle_time − takt_time`; a positive delta means the station runs
over takt. The bottleneck (BN) of each line is the station with the longest
cycle time. Bottlenecks: LINE-3 → SMT Placement Station 3B (3B); LINE-A → Functional Test (A5); LINE-B → Robotic
Welding (B3); LINE-C → Injection Molding (C2).

### Production Line 3 (takt 25.7s at holiday demand: 86,400 s / 3,360 units) — Bottleneck: SMT Placement Station 3B (3B), +9.6s over takt (37.4%)

| Station | ID | Cycle (s) | Takt (s) | Delta | Defect % |
|---|---|---:|---:|---:|---:|
| Solder Paste Print | 3A | 30.5 | 25.7 | +4.8 | 0.05% |
| SMT Placement Station 3B (BN) | 3B | 35.3 | 25.7 | +9.6 | 0.10% |
| Reflow Soldering | 3C | 31.0 | 25.7 | +5.3 | 0.08% |
| Functional Test | 3D | 34.6 | 25.7 | +8.9 | 0.04% |
| Packaging | 3E | 33.9 | 25.7 | +8.2 | 0.02% |

Highest-defect station on LINE-3: SMT Placement Station 3B (3B) at 0.10% (also the bottleneck).

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
| Production Line 3 | component_shift 34%, solder_bridge 28%, tombstoning 18%, cosmetic 12%, functional 8% |
| Electronics Assembly Line A | solder_bridge 38%, component_shift 22%, missing_part 15%, cosmetic 14%, functional 11% |
| Metal Fabrication Line B | weld_porosity 42%, dimensional_oor 28%, surface_scratch 18%, bend_angle 12% |
| Polymer Molding Line C | short_shot 35%, flash 25%, sink_mark 20%, weld_line 12%, warpage 8% |

## Shift schedule

| Shift | Hours | Operators | Premium | Start | End |
|---|---:|---:|---:|---|---|
| Day | 8 | 24 | 1.0x | 06:00 | 14:00 |
| Swing | 8 | 22 | 1.0x | 14:00 | 22:00 |
| Night | 8 | 18 | 1.15x | 22:00 | 06:00 |

Total operators across shifts: 64. Lines running: 4. Average operators per
line per shift: 5.3. Holiday surge on Production Line 3: a 4th shift overlap
adds 12 operators (+400 units/day).

## Planned output by line and shift

Each shift runs `actual_uph × 8`, so the shift-plan Daily Total equals the
full-24-hour Output/Day figure above (one daily-output figure everywhere).

| Line | Day Shift | Swing Shift | Night Shift | Daily Total |
|---|---:|---:|---:|---:|
| Production Line 3 | 800 | 800 | 800 | 2,400 |
| Electronics Assembly Line A | 1,136 | 1,136 | 1,136 | 3,408 |
| Metal Fabrication Line B | 2,088 | 2,088 | 2,088 | 6,264 |
| Polymer Molding Line C | 1,344 | 1,344 | 1,344 | 4,032 |

## Weekly capacity summary

Weekly output uses the full-24-hour daily figure `actual_uph × 24` times the
number of operating days.

| Line | Weekly (5 days) | Weekly (6 days) | Weekly (7 days) |
|---|---:|---:|---:|
| Production Line 3 | 12,000 | 14,400 | 16,800 |
| Electronics Assembly Line A | 17,040 | 20,448 | 23,856 |
| Metal Fabrication Line B | 31,320 | 37,584 | 43,848 |
| Polymer Molding Line C | 20,160 | 24,192 | 28,224 |
