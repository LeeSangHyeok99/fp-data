"""Top 12 individual prediction markets by 30d notional volume.

Reveals what people actually trade: sports + macro dominate, while
US Presidential Election (the canonical Polymarket headline) ranks #14.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent / ".claude/skills/design/four-pillars"))
from config import setup_font, save_chart, COLORS, GRID_CONFIG  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent / "outputs/data/prediction_market_themes.csv"
OUT_DIR = Path(__file__).resolve().parent.parent / "outputs/charts/prediction_markets/themes"

KALSHI_C = "#5470c6"
POLY_C = "#91cc75"

TOP_N = 12

# Theme tag color (text after market name)
THEME_TAG_COLOR = {
    "Sports Betting": "#91cc75",
    "Macro & Rates": "#73c0de",
    "Crypto": "#f7931a",
    "US Elections": "#5470c6",
    "Pop Culture": "#ea7ccc",
    "Geopolitics": "#ef5350",
    "Science & Tech": "#9a60b4",
}


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df["vol_m"] = df["volume_usd"] / 1e6
    df = df.sort_values("vol_m", ascending=False).head(TOP_N).copy()
    df = df.iloc[::-1].reset_index(drop=True)  # ascending for barh (largest on top)

    setup_font()
    fig, ax = plt.subplots(figsize=(11.5, 6.0), dpi=150)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    y = np.arange(len(df))
    colors = [KALSHI_C if s == "Kalshi" else POLY_C for s in df["source"]]

    bars = ax.barh(y, df["vol_m"], height=0.62, color=colors, edgecolor="none", alpha=0.95)

    # Value + theme tag labels
    for i, row in df.iterrows():
        val = row["vol_m"]
        # Value label at end
        ax.text(val + 0.7, i, f"${val:.1f}M",
                va="center", ha="left",
                fontsize=12, fontweight="bold",
                color=COLORS["text_secondary"])

    # Y-tick labels: market name with platform suffix to disambiguate duplicates
    ylabels = []
    for _, row in df.iterrows():
        plat_short = "K" if row["source"] == "Kalshi" else "P"
        ylabels.append(f"{row['subsubcategory']} ({plat_short})")
    ax.set_yticks(y)
    ax.set_yticklabels(ylabels, fontsize=12, fontweight="bold",
                       color=COLORS["text_secondary"])
    ax.tick_params(axis="y", length=0, pad=14)

    # X-axis
    x_max = float(df["vol_m"].max())
    x_lim = 45
    ax.set_xlim(0, x_lim)
    x_ticks = [0, 10, 20, 30, 40]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"${v}M" for v in x_ticks],
                       fontsize=12, fontweight="bold", color=COLORS["text_secondary"])
    ax.tick_params(axis="x", length=0, pad=8)

    # Grid
    ax.grid(True, axis="x",
            color=GRID_CONFIG["color"], alpha=GRID_CONFIG["alpha"],
            linestyle=GRID_CONFIG["linestyle"], linewidth=GRID_CONFIG["linewidth"])
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    png, svg = save_chart(fig, "prediction_market_top_markets", str(OUT_DIR))
    plt.close(fig)
    print(f"saved: {png}")
    print(f"saved: {svg}")

    # Verify ranking output
    print("\nTop 12 by 30d Volume:")
    df_print = df.iloc[::-1]
    for i, r in df_print.iterrows():
        print(f"  {r['subsubcategory']:30} | {r['source']:10} | {r['theme']:15} | ${r['vol_m']:.1f}M")


if __name__ == "__main__":
    main()
