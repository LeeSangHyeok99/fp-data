import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data: How many $0.001 payments per $1 of fees?
# ══════════════════════════════════════════════════
methods = [
    'Credit Card',
    'Ethereum L1',
    'Arbitrum',
    'Base',
    'Solana',
    'Circle\nNanopayments',
]

fees_per_tx = [0.30, 0.50, 0.008, 0.005, 0.00025, 0.000001]
payments_per_dollar = [1 / f for f in fees_per_tx]
# [3.3, 2, 125, 200, 4000, 1000000]

bar_colors = [
    '#787b86',   # Credit card gray
    '#627eea',   # Ethereum purple
    '#28a0f0',   # Arbitrum blue
    '#0052ff',   # Base blue
    '#14f195',   # Solana green
    '#0052ff',   # Circle blue (highlight)
]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.5), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Horizontal bar (log scale)
# ══════════════════════════════════════════════════
y_pos = np.arange(len(methods))
bars = ax.barh(y_pos, payments_per_dollar, height=0.55,
               color=bar_colors, alpha=0.9,
               edgecolor='#1a1a1a', linewidth=0.5)

ax.set_xscale('log')
ax.set_yticks(y_pos)
ax.set_yticklabels(methods, fontsize=12, fontweight='bold',
                   color=COLORS['text'])

ax.set_xlim(1, 3_000_000)

# X-axis: clean log labels
ax.xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x):,}' if x >= 1 else f'{x:.1f}'))
ax.tick_params(axis='x', labelsize=11, colors=COLORS['text_secondary'],
               pad=10, length=0)

# ── Value labels ──
for i, val in enumerate(payments_per_dollar):
    if val >= 1000:
        label = f'{val:,.0f}'
    else:
        label = f'{val:.0f}'

    if val > 100:
        ax.text(val * 0.5, i, label, ha='right', va='center',
                color='white', fontsize=11, fontweight='bold')
    else:
        ax.text(val * 1.8, i, label, ha='left', va='center',
                color=COLORS['text'], fontsize=11, fontweight='bold')

# ── Grid ──
ax.grid(True, axis='x', color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'nanopayments_per_dollar',
                                'outputs/charts/nanopayments')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
