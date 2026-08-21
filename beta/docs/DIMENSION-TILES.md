# Table view and dimension tiles

Table view lets a user move a live Brainstem conversation into the herd as a
dimension tile, retain its exact history, start another conversation, and later
restore or compare either result. The implementation is confined to the
Frontier shell and frame bridge; it does not modify the Brainstem kernel or the
RAPP/1 chat envelope.

## Mode boundary

**Off is off.** Table view defaults to disabled. While disabled, Frontier adds
no tile DOM, CSS, listeners, active IPC operations, or frame-bridge source. A
mode-off identity test proves that the composed frame source is byte-identical
to its input. Disabling the mode removes all view resources immediately but
does not delete stored tiles.

Table view can be changed through:

- the native **View → Table view** checkbox;
- the exact, trimmed composer control word `table view`;
- `RAPP_TABLE_VIEW=1|0`;
- `settings.json`:

  ```json
  {
    "tableView": {
      "on": false,
      "layout": "table",
      "customLayoutPath": null
    }
  }
  ```

The feature has not shipped, so the old setting, environment variable, command,
and IPC names have no compatibility aliases.

## Dimension tile record

A dimension tile is a persisted conversation plus the route and model metadata
needed to restore it:

```json
{
  "schema": "rapp-dimension-tile/1.0",
  "id": "tile-…",
  "title": "first user line, at most 60 characters",
  "createdAt": "…",
  "parkedAt": "…",
  "route": {
    "url": "http://127.0.0.1:PORT",
    "rappid": "…",
    "compositionHash": "…",
    "model": "auto"
  },
  "turns": [
    {
      "role": "user|assistant",
      "text": "…",
      "html": "sanitized…",
      "at": "…"
    }
  ],
  "history": [
    {
      "role": "user|assistant",
      "content": "…"
    }
  ],
  "status": "parked | racing | primary | folded",
  "table": {
    "seat": 2,
    "faceUp": true
  }
}
```

Records are atomic, mode-0600 JSON files under
`~/.brainstem/beta-launcher/tiles/<id>.json`. The store caps each tile at 200
turns and 256 KiB. It validates identifiers, schema, size, roles, status, route,
timestamps, and placement metadata every time it reads or writes a record.

`turns` are captured from the Brainstem frame and sanitized with
`sanitizeMarkdownFragment`. `history` is the observed
`conversation_history` plus the corresponding reply. This distinction preserves
both safe rendering and exact continuation semantics.

## Operations

| Operation | Input | Result |
|---|---|---|
| **Park** | Select the Brainstem grab control or drag it into the herd. | Capture the transcript and observed wire history, persist the tile, then invoke the kernel's own **Clear** control. An accepted pending request remains attached to the tile and completes when its reply arrives. |
| **Wake** | Drag a tile to Brainstem, swipe right, press **Wake**, or use the keyboard action. | Verify the tile belongs to the active RAPPID and composition, render its transcript, and prefix its stored history onto the next chat request. The current conversation is parked first. |
| **Fold** | Swipe left or press **Fold**. | Keep the file, set `status: "folded"`, move it to the discard group, and provide a ten-second undo interval. |
| **Race** | Press **Race** on a tile whose last user turn is a question. | Create one pending contender for the same question. Selecting a winner makes it primary and folds only the paired rival. |
| **Layout controls** | Select riffle, fan, deal-to-seats, or draw-one. | Apply deterministic view arrangement and animation over the same persisted records. |

All operations are available through visible controls and UI Driver v2 handles.
The primary handles are `@brainstem.grab`, `@herd.tile[<id>]`,
`@herd.tile[<id>].wake`, `@herd.tile[<id>].fold`, and
`@herd.tile[<id>].race`.

## Frame bridge and IPC

`composeDimensionTilesFrameBridgeSource` returns the checkpoint source unchanged
while Table view is off. When enabled, `installTableViewFrameBridge`:

1. observes accepted `/chat` and `/chat/stream` requests;
2. binds response slots to request IDs;
3. captures sanitized transcript turns and canonical wire history;
4. preserves accepted requests across the internal Clear operation;
5. reconciles delayed completions by request ID;
6. restores a selected transcript and prefixes its history on continuation;
7. detaches the active tile after a user-initiated Clear.

Shell operations use `beta:tiles-*` IPC channels. Frame messages use
`rapp-beta:tile-*`. The mode toggle uses `beta:set-table-view` and
`rapp-beta:set-table-view`.

## Table layouts

Layouts change presentation only. They do not change the tile schema,
conversation history, actions, or route validation.

| `tableView.layout` | Label | Arrangement |
|---|---|---|
| `table` | Table | Oval positions and a discard group |
| `row` | Rows | Five positions and a discard row |
| `focus` | Focus | One active position above five secondary positions |
| `grid` | Grid | Two horizontal rows |
| `stack` | Stack | Draw and discard groups with a fanned row |
| `custom` | Custom… | Validated local JSON |

A custom layout may define `name`, `surfaceColor`, `seatPositions`, `tileSize`,
`arrangePattern`, and `faceDownRule`. The loader accepts only local JSON up to
64 KiB, rejects unknown fields and remote assets, and bounds every numeric
position and size.

## RAR interoperability

Human-facing Frontier records are dimension tiles. The public RAR protocol keeps
the `.card` extension, `rar-card/2.0` schema ID, and `card` SDK verb. RAR calls
its deterministic seven-word key an seven-word key; Frontier documentation uses
**seven-word key**. These protocol names do not change the Table view storage
directory, feature schema, identifiers, or UI terminology.

See [DIMENSION-TILES-V2.md](DIMENSION-TILES-V2.md) for the portable RAR file
contract and offline interchange path.

## Proof

`beta/tests/e2e/dimension-tiles.e2e.test.mjs` verifies a delayed reply parked
mid-request, a second completed tile, history restoration on the next real chat
request, folding, paired race resolution, manual Clear detachment, mode-off DOM
identity, persistence while disabled, and restoration after re-enabling.

Unit coverage verifies settings and environment precedence, exact composer
matching, atomic persistence and permissions, caps, invalid-record isolation,
request-ID reconciliation, mode-off IPC guards, frame sanitization, custom
layout validation, UI handles, gestures, keyboard paths, and mode-off source
identity.
