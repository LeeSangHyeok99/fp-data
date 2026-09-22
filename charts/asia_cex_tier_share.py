"""Asia CEX — Volume by asset tier, 100% stacked area, 4 venues in one figure (2x2).
Tiers BTC / ETH / Other majors / Tail stacked bottom to top.
Source: asia-cex-analytics.vercel.app (D_TAIL.tail.tier_vol + D_API.benchmark_history.exchanges).
"""
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import DPI, COLORS, GRID_CONFIG, setup_font  # noqa: E402

TIER = {"btc": "#c98500", "eth": "#5b66e8", "majors": "#199e70", "tail": "#c8489b"}
STACK = ["btc", "eth", "majors", "tail"]  # bottom -> top

VENUES = [
    ("upbit", "Upbit", "#4d8dff"),
    ("bithumb", "Bithumb", "#ff8a3d"),
    ("binance", "Binance", "#caa204"),
    ("coinbase", "Coinbase", "#5b8def"),
]

setup_font()
frames = {}
xmin, xmax = None, None
for key, _, _ in VENUES:
    df = pd.read_csv(f"outputs/data/asia_cex_tier_share_{key}.csv")
    df["date"] = pd.to_datetime(df["w"], unit="s")
    frames[key] = df
    lo, hi = df["date"].min(), df["date"].max()
    xmin = lo if xmin is None else min(xmin, lo)
    xmax = hi if xmax is None else max(xmax, hi)

gray = COLORS["text_secondary"]

for key, label, brand in VENUES:
    df = frames[key]
    x = df["date"]
    fig, ax = plt.subplots(figsize=(6.2, 3.9), dpi=DPI)  # ~1.6:1 for 2x2 infographic
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.stackplot(x, *[df[t] for t in STACK],
                 colors=[TIER[t] for t in STACK], alpha=0.92, edgecolor="none")

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, 100)
    ax.margins(x=0, y=0)

    ax.yaxis.set_major_locator(FixedLocator([0, 50, 100]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
    ax.xaxis.set_major_locator(mdates.YearLocator(month=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", labelsize=14, colors=gray, length=0, pad=6)
    ax.tick_params(axis="x", labelsize=12, colors=gray, length=0, pad=6,
                   rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha="right", rotation_mode="anchor")
    ax.grid(True, axis="y", color=GRID_CONFIG["color"], alpha=0.35,
            linestyle=GRID_CONFIG["linestyle"], linewidth=1.0)
    ax.set_axisbelow(False)

    # panel identity: brand dot + venue name, top-left inside panel
    ax.scatter([0.03], [0.9], s=60, color=brand, transform=ax.transAxes,
               zorder=6, edgecolors="none", clip_on=False)
    ax.text(0.075, 0.9, label, transform=ax.transAxes, color="#f0f2f5",
            fontsize=14, fontweight="bold", va="center", ha="left", zorder=6)

    # fixed margins (not tight bbox) so all 4 export at identical dimensions;
    # extra bottom room for the rotated x labels so they never clip
    fig.subplots_adjust(left=0.145, right=0.985, top=0.925, bottom=0.24)
    SAVE_DPI = 85.5  # 6.2in * 85.5 ~= 530px wide
    outdir = Path("outputs/charts/asia-cex/tail")
    outdir.mkdir(parents=True, exist_ok=True)
    base = outdir / f"asia_cex_tier_share_{key}"
    fig.savefig(f"{base}.png", dpi=SAVE_DPI, transparent=True,
                facecolor="none", edgecolor="none")
    fig.savefig(f"{base}.svg", transparent=True,
                facecolor="none", edgecolor="none")
    print(f"{base}.png")
    plt.close(fig)

# sanity: Binance BTC dominance peaked >65% in late 2022 (Oct '22)
b = frames["binance"]
assert b["btc"].max() > 65 and frames["upbit"]["tail"].max() > 75
