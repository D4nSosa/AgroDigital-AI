# AgroDigital-AI Skill

Portable, multipurpose Agent Skill for agriculture, forestry, soils, climate, environment, GIS, remote sensing and precision agriculture.

## Contents
- `SKILL.md`: activation metadata and core operating instructions.
- `references/`: domain methods, evidence rules, precision-agriculture guidance, tool-selection and reporting guidance.
- `scripts/`: small deterministic Python utilities. They do not require a server and do not download user data or remote imagery.

## Use
1. Download or clone the repository.
2. Copy the folder `skills/agrodigital-ai` into the Skills directory supported by your AI client, or upload its files if the client supports manual Skill import.
3. Start a conversation and attach the user's own photos, lot boundary, reports or datasets.
4. Ask a specific question. The Skill will select the relevant workflow and keep the answer focused.

The folder follows the open Agent Skills format. Clients differ in how they install, discover and execute Skills; consult the client's own instructions. A chatbot that can only read Markdown can still use the instructions and references, but may not execute bundled scripts.

## Monitoring and precision agriculture
The Skill supports field monitoring, comparison of platform outputs, exploratory management-zone delineation and preparation/review of draft prescription maps when appropriate data and execution tools are available. It does not claim direct integration with FieldView or another commercial platform, universal controller compatibility or automatic field application. Operational prescriptions require agronomic review, machine-format validation and equipment calibration. See `references/precision-agriculture.md`.

## Scripts
Run with Python 3.10+:
```bash
python scripts/validate_geojson.py --help
python scripts/calculate_indices.py --help
python scripts/calculate_gdd.py --help
```

These scripts are intentionally small and transparent. They operate only on supplied local files. Advanced GeoTIFF, STAC and Sentinel-2 processing remains in the main AgroDigital-AI Python package and requires its optional dependencies and a suitable execution environment.

## Execution honesty
A repository source is not a local clone or runtime. The Skill requires assistants to distinguish execution of original repository tools from an alternative implementation, code-only answers, conceptual workflows and illustrative examples. See `references/evidence-and-sources.md`.

## Data privacy
No lot images, sample farm records or user datasets are included. Users attach their own materials directly to their chosen AI client. Review any Skill scripts before executing them.
