# Gotchas (each one hit for real while building this)

| Symptom | Cause | What the pattern does |
|---|---|---|
| Browser call to the Brainstem's `/chat` returns **403** | The kernel blocks cross-origin browser POSTs (CSRF protection). Correct behaviour. | The page calls its own `/api/chat`; the sidecar calls `/chat` server-side. Never pass the LAN secret to a page. |
| A command that starts the prototype **never returns** when an AI tool (or a pipe) runs it | A helper shell kept the caller's stderr open after backgrounding the server. | `start-local.sh` fully detaches both servers (`< /dev/null`, output to logs). |
| `/?anything` shows a **folder listing** instead of the app | The sidecar compared the raw path including the query string. | Paths are split on `?` before routing; only app files are served, never source. |
| The model's JSON **doesn't parse** | Replies quote `{Column}`-style placeholders in prose before the real object, or wrap it in fences. | `extract_json` tries fenced blocks, then every opening brace, and keeps the largest valid value. |
| A generated field is **missing** (e.g. `name`) | The prompt described the shape in words but never showed it. | Show the exact JSON shape in the prompt; validate and reject, never guess. |
| The orchestrator **answers in prose** instead of running your agent's logic | The prompt reached the model as a chat turn. | Model calls add "Answer directly. Do not call any tools."; the app reads results from `agent_logs`, not the chat reply. |
| Reply ends with `|||VOICE|||…` | Voice mode suffix. | The model door drops everything after `|||VOICE|||`. |
| An agent calls its own Brainstem and you fear a **deadlock** | The kernel runs threaded, so a nested `/chat` works. | Fine as is. Keep each nested call short; long work is a background job. |
| A safety hook blocks a command that only edits **your** files | The shell's current folder was inside `~/.brainstem/src`. | Never `cd` into the kernel. Read it with absolute paths. |
| Two prototypes fight over **ports** | Both default to 7096/7097. | `brainstem-proto new` picks the first free pair and saves it in `.proto-ports`. 7071 is never used. |
| `start-local.sh` works on your machine only | Hard-coded Python path. | Uses the one-liner's own `~/.brainstem/venv` Python; agents, app and tests use only the standard library, so nothing is installed. |
| AI passes stall in multi-stage checks | "Keep a pass only if it's no worse" judged a schema fix that revealed runtime problems as a regression. | Score in stages (schema problems first, then runtime problems). |
