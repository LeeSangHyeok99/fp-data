"""SpaceX 프리IPO 퍼프(SPCXUSDT) 연환산 8시간 펀딩, 2026-05-22 ~ 07-15.
Four Pillars 스타일 (와이드)

레퍼런스는 "FP recreation, final figure pending raw series" 였다. 여기서는
Binance 실API 원계열 165건을 그대로 쓴다. 구간 평균 +10.94%로 레퍼런스의
+10.9%가 그대로 재현된다. 숏이 펀딩을 받는 구간이 양수 쪽이다.

데이터: scripts/fetch_spcx_funding.py → outputs/data/spcx_funding_8h.csv
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, apply_style, create_figure, save_chart

FUNDING = "#4285f4"   # 블루
DIM = COLORS["text_secondary"]
OUT = "outputs/charts/perps/funding"

df = pd.read_csv("outputs/data/spcx_funding_8h.csv", parse_dates=["time"])
avg = df["annualized_pct"].mean()   # 평균은 원계열 기준, 해상도와 무관하게 동일


def render(x, y, ylim, ticks, name):
    """평균선은 항상 원계열 평균(+10.9%). y 해상도만 바꿔 두 장을 만든다."""
    fig, ax = create_figure("line")

    ax.axhline(0, color=DIM, alpha=0.55, linewidth=1.2, zorder=2)
    ax.plot(x, y, color=FUNDING, linewidth=1.9, zorder=4,
            solid_capstyle="round", solid_joinstyle="round")
    ax.axhline(avg, color=DIM, linewidth=1.8, linestyle=(0, (5, 3)), zorder=3)
    ax.annotate(f"Period Avg +{avg:.1f}%", xy=(x.iloc[3], avg),
                xytext=(0, 10), textcoords="offset points", ha="left",
                va="bottom", fontsize=15, fontweight="bold", color=DIM, zorder=5)

    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(*ylim)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v:+d}%".replace("+0%", "0%") for v in ticks])
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    apply_style(fig, ax, "line")
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=20)
    print("saved:", *save_chart(fig, name, OUT))
    plt.close(fig)


# 8시간 원계열. 부제 그대로지만 -117~+104% 스파이크가 평탄 구간을 눌러버린다.
render(df["time"], df["annualized_pct"], (-130, 118),
       [-100, -50, 0, 50, 100], "spcx_perp_funding")

# 일평균. 레퍼런스 진폭(-40~+60%)에 대응하는 해상도.
daily = df.set_index("time")["annualized_pct"].resample("1D").mean().dropna()
render(daily.index.to_series(), daily, (-52, 88),
       [-40, 0, 40, 80], "spcx_perp_funding_daily")
