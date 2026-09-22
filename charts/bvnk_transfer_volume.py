"""
BVNK Finance - Total Transfer Volume (Monthly Cumulative)
Four Pillars design theme
Data source: Dune Analytics (query 6846270)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from config import (create_figure, apply_style, save_chart,
                    SERIES_COLORS, COLORS, AXIS_CONFIG)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/bvnk_transfer_volume.csv')
df['month'] = pd.to_datetime(df['month'])
df['label'] = df['month'].dt.strftime('%b %Y')
df['cumulative_b'] = df['cumulative_volume_usd'] / 1e9

# Exclude Mar 2026 (incomplete month, only $15M)
df = df[df['month'] < '2026-03-01'].reset_index(drop=True)

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('bar')

# ─── Flat Gradient Bars ─────────────────────────────────────────────────
bar_color = '#5470c6'
n = len(df)
bar_width = 0.6

for i, row in df.iterrows():
    h = row['cumulative_b']
    if h <= 0:
        continue
    x_left = i - bar_width / 2
    x_right = i + bar_width / 2
    r, g, b = mcolors.to_rgb(bar_color)
    gradient = np.zeros((256, 1, 4))
    for j in range(256):
        frac = j / 255
        factor = 0.15 + 0.85 * (frac ** 0.5)
        gradient[j, 0] = [r * factor, g * factor, b * factor, 0.95]
    ax.imshow(gradient, aspect='auto', origin='lower',
              extent=[x_left, x_right, 0, h],
              zorder=3, interpolation='bilinear')

# ─── X axis ─────────────────────────────────────────────────────────────
ax.set_xlim(-0.5, n - 0.5)
ax.set_xticks(range(n))
ax.set_xticklabels(
    df['label'],
    fontsize=AXIS_CONFIG['x_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['x_tick']['color'],
    rotation=45,
    ha='right',
)

# Show every 3rd label
for i, label in enumerate(ax.xaxis.get_ticklabels()):
    if i % 3 != 0:
        label.set_visible(False)

# ─── Y axis ─────────────────────────────────────────────────────────────
y_max = 20
ax.set_ylim(0, y_max)
y_ticks = [0, 5, 10, 15, 20]
ax.set_yticks(y_ticks)
ax.set_yticklabels(
    [f'${int(v)}B' for v in y_ticks],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
)

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'bar')
ax.tick_params(axis='x', length=0)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/bvnk/volume'
png_path, svg_path = save_chart(fig, 'bvnk_total_transfer_volume', output_dir)
plt.close()

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
