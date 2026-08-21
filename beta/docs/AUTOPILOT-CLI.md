# Autopilot — a headless CLI inside the page

**The Brainstem's intelligence is expensive; its user interface is not.** Opening the herd, switching
to the arena, parking a tile, reading the transcript — none of that needs a model. Today an AI that
wants to do those things often asks the Brainstem in chat, which spends a model call (and tool
rounds) on a button click.

Autopilot is the deterministic half: **a CLI injected into the frame and driven from the console**,
so an AI operates the interface exactly as a person would, for free, and reaches the model only when
it actually needs intelligence.

There is no terminal window. The "CLI" is a shape — verbs, arguments, text results — because that
shape is what an AI drives well and a person can read.

## How it is driven

The Frontier already injects controllers into frames (`executeInFrame` in
`beta/electron/ui-driver-server.mjs`) and the UI already carries stable `data-drive` handles. Autopilot
adds one global to each driven frame:

```js
// evaluated in the frame — the console, executeJavaScript, or the driver bus
await rapp("herd.open")
await rapp("tile.park")
await rapp(`
  arena.switch
  tile.primary tile-7
  chat.read --last 1
`)
```

`rapp(script)` takes one command per line, runs them in order, stops at the first failure, and
returns a JSON result — never a rendered string to be parsed back:

```json
{ "ok": true, "ran": 3, "results": [ { "cmd": "arena.switch", "ok": true, "view": "arena" } ] }
```

It also `console.log`s a one-line summary per command, so a human watching the console sees exactly
what an AI did, in order — the same evidence trail the driver's traces already keep.

## The command surface

Nouns are the surfaces; verbs are what a person can do to them. Everything here is deterministic —
no model, no network beyond the app's own loopback.

| Command | Does | Costs a model call |
|---|---|---|
| `herd.open` / `arena.switch` / `binder.open` | show a surface | no |
| `herd.list` / `arena.list` / `binder.list` | the tiles on a surface, with ids | no |
| `tile.park [--to herd\|arena\|binder]` | park the current chat as a tile | no |
| `tile.primary <id>` | make a tile primary — hot-loads its agents, restores its history | no |
| `tile.move <id> --to <surface>` | move a tile between surfaces | no |
| `tile.bunch <id> <id>` / `tile.unbunch <id>` | group and ungroup | no |
| `tile.fold <id>` / `tile.undo` | fold, and take it back | no |
| `chat.read [--last N]` | read the transcript | no |
| `chat.type <text>` | put text in the composer without sending | no |
| `ui.inspect [--target shell\|brainstem]` | the operable outline, capped | no |
| `ui.click <handle>` / `ui.press <key>` | the raw fallback for anything unnamed | no |
| `ui.wait <handle> [--text …]` | wait for a condition | no |
| **`chat.send <text>`** | **ask the Brainstem — the model runs** | **yes** |

That table is the point of the whole document: **one row costs money.** If a task can be expressed
with the others, it should be.

## Built for other AIs, not for one of them

The point of a CLI shape is that **any** AI can drive this — GitHub Copilot, another Claude, a local
model, a script — without reading this document, without a client library, and without asking the
Brainstem. That imposes requirements the surface has to meet:

**1. It describes itself in one call.** `rapp("help")` returns the whole command surface as JSON:
every verb, its arguments, its types, whether it costs a model call, and one example each. An AI
learns the interface at runtime instead of being taught it.

```json
{ "version": "rapp-autopilot/1.0",
  "commands": [
    { "cmd": "tile.primary", "args": [{"name":"id","type":"tile-id","required":true}],
      "costs_model": false, "example": "tile.primary tile-7",
      "does": "make a tile primary — hot-loads its agents and restores its history" }
  ] }
```

**2. The bootstrap is one paste-able block.** Nothing to install:

```js
// read the endpoint the app publishes, then drive it
const meta = JSON.parse(fs.readFileSync(`${home}/.brainstem/beta-launcher/ui-driver.json`));
await post(meta, { action: "run", steps: [{ action: "autopilot", script: "help" }] });
```

**3. Errors teach.** An unknown verb returns the nearest valid one and the help entry for it, never
a stack trace: `unknown command "tile.make" — did you mean "tile.primary"? …`. A wrong argument says
which argument and what it accepts. An AI recovers on the next turn instead of falling back to chat.

**4. State is readable, so a driver can orient.** `herd.list`, `arena.list`, `binder.list` and
`ui.inspect` let an AI see where things are before acting, so it never has to guess a tile id or
whether a surface is open.

**5. The vocabulary matches the documentation a person reads.** The verbs are the gestures in
[`TILE-MANAGEMENT-UX.md`](TILE-MANAGEMENT-UX.md) — park, primary, move, bunch, fold. One vocabulary
for the person, the AI, and the tests.

**6. It is discoverable from inside the product.** The same `help` output is what the Brain Surgeon
is told about at startup, so an AI already in the window knows the free path exists before it spends
a model call on a button.

## Laws

1. **No arbitrary code.** `rapp()` accepts allowlisted verbs and validated arguments only. It never
   evaluates caller-supplied JavaScript — an injected CLI that can run anything is not a CLI, it is
   a hole.
2. **Deterministic or nothing.** Every command either performs its effect and reports it, or fails
   with a reason. No command asks a model to interpret intent.
3. **Same surface a person uses.** Commands drive the real controls and the real handles. If a
   person cannot do it in the interface, autopilot cannot do it either.
4. **Bounded and observable.** Every command is capped in time and output, logged to the console,
   and recorded in the driver trace — the existing budgets and traces apply unchanged.
5. **One way in.** Autopilot is a thin naming layer over the existing driver actions; it does not
   fork a second control path or a second security model. The loopback token still guards the bus.
6. **The model stays reachable.** `chat.send` exists precisely so an AI can hand over when it needs
   intelligence — the point is to make that a decision, not a default.

## Why this shape

- **A console-injected CLI needs no window, no port and no client.** One evaluated expression drives
  it; that works from the driver bus, from DevTools, from an automated test, and from an AI with a
  single tool call.
- **Verbs are cheap to learn and cheap to emit.** An AI writes `tile.primary tile-7` reliably; it
  writes a DOM traversal unreliably.
- **It degrades to the raw driver.** Anything without a verb is still reachable through `ui.click`
  and friends, so the layer never becomes a ceiling.

## Proof obligations

Driven end to end, with the model provably not invoked: a navigation sequence (open the herd, switch
to the arena, park a tile, make another primary, read the transcript) completes through `rapp()`
alone, and the model-request count for the session stays at zero; `chat.send` increments it by
exactly one; a malformed or non-allowlisted command is refused without side effects; and every
command appears in the driver trace with its result.
