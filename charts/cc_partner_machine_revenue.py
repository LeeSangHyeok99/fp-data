"""
Collector Crypt: Monthly Partner Machine Revenue by Slug (stacked bar)
파트너(슬러그)별 월 리비뉴 구성. Revenue = machine P&L + kept cards 보험가치.
실소스: sources/cc_partner_revenue.csv (long-format, slug별 집계).
named 시리즈(me/sol/slabz/roll/arena) 외 slug은 others16로 합산.
스택 순서(아래→위): Magic Eden, Solflare, Slabz, "roll", "arena", 16 others.
Source: Collector Crypt public stats API (2026-07-08)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart  # noqa: E402

DATA = "outputs/data/cc_partner_machine_revenue.csv"
OUTDIR = "outputs/charts/collector-crypt/revenue"
FNAME = "cc_partner_machine_revenue"

# 시리즈: (컬럼, 색) 아래→위 스택 순서
SERIES = [
    ("magic_eden", "#7b7ef0"),  # 페리윙클 퍼플
    ("solflare",   "#6ee0b0"),  # 틸 그린
    ("slabz",      "#c9a8e8"),  # 라일락
    ("roll",       "#e3c07f"),  # 탄/골드
    ("arena",      "#6bb6e0"),  # 블루
    ("others16",   "#6f6f78"),  # 그레이
]


def main():
    df = pd.read_csv(DATA, parse_dates=["month"])
    # Sep 2025 (빈 달) 제외
    df = df[df["month"] != "2025-09"].reset_index(drop=True)
    x = np.arange(len(df))

    fig, ax = create_figure("stacked_bar")

    bottom = np.zeros(len(df))
    for col, color in SERIES:
        vals = df[col].to_numpy(dtype=float)
        ax.bar(x, vals, width=0.62, bottom=bottom, color=color, zorder=3)
        bottom += vals

    # X축
    labels = [d.strftime("%b %Y") for d in df["month"]]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.7, len(df) - 0.3)

    # Y축 — 0~1,200K, 5틱, $300K 간격
    ax.set_ylim(0, 1200)
    ax.set_yticks([0, 300, 600, 900, 1200])
    ax.set_yticklabels([f"${v:,}K" for v in [0, 300, 600, 900, 1200]])

    apply_style(fig, ax, "bar")

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
