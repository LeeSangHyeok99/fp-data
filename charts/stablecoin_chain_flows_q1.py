"""
Q1 2026 Stablecoin Net Flows by Chain
Shows where stablecoin capital is moving between networks
With Ethereum internal composition breakdown (USDT out, USDC/yield in)
Source: CEX.IO Q1 Report, Finbold, DefiLlama
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS, POSITIVE_COLOR, NEGATIVE_COLOR

# ── Data ──
chains = ['Tron', 'Ethereum', 'Solana', 'Base', 'BSC', 'Hyperliquid']
net_flows = [6.1, 3.0, 1.6, 0.3, 0.2, 2.1]
supply = [86.6, 168.4, 15.0, 4.7, 13.7, 5.3]

# Ethereum internal breakdown
eth_usdt = -7.0
eth_usdc_yield = 10.0  # +$2B USDC + yield + others = net +$3B

# Chain colors
chain_colors = {
    'Tron': '#ff0013',
    'Ethereum': '#627eea',
    'Solana': '#9945ff',
    'Base': '#0052ff',
    'BSC': '#f0b90b',
    'Hyperliquid': '#50e3c2',
}

# ── Chart ──
fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(12, 5.5)

y_pos = np.arange(len(chains))[::-1]
colors = [chain_colors[c] for c in chains]

bars = ax.barh(y_pos, net_flows, height=0.55, color=colors, alpha=0.9, edgecolor='none')

# Value labels with supply context
for i, (bar, flow, sup) in enumerate(zip(bars, net_flows, supply)):
    sign = '+' if flow > 0 else ''
    # Flow label
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
            f'{sign}{flow:.1f}B',
            va='center', fontsize=15, fontweight='bold', color=COLORS['text'])
    # Supply context (smaller, secondary)
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2 - 0.22,
            f'(Total: {sup:.0f}B)',
            va='center', fontsize=11, color=COLORS['text_secondary'])

# Ethereum internal breakdown annotation
eth_idx = chains.index('Ethereum')
eth_y = y_pos[eth_idx]

# Compact annotation next to ETH bar
ax.text(3.5, eth_y + 0.32,
        'USDT 7B out / USDC+Yield 10B in → Net +3B',
        fontsize=10, fontweight='bold', color=COLORS['text_secondary'],
        va='center', style='italic')

# Y axis
ax.set_yticks(y_pos)
ax.set_yticklabels(chains, fontsize=16, fontweight='bold', color=COLORS['text'])

# X axis
x_ticks = [0, 2, 4, 6]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{v}B' for v in x_ticks])
ax.set_xlim(0, 9)

# Grid
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

output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_chain_flows_q1', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_chain_flows_q1.png')
