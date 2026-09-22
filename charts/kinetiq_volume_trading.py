"""
Markets by Kinetiq — Volume & Trading (1:1 square panels), REAL DATA
Source: https://markets.xyz/stats  (GET /api/stats/daily-volume)
Data:   outputs/data/kinetiq_daily_volume.json  (22 markets, Jan 12 – Jun 9 2026)
Style:  four-pillars, transparent BG, no title/legend/source.

Validated against the site tooltips:
  Feb 3 2026 peak $98.3M | Mar 9 2026 US500 $26.97M, USOIL $17.19M (exact match)
  Grand total $3.78B | US500 48.3% ($1.83B = the dominant blue line)
"""

import sys, json
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG

setup_font()

# Per-market colors (brand-aligned with the markets.xyz tooltips)
COLOR = {
    'US500': '#2f4fd6', 'USTECH': '#22b8cf', 'SILVER': '#c4c9d0',
    'USOIL': '#e0683a', 'SMALL2000': '#845ef7', 'TSLA': '#e82127',
    'GOLD': '#f5b820', 'USBOND': '#4c9f70', 'NVDA': '#76b900',
    'BABA': '#ff6a00', 'MU': '#e8d9a8', 'GOOGL': '#4285f4',
    'EUR': '#5b8def', 'USENERGY': '#20c997', 'PLTR': '#5b6168',
    'AAPL': '#e8eaed', 'BMNR': '#e84393', 'TENCENT': '#3fa9f5',
    'XIAOMI': '#ff7a45', 'SEMI': '#9b59b6', 'GLDMINE': '#d4a017',
    'RTX': '#b0413e',
}
TOTAL_WHITE = '#f1f3f5'

# ----------------------------------------------------------------------
# Load real data -> daily matrix (date x market), $ values
# ----------------------------------------------------------------------
raw = json.load(open('outputs/data/kinetiq_daily_volume.json'))
df = pd.DataFrame([(r[0], r[2], r[3]) for r in raw], columns=['date', 'sym', 'vol'])
df['date'] = pd.to_datetime(df['date'])

piv = (df.pivot_table(index='date', columns='sym', values='vol', aggfunc='sum')
         .fillna(0).sort_index())
order = piv.sum().sort_values(ascending=False).index.tolist()   # biggest at bottom
piv = piv[order] / 1e6        # -> $M
dates = piv.index
colors = [COLOR.get(s, '#787b86') for s in order]


def style_axes(fig, ax):
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'],
                   pad=AXIS_CONFIG['y_tick']['pad'], length=0,
                   colors=AXIS_CONFIG['y_tick']['color'])
    ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'],
                   pad=AXIS_CONFIG['x_tick']['pad'], rotation=45,
                   colors=AXIS_CONFIG['x_tick']['color'])
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')


out_dir = 'outputs/charts/kinetiq/volume'

# ======================================================================
# Chart 1 — Daily volume (stacked bars), 1:1
# ======================================================================
fig1, ax1 = plt.subplots(figsize=(7, 7), dpi=150)
bottom = np.zeros(len(dates))
for i, s in enumerate(order):
    ax1.bar(dates, piv[s].values, width=0.9, bottom=bottom,
            color=colors[i], zorder=3, linewidth=0)
    bottom += piv[s].values

ax1.set_ylim(0, 100)
ax1.yaxis.set_major_locator(MultipleLocator(25))   # 0,25,50,75,100
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}M"))
style_axes(fig1, ax1)
ax1.set_xlim(dates[0] - pd.Timedelta(days=2), dates[-1] + pd.Timedelta(days=2))
fig1.tight_layout()
png1, _ = save_chart(fig1, 'kinetiq_daily_volume', out_dir)
plt.close(fig1)

# ======================================================================
# Chart 2 — Cumulative volume (lines + white total), 1:1
# ======================================================================
cum = piv.cumsum() / 1000.0          # -> $B
cum_total = cum.sum(axis=1)

fig2, ax2 = plt.subplots(figsize=(7, 7), dpi=150)
# small markets first (background), US500 (order[0]) last + filled
for s in order[1:][::-1]:
    ax2.plot(dates, cum[s].values, color=COLOR.get(s, '#787b86'),
             linewidth=1.5, zorder=3)
ax2.fill_between(dates, cum[order[0]].values, color='#3b5bdb', alpha=0.18, zorder=2)
ax2.plot(dates, cum[order[0]].values, color='#3b5bdb', linewidth=2.4, zorder=4)
ax2.plot(dates, cum_total.values, color=TOTAL_WHITE, linewidth=2.8, zorder=5,
         solid_capstyle='round')

ax2.set_ylim(0, 4)
ax2.yaxis.set_major_locator(MultipleLocator(1))    # 0,1,2,3,4
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}B"))
style_axes(fig2, ax2)
ax2.set_xlim(dates[0], dates[-1])
fig2.tight_layout()
png2, _ = save_chart(fig2, 'kinetiq_cumulative_volume', out_dir)
plt.close(fig2)

print('saved:', png1)
print('saved:', png2)
print('markets:', len(order), '| dates:', len(dates))
print('grand total: $%.2fB' % cum_total.iloc[-1],
      '| US500: $%.2fB' % cum[order[0]].iloc[-1],
      '| daily peak: $%.1fM' % piv.sum(axis=1).max())
