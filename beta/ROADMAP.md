# Frontier roadmap — what is real, what is decided, what is next

Written so the thread survives a lost conversation. If you are picking this up cold, read
[`CONSTITUTION.md`](CONSTITUTION.md), then [`GOLDEN_PATH.md`](GOLDEN_PATH.md), then this.

## 1. Built and verified

| | Evidence |
|---|---|
| Tiles: herd, arena, binder; drag and drop; the drop that hot-loads; swap-versus-load; bunching; fold with undo | unit + e2e suites |
| `rapp-autopilot/1.0` — `rapp()`, 21 verbs, both calling shapes, real drag gestures through the renderer's own drop handler, yields a contested tile | `beta/tests/autopilot.test.mjs`; removing the drop handler makes `tile.move` fail |
| The chat lease is a witness, not a blocker — a trusted interaction reclaims the composer and nothing is ever prevented | no `preventDefault` remains in `ui-driver-server.mjs` |
| Driver request-slot correlation — a person's reply can no longer be serialised into the model's tool result | lease suite |
| Attribution — a driver's change stamps the tile instead of toasting, decided by `event.isTrusted` | `beta/tests/tile-attribution.test.mjs` |
| Driver steps are out of the chat transcript, on a click-through strip, off by default | `beta/tests/activity-view.test.mjs` |
| Driven runs do not steal focus (`showInactive`, accessory policy) | `beta/tests/driven-focus.test.mjs` |
| Injected bytes declare themselves | `beta/tests/injection-banner.test.mjs` |
| The generated agentic app checks its embedder's origin and correlates command ids | `beta/tests/agentic-bus-conformance.test.mjs` |
| The media organ is probed before recording spawns | `beta/tests/media-organ.test.mjs` |

## 2. Specified, not built — in dependency order

Build downward; each depends on the one above it.

1. **`stands_on` is read and enforced** — the footprint check in front of composition. Nothing else
   in the protocol family means anything until a runtime can refuse. ([SELF-ASSEMBLE-PROTOCOL](docs/SELF-ASSEMBLE-PROTOCOL.md))
2. **A runtime publishes its `supports` set** — the other half of the intersection. ([PROTOCOLS](docs/PROTOCOLS.md))
3. **The `.tile` producer** — RAR still emits `.card` into `cards/v2/`. Migration must preserve seed,
   face and seven-word key exactly. ([RAPPID-TILE-PROTOCOL](docs/RAPPID-TILE-PROTOCOL.md))
4. **The kit roles** — `agent` payloads, all-or-nothing assembly, identity over the whole set.
5. **The flag checker** — without it a drill has nothing to collapse on. ([DIMENSION-MINING](docs/DIMENSION-MINING.md))
6. **`rapp-qqdrill/1.0`** — isolation, external grading, escape prevention, budget. ([QQDRILL-PROTOCOL](docs/QQDRILL-PROTOCOL.md))
7. **Chant addressing and channel subscription** — step 4 of the summon path. ([SUMMON-PROTOCOL](docs/SUMMON-PROTOCOL.md))
8. **One-time seals** — no seal is stored or read today. ([ONE-TIME-SEALS](docs/ONE-TIME-SEALS.md))
9. **Crystals** — the wear metric needs a computable definition before anything renders one. ([CRYSTALS](docs/CRYSTALS.md))
10. **Voice** — none of it exists. ([VOICE](docs/VOICE.md))
11. **The flock surface and exportable presets.**
12. **Recap export** and the local model player.

## 3. Decisions — do not re-litigate these

Each was argued and settled. The reason is recorded so it does not have to be rediscovered.

| Decision | Because |
|---|---|
| **Herd stays, and the flock is added** as a separate surface | A herd is tended and a grid is for finding; a flock moves together and a space is for seeing a group. Both are true of different views, and having both costs no rename. |
| **The station ident stays** | Accepted deliberately, with the tradeoff understood. It costs nothing, blocks nothing, carries nothing, and buys character. Dropping it is a decision someone makes on purpose and records here. |
| **`rapp-qqdrill`, with the doubled q** | A typographic mark — `ra`**`pp`**`-`**`qq`**`drill` doubles descenders so the word reads as dripping. Deliberate, and the protocol says so, which is what stops it reading as a typo. |
| **Injected payloads are declared data objects, never bytecode** | Data can be logged, diffed, schema-checked and refused before it runs. Fail-closed is unavailable for a blob already handed to an interpreter. |
| **Tiles self-assemble; eggs hatch** | Hatching is one-way and consumes the container. Tiles move in and out constantly, so the lifecycle word must be repeatable, reversible, and able to refuse without having consumed anything. |
| **Driver actions never appear in the chat transcript** | Deterministic driving never reaches the model, so narrating it there records a conversation that did not happen. |
| **A driver's action never toasts; attribution rides on the object** | Two hands on one window must stay legible without writing into the conversation. |
| **Winning a drill confers promotion, not experience; training confers wear** | The crystal measures what the tile still needs. Training is real wherever it happened; a flag captured is not. Lineage records used-versus-drilled so neither can pretend to be the other. |
| **The client is the extension point; the kernel gains nothing** | Adding a command must never require a commit to `rapp_brainstem/`. |
| **Only `chat.send` costs a model call** | The invariant the whole command surface exists to provide. (Under repair: `ui.click`/`ui.press` can reach the model and must report when they did.) |

## 4. Known live inconsistencies

- **`stands_on` is specified and unenforced** — a tile that should refuse to assemble will assemble.
- **`ui.click` / `ui.press` advertise `costs_model: false` and can reach the model** — under repair.
- **The lease's claim against *other automation* is not enforced** — only the keystroke reclaim is.
- **A lowercase `s` is replaced by a space when a driver step summary is rendered into the page.**
  Traces on disk are clean, so it is a render-path defect; the symptom is hidden because steps no
  longer render into the chat. Root cause unproven. Do not mark fixed.
- **The Grail ships a fourth agent** (`rar_rapp_learn_new_agent.py`) that writes generated
  `*_agent.py` into the sacred agents directory, contradicting Article I twice. Kody's call; not to
  be fixed from the Frontier side.

## 5. Standing constraints

- Everything Frontier lives under `beta/`; the mainline never links it.
- `rapp_brainstem/` stays byte-identical. Verified per push.
- Never push to `microsoft/*` or to the Grail. Work lands on the fork branch.
- Do not launch Electron while Kody is at the machine — driven runs are focus-safe now but the
  e2e suite has not been re-verified live.
- Regenerate `beta/frontier/store/index.json` after touching any rapplication's bytes.
