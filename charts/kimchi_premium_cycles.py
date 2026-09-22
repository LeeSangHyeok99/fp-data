"""김치 프리미엄(업비트/빗썸 KRW BTC vs 글로벌 USD BTC, 7일 평균)을 BTC 사이클 top과 함께."""
import sys

import pandas as pd
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import COLORS, save_chart, setup_font  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

MINT = "#7fe3c3"

# BTC 사이클 top (세로선). label_row: 라벨이 겹치지 않게 위/아래 단 배치
TOPS = [("2017-12-17", "BTC Top Dec '17", 0), ("2021-04-14", "BTC Top Apr '21", 1),
        ("2021-11-10", "BTC Top Nov '21", 0), ("2024-12-17", "BTC Top Dec '24", 1),
        ("2025-10-06", "BTC Top Oct '25", 0)]

# 사이클별 최대 프리미엄을 찍을 구간
PEAK_WINDOWS = [("2017-06-01", "2018-06-30", -34), ("2021-01-01", "2021-12-31", 0),
                ("2024-01-01", "2024-12-31", 0), ("2025-06-01", "2026-12-31", 0)]

df = pd.read_csv("outputs/data/kimchi_premium_daily.csv", parse_dates=["date"])
# 7일 평균 위에 중심 15일 평균을 한 번 더 (톱니 제거용). 피크는 49.6 -> 47.9 수준으로만 눌린다
df["premium_pct"] = df["premium_pct"].rolling(15, center=True, min_periods=1).mean()

setup_font()
fig, ax = plt.subplots(figsize=(16, 6.4), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor("none")

ax.plot(df["date"], df["premium_pct"], color=MINT, lw=1.5, solid_joinstyle="round")

ymax = 58
ax.set_ylim(-13, ymax)
ax.set_yticks([0, 20, 40])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "%.0f%%" % v))
ax.set_xlim(pd.Timestamp("2016-12-15"), df["date"].max())

# 0% 기준선
ax.axhline(0, color=COLORS["text_secondary"], alpha=0.55, lw=1.0, zorder=1)

for date, label, row in TOPS:
    d = pd.Timestamp(date)
    ax.axvline(d, color=COLORS["text_secondary"], alpha=0.45, lw=1.0, zorder=1)
    ax.annotate(label, (d, ymax - 2 - row * 4.5), xytext=(6, 0),
                textcoords="offset points", ha="left", va="top",
                fontsize=16, fontweight="bold", color=COLORS["text_secondary"])

for a, b, dx in PEAK_WINDOWS:
    w = df[(df["date"] >= a) & (df["date"] <= b)]
    i = w["premium_pct"].idxmax()
    x, y = w["date"][i], w["premium_pct"][i]
    ax.scatter(x, y, s=60, color=MINT, zorder=5, linewidths=0)
    ax.annotate("+%.1f%%" % y, (x, y), textcoords="offset points", xytext=(dx, 16),
                ha="center", fontsize=18, fontweight="bold", color=COLORS["text"])

ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
for spine in ax.spines.values():
    spine.set_visible(False)
for axis in ("x", "y"):
    ax.tick_params(axis=axis, labelsize=17, length=0, pad=8,
                   colors=COLORS["text_secondary"])
plt.setp(ax.xaxis.get_majorticklabels(), ha="center")

fig.tight_layout()
png, svg = save_chart(fig, "kimchi_premium_cycles", "outputs/charts/korea/premium")
print(png)
print(svg)
