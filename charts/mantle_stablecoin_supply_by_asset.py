"""
Stablecoin Supply on Mantle by Asset - Stacked Area Chart
Four Pillars design theme
Data source: DefiLlama stablecoin API (per-asset circulating supply on Mantle)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import create_figure, apply_style, save_chart, band_gradient, AXIS_CONFIG

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/mantle_stablecoin_supply_by_asset.csv', parse_dates=['date'])
df = df.set_index('date').sort_index()

# Bottom to top, matching reference stacking order
order = ['USDT0', 'USDe', 'USDY', 'USDC', 'AUSD']
pivot_m = df[order] / 1e6

# ─── Colors (reference palette) ────────────────────────────────────────
color_map = {
    'USDT0': '#6EE7C8',
    'USDe': '#5B6BE8',
    'USDY': '#A78BFA',
    'USDC': '#4FD1E0',
    'AUSD': '#F5B54A',
}
colors = [color_map[c] for c in order]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')
fig.set_size_inches(10.67, 5.2)
dates = pivot_m.index

x = mdates.date2num(dates)
lower = pivot_m[order[0]].values * 0
for c, color in zip(order, colors):
    upper = lower + pivot_m[c].values
    band_gradient(ax, x, lower, upper, color, spread=0.18)
    lower = upper

# ─── Annotations ────────────────────────────────────────────────────────
last = pivot_m.iloc[-1]
total = last.sum()
share = last['USDT0'] / total * 100
ax.annotate(
    f'{dates[-1]:%-d %b %Y}\n${total:,.0f}M, USDT0 {share:.0f}%',
    xy=(dates[-1], total), xytext=(dates[-1], 815), textcoords='data',
    fontsize=14, style='italic', color='#d1d4dc', ha='right', va='bottom',
    arrowprops=dict(arrowstyle='-', color='#d1d4dc', lw=1, alpha=0.7),
)
usdg_live = pd.Timestamp('2026-08-27')
ax.annotate(
    'USDG Contract Live 27 Aug,\n501,103 USDG On 10 Sep',
    xy=(usdg_live, pivot_m.loc[usdg_live].sum()), xytext=(dates[-1], 1015),
    textcoords='data', fontsize=14, style='italic',
    color='#F5B54A', ha='right', va='bottom',
    arrowprops=dict(arrowstyle='-', color='#F5B54A', lw=1, alpha=0.8),
)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[2, 5, 8, 11]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
for label in ax.xaxis.get_majorticklabels():
    label.set_rotation(45)
    label.set_ha('right')

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_ylim(0, 1180)
ax.set_yticks([0, 200, 400, 600, 800, 1000])
ax.set_yticklabels(['$0M', '$200M', '$400M', '$600M', '$800M', '$1,000M'])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 8)
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 8)
ax.set_xlim(dates.min(), dates.max())

# ─── Save ───────────────────────────────────────────────────────────────
png_path, svg_path = save_chart(fig, 'mantle_stablecoin_supply_by_asset', 'outputs/charts/mantle/stablecoin')
plt.close()
print(f"Saved: {png_path}\nSaved: {svg_path}")
