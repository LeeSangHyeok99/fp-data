import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG, area_glow, endpoint_dot

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/nvidia_datacenter_revenue.csv')

output_dir = 'outputs/charts/nvidia/revenue'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Colors
NVIDIA_GREEN = '#76B900'
TOTAL_C = '#5470c6'

# =============================================================================
# Chart: NVIDIA Data Center Revenue (Area)
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

quarters = np.arange(len(df))
dc_rev = df['DataCenter_Revenue_B'].values
total_rev = df['Total_Revenue_B'].values

# Area glow for data center revenue
n_layers = 50
for i in range(n_layers):
    frac = i / n_layers
    alpha = 0.20 * (frac ** 2.5)
    lower = dc_rev * frac
    upper = dc_rev * (frac + 1 / n_layers)
    ax.fill_between(quarters, lower, upper,
                    color=NVIDIA_GREEN, alpha=alpha, linewidth=0, zorder=2)

# Data center line
ax.plot(quarters, dc_rev, color=NVIDIA_GREEN, linewidth=2.2, zorder=4)
ax.scatter(quarters[-1], dc_rev[-1], color=NVIDIA_GREEN, s=60, zorder=5, edgecolors='none')

# Total revenue line (thinner, secondary)
ax.plot(quarters, total_rev, color=TOTAL_C, linewidth=1.5, zorder=3, alpha=0.7,
        linestyle='--')
ax.scatter(quarters[-1], total_rev[-1], color=TOTAL_C, s=40, zorder=5, edgecolors='none')

# Value labels on last points
ax.annotate(f'${dc_rev[-1]:.1f}B', (quarters[-1], dc_rev[-1]),
            textcoords="offset points", xytext=(10, -5),
            fontsize=13, fontweight='bold', color=NVIDIA_GREEN, zorder=6)
ax.annotate(f'${total_rev[-1]:.1f}B', (quarters[-1], total_rev[-1]),
            textcoords="offset points", xytext=(10, 5),
            fontsize=13, fontweight='bold', color=TOTAL_C, zorder=6)

# --- Y-axis ---
y_ticks = [0, 20, 40, 60, 80]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}B' for v in y_ticks],
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 85)
ax.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
x_labels = df['Quarter'].values
ax.set_xticks(quarters)
ax.set_xticklabels(x_labels, fontsize=11, fontweight='bold',
                    color=COLORS['text_secondary'], rotation=45, ha='right')
ax.tick_params(axis='x', length=0, pad=8)

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
fig.savefig(f'{output_dir}/nvidia_datacenter_revenue.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/nvidia_datacenter_revenue.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/nvidia_datacenter_revenue.png")
