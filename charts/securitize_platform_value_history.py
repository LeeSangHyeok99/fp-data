"""
Securitize Platform Value History by Product — four-pillars stacked area.
Reference: rwa.xyz Exhibit 15B (Securitize Metrics, Total Value), as of 07/06/2026.
Source: sources/rwa-token-timeseries-export-1783317290925.csv (per-product daily $).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import setup_font, apply_style, COLORS, DPI

setup_font()

SRC = "sources/rwa-token-timeseries-export-1783317290925.csv"
df = pd.read_csv(SRC)
df["date"] = pd.to_datetime(df["Date"])
prod_cols = [c for c in df.columns if c not in ("Timestamp", "Date", "Measure", "date")]
df = df.set_index("date")[prod_cols].fillna(0.0) / 1e9  # $B
df = df[df.index >= "2024-01-01"]

# Rank products by latest value. Ascending so the largest stacks on top.
order = df.iloc[-1].sort_values(ascending=True).index.tolist()

# --- palette 1 (legend): 5 named products from the user's 6-item legend,
#     every other product collapses into a single "Others" gray band ---
OTHERS = "#8e8e8e"
# Colors sampled pixel-exact from the rwa.xyz legend dots (7/9/26 screenshot).
LEGEND_MAP = {
    "BlackRock USD Institutional Digital Liquidity Fund": "#f19732",
    "Blockchain Capital III Digital Liquid Venture Fund":  "#9b8bb4",
    "Securitize AAA CLO Tokenized Fund, Ltd":              "#fda764",
    "Securitize Corp.":                                    "#302b94",
    "Apollo Diversified Credit Securitize Fund":           "#a4def2",
}
legend_colors = [LEGEND_MAP.get(name, OTHERS) for name in order]

# --- palette 2 (full): original per-product colors (kept as the _full variant) ---
FULL_MAP = {
    "BlackRock USD Institutional Digital Liquidity Fund": "#f19732",
    "Blockchain Capital III Digital Liquid Venture Fund":  "#9f9f9f",
    "Securitize AAA CLO Tokenized Fund, Ltd":              "#fda764",
    "VanEck Treasury Fund":                                "#8bdbf1",
    "Securitize Corp.":                                    "#302b94",
    "Mantle Index Four Fund":                              "#e13d3e",
    "Apollo Diversified Credit Securitize Fund":           "#5d786e",
    "Exodus Movement Inc. (Class B)":                      "#5f29f6",
    "Exodus Movement":                                     "#1f62f7",
    "SPiCE VC":                                            "#ee662d",
    "Cosimo X":                                            "#20b69c",
    "Science Blockchain":                                  "#1e3443",
    "Preservation Fund II, LLP":                           "#1a6a5f",
    "CURRENC Group Inc.":                                  "#fc7024",
    "Re Member Fund LP":                                   "#fc7024",
    "KKR Health Care Strategic Growth II Securitize Fund": "#d39c34",
    "Hamilton Lane Secondary VI Securitize Fund":          "#3af4de",
    "Protos":                                              "#1c4951",
    "Hamilton Lane Equity Opportunities Securitize Fund V": "#0e0e0e",
    "USTY U.S. Treasury Tokens":                           "#4497e2",
}
# Funds not in the site legend (ArCoin, ParaFi, HL Senior Credit, 22X) fall to gray.
_tail = ["#8e8e8e"]
full_colors, _ti = [], 0
for name in order:
    if name in FULL_MAP:
        full_colors.append(FULL_MAP[name])
    else:
        full_colors.append(_tail[_ti % len(_tail)]); _ti += 1

out_dir = "outputs/charts/rwa/securitize"
Path(out_dir).mkdir(parents=True, exist_ok=True)
TARGET_W = 545


def render(colors, suffix):
    fig, ax = plt.subplots(figsize=(9.6, 4.6), dpi=DPI)
    ax.stackplot(df.index, *[df[c].values for c in order],
                 colors=colors, linewidth=0)
    ax.set_xlim(df.index.min(), df.index.max())
    ax.set_ylim(0, 4.7)
    ax.yaxis.set_major_locator(FixedLocator([0, 1, 2, 3, 4]))
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:.0f}B")
    ticks = pd.date_range("2024-01-01", df.index.max(), freq="QS")
    ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(ticks)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    apply_style(fig, ax, "stacked")
    ax.tick_params(axis="x", labelsize=15)
    ax.tick_params(axis="y", labelsize=15)
    fig.canvas.draw()
    dpi = TARGET_W / fig.get_tightbbox(fig.canvas.get_renderer()).width
    for ext in ("png", "svg"):
        fig.savefig(f"{out_dir}/securitize_platform_value_history{suffix}.{ext}",
                    dpi=dpi, facecolor="none", edgecolor="none",
                    bbox_inches="tight", transparent=True)
    plt.close(fig)


render(legend_colors, "")        # legend version (main filename)
render(full_colors, "_full")     # original per-product version (kept)
print("latest total $B:", round(df.iloc[-1].sum(), 3))
