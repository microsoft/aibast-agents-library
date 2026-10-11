# Rapid prototyping on a local Brainstem

> **An expansion pack for the Brainstem one-liner.** Install it right after the one-liner; it builds
> around the Brainstem and never changes it. Then `brainstem-proto new "your idea"` (or
> `--transcript discovery-call.txt`) gives anyone a running, checked prototype in about 20 seconds,
> built further by whichever AI they already use. Start here: **[ONBOARDING.md](ONBOARDING.md)**.
> The live, guided version for Solution Engineers is [docs/rapp-guide-live.html](../docs/rapp-guide-live.html) (run `brainstem-proto guide`).

**The pattern:** build a product's AI as Brainstem agent files, run them on a dedicated local
Brainstem, and let the product's web app reach them through a tiny same-origin sidecar. Nothing
runs in the cloud while you iterate. When it's ready, the same agent files drop into an Azure
Function Brainstem and the sidecar points there. No rewrite, no kernel change.

```
 browser ── same origin ──▶ sidecar (your app, :7097) ── /chat ──▶ dedicated Brainstem (:7096)
   app page                  serves the page                        unchanged kernel
   recorded fallback         forwards /api/chat                     loads ONLY your agents/
                                                                    │
                                              your agent ◀──────────┘
                                              needs AI? ── /chat ──▶ the same Brainstem (the model door)
```

Worked example: a discovery call about equipment requests becomes a running, checked prototype and a
customer-ready `DISCOVERY.md` in about 20 seconds. See [docs/WORKED-EXAMPLE.md](docs/WORKED-EXAMPLE.md).

## Why this shape

| Need | How the pattern meets it |
|---|---|
| Iterate in minutes, not deploys | Agents reload from disk on every `/chat`; edit, save, ask again. |
| Never touch the kernel | Your agents live in **your** repo; the Brainstem loads them via `AGENTS_PATH`. Userland pattern 1. |
| Never disturb the Brainstem you use daily | A **dedicated** instance on its own port (7096). Your main one (7071) is untouched. |
| One AI for the whole product | Engine code calls the Brainstem's `/chat` for model work. Locally it's the Copilot-backed Brainstem; in the cloud it's the Azure Function Brainstem. Same call. |
| A browser UI that's allowed to call it | The Brainstem rejects cross-origin browser POSTs (CSRF protection, correctly). The page talks to its own origin; the **sidecar** calls `/chat` server-side. Userland pattern 2. |
| Demo can't break | Every AI feature has a **recorded answer** from a real run, shown with a "recorded" label when the Brainstem isn't reachable. |
| Path to SaaS | Same agent file → Azure Function Brainstem; sidecar → the SaaS API layer; page → Static Web App or Power Apps code app. |

## The three moves

### 1. Your agents, a dedicated Brainstem

Put agent files in your repo at `brainstem/agents/*_agent.py` (one class extending `BasicAgent`,
`metadata` = the tool schema, `perform(**kwargs)` returns a string; return **JSON** so the app can
read it). Start the unchanged kernel on its own port, pointed at that folder:

```bash
PORT=7096 AGENTS_PATH="$PWD/brainstem/agents" python3.11 ~/.brainstem/src/rapp_brainstem/brainstem.py
curl -s localhost:7096/health     # "agents": ["YourAgent"]  ← only yours
```

### 2. The Brainstem is the model door

Engine code never calls a model SDK directly. It calls one function that posts to a Brainstem's
`/chat` and reads `response` (drop the `|||VOICE|||` suffix). Ask it to answer directly so the
orchestrator doesn't route the prompt into a tool:

```python
from app.llm import complete
text = complete("Return ONLY a JSON array of ...")   # → http://localhost:7096/chat
```

An agent may call its **own** Brainstem: the kernel serves requests on threads, so a nested
`/chat` inside a tool call works (tested). In the cloud the same call goes to the Azure Function.

### 3. A same-origin sidecar for the browser

The page calls `/api/chat` on its own server; the sidecar forwards to the Brainstem and returns the
JSON. The app reads the agent's result from `agent_logs` (format: `[AgentName] {json}`), not from
the chat prose, so it gets exact data. If anything fails, the page shows the recorded answer and
says so.

## Try it (2 minutes, after the Brainstem one-liner)

```bash
bash pack/install.sh                                  # adds `brainstem-proto`, beside the Brainstem
brainstem-proto new "ideas for cutting meeting time"   # or: new --transcript pack/samples/discovery-call.txt
```

Or run the template by hand: `cd template && scripts/start-local.sh` (nothing to install: it uses the
one-liner's own Python). Offline tests: `~/.brainstem/venv/bin/python -m unittest discover -s tests`.
Whole-pack test with the kernel fingerprint check: `bash pack/test-pack.sh`.

Type a topic, press **Ask**. The `Idea` agent asks the same Brainstem for three ideas and returns
them as JSON; the page shows them with a 🧠 *Live* badge (or *Recorded* if the Brainstem is down).

To start your own product: rename `idea_agent.py`, change its prompt and `perform()`, and replace
`app/index.html`. Keep the three moves.

## Rules

1. **Never edit the kernel.** Not `brainstem.py`, not its `agents/`, not its `.env`. If you need
   something the kernel lacks, build it in the sidecar (the way `brainstem-mcp` keeps history and
   jobs). If it truly must change for every user, that's a kernel release decision, not yours.
2. **Dedicated port, dedicated agents folder.** Never load prototype agents into the Brainstem you
   use every day.
3. **Agents return JSON**; the app reads `agent_logs`. Prose is for people, JSON is for the app.
4. **Every AI feature ships with a recorded answer** captured from a real run, labelled as such
   when shown. Never fake one by hand.
5. **No secrets in the page.** Don't pass the Brainstem's LAN secret to the browser to get around
   the CSRF check; that's what the sidecar is for.
6. **Long work is a job, not a chat turn.** `/chat` is synchronous. Anything over a minute or two
   (deploys, multi-pass AI) runs as a background job the sidecar tracks.

## Going to the cloud (when the prototype is right)

| Local | Cloud |
|---|---|
| Dedicated Brainstem :7096 | Azure Function Brainstem (Tier 2), same `agents/` files |
| Copilot-backed model | Azure OpenAI behind the Function |
| `app/server.py` sidecar | API layer (Function or App Service) with Entra sign-in |
| `app/index.html` | Static Web App or Power Apps code app |

Gotchas found the hard way: [docs/GOTCHAS.md](docs/GOTCHAS.md).
