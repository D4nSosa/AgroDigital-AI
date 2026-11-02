# AgroDigital-AI

Open AgTech toolkit and modular assistant skill for agriculture, forestry, GIS, remote sensing and agrometeorology. Designed to work across ChatGPT Free/Pro and free external tools without requiring paid APIs.

## Quick start
Python 3.10+:

```bash
python -m pip install -e .
agrodigital check-geojson examples/sample_lot.geojson
agrodigital gdd --tmin 12 --tmax 28 --base 10
agrodigital rainfall 12.5 0 8 3.2
python -m unittest discover -s tests -v
```

Start with [SKILL.md](SKILL.md). Read [ChatGPT compatibility](docs/CHATGPT_COMPATIBILITY.md), [data policy](docs/DATA_POLICY.md), and [roadmap](docs/ROADMAP.md).

## Principles
- Free core; no mandatory API keys, paid services, or proprietary platform.
- Real evidence only: never invent data access, measurements, maps, or execution.
- Separate observed, derived, estimated, forecast, modelled, and illustrative values.
- Record provenance, dates, CRS, resolution, units, method, assumptions and limitations.
- Portable open formats and modular, testable workflows.

## Scope of v0.1
The Python core validates GeoJSON structure, computes normalized spectral differences (NDVI/NDWI) from supplied values/arrays, and performs basic GDD/rainfall calculations. It does not yet download satellite imagery, process GeoTIFFs, reproject data, or generate machinery prescriptions. See [ROADMAP.md](docs/ROADMAP.md).

MIT License. See [LICENSE](LICENSE).
