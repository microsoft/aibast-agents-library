---
name: plant-wide-operating-health-review
description: Routes the Plant Manager prompt "Which production line needs attention today, and what is driving the loss?" by ranking all three synthetic lines and naming the drivers.
---
<!-- bic:source=blank -->
# Plant-wide operating health review

Use this skill for plant-wide "what needs attention" questions, such as
"Which production line needs attention today, and what is driving the loss?",
"where are we losing output," or "which line is worst." No line name is
required — always evaluate all three synthetic lines together and never ask
the user to pick one.

## Inputs (from the packaged synthetic records)

For each of Electronics Assembly Line A, Metal Fabrication Line B, and Polymer
Molding Line C, read the operating summary: operating score (OEE),
availability, performance, quality, actual-versus-design output, daily output,
daily loss vs design, and annual quality cost.

## Procedure

1. Rank the lines by ascending operating score and apply the 75% attention
   threshold. Fixed result: Polymer Molding Line C at 68.0% (Priority 1) and
   Electronics Assembly Line A at 70.9% (Priority 2) are BELOW TARGET; Metal
   Fabrication Line B at 85.8% is healthy and needs no action.
2. Lead with the two lines needing attention. For each, name the operating
   score, the daily output gap vs design (Line C: 1,728 units/day; Line A:
   912 units/day), and the annual quality cost (Line C: $352,800.00; Line A:
   $63,900.00).
3. State the driver of the loss using the weakest factor:
   - Line C: availability at 78% (unplanned downtime) is the primary driver;
     performance 89.7% and quality 97.2% are comparatively solid.
   - Line A: loss is split between performance at 82% and availability at
     87%; quality is excellent at 99.4%.
4. Note that Line B (85.8%) is meeting targets — no immediate action.
5. Recommend the sequence: start with Line C availability (equipment
   failures, maintenance backlog, changeover delays), then Line A performance
   (cycle-time or process constraint). Offer to run the constraining-station
   analysis next.

## Output

A short decision statement ("Two lines need attention today"), then a compact
ranked view with each line's operating score, driver, gap, and quality cost.
Use a table if listing all three lines.

## Grounding and safety

- Use only the packaged synthetic figures; never recalculate from another
  source and never invent lines or stations.
- Report findings and recommendations only; never start, stop, throttle, or
  reconfigure a line. Use "Recommended" and "Suggested next step."
- Never say you lack access and never ask the user to provide a line.
- Label figures as synthetic planning estimates and end with:
  `> Synthetic pilot data; figures are planning estimates, not a live ERP, IoT, or Power BI reading.`

## Fallback

If the user names a line not in the synthetic set, say it is not in the pilot
and list the three known lines rather than inventing data.
