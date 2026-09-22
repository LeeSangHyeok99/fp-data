import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG, apply_style, save_chart

output_dir = 'outputs/charts/hyperliquid/stablecoin'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# HyperEVM Stablecoin Supply (Stacked Area) - HRC Theme
# =============================================================================
setup_font()

df = pd.read_csv('outputs/data/hyperliquid_stablecoin_supply.csv')
df['date'] = pd.to_datetime(df['date'])

# Convert to millions
for col in ['total', 'USDC', 'USDT0', 'USDH', 'USDe', 'feUSD', 'thBILL', 'other']:
    df[col] = df[col].astype(float) / 1e6

# Filter out near-zero days
df = df[df['total'] > 0.01].reset_index(drop=True)

# Brand colors
stablecoin_colors = {
    'USDC': '#2775ca',
    'USDT0': '#26a17b',
    'USDH': '#50e3c2',
    'USDe': '#1a1a2e',
    'feUSD': '#9a60b4',
    'thBILL': '#fac858',
    'other': '#787b86',
}

stack_order = ['USDC', 'USDT0', 'USDH', 'USDe', 'feUSD', 'thBILL', 'other']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y_stack = np.zeros(len(df))
for col in stack_order:
    ax.fill_between(df['date'], y_stack, y_stack + df[col].values,
                    color=stablecoin_colors[col], alpha=0.85, linewidth=0, zorder=2)
    ax.plot(df['date'], y_stack + df[col].values,
            color=stablecoin_colors[col], linewidth=0.3, alpha=0.5, zorder=3)
    y_stack += df[col].values

# Y-axis: clean ticks in $M, max ~$1.5B = 1500M
y_max = 1500
y_ticks = [0, 500, 1000, 1500]
ax.set_yticks(y_ticks)
ax.set_yticklabels(['$0.0B', '$0.5B', '$1.0B', '$1.5B'],
                   fontsize=18, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=15)
ax.set_ylim(0, y_max)

# X-axis
x_ticks = pd.date_range('2025-04-01', '2026-04-01', freq='3MS')
x_ticks = [t for t in x_ticks if t <= df['date'].max()]
ax.set_xticks(x_ticks)
ax.set_xticklabels([t.strftime('%b %Y') for t in x_ticks],
                   fontsize=16, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=6, width=1, pad=10, rotation=45, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.set_xlim(df['date'].min(), df['date'].max())

# Grid (HRC style)
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir}/hyperevm_stablecoin_supply.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/hyperevm_stablecoin_supply.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print("Chart saved: HyperEVM Stablecoin Supply (HRC)")
print(f"  Latest total: ${df['total'].iloc[-1]:,.0f}M")
print(f"  Date: {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
print(f"  Output: {output_dir}/hyperevm_stablecoin_supply.png")
