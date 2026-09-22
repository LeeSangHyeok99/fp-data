"""
Q1 2026 Stablecoin Supply Shift - Waterfall Bar Chart
USDT -$3B, USDC +$2B, Yield-bearing +$4.3B
First time USDT/USDC moved in opposite directions since Q2 2022
Source: CEX.IO Q1 2026 Stablecoin Report
"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS, POSITIVE_COLOR, NEGATIVE_COLOR, gradient_rounded_bar

# ── Data ──
categories = ['USDT', 'USDC', 'sUSDS', 'USDY', 'Other\nYield', 'Others', 'Net']
values =     [-3.0,    2.0,    2.5,    1.2,    0.6,     3.8,    8.0]
# sUSDS +2.5B, USDY +1.2B, other yield ~0.6B = total yield +4.3B

colors = []
for v in values:
    if v > 0:
        colors.append(POSITIVE_COLOR)
    else:
        colors.append(NEGATIVE_COLOR)
colors[-1] = '#5470c6'  # Net total in blue

# ── Chart ──
fig, ax = create_figure('bar')

x = np.arange(len(categories))

for i, (xi, val) in enumerate(zip(x, values)):
    color = colors[i]
    h = abs(val)
    if val >= 0:
        gradient_rounded_bar(ax, xi, 0.55, h, color)
    else:
        # Negative bar: draw downward
        # Use simple bar for negative values
        ax.bar(xi, val, width=0.55, color=color, alpha=0.9, edgecolor='none')

# Value labels
for i, (xi, val) in enumerate(zip(x, values)):
    sign = '+' if val > 0 else ''
    y_pos = val + 0.3 if val >= 0 else val - 0.5
    ax.text(xi, y_pos, f'{sign}{val:.1f}B',
            ha='center', va='bottom' if val >= 0 else 'top',
            fontsize=15, fontweight='bold', color=COLORS['text'])

# Category labels for yield-bearing group
# Add bracket annotation for yield-bearing group
ax.annotate('', xy=(1.8, -1.5), xytext=(4.2, -1.5),
            arrowprops=dict(arrowstyle='-', color=COLORS['text_secondary'], lw=1.5))
ax.text(3.0, -2.0, 'Yield-bearing +4.3B',
        ha='center', va='top', fontsize=12, fontweight='bold',
        color=POSITIVE_COLOR)

# Axes
ax.set_xticks(x)
ax.set_xticklabels(categories)
y_ticks = [-5, 0, 5, 10]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}B' if v != 0 else '0B' for v in y_ticks])
ax.set_ylim(-5, 11)

# Zero line
ax.axhline(y=0, color=COLORS['text_secondary'], linewidth=1, alpha=0.8)

apply_style(fig, ax, 'bar')

output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_q1_supply_shift', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_q1_supply_shift.png')
