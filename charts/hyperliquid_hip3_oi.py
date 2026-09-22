import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG, gradient_rounded_bar

output_dir = 'outputs/charts/hyperliquid/hip3'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
categories = ['Commodities', 'Indices', 'Equities', 'Other']
oi_m = [618, 258, 242, 312]  # in millions
total = sum(oi_m)

colors = {
    'Commodities': '#C9A84C',   # Gold
    'Indices': '#5470c6',       # Blue
    'Equities': '#9a60b4',      # Purple
    'Other': '#787b86',         # Grey
}

# =============================================================================
# Chart: Horizontal Bar
# =============================================================================
setup_font()

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y_pos = np.arange(len(categories))
bar_height = 0.55

# Sort by value (largest on top)
sorted_data = sorted(zip(categories, oi_m), key=lambda x: x[1])
cats_sorted = [d[0] for d in sorted_data]
vals_sorted = [d[1] for d in sorted_data]
colors_sorted = [colors[c] for c in cats_sorted]

for i, (cat, val, color) in enumerate(zip(cats_sorted, vals_sorted, colors_sorted)):
    bar = ax.barh(i, val, height=bar_height, color=color, alpha=0.9, zorder=3)

    # Value label at end of bar
    pct = val / total * 100
    label = f'${val}M ({pct:.0f}%)'
    ax.text(val + 8, i, label,
            va='center', ha='left',
            fontsize=16, fontweight='bold',
            color=COLORS['text'])

# Category labels on y-axis
ax.set_yticks(y_pos)
ax.set_yticklabels(cats_sorted, fontsize=18, fontweight='bold',
                    color=COLORS['text'])
ax.tick_params(axis='y', length=0, pad=15)

# X axis
x_max = 700
ax.set_xlim(0, x_max)
x_ticks = [0, 200, 400, 600]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${int(v)}M' for v in x_ticks],
                    fontsize=16, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Total annotation
ax.text(x_max * 0.95, len(categories) - 0.3,
        f'Total: ${total/1000:.2f}B',
        va='top', ha='right',
        fontsize=20, fontweight='bold',
        color=COLORS['text'])

fig.tight_layout()

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hyperliquid_hip3_oi_breakdown.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()
print('Done: hyperliquid_hip3_oi_breakdown.png / .svg')
print(f'Non-crypto share: {(618+258+242)/total*100:.0f}%')
