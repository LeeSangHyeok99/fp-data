"""
Valuation Summary (Bear/Base/Bull intrinsic value) — four-pillars horizontal bar.
Reference lines: last close $7.41 (white dashed) and weighted PT $14.50 (green).
No title/subtitle/brand/source. 550px wide.
Data: outputs/data/fp_valuation_summary.csv
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
from config import setup_font, DPI

setup_font()

df = pd.read_csv("outputs/data/fp_valuation_summary.csv")
y = np.arange(len(df))  # 0=Bull(bottom) .. 2=Bear(top)

LAST_CLOSE, PT = 7.41, 14.50
PT_COLOR = "#7EE6BD"

out_dir = "outputs/charts/four_pillars/valuation"
Path(out_dir).mkdir(parents=True, exist_ok=True)
TARGET_W = 550


def render(name, labels="outside"):
    fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.barh(y, df["value"], height=0.62, color=df["color"], zorder=3)
    for yi, v, col in zip(y, df["value"], df["color"]):
        if labels == "inside":  # value inside bar, black, right-aligned to bar end
            ax.text(v - 0.4, yi, f"${v:.2f}", ha="right", va="center",
                    fontsize=15, fontweight="bold", color="#111111", zorder=5)
        else:                   # value outside bar, in the bar's color
            ax.text(v + 0.5, yi, f"${v:.2f}", ha="left", va="center",
                    fontsize=15, fontweight="bold", color=col, zorder=5)

    # Reference lines (stop below the top labels, not through them).
    ax.axvline(LAST_CLOSE, color="#ffffff", lw=1.6, ls=(0, (5, 4)),
               ymin=0.02, ymax=0.80, zorder=4)
    ax.axvline(PT, color=PT_COLOR, lw=2.2, ymin=0.02, ymax=0.80, zorder=4)
    ax.text(LAST_CLOSE, 2.9, "Last Close\n$7.41", ha="center", va="bottom",
            fontsize=11.5, fontweight="bold", color="#c7ccd3", zorder=5)
    ax.text(PT, 2.9, "PT $14.50\n(Weighted)", ha="center", va="bottom",
            fontsize=11.5, fontweight="bold", color=PT_COLOR, zorder=5)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.scenario}\n{r.sublabel}" for r in df.itertuples()])
    ax.set_ylim(-0.6, 3.35)
    ax.set_xlim(0, 32)
    ax.xaxis.set_major_locator(FixedLocator([0, 10, 20, 30]))
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}")

    for s in ax.spines.values():
        s.set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color("#787b86")
    ax.spines["left"].set_linewidth(1.0)
    ax.tick_params(axis="y", length=0, labelsize=11.5, colors="#c7ccd3", pad=8)
    ax.tick_params(axis="x", length=0, labelsize=13, colors="#787b86", pad=6)

    fig.canvas.draw()
    dpi = TARGET_W / fig.get_tightbbox(fig.canvas.get_renderer()).width
    for ext in ("png", "svg"):
        fig.savefig(f"{out_dir}/{name}.{ext}", dpi=dpi, facecolor="none",
                    edgecolor="none", bbox_inches="tight", transparent=True)
    svg = Path(f"{out_dir}/{name}.svg").read_text()
    w, h = (float(v) for v in
            re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg).groups())
    svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
                 f'width="{TARGET_W}" height="{TARGET_W * h / w:.1f}"', svg, count=1)
    Path(f"{out_dir}/{name}.svg").write_text(svg)
    plt.close(fig)
    print(f"{name}: {TARGET_W} x {TARGET_W * h / w:.0f} px")


render("fp_valuation_summary", "outside")        # original (labels outside)
render("fp_valuation_summary_inside", "inside")  # values inside bars, black
