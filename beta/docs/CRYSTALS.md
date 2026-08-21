# Crystals — the tile wears down as you master it

Every rappid tile carries a **crystal**. It runs backwards from how progression usually works, and
the inversion is the whole idea.

**The newest tile has the largest crystal. Use wears it down. A master's crystal is a nub.**

## Why backwards

Collecting is the wrong model for expertise. Badges, levels and streaks all say the same thing — you
have accumulated — and none of them say the thing that is actually true about getting good at
something: **you need less.** Fewer prompts, fewer explanations, fewer affordances, less scaffolding
in the way. The tall crystal *is* the scaffolding, and mastery is what grinds it down.

So a worn tile reads correctly at a glance. "I have done this a thousand times" looks like a nub. "I
started this yesterday" looks like a spire. Neither is shameful; one is simply newer.

**And the weight follows the wear.** A tall crystal is top-heavy — showy, unsettled, easy to knock.
As it wears the centre of gravity drops and the tile sits low and steady. The tile becomes a
physical object that *feels* mastered, which is what makes it the person's own: their physical AI
tile, not a score on a profile.

## What actually wears it

The crystal is tied to the locally running model. It measures **assistance drawn down** — the help
this tile actually needed from the local LLM to get work done — not time elapsed, not sessions
opened, not turns taken. A tile left alone for a year is exactly as tall as you left it. A tile that
carried you through a hundred real pieces of work is a nub, because you stopped needing to be
carried.

That makes the indicator honest in the only way that matters: it cannot be waited out, and it tracks
the thing it claims to track.

## Rules

1. **Wear is monotonic.** It only ever goes down. Nothing resets a crystal, nothing regrows one, and
   no update restores it — the same one-way property that makes a
   [one-time seal](ONE-TIME-SEALS.md) trustworthy, for the same reason.
2. **It cannot be granted, bought, transferred or set.** A crystal is worn by doing the work on this
   tile. There is no other way to move it, including for us.
3. **It is per tile, not per person.** You can be a master of one tile and brand new at another,
   which is true of people and is the useful thing to show. A tile carries its own crystal because
   the tile is the working situation.
4. **It is local and private by default.** It is derived from your own device's model use. It is not
   a rank, not a leaderboard, and not something other people can see because you published
   something — a published tile carries its lineage, never its owner's wear.
5. **A tall crystal is never a penalty.** Nothing is gated behind wear. It describes; it does not
   restrict.

## The honest risk

Any visible progression measure becomes a target if there is something to win. Two things hold that
down here, and they should stay: wear tracks work actually completed rather than raw calls made, so
grinding it is just doing the work; and it is private and local, so there is nobody to show it to.
If either of those changes — a public crystal, a leaderboard, a reward — the measure stops being
honest, and it would be better to remove it than to keep it under those conditions.

## Status

Specified, not implemented. Nothing in the tree renders or tracks a crystal yet; this is the
conforming behaviour, and the wear metric in particular needs a definition precise enough to
compute before it can ship.
