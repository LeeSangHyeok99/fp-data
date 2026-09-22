import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/gtc2026_stock_reaction.csv')
df = df.sort_values('Change_Pct', ascending=True)

output_dir = 'outputs/charts/nvidia/gtc2026'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Chart: Horizontal Bar
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 7), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y = np.arange(len(df))
values = df['Change_Pct'].values
colors_list = df['Color'].values

# Bars with per-company colors
bars = ax.barh(y, values, height=0.6, zorder=3, edgecolor='none')
for bar, color, val in zip(bars, colors_list, values):
    if val >= 0:
        bar.set_color(color)
        bar.set_alpha(0.85)
    else:
        bar.set_color('#ef5350')
        bar.set_alpha(0.7)

# Value labels
for i, (val, company, ticker) in enumerate(zip(values, df['Company'].values, df['Ticker'].values)):
    if val >= 0:
        ax.text(val + 0.15, i, f'+{val:.1f}%', va='center', ha='left',
                fontsize=12, fontweight='bold', color=COLORS['text'])
    else:
        ax.text(val - 0.15, i, f'{val:.1f}%', va='center', ha='right',
                fontsize=12, fontweight='bold', color='#ef5350')

# Y-axis labels
labels = [f"{row['Company']} ({row['Ticker']})" for _, row in df.iterrows()]
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
ax.set_xlim(-2.5, 8.5)
x_ticks = [-2, 0, 2, 4, 6, 8]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{v}%' for v in x_ticks],
                    fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)

# Zero line
ax.axvline(x=0, color=COLORS['text_secondary'], linewidth=1.0, alpha=0.5, zorder=2)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Tier annotations on right side
tier_colors = {'Tier 1': '#76B900', 'Tier 2': '#FF9900', 'Tier 3': '#5470c6',
               'Core': '#76B900', 'Competitor': '#ef5350'}
for i, (_, row) in enumerate(df.iterrows()):
    tier = row['Tier']
    ax.text(8.3, i, tier, va='center', ha='left',
            fontsize=9, fontweight='bold', color=tier_colors.get(tier, COLORS['text_secondary']),
            alpha=0.8)

# Save
fig.savefig(f'{output_dir}/gtc2026_stock_reaction.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/gtc2026_stock_reaction.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/gtc2026_stock_reaction.png")
