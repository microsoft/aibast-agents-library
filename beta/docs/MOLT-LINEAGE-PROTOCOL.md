# Molt Lineage — `molt-lineage/1.0`

Every on-device Brainstem is an **organism of one species**. It must adapt to the
device, the user, and the moment — mutating its own agents in real time — while
never losing the ability to return to a common, working baseline. Molt Lineage is
the contract that lets an instance become a **unique snowflake without getting
cancer, dying, or becoming a zombie**, and lets a fleet of such snowflakes always
come back together.

This is a **protocol, not a library**. It is downstream of the Brainstem
`CONSTITUTION.md` and the `rapp/1` spine; where they conflict, the kernel's law
wins. Amend by a PR that changes this file in the same commit as the behavior it
governs.

**Cardinal rule:** *the Grail baseline is never mutated in place.* Everything an
instance grows is an **additive overlay** composed onto that immutable baseline at
load time. If a change edits a baseline agent's bytes on disk, the pattern has
failed.

---

## Definitions

- **Genome / baseline (ring 0).** The pristine Grail factory agents on disk —
  the sacred three plus `basic_agent` — byte-for-byte identical on every instance,
  everywhere, forever. The species standard, the common ground, and the survival
  floor. Pinned in a **baseline manifest**: `ancestor_rappid → sha256 → source`.
- **Molt.** A mutation of exactly one agent, produced by growth (the Molter's
  `generate` / `mutate`) or dropped in by a person. It descends from one ancestor.
- **Ring.** One generation in an agent's lineage. Append-only; never deleted.
- **Frame.** A ring made portable: a self-contained snapshot (`source` +
  lineage metadata + `rappid` + `sha256`) that can be hot-loaded on its own. Every
  frame is a valid still of the organism at that generation.
- **Gene locus.** One agent's independent lineage. Each agent molts on its own
  timeline, at its own cadence, under its own policy — memory pinned at ring 0
  while news molts daily, or the reverse; it is per-agent and per-use-case.
- **HEAD.** The pointer, per gene locus, to the currently-live ring.
- **Ancestor rappid.** The lineage primary key — the baseline agent's minted
  `rappid`, identical across all instances (the cross-instance "same species" key).
- **Ring rappid.** A per-generation id, hash-chained to its parent:
  `ring_rappid = mintRappid(parent_rappid + sha256(source) + ancestor_rappid)`.
  Because each ring cryptographically commits to its parent and its bytes, the
  tree-rings are **tamper-evident** — a ring cannot forge its place in the lineage.

## The model

An agent's lineage is an **append-only, content-addressed log** (git-for-agents):
rings keyed and partitioned by `ancestor_rappid`, each ring naming its
`parent_rappid`, with a movable `HEAD`. Composition reads `HEAD` and lays down that
ring; growth appends a new ring and advances `HEAD`; nothing is ever overwritten.

Loci are **independent**: a bad molt in one agent can never touch another, and each
agent time-travels on its own axis.

## Composition — the "monkey-patch," done safely

The Frontier already materializes each worker's `AGENTS_PATH` by hardlinking-or-
copying agent sources (`route-manager.mjs` `hardlinkOrCopy`). That is the overlay
point. Per agent, materialization selects the **live ring**:

- if a *verified* molt sits at `HEAD` over the Grail ancestor, materialize that
  ring's frame;
- otherwise, materialize (hardlink) the **pristine Grail ancestor**.

The kernel then loads the composed directory and neither knows nor cares which
agents are molted. **Grail on disk is never touched.** Rollback is composition
choosing an earlier ring; there is nothing to un-edit.

## Benjamin Button — non-destructive time travel

Because the log is append-only and `HEAD` is a pointer, an instance can move
through its entire growth history at will:

- **Back:** walk `parent_rappid` from `HEAD` to any target ring, or jump straight
  to `ancestor_rappid` for the newborn baseline (O(1)).
- **Forward / fork:** point `HEAD` at a later ring (grow up again) or branch a new
  ring from any past ring.

Newborn → super-advanced → newborn, within a single chat, every frame valid. It is
reversible aging, and it is always available.

## The three deaths, and the safeguards against them

