# Copilot Studio source

This directory contains the reviewed, source-controlled component set pushed to
the kodyv8 Building Permit Pilot.

The `.mcs/` directory is intentionally excluded because it contains
environment-specific synchronization metadata. Create a new connected workspace
with `pac copilot init`, then copy or generate these components into that
workspace before pushing.

## Components

- `settings.mcs.yml` — global role, routing, synthetic-data boundary, safety,
  response style, and production integration seams.
- `behaviors/` — seven focused skills corresponding to the seven portable
  Python workflows.
- `capabilities/knowledge/files/` — the static synthetic permit records and the
  synthetic routing, zoning, checklist, and fee references.

The canonical acceptance corpus lives in
`../evals/copilot-studio-transcripts.json`.
