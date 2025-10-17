# AI BAST Agents Library

Main repository for the AI BAST (Business Applications Specialist Team) AI Agents Library - a Microsoft framework for building and deploying AI agent automation capabilities.

## Overview

This framework enables rapid development and deployment of AI agents integrated with Microsoft 365, Teams, and Copilot Studio. It implements the **Rapid Agent Prototype Pattern (RAPP)** - a structured 14-step process from customer discovery through production deployment, with built-in validation checkpoints to ensure customer alignment at every stage.

## Architecture

The system uses a three-layer architecture designed for scalability, flexibility, and rapid iteration:

### 1. Orchestration Layer
- **Components**: Copilot Studio + Power Automate
- **Purpose**: Handles routing, UI, and channel management across M365 Copilot, Teams, Web, Mobile, and Voice

### 2. Intelligence Layer
- **Components**: Stateless Azure Function App (~500 lines of code)
- **Purpose**: Dynamically loads and executes agents on each request
- **Benefits**: Enables infinite horizontal scaling for concurrent users

### 3. Memory Layer
- **Components**: Azure File Storage
- **Purpose**: Stores agent code and user context
- **Location**: `memory/{user-guid}/agents/`

## Key Features

- **Zero-Downtime Updates**: Agents hot-load from Azure File Storage - drop in a new Python file and it's live instantly
- **Universal Memory**: Context persists across Teams, Web, and Mobile interfaces, stored by `user_guid`
- **Stateless Design**: Every request is self-contained, enabling trivial horizontal scaling
- **Multi-Channel Support**: Same AI and context work across Teams, web, mobile, and voice interfaces
- **Modular Agents**: Self-documenting Python agents that are dynamically loaded at runtime

## Documentation

The comprehensive framework documentation is available in `index.html`, covering:
- Complete Rapid Agent Prototype Pattern (RAPP) 14-step workflow from discovery to post-deployment
- Architecture diagrams and business justifications
- Audit checkpoints and validation gates
- Team scaling and resource management
- Cost analysis and timeline estimates

## Agent Development

Agents are Python files that:
- Follow a modular, self-documenting template pattern
- Are stored in Azure File Storage and dynamically loaded by the Intelligence Layer
- Work seamlessly across multiple interfaces without modification
- Require no redeployment when updated

## License

MIT License - Copyright (c) 2025 Microsoft

See [LICENSE](LICENSE) for full details.
