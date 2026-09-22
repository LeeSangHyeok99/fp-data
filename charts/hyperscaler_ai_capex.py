import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG, gradient_rounded_bar

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/hyperscaler_ai_capex.csv')

output_dir = 'outputs/charts/nvidia/capex'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Brand colors
AMAZON_C = '#FF9900'
MSFT_C = '#00A4EF'
GOOGLE_C = '#4285F4'
META_C = '#0668E1'

companies = ['Amazon', 'Microsoft', 'Google', 'Meta']
colors = [AMAZON_C, MSFT_C, GOOGLE_C, META_C]

# =============================================================================
# Chart: Stacked Bar
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

years = df['Year'].values
x = np.arange(len(years))
bar_width = 0.55

# Stacked bars with gradient effect
bottoms = np.zeros(len(years))
for idx, (company, color) in enumerate(zip(companies, colors)):
    values = df[company].values
    for i, (xi, val, bot) in enumerate(zip(x, values, bottoms)):
        gradient_rounded_bar(ax, x_center=xi, width=bar_width,
                             height=bot + val, color=color, alpha=0.9)
        # We need stacking, so draw regular bars instead
    # Clear and use regular stacked approach
    pass

# Actually let's use clean stacked bars with semi-transparent fills
plt.close(fig)

fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bottoms = np.zeros(len(years))
bars_collection = []
for idx, (company, color) in enumerate(zip(companies, colors)):
    values = df[company].values
    bars = ax.bar(x, values, bar_width, bottom=bottoms, color=color,
                  alpha=0.85, zorder=3, edgecolor='none')
    bars_collection.append(bars)
    bottoms += values

# Total labels on top
totals = df['Total'].values
for i, (xi, total) in enumerate(zip(x, totals)):
    ax.text(xi, total + 12, f'${total:.0f}B',
            ha='center', va='bottom', fontsize=13, fontweight='bold',
            color=COLORS['text'])

# YoY growth annotation
for i in range(1, len(totals)):
    growth = (totals[i] - totals[i-1]) / totals[i-1] * 100
    if growth > 5:
        ax.annotate(f'+{growth:.0f}%',
                    xy=(x[i], totals[i] + 5),
                    ha='center', va='bottom', fontsize=10, fontweight='bold',
                    color='#26a69a', zorder=6)

# --- Y-axis ---
y_ticks = [0, 200, 400, 600]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}B' for v in y_ticks],
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 750)
ax.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in years],
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=10)

# --- Grid ---
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# --- Spines ---
for spine in ax.spines.values():
    spine.set_visible(False)

# --- Save ---
fig.savefig(f'{output_dir}/hyperscaler_ai_capex_stacked.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/hyperscaler_ai_capex_stacked.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/hyperscaler_ai_capex_stacked.png")
