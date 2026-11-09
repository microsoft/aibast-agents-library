# Bringing a solution into the library

**The short version:** translate the outside solution into one `agent.py` first. Test it by hot-loading it
in a local Brainstem until it answers right. The cloud comes last, and only when we choose.

The `agent.py` is the **transfer layer**. It is where we translate their solution and where we add our own
synthetic data. Every other shape (Brainstem, skill, Copilot Studio package) is produced from it.

## Two versions of every outside solution

| Version | What it is | Where it comes from |
|---|---|---|
| **Bare** | Their package, unchanged | Their own published download. We never edit their tree or push to their repository. |
| **Layered** | Our `agent.py`: their solution plus our synthetic records, written instructions and checks | `federation/<source>/<their-slug>/<name>_agent.py` in this repository |

## Why this is faster

- **One translation, not one per platform.** Their solution becomes an `agent.py` once. The other shapes are
  built from that file.
- **Each fix takes seconds.** Edit the file, then ask the local Brainstem. It reloads agents on every message,
  so there is no restart and no import. In our hand runs (2026-11-09) each answer came back in about 3 to 5
  seconds.
- **The cloud loop is much slower.** A cloud change means rebuilding, importing and publishing a package before
  you can ask again. That takes minutes per change, not seconds. We have not timed it end to end ourselves.
- **Adding our data is just editing the file.** The synthetic records live in the `agent.py`, so every shape
  picks them up.

## The steps

1. **Read their solution.** Start with their README and any sample data they ship. Their files are read-only
   to us.
2. **Write the cartridge.** One `agent.py` (a `BasicAgent` subclass, `__manifest__` schema `rapp-agent/1.0`)
   that does the deterministic part in code: rules, checks, calculations, views. It carries their sample data
   unchanged, or our fictional records when they ship none.
3. **Add the transfer layer**, above the agent class:
   - `INSTRUCTIONS`: who the agent is, which records it uses, how it answers, what it never does.
     Written for this solution, never generic.
   - `OPERATION_GUIDE`: one entry per operation, `{"title": ..., "when": "Use when ..."}`.
   - `CARRIED`: what their solution does that is not code (flows, connectors, document output, web
     research), one sentence each. It is passed through unchanged and marked as the part that stays with
     the AI.
4. **Hot-load it in a local Brainstem.** Put the file in a test Brainstem's agents folder and ask it a
   question for each operation. Fix and ask again until every answer follows their solution's own rules.
5. **Run the checker.**
   `python3 tools/check_cartridges.py --layered --brainstem http://localhost:<port>`. It checks that the
   answer is the same twice, there are no network or AI calls, the transfer layer is present, the script and
   the Brainstem give byte-identical output, and the Brainstem calls the tool for every operation.
6. **Three by hand, then the pipeline.** Convert three different kinds of solution by hand and keep
   everything they produce. Make the pipeline reproduce those three, then run the rest.
7. **Cloud, later and only by choice.** `tools/agent_to_package.py` writes our `manual/` package from the
   file, and `tools/promote_solution_draft.py` pushes it as a Draft. Copilot Studio uses the library's current
   pattern: instructions, skills and knowledge.

## The judge

Never our own output. Each conversion is checked against **their** stated rules or data, by hand for the
first three. Example: the policy check returns "6 of 7 policies not met" for the sample contract, and each of
the seven was checked against the policy text.

## Three hand runs (2026-11-09)

| Solution | Shape | Operations | Local Brainstem |
|---|---|---|---|
| Contract Compliance Reviewer | Agent with skills | `consistency_review`, `policy_check` | 2 of 2 questions called the right operation; 7 findings, 6 of 7 policies not met |
| Invoice Processing | Flow with an AI rules step | `ledger_decisions` | 3 of 4 invoices logged, FAB-1043 flagged as a duplicate, the cover letter skipped |
| Team Ideas Board | App over a list | `board`, `check` | 2 high-priority ideas shown; "Done" and "Urgent" turned away |

## Rules that do not bend

- Never push to, or open a pull request against, the source library.
- Synthetic data only. Never connect a layered solution to real organization data.
- Plain business words. No product or competitor names in instructions or on public pages.
