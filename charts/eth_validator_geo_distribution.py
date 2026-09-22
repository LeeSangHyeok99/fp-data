"""
Ethereum Validator Geographic Distribution
그룹 바 차트: All validators vs Professional validators, 국가별 점유율(%)
X축 국가명은 대륙별 색으로 구분. 빈 바 = 해당 세트 top10 밖 (0% 아님).
Source: Rated (2026-07-08)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart, SERIES_COLORS  # noqa: E402

DATA = "sources/eth_validator_geo_distribution_en.csv"
OUTDIR = "outputs/charts/ethereum/validators"
FNAME = "eth_validator_geo_distribution"

# 대륙별 x축 라벨 색 (레퍼런스 재현)
CONTINENT_COLORS = {
    "North America": "#8b7cf6",  # 라이트 퍼플
    "Europe": "#ff8a6b",         # 코랄
    "Asia": "#ee7ac6",           # 핑크
    "Oceania": "#fac858",        # 골드
    "Other": "#9aa0ab",          # 그레이
}

ALL_COLOR = SERIES_COLORS[0]          # 블루  #5470c6  (All validators)
PRO_COLOR = SERIES_COLORS[1]          # 그린  #91cc75  (Professional validators)


def main():
    df = pd.read_csv(DATA)

    categories = df["country"].tolist()
    x = np.arange(len(categories))

    all_vals = df["all_validators_pct"].to_numpy(dtype=float)
    pro_vals = df["professional_validators_pct"].to_numpy(dtype=float)

    fig, ax = create_figure("bar")

    group_w = 0.8
    bar_w = group_w / 2

    ax.bar(x - bar_w / 2, all_vals, width=bar_w * 0.92,
           color=ALL_COLOR, zorder=3)
    ax.bar(x + bar_w / 2, pro_vals, width=bar_w * 0.92,
           color=PRO_COLOR, zorder=3)

    # 축
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlim(-0.6, len(categories) - 0.4)

    ax.set_ylim(0, 40)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_yticklabels(["0%", "10%", "20%", "30%", "40%"])

    apply_style(fig, ax, "bar")

    # 축 폰트 크기: 축별로 통일 + 살짝 축소 (config 기본 x=22/y=24)
    X_TICK_FS = 17
    Y_TICK_FS = 17
    ax.tick_params(axis="x", labelsize=X_TICK_FS)
    ax.tick_params(axis="y", labelsize=Y_TICK_FS)

    # 대륙별 x축 라벨 색 + 회전 조정 (apply_style 이후에 덮어씀)
    country_continent = dict(zip(df["country"], df["continent"]))
    for lbl in ax.get_xticklabels():
        cont = country_continent.get(lbl.get_text())
        if cont in CONTINENT_COLORS:
            lbl.set_color(CONTINENT_COLORS[cont])
        lbl.set_rotation(52)
        lbl.set_ha("right")
        lbl.set_fontsize(X_TICK_FS)

    # y축 라벨 크기 명시 통일
    for lbl in ax.get_yticklabels():
        lbl.set_fontsize(Y_TICK_FS)

    Path(OUTDIR).mkdir(parents=True, exist_ok=True)
    png, svg = save_chart(fig, FNAME, OUTDIR)
    print("saved:", png, svg)


if __name__ == "__main__":
    main()
