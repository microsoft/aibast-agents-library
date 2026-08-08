---
name: improvement-option-comparison
description: Routes the Operations Director prompt "Give me the practical options to improve throughput without hiding the quality tradeoffs." with three evidence-backed choices per line.
---
<!-- bic:source=blank -->
# Improvement option comparison

Use this skill for requests such as "Give me the practical options to improve
throughput without hiding the quality tradeoffs," "how do we raise output," or
"what are our response paths." Always present three options per line and keep
the quality tradeoff explicit.

## Inputs (from the packaged synthetic records)

Per line: the throughput gap (uph), the bottleneck station and its cycle/takt,
and the highest-defect station. Use the precomputed option figures in the
rules reference.

## Procedure

For each line, present exactly three labeled options and keep quality visible:

- **Option 1 — Reduce the bottleneck cycle time** (process re-engineering,
  tooling upgrade). Target cycle = takt × 0.95; expected gain = round(gap × 0.6).
- **Option 2 — Add a parallel station at the bottleneck.** Effective cycle =
  bottleneck cycle / 2; expected gain = round(gap × 0.85); investment estimate
  $45,000 – $120,000.
- **Option 3 — Quality improvement** at the highest-defect station (reduce
  rework loop and scrap); expected gain = round(gap × 0.2). Never drop this
  option — it is how the quality tradeoff stays visible.

Then state the combined projected operating score = round(current OEE × 1.12).

### Precomputed results to use

- Electronics Assembly Line A (gap 38 uph): Option 1 Functional Test 25.3s →
  19.0s, +23 uph; Option 2 parallel Functional Test 12.7s, +32 uph,
  $45,000 – $120,000; Option 3 quality at Final Assembly (0.18%), +8 uph;
  combined 79.4% (from 70.9%).
- Metal Fabrication Line B (gap 39 uph): Option 1 Robotic Welding 14.2s →
  11.4s, +23 uph; Option 2 parallel Robotic Welding 7.1s, +33 uph,
  $45,000 – $120,000; Option 3 quality at Robotic Welding (0.30%), +8 uph;
  combined 96.1% (from 85.8%).
- Polymer Molding Line C (gap 72 uph): Option 1 Injection Molding 18.4s →
  14.2s, +43 uph; Option 2 parallel Injection Molding 9.2s, +61 uph,
  $45,000 – $120,000; Option 3 quality at Injection Molding (0.45%), +14 uph;
  combined 76.2% (from 68.0%).

## Output

For every line, use these exact labels in full; never abbreviate them as
`Opt 1`, `Opt 2`, `Opt 3`, or `Quality Gain`:

- `Option 1`
- `Option 2`
- `Quality improvement`

Show each exact label with its expected gain, then the combined projected
operating score. If the user asks about one line, give that line's three
options; otherwise cover all three lines.

## Grounding and safety

- Every gain, cost, and investment range is a synthetic planning estimate, not
  a commitment. Label them as such.
- Never present a throughput gain while hiding its quality/defect impact.
- Recommend only; never authorize spend, equipment, or headcount.
- Never say you lack access and never ask the user to name a line.
- End with:
  `> Synthetic pilot data; figures are planning estimates, not a live ERP, IoT, or Power BI reading.`

## Fallback

If the user requests a valuation or scenario outside the packaged records,
say which evidence is missing and offer the three known lines and their
precomputed options; do not calculate or invent a new scenario.
