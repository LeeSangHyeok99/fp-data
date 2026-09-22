"""
Stablecoin Supply by Chain - Horizontal Bar Chart
Current snapshot from DefiLlama stablecoinchains API
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS

# ── Data (from DefiLlama API, April 2026) ──
chains_data = {
    'Ethereum': 164.78,
    'Tron': 85.74,
    'Solana': 14.99,
    'BSC': 13.67,
    'Hyperliquid': 5.30,
    'Base': 4.71,
    'Arbitrum': 3.69,
    'Polygon': 3.62,
    'BUIDL (Multi)': 2.96,
    'Aptos': 1.67,
}

# Others = total - sum of top
total_supply = 316.1  # from weekly data
others = total_supply - sum(chains_data.values())
chains_data['Others'] = round(others, 2)

chains = list(chains_data.keys())[::-1]
values = [chains_data[c] for c in chains]

# Chain brand colors
chain_colors = {
    'Ethereum': '#627eea',
    'Tron': '#ff0013',
    'Solana': '#9945ff',
    'BSC': '#f0b90b',
    'Hyperliquid': '#50e3c2',
    'Base': '#0052ff',
    'Arbitrum': '#28a0f0',
    'Polygon': '#8247e5',
    'BUIDL (Multi)': '#000000',
    'Aptos': '#2dd8a3',
    'Others': '#787b86',
}
colors = [chain_colors[c] for c in chains]

# ── Chart ──
fig, ax = create_figure('horizontal_bar')

bars = ax.barh(range(len(chains)), values, color=colors, height=0.6, alpha=0.9, edgecolor='none')

# Value labels
for i, (bar, val) in enumerate(zip(bars, values)):
    label = f'{val:.1f}B' if val >= 1 else f'{val*1000:.0f}M'
    share = val / total_supply * 100
    ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
            f'{label} ({share:.1f}%)',
            va='center', fontsize=14, fontweight='bold', color=COLORS['text'])

ax.set_yticks(range(len(chains)))
ax.set_yticklabels(chains, fontsize=16, fontweight='bold', color=COLORS['text'])

# X axis
x_ticks = [0, 50, 100, 150]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{int(v)}B' for v in x_ticks])
ax.set_xlim(0, 200)

# Grid on x axis
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.grid(False, axis='y')
ax.set_axisbelow(True)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', labelsize=16, pad=10, colors=COLORS['text_secondary'], length=0)
ax.tick_params(axis='y', length=0)
fig.tight_layout()

# Output
output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_chain_distribution', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_chain_distribution.png')

# Stats for .md
print(f'\nChain Distribution (Total: ${total_supply}B):')
for c in list(chains_data.keys()):
    share = chains_data[c] / total_supply * 100
    print(f'  {c}: ${chains_data[c]:.1f}B ({share:.1f}%)')
