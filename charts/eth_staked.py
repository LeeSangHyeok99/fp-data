"""
ETH Staked by Category - Stacked Area Chart
Four Pillars design theme
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
df = pd.read_csv('outputs/data/eth_staked.csv')
df['time'] = pd.to_datetime(df['time'])

# Pivot
pivot = df.pivot_table(index='time', columns='depositor_entity_category',
                       values='cum_deposited_eth', aggfunc='sum').fillna(0)
pivot = pivot.sort_index()

# Order by latest total (largest at bottom)
latest = pivot.iloc[-1].sort_values(ascending=False)
order = latest.index.tolist()
pivot = pivot[order]

# Convert to millions
pivot_m = pivot / 1e6

# ─── Colors ─────────────────────────────────────────────────────────────
color_map = {
    'Liquid Staking': '#5470c6',
    'CEXs': '#91cc75',
    'Unidentified': '#787b86',
    'Staking Pools': '#fac858',
    'Liquid Restaking': '#73c0de',
    'Solo Stakers': '#ee6666',
}
colors = [color_map.get(c, '#787b86') for c in order]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')

# ─── Stacked Area ──────────────────────────────────────────────────────
dates = pivot_m.index
ax.stackplot(
    dates,
    [pivot_m[col].values for col in order],
    colors=colors,
    alpha=0.9,
    edgecolor='#1a1a1a',
    linewidth=0.3,
)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(AXIS_CONFIG['x_tick']['fontsize'])
    label.set_fontweight('bold')
    label.set_color(AXIS_CONFIG['x_tick']['color'])
    label.set_rotation(0)
    label.set_ha('center')
    if suit_font:
        label.set_fontproperties(suit_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
y_max = pivot_m.sum(axis=1).max()
ax.set_ylim(0, 40)
y_ticks = [0, 10, 20, 30, 40]
ax.set_yticks(y_ticks)
ax.set_yticklabels(
    [f'{int(v)}M' for v in y_ticks],
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
output_dir = 'outputs/charts/stakers/general'
png_path, svg_path = save_chart(fig, 'eth_staked_by_category', output_dir)
plt.close()

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
