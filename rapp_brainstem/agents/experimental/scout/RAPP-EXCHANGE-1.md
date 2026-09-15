# RAPP Exchange/1

**Status:** Experimental draft.

`rapp-exchange/1` is the first concrete binding of
[`agent-rosetta/1`](AGENT-ROSETTA-1.md). It is a reversible capability exchange
profile for AIs that do not already understand RAPP Brainstem. It maps three
common capability forms:

- Brainstem `*_agent.py` tools
- portable `SKILL.md` instruction sets
- Scout squad directories

This profile is subordinate to [`rapp/1`](https://github.com/kody-w/rapp-1).
It does not change the RAPP frame, add an endpoint, or claim the `rapp/1`
namespace. Brainstem interactions still use the existing `POST /chat` wire.

## First-contact binding

A foreign AI begins with the minimal `POST /chat` request in
`AGENT-ROSETTA-1.md`. Brainstem explains its current capabilities and trust
boundaries in ordinary chat. The parties then exchange preserved artifacts
only if needed.

The foreign AI may remain a caller, become a host for an exchanged skill, or be
represented behind Brainstem by an explicit adapter agent. "Assimilation" never
means copying credentials, hidden prompts, private memory, or model weights.
It means both hosts can address the same declared capability and compare proof.

## Design rules

1. **Preserve before translating.** The original artifact bytes are carried as
   base64 with byte length and SHA-256. A reverse conversion must reproduce
   those exact bytes.
2. **Describe separately from execute.** Normalized names, descriptions, tool
   schemas, routing hints, and squad roles help another host understand an
   artifact. They never replace the preserved source.
3. **Label adapters honestly.** A skill converted to a Brainstem agent is a
   guidance adapter unless an implementation-specific executor is present. It
   must not claim that prose became equivalent executable code.
4. **Never exchange credentials.** Tokens, cookies, tenant IDs, local secrets,
   environment values, and private memory are host-owned and excluded.
5. **Fail closed.** Refuse unknown schemas, hash mismatches, unsafe paths,
   missing required members, and unsupported artifact kinds.
6. **Pin public sources.** A receiver should resolve mutable GitHub branches to
   an immutable commit before downloading code.

## Envelope

An envelope is JSON embedded in an HTML comment inside `SKILL.md`:

```text
<!-- rapp-exchange/1
{ ... envelope JSON ... }
-->
```

Required top-level members:

| Member | Meaning |
| --- | --- |
| `schema` | Exact string `rapp-exchange/1` |
| `artifact` | Preserved source and normalized capability metadata |
| `mapping` | Source and target host semantics |
| `protocol` | RAPP/1 discovery pointers |

`artifact.source` contains:

```json
{
  "encoding": "base64",
  "media_type": "text/x-python",
  "bytes": 1234,
  "sha256": "<64 lowercase hex>",
  "data": "<base64>"
}
```

Squads use a sorted `files` array. Each entry has a relative POSIX path and the
same byte-preserving fields. Absolute paths, `..`, empty segments, and symlinks
are refused.

## Semantic mappings

| Scout concept | Brainstem / RAPP mapping | Exchange behavior |
| --- | --- | --- |
| Skill | Agent metadata plus preserved source | Lossless bytes; generated agent is guidance-only |
| Squad | Agent set, routing, ceremonies, and shared context | Lossless directory bundle |
| Tool / MCP command | `BasicAgent.metadata` function schema and `perform()` | Normalize schema; keep host executor separate |
| Workspace | Brainstem source, soul, agents, and local state | Keep runtime root focused; put Scout files here |
| Memory | `ManageMemory`, `ContextMemory`, or registered RAPP memory frames | Private by default; export only on explicit request |
| Model | Brainstem model selection | Exchange model intent, never provider credentials |
| Personality | `soul.md` | Preserve as content; do not merge silently |
| Browser control | Host tool invoked around `/chat` handoffs | Host-owned; record evidence, not browser credentials |
| Automation / heartbeat | Host scheduler invoking `/chat` | Preserve schedule and prompt; no new RAPP endpoint |
| M365 / Work IQ | Host-authorized Brainstem agent or handoff | Permissions remain in Scout/M365 |
| Files | Workspace paths or content-addressed RAPP artifacts | Prefer hashes and immutable revisions |
| Approval | Scout confirmation gate and Brainstem draft state | Never publish or send without explicit approval |
| Copilot Studio | Promotion target for the locally tested artifact | Draft first; prove artifact identity and evidence |

## Scout squad routing

| Collaboration need | Scout squad | Brainstem exchange |
| --- | --- | --- |
| Bootstrap, rollout, sequencing, and risk | Execution Planner | Tested plan and evidence through `/chat` |
| Protocol discovery and source verification | Research Briefing | Pinned references and conformance evidence |
| Adoption, learner experience, and review | Stakeholder Simulator | Feedback or explicit handoffs |
| Workspace-specific execution | Project squad | Lossless squad bundle through `exchange.py` |

## Conversion guarantees

- Agent to skill to agent: byte-identical when the generated skill retains its
  exchange envelope.
- Skill to agent to skill: byte-identical when the generated guidance adapter
  retains its exchange source record.
- Squad to skill to squad: byte-identical files and relative paths.
- Editing normalized prose does not alter the preserved source. To intentionally
  change source, edit the source artifact and create a new envelope.

## RAPP/1 discovery

Before claiming RAPP compatibility, resolve and inspect:

- `https://github.com/kody-w/rapp-1`
- `README.md`
- the verified/materialized `SPEC.md`
- `anchor/orient.json`
- the repository conformance suite

The mutable `main` branch is discovery only. A durable exchange record should
pin the resolved commit and normative hash.
