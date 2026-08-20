# Chat cards and the April Fools card table

Kody, 2026-08-20 (four messages, one feature):

> *"When users are waiting on an AI this is when they can GRAB and DRAG THE CHAT INTO THE HERD FOR
> SAFE KEEPING WHILE THEY START A NEW CHAT from that spot forward, to have the AIs able to RACE for
> the same task but different AIs are in the challenge (swipe-right / swipe-left mechanics, but for
> the Brainstem chat) instead of just being able to have one chat and clear it — this way the
> history is preserved instead of getting completely wiped."*
>
> *"This is the UI/UX we want to wrap this around without changing anything else… just add this
> drag-and-drop component that moves chat context around just like they are chat cards — they can
> grab and shuffle the chats, through an easter egg with different ways of dealing, as a fun minigame
> for people that play card games to be onboarded onto this UI/UX."*
>
> *"An April Fools version of the herd area to make it look like a poker table (or Yu-Gi-Oh, or
> Pokémon trading cards, or Magic: The Gathering, or UNO, or their custom version they can load in
> for games that are not default — mahjong etc.) for at least how the cards are laid on the table
> just like they were playing the game, but they are playing with the AI that is represented as
> contained in that chat card (they can drag it back into the main Brainstem to wake it back up
> fully as the primary companion — the user's Pikachu, but just for the chat transcript representing
> that dimension of the rappid creature)."*
>
> *"Save a checkpoint before you start this because this is an easter egg that we don't want to
> break anything or change anything with the default AI until April Fools mode is turned on and then
> this is exposed (and they can quickly turn it back off at any time once the joke is over)."*

## The one invariant

**Off is off.** With April Fools mode off (the default), the Frontier is byte-for-byte the
checkpoint: no extra DOM, CSS, listeners, IPC handlers that do anything, or bridge code in the
Brainstem frame. The kernel (`rapp_brainstem/`) is never touched — everything lives in the
Frontier shell and its frame bridge, like the safe words and the Messages look. Turning the mode
off mid-session removes the table and the card chrome immediately; parked cards stay on disk
and reappear when the mode is turned on again (nothing a user made is ever thrown away by the
toggle).

Toggle: **Chat Look → April Fools: Card Table** in the Frontier three-dot and native View menus
(persisted in `settings.json` as `aprilFools.on`), `RAPP_APRIL_FOOLS=1|0` as an override, and the
chat word `april fools` (exact, trimmed) in the Brainstem composer flips it — intercepted by the
same fail-open layer as the lineage words.

## What a chat card is

A card is a parked dimension of the companion: one transcript plus everything needed to wake it up.

```json
{
  "schema": "rapp-chat-card/1.0",
  "id": "card-…",
  "title": "first user line, ≤ 60 chars",
  "createdAt": "…", "parkedAt": "…",
  "route": { "url": "http://127.0.0.1:PORT", "rappid": "…", "compositionHash": "…", "model": "auto" },
  "turns": [ { "role": "user|assistant", "text": "…", "html": "sanitized…", "at": "…" } ],
  "history": [ { "role": "user|assistant", "content": "…" } ],
  "status": "parked | racing | primary | folded",
  "table": { "seat": 2, "faceUp": true }
}
```

`turns` come from the Brainstem frame's transcript (`#chat`), sanitized with the same
`sanitizeMarkdownFragment` the smooth stream uses; `history` is exactly the `conversation_history`
the kernel sent on its last `/chat` request plus the last reply — the bridge already sees both.
Cards are files: `~/.brainstem/beta-launcher/cards/<id>.json` (0600), listed on launch; they also
land in the ledger (`agents`-style event `card-parked` / `card-woken`) so the Brainstem can find
them.

## What a card looks like

A parked card is a **static twin tile** — the same chrome a hatched rapplication tile has in the
herd, with the conversation frozen inside it: the ◈ badge and name in the header, a status pill in
the READY style (`PARKED` · `RACING` · `PRIMARY` · `FOLDED`), the mono meta line
(`:<port> · <model or agent> · rappid:<…>`), the transcript's last lines in the same mono, and no
composer — a single quiet line, *Wake to message*, where the composer would be. The card-table
themes skin *around* this tile (felt, frames, seats); the tile itself stays the tile. Copy says
"rapplication", never "RAPPlication".

## The moves (mode on)

