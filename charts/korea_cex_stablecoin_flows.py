"""
Monthly stablecoin inflow / outflow at Korean crypto exchanges (Jan 2025 - Jun 2026)
Four Pillars 스타일 그룹 바 + 듀얼축 라인 (레퍼런스 이미지 + 표 데이터 재현)
Source: South Korea Financial Supervisory Service, Data by Surf
단위: 원 데이터 억원(100M KRW) -> 조원(T KRW)으로 환산
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, DPI, GRID_CONFIG, save_chart, setup_font

setup_font()

df = pd.read_csv("outputs/data/korea_cex_stablecoin_flows.csv")
df["date"] = pd.to_datetime(df["month"], format="%Y-%m")
for c in ["inflow", "outflow", "net_outflow"]:
    df[c] = df[c] / 10000.0  # 억원 -> 조원

INFLOW = "#26a69a"
OUTFLOW = "#ef5350"
NET = "#73c0de"

fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax2 = ax.twinx()
ax2.set_facecolor("none")

x = np.arange(len(df))
w, gap = 0.29, 0.05  # 바 너비 / 그룹 안 간격 (그룹 사이는 0.37 비움)
ax.bar(x - (w + gap) / 2, df["inflow"], width=w, color=INFLOW, zorder=2)
ax.bar(x + (w + gap) / 2, df["outflow"], width=w, color=OUTFLOW, zorder=2)

ax2.plot(x, df["net_outflow"], color=NET, linewidth=2.4, zorder=5)
ax2.scatter(x, df["net_outflow"], s=28, color=NET, zorder=6, edgecolors="none")

# 듀얼축: 좌/우 틱 4개씩, 같은 그리드 라인에 정렬 (12/12.4 = 1.5/1.55)
ax.set_yticks([0, 4, 8, 12])
ax.set_yticklabels([f"₩{t}T" for t in [0, 4, 8, 12]], fontsize=18,
                   fontweight="bold", color=COLORS["text_secondary"])
ax.set_ylim(0, 12.4)

ax2.set_yticks([0, 0.5, 1.0, 1.5])
ax2.set_yticklabels(["₩0T", "₩0.5T", "₩1.0T", "₩1.5T"], fontsize=18,
                    fontweight="bold", color=NET)
ax2.set_ylim(0, 1.55)

# x축: 매달 라벨(수평, 그룹 정중앙)을 찍어 바와 1:1 매칭
# 짝수 월(Feb/Apr/Jun/Aug/Oct/Dec)만 틱 + 라벨
even = [xi for xi, d in zip(x, df["date"]) if d.month % 2 == 0]
ax.set_xticks(even)
ax.set_xticklabels([d.strftime("%b %Y") for d in df["date"] if d.month % 2 == 0],
                   fontsize=15, fontweight="bold", rotation=45, ha="right",
                   color=COLORS["text_secondary"])
ax.set_xlim(-0.7, len(df) - 0.3)

ax.grid(True, axis="y", color=GRID_CONFIG["color"], alpha=GRID_CONFIG["alpha"],
        linestyle=GRID_CONFIG["linestyle"], linewidth=GRID_CONFIG["linewidth"])
ax.set_axisbelow(True)
for spine in list(ax.spines.values()) + list(ax2.spines.values()):
    spine.set_visible(False)
ax.tick_params(axis="y", length=0)
ax2.tick_params(axis="both", length=0)
# x 틱마크 (share 차트와 동일)
ax.tick_params(axis="x", length=6, width=1, color=COLORS["text_secondary"])

# 시리즈명 직접 표기 (범례 없음)
fig.tight_layout()
png, svg = save_chart(fig, "korea_cex_stablecoin_flows",
                      "outputs/charts/korea_cex/stablecoin")
plt.close(fig)
print("saved:", png, svg)
