"""
Equity perps vs top-30 altcoin perps, 30-day avg daily volume (Jan ~ Jul 2026)
레퍼런스 내재화판. Four Pillars 스타일, 인포그래픽용 1:1 정사각 두 장.

  1) equity_vs_alt_perp_volume_traced          절대 규모 ($B, 선형)
  2) equity_vs_alt_perp_volume_traced_indexed  시작점 100 기준 인덱스 (로그)

데이터: outputs/data/equity_vs_alt_perp_volume.csv (레퍼런스 발표 끝점에 맞춰
        트레이스한 주간 시계열). 실API 버전은 equity_vs_alt_perp_volume.py.
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, save_chart, setup_font

ALT = "#4285f4"      # 블루 (알트 퍼프)
EQUITY = "#e8710a"   # 오렌지 (주식 퍼프)
OUT = "outputs/charts/perps/volume"

df = pd.read_csv("outputs/data/equity_vs_alt_perp_volume.csv",
                 parse_dates=["date"]).set_index("date")
alt, equity = df["alt_perps_bn"], df["equity_perps_bn"]
alt_idx, eq_idx = df["alt_index"], df["equity_index"]


def money(v):
    return f"\\${v*1000:,.0f}M" if v < 1 else f"\\${v:,.1f}B"


def pct(s):
    return (s.iloc[-1] / s.iloc[0] - 1) * 100


def square_figure():
    setup_font()
    return plt.subplots(figsize=(8, 8), dpi=150)


def draw(ax, blue, orange):
    """라인 + 끝점 도트. clip_on=False 로 축 경계에서 끝이 잘리지 않게."""
    for s, c in ((blue, ALT), (orange, EQUITY)):
        ax.plot(s.index, s, color=c, linewidth=2.6, zorder=4, clip_on=False,
                solid_capstyle="round", solid_joinstyle="round")
        ax.scatter(s.index[-1], s.iloc[-1], color=c, s=52, zorder=5,
                   edgecolors="none", clip_on=False)
    ax.set_xlim(df.index.min(), df.index.max())
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def label(ax, text, y, color):
    ax.annotate(text, xy=(df.index[-1], y), xytext=(-10, 0),
                textcoords="offset points", ha="right", va="center",
                fontsize=15, fontweight="bold", color=color, zorder=6)


def finish(ax, fig, name):
    apply_style(fig, ax, "line")
    ax.tick_params(axis="y", labelsize=20)
    ax.tick_params(axis="x", labelsize=18)
    print("saved:", *save_chart(fig, name, OUT))


# -----------------------------------------------------------------------------
# 1) 절대 규모
# -----------------------------------------------------------------------------
fig, ax = square_figure()
draw(ax, alt, equity)
label(ax, f"Top-30 Alt Perps\n{money(alt.iloc[0])} → {money(alt.iloc[-1])}",
      9.6, ALT)
label(ax, f"Equity Perps\n{money(equity.iloc[0])} → {money(equity.iloc[-1])}",
      8.5, EQUITY)

ax.set_ylim(0, 10)
ax.set_yticks([0, 2.5, 5, 7.5, 10])   # 레퍼런스와 동일한 5개 눈금
ax.set_yticklabels(["$0B", "$2.5B", "$5.0B", "$7.5B", "$10B"])
finish(ax, fig, "equity_vs_alt_perp_volume_traced")

# -----------------------------------------------------------------------------
# 2) 인덱스 (100 = 시작점), 로그 스케일
# -----------------------------------------------------------------------------
fig, ax = square_figure()
draw(ax, alt_idx, eq_idx)
label(ax, f"Equity Perps\n+{pct(equity):,.0f}%", 12500, EQUITY)
label(ax, f"Alt Perps\n−{-pct(alt):,.0f}%", 145, ALT)

ax.set_yscale("log")
ax.set_ylim(50, 20000)
ax.set_yticks([100, 500, 1000, 5000, 10000])
ax.set_yticklabels(["100", "500", "1,000", "5,000", "10,000"])
ax.minorticks_off()
finish(ax, fig, "equity_vs_alt_perp_volume_traced_indexed")
