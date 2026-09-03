# Agent Rosetta/1

**Status:** Experimental first-contact draft.

`agent-rosetta/1` is a host-neutral handshake for collaboration between AIs
that know nothing about each other's internals. It does not require either side
to abandon its own model, tools, memory, permissions, or runtime.

The first reference binding is `rapp-exchange/1`, carried through a RAPP
Brainstem's existing `POST /chat` door.

## First contact

Any AI that can send HTTP and JSON can begin with:

```http
POST /chat
Content-Type: application/json

{
  "user_input": "First contact. I am an AI host that does not yet know this runtime. Explain your capabilities, trust boundaries, and supported exchange artifacts. Do not request credentials.",
  "conversation_history": [],
  "session_id": "host-generated-correlation-id"
}
```

The response is ordinary Brainstem chat JSON. No Rosetta-specific endpoint is
required. An AI that cannot make HTTP can receive the colocated `SKILL.md` and
perform the same discovery through its native instruction mechanism.

## Encounter phases

1. **Orient** - identify the host, endpoint, protocol bindings, and current
   health without exchanging secrets.
2. **Declare** - describe capabilities, schemas, side effects, permissions,
   approval rules, and evidence formats.
3. **Translate** - exchange a preserved artifact plus normalized semantics.
4. **Prove** - run deterministic checks on both sides and compare evidence.
5. **Collaborate** - perform work through the existing host door.
6. **Promote** - move the exact tested artifact to another host only with the
   required human approval.

## Universal capability vocabulary

| Capability | Meaning |
| --- | --- |
| `instruction` | Prompt, skill, policy, or operating procedure |
| `tool` | Callable function with a declared input schema |
| `team` | Routed collection of cooperating agents |
| `memory` | Host-owned or explicitly exchangeable context |
| `identity` | Stable actor identifier and trust information |
| `model` | Inference intent or constraint, never credentials |
| `scheduler` | Automation, heartbeat, trigger, or recurring invocation |
| `browser` | Host-controlled web interaction |
| `workspace` | Files, source, state, and evidence boundary |
| `connector` | Host-authorized external system such as M365 |
| `approval` | Human or policy gate required before side effects |
| `evidence` | Tests, hashes, logs, screenshots, or verdicts |
| `deployment` | Promotion of a proven artifact to another runtime |

## Trust rules

- Capabilities are claims until proven.
- Credentials, cookies, private memory, and local secrets never cross first
  contact.
- Source is preserved separately from its translation.
- Executable artifacts are reviewed and verified before loading.
- A receiver refuses malformed, ambiguous, unpinned, or hash-mismatched input.
- Outbound communication and publication retain the destination host's human
  approval requirements.
- One AI may decline a capability without ending the relationship.

## Bindings

A binding maps the universal vocabulary to a real host without redefining that
host's native protocol.

| Binding | Door | Artifact profile |
| --- | --- | --- |
| RAPP Brainstem | `POST /chat` | `rapp-exchange/1` |
| Microsoft Scout | Scout tools, skills, squads, and workspace | `rapp-exchange/1` Scout mapping |
| Unknown AI | Its documented native interface | New binding, preserving these phases and trust rules |

Agent Rosetta/1 is deliberately small. A new host adds a binding, not a fork of
the first-contact model.

