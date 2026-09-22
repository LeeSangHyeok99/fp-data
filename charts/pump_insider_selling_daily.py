"""
PUMP Insider Selling Since the July Cliff Unlock, daily basis, four-pillars bar.
Reproduction of a reference chart (image mode), internalized into our own pipeline.
Data extracted from the reference image (pixel-estimated), no title/subtitle/legend/source.
Data: outputs/data/pump_insider_selling_daily.csv
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, apply_style, DPI, gradient_rounded_bar

setup_font()

PUMP_GREEN = "#55d292"

df = pd.read_csv("outputs/data/pump_insider_selling_daily.csv", parse_dates=["date"])
df["x"] = mdates.date2num(df["date"])

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)

x0, x1 = df["x"].min() - 1.0, df["x"].max() + 1.0
ax.set_xlim(x0, x1)
ax.set_ylim(0, 1.05e9)

for r in df.itertuples():
    if r.pump_sold > 0:
        gradient_rounded_bar(ax, r.x, 0.6, r.pump_sold, PUMP_GREEN, floor=0.35, round_top=False)

tick_dates = pd.to_datetime(
    ["2026-07-15", "2026-07-20", "2026-07-25", "2026-07-30", "2026-08-05"]
)
ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(tick_dates)))
ax.xaxis.set_major_formatter(FuncFormatter(
    lambda v, _: mdates.num2date(v).strftime("%b") + " " + str(mdates.num2date(v).day)
))

ax.yaxis.set_major_locator(FixedLocator([0, 0.25e9, 0.5e9, 0.75e9, 1e9]))
ax.yaxis.set_major_formatter(FuncFormatter(
    lambda v, _: "1B" if v >= 1e9 else f"{v/1e6:.0f}M"
))

apply_style(fig, ax, "bar")
ax.tick_params(axis="x", rotation=0, labelsize=15, length=6, width=1,
                color="#787b86")
ax.tick_params(axis="y", labelsize=15, length=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")

out_dir = "outputs/charts/pump/token"
Path(out_dir).mkdir(parents=True, exist_ok=True)
name = "pump_insider_selling_daily"
for ext in ("png", "svg"):
    fig.savefig(f"{out_dir}/{name}.{ext}", dpi=DPI, facecolor="none",
                edgecolor="none", bbox_inches="tight", transparent=True)

print(f"saved {out_dir}/{name}.png and .svg")
