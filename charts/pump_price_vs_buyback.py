"""
PUMP Price vs. Buyback Spend, daily % change from Apr 29, 2026, four-pillars dual line.
Reproduction of a reference chart (image mode), internalized into our own pipeline.
Data extracted from the reference image via pixel calibration, endpoint snapped to
labeled ground truth (+57% / +22%). No title/subtitle/legend/source in the image.
Data: outputs/data/pump_price_vs_buyback.csv
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter
import matplotlib.dates as mdates

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, apply_style, DPI, endpoint_dot

setup_font()

PUMP_GREEN = "#55d292"
BUYBACK_WHITE = "#e4e4e7"

df = pd.read_csv("outputs/data/pump_price_vs_buyback.csv", parse_dates=["date"])

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)

ax.plot(df["date"], df["pump_price_pct"], color=PUMP_GREEN, linewidth=2, zorder=4)
ax.plot(df["date"], df["buyback_usd_pct"], color=BUYBACK_WHITE, linewidth=1.6, zorder=3)

endpoint_dot(ax, df["date"].iloc[-1], df["pump_price_pct"].iloc[-1], color=PUMP_GREEN, size=40)
endpoint_dot(ax, df["date"].iloc[-1], df["buyback_usd_pct"].iloc[-1], color=BUYBACK_WHITE, size=40)

# Cliff unlock event marker
event_date = pd.Timestamp("2026-07-14")
ax.axvline(x=event_date, color="#e4e4e7", linestyle="--", linewidth=0.8, alpha=0.45, zorder=2)
ax.text(event_date - pd.Timedelta(days=2), 56, "Jul 14, 2026\nCliff Unlock Lands, 84% of\nInsider Selling Clears by Jul 20",
        fontsize=10, fontweight="bold", color="#e4e4e7", alpha=0.85,
        ha="right", va="top", linespacing=1.6, clip_on=False)

# End-of-line values only (no legend, no series-name text; caller adds their own legend)
last_x = df["date"].iloc[-1]
ax.text(last_x + pd.Timedelta(days=2), df["pump_price_pct"].iloc[-1] - 5,
        "+57%", fontsize=18, fontweight="bold", color=PUMP_GREEN,
        ha="left", va="center", clip_on=False)
ax.text(last_x + pd.Timedelta(days=2), df["buyback_usd_pct"].iloc[-1] - 5,
        "+22%", fontsize=18, fontweight="bold", color=BUYBACK_WHITE,
        ha="left", va="center", clip_on=False)

ax.axhline(0, color="#787b86", linewidth=0.8, alpha=0.5, zorder=1)

ax.set_xlim(df["date"].min() - pd.Timedelta(days=1), last_x + pd.Timedelta(days=14))
ax.set_ylim(-65, 68)

ax.yaxis.set_major_locator(FixedLocator([-60, -30, 0, 30, 60]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%" if v else "0%"))

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: mdates.num2date(v).strftime("%b %Y")))

apply_style(fig, ax, "line")
ax.tick_params(axis="x", rotation=45, labelsize=14, length=6, width=1, color="#787b86")
ax.tick_params(axis="y", labelsize=14, length=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha="right")

out_dir = "outputs/charts/pump/token"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "pump_price_vs_buyback"
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=DPI, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)

print(f"saved {out_dir}/{name}.png and .svg")
