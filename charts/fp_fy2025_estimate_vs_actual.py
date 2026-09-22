"""
FY2025 Management Estimates vs Actual — four-pillars grouped bar.
Reproduction of the FP reference. Mixed-unit y-axis (AUM plotted x10), so no
y-axis: values are labeled on the bars. No legend/title/subtitle/source.
Data: outputs/data/fp_fy2025_estimate_vs_actual.csv
"""

import sys
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, DPI, gradient_rounded_bar

setup_font()

df = pd.read_csv("outputs/data/fp_fy2025_estimate_vs_actual.csv")
x = np.arange(len(df))
W = 0.4
PAD = 0.05  # gap between the purple/green pair within a group
EST, ACT = "#B9A6F5", "#6EE7B7"

fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

series = ((x - (W + PAD) / 2, "plot_estimate", "label_estimate", EST),
          (x + (W + PAD) / 2, "plot_actual", "label_actual", ACT))
for xs, hcol, lcol, col in series:
    for xc, h, txt in zip(xs, df[hcol], df[lcol]):
        gradient_rounded_bar(ax, xc, W, h, col, floor=0.5)
        ax.text(xc, h + 1.5, txt, ha="center", va="bottom",
                fontsize=15, fontweight="bold", color=col, zorder=5)

ax.set_xticks(x)
ax.set_xticklabels(df["metric"])
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, 80)

# No y-axis (mixed units); keep only x category labels.
ax.yaxis.set_visible(False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="x", length=0, labelsize=15, colors="#d1d4dc", pad=8)

out_dir = "outputs/charts/four_pillars/revenue"
Path(out_dir).mkdir(parents=True, exist_ok=True)
TARGET_W = 550
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_W / bb.width
name = "fp_fy2025_estimate_vs_actual"
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=dpi, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)

# Rewrite SVG intrinsic size to TARGET_W px (viewBox stays → content scales).
svg_path = f"{out_dir}/{name}.svg"
svg = Path(svg_path).read_text()
w, h = (float(v) for v in re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg).groups())
svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
             f'width="{TARGET_W}" height="{TARGET_W * h / w:.1f}"', svg, count=1)
Path(svg_path).write_text(svg)
print("dpi", round(dpi, 1))
