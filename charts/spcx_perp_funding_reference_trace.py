"""레퍼런스 차트를 그대로 재현한 버전 (실데이터 아님).

원본은 FP 의 "recreation for review, final figure pending raw series" 목업이다.
여기서는 그 목업의 곡선을 이미지에서 좌표로 읽어 four-pillars 스타일로만
다시 그린다. 실측 계열은 charts/spcx_perp_funding.py 쪽이다.

레퍼런스와 실측이 갈리는 지점(재현 대상이므로 여기서는 레퍼런스를 따른다):
  · 평탄 구간을 평균선(+10.9%)에 얹었다. 실측은 +5.475%.
  · 변곡이 6/15~16. 실측은 SpaceX 나스닥 상장일인 6/12.
  · 주말/휴장 0% 구간이 없다. 실측은 165 회 중 48 회.
  · 진폭 -35~+55%. 실측 8시간 원계열은 -117~+104%.

출력에 _reference 접미사를 붙여 실측본과 섞이지 않게 한다.
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, apply_style, create_figure, save_chart

FUNDING = "#4285f4"
DIM = COLORS["text_secondary"]
OUT = "outputs/charts/perps/funding"

AVG = 10.9        # 레퍼런스가 표기한 구간 평균
FLAT = 10.9       # 레퍼런스가 평탄 구간을 그린 높이 (평균선과 같음)

# 6/16 이후 일별 값. 이미지에서 픽셀 좌표로 읽은 근사치다.
TAIL = [4, -20, -35, 0, 36, 20, -28, -13, 38, 55, 52, 30, 9, -5, 36,
        25, 18, 11, 2, 10, 6, 3, 18, 9, 2, 11, 20, 10, 16, 16]

dates = pd.date_range("2026-05-22", "2026-07-15", freq="D")
flat_n = len(dates) - len(TAIL)
values = [FLAT] * (flat_n - 1) + [11.2] + TAIL   # 하락 직전 작은 위꺾임
df = pd.DataFrame({"date": dates, "annualized_pct": values})

Path("outputs/data").mkdir(parents=True, exist_ok=True)
df.to_csv("outputs/data/spcx_funding_reference_trace.csv", index=False)

fig, ax = create_figure("line")

ax.axhline(0, color=DIM, alpha=0.55, linewidth=1.2, zorder=2)
ax.plot(df["date"], df["annualized_pct"], color=FUNDING, linewidth=2.4,
        zorder=4, solid_capstyle="round", solid_joinstyle="round")
ax.axhline(AVG, color=DIM, linewidth=1.8, linestyle=(0, (5, 3)), zorder=3)
ax.annotate(f"Period Avg +{AVG:.1f}%", xy=(df["date"].iloc[3], AVG),
            xytext=(0, 16), textcoords="offset points", ha="left", va="bottom",
            fontsize=15, fontweight="bold", color=DIM, zorder=5)

ax.set_xlim(df["date"].min(), df["date"].max())
ax.set_ylim(-46, 64)
ax.set_yticks([-40, -20, 0, 20, 40, 60])
ax.set_yticklabels(["-40%", "-20%", "0%", "+20%", "+40%", "+60%"])
ax.xaxis.set_major_locator(mdates.DayLocator(interval=9))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

apply_style(fig, ax, "line")
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=20)

print(f"추적본 구간 평균 = {df['annualized_pct'].mean():.2f}%  (레퍼런스 표기 +10.9%)")
print("saved:", *save_chart(fig, "spcx_perp_funding_reference", OUT))
plt.close(fig)
