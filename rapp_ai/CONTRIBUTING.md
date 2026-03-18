# Contributing to CommunityRAPP

Thanks for your interest in contributing! This project powers the RAPP (Rapid Agent Prototyping Platform) ecosystem and welcomes community participation.

## Quick Start

1. **Read [`CONSTITUTION.md`](CONSTITUTION.md)** — the governing document for this repo
2. **Fork & clone** the repository
3. **Create a branch** following naming conventions (see below)
4. **Make your changes** and ensure tests pass
5. **Open a PR** against `main`

## Before You Write Code

Ask yourself:
- Does this serve the RAPP pipeline or agent runtime? → ✅ Proceed
- Does this add customer-specific content? → ❌ Use `.vault/` for local content
- Does this add a new agent? → ✅ Follow agent standards below
- Does this add a new top-level directory? → 🤔 Discuss first in an issue

## Agent Standards

Every agent MUST:
1. Inherit from `BasicAgent` (`agents/basic_agent.py`)
2. Define `name`, `metadata` (JSON schema), and `perform(**kwargs)`
3. Return a string result
4. Be a single file in `agents/`
5. **Be generic** — no hardcoded customer names, endpoints, or credentials

```python
from agents.basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyAgent'
        self.metadata = {
            "name": self.name,
            "description": "What this agent does",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return f"Result: {kwargs.get('input', '')}"
```

## Branch Naming

```
feature/agent-name        # New agent
fix/issue-description     # Bug fix
docs/topic                # Documentation
refactor/component        # Code improvement
```

## Pull Request Checklist

- [ ] Tests pass: `python tests/run_tests.py`
- [ ] No secrets or credentials in code
- [ ] No customer-specific content (names, endpoints, data)
- [ ] No hardcoded Azure resource names — use environment variables
- [ ] Agent follows `BasicAgent` contract (if applicable)
- [ ] CLAUDE.md updated (if architecture changed)
- [ ] CHANGELOG.md updated

## Running Tests

```bash
# All unit tests (mocked, no API keys needed)
python tests/run_tests.py

# Verbose output
python tests/run_tests.py -v

# Live API tests (requires environment variables)
python tests/run_tests.py --live
```

## The Golden Rule

> **If a thousand developers cloned this repo tomorrow, would your change help them — or confuse them?**

Customer-specific content belongs in `.vault/` (your local Obsidian workspace). The repo ships clean for everyone.

## Data Protection

**Never commit:**
- `local.settings.json` or files with API keys
- Customer names, email addresses, or PII
- Hardcoded Azure resource names or subscription IDs
- Customer-specific demo scripts or transpiled output

**Safe to commit:**
- Generic agent code with environment variable configuration
- Demo scripts using placeholder names
- Documentation with `YOUR_*` placeholders

## Getting Help

- Open an issue for bugs or feature requests
- Check `docs/` for architecture and API reference
- Read `CONSTITUTION.md` for governance questions

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
