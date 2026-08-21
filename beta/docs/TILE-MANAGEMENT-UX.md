# Managing tiles: pick one up, put it down

This is the interaction guide for rappid tiles in the Frontier. It is deliberately small, because the
whole point is that there is almost nothing to learn.

## The principle

**People already know how to move a physical tile.** You pick it up, you put it somewhere, and where
you put it is what happens. Agent management piggybacks on that: no menu to find, no button to
discover, no vocabulary to memorise. If a person can move a coaster across a table, they can manage
a fleet of agents.

That is an accessibility position, not a decoration: the cheapest interface to teach is the one the
body already knows. It scales because nothing new has to be explained as the number of tiles grows.

## The four surfaces

| Surface | What it is | State of tiles on it |
|---|---|---|
| **The Brainstem chat** | the big window — **this is a tile too**, the primary one: the companion currently loaded | active, running |
| **The herd** (default view) | every tile you have parked, side by side | parked, ready |
| **The arena** | the same tiles arranged to compete on a task | parked, competing |
| **The binder** | the tile keeper — where tiles you are not using are stored and organised in bunches, like a binder of pages | dormant, stored |

The herd and the arena are two views of one set. The binder is storage: nothing in it is running.

## Why you would move a tile at all

**Only the primary tile is running.** The Brainstem loads one companion; everything else sits
dormant — no worker, no port, no cost. That is the point of moving tiles rather than loading
agents: a person can keep many capabilities without paying for all of them being live, and reach
for one by dragging it in.

**The drag is the load.** A tile carries its agents, so dropping it on the chat composes those
agents into the Brainstem worker and dropping it back out takes them away again. Hot-loading stops
being an operation a person performs on a system and becomes a place they put a thing.

So tiles are kept in **bunches** — small groups a person makes for their own reasons: the ones for
this customer, the ones for this week, the ones that are competing on a task. A bunch is made the
same way everything else happens here: drag one tile onto another and they bunch; drag a tile out
and it leaves. Bunches live on any surface, and the binder is where the ones you are not using
right now are kept.

Nothing about a bunch changes what a tile *is*. It is organisation, and organisation is free:
grouping never starts a worker, never touches a conversation, and never changes which tile is
primary.

## The gestures, and exactly what each does

### 1. Drag the Brainstem chat → herd, arena, or binder
The conversation becomes a tile on that surface, and **the Brainstem opens a fresh chat.** Nothing is
lost and nothing is asked: the thing you were talking to is now a tile you can see.

### 2. Drag a tile → the Brainstem chat
**This drop is the hot-load.** The tile's agents are composed into the running Brainstem and its
conversation is restored: dropping is how a capability gets into the primary window — there is no
separate install step, no menu, no restart. What happens to what was already there depends on
whether there *was* anything:

- **The chat has a conversation → the two swap.** The incoming tile becomes primary; the outgoing
  conversation becomes a tile *in the place the incoming one came from*. A swap, exactly as it looks:
  two objects trading places.
- **The chat is blank → it just loads.** Nothing is parked, because an empty chat is not worth
  keeping. No empty tiles are ever created.

### 3. Drag a tile between herd, arena, and binder
It moves. Nothing about the conversation changes — this is organisation, not state.

### 4. Drag a tile onto another tile
They bunch. Drag one out of the bunch and it leaves. A bunch is a group a person made, nothing
more: no worker starts, no conversation changes, no tile becomes primary.

### 5. Drop a `.tile` file from the operating system onto the window
It is verified and added, the same way dropping an `agent.py` onto the Brainstem installs an agent.
The gesture is already in the product; tiles reuse it rather than inventing a second one.

## Rules that hold for every gesture

1. **Nothing is lost.** Every move preserves the conversation it carries *and* the agents it
   carries. A swap parks the outgoing side — conversation and agents together — before the incoming
   side loads.
2. **The drop target says what will happen** before the person lets go — the surface highlights and
   names the outcome ("Make primary", "Park as a tile", "Keep in the binder", "Swap with this chat"),
   using the same dashed-overlay affordance the Brainstem already uses for dropping an `agent.py`.
3. **No gesture requires a button.** There is no Park button, no Wake button in the flow. Buttons may
   exist for *destructive* or *rare* actions, never for movement.
4. **Every gesture has a keyboard path and a driver handle.** Drag is the primary gesture, not the
   only one: a person using a keyboard or assistive technology, and an AI driving the window, both
   move tiles the same way. A pointer-only design would exclude the people this is meant to include.
5. **Empty is not a state worth keeping.** No empty tile, no empty swap, no placeholder.

## Why this is core, not cosmetic

The Frontier's promise is that a person can hold several capabilities at once and move between them
without ceremony. Menus make that cost grow with the number of agents; picking things up does not.
The tile is the unit precisely because it is a thing you can move — a surface a rappid stands on, and
therefore something a hand can carry from one place to another.

## Proof obligations

A conforming implementation demonstrates, driven end to end: dropping a tile on the chat composes
its agents into the running Brainstem (they appear in `/health` and are callable in the next turn)
and dropping it back out removes them; the chat dragged to the herd becomes a tile and leaves a
fresh chat behind; a tile dragged onto a chat that has a conversation swaps the two
and loses neither; the same drag onto a blank chat loads without creating an empty tile; a tile moved
between herd, arena and binder keeps its conversation intact; and every one of those moves is also
reachable from the keyboard and from the UI driver.
