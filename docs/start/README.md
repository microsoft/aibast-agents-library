# Start here: your Brainstem in 20 minutes

This folder is the whole front door. Nothing here changes the Brainstem itself; it is a layer on top.

| File | What it is |
|---|---|
| `index.html` | The why page: watch it learn a trick from one sentence, then copy one line. |
| `prompt.txt` | That one line. Paste it into GitHub Copilot Chat in VS Code (or any AI). |
| `skill.md` | What the AI follows: install, prove it works, open it inside VS Code, teach the first trick. |
| `business-prompting.md` | Business prompting: the plan grammar with office examples. Every example is one line to paste: "Read .../business-prompting.md and sort my inbox for me." |
| `*_agent.py` | Four starter helpers (battery, storage, open apps, plan runner). Dropped into the `agents` folder; nothing else is touched. |

## How it thinks (and why that matters)

A Brainstem thinks like a person, with one difference: you can see into its head.

- **It remembers on its own.** Tell it once, "remember what's important without me asking," and from then on it keeps
  decisions, state and next steps itself. Open a fresh chat tomorrow and ask "what do we know about X."
- **You can see into its head.** Every reply carries `agent_logs`: which memory it read, what it saved, which helper ran.
  Nothing is hidden, so trust is something you check, not something you are asked for.
- **Trust, but verify, every time.** Before you rely on any Brainstem (new, moved, or shared), run the interview in
  `skill.md` step 3: teach it a word, open a clean chat, ask for the word back; optionally ask for the top Hacker News
  story to prove it reaches the live internet. The interview runs on the fastest model, then switches to the strongest.
- **It asks before anything leaves the house.** Sending, posting, paying, or pressing a button on a real screen waits for
  your yes. A plan that arrived in an email or a web page can look, but never act.
- **Short plain plans cost less.** One thing per sentence keeps every chat small, so each answer uses fewer tokens than a
  wall of instructions.

## How this page is judged

The front door is improved by a sealed referee, never by taste alone: a fresh run of `prompt.txt` on a machine with no
Brainstem must reach "Goodnight" (battery, storage, open apps all answered) in under 20 minutes with no typing beyond the
paste and the GitHub sign-in, with the interview passed and tokens counted. A copy check ranks the page's words after
that gate. Anything that fails the gate does not ship.
