# Rappid tiles — `rappid-tile/1.0`

**Status:** this specification supersedes `rar-card/2.0`. Every `rar-card/2.0` document is a valid
rappid tile after a mechanical, lossless migration, and a tile carries everything a card carried.
Readers accept both; writers emit tiles.

> Direction: *"cards are flimsy — tiles are substantial for a rappid to live on."* A card is
> something you look at. A **tile** is something a rappid **stands on**: a surface with a footprint,
> an identity, and a load it can bear. The change of noun is the change of contract.
>
> And what it bears is a working situation: a **transcript** together with **the agents that were
> hot-loaded for it**. A tile is inert data — static history plus an agent payload — which is why it
> can be carried at all, and why dropping it back into the live window is enough to resume the work.

## The metaphor shift: cards on a table → tiles in an arena

The rename is not cosmetic. The old vocabulary came from collectible cards, and it carried
assumptions that were wrong for what a rappid is:

| Card metaphor | Tile metaphor | Why it matters |
|---|---|---|
| A **card** is dealt, held, and looked at | A **tile** is placed, and something *stands on it* | A rappid is a running thing with a footprint, not an illustration of one. `stands_on` exists because a tile must bear a load. |
| Cards are flimsy and interchangeable | Tiles are substantial and load-bearing | A tile carries a primary payload plus the resources that payload needs — it is the whole unit of transfer, not a picture with attachments. |
| A **table** is where cards are dealt and compared | An **arena** is where agents *compete* | The view is not a layout preference; it is the use case. Several rappids answer the same task side by side and a person picks the winner. |
| A card's value is its rarity | A tile's value is what it can do, and where it came from | `lineage` records the ancestor, the ring, and the verdict that admitted it — provenance a collector's rarity never expressed. |

**One takeover, not two features.** The Agent Arena *is* the former table view, renamed and re-aimed:
the same surface, the same arrangements, the same moves. Nothing was kept in parallel — there is no
"table view" left to choose. The herd is the default view; the arena is the same herd arranged for
competition, with the tiles as the competitors.

So the vocabulary now reads end to end: **rappid tiles**, held in a **herd**, arranged in an
**arena** when they compete, each tile a `.tile` file that a rappid can stand on.

**Placement is arena vocabulary too.** A tile that sits in an arena records where it stands —
`arena: { seat, faceUp }` — the field the card format called `table`. The arena's arrangements are
**Ring** (the default), **Rows**, **Focus**, **Grid**, **Stack** and a validated **Custom** layout;
each describes how tiles are placed, never a game they came from.

**A rapplication is a tile.** A tile whose primary payload is a RAPP/1 `.egg` is a rapplication —
its agents and its own UI travel in the same object, verified by the same hashes, moved by the same
gestures. There is no separate rapplication format and no separate way to manage one.

## What a tile is

One UTF‑8 JSON object, one file, newline‑terminated, named after what it carries:

| Carries | File name |
|---|---|
| `bookfactory_agent.py` | `bookfactory_agent.py.tile` |
| `bookfactory.egg` | `bookfactory.egg.tile` |
| a face only (no payload) | `<slug>.tile` |

`.card` remains readable forever; `.tile` is what is written now.

## Why a tile is more than a card

A card was a *face plus a payload*. A tile adds the three things a rappid needs to actually live on
it, and they are the reason the protocol is superseded rather than extended:

1. **A footprint** — a tile declares what it needs to run (`stands_on`): the kernel contract, the
   Python version, whether it wants network or a filesystem, and its declared tools. A reader can
   answer *"will this run here?"* before it hatches anything. A card could not be asked that.
2. **A bearing surface** — a tile may carry more than one file (`payload[]` was already plural, but a
   tile makes the **primary** explicit and lets the rest be resources the agent legitimately needs:
   fixtures, a prompt, a small model card). The tile is the unit of transfer, not one file with
   attachments.
3. **Lineage** — a tile records where it came from and what it grew out of (`lineage`): the ancestor
   tile's seed, the ring, and the verification verdict that admitted it. A rappid that molts writes a
   new tile whose lineage points at the old one, so a chain of growth is readable offline.

Everything else — the deterministic seed, the face, the seven‑word key, the hashes, the
`dormant`/`active` states, the local‑only `dimension` — is carried over from `rar-card/2.0`
unchanged, which is what keeps the two compatible.

## The document

