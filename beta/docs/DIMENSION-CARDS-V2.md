# Rappid dimension cards — the `.card` file (`rar-card/2.0`)

Kody, 2026-08-20: *"make them globally scannable through GitHub raw user data — if uploaded to the
RAR store, immediately summon that card for a task from the global public repo (online versions of
the local dimension cards). They are RAR cards v2 — the next version of that spec; update the RAR
repo and migrate the legacy cards to the new protocol, then test with usage on the Frontier client
for local-first tests to make sure they interchange on device and off. What data type should we make
these cards to get this right — simple and iconic without being hard to use as a file type, but
still very user-friendly like `agent.py` and `.egg` files… like a grail you can put `agent.py` and
`.egg` files INTO for safekeeping, just like Pokémon cards."*

## The decision: one JSON object, extension `.card`

A card is **one UTF-8 JSON file, one object, newline-terminated, extension `.card`**, schema
`rar-card/2.0`. Not a new container format.

## The hero law: the medium is the message

The card is the **Grail vehicle** for an `agent.py` or RAPP/1 `.egg`: the friendly
face, deterministic identity, integrity proof, portable payload, and optional
local dimension are one object. The visual card is not a screenshot or a link
to the real artifact. The `.card` file **is the artifact a person keeps**.

The acceptance story is **Charizard in the Woods**:

1. Two devices have no network.
2. One device has a saved `.card`; the other needs its capability.
3. The card crosses by any local file transport.
4. The receiver recomputes the seed/face and verifies every payload hash without
   fetching a repository.
5. The receiver unsleeves the exact `agent.py` or verifies and hatches the exact
   RAPP/1 `.egg`.
6. Any new conversation or experience enters only the receiver's local
   `dimension`.
7. Publishing later is an explicit export that strips the local dimension.

**Therefore, a woods-ready card MUST carry every required payload inline.** A
revision-pinned URL is a valid compact public/RAR representation, but it does
not pass the offline hero path unless those pinned bytes are already present in
the local content-addressed cache. A reader MUST never call a pinned-only card
"offline ready."

This is a north-star acceptance contract, not a claim that the historical
phone-to-phone QR/WebRTC flow currently ships. The currently deliverable unit
is the self-contained, locally verifiable file.

Why this and not a zip, a Markdown page, or a single-file HTML:

- **RAR's cards are already JSON.** Every entry of `cards/holo_cards.json` is a card face. v2 is a
  superset of v1 — the migration is mechanical and lossless, and v1 readers keep working on the
  `face` block.
- **Everything parses it.** `rapp_sdk.py`, the Frontier, `jq`, a phone that scanned a QR. No
  unpacking step, no base64 envelope around the whole thing, no renderer required to read it.
- **It streams off `raw.githubusercontent.com`** and diffs on GitHub exactly like `agent.py`.
- **"Iconic" is the extension and the face**, which every client renders the same way from the
  same seed; it is not a property of the bytes. "Sealed like an `.egg`" is the hashes inside.
- A zip hides the contents; an HTML card is active content from a stranger; Markdown front matter
  is two parsers. JSON is one.

## What is in a card

```json
{
  "schema": "rar-card/2.0",
  "id": "@kody-w/book_factory",
  "seed": 13467203979104256843,
  "name_seed": 3136112411,
  "incantation": "TWIST MOLD BEQUEST VALOR LEFT ORBIT RUNE",
  "version": "1.2.0",
  "face": { "…every v1 holo-card field, unchanged: name, title, type_line, colors, hp, stats, abilities, rarity, evolution, avatar_svg…" },
  "manifest": { "schema": "…", "name": "@kody-w/book_factory", "display_name": "BookFactory", "description": "…", "author": "…", "tags": [], "category": "creative", "quality_tier": "community" },
  "payload": [
    { "kind": "agent.py", "filename": "bookfactory_agent.py", "sha256_lf_v1": "1224fe87e3cf…", "inline": "…source…" },
    { "kind": "egg", "filename": "bookfactory.egg", "sha256": "…", "url": "https://raw.githubusercontent.com/kody-w/RAR/<rev>/agents/@kody-w/bookfactory.egg" }
  ],
  "state": "dormant",
  "origin": { "kind": "frontier", "brainstem": "rappid:…", "twin": null, "parkedAt": "2026-08-20T18:44:00Z" },
  "dimension": null,
  "scan": { "url": "https://raw.githubusercontent.com/kody-w/RAR/main/cards/v2/@kody-w/book_factory.card", "qr": "<svg…>" },
  "provenance": { "minted_by": "rapp_sdk 2.0 | frontier 0.6.x", "rar_revision": "e47755fa…" },
  "signature": null
}
```