| Death | What it is | Safeguard |
|-------|-----------|-----------|
| **Cancer** | a malignant / fake-lineage / sterile mutation promoted as if healthy | the **fertility / compile gate** (below) + molt isolation |
| **Dying** | the instance is bricked and cannot run | **fail-safe composition** (never serve an unverified ring; fall back last-good → baseline) + rollback |
| **Zombie** | an agent that loads but is undead — broken, non-functional | **whole-set verification** at promote time + **proprioception** (Ambient Context surfaces a broken agent in chat) |

## The fertility / compile gate (the "TypeScript" step)

Dynamic composition at runtime is how a system gets JavaScript-style
"undefined is not a function" *in front of the user*. Molt Lineage forbids it:
**all risk is moved to a promote-time compile step, and runtime is a pure load of
an already-checked artifact.**

A ring is promoted to *live* only after passing an **isolated verifier**:

1. **AST verdict (trusted, unforgeable).** The parent *parses* the candidate — it
   never executes it — and passes it only if it statically (a) imports `BasicAgent`
   from the kernel base module and never rebinds that name (the base is the genuine
   kernel class, not a `BasicAgent = object` decoy), (b) defines a class
   subclassing it, and (c) that class defines its own `perform()` — **a molt that
   cannot act is sterile and is refused.** This is the fertility check.
2. **Correctness signal (advisory).** A disposable subprocess imports and
   instantiates the candidate; the parent reads only its **exit status**, never any
   byte it writes. A candidate cannot forge a pass through what it prints, an
   inherited fd, or `os._exit()`.
3. **Whole-set validation.** Before a composed `AGENTS_PATH` goes live, the entire
   set (baseline + every live overlay) is dry-loaded together: no duplicate tool
   names, no import collisions, every agent instantiates. Interactions are checked,
   not just individual files.
4. **Atomic blue-green swap.** The new set is built in a staging directory,
   validated, and only then swapped in **between** requests — never mutated in
   place while serving. A half-composed state never reaches a user; if validation
   fails, the current good set keeps serving.

Reference implementation of the AST verdict + isolated correctness signal:
`_verify` / `_ast_agent_verdict` in
`beta/frontier/rapplications/molter/agents/molter_agent.py`.

## Reproduction — no mules, no lethal inheritance

- **Single lineage.** Every ring descends from exactly one `ancestor_rappid`; the
  lineage marker is conserved through every generation. Two different ancestors are
  never fused into one agent — no horse × donkey, so no sterile mule can be born.
- **Fertile parents only.** The gate confirms each live ring is itself a valid,
  mutatable parent — so reproduction never carries a dead-end.
- **Safe inheritance.** When an instance seeds a twin or rapplication, the
  offspring inherit only *verified* live rings plus the Grail baseline — never an
  unverified or failed molt. And the offspring's own materialization re-applies the
  fail-safe rule, so even a bad inherited reference falls back to Grail rather than
  bricking the seed. A bad mutation can never end the line: it goes back to Grail
  and keeps living.

## The dream catcher — reassimilation at scale

Local devices grow their own frame-films independently — a hive of snowflakes.
The **dream catcher** merges local frames back into the collective:

1. **Verified ingest.** Only frames that pass the fertility gate are reassimilated
   — the gate applies on the way *in*, not just on the way out.
2. **Merge by shared ancestry.** Because every frame is keyed by `rappid` and
   rooted at the shared `ancestor_rappid`, lineages that share an ancestor can be
   compared and merged; the hash-chain makes merges verifiable.
3. **Branch, never force-cross.** Lineages that cannot merge cleanly stay as
   branches off the shared ancestor — never force-crossed into a hybrid.
4. **Baseline is the convergence point.** However far the hive diverges, the Grail
   baseline is identical everywhere, so any two instances can *always* come back
   together by Benjamin-Buttoning to the common ancestor, then re-applying
   compatible frames. Convergence is always available, even if a branch is abandoned.

## Layering over a Grail brainstem — the passthrough contract

Molt Lineage is a **big release that must not break a simple Grail brainstem.** The
layer is additive and **inert by default**: with no molts it does nothing, and a
plain Grail brainstem — even one with no lineage store, no baseline manifest, and
no Frontier around it — boots and chats exactly as it does bare. Grail is a black
box the layer feeds a valid `AGENTS_PATH`; it never modifies the kernel or its
agent-loading contract.

1. **Transparent passthrough.** The layer overlays bytes only for an agent it has
   an explicit *verified* live molt for. Every other agent — including ones it has
   never seen — passes through untouched: never dropped, renamed, or reordered. It
   can only ever substitute, never subtract from, what Grail would have loaded.
