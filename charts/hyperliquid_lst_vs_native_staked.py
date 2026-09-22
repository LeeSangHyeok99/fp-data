"""Hyperliquid LSTs vs. Native Staked ratio — four-pillars theme."""
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

sys.path.append(str(Path(__file__).resolve().parent.parent / ".claude/skills/design/four-pillars"))
from config import create_figure, apply_style, save_chart, area_glow, endpoint_dot  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent / "outputs/data/hyperliquid_lst_vs_native_staked.csv"
OUT_DIR = Path(__file__).resolve().parent.parent / "outputs/charts/hyperliquid/staking"

COLOR = "#3ba272"


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

    fig, ax = create_figure("area")

    x = df["date"]
    y = df["lst_to_staked_ratio_pct"]

    ax.fill_between(x, 0, y, color=COLOR, alpha=0.55, linewidth=0, zorder=3)
    ax.plot(x, y, color=COLOR, linewidth=2.2, zorder=4)
    area_glow(ax, x, y, color=COLOR, n_layers=40, max_alpha=0.12, power=2.8)
    endpoint_dot(ax, x.iloc[-1], y.iloc[-1], color=COLOR, size=60)

    ax.set_ylim(0, 12)
    ax.set_yticks([0, 3, 6, 9, 12])
    ax.yaxis.set_major_formatter(lambda v, _: f"{int(v)}%")

    ax.set_xlim(x.iloc[0], x.iloc[-1])
    tick_dates = [pd.Timestamp(s) for s in ["2025-02-01", "2025-05-01", "2025-07-01", "2025-10-01", "2026-01-01"]]
    ax.set_xticks(tick_dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    apply_style(fig, ax, "area")
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")

    png, svg = save_chart(fig, "hyperliquid_lst_vs_native_staked", str(OUT_DIR))
    plt.close(fig)
    print("saved", png)
    print("saved", svg)


if __name__ == "__main__":
    main()
