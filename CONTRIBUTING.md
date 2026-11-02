# Contributing

Thanks for improving AgroDigital-AI.

- Keep the core usable without paid services or mandatory credentials.
- Never commit private field data, API keys, tokens or personal information.
- Do not claim a workflow is implemented unless tested.
- Document provenance, units, CRS, temporal context and limitations.
- Prefer small, independently testable modules.

Development: Python 3.10+, install with `python -m pip install -e .`, then run `python -m unittest discover -s tests -v`. Add tests for calculations/validation and update module documentation and roadmap. Pull requests should explain the operational problem, sources, assumptions, expected outputs and test evidence.