2. **No-op with no molts.** An empty/absent/corrupt lineage store yields a composed
   `AGENTS_PATH` byte-identical to today's factory compose. Source selection happens
   before content-addressing, so the composition hash reflects exactly what shipped.
3. **Kill-switch.** One environment flag forces pure Grail passthrough — total,
   redeploy-free rollback of the whole layer if anything smells wrong in the field.
4. **Fail-safe degradation.** Any store error, corrupt ring, or failed whole-set
   validation falls back to the pristine baseline = current behavior. The layer can
   never make an instance *worse* than bare Grail.
5. **Realized safely.** Source selection is hash-aware (so the cache and fingerprint
   stay correct); byte placement is physical only. The composed directory is built
   in staging, whole-set dry-loaded, and swapped in atomically between requests —
   a half-composed set never reaches a running kernel.

## Enterprise ALM — environments, promotion, and drift

A molt made directly in production that dev never sees, then a dev promotion built
on a different base, must not "break at literally the worst time." Content-
addressing is what prevents it: because `ring_rappid` is deterministic, the *same*
molt has the *same* rappid in every environment, so divergence is detected exactly.

1. **Environments are HEADs, not copies.** dev, staging, and production each pin
   their own `HEAD` per gene locus into the *same* content-addressed ring store.
   Rings are environment-independent; "the same molt" is one object everywhere.
2. **Promotion is a gated three-way merge.** Promote = advance the target
   environment's `HEAD` toward the source's, checked against their common ancestor.
   **Fast-forward only** when the target has not diverged. If the target holds a
   ring the promotion did not build on (a production-only molt), it is a
   **CONFLICT → refuse**, naming the diverging rappids and requiring explicit
   reconciliation (rebase the production molt onto the new base, or a deliberate,
   recorded override). Never a silent overwrite — branches do not force-cross, the
   same "no mule" law applied across environments.
3. **Drift is detected before promotion.** The target's live ring rappids are
   compared against the base the promotion expects; any unexpected ring is drift and
   the promotion refuses with a precise diff — not a runtime surprise.
4. **Fail at promote, not at runtime.** The whole-set dry-load validation runs
   against the *resulting* target composition at promotion time (in a staging
   materialization). A break surfaces before the production swap; "the worst time"
   becomes "the promotion refused, and here is why."
5. **Tamper-evident audit trail.** Hash-chained rings plus an immutable promotion
   record (from/to `ring_rappid`, environment, actor, UTC) give ALM a verifiable
   history of every change that reached each environment.

## Laws

1. **The genome never drifts.** Baseline agents are immutable on disk; all growth
   is additive overlay. Instance-level variation is unbounded; species-level
   drift (baseline mutation) is forbidden.
2. **One lineage per ring.** A ring descends from exactly one ancestor; ancestors
   are never fused.
3. **Fertility gate.** A ring is promoted only if it is a valid, actable,
   genuinely-descended agent. Sterile and fake-lineage molts are refused.
4. **Compile before run.** All verification is promote-time and isolated; runtime
   is a read-only load of a pinned, pre-validated artifact. No hot-mutation of live
   modules.
5. **Fail-safe composition.** Only verified rings go live; composition falls back
   last-good → baseline; the composed set is always loadable.
6. **Non-destructive log.** Rings are append-only and content-addressed. History is
   never rewritten; the baseline is always reachable.
7. **Verified ingest.** Reassimilation carries only verified frames; un-mergeable
   lineages branch, they do not force-cross.
8. **Inert over Grail.** The layer is passthrough by default and requires none of
   its own machinery to exist; with no molts a plain Grail brainstem is unaffected,
   and any failure degrades to bare-Grail behavior. It substitutes, never subtracts.
9. **Promotion is gated, never forced.** Crossing an environment boundary is a
   three-way merge against a common ancestor: fast-forward or refuse-with-a-diff.
   Drift and conflicts fail at promotion time, never at runtime.

## Cross-references

- `CONSTITUTION.md` — Article I (the sacred three + molt isolation: molts live
  only in isolated twins, never the sacred Brainstem) and Article II (organs and
  senses).
- `AMBIENT-CONTEXT-PROTOCOL.md` — the proprioception layer that surfaces a broken
  or bricked agent in chat (the anti-zombie sense).
- `UI-AUTOSTEER-PROTOCOL.md` — the sibling protocol for driving an application
  through its surface.
