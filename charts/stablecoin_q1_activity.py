"""
Q1 2026 Stablecoin Activity Shift - Grouped Bar
Bot activity 76%, retail -16%, USDC overtook USDT in organic volume
Source: CEX.IO Q1 2026 Report, rwa.xyz
"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS, POSITIVE_COLOR, NEGATIVE_COLOR, gradient_rounded_bar

# ── Data: Key Q1 shifts ──
metrics = [
    'Bot Volume\nShare',
    'Retail\nTransfers',
    'USDC Organic\nVol Share',
    'USDT Organic\nVol Share',
    'Monthly Active\nAddresses',
    'Trading Vol\nShare',
]
q4_vals = [65, 100, 38, 55, 48.6, 68]
q1_vals = [76, 84,  51, 42, 54.2, 75]
changes = [+11, -16, +13, -13, +5.6, +7]
units =   ['%', 'idx', '%', '%', 'M', '%']

# ── Chart ──
fig, ax = create_figure('bar')
fig.set_size_inches(12, 5)

x = np.arange(len(metrics))
width = 0.3

# Q4 2025 bars
for i, val in enumerate(q4_vals):
    gradient_rounded_bar(ax, x[i] - width/2, width, val, '#787b86')

# Q1 2026 bars
for i, val in enumerate(q1_vals):
    color = POSITIVE_COLOR if changes[i] > 0 else NEGATIVE_COLOR
    # Special: bot volume up is negative signal, retail down is negative
    if i == 0:  # bot volume up = concerning
        color = NEGATIVE_COLOR
    elif i == 1:  # retail down = concerning
        color = NEGATIVE_COLOR
    elif i == 2:  # USDC organic up = positive
        color = POSITIVE_COLOR
    elif i == 3:  # USDT organic down = neutral
        color = '#787b86'
    elif i == 4:  # MAA up = positive
        color = POSITIVE_COLOR
    elif i == 5:  # trading vol share up = positive
        color = POSITIVE_COLOR
    gradient_rounded_bar(ax, x[i] + width/2, width, val, color)

# Change labels
for i, (xi, chg) in enumerate(zip(x, changes)):
    val = max(q4_vals[i], q1_vals[i])
    sign = '+' if chg > 0 else ''
    unit = 'pp' if units[i] == '%' else ('%' if units[i] == 'idx' else '')
    label = f'{sign}{chg:.0f}{unit}' if i != 4 else f'{sign}{chg:.1f}M'
    color = POSITIVE_COLOR if chg > 0 else NEGATIVE_COLOR
    # Override colors for contextual meaning
    if i == 0:  # bot up = bad
        color = NEGATIVE_COLOR
    elif i == 1:  # retail down = bad
        color = NEGATIVE_COLOR
    ax.text(xi + width/2, val + 2, label,
            ha='center', va='bottom', fontsize=12, fontweight='bold', color=color)

# Axes
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=13)

y_ticks = [0, 25, 50, 75, 100]
ax.set_yticks(y_ticks)
ax.set_yticklabels([str(v) for v in y_ticks])
ax.set_ylim(0, 110)

apply_style(fig, ax, 'bar')

output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_q1_activity', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_q1_activity.png')
