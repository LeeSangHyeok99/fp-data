"""Asia CEX — Tail share vs BTC share of 24h spot volume, grouped bars.
5 venues (Upbit, Bithumb, HashKey, Binance, Coinbase), 24h snapshot 2026-07-08.
Source: asia-cex-analytics.vercel.app (D_API.benchmark.exchanges[x].tier_share).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import COLORS, apply_style, create_figure, gradient_rounded_bar, save_chart  # noqa: E402

df = pd.read_csv("outputs/data/asia_cex_tail_vs_btc_24h.csv")
TAIL, BTC = "#c8489b", "#c98500"

x = np.arange(len(df))
w = 0.34

fig, ax = create_figure("bar")

# lock limits/ticks first so gradient corner-rounding maps to pixels correctly
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(FixedLocator([0, 20, 40, 60, 80, 100]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
ax.set_xticks(x)
ax.set_xticklabels(df["exchange"])
ax.set_xlim(-0.6, len(df) - 0.4)

# ~2px gap between the two bars of each group
px_per_unit = ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]
gap = 2 / px_per_unit
tail_c = w / 2 + gap / 2  # tail bar center offset from group center
btc_c = w / 2 + gap / 2

for xc, (_, row) in zip(x, df.iterrows()):
    # floor=0.55 keeps the gradient inside the same hue (dark shade -> bright),
    # instead of fading all the way to near-black
    gradient_rounded_bar(ax, xc - tail_c, w, row["tail"], TAIL, floor=0.55)
    gradient_rounded_bar(ax, xc + btc_c, w, row["btc"], BTC, floor=0.55)
    ax.text(xc - tail_c, row["tail"] + 1.8, f"{round(row['tail'])}%",
            ha="center", va="bottom", fontsize=17, fontweight="bold",
            color=COLORS["text"])
    ax.text(xc + btc_c, row["btc"] + 1.8, f"{round(row['btc'])}%",
            ha="center", va="bottom", fontsize=17, fontweight="bold",
            color=COLORS["text"])

apply_style(fig, ax, "bar")
ax.tick_params(axis="x", rotation=0, length=0, labelsize=19)  # config 22 - 3
ax.tick_params(axis="y", labelsize=21)  # config 24 - 3
import matplotlib.pyplot as plt  # noqa: E402
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")

png, svg = save_chart(fig, "asia_cex_tail_vs_btc_24h",
                      "outputs/charts/asia-cex/tail")
print(png)
print(svg)

# sanity: Upbit most tail-heavy, Coinbase most BTC-heavy
assert df.loc[df["tail"].idxmax(), "exchange"] == "Upbit"
assert df.loc[df["btc"].idxmax(), "exchange"] == "Coinbase"
