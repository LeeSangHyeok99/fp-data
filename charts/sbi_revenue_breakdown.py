"""
SBI Holdings Revenue Breakdown by Business Segment
Donut chart — four-pillars theme
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import create_figure, save_chart, COLORS, AXIS_CONFIG

# Data
df = pd.read_csv('outputs/data/sbi_revenue_breakdown.csv')

# Sort by share descending
df = df.sort_values('share_pct', ascending=False).reset_index(drop=True)

# Color map per segment
color_map = {
    'Financial Services Business': '#2b5797',
    'Asset Management Business': '#5b9bd5',
    'PE Investment Business': '#6bab90',
    'Crypto-asset Business': '#8b7bb5',
    'Next Gen Business': '#d4943a',
}
segment_colors = [color_map[s] for s in df['segment']]

# Create figure
fig, ax = plt.subplots(figsize=(10.67, 6), dpi=150)

shares = df['share_pct'].values
labels = df['segment'].values

# Donut chart
wedges, _ = ax.pie(
    shares,
    colors=segment_colors,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.38, edgecolor='#141414', linewidth=1.5),
    pctdistance=0.82,
)

# Percentage labels outside with leader lines
for i, (wedge, share) in enumerate(zip(wedges, shares)):
    ang = (wedge.theta2 + wedge.theta1) / 2
    rad = np.deg2rad(ang)

    # Position for label
    x_label = 1.25 * np.cos(rad)
    y_label = 1.25 * np.sin(rad)

    fontsize = 13 if share >= 10 else 11
    ax.text(x_label, y_label, f'{share}%',
            ha='center', va='center',
            fontsize=fontsize, fontweight='bold',
            color=COLORS['text'])

# Center text
ax.text(0, -0.02, '¥1,443.7B', ha='center', va='center',
        fontsize=22, fontweight='bold', color=COLORS['text'])

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.set_aspect('equal')

# 16:9 canvas with donut centered, not filling height
ax.set_xlim(-2.0, 2.0)
ax.set_ylim(-1.125, 1.125)

# Save
import os
output_dir = 'outputs/charts/sbi/revenue'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(fig, 'sbi_revenue_breakdown', output_dir)
print(f"Saved: {png_path}")
plt.close()
