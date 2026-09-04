# Scout - Brainstem Rosetta Stone

This directory is Scout's collaboration layer for the Brainstem workspace. The
runtime root remains focused on Brainstem; Scout-specific lifecycle, exchange,
and squad mappings stay here.

## Golden path

1. Scout installs or updates the supported Brainstem runtime.
2. Scout materializes only `rapp_brainstem/` in the user workspace.
3. Scout starts the unchanged Grail kernel plus the nested RAPP/1 sidecar with
   `brainstem-workspace.ps1`.
4. The user opens `agents/experimental/scout/workspace.html` in Scout's center
   pane, or opens the sidecar's loopback `gateway_url`.
5. The Scout page authenticates to the sidecar through ignored state under
   `.brainstem_data/scout/`; the sidecar forwards the existing API contract.
6. `brainstem.py` and the Grail `index.html` remain byte-for-byte unchanged.
7. Scout and Brainstem build and test against the same workspace in real time.
8. Scout promotes the exact locally tested artifact to a Copilot Studio draft.
9. Publishing or sending remains an explicit user-approved action.

## Exchange map

| Direction | Command |
| --- | --- |
| Brainstem agent to portable skill | `python exchange.py agent-to-skill input_agent.py SKILL.md` |
| Portable skill to Brainstem agent | `python exchange.py skill-to-agent SKILL.md output_agent.py` |
| Scout squad to portable skill | `python exchange.py squad-to-skill .squad SQUAD-SKILL.md` |
| Portable squad skill to squad | `python exchange.py skill-to-squad SQUAD-SKILL.md .squad` |
| Inspect without exposing source bytes | `python exchange.py inspect SKILL.md` |

See `AGENT-ROSETTA-1.md` for universal first contact,
`RAPP-EXCHANGE-1.md` for the RAPP binding, and `SKILL.md` for autonomous setup
instructions that can be given to a fresh Scout.

## First contact with a foreign AI

1. Start with the ordinary Brainstem `POST /chat` contract.
2. Ask the foreign AI to declare capabilities and approval boundaries, not
   credentials or hidden prompts.
3. Translate only the capability needed for the shared task.
4. Preserve the original artifact and verify hashes before execution.
5. Test from both hosts and exchange evidence.
6. Keep identity, model state, memory, and permissions with their original host.

Scout's first encounter with Brainstem is the reference journey. No step may
assume the other AI already knows RAPP, Scout, skills, agents, or squads.
