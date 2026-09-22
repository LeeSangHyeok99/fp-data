import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (create_figure, apply_style, save_chart,
                    COLORS, GRID_CONFIG, AXIS_CONFIG, gradient_rounded_bar)

# =============================================================================
# LIVE DATA from trade.xyz (Mar 19, 2026)
# =============================================================================
assets = ['Oil\n(CL)', 'Silver\n(SI)', 'Brent\n(BZ)', 'XYZ100', 'Gold\n(GC)', 'S&P 500\n(ES)']

# ASXN hyperscreener live data (Mar 20, 2026)
hip3_vol = [893.50, 807.19, 593.95, 363.49, 276.95, 122.64]  # $M 24h
cme_daily = [56000,  14000,  30000,  120000, 81000,  500000]  # $M

pcts = [v / c * 100 for v, c in zip(hip3_vol, cme_daily)]

colors = ['#C9A84C', '#C9A84C', '#C9A84C', '#5470c6', '#C9A84C', '#5470c6']

# =============================================================================
# Chart
# =============================================================================
fig, ax = create_figure('bar')

x = np.arange(len(assets))
bar_w = 0.42

# Gradient rounded bars
for i in range(len(assets)):
    gradient_rounded_bar(ax, x[i], bar_w, pcts[i], color=colors[i], alpha=0.95)

# % labels
for i in range(len(assets)):
    ax.text(x[i], pcts[i] + 0.12, f'{pcts[i]:.2f}%',
            ha='center', va='bottom',
            fontsize=14, fontweight='bold',
            color=colors[i])

# HIP-3 vol / CME vol below x-axis
for i in range(len(assets)):
    h = hip3_vol[i]
    c = cme_daily[i]
    h_str = f'\${h:,.0f}M' if h < 1000 else f'\${h/1000:.1f}B'
    c_str = f'\${c//1000:.0f}B'
    ax.text(x[i], -0.32, f'{h_str} / {c_str}',
            ha='center', va='top',
            fontsize=9, fontweight='bold',
            color=COLORS['text_secondary'], alpha=0.5)

# S&P 500 callout
ax.annotate('Launched\nMar 18', xy=(x[5], pcts[5] + 0.06), xytext=(x[5] + 0.55, 1.5),
            fontsize=9, fontweight='bold', color='#5470c6', alpha=0.5,
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#5470c6', alpha=0.3, lw=1))

# --- Axis ---
ax.set_xticks(x)
ax.set_xticklabels(assets,
                    fontsize=AXIS_CONFIG['x_tick']['fontsize'],
                    fontweight='bold',
                    color=COLORS['text'])
ax.tick_params(axis='x', rotation=0, length=0,
               pad=AXIS_CONFIG['x_tick']['pad'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

y_ticks = [0, 1.5, 3.0, 4.5]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v:.1f}%' if v % 1 else f'{v:.0f}%' for v in y_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(-0.5, 5.5)
ax.tick_params(axis='y',
               length=AXIS_CONFIG['y_tick']['length'],
               pad=AXIS_CONFIG['y_tick']['pad'])

# Four-pillars style: grid, spines, background (manual to preserve x-axis rotation=0)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# Save
output_dir = 'outputs/charts/hyperliquid/sp500'
save_chart(fig, 'hl_sp500_volume_comparison', output_dir)
print('Done')
plt.close()