| Move | How | What happens |
|---|---|---|
| **Park** | a grab handle on the Brainstem pane header (*"grab this chat"*); drag it into the herd, or press *Park* on the handle | the card is captured (even mid-reply — the pending turn is marked `pending` and completed from the wire when the reply lands), the kernel chat is cleared through its own *Clear* button, the card appears in the herd at the next free seat |
| **Wake** | drag a card from the herd onto the Brainstem pane, or swipe **right**, or its *Wake* button | the transcript is re-rendered in the frame from the card, and the bridge splices the card's `history` in front of `conversation_history` on the next `/chat` requests — the layer substitutes, never subtracts — so the kernel continues that conversation without an API it does not have; the current chat (if any) is parked first, never lost |
| **Fold** | swipe **left**, or *Fold* | the card goes to the discard pile (still on disk, `status: folded`); *Undo* for 10 s; the pile can be fanned open |
| **Race** | *Race this* on a parked card whose last turn is a question | a fresh chat is started with the same question; the user picks the model/agent (the kernel's model select, or a twin); both cards are `racing`; swipe right on the winner → primary, the loser folds |
| **Shuffle / Deal** | the table's *Deal* menu | the onboarding minigame: riffle, fan, deal-to-seats, draw-one (a random card wakes) — pure layout and animation over the same cards |

Swipes are pointer gestures on a card (touchpad/touch/mouse drag past a threshold with a tilt); every
move also has a button and a keyboard path, and every move is a UI Driver v2 handle
(`@herd.card[<id>]`, `@herd.card[<id>].wake`, `@brainstem.grab`) so it can be driven and tested.

## One card, two states — compatible with the public RAR

Kody: *"look up the public RAR repo's card to make it compatible … make the cards exportable as
RAR-compliant so we can submit them to RAR, and the card stays (dormant) versus in the herd view
(active card)."*

The public registry (`kody-w/RAR`, MIT) already defines what a card **is**, and it is deterministic:

```
__manifest__ → forge_seed(name, category, quality_tier, tags, dependencies) → 64-bit seed
seed → resolve_card_from_seed() → type colors · HP · ATK/DEF/SPD/INT · abilities · rarity ·
       evolution stage · weakness/resistance · retreat cost · avatar SVG
seed → seed_to_words() → a 7-word incantation that reconstructs the exact card, offline
```

(`rapp_sdk.py`; minted cards at `cards/holo_cards.json`, keyed `@publisher/slug`; `api.json` marks
card resolution *LOCAL — computed, zero bandwidth*.) So compatibility is not a new format — it is
using theirs:

- **Same seed, same card.** `beta/electron/rar-card.mjs` ports `seed_hash` → `mulberry32` →
  `forge_seed` / `resolve_card_from_seed` / `seed_to_words` to JavaScript, with a conformance test
  that re-mints every entry of `cards/holo_cards.json` at the pinned RAR revision `e47755faaa04`
  and asserts byte-equal stats, types, rarity, stage, and incantation. The tile wears the RAR card:
  the type colors ring the ◈ badge, the stage and HP/ATK/DEF sit in the meta line, the incantation
  is the card's caption, the avatar is the art. Nothing is invented twice — the April Fools themes
  are *layouts* around RAR's card vocabulary (RAR already carries both the creature-card stats and
  the mana-cost/type-line reading).
- **Active vs dormant.** In the herd a card is **active**: it has a port, a READY/PARKED pill, a
  transcript. In RAR the same card is **dormant**: a catalog entry with a seed and an incantation and
  no process. The Store picker's *Public RAR* rows are dormant cards; dragging one into the herd is
  the existing *◈ Hatch* — that is activation. The new move is the reverse.
- **Export to RAR** (a move on an active card that carries an agent): the Frontier builds the
  single `.py` RAR accepts — the agent's source with a complete `__manifest__`
  (`schema`, `name` = `@<github-login>/<slug>`, `version`, `display_name`, `description`, `author`,
  `tags`, `category`, `quality_tier: community`), canonical `sha256-lf-v1` — shows the user **exactly
  the bytes that will leave the machine**, then files the `rar-change-request/1.0` Issue through the
  user's own GitHub identity (`gh auth` / `GITHUB_TOKEN`, never stored by the Frontier). The card's
  pill reads *submitted · issue #N* until the forge mints it; the seed is already known locally, so
  the dormant and active cards match before RAR ever answers.
- **What exports, what stays.** Only the agent file goes. A chat card's transcript never leaves the
  machine (RAR Issues are public by design); a chat card exports when it *carries* an agent — a
  twin's agent, a Surgeon-built or Molter-grown agent the conversation produced — and says plainly
  when it carries none.
- **Card JSON grows one block:** `"rar": { "seed", "name_seed", "incantation", "manifest",
  "sha256_lf_v1", "submitted": { "issue", "at", "operation" } }`.

## The table (themes)

Themes change only how cards are laid on the table and how a card looks; the moves are the same.
Original art only: felt, chips, frames, and color language that *evoke* each game — never a
trademarked logo, character, card face, or copyrighted artwork.

| `aprilFools.table` | Layout | Card look |
|---|---|---|
| `poker` (default) | green felt, seats around an oval, a dealer button, a discard pile | plain playing-card frame, corner index = turn count |
| `yugioh` | five monster zones in a row over a graveyard | tall frame, attribute-style dot, "ATK/DEF" = turns/tools |
| `pokemon` | bench of five under one active seat (the primary) | rounded frame, energy-style pips for tools used |
| `mtg` | battlefield rows, tapped = folded (rotated 90°) | framed art box with the title banner |
| `uno` | a draw pile and a discard pile; cards fanned in a hand | bold color per model, big center number = turns |
| `custom` | a JSON the user loads (`Load table…`): felt color, seat positions, card size, deal pattern, face-down rule | as the JSON says; validated, size-bounded, no remote assets |

`mahjong` and anything else are what `custom` is for.

## Laws

- **Off is off** (above). A test proves the shell's DOM outline and injected bridge sources are
  identical with the mode off before and after this feature.
- **Nothing is lost.** Park before clear; fold keeps the file; the toggle never deletes.
- **Kernel untouched.** Clearing uses the kernel's own button; continuing uses wire substitution.
- **Small and honest.** Cards cap at 200 turns / 256 KiB; the table shows at most 12 seats, the
  rest fan in the pile; a card that cannot be restored says so instead of pretending.
- **Drivable.** Every move has a handle; the regression harness gains a scenario.

## Proof

`beta/tests/e2e/chat-cards.e2e.test.mjs` (harness, mode on): ask a question through a fake
model with a delayed reply; park mid-reply; start a new chat and ask again; both cards show; the
parked card completes its pending turn when the wire delivers; swipe right wakes the first card
— the next `/chat` request's `conversation_history` begins with that card's history; fold the
other; toggle the mode off — the herd is the checkpoint's herd (outline equal), the card files
still exist; toggle on — the cards are back. Plus unit tests for the card store, sanitizer use,
and the custom-table JSON validator. Mode-off identity is asserted in the unit suite from the
checkpoint's recorded outline.
