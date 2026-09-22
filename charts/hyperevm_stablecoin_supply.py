"""
HyperEVM Stablecoin Supply - Stacked Area Chart
Four Pillars design theme
Data source: Dune Analytics (@fourpillars)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

# SUIT Bold font
suit_path = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
if suit_path.exists():
    fm.fontManager.addfont(str(suit_path))
    suit_font = fm.FontProperties(fname=str(suit_path))
else:
    suit_font = None

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hyperevm_stablecoin_supply_market_share.csv')
df['date'] = pd.to_datetime(df['date'])

# Top 4 tokens + Others
top_tokens = ['USDC', 'USD₮0', 'USDH', 'USDe']
df_top = df[df['token_name'].isin(top_tokens)].copy()
df_others = df[~df['token_name'].isin(top_tokens)].groupby('date')['supply'].sum().reset_index()
df_others['token_name'] = 'Others'

df_combined = pd.concat([df_top[['date', 'token_name', 'supply']], df_others], ignore_index=True)

# Pivot
pivot = df_combined.pivot_table(index='date', columns='token_name', values='supply', aggfunc='sum').fillna(0)
pivot = pivot.sort_index()

# Order: bottom to top (largest at bottom)
order = ['USDC', 'USD₮0', 'USDH', 'USDe', 'Others']
order = [c for c in order if c in pivot.columns]
pivot = pivot[order]

# Filter from May 2025
pivot = pivot[pivot.index >= '2025-05-01']

# Convert to billions
pivot_b = pivot / 1e9

# ─── Colors (brand colors) ─────────────────────────────────────────────
color_map = {
    'USDC': '#2775ca',
    'USD₮0': '#26a17b',
    'USDH': '#50e3c2',
    'USDe': '#b8b8d1',
    'feUSD': '#7ee8b8',
    'Others': '#787b86',
}
colors = [color_map.get(c, '#787b86') for c in order]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')

# ─── Stacked Area ──────────────────────────────────────────────────────
dates = pivot_b.index
ax.stackplot(
    dates,
    [pivot_b[col].values for col in order],
    colors=colors,
    alpha=0.9,
    edgecolor='#1a1a1a',
    linewidth=0.3,
)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 7, 9, 11, 1, 3]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Hide first tick if it's Mar 2025 (data starts mid-Feb, first label too early)
def tick_filter(x, pos):
    dt = mdates.num2date(x)
    if dt.year == 2025 and dt.month == 3:
        return ''
    return dt.strftime('%b %Y')
ax.xaxis.set_major_formatter(plt.FuncFormatter(tick_filter))
for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(AXIS_CONFIG['x_tick']['fontsize'])
    label.set_fontweight('bold')
    label.set_color(AXIS_CONFIG['x_tick']['color'])
    label.set_rotation(45)
    label.set_ha('right')
    if suit_font:
        label.set_fontproperties(suit_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
y_max = 1.2
ax.set_ylim(0, y_max)
y_ticks = [0, 0.3, 0.6, 0.9, 1.2]
ax.set_yticks(y_ticks)
ax.set_yticklabels(
    ['$0.0B', '$0.3B', '$0.6B', '$0.9B', '$1.2B'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
    fontproperties=suit_font,
)

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='x', length=0)
ax.tick_params(axis='y', pad=5)
ax.set_xlim(dates.min(), dates.max())

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/hyperliquid/stablecoin'
png_path, svg_path = save_chart(fig, 'hyperevm_stablecoin_supply', output_dir)
plt.close()

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
