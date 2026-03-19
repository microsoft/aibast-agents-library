# AI BAST Agents Library

> ⚠️ **IMPORTANT:** This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications Specialist Team (AIBAST), not an officially supported Microsoft product.

> **📖 For Non-Technical Users:** View the full interactive documentation at [https://microsoft.github.io/aibast-agents-library/](https://microsoft.github.io/aibast-agents-library/)

Main repository for the AIBAST (Artificial Intelligence Business Applications Specialist Team) AI Agents Library — a Microsoft framework for building and deploying AI agent automation capabilities.

**104 agent templates. 14 industry verticals. Local-first brainstem. One-liner install.**

---

## Quick Start

### Install the Brainstem (macOS/Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.sh | bash
```

### Install the Brainstem (Windows PowerShell)

```powershell
irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex
```

Then:
```bash
gh auth login   # one-time GitHub auth
brainstem       # start the server → localhost:7071
```

### Deploy to Azure

```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/deploy.sh | bash
```

Or click: [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Faibast-agents-library%2Fmain%2Fazuredeploy.json)

---

## Architecture

The system uses a three-tier architecture designed for progressive learning of the Microsoft AI stack:

### 🧠 Tier 1: The Brainstem (Local)

A local Flask server powered by GitHub Copilot. No API keys needed beyond a GitHub account. Define a **soul** (system prompt), drop in **agents** (Python tools), and talk to it at `localhost:7071`.

### ☁️ Tier 2: The Spinal Cord (RAPP on Azure)

Deploy RAPP to Azure — the same agent logic from your brainstem, now always-on with Azure OpenAI, persistent Azure File Storage, and Application Insights monitoring. One-click ARM template deployment. Agents hot-load from storage — no redeployment needed.

```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/deploy.sh | bash
```

Or click: [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Faibast-agents-library%2Fmain%2Fazuredeploy.json)

### 🤖 Tier 3: The Nervous System (Copilot Studio)

Connect your agent to Teams and M365 Copilot using Copilot Studio. Two paths:

- **Import the Power Platform solution** — The included `MSFTAIBASMultiAgentCopilot_*.zip` wires a declarative agent to your Azure Function. Same agent logic, now in Teams and M365 Copilot across your org.
- **Go native with [Skills for Copilot Studio](https://github.com/microsoft/skills-for-copilot-studio)** — Use the CAT team's open-source plugin for Claude Code or GitHub Copilot CLI to author Copilot Studio agents directly as YAML — up to 20x faster. Describe your agent requirements in natural language, push YAML to Copilot Studio, and deploy without the Azure Function dependency.

  ```
  /plugin marketplace add microsoft/skills-for-copilot-studio
  @copilot-studio:author Build an agent for [your use case]...
  ```

---

## Agent Library

104 industry agent **templates** across 14 verticals. These are starting points — each template provides the structure, prompts, and logic for a business function, but must be customized to fit your specific data sources, business rules, and integrations before deployment.

| Vertical | Agents | Examples |
|----------|--------|----------|
| B2B Sales | 23 | Account intelligence, deal progression, proposal generation, win/loss analysis |
| General | 22 | AI customer assistant, CRM data seeder, sales coach, triage bot |
| Financial Services | 10 | Claims processing, fraud detection, loan origination, portfolio rebalancing |
| B2C Sales | 7 | Cart abandonment, loyalty rewards, omnichannel engagement |
| Energy | 5 | Asset maintenance, emission tracking, field service dispatch |
| Federal Government | 5 | Acquisition support, grants oversight, regulatory compliance |
| Healthcare | 5 | Care gap closure, clinical notes, patient intake, prior authorization |
| Manufacturing | 5 | Inventory rebalancing, maintenance scheduling, production optimization |
| Professional Services | 5 | Client health score, contract risk review, resource utilization |
| Retail / CPG | 5 | Inventory visibility, personalized marketing, supply chain alerts |
| State & Local Government | 5 | Building permits, citizen services, FOIA requests |
| Software / Digital Products | 5 | Competitive intel, customer onboarding, license renewal |
| Human Resources | 1 | Ask HR |
| IT Management | 1 | IT Helpdesk |

### Install an Agent

Point any LLM or AI agent at the skill manifest:
```
https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skill.md
```

Or manually:
```bash
cp agents/@aibast-agents-library/healthcare_stacks/care_gap_closure_stack/care_gap_closure_agent.py \
   /path/to/your/agents/care_gap_closure_agent.py
```

### Package Structure

Every agent is a **single `.py` file** with a `__manifest__` dict embedded inside. No separate manifest.json. No README.md per agent. One file = one agent.

```
agents/@aibast-agents-library/
├── b2b_sales_stacks/           # 5 stacks, ~23 agents
├── b2c_sales_stacks/           # 7 stacks
├── energy_stacks/              # 5 stacks
├── federal_government_stacks/  # 5 stacks
├── financial_services_stacks/  # 10 stacks
├── general_stacks/             # 17+ stacks
├── healthcare_stacks/          # 5 stacks
├── human_resources_stacks/     # 1 stack
├── it_management_stacks/       # 1 stack
├── manufacturing_stacks/       # 5 stacks
├── professional_services_stacks/ # 5 stacks
├── retail_cpg_stacks/          # 5 stacks
├── slg_government_stacks/      # 5 stacks
├── software_dp_stacks/         # 5 stacks
└── templates/                  # BasicAgent base class + utility templates
```

---

## Build & Validate

```bash
# Build the agent registry (auto-generates registry.json)
python build_registry.py

# Run tests
pytest
```

---

## Documentation

| Resource | Description |
|----------|-------------|
| [RAPP Production Guide](index.html) | Complete 14-step workflow from discovery to post-deployment |
| [RAPP Installer](docs/installer.html) | One-liner install, Azure deploy, Copilot Studio setup |
| [CONSTITUTION.md](CONSTITUTION.md) | Governing document for agent standards |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute agents |
| [skill.md](skill.md) | Machine-readable AI interface for agent discovery |

---

## Current Limitations

> ⚠️ **IMPORTANT:** This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications Specialist Team (AIBAST), not an officially supported Microsoft product.

This project is still in beta. Even if we're optimizing it for best-practice adherence, by using it you might sometimes experience unwanted patterns, errors, or simply bad architectures. By filing a [GitHub issue in the project repo](https://github.com/microsoft/aibast-agents-library/issues) you will help us improve these tools.

A few additional things to keep in mind:

- **Agent templates are starting points, not turnkey solutions.** Each template provides the structure, system prompts, and logic scaffold for a specific business function. Users must customize them with AI (e.g., via the RAPP pipeline or Copilot) or manually to adapt to their specific data sources, business rules, APIs, and deployment environment before production use.
- **AI-generated output may contain errors or unsupported patterns.** The agent templates reduce this significantly compared to a general-purpose model, but human review remains important.
- **The project is evolving quickly.** We're actively improving it based on feedback.

If you've used these tools, opened an issue, or simply have spent some time with this project and have feedback — we want to hear from you. Open a [GitHub issue](https://github.com/microsoft/aibast-agents-library/issues).

---

## Microsoft Open Source Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

Resources:

- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- [Microsoft Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
- Contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with questions or concerns

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.

## Security

Microsoft takes the security of our software products and services seriously, which includes all source code repositories managed through our GitHub organizations.

If you believe you have found a security vulnerability in any Microsoft-owned repository that meets [Microsoft's definition of a security vulnerability](https://docs.microsoft.com/en-us/previous-versions/tn-archive/cc751383(v=technet.10)), please report it to the Microsoft Security Response Center (MSRC) at [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report).

**Please do not report security vulnerabilities through public GitHub issues.**

## License

MIT License - Copyright (c) 2026 Microsoft

See [LICENSE](LICENSE) for full details.
