"""Tokenized stocks (left) vs tokenized treasuries (right) total value — rwa.xyz style."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
import config  # noqa: E402

BLUE = "#4e81ee"
LIGHT = "#dce2ef"
GREY = "#787b86"

FS_Y = 20  # 두 y축 공통
FS_X = 16  # x축 공통

OUT = Path("outputs/charts/rwa/asset_classes")
NAME = "tokenized_stocks_treasuries_total_value"


def total(csv):
    d = pd.read_csv(csv, parse_dates=["Date"]).set_index("Date")
    s = d.iloc[:, 2:].sum(axis=1)
    s = s[s.index >= "2025-01-01"]
    return s.rolling(7, center=True, min_periods=1).mean()


stocks = total("sources/rwa-xyz-stocks-market-caps.csv")
treas = total("sources/rwa-xyz-treasury-market-caps.csv")

config.setup_font()
fig, ax_r = plt.subplots(figsize=(11.9, 5.4))
ax_l = ax_r.twinx()

ax_r.fill_between(treas.index, treas.values, color=LIGHT, alpha=0.34, lw=0)
ax_r.plot(treas.index, treas.values, color=LIGHT, lw=1.6, alpha=0.95, solid_capstyle="butt")
ax_l.fill_between(stocks.index, stocks.values, color=BLUE, alpha=0.56, lw=0)
ax_l.plot(stocks.index, stocks.values, color=BLUE, lw=1.5, alpha=0.95, solid_capstyle="butt")

# 좌축 0~2.2B, 우축은 정확히 10배라 눈금이 서로 맞음
ax_l.set_ylim(0, 2.2e9)
ax_r.set_ylim(0, 22e9)
ax_l.set_yticks([0, 0.5e9, 1e9, 1.5e9, 2e9])
ax_l.set_yticklabels(["$0B", "$0.5B", "$1.0B", "$1.5B", "$2.0B"])
ax_r.set_yticks([0, 5e9, 10e9, 15e9, 20e9])
ax_r.set_yticklabels([f"${v}B" for v in [0, 5, 10, 15, 20]])

ax_l.yaxis.tick_left()
ax_r.yaxis.tick_right()
ax_l.tick_params(axis="y", labelsize=FS_Y, colors=BLUE, length=0, pad=8)
ax_r.tick_params(axis="y", labelsize=FS_Y, colors=LIGHT, length=0, pad=8)

ax_r.set_xlim(stocks.index.min(), stocks.index.max())
ax_r.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax_r.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax_r.tick_params(axis="x", labelsize=FS_X, colors=GREY, length=6, width=1.0)
plt.setp(ax_r.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

ax_l.grid(axis="y", color=GREY, alpha=0.5, ls="--", lw=0.8)
ax_l.set_axisbelow(True)
for a in (ax_l, ax_r):
    for s in a.spines.values():
        s.set_visible(False)

fig.canvas.draw()
# 첫 x라벨(Jan 2025) 제거
ax_r.get_xticklabels()[0].set_visible(False)
ax_r.xaxis.get_major_ticks()[0].tick1line.set_visible(False)

OUT.mkdir(parents=True, exist_ok=True)
for ext in ("png", "svg"):
    fig.savefig(OUT / f"{NAME}.{ext}", dpi=150, bbox_inches="tight", transparent=True)
print("saved", OUT / NAME, f"stocks last={stocks.iloc[-1]/1e9:.2f}B treas last={treas.iloc[-1]/1e9:.2f}B")
