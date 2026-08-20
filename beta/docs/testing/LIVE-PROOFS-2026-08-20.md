# Live proofs — 2026-08-20

Evidence, not claims. Each entry is something exercised on a real artifact, with what was
observed. "Unverified" means exactly that.

## Fresh Grail, isolated HOME (the handoff's §5 recipe)

Installed `install.sh` from `main` under a throwaway `HOME`; kernel 0.6.16 on :7098.

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

Branch Frontier launched against the live kernel with an isolated lineage root; words typed into
the Grail composer through `/drive`; HEAD files read from disk after each.

| Word | Reply | On disk |
|---|---|---|
| (fresh home) | — | ring-1 ContextMemory seeded at HEAD |
| `baseline` | *Reverted to Grail baseline — your memories are intact.* | `HEAD` = ancestor (baseline), `PRIOR_HEAD` = ring-1 |
| `restore` | *Restored the latest verified molts — your memories are intact.* | `HEAD` = ring-1 |
| `environments` | *Molt Lineage environments: … context_memory_agent.py: default → ring …* | — |
| `promote default prod` | fast-forward | `HEAD.prod` = ring-1 |
| `baseline` again | reverted | default at baseline, **`HEAD.prod` unchanged** |

## Streaming delivery timelines (branch Frontier, live kernel, `/drive` sampling)

| Build | Typing bubble | Reply growth | First text |
|---|---|---|---|
| kernel-native (today) | yes (bounce) | **12 steps of 96–240 chars every ~0.53–1.5 s** (median ~0.76 s), each wiped in with the masked reveal | 3.6 s |
| hold-and-pop (built, then declined: "I want it to stream in") | yes | **1 step: the whole 1,604-char reply at 11.8 s** | 11.8 s |
| smooth (in progress) | pulse | target: word-sized steps at a steady ~30 ms cadence, tail always above the bar | ≈ kernel |

## Unverified

- `frontier.ps1`'s token/`git ls-remote` fallback (no PowerShell on the proving machine; `frontier.sh` verified in all three modes).
- Visual appearance of the smoothed stream (caret, pulse, glide) until the live capture after the build lands.
- The Electron composition overlay / atomic swap / kill switch driven through the UI (unit- and integration-tested; the regression harness will drive them).
