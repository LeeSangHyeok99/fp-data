"""
BTC Price after Strategy's BTC-sale disclosure — line chart
Style: four-pillars, transparent BG, no title/legend/source.
Highlights the decline following the disclosure date.
Data: outputs/data/btc_price_120d.csv (CoinGecko daily, USD)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator
from config import setup_font, save_chart, apply_style, area_glow, endpoint_dot, COLORS

setup_font()

BTC_ORANGE = '#F7931A'
DIM = '#6b5a3e'  # pre-event dimmed line

# Disclosure inflection (approximate — adjust to the verified filing date)
EVENT_DATE = pd.Timestamp('2026-05-26')
# Focus window: run-up + post-disclosure decline
WINDOW_START = pd.Timestamp('2026-04-01')

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
df = pd.read_csv('outputs/data/btc_price_120d.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)
df = df[df['date'] >= WINDOW_START].reset_index(drop=True)

x = df['date']
y = df['price']

# Split pre/post event for emphasis
post_mask = x >= EVENT_DATE

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

# Pre-event: dimmed
pre = df[x <= EVENT_DATE]
ax.plot(pre['date'], pre['price'], color=DIM, linewidth=2.2, zorder=3,
        solid_capstyle='round')

# Post-event: full brand color + glow under the segment
post = df[x >= EVENT_DATE]
ax.plot(post['date'], post['price'], color=BTC_ORANGE, linewidth=2.8, zorder=4,
        solid_capstyle='round')
area_glow(ax, post['date'], post['price'], color=BTC_ORANGE,
          max_alpha=0.16, power=2.2)

# Event marker
ax.axvline(EVENT_DATE, color=COLORS['text_secondary'], linewidth=1.3,
           linestyle=(0, (4, 3)), alpha=0.8, zorder=2)

# Endpoint dot + price label
endpoint_dot(ax, x.iloc[-1], y.iloc[-1], color=BTC_ORANGE, size=60)
ax.annotate(f"${y.iloc[-1]/1000:.1f}K",
            xy=(x.iloc[-1], y.iloc[-1]), xytext=(-6, 14),
            textcoords='offset points', ha='right', va='bottom',
            fontsize=15, fontweight='bold', color=BTC_ORANGE)

# Event annotation (placed high-left of the marker, clear of the line)
ax.annotate("Strategy BTC sale\ndisclosed",
            xy=(EVENT_DATE, 83600), xytext=(-12, 0),
            textcoords='offset points', ha='right', va='top',
            fontsize=12.5, fontweight='bold', color=COLORS['text'],
            linespacing=1.3)

# ----------------------------------------------------------------------
# Axes
# ----------------------------------------------------------------------
ax.set_ylim(65000, 84000)
ax.yaxis.set_major_locator(MultipleLocator(5000))  # 65,70,75,80K → clean, ≤5 ticks
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(x.iloc[0], x.iloc[-1] + pd.Timedelta(days=3))

apply_style(fig, ax, 'line')

out_dir = 'outputs/charts/bitcoin/price'
png, svg = save_chart(fig, 'btc_price_strategy_sale', out_dir)
plt.close(fig)

print('saved:', png)
print('event:', EVENT_DATE.date(),
      '| peak', f"${y.max()/1000:.1f}K", '| last', f"${y.iloc[-1]/1000:.1f}K")
