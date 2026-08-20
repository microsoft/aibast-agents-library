# Live proofs — 2026-08-20

Evidence, not claims. Each entry is something exercised on a real artifact,
with what was observed. "Unverified" means exactly that.

## Fresh Grail, isolated HOME (the handoff's §5 recipe)

Installed `install.sh` from `main` under a throwaway `HOME`; kernel 0.6.16 on
:7098.

| Step | Observed |
|---|---|
| baseline `/health` | `agents: 4, quarantined: 0` |
| drag every Frontier agent in (+ ring-1 ContextMemory) | `/health`: **9 agents, `quarantined: []`**; `/chat` listed all nine tools |
| drop a broken `weather_agent.py` (class that is not a `BasicAgent` subclass), ask "what is 2+2?" | reply: *"2 + 2 = 4. ⚠️ Agent issue: Your `weather_agent.py` failed to load because it doesn't define a `BasicAgent` subclass — it's not available as a tool…"* — Ambient Context volunteered it unprompted |
| drop an agent with module-level `os._exit(0)`, hit `/health` | **process dead** (curl rc 52) — the going-home law's teeth |

## Windows (the lab branch on the fork, windows-latest)

| Step | Observed |
|---|---|
| A — as checked out (`.gitattributes` pin in effect) | ring-1 LF, Grail CRLF; seed + verify + overlay OK; `node --test tests/molt-lineage-integration.test.mjs` **21/21** |
| B — forced CRLF ring-1 and CRLF Grail (an older checkout's shape) | `ring1 has CR: true`; seed + verify + overlay OK; HARD 3 green |
| C — full beta suite | **221/221** on Windows |

## Safe words typed into the real chat window (handoff §6.1 gap)

Branch Frontier launched against the live kernel with an isolated lineage root;
words typed into the Grail composer through `/drive`; HEAD files read from disk
after each.

| Word | Reply | On disk |
|---|---|---|
| (fresh home) | — | ring-1 ContextMemory seeded at HEAD |
| `baseline` | *Reverted to Grail baseline — your memories are intact.* | `HEAD` = ancestor (baseline), `PRIOR_HEAD` = ring-1 |
| `restore` | *Restored the latest verified molts — your memories are intact.* | `HEAD` = ring-1 |
| `environments` | *Molt Lineage environments: … context_memory_agent.py: default → ring …* | — |
| `promote default prod` | fast-forward | `HEAD.prod` = ring-1 |
| `baseline` again | reverted | default at baseline, **`HEAD.prod` unchanged** |

## Streaming delivery timelines (branch Frontier, live kernel, `/drive` sampling)

| Build | Typing bubble | Reply growth | First text | Done |
|---|---|---|---|---|
| kernel-native | yes (bounce) | **12 steps of 96–240 chars every ~0.53–1.5 s** (median ~0.76 s) | 3.6 s | — |
| hold-and-pop (built, then declined: "I want it to stream in") | yes | **1 step: the whole 1,604-char reply** | 11.8 s | 11.8 s |
| smooth v1 — paced kernel wire | pulse | **six visible growth steps** for a 1,683-character reply, including `+22`, `+431`, `+216`, `+68`, and `+600` after the initial paint, separated by 1–2 s gaps; kernel unresolved-Markdown structural gating caused the lumps | ≈ kernel | — |
| smooth v2 — Frontier provisional renderer | pulse | **27 visible growth steps for 1,658 characters** | 3.6 s | 11.7 s |
| smooth v2 on the final merged tree (`94436b6c`) | pulse | **27 growth steps for 1,638 chars** (median +59 chars per ~300 ms sample), provisional bubble rendered by the bridge, kernel bubble swapped in at the end; Messages look default | 2.6 s |

The deterministic v2 VM proof separately covers zero kernel bytes before
terminal, at least 40 monotonic provisional renders for 1,600 characters,
byte-identical replay, and a single handoff/removal.

## Chat look

| Build | Observation | Status |
|---|---|---|
| Messages look | Messages is the default across Brainstem, Brain Surgeon, and twin chats; Business remains a theming-only toggle. | Captured |

## Unverified

- `frontier.ps1`'s token/`git ls-remote` fallback (no PowerShell on the proving
  machine; `frontier.sh` verified in all three modes).
- The Electron composition overlay / atomic swap / kill switch driven through
  the UI (unit- and integration-tested; the regression harness will drive them).
