"""
Gap Between Stock and Crypto Investor Base in Korea
Two-line chart (Stock vs Crypto) with filled gap area + gap callouts.
Follows four-pillars style: no title/legend/source/Y-label inside the chart,
max 5 Y-ticks.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import (
    create_figure, apply_style, save_chart,
    SERIES_COLORS, AXIS_CONFIG, COLORS
)

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
df = pd.read_csv('outputs/data/korea_stock_crypto_investor_gap.csv')
df['stock_interp'] = df['stock_investors'].interpolate(method='linear')

periods = df['period'].tolist()
x = np.arange(len(periods))
crypto = df['crypto_investors'].values
stock = df['stock_interp'].values

# ----------------------------------------------------------------------
# Colors
# ----------------------------------------------------------------------
# Line / area tones (from four-pillars SERIES_COLORS)
STOCK_COLOR = SERIES_COLORS[0]   # 블루 #5470c6
CRYPTO_COLOR = SERIES_COLORS[6]  # 오렌지 #fc8452
GAP_FILL = SERIES_COLORS[7]      # 퍼플 #9a60b4 (area fill)

# Pill tones (deeper / more saturated for high-contrast labels)
STOCK_PILL = '#3B5FD6'
CRYPTO_PILL = '#E55A1F'
GAP_PILL = '#4A3D9F'        # darker purple inner
GAP_PILL_EDGE = '#7C6FE5'   # lighter purple outer ring

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = create_figure('line')

# Gap area
ax.fill_between(x, crypto, stock,
                color=GAP_FILL, alpha=0.30,
                linewidth=0, zorder=2)

# Lines (hollow markers with white center + colored ring)
ax.plot(x, stock, color=STOCK_COLOR, linewidth=2.5, zorder=4,
        marker='o', markersize=7,
        markerfacecolor='#ffffff', markeredgecolor=STOCK_COLOR,
        markeredgewidth=2.0)
ax.plot(x, crypto, color=CRYPTO_COLOR, linewidth=2.5, zorder=4,
        marker='o', markersize=7,
        markerfacecolor='#ffffff', markeredgecolor=CRYPTO_COLOR,
        markeredgewidth=2.0)

# ----------------------------------------------------------------------
# Axes (max 5 Y-ticks, clean values)
# ----------------------------------------------------------------------
ax.set_xlim(-0.4, len(periods) - 0.6)
ax.set_ylim(0, 16)

ax.set_xticks(x)
ax.set_xticklabels(periods)

yticks = [0, 4, 8, 12, 16]
ax.set_yticks(yticks)
ax.set_yticklabels([f'{v}M' for v in yticks])

# ----------------------------------------------------------------------
# Pill helper
# ----------------------------------------------------------------------
def pill(x_data, y_data, text, color, ha='left', va='center',
         dx=0.0, dy=0.0, text_color='#ffffff', alpha=1.0,
         edge_color='none', edge_width=0):
    ax.annotate(
        text,
        xy=(x_data, y_data),
        xytext=(x_data + dx, y_data + dy),
        textcoords='data',
        ha=ha, va=va,
        fontsize=11, fontweight='bold', color=text_color,
        zorder=10,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=color,
                  edgecolor=edge_color, linewidth=edge_width,
                  alpha=alpha),
    )


# ----------------------------------------------------------------------
# Endpoint pills at '25 H2 (Stock above, Gap middle, Crypto below)
# ----------------------------------------------------------------------
last = len(periods) - 1
pill(last, stock[last],  '14.56M', STOCK_PILL,  dx=0.18, ha='left', va='center')
pill(last, crypto[last], '11.13M', CRYPTO_PILL, dx=0.18, ha='left', va='center')

# ----------------------------------------------------------------------
# Gap callouts at '21 H2, '23 H2, '25 H2
# Pill is centered ON the dashed line (the line passes through the pill).
# '25 H2 sits high (near stock endpoint) so it doesn't collide with the
# 11.13M endpoint pill below it.
# ----------------------------------------------------------------------
gap_points = [
    (0, 8.26, None),       # '21 H2: midpoint
    (4, 7.71, None),       # '23 H2: midpoint
    (8, 3.43, 13.10),      # '25 H2: forced y so it stacks just below 14.56M
]

for idx, gap_val, y_force in gap_points:
    y_low = crypto[idx]
    y_high = stock[idx]

    ax.plot([idx, idx], [y_low, y_high],
            color=GAP_PILL_EDGE, linewidth=1.0,
            linestyle=(0, (3, 3)), alpha=0.9, zorder=3)

    y_pill = y_force if y_force is not None else (y_low + y_high) / 2
    pill(idx, y_pill, f'{gap_val:.2f}M', GAP_PILL,
         dx=0.0, ha='center', va='center',
         edge_color=GAP_PILL_EDGE, edge_width=1.4)

# Position the '25 H2 gap pill near the top so the three pills stack
# tightly at the right edge (Stock pill / Gap pill / Crypto pill)
# Override the last entry by re-drawing at a higher y near stock[last]
# (already handled above with side='left' and y_mid)

# ----------------------------------------------------------------------
# Apply four-pillars style (grid, spines, ticks)
# ----------------------------------------------------------------------
apply_style(fig, ax, 'line')

# Brighter tick label color (between text_secondary and text)
TICK_COLOR = '#b0b4bb'

# Force x-tick rotation flat (periods are short enough to read horizontally)
ax.tick_params(axis='x', rotation=0, pad=8, length=0,
               labelsize=AXIS_CONFIG['x_tick']['fontsize'],
               colors=TICK_COLOR)
ax.tick_params(axis='y', length=0,
               labelsize=AXIS_CONFIG['y_tick']['fontsize'],
               colors=TICK_COLOR)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

# ----------------------------------------------------------------------
# Save (transparent PNG + SVG via four-pillars helper)
# ----------------------------------------------------------------------
output_dir = 'outputs/charts/korea/investors'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(
    fig, 'korea_stock_crypto_investor_gap', output_dir
)
print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
plt.close(fig)
