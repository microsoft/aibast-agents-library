# The public lookup — subscribe once, resolve deterministically, work offline

The Frontier's one door outward ([`ONE-TIME-SEALS.md`](ONE-TIME-SEALS.md)) needs a pipeline behind
it: something that says where public things live, lets a person opt in to a source, and keeps
working when the network does not. That pipeline should not be invented here, because a working
instance of it already exists.

## The precedent: RAPP Vision

[`kody-w/rapp-vision`](https://kody-w.github.io/rapp-vision/) is a local-first player — "one HTML
file, no server, no account, no tracking" — that streams straight from public GitHub repositories.
Its shape is the shape this needs, and these parts are the reusable ones:

| Artifact | What it is | What it gives us |
|---|---|---|
| `channel.json` | one publisher's manifest: metadata and entries | the unit a person subscribes to |
| `channels.json` | a registry aggregating channel URLs | **subscription is adding a URL** — no account, no server |
| `hive.schema.json` | the RAPP Hive federation format, `rapp-hive/1.0` | a federation format that already exists |
| URL-relative resolution | every `src` resolves **against its own manifest's URL** | addressing with no service to query |

Two of its properties matter more than the file list:

- **Resolution is deterministic.** Because entries resolve relative to the manifest that names them,
  knowing the manifest and the id is enough to know the location. There is nothing to ask. That is
  what makes the same lookup work identically on any Brainstem, and what makes it work with no
  network at all once the manifest is in hand.
- **Personal state never leaves the device**, and lists export and import as JSON — which is exactly
  the exported-profile behaviour the seal model already requires.

Its "live" entries are also worth noting: they replay recorded gestures against the real application
in an iframe, with play, pause and seek. That is the same family as
[`UI-AUTOSTEER-PROTOCOL.md`](UI-AUTOSTEER-PROTOCOL.md) — a demonstration is a driven application, not
a recording of one — so a channel can carry a real driven walkthrough rather than a video of one.

## What the Frontier adds

Stated separately, because it does not exist in rapp-vision today and should not be described as
though it does:

- **The chant.** A rappid tile's seven-word key ([`RAPPID-TILE-PROTOCOL.md`](RAPPID-TILE-PROTOCOL.md))
  as an addressing layer over subscribed channels: a memorable phrase resolves to an entry, and
  because resolution is deterministic the same phrase resolves the same way on any Brainstem —
  including one with no network, if the manifest is cached. A person can carry a capability in their
  head.
- **Verification on arrival.** Bytes are checked against their recorded hash, seed and face before
  they become anything. Fetching is not trusting, and a deterministic address is not a guarantee
  about content.
- **Subscription as a seal.** Opting into a source is a decision made once, in the moment it means
  something — the same primitive as everything else here.

## Participating: local state is the substrate, and divergence is the point

The local state a person accumulates by using this — what they subscribed to, what they cached, the
tiles they built, how a capability was adapted — is not exhaust. It is the useful part, and the
model should treat it that way.

**Divergence is expected, and it is how the catalog grows.** A public thing arrives; it gets used;
it changes. The local copy stops being a copy and becomes **its own dimension of that data** — a
branch with its own history, still carrying the lineage that says where it came from, so the
divergence is legible rather than mysterious. That is the same shape the tile model already has: a
dimension is a branch of a situation, not a corruption of one.

**And the loop closes.** What diverged locally can go back out: a person publishes it to their own
public channel, where it becomes an entry addressed deterministically like any other, summonable by
anyone. Nobody grants permission, because it is their namespace — which is exactly what makes a
catalog with no curator able to grow.

Three constraints keep participation from becoming something else:

1. **Nothing is uploaded on its own.** Publishing is an action a person takes, to a destination they
   chose. There is no ambient sync, no background contribution, no "help us improve" telemetry
   riding along. A model whose whole premise is that local state never leaves the device cannot have
   an exception.
2. **What goes out is the artifact, not the person.** A published divergence carries the capability
   and its lineage. It does not carry watch history, caches, credentials, or the contents of
   unrelated conversations.
3. **Work does not flow out this way.** Anything belonging to an employer or a customer is not
   material for a personal public channel, and the fact that publishing is easy is not a reason to
   treat that boundary as softer.

The result is a system where using it produces something worth having offline, and where the thing
you made by using it can become the next person's starting point.

## Offline is the normal case, not the fallback

Because the manifest is data and resolution is arithmetic, a subscribed and cached profile is a
complete lookup system on its own. That yields the property worth designing for: **a person who has
subscribed, cached and exported can summon by chant on a machine with no network, and get the same
answer.** Offline is not a degraded mode; it is the same mechanism with one fewer participant.

## What this costs, honestly

- **A dependency on a repository outside this one.** It is public, opt-in, and confined to the
  Frontier — but it is a personal-account repository referenced from a Microsoft-published one, and
  that is a thing a reviewer will reasonably ask about. It stays behind an opt-in seal, under
  `beta/`, and nothing on the mainline path depends on it.
- **A cached manifest can go stale.** Deterministic resolution means an old manifest resolves
  confidently to old bytes. Staleness must be visible, and refreshing must be a normal action.
- **No service also means no revocation.** Nothing can be recalled centrally, so verification on
  arrival is not optional — it is the only check there is.
