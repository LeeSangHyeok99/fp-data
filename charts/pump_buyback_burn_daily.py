"""
Pump.fun Daily Buyback and Burn, USD spent per day, four-pillars filled area.
Reproduction of a reference chart (image mode), internalized into our own pipeline.
Data extracted from the reference image via direct pixel/gridline calibration
(y-axis ticks -> $M, x-axis month ticks -> date), values NOT rescaled to the
disclosed $424.65M total: that total sits ~24% above the extracted sum, but the
peak bar already lines up with the reference's own ~$2.4M ceiling (just under its
$2.5M top gridline), so uniform rescaling would push the peak past what the
reference axis actually shows. Treat totals as approximate; per-day shape and
axis scale follow the reference image directly.
Attempted to source directly from pump.fun (fees.pump.fun / pump.fun/pump-token network
calls inspected via Playwright); no public daily buyback/burn API endpoint was found,
so this is an image-extraction reproduction per user's fallback instruction.
Data: outputs/data/pump_buyback_burn_daily.csv
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import FixedLocator, FuncFormatter
import matplotlib.dates as mdates

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, apply_style, DPI

setup_font()

PUMP_GREEN = "#55d292"


def gradient_bars_relative(ax, xs, heights, width, color, floor=0.35, n_segments=16):
    """Each bar gets its own dark-bottom-to-light-top sweep (relative to its own
    height), drawn as stacked solid-color bands instead of a per-bar raster image.
    One ax.bar call per band (same band = same color for every bar) keeps every
    bar's shade rendering identically instead of the per-bar imshow drifting at
    small pixel sizes."""
    xs = np.asarray(xs, dtype=float)
    heights = np.asarray(heights, dtype=float)
    r, g, b = mcolors.to_rgb(color)
    seg_h = heights / n_segments
    for k in range(n_segments):
        frac = (k + 0.5) / n_segments
        factor = floor + (1 - floor) * (frac ** 0.5)
        band_color = (r * factor, g * factor, b * factor)
        ax.bar(xs, seg_h, bottom=seg_h * k, width=width, color=band_color,
               linewidth=0, zorder=3)


df = pd.read_csv("outputs/data/pump_buyback_burn_daily.csv", parse_dates=["date"])
df["x"] = mdates.date2num(df["date"])

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)

BAR_WIDTH = 0.75
x0, x1 = df["x"].min() - 0.6, df["x"].max() + 0.6
ax.set_xlim(x0, x1)
ax.set_ylim(0, 3.0)

gradient_bars_relative(ax, df["x"].to_numpy(), df["buyback_burn_usd_m"].to_numpy(),
                        BAR_WIDTH, PUMP_GREEN, floor=0.35)

# Programmatic-buyback event marker
event_x = mdates.date2num(pd.Timestamp("2026-04-28"))
ax.axvline(x=event_x, color="#e4e4e7", linestyle="--", linewidth=0.8, alpha=0.6, zorder=4)
ax.text(event_x + 6, 2.85, "Apr 28, 2026\nBuyback Becomes Programmatic\nat 50% of Revenue",
        fontsize=10, fontweight="bold", color="#e4e4e7", alpha=0.9,
        ha="left", va="top", linespacing=1.6, clip_on=False)

ax.yaxis.set_major_locator(FixedLocator([0, 0.5, 1.0, 1.5, 2.0]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.1f}M" if v else "0"))

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 3, 5, 7, 9, 11]))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: mdates.num2date(v).strftime("%b %Y")))

apply_style(fig, ax, "area")
ax.tick_params(axis="x", rotation=45, labelsize=13, length=6, width=1, color="#787b86")
ax.tick_params(axis="y", labelsize=14, length=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha="right")

out_dir = "outputs/charts/pump/token"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "pump_buyback_burn_daily"
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=DPI, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)

print(f"saved {out_dir}/{name}.png and .svg")
