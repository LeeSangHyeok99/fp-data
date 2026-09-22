"""Onchain barbell — YoY change in key metrics, grouped dot plot.
3 buckets (Speculative, Onchain Native, TradFi-linked), 28 metrics.

Y축은 성장 배수의 로그(log10(1 + pct/100)). 원본 이미지의 축은 -43%가 0.1%
근처에 찍히는 등 깨져 있어서, 배수 로그로 다시 잡았다. 이러면 x2와 /2가
같은 거리로 대칭이 되고, -6%~-79% 구간도 눌리지 않는다.
"""
import sys

import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import COLORS, apply_style, save_chart, setup_font  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

df = pd.read_csv("outputs/data/onchain_barbell_yoy.csv")

GROUPS = ["Speculative", "Onchain Native", "TradFi-linked"]
GROUP_COLOR = {
    "Speculative": "#26a69a",
    "Onchain Native": "#ef5350",
    "TradFi-linked": "#5470c6",
}
BAND = 10.0
PAD = 0.6  # 밴드 좌우 안쪽 여백 (라벨이 구분선을 넘지 않게)

# 성장 배수의 로그. -100%면 0배라 정의역 밖이므로 데이터에 없다고 전제.
y = np.log10(1 + df["pct"] / 100)
x = df["group"].map(lambda g: GROUPS.index(g) * BAND) + PAD + df["x"] * (BAND - 2 * PAD)

setup_font()
fig, ax = plt.subplots(figsize=(22, 10), dpi=150)

ax.set_xlim(0, BAND * len(GROUPS))
ax.set_ylim(np.log10(0.13), np.log10(75))

# 5배 간격 틱 (로그 축에서 등간격). 라벨은 레퍼런스대로 % (YoY).
ticks = [0.2, 1, 5, 25]
ax.yaxis.set_major_locator(FixedLocator([np.log10(t) for t in ticks]))
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f"{(10 ** v - 1) * 100:+,.0f}%")
)
ax.set_xticks([i * BAND + BAND / 2 for i in range(len(GROUPS))])
ax.set_xticklabels(GROUPS)

apply_style(fig, ax)
ax.tick_params(axis="x", rotation=0, length=0, labelsize=22, pad=18)
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")  # apply_style이 right로 두는 걸 되돌림
ax.tick_params(axis="y", labelsize=20)

# 1x(=YoY 0%) 기준선을 한 톤 밝게
ax.axhline(0, color=COLORS["text_secondary"], alpha=0.9, lw=1.2, zorder=1)

# 밴드 구분선
for i in range(1, len(GROUPS)):
    ax.axvline(i * BAND, color=COLORS["grid"], alpha=0.45, lw=1.2,
               linestyle=(0, (4, 3)), zorder=1)

# 라벨 위치별 오프셋(포인트): (이름 dx, dy), (수치 dx, dy), ha
OFFSETS = {
    "right": ((13, 9), (13, -11), "left"),
    "above": ((0, 31), (0, 13), "center"),
    "below": ((0, -17), (0, -36), "center"),
}

for (_, row), yy, xx in zip(df.iterrows(), y, x):
    color = GROUP_COLOR[row["group"]]
    ax.scatter(xx, yy, s=150, color=color, zorder=5, linewidths=0)

    (ndx, ndy), (vdx, vdy), ha = OFFSETS[row["pos"]]
    ax.annotate(row["label"], (xx, yy), textcoords="offset points",
                xytext=(ndx, ndy), ha=ha, va="center",
                fontsize=16, fontweight="bold", color=COLORS["text"], zorder=6)
    ax.annotate(f"({row['pct']:+d}%)", (xx, yy), textcoords="offset points",
                xytext=(vdx, vdy), ha=ha, va="center",
                fontsize=15, fontweight="bold", color=color, zorder=6)

fig.tight_layout()
png, svg = save_chart(fig, "onchain_barbell_yoy", "outputs/charts/market/structure")
print(png)
print(svg)
