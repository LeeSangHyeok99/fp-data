"""Asia CEX — Liquidity retention (survival) curve.
% of listings still trading >10% of debut liquidity, by week since listing.
Korean exchanges (Upbit, Bithumb) solid; US benchmarks (Binance, Coinbase) dashed.
Source: asia-cex-analytics.vercel.app (D_LISTINGS.survival + D_API.benchmark_history).
"""
import sys
from pathlib import Path

import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import apply_style, create_figure, save_chart  # noqa: E402

df = pd.read_csv("outputs/data/asia_cex_liquidity_survival.csv")
w = df["week"]

SERIES = [
    ("upbit", "#4d8dff", "solid"),
    ("bithumb", "#ff8a3d", "solid"),
    ("binance", "#caa204", "dashed"),
    ("coinbase", "#5b8def", "dashed"),
]

fig, ax = create_figure("line")

for col, color, style in SERIES:
    ax.plot(
        w, df[col], color=color, linewidth=2.4,
        linestyle=(0, (6, 3)) if style == "dashed" else "solid",
        solid_capstyle="round", dash_capstyle="round", zorder=4,
    )

ax.set_xlim(w.min(), w.max())
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
ax.xaxis.set_major_locator(MultipleLocator(5))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"W{int(v)}"))

apply_style(fig, ax, "line")
ax.tick_params(axis="x", rotation=0, labelsize=20)  # config 22 - 2
ax.tick_params(axis="y", labelsize=22)  # config 24 - 2
import matplotlib.pyplot as plt  # noqa: E402
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")

png, svg = save_chart(fig, "asia_cex_liquidity_survival",
                      "outputs/charts/asia-cex/listings")
print(png)
print(svg)

# sanity: Week 51 must match source tooltip
row = df[df.week == 51].iloc[0]
assert abs(row.upbit - 42.71) < 0.01 and abs(row.binance - 43.58) < 0.01, "data drift"
