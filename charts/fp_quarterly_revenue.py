"""
Quarterly Revenue and the Flat Tokenization Line — four-pillars bar.
Reproduction of the FP reference (bars + value labels + flat tokenization
line and its two annotations). No title/subtitle/brand/source/y-label.
Data: outputs/data/fp_quarterly_revenue.csv
"""

import sys
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

df = pd.read_csv("outputs/data/fp_quarterly_revenue.csv")
x = np.arange(len(df))

GREEN, PURPLE = "#6EE7B7", "#6C5CE7"
LINE, DOT = "#A78BFA", "#C4B5FD"
colors = [PURPLE if h else GREEN for h in df["highlight"]]

fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=DPI)

for xi, v, col in zip(x, df["total_revenue"], colors):
    gradient_rounded_bar(ax, xi, 0.62, v, col, floor=0.5, round_top=False)
for xi, v in zip(x, df["total_revenue"]):
    ax.text(xi, v + 0.6, f"${v:.1f}M", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color="#ffffff", zorder=5)

# Flat tokenization line (dashed) with endpoint dots.
tok = df["tokenization"]
i0, i1 = tok.first_valid_index(), tok.last_valid_index()
ax.plot([x[i0], x[i1]], [tok[i0], tok[i1]], ls=(0, (6, 4)), lw=2.2,
        color=LINE, zorder=4)
ax.scatter([x[i0], x[i1]], [tok[i0], tok[i1]], s=60, color=DOT, zorder=5)
ax.text(1.5, tok[i0] + 1.5, r"Tokenization revenue \$11.3M to \$11.1M, down 1%",
        ha="center", va="bottom", fontsize=11, fontweight="bold", color=LINE,
        zorder=5)

# PCAOB annotation pointing to the Q4 bar.
ax.annotate("\\$6.4M PCAOB Deferral +\nIntegration Timing",
            xy=(3, 6.9), xytext=(3.05, 16.6),
            ha="center", va="bottom", fontsize=11.5, fontweight="bold",
            color="#c7ccd3", zorder=5,
            arrowprops=dict(arrowstyle="-", color="#8b9099", lw=1.2))

ax.set_xticks(x)
ax.set_xticklabels(df["quarter"])
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, 26)
ax.yaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))
ax.yaxis.set_major_formatter(lambda v, _: f"${v:.0f}M")

apply_style(fig, ax, "bar")
ax.tick_params(axis="x", rotation=0, labelsize=15)
ax.tick_params(axis="y", labelsize=15)

out_dir = "outputs/charts/four_pillars/revenue"
Path(out_dir).mkdir(parents=True, exist_ok=True)
TARGET_W = 550
fig.canvas.draw()
bb = fig.get_tightbbox(fig.canvas.get_renderer())
dpi = TARGET_W / bb.width
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/fp_quarterly_revenue.{ext}", dpi=dpi,
                facecolor="none", edgecolor="none", bbox_inches="tight",
                transparent=True)

# SVG intrinsic width is figsize*72pt (DPI-independent); rewrite width/height
# to TARGET_W px so it embeds at the same size as the PNG. viewBox stays → content scales.
import re
svg_path = f"{out_dir}/fp_quarterly_revenue.svg"
svg = Path(svg_path).read_text()
w, h = (float(v) for v in re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg).groups())
svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
             f'width="{TARGET_W}" height="{TARGET_W * h / w:.1f}"', svg, count=1)
Path(svg_path).write_text(svg)
print("dpi", round(dpi, 1))
