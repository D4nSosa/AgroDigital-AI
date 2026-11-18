# AgroDigital-AI — repository entry point

This file is a short entry point for agents that inspect the repository root. The canonical, installable Agent Skill is `skills/agrodigital-ai/SKILL.md`; do not treat this file as a second independent Skill or merge its contents with the canonical Skill.

For the complete repository-level AI workflow, read `AGENT_ENTRYPOINT.md` when present. For package installation, supported commands, security boundaries and current capabilities, read `README.md` and `docs/AI_AGENT_GUIDE.md`.

Canonical Skill metadata and version are maintained only in `skills/agrodigital-ai/SKILL.md`. The Python package version is maintained in `src/agrodigital/__init__.py` and `pyproject.toml`.

A repository link is context, not installation or tool access. Never claim that Python, MCP, Google Earth Engine, Colab, network access or external data sources are available unless the current session actually provides them. Separate observed, retrieved, derived, estimated, forecast and illustrative outputs. Never invent data, execution, files, maps or citations.
