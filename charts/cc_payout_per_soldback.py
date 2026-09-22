"""
Collector Crypt: Payout per Sold-Back Dollar (%) monthly line
Payout = buybacks paid / spin cost of sold-back spins (CC machines).
실소스: sources/cc_payout_repricing.csv (payout_per_soldback_dollar_pct).
$1,000 머신 런치 수직선(Jan 2026),
포인트 값 라벨(90.6% / 94.8% / 94.0%).
Source: Collector Crypt public stats API (2026-07-08)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart  # noqa: E402

DATA = "outputs/data/cc_payout_per_soldback.csv"
OUTDIR = "outputs/charts/collector-crypt/metrics"
FNAME = "cc_payout_per_soldback"

LINE_COLOR = "#5ec9ac"   # 민트/틸


def main():
    df = pd.read_csv(DATA, parse_dates=["month"])
    x = np.arange(len(df))
    y = df["payout_pct"].to_numpy()

    fig, ax = create_figure("line")

    # $1,000 머신 런치 수직 점선 (Jan 2026 = x 4)
    ax.axvline(4, color="#9aa0ab", linewidth=1.1, linestyle=(0, (5, 4)),
               alpha=0.8, zorder=2)
    ax.text(4.15, 90.35, "$1,000 Machine Launches", fontsize=14,
            fontstyle="italic", color="#9aa0ab", ha="left", va="center",
            zorder=5)

    # 라인 + 포인트
    ax.plot(x, y, color=LINE_COLOR, linewidth=2.8, zorder=4,
            marker="o", markersize=7, markerfacecolor=LINE_COLOR,
            markeredgecolor="none", solid_capstyle="round")

    # 포인트 값 라벨 (시작/피크/끝)
    ax.annotate("90.6%", (0, y[0]), textcoords="offset points",
                xytext=(-2, 20), ha="center", fontsize=17, fontweight="bold",
                color=LINE_COLOR, zorder=6)
    ax.annotate("94.8%", (3, y[3]), textcoords="offset points",
                xytext=(0, 13), ha="center", fontsize=17, fontweight="bold",
                color=LINE_COLOR, zorder=6)
    ax.annotate("94.0%", (9, y[9]), textcoords="offset points",
                xytext=(0, 13), ha="center", fontsize=17, fontweight="bold",
                color=LINE_COLOR, zorder=6)

    # X축
    labels = [d.strftime("%b %Y") for d in df["month"]]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.5, len(df) - 0.5)

    # Y축 — 89~96%, 4틱 2% 간격 (깔끔한 짝수 %)
    ax.set_ylim(89, 96)
    ax.set_yticks([90, 92, 94, 96])
    ax.set_yticklabels([f"{v}%" for v in [90, 92, 94, 96]])

    apply_style(fig, ax, "line")

    # 축 폰트 통일 + 살짝 축소, x 라벨 회전
    FS = 19
    ax.tick_params(axis="x", labelsize=FS)
    ax.tick_params(axis="y", labelsize=FS)
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(40)
        lbl.set_ha("right")
        lbl.set_fontsize(FS)
    for lbl in ax.get_yticklabels():
        lbl.set_fontsize(FS)

    Path(OUTDIR).mkdir(parents=True, exist_ok=True)
    png, svg = save_chart(fig, FNAME, OUTDIR)
    print("saved:", png, svg)


if __name__ == "__main__":
    main()
