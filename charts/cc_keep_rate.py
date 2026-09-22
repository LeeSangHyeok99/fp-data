"""
Collector Crypt: Monthly Keep Rate (cards kept by users, % of spin value)
단일 시리즈 바. Keep % = 되팔지 않은 카드의 스핀 비용 / 총 확정 스핀 비용.
실소스: sources/cc_keep_share.csv (kept_pct_of_spin_value). 2.5% 10개월 고점 기준선 표시.
Source: Collector Crypt public stats API (2026-07-08)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart  # noqa: E402

DATA = "outputs/data/cc_keep_rate.csv"
OUTDIR = "outputs/charts/collector-crypt/metrics"
FNAME = "cc_keep_rate"

BAR_COLOR = "#7f83ec"   # 페리윙클 퍼플


def main():
    df = pd.read_csv(DATA, parse_dates=["month"])
    x = np.arange(len(df))
    vals = df["keep_pct"].to_numpy()

    fig, ax = create_figure("bar")

    ax.bar(x, vals, width=0.6, color=BAR_COLOR, zorder=3)

    # 10개월 고점 기준선 (2.5%) + 라벨
    ax.axhline(2.5, color="#787b86", linewidth=1.2,
               linestyle=(0, (4, 3)), alpha=0.8, zorder=2)
    ax.text(0.9, 2.58, "10-Month High, 2.5%", fontsize=15,
            fontstyle="italic", fontweight="normal",
            color="#9aa0ab", va="bottom", ha="left", zorder=4)

    # X축
    labels = [d.strftime("%b %Y") for d in df["month"]]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.7, len(df) - 0.3)

    # Y축 — 0~3%, 4틱, 1% 간격
    ax.set_ylim(0, 3.0)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels([f"{v}%" for v in [0, 1, 2, 3]])

    apply_style(fig, ax, "bar")

    # 축 폰트 통일 + 살짝 축소, x 라벨 회전(겹침 방지)
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
