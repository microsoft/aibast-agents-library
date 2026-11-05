---
title: Step 07 Deploy Prototype
section: Production Guide
status: published
hook: How reviewed agents get running locally, in Azure, and in Copilot Studio, and how to verify the deployment.
source: "docs/rapp-guide.html#step7; docs/rapp-guide.html#architecture; SPEC.md §8, §11.1"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Step 07 Deploy Prototype

**Deploying the prototype** means getting the reviewed agents to answer real questions.
Locally there is nothing to deploy: install the Brainstem, drop the files in its agents folder, and ask.
Move to **Azure Functions** and **Copilot Studio** when the customer needs access without your laptop.

Guide section: [Step 7 in the production guide](../rapp-guide.html#step7)

## At a glance

- **Type:** Manual
- **Duration:** minutes locally; 1-2 hours for the cloud tiers, with scripts
- **Owner:** Technical Team
- **Input:** approved agents from [[Step 06 Code Quality Review]], project JSON, integration notes, the `microsoft/aibast-agents-library` repository
- **Output:** a working prototype reachable from Teams or web chat, verified before the demo

## The cloud path

### 7.1 Deploy Azure infrastructure

Use the **Deploy to Azure** button in the repository README. It provisions from `azuredeploy.json`:

- Azure Function App (stateless intelligence layer)
- Azure File Storage (agent code and user memory)
- Application Insights
- Networking and security configuration

It completes in 5-10 minutes.

### 7.2 Run the setup script

```
git clone https://github.com/microsoft/aibast-agents-library.git
cd aibast-agents-library
./deploy.sh # or deploy.ps1 on Windows
```

### 7.3 Deploy your agents

Copy the approved `.py` files into the agents location: deploy from VS Code, or drag them into the File Storage `agents` folder.
Agents **hot-load** with no restart. In Azure they refresh within five minutes.

### 7.4 Connect to Copilot Studio

1. Download `solutions/<slug>/exports/<slug>-copilot-studio-solution.zip` and its deployment settings JSON.
2. Import the solution in Copilot Studio.
3. Set environment variables (Function URL, API key).
4. Enable channels: Teams, Web, Outlook.
5. Publish.

## Verification checklist

| Check | How | Expected |
|---|---|---|
| Function App running | Portal → Overview | Status "Running" |
| Agents loaded | File Storage → agents folder | Your `.py` files |
| Function responds | POST to Function URL | Lists available agents |
| Copilot Studio connected | Test chat | Replies to "Hello" |
| Agent calls work | Ask for one agent | Agent runs, returns result |
| Memory persists | Tell it something, ask later | It remembers |

## Common issues

- **Timeouts:** raise `functionTimeout` in `rapp_ai/host.json` and republish. A portal edit is overwritten by the next deployment.
- **Copilot Studio can't reach the Function:** rarely CORS. Check the Function is running and the key is right. Narrow `allowedOrigins` before production.
- **Agents not loading:** the Function App managed identity is missing a storage role. The storage account disallows shared keys, so no connection string will work.

## Rehearse before the demo

Role-play every MVP scenario. Check that:

- The model picks the **right agent** for each request.
- **Parameters** arrive correctly.
- Responses are useful and well formatted.
- **Invalid inputs fail gracefully.**
- Memory works across messages.

Then move to [[Step 08 Demo Review]].

## How rapp/1 underpins this step

- **One endpoint to test.** Every channel reaches the agents through the same wire: `POST /chat` with `user_input`, answering with `response`, `agent_logs` and `session_id`. `GET /health` is the liveness probe (§8). See [[The Wire]].
- **Deploying agents does not change the kernel.** New behavior lives outside the pinned Grail kernel (§11.1). Hot-loading agent files is that rule in practice. See [[The Brainstem Kernel]] and [[Distros and Pinning]].
- **Later stages.** Qualified releases and progressive rollout to production are covered by [[RAPP CICD]] and [[RAPP Deploy]], used from [[Step 13 Production Deployment]].

## Related

- [[Step 06 Code Quality Review]]
- [[Step 08 Demo Review]]
- [[The Wire]]
- [[The Brainstem Kernel]]
- [[RAPP Deploy]]
- [[Failure Atlas]]
