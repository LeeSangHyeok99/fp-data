# fp-data

Four Pillars data-visualization workspace containing chart scripts, source
datasets, reusable Claude agents, and a browsable chart archive.

## Repository map

| Path | Contents |
|---|---|
| `chart-library/by-type/` | Generated charts copied and grouped by visual type |
| `chart-library/manifest.csv` | Source path, inferred type, matching script, size, and SHA-256 |
| `charts/` | Python chart-generation scripts |
| `scripts/` | Data collection and transformation utilities |
| `sources/` | Source datasets and captured API responses |
| `.claude/` | Chart and validation agents, skills, configuration, and docs |

Rebuild the archive from local generated outputs with:

```bash
python3 scripts/organize_chart_library.py
```

Newsletter week folders and newsletter-only agents are intentionally excluded
from this repository.
