"""Asia CEX — Post-listing liquidity (median weekly USD, log scale).
Upbit median + p25-p75 band (thin dashed), Bithumb median solid,
Binance/Coinbase median dashed benchmarks.
Source: asia-cex-analytics.vercel.app (D_LISTINGS.lifecycle + D_API.benchmark_history.listing).
"""
import sys
from pathlib import Path

import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import apply_style, create_figure, save_chart  # noqa: E402

df = pd.read_csv("outputs/data/asia_cex_post_listing_liquidity.csv")
w = df["week"]

C = {"upbit": "#4d8dff", "bithumb": "#ff8a3d", "binance": "#caa204", "coinbase": "#5b8def"}
DASH = (0, (6, 3))

fig, ax = create_figure("line")

# Upbit p25-p75 band as thin dashed lines
for col in ["upbit_p25", "upbit_p75"]:
    ax.plot(w, df[col], color=C["upbit"], linewidth=1.1, linestyle=(0, (4, 2)),
            alpha=0.55, zorder=3)

# medians
ax.plot(w, df["binance_med"], color=C["binance"], linewidth=2.4, linestyle=DASH,
        dash_capstyle="round", zorder=4)
ax.plot(w, df["coinbase_med"], color=C["coinbase"], linewidth=2.4, linestyle=DASH,
        dash_capstyle="round", zorder=4)
ax.plot(w, df["upbit_med"], color=C["upbit"], linewidth=2.6,
        solid_capstyle="round", zorder=5)
ax.plot(w, df["bithumb_med"], color=C["bithumb"], linewidth=2.6,
        solid_capstyle="round", zorder=5)

ax.set_yscale("log")
ax.set_xlim(w.min(), w.max())
ax.set_ylim(1e6, 1e9)


def fmt_usd(v, _):
    if v >= 1e9:
        return f"${v/1e9:.0f}B"
    return f"${v/1e6:.0f}M"


ax.yaxis.set_major_locator(FixedLocator([1e6, 1e7, 1e8, 1e9]))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_usd))
ax.yaxis.set_minor_locator(FixedLocator([]))
ax.xaxis.set_major_locator(FixedLocator(list(range(0, 51, 5))))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"W{int(v)}"))

apply_style(fig, ax, "line")
ax.tick_params(axis="x", rotation=0)
import matplotlib.pyplot as plt  # noqa: E402
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")

png, svg = save_chart(fig, "asia_cex_post_listing_liquidity",
                      "outputs/charts/asia-cex/listings")
print(png)
print(svg)

# sanity: W51 medians match source tooltip scale
r = df[df.week == 51].iloc[0]
assert round(r.upbit_med / 1e6, 1) == 11.3 and round(r.bithumb_med / 1e6, 1) == 2.2
