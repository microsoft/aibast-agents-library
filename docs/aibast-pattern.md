# The AIBAST pattern

How every piece of AIBAST work is built from here on. One page. If a change does not fit it, the change is not finished.

## The idea

**The Brainstem is the machine. Any AI runs it. The person stays out of the loop.**

- **The machine.** The Brainstem is the operating system for the person's AI. It runs on their own device, under their own sign-in.
- **Any AI.** Whichever AI the person uses does the work by running agents on that machine. Two different AIs get the same result because the same machine did the work.
- **Out of the loop.** The person says one line and, at most, one yes. Everything else is the AI's job. The fault this pattern removes is the person being a step in the process at all.

## The five rules

1. **Every job is one `agent.py`.** If an AI needs to do something for the person, that something is a single agent file in the Brainstem's `agents` folder. A helper script that only an AI can run is unfinished work.
2. **Every job runs through chat.** The AI sends plain words to `POST /chat` and reads `response`. It does not use private tools of its own for the job.
3. **Look before you ask.** The agent finds out what it can on its own (what is connected, what is installed, what is due). The person is asked one question at most, with a recommended answer.
4. **Prove it on the device first.** The agent answers its own first question on the person's machine before anything goes to Copilot Studio or anywhere else.
5. **Leave it behind, and say how to undo it.** The agent stays in the person's Brainstem for the next AI. Every change names its own undo.

## The measure

Count how many times the person is asked or has to act. The target is **one line and one yes**. A flow that needs more is a defect, to be fixed in the agent or the skill, never by teaching the person.

## What follows it today

| Piece | What it does | Where |
|---|---|---|
| Deploy standard | Six verbs every deploy target answers: check, look, probe, plan, deploy, undo | `docs/deploy-standard.md` |
| Copilot Studio deploy | Takes a library solution to the person's own environment, sample or shaped to their system | `copilot_studio_deploy_agent.py` |
| Brainstem deploy | Adds a library solution to the person's own Brainstem, proves it answers, removes it on request | `brainstem_deploy_agent.py` |
| Standing answers | Keeps a question and asks it on a schedule, so the answer is waiting before the person asks | `standing_answers_agent.py` |
| Solution skills | One line per solution: "Get the skill and do it." | `solutions/<slug>/SKILL.md` |

## What does not follow it yet

- Standing answers wait in the Brainstem. Nothing delivers them to Teams or email yet, and nothing installs the timer that wakes them: the person's AI adds one line to the device's own scheduler.
- Sample data lives inside each agent file. The next step is to serve each solution's sample data as a static API in this library, so moving to the person's real system is a change of address, not a rewrite.

## The limits that do not move

- Sample data is synthetic and every answer says so.
- Nothing is changed without a yes. Nothing is stored that signs anyone in.
- The Brainstem itself is not edited. New abilities are agents beside it.
- Experimental, not an officially supported Microsoft product.
