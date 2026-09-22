"""
Cap TVL Trajectory: Peak, Trough, and Recovery
Four Pillars 스타일 area/line 차트 (DefiLlama 실데이터 재현)
Source: https://defillama.com/protocol/cap  (api.llama.fi/protocol/cap)
"""

import sys
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, area_glow, create_figure, endpoint_dot, save_chart

# -----------------------------------------------------------------------------
# 데이터 로드
# -----------------------------------------------------------------------------
df = pd.read_csv("outputs/data/cap_tvl_trajectory.csv", parse_dates=["date"])
df["tvl_m"] = df["tvl_usd"] / 1e6

# Cap 브랜드 틸 컬러
LINE = "#1fc7a4"
DOT_HIGHLIGHT = "#e8895a"  # 피크/저점 (오렌지)
DOT_FIRST = "#c8a24a"      # 첫 기사 (골드)

# -----------------------------------------------------------------------------
# 차트
# -----------------------------------------------------------------------------
fig, ax = create_figure("area")

# 라인 근처 글로우 필
area_glow(ax, df["date"], df["tvl_m"], color=LINE, max_alpha=0.16)
ax.plot(df["date"], df["tvl_m"], color=LINE, linewidth=2.0, zorder=4)

# -----------------------------------------------------------------------------
# 주요 포인트 주석
# -----------------------------------------------------------------------------
def point(d):
    row = df.loc[df["date"] == pd.Timestamp(d)].iloc[0]
    return row["date"], row["tvl_m"]

TEXT = "#d1d4dc"

# (date, label, value_text, dot_color, text_xy_offset, ha)
annos = [
    (date(2025, 12, 13), "First article\n~$355M", DOT_FIRST, (-6, 34), "center"),
    (date(2026, 1, 28),  "Peak\n~$484M",          DOT_HIGHLIGHT, (-2, 30), "center"),
    (date(2026, 2, 3),   "Stabledrop Announced\n~$318M",   DOT_HIGHLIGHT, (24, -34), "center"),
    (date(2026, 3, 4),   "Trough\n~$154M",        DOT_HIGHLIGHT, (0, -42), "center"),
    (date(2026, 5, 9),   "Recovery high\n~$375M", LINE, (-8, 36), "center"),
]

for d, label, dot_c, (ox, oy), ha in annos:
    x, y = point(d)
    endpoint_dot(ax, x, y, color=dot_c, size=42)
    ax.annotate(
        label,
        xy=(x, y),
        xytext=(ox, oy),
        textcoords="offset points",
        ha=ha,
        va="center",
        fontsize=12,
        fontweight="bold",
        color=TEXT,
        zorder=6,
        arrowprops=dict(arrowstyle="-", color=dot_c, lw=1.2, alpha=0.8),
    )

# -----------------------------------------------------------------------------
# 축
# -----------------------------------------------------------------------------
ax.set_ylim(0, 510)
ax.set_yticks([0, 100, 200, 300, 400, 500])
ax.set_yticklabels([f"${int(v)}M" for v in [0, 100, 200, 300, 400, 500]])

ax.set_xlim(df["date"].min(), pd.Timestamp("2026-07-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "area")

# 틱 폰트 조정 (Y 24->22, X 22->20)
ax.tick_params(axis="y", labelsize=22)
ax.tick_params(axis="x", labelsize=20)

png, svg = save_chart(fig, "cap_tvl_trajectory", "outputs/charts/cap/tvl")
print("saved:", png, svg)
