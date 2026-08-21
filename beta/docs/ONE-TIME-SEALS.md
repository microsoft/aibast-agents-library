# One-time seals — local-first preferences that need no setting up

A preference system usually asks people to make decisions before they have any basis for making
them: a settings screen, presented up front, full of switches whose consequences you cannot yet
imagine. Then it compounds the problem by syncing, so a new device inherits years of accumulated
choices instead of starting clean.

The Frontier uses a different primitive.

## The primitive

**Everything ships sealed.** A seal is a feature in its default state on this device, untouched.

**Acting on it pops the seal.** The person hears the station ident once, decides they do not want
it, and ends it there. That single action is the whole configuration step — no settings screen, no
confirmation, no decision made in advance of the experience that would inform it.

**A popped seal never re-seals.** Not at the next launch, not after an update, not after a month of
not being used, not because a later version thinks the person might feel differently now. The set of
popped seals *is* the preference state, and it only ever grows.

## Why this shape

- **A new device is intuitive from nothing.** Every seal is intact, so the product arrives in one
  known state. There is no configuration to import, no migration, nothing to understand before
  starting. The person shapes it by using it, in the moments where the choice actually makes sense.
- **It cannot surprise you.** Monotonicity is the trust property. A preference system that can
  silently revert — a reset, a migration, a well-meaning re-introduction — is worse than none,
  because the person learns their choices do not hold and stops making them.
- **No settings archaeology.** Nobody has to go looking for the thing they wanted to stop. The
  control lives at the moment, which matters most for rare features: when something happens once in
  twenty-five turns, the annoyance and the search are separated in time, and a buried setting is
  effectively unreachable.
- **It is trivially inspectable and trivially honest.** The state is a set of names. You can show a
  person exactly what they have popped, and "clear everything" means precisely what it says.
- **Local-first, so its promises are keepable.** The seal lives with the install, which is why the
  scope of "never" is this device and this install. Claiming more would be claiming something the
  product cannot deliver.

## The one door outward: the public summon

Seals do not sync, so a new device starts sealed and empty. That raises the obvious question — if
nothing carries over, how does a person get anything? — and the answer is the part that makes the
whole model work rather than merely tidy.

**There is exactly one door outward, and it is a public read.** A device with nothing on it can
**summon** a rappid tile from the public catalog by its seven-word key
([`RAPPID-TILE-PROTOCOL.md`](RAPPID-TILE-PROTOCOL.md)) — the tile is fetched from the public store
and verified locally. That is the entire handshake:

- **No account, no sign-in, no sync.** Nothing about the person is transmitted. The device asks for
  a name and receives bytes. That is what lets it work from nothing, and what makes it safe to
  offer on a device that has made no decisions yet.
- **Only the public face crosses.** The catalog reached through this door is public by
  construction; private material is not on the other side of it and cannot arrive through it. A
  device starting from nothing gets the public world, and only the public world.
- **The bytes are verified before they are anything.** A public read must not become a trust hole:
  a summoned tile is checked against its seed and face before it is installed or run, exactly as a
  locally-dropped one is. Fetching is not trusting.
- **Reaching out is itself a seal.** The first summon pops the seal on public lookup — a decision
  made once, in the moment it means something ("go and get that"), rather than a network-access
  question asked during setup before the person knows why they would say yes.

So the shape of a fresh device is: everything sealed, nothing inherited, and one public door a
person can choose to walk through. Set-up is not a screen to get through; it is the first thing you
actually wanted to do.

## Rules

1. **One action pops it.** No confirmation dialog, no "not now", no multi-step flow. A person who
   has decided has decided.
2. **Immediate.** It takes effect in the moment, including mid-occurrence — not at the next restart.
3. **Never re-seal, never re-prompt, never re-introduce.** No nagging, no gradual re-enablement, no
   experiment that turns it back on for a sample of people.
4. **Reset is deliberate and total.** A fresh install, or an explicit clear-data, restores every
   seal. Nothing else does, and nothing does it silently.
5. **If it cannot be written down**, honour it for the session and surface the failure. Silently
   discarding a person's choice is the one outcome that is never acceptable.
6. **Seals do not sync.** A second device starts sealed, on purpose. Inheriting configuration is the
   problem this avoids, not a feature it is missing — what a fresh device gets instead is the public
   summon above.

## Where it applies

Anything a person may reasonably want to end on first contact, and anything rare enough that a
buried setting would not be found in time. The first instance is the station ident in
[`VOICE.md`](VOICE.md); it is the pattern for the ones after it.

It is **not** the right shape for settings that need to be changed back and forth — a volume, a
model choice, a theme. Those are ordinary preferences. A seal is for a decision that only ever gets
made in one direction.
