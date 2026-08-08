---
name: algorithm-documentation-and-go-live-review
description: Use when an algorithm or strategy is about to go live, needs sign-off, or may be running with incomplete or expired documentation.
---
<!-- bic:source=blank -->
# Algorithm documentation and go-live review

## Fixed snapshot result

- ALGO-POV-NL goes live in 6 days, has never been validated, and is missing
  risk controls, a kill-switch test, and a conformance test.
- ALGO-IS-DE is already live, but its validation is expired; TRD-88117,
  TRD-88133, and TRD-88162 used it.
- ALGO-VWAP-EU and ALGO-DARK-EU are current.

## Procedure

1. Block ALGO-POV-NL from go-live in the pilot until the missing artefacts are
   complete and validation is recorded.
2. Escalate ALGO-IS-DE for revalidation and name the affected trades.
3. Distinguish an upcoming go-live block from an already-live documentation
   exception.
4. Name Quant Execution as the role owner.
5. Do not claim that a real deployment was disabled.
