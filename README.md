# ORBIT

ORBIT — Open Research & Broadcast Intelligence Terminal

A terminal-first, local-first AI research and intelligence environment for collecting, verifying, organizing, and synthesizing information from configurable sources.

## Project Vision

ORBIT is designed to turn a personal computer into a structured research terminal that can:

- collect information from RSS/API/web sources
- preserve source provenance and evidence
- organize research in markdown and Obsidian-friendly storage
- route requests through pluggable AI providers
- support local-first and offline operation
- provide a terminal experience inspired by agentic developer tools
- support sessions, memory, source health, diagnostics, and plugin/skill extensibility

The goal is not to replace source material with AI-generated summaries, but to create a system where source evidence, verification, and synthesis remain clearly separated.

## Why ORBIT exists

ORBIT sits between raw information sources and the user’s own knowledge base.

The intended workflow is:

1. User enters a research or investigation request in the terminal.
2. ORBIT opens a research session.
3. Source adapters fetch relevant data from RSS, APIs, sitemaps, or web sources.
4. Provenance and duplication checks are preserved.
5. AI routing selects the most appropriate model/provider.
6. Verification, synthesis, and reporting produce structured outputs.
7. Knowledge is stored in a markdown-based vault for later retrieval and recall.

## Project boundaries

SeaTrace is separate and is not being modified as part of ORBIT.

ORBIT is its own project with its own architecture, CLI, database, source ingestion, research workflows, and future Windows packaging path.

## Current project status

The project has evolved from a source-ingestion prototype into a broader ORBIT architecture and now includes:

- PostgreSQL-backed development database
- SQLAlchemy + Alembic persistence layer
- Source registry and synchronization logic
- RSS ingestion and article fingerprinting
- Duplicate protection
- Source health tracking
- Deterministic pytest coverage
- Textual/TUI CLI foundation
- Distributed subsystem layout for agent, AI, research, knowledge, sessions, plugins, and security

## Architecture overview

```text
User
  ↓
ORBIT Terminal / TUI
  ↓
Session + Agent Loop
  ↓
Research / Source / Knowledge Tools
  ↓
RSS / APIs / Sitemaps / Web Sources
  ↓
Evidence + Provenance
  ↓
AI Analysis / Verification / Synthesis
  ↓
Markdown / Knowledge Vault + Reports
```

## Major subsystems

### CLI

The ORBIT CLI is being rebuilt into modular components for:

- app lifecycle
- theming
- keybindings
- state management
- screens
- widgets
- renderers

### Agent

The agent layer is intended to provide:

- planning
- execution
- context handling
- memory
- checkpoints
- sub-agents
- event flow

### AI

The AI subsystem is designed to support provider-agnostic routing across:

- Gemini
- OpenRouter
- OpenAI
- Anthropic
- Ollama

### Sources

The sources layer supports a growing source ecosystem including:

- RSS
- Atom
- APIs
- Sitemaps
- web adapters

### Research

Research features target:

- search
- verification
- synthesis
- comparisons
- timelines
- reports
- citations

### Knowledge

The knowledge layer is intended to support:

- markdown vault storage
- note indexing
- entity recognition
- topics
- backlinks
- knowledge search

### Sessions, plugins, skills, and security

ORBIT is being structured around:

- persistent sessions and history
- skills and plugin extensibility
- permissions and security controls
- diagnostics and doctor checks
- watchlists, updater, and future server capabilities

## Current source and ingestion foundation

ORBIT includes a working source ingestion prototype that currently supports:

- PostgreSQL development database
- source registration and synchronization
- NASA RSS source integration
- article creation and deduplication
- source health monitoring
- defensive rollback on failed ingestion runs

The current prototype was validated with a deterministic test suite covering:

- database connectivity
- duplicate ingestion handling
- RSS parsing and fingerprint generation
- source health transitions
- source registration behavior

## CLI direction

The current user experience is terminal-first and inspired by modern agentic tools, but implemented independently. The target experience is a full-screen interactive research terminal with:

- natural-language requests
- slash commands such as /help, /status, /doctor, /exit
- transcript and activity visibility
- command palette and status controls
- persistent session flow

## Project structure

```text
ORBIT/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── docker-compose.yml
├── .github/
├── docs/
├── migrations/
├── data/
├── orbit/
├── app/
├── installer/
├── tests/
├── scripts/
└── ...
```

## Recent changes included in this project

This version establishes the ORBIT project foundation and includes the following important changes from the design brief:

- project identity separated from SeaTrace as a distinct ORBIT application
- PostgreSQL development database and Docker Compose setup
- Pydantic Settings configuration loading from .env
- SQLAlchemy + Alembic persistence layer
- source registry, NASA RSS source, and ingestion runner
- duplicate protection and article fingerprinting
- source health tracking and failure handling
- expanded modular ORBIT architecture for agent, AI, sources, research, knowledge, sessions, security, and server layers
- initial Textual CLI and reusable component structure for upcoming TUI work
- CI workflow files and project documentation scaffolding

## Development goals

The next major milestone is to complete the interactive terminal interface and reconnect the research and agent loop so the system can move from a working source prototype into a complete local research environment.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest
python -m orbit
```

## License

This project is distributed under the MIT License.

## Status

ORBIT is currently in an active architectural and prototype development phase, with a working backend foundation and the next major milestone focused on the terminal-first research experience.
