# git-molt — version control for autonomous agents

> Git for agents. Not a reimplementation of Git — a set of conventions *on top
> of* it, so agent lineage inherits everything Git already guarantees.

Agents have begun to modify themselves: rewriting their own tools, accepting
generated code, adapting per device and per user — increasingly without a human
reading the diff. That creates four problems every platform hits in the same
order:

| Problem | What it looks like in production |
|---|---|
| **Divergence** | Every deployed instance is different. Nothing reproduces. |
| **No floor** | A bad self-modification has nothing to fall back to. |
| **No provenance** | Nobody can say what a running agent descended from. |
| **No interchange** | An adaptation learned on one instance can't move to another. |

These are version control problems, and Git solved them in 2005.

## The idea

`git-molt` represents agent lineage as an ordinary Git repository:

| Concept | Git object |
|---|---|
| Generation ("ring") | a **commit** |
| Agent lineage ("locus") | a **ref** — `refs/molt/loci/<locus>` |
| What's running now | a **ref** — `refs/molt/live/<locus>` |
| Factory baseline (ring 0) | the **root commit** — `refs/molt/base/<locus>` |
| Portable frame | a **bundle** |
| Verification verdict | a **commit trailer** (inside the commit hash) |
| Tamper-evidence | Git's Merkle DAG |
| Replication | `fetch` / `push` |
| Authorship authenticity | Git commit signing |

Everything Git already does well, we don't do at all. What we add is the part
Git has no opinion about: **a verification gate between commit and checkout**
(agents can't assume a human reviewed), **a guaranteed floor** every instance
shares, and **a composition contract** for handing a resolved generation to a
live, lineage-unaware runtime.

Spec: [`gitprotocol-molt(5)`](../beta/docs/RAPP-LINEAGE-STANDARD.md).

## Install

```sh
cp bin/git-molt /usr/local/bin/      # anywhere on PATH
git molt version                     # git finds git-* as a subcommand
```

Zero dependencies beyond Git itself (2.x; SHA-256 repositories are used when
available).

## Use

```sh
git molt init

# Record the factory agent. The locus id is DERIVED from name + content, so the
# same agent gets the same id on every machine in the world.
LOCUS=$(git molt baseline memory ./memory_agent.py)

# An agent adapts. Recording is always allowed; activating is not.
RING=$(git molt record $LOCUS ./memory_agent.v2.py)
git molt activate $LOCUS $RING          # refused: unverified

# Gate it. Your verifier decides — the candidate never emits its own verdict.
VERIFIED=$(GIT_MOLT_VERIFIER=./my-gate.sh git molt verify $LOCUS $RING)
git molt activate $LOCUS $VERIFIED      # now it's live

# Materialize what the runtime loads. Fail-safe: anything unverified,
# missing, or pinned resolves to the baseline instead.
git molt compose ./agents

# Time travel. Non-destructive — history is append-only.
git molt revert                          # every locus back to factory
git molt restore                         # forward again

# Freeze one agent for life while its siblings keep adapting.
git molt policy $LOCUS pinned

# Move an adaptation to another instance.
git molt frame export $LOCUS memory.frame
git molt frame import memory.frame       # imported ≠ trusted; verify to activate
```

Because it's just Git:

```sh
git --git-dir=~/.molt/lineage.git log  refs/molt/loci/$LOCUS   # generation history
git --git-dir=~/.molt/lineage.git diff  $BASE $RING            # what the agent changed
git --git-dir=~/.molt/lineage.git bisect start                 # find the bad generation
```

## Guarantees

- **Substitute, never subtract.** An instance running `git-molt` is never less
  capable than the same instance without it. Every failure path degrades to the
  runtime's native behavior.
- **Zero-adaptation identity.** With no molts, the composed directory is
  byte-identical to what you'd have without this tool. Adoption is a no-op until
  something actually changes.
- **Fail-safe composition.** Missing, corrupt, unverified, or pinned all resolve
  to the baseline. Composition cannot fail.
- **Code, not data.** Reverting restores factory *behavior*; it never touches
  agent memory or user data. That's what makes reversal safe to expose to end
  users.
- **The verdict is the verifier's.** A candidate cannot forge its own pass, and
  the verdict lives inside the commit hash — editing it orphans every descendant.

## Tests

```sh
bash t/t0001-molt.sh     # 33 assertions against a real repository
```

Covers determinism across unrelated instances, gate refusal, tamper-evident
verdicts, pinning, non-destructive reversal, fail-safe composition, bundle
interchange, and native `git log` / `diff` / `fsck` compatibility.

## Status

Draft standard, working reference implementation. The first production use case
is Molt Lineage in the RAPP Brainstem Frontier — see
[`MOLT-LINEAGE-PROTOCOL.md`](../beta/docs/MOLT-LINEAGE-PROTOCOL.md).

Implementations, critiques, and profile registrations are welcome. MIT licensed.
