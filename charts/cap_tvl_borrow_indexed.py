"""
Cap: Borrowed Capital vs TVL, indexed to 100 at first article (Dec 11, 2025)
Four Pillars 스타일 멀티라인 (DefiLlama 실데이터 재현)
Source: https://defillama.com/protocol/cap, https://defillama.com/protocol/active-loans/cap
        (api.llama.fi/protocol/cap, chainTvls.borrowed)
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, create_figure, endpoint_dot, save_chart

# -----------------------------------------------------------------------------
# 데이터 로드
# -----------------------------------------------------------------------------
df = pd.read_csv("outputs/data/cap_tvl_borrow_indexed.csv", parse_dates=["date"])

BORROW = "#c8693a"  # 오렌지 (차입)
TVL = "#1fc7a4"     # 틸 (TVL)
TEXT = "#d1d4dc"
SECONDARY = "#787b86"

# -----------------------------------------------------------------------------
# 차트
# -----------------------------------------------------------------------------
fig, ax = create_figure("line")

# 베이스라인 100 기준선
ax.axhline(100, color=SECONDARY, linewidth=1.0, linestyle=(0, (4, 3)), alpha=0.7, zorder=1)

ax.plot(df["date"], df["borrow_index"], color=BORROW, linewidth=2.2, zorder=4)
ax.plot(df["date"], df["tvl_index"], color=TVL, linewidth=2.2, zorder=4)

# 끝점 도트 + 라벨
last = df.iloc[-1]
endpoint_dot(ax, last["date"], last["borrow_index"], color=BORROW, size=46)
endpoint_dot(ax, last["date"], last["tvl_index"], color=TVL, size=46)

ax.annotate(
    f"Borrowed\n~{int(round(last['borrow_index']))}",
    xy=(last["date"], last["borrow_index"]),
    xytext=(14, 6), textcoords="offset points",
    ha="left", va="center", fontsize=13, fontweight="bold", color=BORROW, zorder=6,
)
ax.annotate(
    f"TVL\n~{int(round(last['tvl_index']))}",
    xy=(last["date"], last["tvl_index"]),
    xytext=(14, -2), textcoords="offset points",
    ha="left", va="center", fontsize=13, fontweight="bold", color=TVL, zorder=6,
)

# 베이스라인 라벨
ax.annotate(
    "Baseline 100\n(Dec 11, 2025)",
    xy=(df["date"].iloc[0], 100),
    xytext=(6, -26), textcoords="offset points",
    ha="left", va="center", fontsize=11, fontweight="bold", color=SECONDARY, zorder=6,
)

# -----------------------------------------------------------------------------
# 축
# -----------------------------------------------------------------------------
ax.set_ylim(0, 420)
ax.set_yticks([0, 100, 200, 300, 400])
ax.set_yticklabels([str(v) for v in [0, 100, 200, 300, 400]])

ax.set_xlim(df["date"].min(), pd.Timestamp("2026-07-15"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "line")

ax.tick_params(axis="y", labelsize=22)
ax.tick_params(axis="x", labelsize=20)

png, svg = save_chart(fig, "cap_tvl_borrow_indexed", "outputs/charts/cap/tvl")
print("saved:", png, svg)
