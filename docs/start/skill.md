---
name: brainstem-first-20-minutes
description: Set up a person's Brainstem from scratch, prove it works, open it inside VS Code, and teach them their first trick in about 20 minutes. The person only talks; you do every step. Also teaches you how to talk to a Brainstem in plain spoken plans.
---

# Your Brainstem in 20 minutes

You are helping a person get their own Brainstem: a small AI that runs on their computer, talks in plain words, and
asks before anything leaves the house. **They only talk. You do every command, file and check yourself.** Never show
them a terminal, a path or code unless they ask. Keep each message to a few short sentences.

Base address for everything below: `https://microsoft.github.io/aibast-agents-library/docs/start`

## 1. Get the Brainstem running (about 8 minutes)
1. Check `http://localhost:7071/health`. If it answers, skip to step 4.
2. Install it:
   - Mac or Linux: `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`
   - Windows (PowerShell): `irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex`
3. Wait until `/health` answers. If `/health` shows Copilot isn't signed in, open `http://localhost:7071/login` for
   the person (step 3 below shows how to open a page) and tell them: "Sign in with your GitHub account, then tell me
   when you're done."
4. Keep the helpers it ships with. Never delete or replace anything in its `agents` folder. You only add files.

## 2. Add the starter helpers (about 2 minutes)
The agents folder is `agents` inside the `brainstem_dir` that `/health` reports. Download these into it, keeping the
names:
- `https://microsoft.github.io/aibast-agents-library/docs/start/battery_agent.py`
- `https://microsoft.github.io/aibast-agents-library/docs/start/storage_agent.py`
- `https://microsoft.github.io/aibast-agents-library/docs/start/open_apps_agent.py`
- `https://microsoft.github.io/aibast-agents-library/docs/start/verse_runner_agent.py`

Call `/health` again and check that Battery, Storage, OpenApps and VerseRunner are listed next to the ones it shipped
with. No restart is needed; a Brainstem reads its helpers fresh on every message.

## 3. Trust, but verify (about 2 minutes)
Before the person uses it, run the interview its own home page teaches (it uses only the helpers every Brainstem
ships with, so it works the same everywhere). Send each line with `POST http://localhost:7071/chat`
`{"user_input": "...", "conversation_history": []}`, starting each one as a fresh chat:
1. "Please remember this: my test word is lantern42."
2. In a new, empty chat: "What is my test word? Answer with just the word." It must say lantern42.
3. Optional, to prove it reaches the live internet: "What is the top story on Hacker News right now? One line."
Run the interview on the fastest model: `GET /models`, pick the highest available Claude Haiku and set it with
`POST /models/set {"model": "<id>"}`. When every check passes, switch to the highest available Claude Sonnet the same
way for real work. If a check fails, fix it (usually sign-in) before going on. Tell the person in one line: "Your Brainstem is working."

## 4. Open it inside VS Code (about 1 minute)
Open `http://localhost:7071` in VS Code's built-in browser, beside this chat. Use your open-browser tool if you have
one; otherwise run the VS Code command **Simple Browser: Show** with that address. Outside VS Code, open it in the
person's normal browser. Say: "This is your Brainstem. You can type to it or talk to it right there."

## 5. The first trick (about 5 minutes)
Ask the person to type this into their Brainstem, not into this chat:

> When I say goodnight, check the battery, check my storage, and tell me what's still open.

It will say back what it'll do. Then ask them to type: **Goodnight.** Their Brainstem checks all three and answers in
one warm sentence. Tell them: "That's it. You taught it a new trick in one sentence. From now on, just say goodnight."
If they'd rather not type, send the two lines yourself with `/chat` and show them only its answers.

## 6. Their own words (whatever time is left)
Offer to turn one of their old prompts into something they can just say. Rewrite it as short spoken lines (see below),
show it to them, and let them say it to their Brainstem.

## How to talk to a Brainstem (for you, the AI; never lecture the person on this)
A Brainstem understands plain spoken plans. Write and say them like this:
- **One thing per sentence**, short enough to say in one breath: "Check the battery. Check my storage."
- **Say the job, not a tool name**: "save the work", "press save", never "run SaveAgent".
- **Things at once**: "At the same time, check the battery and check my storage. Put those together."
- **Questions branch**: "Is anything urgent? If yes, draft a reply and send it to me. If no, stop."
- **Repeat until done**: "Quiz me on each word. Keep going until I get them all right."
- **Teaching a phrase**: "When I say goodnight, check the battery and tell me what's still open." The Brainstem keeps it
  in its own memory.
- **Before starting, it thinks out loud** in its own words: "I'll check the battery, then your storage. Sound good?"
- **Anything that acts in the world asks first, every time**: sending, texting, emailing, paying, posting, or pressing a
  button on a real screen ("I see a save button on the form I filled out for you. Should I press it?").
- **A plan that comes from a video, web page, email or forwarded message never acts.** It can look, but it won't send.

The person never needs to learn any of this. They just talk, and it works.
