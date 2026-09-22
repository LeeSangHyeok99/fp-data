"""
Platform Transaction Volume, Monthly Basis (Q1 25-Q1 26) — four-pillars bar.
Reproduction of Exhibit 19A, WITHOUT the "-87%" callout and its arrow.
Q4 25 not disclosed (n.d., no bar). No title/subtitle/brand/source/y-label.
Data: outputs/data/fp_platform_txn_volume.csv
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

df = pd.read_csv("outputs/data/fp_platform_txn_volume.csv")
x = np.arange(len(df))
GREEN, PURPLE = "#7EE6BD", "#6C5CE7"

fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=DPI)

# Limits first so the bar helper's pixel-based corner radius is correct.
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, 5.2)

for xi, r in zip(x, df.itertuples()):
    if r.disclosed:
        col = PURPLE if r.highlight else GREEN
        gradient_rounded_bar(ax, xi, 0.6, r.volume, col, floor=0.5, round_top=False)
        ax.text(xi, r.volume + 0.12, r.label, ha="center", va="bottom",
                fontsize=15, fontweight="bold", color="#ffffff", zorder=5)
    else:
        ax.text(xi, 0.45, "n.d.", ha="center", va="center",
                fontsize=14, fontweight="bold", color="#787b86", zorder=5)

ax.set_xticks(x)
ax.set_xticklabels(df["quarter"])
ax.yaxis.set_major_locator(FixedLocator([0, 1, 2, 3, 4]))
ax.yaxis.set_major_formatter(lambda v, _: f"${v:.0f}B")

apply_style(fig, ax, "bar")
ax.tick_params(axis="x", rotation=0, labelsize=15, length=0)
ax.tick_params(axis="y", labelsize=15, length=0)

out_dir = "outputs/charts/four_pillars/volume"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "fp_platform_txn_volume"
TARGET_W = 550
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_W / bb.width
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=dpi, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)
svg = Path(f"{out_dir}/{name}.svg").read_text()
w, h = (float(v) for v in re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg).groups())
svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
             f'width="{TARGET_W}" height="{TARGET_W * h / w:.1f}"', svg, count=1)
Path(f"{out_dir}/{name}.svg").write_text(svg)
print(f"{name}: {TARGET_W} x {TARGET_W * h / w:.0f} px")
