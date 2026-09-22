"""
Base adjusted EBITDA margin (FY26E-FY30E) — four-pillars bar.
Sized to sit beside the scenario chart within 550px (common height).
Data: outputs/data/fp_base_ebitda_margin.csv
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
from config import setup_font, apply_style, DPI, gradient_rounded_bar

setup_font()

df = pd.read_csv("outputs/data/fp_base_ebitda_margin.csv")
x = np.arange(len(df))
GREEN = "#7EE6BD"

fig, ax = plt.subplots(figsize=(4.6, 5.0), dpi=DPI)

for xi, v in zip(x, df["margin"]):
    gradient_rounded_bar(ax, xi, 0.64, v, GREEN, floor=0.5, round_top=False)
for xi, v in zip(x, df["margin"]):
    ax.text(xi, v + 0.8, f"{v:.0f}%", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color="#ffffff", zorder=5)

ax.set_xticks(x)
ax.set_xticklabels(df["year"])
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, 46)
ax.yaxis.set_major_locator(FixedLocator([0, 10, 20, 30, 40]))
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

apply_style(fig, ax, "bar")
ax.tick_params(axis="x", rotation=0, labelsize=14)
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")  # override apply_style's ha="right" (for 45° labels)
ax.tick_params(axis="y", labelsize=14)

out_dir = "outputs/charts/four_pillars/revenue"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "fp_base_ebitda_margin"
TARGET_H = 217
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