Rules that make it simple:

| Rule | Meaning |
|---|---|
| **The seed is the identity.** | `seed` = `forge_seed(manifest)`; `face` = `resolve_card_from_seed(seed)`; `incantation` = `seed_to_words(seed)`. A reader may recompute all three and must refuse a card whose `face` disagrees with its `seed`. |
| **Payload items are inline OR pinned, always hashed.** | `inline` carries the bytes (UTF-8 text for `agent.py`; base64 for `egg`); `url` is a revision-pinned raw GitHub URL. Either way `sha256_lf_v1` (text) or `sha256` (binary) is mandatory and verified before anything runs. Inline when the card travels or must work offline; pinned when it lives in RAR and compact online resolution is acceptable. |
| **The sleeve holds agents and eggs only.** | `kind` ∈ `agent.py` · `egg`. A card with an empty payload is a face-only card (v1 in v2 clothing). |
| **State is a word.** | `dormant` (in a registry or on disk, no process) · `active` (in a herd: a live twin or a parked conversation). The same card moves between the two without changing identity. |
| **The dimension stays home.** | `dimension` (a conversation: turns, history) is `null` in anything published; it exists only in the local binder copy unless the user exports it explicitly, and then it is its own choice on the export panel. The global RAPPID protocol tracks identity and lineage; it does not require uploading the private dimension. |
| **Scannable means a URL.** | `scan.url` is the card's public raw URL; the QR on the face encodes it (or `rar://@publisher/slug@<seed>` for offline resolution). Summon = fetch → verify hashes → recompute the seed → hatch the payload as a twin, or wake the dimension. |
| **Small.** | ≤ 1 MiB with inline payload; larger payloads must be pinned. |

## RAR v2 — what changes in `kody-w/RAR`

1. `spec/rar-card-v2.md` (this contract, in the repo's voice) and `schema/rar-card-2.0.json`.
2. `scripts/migrate_cards_v2.py`: for every v1 entry in `cards/holo_cards.json` write
   `cards/v2/@publisher/slug.card` with `face` = the v1 entry, `payload` = the registry's agent file
   **pinned** (url + `sha256-lf-v1` from `registry.json`), `state: "dormant"`, `scan.url` set.
   Keep `holo_cards.json` as the v1 index; add `cards/v2/index.json` (id → seed, sha, url).
3. `rapp_sdk.py`: `card pack <agent.py> [--egg …] [--inline]` · `card unpack <x.card>` ·
   `card scan <url|incantation|seed>` (fetch/resolve → verify → print the face and the payload
   hashes) · `card verify <x.card>`. `mint_card` gains `to_v2()`.
4. The site renders v2 cards from `cards/v2/` with the QR; `api.json` gains `cards_v2`.
5. Tests: v1 → v2 → v1 round-trip keeps every face byte; seed recomputation over the whole index;
   a tampered payload hash is refused; a card whose face disagrees with its seed is refused.

## Frontier — what changes here

1. `beta/electron/rar-card.mjs` (already ordered): the JS port of seed/face/incantation, plus
   `packCard` / `unpackCard` / `verifyCard` for `rar-card/2.0`.
2. A dimension card on disk **is** a `.card` (`~/.brainstem/beta-launcher/cards/<id>.card`) with
   `state: "active"` and a local `dimension`; *Export to RAR* writes the public form (payload
   inline or pinned, `dimension: null`, `state: "dormant"`) and shows those exact bytes first.
3. **Summon**: paste a raw URL, a seed, or seven words into the Store picker (or scan a QR from the
   phone companion later): fetch → verify → the card appears dormant in the herd; *◈ Hatch* makes
   it active.
4. **Interchange proof** (local-first): pack a card from a live twin → unpack on a second isolated
   Frontier home → byte-identical payload and face; publish-form round trip through a fixture "RAR"
   served from a local directory (no network) and through the real raw URL when online; a
   tampered hash is refused; the dimension block never appears in the public form.

## Migration of the legacy cards

Every v1 face becomes a v2 card with a pinned payload — nothing is re-minted, so seeds and
incantations do not change; anyone holding seven words still gets the same card. The v1 index stays
until every client reads v2, then it is frozen, never deleted.

## Who does what

RAR changes land as a pull request prepared in a clone of `kody-w/RAR` — Kody pushes/merges (his
repo, his call). Frontier changes ride PR #182's branch behind the same gates as everything else.
