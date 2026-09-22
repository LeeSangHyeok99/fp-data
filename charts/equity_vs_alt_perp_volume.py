"""
Equity perps vs top-30 altcoin perps, 30-day average daily volume (Jan ~ Jul 2026)
Four Pillars 스타일 (인포그래픽용, 1:1 정사각). 실API 버전.

거래소를 섞지 않고 따로 본 뒤 합친 것까지, 세 벌 x 두 장 = 여섯 장:
  {binance, hyperliquid, both} x {절대 규모 ($B, 선형), 인덱스 100 (로그)}

데이터: scripts/fetch_perp_volume_api.py 가 만든
        outputs/data/equity_vs_alt_perp_volume_api.csv
  알트(파랑) = 시총 상위 30 알트 퍼프
  주식(주황) = Binance 주식 퍼프(EQUITY/HK/KR/PREMARKET) + Hyperliquid HIP-3 주식 퍼프

인덱스 기준일(base)은 변종마다 다르다. Binance 주식 퍼프는 2026-01-28 상장이라
30일 이동평균이 다 차는 2026-02-27 부터 100 으로 잡는다. 그 전 구간을 기준으로
잡으면 반쪽짜리 MA 때문에 증가율이 몇 배로 부풀려진다.
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
W0, W1 = "2026-01-10", "2026-07-12"   # 레퍼런스와 동일 윈도
OUT = "outputs/charts/perps/volume"

SMOOTH = 9   # 30일 MA 위에 얹는 중앙정렬 이동평균(일). 0이면 스무딩 없음.

# 변종별 컬럼 / 인덱스 기준일 / 축 / 라벨 위치(데이터 좌표)
VARIANTS = [
    dict(key="binance", alt="alt_binance", eq="equity_binance", base="2026-02-27",
         ytop=11, yticks=[0, 5, 10], abs_lab=(6.0, 4.4),
         log_ylim=(50, 15000), log_ticks=[100, 500, 1000, 5000, 10000],
         log_lab=(11000, 190)),
    dict(key="hyperliquid", alt="alt_hyperliquid", eq="equity_hyperliquid", base=W0,
         ytop=2.6, yticks=[0, 1, 2], abs_lab=(2.42, 2.14),
         log_ylim=(60, 8000), log_ticks=[100, 500, 1000, 5000],
         log_lab=(6000, 350)),
    # 교차본: 알트는 Hyperliquid, 주식은 Binance. 각 거래소가 강한 쪽만 본 것.
    # 거래소가 달라 규모 비교는 못 하고 추세만 본다.
    dict(key="hlalt_binaneq", alt="alt_hyperliquid", eq="equity_binance",
         base="2026-02-27",
         ytop=8.0, yticks=[0, 2, 4, 6], abs_lab=(7.7, 7.0),
         log_ylim=(50, 15000), log_ticks=[100, 500, 1000, 5000, 10000],
         log_lab=(11000, 320)),
]
# 합산본은 만들지 않는다. 거래소별로 심볼 집합도 분류 기준도 달라서, 합치면
# 두 정의를 한 라인에 섞게 된다. 비교는 같은 거래소 안에서만 한다.

df = pd.read_csv("outputs/data/equity_vs_alt_perp_volume_api.csv",
                 parse_dates=["date"]).set_index("date").loc[W0:W1]


def smooth(s):
    """일별 톱니 제거. min_periods=1 이라 양 끝점이 잘리지 않는다."""
    return s.rolling(SMOOTH, center=True, min_periods=1).mean() if SMOOTH else s


def money(v):
    return f"\\${v*1000:,.0f}M" if v < 1 else f"\\${v:,.1f}B"


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
    ax.set_xlim(blue.index.min(), blue.index.max())
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def label(ax, x, text, y, color, side="right"):
    left = side == "left"
    ax.annotate(text, xy=(x, y), xytext=(10 if left else -10, 0),
                textcoords="offset points", ha=side, va="center",
                fontsize=15, fontweight="bold", color=color, zorder=6)


def finish(ax, fig, name):
    apply_style(fig, ax, "line")
    ax.tick_params(axis="y", labelsize=20)
    ax.tick_params(axis="x", labelsize=18)
    print("saved:", *save_chart(fig, name, OUT))


for v in VARIANTS:
    # 라벨 숫자는 스무딩 전 실데이터. 중앙정렬 이동평균은 양 끝에서 표본이
    # 반쪽이라 끝점을 안쪽으로 끌어당긴다. 선은 스무딩본, 숫자는 원본.
    # 절대 규모는 전 구간(30일 MA 자체는 상장 전 0 을 포함해도 맞는 값이다).
    # 인덱스만 base 이후로 자른다. 반쪽 MA 로 나누면 증가율이 부풀려진다.
    alt_raw, eq_raw = df[v["alt"]], df[v["eq"]]
    alt, equity = smooth(alt_raw), smooth(eq_raw)
    alt_b, eq_b = alt.loc[v["base"]:], equity.loc[v["base"]:]
    x0, x1 = alt.index[0], alt.index[-1]

    def pct(s):
        return (s.iloc[-1] / s.iloc[0] - 1) * 100

    # ---- 1) 절대 규모 -------------------------------------------------------
    fig, ax = square_figure()
    draw(ax, alt, equity)
    # 라벨은 좌측 중단. 알트 피크가 우측 상단을 지나가서 오른쪽에 두면 겹친다.
    ya, ye = v["abs_lab"]
    label(ax, x0, f"Top-30 Alt Perps\n{money(alt_raw.iloc[0])} → "
                  f"{money(alt_raw.iloc[-1])}", ya, ALT, "left")
    label(ax, x0, f"Equity Perps\n{money(eq_raw.iloc[0])} → "
                  f"{money(eq_raw.iloc[-1])}", ye, EQUITY, "left")

    ax.set_ylim(0, v["ytop"])
    ax.set_yticks(v["yticks"])
    ax.set_yticklabels([f"\\${t:g}B" for t in v["yticks"]])
    finish(ax, fig, f"equity_vs_alt_perp_volume_{v['key']}")

    # ---- 2) 인덱스 (base = 100), 로그 --------------------------------------
    fig, ax = square_figure()
    draw(ax, alt_b / alt_b.iloc[0] * 100, eq_b / eq_b.iloc[0] * 100)
    ye, ya = v["log_lab"]
    base_raw = df.loc[v["base"]:]
    label(ax, x1, f"Equity Perps\n+{pct(base_raw[v['eq']]):,.0f}%", ye, EQUITY)
    label(ax, x1, f"Alt Perps\n{pct(base_raw[v['alt']]):+,.0f}%".replace("-", "−"),
          ya, ALT)

    ax.set_yscale("log")
    ax.set_ylim(*v["log_ylim"])
    ax.set_yticks(v["log_ticks"])
    ax.set_yticklabels([f"{t:,}" for t in v["log_ticks"]])
    ax.minorticks_off()
    finish(ax, fig, f"equity_vs_alt_perp_volume_{v['key']}_indexed")
