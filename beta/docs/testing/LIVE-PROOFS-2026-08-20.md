# Frontier live proofs — 2026-08-20

This log separates real-kernel visual captures from deterministic automated
coverage. A pending row is not a visual claim.

## Streaming

| Variant | Real-kernel observation | Status |
|---------|-------------------------|--------|
| Raw | The comparison run produced 12 visible growth steps. | Captured |
| Smooth v1 — paced kernel wire | A 1,683-character Claude reply produced six visible growth steps: `+22`, `+431`, `+216`, `+68`, and `+600` characters after the initial paint, with 1–2 second gaps. Kernel unresolved-Markdown structural gating caused the lumps. | Captured; superseded |
| Smooth v2 — Frontier provisional renderer | Live visual capture and handoff-height observation. | **Pending** |

The deterministic v2 VM proof covers zero kernel bytes before terminal, at
least 40 monotonic provisional renders for 1,600 characters, byte-identical
replay, and a single handoff/removal. It does not replace the pending live
visual capture.
