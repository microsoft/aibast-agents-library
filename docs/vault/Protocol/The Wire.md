---
title: The Wire
section: Protocol
status: published
hook: How do RAPP systems talk to each other, and what exactly does POST /chat accept and return?
source: "SPEC.md §8; book/06-the-wire.md; book/A-reference-manual.md §A.5"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Wire

The **wire** is how RAPP systems exchange data.
There are **exactly two forms**: a synchronous `POST /chat` call, or an asynchronous append-only [[The Frame|frame]].
New capability is always a new agent behind `/chat` — never a new route.

## Form 1: `POST /chat` (synchronous)

JSON in, JSON out.

**Request:**

```
POST /chat
Content-Type: application/json

{ "user_input": "<plain-language request>",
  "session_id": "<optional>",
  "conversation_history": [ {"role": "...", "content": "..."} ] }
```

- `user_input` — string, **required**. Empty or whitespace-only counts as missing.
- `conversation_history` — optional array. Each item has `role` (`user`, `assistant` or `tool`) and string `content`.
- `session_id` — optional string.
- Unrecognized members **MUST be ignored**, never refused.

**Success (HTTP 200):**

```
200 OK
{ "response": "<assistant text>", "agent_logs": "<what fired>", "session_id": "<id>" }
```

- `response` — the assistant text.
- `agent_logs` — one line per agent call, newline-separated; empty when no agent ran.
- `session_id` — string.
- An endpoint may add members. The Grail adds `model`, `requested_model` and `voice_mode`. Consumers ignore what they do not recognize.

**Malformed request (HTTP 400):** exactly one member.

```json
{
  "error": "<human-readable message>"
}
```

The status and shape are fixed. The message text is not frozen; a Grail bug-fix release may reword it.

**Health:** `GET /health` returns HTTP 200 with a JSON object containing `status`. It carries no RAPP meaning.

## Try it

Against a running Brainstem:

```bash
curl -sS http://localhost:7071/chat \
  -H 'content-type: application/json' \
  -d '{
    "user_input": "Describe your loaded capabilities in one sentence."
  }'
```

Then send `{ "messages": [] }`. The server should return HTTP 400 with one `error` string — not guess that `messages` meant `user_input`.

## The Grail is the reference

An endpoint conforms when it answers every scenario of the Grail conformance suite (`conformance/grail/`) the way the pinned Grail does: same status, same members, same `response` and `session_id` values.
The suite defines 25 scenarios. Fourteen never reach the model and form a live join probe.
See [[The Brainstem Kernel]] and [[Conformance Classes]].

## Form 2: an append-only frame (asynchronous)

A frame is published to a stream: a repository path, an `events/` log, or any transport that keeps the exact frame value.
The transport may not reparent, rename or "upgrade" a frame in flight.

Two stream disciplines, chosen by the `stream_id`:

- **Rappid streams** (`rappid:@owner/slug:64hex`) — one agent's own history. `prev_wave` is `null`. Signatures are optional.
- **Swarm streams** (`net:…`, for example `net:commons`) — shared by many writers. `prev_wave` chains whole frames, and every frame **MUST** be signed.

Given a trusted head, any history is safe to read; the hash chain makes tampering detectable.
See [[Trust and Signatures]] and [[Security Considerations]].

## One shape for every tier

A Brainstem runs locally (`localhost:7071`), on a cloud endpoint, or behind a managed studio.
All three speak the same `POST /chat` contract.
Moving from laptop to cloud changes the URL, not the protocol.
That is why the wire stays at one endpoint: two endpoints would let the tiers drift apart.
See [[The Agent Contract]] and [[RAPP Deploy]].

## Related

- [[The Frame]]
- [[The Agent Contract]]
- [[The Brainstem Kernel]]
- [[Conformance Classes]]
- [[Protocol Layers]]
