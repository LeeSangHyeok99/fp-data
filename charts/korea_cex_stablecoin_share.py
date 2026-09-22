"""
Stablecoin Market Share of Top 5 Korean Crypto Exchanges (Jan 2025 - Jun 2026)
Four Pillars 스타일 멀티라인 (레퍼런스 이미지 + 표 데이터 재현)
Source: South Korea Financial Supervisory Service, Data by Surf
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, create_figure, save_chart

df = pd.read_csv("outputs/data/korea_cex_stablecoin_share.csv")
df["date"] = pd.to_datetime(df["month"], format="%Y-%m")

# 레퍼런스 색 구성 그대로 (Upbit 네이비 / Bithumb 오렌지 / Coinone 그린 /
# Korbit 라이트블루 / Gopax 다크그레이)
SERIES = [
    ("coinone", "Coinone", "#3ecf8e", 8),
    ("bithumb", "Bithumb", "#ff8a1e", 8),
    ("upbit", "Upbit", "#1f47b3", -14),
    ("korbit", "Korbit", "#1e9bff", 9),
    ("gopax", "Gopax", "#787b86", -9),
]

fig, ax = create_figure("line")

last = df.iloc[-1]
for col, name, color, dy in SERIES:
    ax.plot(df["date"], df[col], color=color, linewidth=2.2, zorder=4)
    ax.scatter(last["date"], last[col], color=color, s=40, zorder=5,
               edgecolors="none", clip_on=False)
    ax.annotate(
        name,
        xy=(last["date"], last[col]),
        xytext=(14, dy), textcoords="offset points",
        ha="left", va="center", fontsize=15, fontweight="bold",
        color=color, zorder=6, annotation_clip=False,
    )

ax.set_ylim(0, 60)
ax.set_yticks([0, 20, 40, 60])
ax.set_yticklabels([f"{v}%" for v in [0, 20, 40, 60]])

ax.set_xlim(df["date"].min(), df["date"].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "line")
# 축별로 크기 통일: y틱 전부 20, x틱 전부 17
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=17)
for t in ax.get_yticklabels():
    t.set_fontsize(20)
for t in ax.get_xticklabels():
    t.set_fontsize(17)

png, svg = save_chart(fig, "korea_cex_stablecoin_share",
                      "outputs/charts/korea_cex/stablecoin")
print("saved:", png, svg)
