# Claude Agent System

This directory contains the repository-local agents, reusable skills, shared
configuration, and operating notes for the chart production workflow.

## Start here

| Path | Purpose |
|---|---|
| `agents/` | Thin controllers that route chart creation and validation work |
| `skills/` | Reusable chart, data, design, and output instructions |
| `config/` | Project paths, defaults, and approved data-source definitions |
| `docs/ARCHITECTURE.md` | System structure and data flow |
| `memory/` | Durable project-specific feedback |

## Skill catalog

| Skill | Responsibility |
|---|---|
| `chart` | Line, area, bar, stacked, pie, and donut chart rules |
| `data` | Source collection, parsing, and two-source validation |
| `design` | Four Pillars and HRC visual systems |
| `output` | PNG, SVG, HTML, CSV, and JSON export contracts |

Agent definitions should coordinate work and delegate detailed rules to skills.
New reusable behavior belongs in `skills/<name>/SKILL.md`; project-wide paths
and defaults belong in `config/settings.json`.
