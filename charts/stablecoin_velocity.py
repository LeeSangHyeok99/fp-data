"""
Stablecoin Velocity: Annual Volume vs Market Cap
Shows usage growing faster than supply = increasing real-world adoption
Source: rwa.xyz / DefiLlama
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import (create_figure, apply_style, save_chart, COLORS,
                    gradient_rounded_bar, endpoint_dot)

# ── Data ──
df = pd.read_csv('outputs/data/stablecoin_annual_volume.csv')
# year, volume_t (trillions), market_cap_b (billions)

years = df['year'].values
volume = df['volume_t'].values
mcap = df['market_cap_b'].values
velocity = volume * 1000 / mcap  # volume in B / mcap in B

# ── Chart ──
fig, ax1 = create_figure('bar')

# Bar width
x = np.arange(len(years))
width = 0.35

# Volume bars (left axis)
for i, (yr, vol) in enumerate(zip(x, volume)):
    gradient_rounded_bar(ax1, yr - width/2, width, vol, '#5470c6')

# Market cap bars
for i, (yr, mc) in enumerate(zip(x, mcap)):
    gradient_rounded_bar(ax1, yr + width/2, width, mc / 10, '#91cc75')  # scale to fit

# Actually, dual axis with line is better for velocity insight
plt.close()

# ── Redesign: Bars for volume, line for velocity ──
fig, ax1 = create_figure('bar')

bar_color = '#5470c6'
line_color = '#fac858'

# Volume bars
for i, vol in enumerate(volume):
    gradient_rounded_bar(ax1, i, 0.5, vol, bar_color)

# Volume labels on bars
for i, vol in enumerate(volume):
    ax1.text(i, vol + 0.5, f'{vol:.0f}T' if vol >= 1 else f'{vol*1000:.0f}B',
             ha='center', va='bottom', fontsize=14, fontweight='bold',
             color=COLORS['text'])

# Y axis left (Volume)
vol_max = 40
vol_ticks = [0, 10, 20, 30, 40]
ax1.set_yticks(vol_ticks)
ax1.set_yticklabels([f'{int(v)}T' for v in vol_ticks])
ax1.set_ylim(0, vol_max)

# X axis
ax1.set_xticks(x)
ax1.set_xticklabels([str(y) for y in years])

# Velocity line on secondary axis
ax2 = ax1.twinx()
ax2.plot(x, velocity, color=line_color, linewidth=3, zorder=5, marker='o',
         markersize=8, markerfacecolor=line_color, markeredgecolor='none')

# Velocity labels
for i, vel in enumerate(velocity):
    ax2.text(i, vel + 3, f'{vel:.0f}x', ha='center', va='bottom',
             fontsize=13, fontweight='bold', color=line_color)

# Y axis right (Velocity)
vel_max = int(np.ceil(max(velocity) / 20) * 20 + 20)
n_ticks = len(vol_ticks)
vel_ticks = np.linspace(0, vel_max, n_ticks)
vel_ticks = [int(round(v / 10) * 10) for v in vel_ticks]
ax2.set_yticks(vel_ticks)
ax2.set_yticklabels([f'{int(v)}x' for v in vel_ticks])
ax2.set_ylim(0, vel_max)

# Style
apply_style(fig, ax1, 'bar')

# ax2 styling
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=line_color)
ax2.grid(False)

fig.tight_layout()

# Output
output_dir = 'outputs/charts/stablecoin/volume'
save_chart(fig, 'stablecoin_velocity', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_velocity.png')

# Stats
print('\nVelocity Data:')
for y, v, m, vel in zip(years, volume, mcap, velocity):
    print(f'  {y}: Vol ${v}T, MCap ${m}B, Velocity {vel:.0f}x')
