import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data: Fee-to-Payment ratio for a $0.001 micropayment
# ══════════════════════════════════════════════════
methods = [
    'Circle\nNanopayments',
    'Solana',
    'Base',
    'Arbitrum',
    'Ethereum L1',
    'Credit Card',
]

# Estimated fees for a single $0.001 payment (March 2026)
fees = [
    0.000001,   # Nanopayments: batched, effective per-tx cost ~$0.000001
    0.00025,    # Solana: ~5000 lamports, SOL ~$130
    0.005,      # Base: ~$0.002-0.02 avg
    0.008,      # Arbitrum: ~$0.003-0.01 avg
    0.50,       # Ethereum L1: ~$0.10-0.50 moderate congestion avg
    0.30,       # Credit Card: $0.30 fixed fee (Stripe/Visa)
]

payment = 0.001
ratios = [f / payment for f in fees]  # [0.005x, 2x, 5x, 30x, 800x, 300x]

# Colors: Nanopayments highlighted (Circle brand blue), others gradient
bar_colors = [
    '#0052ff',   # Circle/USDC blue (highlight)
    '#14f195',   # Solana green
    '#0052ff',   # Base blue (Coinbase blue)
    '#28a0f0',   # Arbitrum blue
    '#627eea',   # Ethereum purple
    '#787b86',   # Credit card (muted gray)
]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Horizontal bar chart (log scale)
# ══════════════════════════════════════════════════
y_pos = np.arange(len(methods))
bars = ax.barh(y_pos, ratios, height=0.55, color=bar_colors, alpha=0.9,
               edgecolor='#1a1a1a', linewidth=0.5)

ax.set_xscale('log')
ax.set_yticks(y_pos)
ax.set_yticklabels(methods, fontsize=12, fontweight='bold',
                   color=COLORS['text'])

# X-axis formatting
ax.set_xlim(0.0005, 1500)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{x:g}x' if x >= 1 else f'{x:.3f}x'))

ax.tick_params(axis='x', labelsize=12, colors=COLORS['text_secondary'],
               pad=10, length=0)

# ── Break-even line at 1x (fee = payment) ──
ax.axvline(x=1, color='#ee6666', linewidth=1.5, linestyle='--',
           alpha=0.8, zorder=1)
ax.text(1.15, len(methods) - 0.3, '1x (fee = payment)',
        color='#ee6666', fontsize=10, fontweight='bold',
        va='center', alpha=0.9)

# ── Value labels on bars ──
for i, (ratio, fee) in enumerate(zip(ratios, fees)):
    if ratio > 1:
        label = f'{ratio:,.0f}x'
        ax.text(ratio * 0.6, i, label, ha='right', va='center',
                color='white', fontsize=11, fontweight='bold')
    else:
        label = f'{ratio:.3f}x'
        ax.text(ratio * 1.5, i, label, ha='left', va='center',
                color=COLORS['text'], fontsize=11, fontweight='bold')

# ── Grid (y-axis only → x for horizontal) ──
ax.grid(True, axis='x', color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# ── Spines ──
for spine in ax.spines.values():
    spine.set_visible(False)

# Invert y-axis so highest cost is at top
ax.invert_yaxis()

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'nanopayments_fee_ratio',
                                'outputs/charts/nanopayments')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
