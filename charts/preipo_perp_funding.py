"""대표 프리IPO 주식 퍼프 3종의 연환산 펀딩, 2026-05-21 ~ 08-07 (일평균).
Four Pillars 스타일 (와이드). 종목마다 한 장씩 따로 그린다.

  preipo_funding_spacex     SPCX       05-21 상장, 06-12 나스닥 IPO
  preipo_funding_openai     OPENAI     05-26 상장
  preipo_funding_anthropic  ANTHROPIC  06-02 상장

축(x 범위, y 눈금)은 세 장 모두 같게 고정한다. 나란히 놓고 비교하는 용도라
종목마다 스케일이 다르면 안 된다. OpenAI, Anthropic 은 상장이 늦어 선이
중간부터 시작하는데, 그 왼쪽 빈 구간이 "아직 상장 전"이라는 정보다.

핵심: 셋 다 +5.475%(0.005%/8h) 고정에서 출발한다. 비상장 회사는 비교할 실제
주가가 없어 프리미엄 성분이 안 붙고 기본요율만 찍힌다. 이 고정이 풀린 건
SPCX 뿐이고 풀린 시점이 나스닥 IPO 다.

데이터: scripts/fetch_preipo_funding.py → outputs/data/preipo_funding_8h.csv
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import COLORS, apply_style, create_figure, save_chart

DIM = COLORS["text_secondary"]
OUT = "outputs/charts/perps/funding"
IPO = pd.Timestamp("2026-06-12")   # SpaceX 나스닥 상장

# (심볼, 표시명, 색, 파일명, IPO 선 표시 여부)
SERIES = [
    ("SPCX", "SpaceX", "#4285f4", "spacex", True),
    ("OPENAI", "OpenAI", "#e8710a", "openai", False),
    ("ANTHROPIC", "Anthropic", "#26a69a", "anthropic", False),
]

df = pd.read_csv("outputs/data/preipo_funding_8h.csv", parse_dates=["time"])
daily = {s: g.set_index("time")["annualized_pct"].resample("1D").mean().dropna()
         for s, g in df.groupby("symbol")}
X0 = min(s.index.min() for s in daily.values())
X1 = max(s.index.max() for s in daily.values())

for key, name, color, fname, show_ipo in SERIES:
    s = daily[key]
    avg = df[df.symbol == key]["annualized_pct"].mean()   # 평균은 8시간 원계열 기준

    fig, ax = create_figure("line")
    ax.axhline(0, color=DIM, alpha=0.55, linewidth=1.2, zorder=2)
    ax.axhline(avg, color=DIM, linewidth=1.8, linestyle=(0, (5, 3)), zorder=3)
    ax.annotate(f"Period Avg {avg:+.1f}%", xy=(X0, avg), xytext=(6, 12),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=15, fontweight="bold", color=DIM, zorder=5)

    if show_ipo:
        ax.axvline(IPO, color=DIM, alpha=0.5, linewidth=1.4,
                   linestyle=(0, (4, 3)), zorder=2)
        ax.annotate("Nasdaq IPO", xy=(IPO, 100), xytext=(-8, 0),
                    textcoords="offset points", ha="right", va="top",
                    fontsize=14, fontweight="bold", color=DIM, zorder=5)

    ax.plot(s.index, s, color=color, linewidth=2.4, zorder=4,
            solid_capstyle="round", solid_joinstyle="round")
    ax.annotate(name, xy=(X1, 92), xytext=(-4, 0), textcoords="offset points",
                ha="right", va="top", fontsize=19, fontweight="bold",
                color=color, zorder=6)

    ax.set_xlim(X0, X1)
    ax.set_ylim(-58, 108)
    ax.set_yticks([-40, 0, 40, 80])
    ax.set_yticklabels(["-40%", "0%", "+40%", "+80%"])
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO,
                                                     interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    apply_style(fig, ax, "line")
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=20)
    print(f"{name:10s} avg {avg:+.2f}%  선 시작 {s.index[0]:%m-%d}")
    print("saved:", *save_chart(fig, f"preipo_funding_{fname}", OUT))
    plt.close(fig)
