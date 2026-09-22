"""
Metaplanet (3350.T) Enterprise Value vs BTC NAV — dual filled-area line chart.
Style: four-pillars, transparent BG, no title/legend/source.

REAL DATA from the source dashboard's underlying API (StrategyTracker, which
powers analytics.metaplanet.jp's embed):
  latest.json -> data.strategytracker.com/all.v<ver>.json -> companies['3350.T']

  Enterprise Value = market_cap_basic + debt - cash   (USD)
  BTC NAV          = holdings_value (BTC balance x BTC price, USD)

Verified against dashboard tooltips: Oct 3 2025 EV $4.70B / NAV $3.77B (exact).
EV here excludes preferred equity (no separate field), a small offset vs the
tooltip's "+ Preferred" line.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import io
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, FixedLocator
from config import setup_font, save_chart, apply_style, area_glow, endpoint_dot, COLORS

setup_font()

EV_BLUE = '#4d7cff'     # Enterprise Value
NAV_ORANGE = '#f0883e'  # BTC NAV
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'https://data.strategytracker.com'

# ----------------------------------------------------------------------
# Fetch real historical data
# ----------------------------------------------------------------------
latest = requests.get(f'{BASE}/latest.json', headers=UA, timeout=30).json()
full_file = latest['files']['full']
print('data version:', latest['version'], '| file:', full_file)

alldata = requests.get(f'{BASE}/{full_file}', headers=UA, timeout=60).json()
hd = alldata['companies']['3350.T']['historicalData']

df = pd.DataFrame({
    'date': pd.to_datetime(hd['dates']),
    'nav': pd.Series(hd['holdings_value'], dtype='float64'),
    'mc': pd.Series(hd['market_cap_basic'], dtype='float64'),
    'debt': pd.Series(hd['debt'], dtype='float64').fillna(0.0),
    'cash': pd.Series(hd['cash_balance'], dtype='float64').fillna(0.0),
})
df['ev'] = df['mc'] + df['debt'] - df['cash']
df = df.dropna(subset=['ev', 'nav']).sort_values('date').reset_index(drop=True)

# To $B
df['ev_b'] = df['ev'] / 1e9
df['nav_b'] = df['nav'] / 1e9

df[['date', 'ev_b', 'nav_b']].to_csv(
    'outputs/data/enterprise_value_vs_btc_nav.csv', index=False)

x = df['date']

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

area_glow(ax, x, df['nav_b'], color=NAV_ORANGE, max_alpha=0.22, power=2.0)
area_glow(ax, x, df['ev_b'], color=EV_BLUE, max_alpha=0.20, power=2.2)

ax.plot(x, df['nav_b'], color=NAV_ORANGE, linewidth=1.6, zorder=4, solid_capstyle='round')
ax.plot(x, df['ev_b'], color=EV_BLUE, linewidth=1.8, zorder=5, solid_capstyle='round')

endpoint_dot(ax, x.iloc[-1], df['ev_b'].iloc[-1], color=EV_BLUE, size=55)
endpoint_dot(ax, x.iloc[-1], df['nav_b'].iloc[-1], color=NAV_ORANGE, size=55)

# ----------------------------------------------------------------------
# Axes
# ----------------------------------------------------------------------
ev_max = df['ev_b'].max()
# Clean ticks, <=5: largest even tick at/below the peak, peak pokes above top line
top_tick = int(np.floor(ev_max / 2) * 2)
ax.set_ylim(0, ev_max * 1.08)
ax.yaxis.set_major_locator(FixedLocator(np.arange(0, top_tick + 0.1, 2)))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}B"))

tick_dates = pd.to_datetime(['2024-09-01', '2025-02-01', '2025-07-01',
                             '2025-12-01', '2026-05-01'])
tick_dates = tick_dates[(tick_dates >= x.iloc[0]) & (tick_dates <= x.iloc[-1])]
ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(tick_dates)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(x.iloc[0], x.iloc[-1] + pd.Timedelta(days=5))

apply_style(fig, ax, 'line')

out_dir = 'outputs/charts/bitcoin/treasury'
png, svg = save_chart(fig, 'enterprise_value_vs_btc_nav', out_dir)
plt.close(fig)

print('saved:', png)
print(f"points {len(df)} | {x.iloc[0].date()} -> {x.iloc[-1].date()}")
print(f"EV peak ${df['ev_b'].max():.2f}B | EV last ${df['ev_b'].iloc[-1]:.2f}B | "
      f"NAV last ${df['nav_b'].iloc[-1]:.2f}B | ratio {df['ev_b'].iloc[-1]/df['nav_b'].iloc[-1]:.2f}x")
