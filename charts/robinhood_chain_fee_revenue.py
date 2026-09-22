"""Robinhood Chain — daily fee revenue, Aug 6 to Sep 3 2026.
Source: arbdata.com/api/robinhood/economics (Entropy Advisors).
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter  # noqa: E402

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import apply_style, create_figure, gradient_rounded_bar, save_chart  # noqa: E402

df = pd.read_csv("outputs/data/robinhood_chain_fee_revenue.csv", parse_dates=["date"])
COLOR = "#CCFF00"  # Robinhood brand green

fig, ax = create_figure("bar")

# lock limits/ticks before drawing: corner rounding is computed in pixels
ax.set_ylim(0, 5_000_000)
ax.yaxis.set_major_locator(FixedLocator([0, 1e6, 2e6, 3e6, 4e6]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v / 1e6:.0f}M"))
ax.set_xlim(df["date"].min() - pd.Timedelta(hours=14),
            df["date"].max() + pd.Timedelta(hours=14))
# anchor ticks on the data so both endpoints get labelled
ax.set_xticks(df["date"][::4])
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

width = 0.62  # in days
for d, v in zip(mdates.date2num(df["date"]), df["fee_revenue_usd"]):
    gradient_rounded_bar(ax, d, width, v, COLOR, floor=0.55, round_top=False)

apply_style(fig, ax, "bar")
ax.tick_params(axis="y", labelsize=19, length=0)
ax.tick_params(axis="x", labelsize=17, rotation=45, length=6, width=1)
import matplotlib.pyplot as plt  # noqa: E402
plt.setp(ax.xaxis.get_majorticklabels(), ha="right")

png, svg = save_chart(fig, "robinhood_chain_fee_revenue",
                      "outputs/charts/robinhood/revenue")
print(png)
print(svg)

# sanity: Sep 2 is the peak and the last 3 days each clear $2M
assert df.loc[df["fee_revenue_usd"].idxmax(), "date"] == pd.Timestamp("2026-09-02")
assert (df["fee_revenue_usd"].tail(3) > 2e6).all()
