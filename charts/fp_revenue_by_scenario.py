"""
Revenue by scenario (Bear/Base/Bull, FY25A-FY30E) — four-pillars multi-line.
Sized to sit beside the EBITDA-margin chart within 550px (common height).
No title/legend/y-label; series named at their right endpoints.
Data: outputs/data/fp_scenario_projection.csv
"""

import sys
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, apply_style, DPI

setup_font()

df = pd.read_csv("outputs/data/fp_scenario_projection.csv").set_index("scenario")
fy = ["FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]
xlabels = ["FY25A", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E"]
x = np.arange(len(fy))

COLORS = {"Bull": "#45C4C0", "Base": "#7EE6BD", "Bear": "#B9A6F5"}

fig, ax = plt.subplots(figsize=(7.0, 5.0), dpi=DPI)

for name in ("Bull", "Base", "Bear"):
    y = df.loc[name, fy].astype(float).values
    ax.plot(x, y, color=COLORS[name], lw=2.4, marker="o", ms=5,
            markerfacecolor=COLORS[name], markeredgecolor="none", zorder=3)
    ax.text(x[-1] + 0.12, y[-1], f"{name} ${y[-1]:,.0f}M", ha="left", va="center",
            fontsize=13, fontweight="bold", color=COLORS[name], zorder=4)

ax.set_xticks(x)
ax.set_xticklabels(xlabels)
ax.set_xlim(-0.15, 6.9)
ax.set_ylim(0, 1500)
ax.yaxis.set_major_locator(FixedLocator([0, 500, 1000, 1500]))
ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}M")

apply_style(fig, ax, "line")
ax.tick_params(axis="x", rotation=45, labelsize=14)
plt.setp(ax.xaxis.get_majorticklabels(), ha="right")
ax.tick_params(axis="y", labelsize=14)

out_dir = "outputs/charts/four_pillars/revenue"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "fp_revenue_by_scenario"
TARGET_H = 217  # common height; line+bar+gap fits 550px
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_H / bb.height
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=dpi, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)
svg = Path(f"{out_dir}/{name}.svg").read_text()
w, h = (float(v) for v in re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg).groups())
px_w = TARGET_H * w / h
svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
             f'width="{px_w:.1f}" height="{TARGET_H}"', svg, count=1)
Path(f"{out_dir}/{name}.svg").write_text(svg)
print(f"{name}: {px_w:.0f} x {TARGET_H} px")
