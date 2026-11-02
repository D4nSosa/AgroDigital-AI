# Automation and reproducibility

Prefer small scripts with explicit inputs and outputs. Include Python version/dependencies; input paths and schema; CRS, units, dates, timezone and nodata assumptions; deterministic parameters; logging and actionable errors; output validation and provenance.

Use the portable CLI for basic validation/calculations, QGIS for interactive spatial review, and Colab/local Python for heavier computation. Never commit API keys, tokens or private field data. Load secrets from environment variables only when an integration genuinely requires them.
