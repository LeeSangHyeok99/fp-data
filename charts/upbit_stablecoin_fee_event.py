"""
Upbit stablecoin volume around the zero-fee event (Jun 17 - Aug 4, 2026)
1:1 비율 차트 2장 (한 인포그래픽에 나란히 들어감)
  1) upbit_stablecoin_avg_volume_compare : 토큰별 일평균 거래량, 이벤트 전 30일 vs 이벤트 기간
  2) upbit_stablecoin_daily_volume       : 전체 일별 거래량 추이 + 이벤트 구간
Source: Upbit, Data by Surf
단위: 원 데이터 억원 -> ₩B(십억원)
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, DPI, GRID_CONFIG, save_chart, setup_font

setup_font()

DF = pd.read_csv("outputs/data/upbit_stablecoin_daily_volume.csv", parse_dates=["date"])
EVENT_START = pd.Timestamp("2026-07-26")  # 데이터의 '구분' 컬럼 기준 이벤트 기간 시작

BEFORE = "#787b86"   # 이벤트 전
DURING = "#1e9bff"   # 이벤트 기간
MARK = "#ef5350"
OUT = "outputs/charts/upbit/stablecoin"
FIGSIZE = (7.2, 7.2)  # 1:1
FS_X, FS_Y, FS_VAL, FS_LEG = 16, 18, 15, 13


def base_axes(figsize=None):
    fig, ax = plt.subplots(figsize=figsize or FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.grid(True, axis="y", color=GRID_CONFIG["color"], alpha=GRID_CONFIG["alpha"],
            linestyle=GRID_CONFIG["linestyle"], linewidth=GRID_CONFIG["linewidth"])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=6, width=1, color=COLORS["text_secondary"])
    return fig, ax


# =============================================================================
# 1) 토큰별 일평균 거래량 비교
# =============================================================================
pre = DF[(DF.date >= "2026-06-26") & (DF.date < EVENT_START)]
during = DF[DF.date >= EVENT_START]
others = ["usd1", "usds", "usde", "xaut"]

cats = ["USDT", "USDC", "RLUSD", "USDG", "Others", "Total"]
pre_v = [pre.usdt.mean(), pre.usdc.mean(), pre.rlusd.mean(), pre.usdg.mean(),
         pre[others].sum(axis=1).mean(), pre.total.mean()]
dur_v = [during.usdt.mean(), during.usdc.mean(), during.rlusd.mean(),
         during.usdg.mean(), during[others].sum(axis=1).mean(), during.total.mean()]
pre_v = np.array(pre_v) / 10.0   # 억원 -> ₩B
dur_v = np.array(dur_v) / 10.0

fig, ax = base_axes((7.2, 5.95))  # 위 여백만큼 높이 축소 (바 크기 유지)
x = np.arange(len(cats))
w, gap = 0.36, 0.06
ax.bar(x - (w + gap) / 2, pre_v, width=w, color=BEFORE, zorder=2)
ax.bar(x + (w + gap) / 2, dur_v, width=w, color=DURING, zorder=2)

for xi, (a, b) in enumerate(zip(pre_v, dur_v)):
    # 단위는 y축에 있으므로 값 라벨은 숫자만 (작은 바끼리 라벨이 겹치지 않게)
    for xo, v, c in ((-(w + gap) / 2, a, BEFORE), ((w + gap) / 2, b, DURING)):
        txt = f"{v:,.1f}".removesuffix(".0")   # 0.0 -> 0, 47.0 -> 47
        ax.text(xi + xo, v + 2.0, txt, ha="center", va="bottom",
                fontsize=FS_VAL, fontweight="bold", color=c)

ax.set_yticks([0, 40, 80, 120])
ax.set_yticklabels([f"₩{t}B" for t in [0, 40, 80, 120]], fontsize=FS_Y,
                   fontweight="bold", color=COLORS["text_secondary"])
ax.set_ylim(0, 132)
ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=FS_X, fontweight="bold",
                   color=COLORS["text_secondary"])
ax.set_xlim(-0.65, len(cats) - 0.35)

fig.tight_layout()
save_chart(fig, "upbit_stablecoin_avg_volume_compare", OUT)
plt.close(fig)

# =============================================================================
# 2) 전체 일별 거래량 추이
# =============================================================================
fig, ax = base_axes((FIGSIZE[0] * 7 / 6, FIGSIZE[1]))  # 가로만 +1/6, 세로/폰트 그대로
total = DF.total / 10.0

ax.axvspan(EVENT_START - pd.Timedelta(hours=12), DF.date.max(), color=DURING,
           alpha=0.13, zorder=1, linewidth=0)
ax.axvline(EVENT_START - pd.Timedelta(hours=12), color=MARK, linewidth=1.8,
           linestyle=(0, (5, 3)), zorder=3)
ax.plot(DF.date, total, color=COLORS["text"], linewidth=2.0, zorder=4)
ax.scatter(DF.date, total, s=18, color=COLORS["text"], zorder=5, edgecolors="none")

ax.set_yticks([0, 50, 100, 150, 200])
ax.set_yticklabels([f"₩{t}B" for t in [0, 50, 100, 150, 200]], fontsize=FS_Y,
                   fontweight="bold", color=COLORS["text_secondary"])
ax.set_ylim(0, 215)

ax.set_xlim(DF.date.min(), DF.date.max())
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.WE))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.setp(ax.get_xticklabels(), fontsize=FS_X, fontweight="bold", rotation=45,
         ha="right", color=COLORS["text_secondary"])

# 이벤트 개시선 옆 직접 주석 (범례 없음)
ax.annotate("zero-fee event\nstarts Jul 26",
            xy=(EVENT_START - pd.Timedelta(days=1), 190), ha="right", va="top",
            fontsize=FS_LEG, fontweight="bold", color=MARK, linespacing=1.35,
            zorder=6)

fig.tight_layout()
save_chart(fig, "upbit_stablecoin_daily_volume", OUT)
plt.close(fig)

print(f"pre  n={len(pre)}  total avg ₩{pre_v[-1]:.1f}B")
print(f"during n={len(during)}  total avg ₩{dur_v[-1]:.1f}B  ({dur_v[-1]/pre_v[-1]:.2f}x)")
print("saved:", OUT)
