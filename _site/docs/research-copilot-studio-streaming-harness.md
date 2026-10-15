# Reverse-Engineering the Copilot Studio Agentic-Loop Streaming Harness

**Status:** Research note (non-normative). Documents publicly available Microsoft
source; does not disclose anything obtained via network interception, decompilation
of closed binaries, or private access.

**Date:** 2026-09-05

## Why this note exists

Two public artifacts prompted this investigation:

1. [Lighthouse Newsletter — "I put GitHub Copilot behind a MITM"](https://www.lighthousenewsletter.com/p/i-put-github-copilot-behind-a-mitm) —
   demonstrates using `mitmproxy` to intercept an Electron app's traffic when its
   behavior can't be determined from source alone.
2. [`microsoft/copilot-studio-plugin`](https://github.com/microsoft/copilot-studio-plugin)
   (target of `aka.ms/CopilotStudioPlugin`) — an experimental, openly licensed CLI
   plugin for authoring "CLI / agentic-loop" Copilot Studio agents.
3. [copilot-streaming-chat-playground — streaming tech note](https://raw.githack.com/jzh24516/copilot-streaming-chat-playground/main/docs/streaming-tech-note.html) —
   a community write-up of black-box discovery of the streaming protocol while
   building a live chat UI against Direct-to-Engine and Direct Line.

This note answers: **do you need to MITM the new Copilot Studio harness to
understand its wire protocol, or is it already public?** It's public. The
protocol implementation ships as a plain npm package.

## Method

No traffic was intercepted. The investigation was pure static analysis of
published artifacts:

```bash
git clone --depth 1 https://github.com/microsoft/copilot-studio-plugin
npm pack @microsoft/agents-copilotstudio-client   # v1.8.1 at time of writing
tar xzf microsoft-agents-copilotstudio-client-1.8.1.tgz
```

Both `copilot-studio-plugin/scripts/src/chat-with-agent.js` and `pac` itself
depend on `@microsoft/agents-copilotstudio-client` for the actual
Direct-to-Engine wire protocol. It is the authoritative, vendor-shipped
implementation — reading its compiled (sourcemapped) JS is strictly more
reliable than reconstructing behavior from captured traffic.

## Endpoint / connection resolution

CLI-authored ("agentic-loop") agents are recognized by
`settings.mcs.yml -> recognizer.kind` being one of:

- `CLIAgentRecognizer` (earlier)
- `CLICopilotRecognizer` (produced by `pac clone` / migration)

Any other recognizer kind (e.g. `GenerativeAIRecognizer`) is a classic
generative-orchestration agent, served by a different endpoint family and out
of scope here.

Connect URL shape (`buildDirectConnectUrl` in `chat-with-agent.js`):

```
https://<env-host>/copilotstudio/agenticruntime/3p/dataverse-backed/authenticated/bots/<schemaName>?api-version=1
```

`<env-host>` is derived from the environment GUID and target cloud:

| Cloud | API host suffix | GUID split (prefix.tail) |
|---|---|---|
| Prod / FirstRelease | `api.powerplatform.com` | 30 / 2 |
| Test | `api.test.powerplatform.com` | 31 / 1 |
| Preprod | `api.preprod.powerplatform.com` | 31 / 1 |
| Dev | `api.dev.powerplatform.com` | 31 / 1 |
| Gov / GovFR | `api.gov.powerplatform.microsoft.us` | 31 / 1 |
| High | `api.high.powerplatform.microsoft.us` | 31 / 1 |
| DoD | `api.appsplatform.us` | 31 / 1 |
| Mooncake | `api.powerplatform.partner.microsoftonline.cn` | 31 / 1 |

Result: `https://<30or31-hex>.<1or2-hex>.environment.<suffix>/...`.

An `island-experimental-url` response header can redirect the client to a
different `directConnectUrl` mid-session (`processResponseHeaders` in
`copilotStudioClient.js`) — used for experimental/"island" routing without a
client-side redeploy.

## Auth

- MSAL device-code flow, **public client** (no secret).
- Delegated scope: `CopilotStudio.Copilots.Invoke`.
- Scope string: `https://<cloud-api-suffix>/.default`.
- Token cache: OS-native secure storage via `@azure/msal-node-extensions`
  (Keychain / DPAPI / libsecret), one cache slot per agent
  (`chat-<agentId>` account name), with an explicit plaintext-file fallback
  and a warning when the native module can't load (e.g. before a plugin's
  native deps are provisioned).
- A dedicated diagnostic path exists because MSAL-node masks a failed
  `/devicecode` request as an opaque `invalid_grant`: the client re-issues the
  raw `POST {authority}/oauth2/v2.0/devicecode` request itself to surface the
  real AADSTS error/hint (e.g. "enable public client flows", "app not in this
  tenant").

## Transport: Server-Sent Events carrying Bot Framework Activities

`copilotStudioClient.js: postRequestAsync()` is the entire transport layer:

```js
const eventSource = createEventSource({
  url,
  headers: {
    Authorization: `Bearer <token>`,
    'User-Agent': UserAgentHelper.getProductInfo(),
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
  },
  body: body ? JSON.stringify(body) : undefined,
  method,
});

for await (const { data, event } of eventSource) {
  if (data && event === 'activity') {
    const activity = Activity.fromJson(data);
    // ... see below
  } else if (event === 'end') {
    break; // stream complete
  }
  if (eventSource.readyState === 'closed') break;
}
```

- One HTTP request (`POST .../conversations` or `.../conversations/{id}`),
  response is `text/event-stream`.
- Each SSE frame with `event: activity` carries a JSON-serialized Bot
  Framework `Activity`.
- `event: end` (or the EventSource entering `closed` state) terminates the
  generator.

## Activity taxonomy and the streamId/streamSequence reassembly

Three activity shapes matter for a streamed turn (confirmed against both the
SDK source and the independent playground's empirical description):

| Kind | `activity.type` | Marker | Purpose |
|---|---|---|---|
| Reasoning step | `typing` | `channelData.streamType === "informative"` | Human-readable progress cue ("Generating plan…", "Analyzing data…") |
| Streaming chunk | `typing` | `entities[].type === "streaminfo" && streamType === "streaming"` (or legacy `channelData.streamType === "streaming"`) | Interim, cumulative text delta |
| Final answer | `message` | — | The concluded answer; also may carry the conversation id if not set via headers |

Streaming chunks share a `streamId` across one answer but each chunk has a
**distinct activity id** — this is the detail the playground's tech note
calls "the biggest gotcha," because chat UIs (e.g. Web Chat) dedupe/key
their transcript by activity id, not stream id, and will otherwise render
one bubble per chunk (150+ observed for a long answer).

The SDK itself does the reassembly work one layer below any UI, so a
consumer never needs to re-derive it by hand:

```js
const streamingEntity = activity.entities?.find(
  e => e.type === 'streaminfo' && e.streamType === 'streaming'
);
if (activity.type === ActivityTypes.Typing) {
  if (streamingEntity || activity.channelData?.streamType === 'streaming') {
    const id = streamingEntity?.streamId ?? activity.channelData?.streamId;
    const sequence = streamingEntity?.streamSequence ?? activity.channelData?.streamSequence;
    if (id && sequence) {
      const chunks = streamMap.get(id) ?? [];
      chunks.push({ text: activity.text ?? '', sequence });
      streamMap.set(id, chunks);
      activity.text = chunks.sort((a, b) => a.sequence - b.sequence)
                             .map(c => c.text).join('');
    }
  }
  yield activity; // activity.text is now the cumulative answer-so-far
}
```

A consumer building its own UI (as the playground did against raw Direct
Line / Web Chat, which does **not** do this reassembly for you) must
replicate this: key the rendered bubble by `streamId` (not activity id),
and either rely on the SDK's cumulative `activity.text` or do the
sort-and-join itself.

Two protocol generations are reconciled transparently by the SDK: the
current `entities[].type === "streaminfo"` shape, and a legacy shape where
the same fields live directly on `activity.channelData`. Any home-grown
client needs to check both, or it will silently miss chunks from agents/
runtimes still emitting the older shape.

## Conversation lifecycle

- `startConversationStreaming({ locale?, emitStartConversationEvent?, conversationId? })`
  → `POST` to the connect URL (or `.../conversations/{id}` if resuming),
  body `{ emitStartConversationEvent, locale? }`.
- `sendActivityStreaming(activity, conversationId)` / `executeStreaming(...)`
  → subsequent turns, `POST .../conversations/{id}` with the outbound
  activity.
- Conversation id resolution order: response header
  (`x-ms-conversationid`-equivalent, read in `processResponseHeaders`) first;
  if absent, taken from the first `message` activity's `conversation.id`.
- `execute()`, `askQuestionAsync()`, `sendActivity()` are documented
  `@deprecated` non-streaming wrappers that simply buffer the streaming
  generator into an array — kept for back-compat callers that haven't moved
  to the streaming API.

## Attachment handling (client-side distillation, not part of the wire protocol)

Not part of the SDK itself, but documented for completeness because it's the
other half of making a streamed turn usable: `copilot-studio-plugin`'s
`response-format.js` distills a raw activity list into
`{ greeting, reasoning[], steps[], text, attachments[] }`, decoding any
`data:` URL attachments to disk (keyed by name+byte-length to dedupe) rather
than passing multi-KB base64 blobs back to a caller such as an LLM tool-call
loop.

## Practical implications

- **This is the actual harness** behind `pac copilot`, the Copilot Studio
  plugin's chat command, and any third-party Direct-to-Engine integration
  (e.g. the community streaming playground). One client library, several
  surfaces.
- **No interception was necessary** to establish any of the above — everything
  came from `npm pack`-able, sourcemapped, commented source. MITM remains the
  right tool only for the parts nobody publishes source for (e.g. a fully
  closed Electron client with no public SDK dependency).
- **A minimal reproduction** requires only: an Entra public-client app
  registration with `CopilotStudio.Copilots.Invoke` consent, the agent's
  environment id + schema name, and `@microsoft/agents-copilotstudio-client`
  (or a hand-rolled SSE client following the shapes documented above).

## References

- Lighthouse Newsletter: <https://www.lighthousenewsletter.com/p/i-put-github-copilot-behind-a-mitm>
- `microsoft/copilot-studio-plugin`: <https://github.com/microsoft/copilot-studio-plugin> (`aka.ms/CopilotStudioPlugin`)
- `@microsoft/agents-copilotstudio-client` on npm (v1.8.1 examined)
- Streaming tech note: <https://raw.githack.com/jzh24516/copilot-streaming-chat-playground/main/docs/streaming-tech-note.html>