```json
{
  "schema": "rappid-tile/1.0",
  "supersedes": "rar-card/2.0",
  "id": "@kody-w/book_factory",
  "seed": 13467203979104256843,
  "name_seed": 3136112411,
  "key": "TWIST MOLD BEQUEST VALOR LEFT ORBIT RUNE",
  "version": "1.2.0",
  "face": { "…the rar-card/2.0 face, unchanged…" },
  "manifest": { "…the agent __manifest__…" },
  "stands_on": {
    "kernel": "rapp/1",
    "python": ">=3.11",
    "network": false,
    "filesystem": "agent-directory",
    "tools": ["BookFactory"]
  },
  "payload": [
    { "role": "primary", "kind": "agent.py", "filename": "bookfactory_agent.py",
      "sha256_lf_v1": "1224fe87e3cf…", "inline": "…source…" },
    { "role": "resource", "kind": "file", "filename": "styles.json",
      "sha256": "…", "inline_base64": "…" }
  ],
  "lineage": {
    "ancestor_seed": 9930127740482211903,
    "ring": 2,
    "verified_by": "molter/1",
    "verdict": "admitted"
  },
  "state": "dormant",
  "arena": { "seat": 2, "faceUp": true },
  "origin": { "kind": "frontier", "brainstem": "rappid:…", "twin": null, "parkedAt": "…" },
  "dimension": null,
  "scan": { "url": "https://raw.githubusercontent.com/…/bookfactory_agent.py.tile", "qr": "<svg…>" },
  "provenance": { "minted_by": "rapp_sdk 2.1 | frontier 0.6.x", "registry_revision": "e47755fa…" },
  "signature": null
}
```

### Rules

| Rule | Meaning |
|---|---|
| **The seed is still the identity.** | `seed = forge_seed(manifest)`, `face = resolve_from_seed(seed)`, `key = seed_to_words(seed)` — the same functions, the same numbers, the same seven words as `rar-card/2.0`. A tile migrated from a card keeps its seed, so anyone holding those seven words still gets the same thing. |
| **Exactly one primary.** | `payload[0].role === "primary"` and the file is named after it. Resources are additive and may be omitted by a reader that only wants the agent. |
| **Hashed, always.** | `sha256_lf_v1` for text, `sha256` for binary, verified before anything runs — inline or revision‑pinned alike. |
| **Offline is a claim you must earn.** | A tile is `offline: ready` only when every required payload is inline and its hash matches. A pinned‑only tile is never called offline‑ready. |
| **The footprint is honest.** | `stands_on` describes what the tile needs, not what it wishes for. A reader that cannot satisfy it refuses to hatch and says which requirement failed. |
| **The dimension stays home.** | A conversation (`dimension`) is `null` in anything published; it exists only in the local copy unless the person exports it deliberately. |
| **Small.** | ≤ 1 MiB with inline payloads; larger payloads must be pinned. |

## Migration from `rar-card/2.0`

Mechanical and lossless, in both directions for everything a card could express:

```
schema         "rar-card/2.0"            → "rappid-tile/1.0", supersedes: "rar-card/2.0"
incantation    <7 words>                 → key            (same value)
table          { seat, faceUp }          → arena          (same shape; the field is named for the
                                                            surface a tile stands in, not the one
                                                            cards were dealt on)
payload[0]                               → role: "primary"  (others become role: "resource")
—                                        → stands_on      (derived: kernel rapp/1, python from the
                                                            manifest, tools from the manifest)
—                                        → lineage        (omitted when the card had no ancestor)
file           x_agent.py.card           → x_agent.py.tile
```

Downgrading a tile to a card renames `arena` back to `table` and drops `stands_on`, `lineage`,
and any non‑primary payload, and is only
offered for readers pinned to the old schema. `tile verify` reports what a downgrade would lose.

**Registry:** `cards/v2/**.card` stay where they are and keep resolving. The migration writes
`tiles/v1/@publisher/<filename>.tile` beside them and the index gains a `tiles` section; the card
index is frozen, never deleted, once every client reads tiles.

## Tooling

| Command | Does |
|---|---|
| `tile pack <agent.py> [--resource f] [--pin url]` | mints a tile (inline by default) |
| `tile unpack <x.tile> [dir]` | verifies, then writes the primary and its resources |
| `tile verify <x.tile>` | schema, seed↔face, hashes, `stands_on` satisfiable here, offline readiness |
| `tile scan <url \| seed \| seven words>` | resolves and verifies; prints the face and the footprint |
| `tile from-card <x.card>` | migrates a `rar-card/2.0` document |

The Frontier reads and writes both; the registry keeps serving cards until every client has moved.

## Proof obligations

A conforming implementation demonstrates, offline: a card migrates to a tile with an identical seed,
face and seven‑word key; a tile packs and unpacks byte‑identically for text and binary payloads,
CRLF input included; a tampered payload hash is refused; a tile whose face disagrees with its seed is
refused; an unsatisfiable `stands_on` refuses to hatch and names the failed requirement; and a
pinned‑only tile never reports `offline: ready`.
