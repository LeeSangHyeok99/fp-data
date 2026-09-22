# Agents

The controllers in this directory are intentionally small. They define routing
and orchestration; reusable implementation rules live in `.claude/skills/`.

| Agent | Responsibility | Main dependencies |
|---|---|---|
| `chart.agent.md` | Load data, select a chart/design skill, render, and export | `chart`, `design`, `output` |
| `validator.agent.md` | Cross-check chart data against at least two sources | `config/sources.json` |

When adding an agent, keep the filename as `<name>.agent.md`, include YAML
frontmatter, and document the new controller in this table and in
`.claude/docs/ARCHITECTURE.md`.
