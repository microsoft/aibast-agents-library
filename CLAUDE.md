# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the AI BAST (Business Applications Solution Technologies) Specialist Teal AI Agents Library - a Microsoft project for building and deploying AI agent automation capabilities integrated with Microsoft 365, Teams, and Copilot Studio.

The framework implements the **Rapid Agent Prototype Pattern (RAPP)** - a 14-step process from customer discovery through production deployment, with a focus on rapid MVP validation and iterative customer feedback.

## Architecture

The system uses a three-layer architecture:

1. **Orchestration Layer**: Copilot Studio + Power Automate for routing and UI
2. **Intelligence Layer**: Stateless Azure Function App (~500 lines) that dynamically loads agents
3. **Memory Layer**: Azure File Storage for agent code and user context storage

**Key Design Principles**:
- Agents are hot-loaded from Azure File Storage (`memory/{user-guid}/agents/`) - no redeployment needed for updates
- Stateless function design enables infinite horizontal scaling
- Universal memory allows context persistence across Teams, Web, Mobile interfaces
- Memory stored by `user_guid`, not by interface

## Agent Development

Agents are Python files that are:
- Self-documenting and modular
- Stored in Azure File Storage and dynamically loaded
- Designed to work across multiple interfaces (Teams, web, mobile, voice)

Agent files should follow the template pattern for consistency with the framework's dynamic loading system.

## Documentation

The primary framework documentation is in `index.html` - a comprehensive production guide covering:
- Complete Rapid Agent Prototype Pattern (RAPP) 14-step workflow from discovery to post-deployment
- Architecture diagrams and business justifications
- Audit checkpoints and validation gates
- Team scaling and resource management
- Cost analysis and timeline estimates

This HTML file serves as both technical documentation and client-facing material.

## License

This project uses the MIT License (Copyright 2025 Microsoft).
