"""주식 퍼프 일거래대금, 거래소별 (Binance vs Hyperliquid HIP-3).

equity_vs_alt_perp_volume.py 가 둘을 합쳐 한 선으로 그리는 것을, 여기서는
출처별로 갈라 놓는다. 같은 CSV, 같은 창, 같은 스무딩이라 두 차트가 서로
대조된다.

주의: Hyperliquid 명목은 파생값이다. HL 캔들이 quote volume 을 안 줘서
base volume × OHLC 평균가로 만든다. Binance 는 거래소가 주는 quote volume
그대로라, 두 선의 정확도가 같지 않다.

데이터: scripts/fetch_perp_volume_api.py
"""

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, save_chart, setup_font

BINANCE = "#e8710a"   # 오렌지
HYPERL = "#4285f4"    # 블루
TOTAL = "#b0b5bd"     # 그레이, 합계
W0, W1 = "2026-01-10", "2026-07-12"
SMOOTH = 9
OUT = "outputs/charts/perps/volume"

df = pd.read_csv("outputs/data/equity_vs_alt_perp_volume_api.csv",
                 parse_dates=["date"]).set_index("date").loc[W0:W1]
# 합계는 두 거래소의 합. 산술평균이 아니다. 평균을 내면 "거래소 하나당 평균
# 거래대금"이 돼서 시장 규모가 절반으로 줄어든다.
raw = {"Binance": df["equity_binance"], "Hyperliquid": df["equity_hyperliquid"],
       "Combined": df["equity_total"]}
sm = {k: v.rolling(SMOOTH, center=True, min_periods=1).mean() for k, v in raw.items()}


def money(v):
    return f"${v*1000:,.0f}M" if v < 1 else f"${v:,.1f}B"


setup_font()
fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

ZORDER = {"Combined": 3, "Binance": 4, "Hyperliquid": 4}
for (name, s), color in zip(sm.items(), (BINANCE, HYPERL, TOTAL)):
    ax.plot(s.index, s, color=color, linewidth=2.6, zorder=ZORDER[name],
            clip_on=False, solid_capstyle="round", solid_joinstyle="round")
    ax.scatter(s.index[-1], s.iloc[-1], color=color, s=52, zorder=5,
               edgecolors="none", clip_on=False)

# 라벨 숫자는 스무딩 전 원본. 첫 거래일이 다르니 시작값 대신 끝값과 점유율.
total = raw["Combined"].iloc[-1]
for (name, color, y) in (("Combined", TOTAL, 8.4), ("Binance", BINANCE, 7.4),
                         ("Hyperliquid", HYPERL, 6.4)):
    v = raw[name].iloc[-1]
    share = "" if name == "Combined" else f"  ({v/total*100:.0f}%)"
    ax.annotate(f"{name}\n{money(v)}{share}", xy=(df.index[-1], y),
                xytext=(-10, 0), textcoords="offset points", ha="right",
                va="center", fontsize=15, fontweight="bold", color=color, zorder=6)

ax.set_ylim(0, 9.0)
ax.set_yticks([0, 2, 4, 6, 8])
ax.set_yticklabels(["$0B", "$2B", "$4B", "$6B", "$8B"])
ax.set_xlim(df.index.min(), df.index.max())
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "line")
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=18)
print("saved:", *save_chart(fig, "equity_perp_volume_by_venue", OUT))
plt.close(fig)
