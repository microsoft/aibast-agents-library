# Prototype your idea on your Brainstem

For people who want a working prototype, not a lesson in AI. You need the Brainstem (one line)
and the AI you already use: GitHub Copilot, Claude, Cursor, Codex, Gemini, any of them.

## 1. Once: install

```bash
# the Brainstem one-liner you already know, then:
bash install.sh            # this pack, from its folder (adds the `brainstem-proto` command)
```

The pack sits beside your Brainstem and never changes it. Your everyday Brainstem keeps running
exactly as before.

## 2. Each idea: one command

```bash
brainstem-proto new "an approval app for equipment requests"
```

or, if you had a discovery call:

```bash
brainstem-proto new --transcript discovery-call.txt
```

In about 20 seconds you get a prototype folder, its own Brainstem and app running, a check that
says **"Your prototype is working."**, and (from a transcript) a one-page `DISCOVERY.md` of what the
customer needs, with roles instead of names. The first instruction for your AI is on your clipboard.

## 3. Paste, then talk

Your AI opens in the prototype folder (or open it yourself). Paste. From then on, just say what you
want in plain words. `PROMPTS.md` in the folder has sentences for every moment: add something, fix
something, make it safe to demo, explain it to the team.

Your AI follows `AGENTS.md`: it builds in small steps, runs the check before it tells you anything,
stops at the RAPP gates for your yes, keeps real names and data out, and never touches your Brainstem.

## Day to day

| You want to | Say or run |
|---|---|
| See it | the link it printed (http://localhost:7097 or similar) |
| Know if it's working | `brainstem-proto check` |
| Stop / start it | `brainstem-proto stop` / `brainstem-proto start` |
| Find your prototypes | `brainstem-proto list` |

## When it's ready for more than your laptop

The same agent files run on an Azure Function Brainstem. Ask your AI "what would it take to run this
for my team?" and it will tell you; nothing moves until you say so.

## Feature requests and usage

- **Ask for something:** `brainstem-proto feedback "I wish it could ..."` opens a prefilled request (GitHub issue today; set `PROTO_FEEDBACK_FORM` to a Microsoft Form link to use that instead). Nothing is sent until you submit it. Or tell your AI: *"send a feature request: ..."*.
- **Usage:** the pack keeps a local log of counts and timestamps only (prototypes created, from a transcript or not, checks passed or failed, feedback opened): never content, names or transcripts. `brainstem-proto usage` shows it; set `PROTO_NO_USAGE=1` to turn it off. Nothing leaves your computer; sending aggregate counts is planned only after a privacy review.
