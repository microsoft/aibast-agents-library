---
title: Sources and Provenance
section: Reference
status: published
hook: Where does this vault's protocol content come from, and which text is authoritative?
source: "SPEC.md (whole document); book/ (whole book); NOTICE.md"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Sources and Provenance

The protocol notes in this vault are an **authored, plain-language expansion** of the upstream RAPP/1 specification.
They explain the specification. They do not replace it.
When a note and the specification differ, **the specification wins**.

## What the vault draws on

- **Protocol, Operations and Building notes** — expand the upstream RAPP/1 specification and its companion book.
- **Production Guide step notes** — expand the RAPP production guide in this repository, [the production guide](../rapp-guide.html).

Notes drawn only from the production guide carry no upstream pin.

## The pin

Every specification-derived note is pinned to one upstream commit:

`0b24e7d60786d39d97265338add9ca784bf5a7ab`

- The pin means the note was written against that exact version of the specification.
- Newer upstream versions do not change these notes until someone re-reviews them and moves the pin.

## How each note records its source

Every note starts with YAML frontmatter. Two fields carry provenance:

- `source` — the upstream file and section the note expands, for example `SPEC.md §7; book/05-the-frame.md`.
- `upstream_commit` — the pinned commit, for notes drawn from the specification.

Example:

```yaml
source: "SPEC.md §7; book/05-the-frame.md"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
```

## The build check

A build check reads every note's frontmatter.
**It fails if a specification-derived note loses its pin.**
This keeps every protocol claim traceable to a fixed source.

## The specification text is authoritative

- The vault paraphrases. It may simplify wording for readability.
- Normative rules (MUST, MUST NOT, exact formats) live in the specification.
- Exact identifiers — field names, wire tags such as `rapp/1`, hash space names, file names — are copied verbatim.

If you are implementing, read the specification section named in each note's `source` field.
Start with [[Implementing the Protocol]].

## License

The upstream RAPP/1 specification is MIT licensed.
Copyright (c) 2025-2026 Kody Wildfeuer.

The full upstream license notice is in [NOTICE](NOTICE.md).

## Related

- [[How to Use This Vault]]
- [[Protocol at a Glance]]
- [[Versioning and Evolution]]
- [[Conformance and Drift]]
- [[Glossary]]
