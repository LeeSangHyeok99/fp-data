"""
BTC Price (1-week) around Strategy's first BTC-sale disclosure — line chart
Style: four-pillars, transparent BG, no title/legend/source.
Event: 2026-06-01 8-K discloses 32 BTC sold ($2.5M) during May 26-31.
Data: outputs/data/btc_price_hourly_1w.csv (Binance BTCUSDT 1h close)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator
from config import setup_font, save_chart, apply_style, area_glow, endpoint_dot, COLORS

setup_font()

BTC_ORANGE = '#F7931A'
DIM = '#6b5a3e'  # pre-disclosure dimmed line

# Strategy's first BTC-sale 8-K filed Jun 1, 2026, 08:00 ET (EDT, UTC-4)
EVENT_DT = pd.Timestamp('2026-06-01 08:00')  # ET

# ----------------------------------------------------------------------
# Data — convert UTC timestamps to US Eastern (EDT, UTC-4)
# ----------------------------------------------------------------------
df = pd.read_csv('outputs/data/btc_price_hourly_1w.csv', parse_dates=['datetime_utc'])
df = df.sort_values('datetime_utc').reset_index(drop=True)
df['datetime_et'] = df['datetime_utc'] - pd.Timedelta(hours=4)
x = df['datetime_et']
y = df['price']

pre = df[x <= EVENT_DT]
post = df[x >= EVENT_DT]

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

ax.plot(pre['datetime_et'], pre['price'], color=DIM, linewidth=2.4,
        zorder=3, solid_capstyle='round')
ax.plot(post['datetime_et'], post['price'], color=BTC_ORANGE, linewidth=3.0,
        zorder=4, solid_capstyle='round')
area_glow(ax, post['datetime_et'], post['price'], color=BTC_ORANGE,
          max_alpha=0.16, power=2.2)

# Event marker
ax.axvline(EVENT_DT, color=COLORS['text_secondary'], linewidth=1.3,
           linestyle=(0, (4, 3)), alpha=0.85, zorder=2)

# Price at disclosure (dot + number)
ev_price = float(df.iloc[(x - EVENT_DT).abs().argmin()]['price'])
endpoint_dot(ax, EVENT_DT, ev_price, color=COLORS['text'], size=55)
ax.annotate(f"${ev_price/1000:.1f}K",
            xy=(EVENT_DT, ev_price), xytext=(10, 12),
            textcoords='offset points', ha='left', va='bottom',
            fontsize=14, fontweight='bold', color=COLORS['text'])

# Endpoint dot + price label
endpoint_dot(ax, x.iloc[-1], y.iloc[-1], color=BTC_ORANGE, size=60)
ax.annotate(f"${y.iloc[-1]/1000:.1f}K",
            xy=(x.iloc[-1], y.iloc[-1]), xytext=(10, 4),
            textcoords='offset points', ha='left', va='center',
            fontsize=15, fontweight='bold', color=BTC_ORANGE)

# Event annotation (top-left of the marker, clear of the line)
ax.annotate("Strategy BTC sale\ndisclosed (Jun 1)",
            xy=(EVENT_DT, 77600), xytext=(-12, 0),
            textcoords='offset points', ha='right', va='top',
            fontsize=12.5, fontweight='bold', color=COLORS['text'],
            linespacing=1.3)

# ----------------------------------------------------------------------
# Axes
# ----------------------------------------------------------------------
ax.set_ylim(69000, 78000)
ax.yaxis.set_major_locator(MultipleLocator(2000))  # 70,72,74,76,78K → 5 ticks
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))

ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(
    mdates.DateFormatter('%b %-d'))  # no leading zero: "Jun 1", "Jun 2"
ax.set_xlim(x.iloc[0], x.iloc[-1] + pd.Timedelta(hours=14))

apply_style(fig, ax, 'line')

out_dir = 'outputs/charts/bitcoin/price'
png, svg = save_chart(fig, 'btc_price_strategy_sale_1w', out_dir)
plt.close(fig)

peak = y.max()
print('saved:', png)
print(f"week peak ${peak/1000:.1f}K -> last ${y.iloc[-1]/1000:.1f}K "
      f"({(y.iloc[-1]/peak-1)*100:.1f}%)")
