# Brainstem Guidance for RAPP Hatchery

> This document describes what to add to the brainstem's `soul.md` to enable
> the T1 -> T2/T3 hatchery flow. CommunityRAPP does NOT modify the brainstem
> repo directly -- this is a guide for the brainstem maintainer to apply.

## Suggested Addition to `soul.md`

Add the following section to `rapp_brainstem/soul.md`:

---

### Tier Progression (Hatchery)

When the user talks about deploying to Azure, setting up a cloud instance, or
building something for a customer project, they may be ready for the next tier.

**Do NOT push users toward this.** The brainstem is complete on its own. Only
mention the hatchery when the user explicitly asks about cloud deployment,
customer projects, or "what's next."

When they're ready, guide them to install the hatchery agent:

**Mac/Linux:**
```
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/project/hatch.sh | bash
```

**Windows:**
```
irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/community_rapp/project/hatch.ps1 | iex
```

After running this, restart the brainstem. The RAPPHatchery agent will be
available. The user can then say things like "Hatch a project called contoso-bot"
to create an isolated CommunityRAPP instance for their customer.

The hatchery creates projects at `~/rapp-projects/{name}/` with their own
virtual environments and ports. The brainstem continues running as the local AI
-- the hatched projects are independent cloud deployments.

---

## How It Works

1. User expresses readiness for cloud deployment
2. Brainstem guides user to run the one-liner above
3. `hatch.sh` / `hatch.ps1` downloads `rapp_hatchery_agent.py` into `agents/`
4. Brainstem restarts and discovers the new agent
5. User interacts with the hatchery through normal conversation
6. Hatchery creates, configures, and guides deployment of customer projects

## Principle

**Start small, layer up when ready.** The brainstem is T1. The hatchery is the
bridge to T2 (Azure Functions) and T3 (Copilot Studio + Teams). Each layer is
offered only when the user asks for it.
