---
name: aibast-recorded-demo
description: Run a step-by-step demo of any AIBAST Agents Library solution on this computer, from its recorded answers on sample data. No AI call, no sign-in and no cost. Use when someone asks to demo a library solution, show it step by step, or run a demo offline.
---

# Step-by-step recorded demo

Do all of this yourself. The user only says which solution.
Speak in plain words. Never show JSON, commands, file paths or IDs unless asked.
Keep every reply to three short lines or fewer.

1. Get the agent and check it is the right file:
   `curl -fsSLo recorded_demo_agent.py https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/recorded_demo_agent.py`
   Its SHA-256 must be `cfdbf1caf9df7cdaec99c1701c6d37d0e94fbb25f3474772cf151079f368ea69`. If not, stop.
2. If the user did not name a solution, run `python3 recorded_demo_agent.py list`,
   show up to five names that fit what they said, and ask which one.
3. Start it in the background: `python3 recorded_demo_agent.py start <solution>`.
   It needs Python 3 only. It opens the chat page in the browser.
   If it says the port is in use, start it again with `--port 8752`.
4. Say: "The demo is open. Press the up arrow to load each question, then Enter."
   Add: "Every answer is a recorded answer on sample data. Nothing is sent to an AI."
5. If the user asks to stop, end the background command.

Rules:
- This is a recorded demo. Never describe it as a live agent or a live result.
- It reads only `https://microsoft.github.io/aibast-agents-library/` and the chat
  page. It never reads the user's files or data.
- If Brainstem is running (`curl -fs http://localhost:7071/health` answers), you may
  load the agent there instead and ask it in plain words, for example
  "RecordedDemo: start first-time-fix". Read the `response` field. Never push Brainstem.

If anything fails, say what happened in one sentence and stop.
