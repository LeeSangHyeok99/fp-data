"""
Bybit Exchange Wallets on Mantle by Asset - Stacked Area Chart
Four Pillars design theme
Data source: DefiLlama CEX transparency adapter (api.llama.fi/protocol/bybit, chainTvls.Mantle.tokensInUsd)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import create_figure, apply_style, save_chart, band_gradient, AXIS_CONFIG

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/bybit_mantle_wallets_by_asset.csv', parse_dates=['date'])
df = df.set_index('date').sort_index()

order = ['ETH', 'MNT', 'mETH', 'USDe', 'cmETH', 'FBTC', 'USDC', 'Other']
pivot_m = df[order] / 1e6

# ─── Colors (reference palette) ────────────────────────────────────────
color_map = {
    'ETH': '#6EE7C8',
    'MNT': '#5B6BE8',
    'mETH': '#A78BFA',
    'USDe': '#4FD1E0',
    'cmETH': '#F5B54A',
    'FBTC': '#E8827A',
    'USDC': '#8FA3B0',
    'Other': '#6D6D6D',
}
colors = [color_map[c] for c in order]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')
dates = pivot_m.index

x = mdates.date2num(dates)
lower = pivot_m[order[0]].values * 0
for c, color in zip(order, colors):
    upper = lower + pivot_m[c].values
    band_gradient(ax, x, lower, upper, color, spread=0.18)
    lower = upper

# ─── Annotation ─────────────────────────────────────────────────────────
total = pivot_m.iloc[-1].sum()
ax.annotate(
    f'{dates[-1]:%-d %b %Y}  ${total:,.0f}M',
    xy=(dates[-1], total), xytext=(-30, 55), textcoords='offset points',
    fontsize=14, style='italic', color='#d1d4dc', ha='right', va='bottom',
    arrowprops=dict(arrowstyle='-', color='#d1d4dc', lw=1, alpha=0.7),
)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
for label in ax.xaxis.get_majorticklabels():
    label.set_rotation(45)
    label.set_ha('right')

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_ylim(0, 800)
ax.set_yticks([0, 200, 400, 600, 800])
ax.set_yticklabels(['$0M', '$200M', '$400M', '$600M', '$800M'])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 8)
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 8)
ax.set_xlim(dates.min(), dates.max())

# ─── Save ───────────────────────────────────────────────────────────────
png_path, svg_path = save_chart(fig, 'bybit_mantle_wallets_by_asset', 'outputs/charts/mantle/exchange')
plt.close()
print(f"Saved: {png_path}\nSaved: {svg_path}")
