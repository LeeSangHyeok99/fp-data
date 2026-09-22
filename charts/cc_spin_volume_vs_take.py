"""
Collector Crypt: Monthly Spin Volume vs Cost-Matched Machine Take
듀얼 축: 바(월별 스핀 볼륨, 좌축 $M) + 라인(machine take, 우축 %)
Source: Collector Crypt public stats API (2026-07-08)
실소스: sources/cc_gmv_vs_margin.csv (gmv_usd_m, cost_matched_take_at85_pct).
볼륨 26/06 $212.31M, take는 cost-matched take(85% costed) 실데이터.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart, GRID_CONFIG  # noqa: E402

DATA = "outputs/data/cc_spin_volume_take.csv"
OUTDIR = "outputs/charts/collector-crypt/volume"
FNAME = "cc_spin_volume_vs_take"

BAR_COLOR = "#77e0b0"   # 민트 그린 (스핀 볼륨)
LINE_COLOR = "#b49bf0"  # 라벤더 (machine take)


def main():
    df = pd.read_csv(DATA, parse_dates=["month"])
    x = np.arange(len(df))
    vol = df["spin_volume_musd"].to_numpy()
    take = df["machine_take_pct"].to_numpy()

    fig, ax = create_figure("bar")

    # 좌축: 볼륨 바
    ax.bar(x, vol, width=0.62, color=BAR_COLOR, zorder=3)

    # 우축: take 라인
    ax2 = ax.twinx()
    ax2.plot(x, take, color=LINE_COLOR, linewidth=2.6, zorder=4,
             marker="o", markersize=6, markerfacecolor=LINE_COLOR,
             markeredgecolor="none", solid_capstyle="round")

    # X축
    labels = [d.strftime("%b %Y") for d in df["month"]]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.7, len(df) - 0.3)

    # 좌축 (볼륨) — 틱 0/50/100/150/200, ylim 225 (26/06 $212M 수용)
    ax.set_ylim(0, 225)
    ax.set_yticks([0, 50, 100, 150, 200])
    ax.set_yticklabels([f"${v}M" for v in [0, 50, 100, 150, 200]])

    # 우축 (take) — 틱 0/2/4/6/8, ylim 9.0 (좌축과 동일 비율 200↔8%, 그리드 정확 정렬)
    ax2.set_ylim(0, 9.0)
    ax2.set_yticks([0, 2, 4, 6, 8])
    ax2.set_yticklabels([f"{v}%" for v in [0, 2, 4, 6, 8]])

    apply_style(fig, ax, "bar")

    # 축 폰트 크기: x끼리, y끼리(좌/우) 통일 + 축소
    X_FS = 15
    Y_FS = 17

    # 좌축 틱: 바 색(민트), 크기 통일
    ax.tick_params(axis="x", labelsize=X_FS)
    ax.tick_params(axis="y", labelsize=Y_FS, colors=BAR_COLOR)
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(X_FS)
    for lbl in ax.get_yticklabels():
        lbl.set_fontsize(Y_FS)
        lbl.set_color(BAR_COLOR)

    # 우축 스타일 (spine 숨김, 틱은 라인 색(라벤더), 좌축과 동일 크기, 그리드 없음)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.tick_params(axis="y", labelsize=Y_FS, length=0, pad=15,
                    colors=LINE_COLOR)
    for lbl in ax2.get_yticklabels():
        lbl.set_fontweight("bold")
        lbl.set_fontsize(Y_FS)
        lbl.set_color(LINE_COLOR)
    ax2.set_axisbelow(True)

    Path(OUTDIR).mkdir(parents=True, exist_ok=True)
    png, svg = save_chart(fig, FNAME, OUTDIR)
    print("saved:", png, svg)


if __name__ == "__main__":
    main()
