"""
Japan Cashless Payment Trend (2010-2024)
Stacked bar (Credit card, Debit card, Electronic money, Code payment) + Line (Cashless ratio)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from config import create_figure, apply_style, save_chart, COLORS, SERIES_COLORS, AXIS_CONFIG

# Load data
df = pd.read_csv('outputs/data/japan_cashless_payments.csv')

# Colors for each payment type
colors = {
    'credit_card': SERIES_COLORS[0],      # 블루
    'debit_card': SERIES_COLORS[3],        # 레드
    'electronic_money': SERIES_COLORS[1],  # 그린
    'code_payment': SERIES_COLORS[7],      # 퍼플
}

line_color = SERIES_COLORS[2]  # 옐로우 for cashless ratio

# Create figure
fig, ax = create_figure('stacked_bar')

years = df['year'].values
x = np.arange(len(years))
bar_width = 0.55

# Stacked bar
bottom = np.zeros(len(years))
series_order = ['credit_card', 'debit_card', 'electronic_money', 'code_payment']

for series in series_order:
    vals = df[series].values
    ax.bar(x, vals, bar_width, bottom=bottom, color=colors[series],
           edgecolor='#1a1a1a', linewidth=0.5, alpha=0.9, zorder=3)
    bottom += vals

# Right Y-axis for cashless ratio
ax2 = ax.twinx()
ratios = df['cashless_ratio'].values

ax2.plot(x, ratios, color=line_color, linewidth=2.5, zorder=5,
         marker='o', markersize=5, markerfacecolor=line_color, markeredgecolor='none')

# Data labels on line
for i, (xi, ratio) in enumerate(zip(x, ratios)):
    fontsize = 9
    fw = 'bold'
    color = line_color

    # Last point highlighted
    if i == len(x) - 1:
        fontsize = 12
        color = '#ef5350'  # red highlight for 42.8%

    ax2.annotate(f'{ratio:.1f}%',
                 xy=(xi, ratio),
                 xytext=(0, 12),
                 textcoords='offset points',
                 ha='center', va='bottom',
                 fontsize=fontsize, fontweight=fw, color=color,
                 zorder=6)

# X-axis
ax.set_xticks(x)
ax.set_xticklabels(years.astype(str), rotation=0,
                   fontsize=AXIS_CONFIG['x_tick']['fontsize'],
                   fontweight='bold',
                   color=AXIS_CONFIG['x_tick']['color'])
ax.tick_params(axis='x', rotation=0, pad=8, length=0)

# Left Y-axis (trillion yen) - max 5 ticks
ax.set_ylim(0, 160)
ax.set_yticks([0, 40, 80, 120, 160])
ax.set_yticklabels(['¥0T', '¥40T', '¥80T', '¥120T', '¥160T'],
                   fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                   fontweight='bold',
                   color=AXIS_CONFIG['y_tick']['color'])
ax.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Right Y-axis (%) - match tick count with left (5 ticks)
ax2.set_ylim(0, 50)
ax2.set_yticks([0, 12.5, 25, 37.5, 50])
ax2.set_yticklabels(['0%', '12.5%', '25%', '37.5%', '50%'],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold',
                    color=AXIS_CONFIG['y_tick']['color'])
ax2.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2.set_facecolor('none')

# Grid (left axis only)
ax.grid(True, axis='y', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# Hide spines
for spine in ax.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# Save
import os
output_dir = 'outputs/charts/japan/cashless'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(fig, 'japan_cashless_payments', output_dir)
print(f"Saved: {png_path}")
plt.close()
