"""
RWA.xyz: Bridged Stablecoin Market Cap by Chain (Ethereum / Solana / Arbitrum / Stellar)
Stacked area chart, daily data 2023-08 ~ 2026-05.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import create_figure, save_chart, COLORS, AXIS_CONFIG

df = pd.read_csv('outputs/data/rwa_stablecoin_bridged_mcap_by_chain.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# Fill missing chain values with 0 before they appear in the data
for c in ['Ethereum', 'Solana', 'Arbitrum', 'Stellar']:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0) / 1e9  # to $B

# Order largest at bottom for natural stacking
series_order = ['Ethereum', 'Solana', 'Arbitrum', 'Stellar']
chain_colors = {
    'Ethereum': '#627eea',
    'Solana':   '#9945ff',
    'Arbitrum': '#28a0f0',
    'Stellar':  '#14b6e7',
}

fig, ax = create_figure('stacked')

ys = [df[c].values for c in series_order]
ax.stackplot(
    df['Date'].values, *ys,
    colors=[chain_colors[c] for c in series_order],
    alpha=0.92,
    edgecolor='none',
    zorder=3,
)

# X-axis: 6-month interval
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(
    ax.get_xticklabels(),
    rotation=30, ha='right', rotation_mode='anchor',
    fontsize=AXIS_CONFIG['x_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['x_tick']['color'],
)
ax.tick_params(axis='x', pad=6, length=0)

# Y-axis: 0 ~ $6B (peak ~$4.24B in Apr 2026)
ax.set_ylim(0, 6)
ax.set_yticks([0, 1.5, 3, 4.5, 6])
ax.set_yticklabels(
    ['$0B', '$1.5B', '$3B', '$4.5B', '$6B'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
)
ax.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.grid(
    True, axis='y',
    color=COLORS['grid'], alpha=0.5,
    linestyle=(0, (3.7, 1.6)), linewidth=1.0,
)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.margins(x=0)
fig.tight_layout()

output_dir = 'outputs/charts/rwa/stablecoin'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(fig, 'rwa_stablecoin_bridged_mcap_by_chain', output_dir)
print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")

# Print summary
latest = df.iloc[-1]
total = sum(latest[c] for c in series_order)
print(f"\nLatest ({latest['Date'].strftime('%Y-%m-%d')}):")
for c in series_order:
    pct = latest[c] / total * 100 if total else 0
    print(f"  {c:10s}: ${latest[c]:.3f}B ({pct:.1f}%)")
print(f"  {'Total':10s}: ${total:.3f}B")

plt.close()
