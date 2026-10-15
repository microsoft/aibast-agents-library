---
name: day-swing-night-production-plan
description: Routes the Plant Manager prompt "Translate the current line performance into a day, swing, and night shift plan." using the packaged schedule and staffing records.
---
<!-- bic:source=blank -->
# Day, swing, and night production plan

Use this skill for requests such as "Translate the current line performance
into a day, swing, and night shift plan," "build the three-shift plan," or
"how should we staff the shifts." Cover all three lines and all three shifts.

## Inputs (from the packaged synthetic records)

The shift schedule (Day, Swing, Night with hours, operators, premium, start,
end) and each line's actual output per hour.

## Procedure

1. Present the shift schedule: Day (06:00–14:00, 24 operators, 1.0x), Swing
   (14:00–22:00, 22 operators, 1.0x), Night (22:00–06:00, 18 operators,
   1.15x premium). Each shift is 8 hours.
2. Compute planned output per line and shift: Day and Swing = actual_uph × 8;
   Night = round(actual_uph × 8 × 0.9) at 90% efficiency. Fixed results:
   - Electronics Assembly Line A: Day 1,136 / Swing 1,136 / Night 1,022 /
     Daily Total 3,294.
   - Metal Fabrication Line B: Day 2,088 / Swing 2,088 / Night 1,879 /
     Daily Total 6,055.
   - Polymer Molding Line C: Day 1,344 / Swing 1,344 / Night 1,210 /
     Daily Total 3,898.
3. Show operator allocation: 64 total operators across shifts, 3 lines, 7.1
   average operators per line per shift.
4. Note that the Night shift runs at 90% efficiency and carries a 1.15x labor
   premium — surface this as the cost/tradeoff of the night shift.
5. If asked, add the weekly capacity view (5/6/7 operating days) from the
   full-24-hour daily figures.

## Output

A shift-schedule table, a planned-output-by-line-and-shift table with the
Day/Swing/Night columns and Daily Total, and the operator-allocation summary.

## Grounding and safety

- Use only the packaged schedule and output figures; never invent shifts,
  operators, or lines.
- The Daily Total (Night at 90%) is intentionally lower than the full-24-hour
  Output/Day figure — do not conflate them.
- The plan is a synthetic projection to evaluate, not a committed schedule or
  a staffing order.
- Never say you lack access and never ask the user to name a line.
- End with:
  `> Synthetic pilot data; figures are planning estimates, not a live ERP, IoT, or Power BI reading.`

## Fallback

If the user asks for a shift, day count, or line not in the records, say what
is missing and use only the known synthetic schedule.
