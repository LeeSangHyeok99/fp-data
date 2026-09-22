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
df = pd.read_csv('outputs/data/nvidia_capex_cascade.csv')

output_dir = 'outputs/charts/nvidia/cascade'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Colors
NVIDIA_C = '#76B900'
CAPEX_C = '#FF9900'
HBM_C = '#ee6666'
TSMC_C = '#5470c6'

# =============================================================================
# Chart: Cascade Multi-line (Dual Y-axis)
# =============================================================================
setup_font()
fig, ax1 = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')

years = df['Year'].values
x = np.arange(len(years))

# Left Y-axis: NVIDIA DC Revenue + HBM + TSMC Pkg
nvidia_rev = df['NVIDIA_DC_Revenue_B'].values
hbm = df['HBM_Market_B'].values
tsmc_pkg = df['TSMC_Advanced_Pkg_Rev_B'].values

# NVIDIA DC Revenue - area glow
n_layers = 40
for i in range(n_layers):
    frac = i / n_layers
    alpha = 0.15 * (frac ** 2.5)
    lower = nvidia_rev * frac
    upper = nvidia_rev * (frac + 1 / n_layers)
    ax1.fill_between(x, lower, upper,
                     color=NVIDIA_C, alpha=alpha, linewidth=0, zorder=2)

ax1.plot(x, nvidia_rev, color=NVIDIA_C, linewidth=2.2, zorder=4)
ax1.scatter(x[-1], nvidia_rev[-1], color=NVIDIA_C, s=60, zorder=5, edgecolors='none')

# HBM Market
ax1.plot(x, hbm, color=HBM_C, linewidth=1.8, zorder=4, alpha=0.9)
ax1.scatter(x[-1], hbm[-1], color=HBM_C, s=45, zorder=5, edgecolors='none')

# TSMC Advanced Packaging
ax1.plot(x, tsmc_pkg, color=TSMC_C, linewidth=1.8, zorder=4, alpha=0.9)
ax1.scatter(x[-1], tsmc_pkg[-1], color=TSMC_C, s=45, zorder=5, edgecolors='none')

# Value labels
ax1.annotate(f'${nvidia_rev[-1]:.0f}B', (x[-1], nvidia_rev[-1]),
             textcoords="offset points", xytext=(8, 8),
             fontsize=12, fontweight='bold', color=NVIDIA_C, zorder=6)
ax1.annotate(f'${hbm[-1]:.0f}B', (x[-1], hbm[-1]),
             textcoords="offset points", xytext=(8, -3),
             fontsize=11, fontweight='bold', color=HBM_C, zorder=6)
ax1.annotate(f'${tsmc_pkg[-1]:.0f}B', (x[-1], tsmc_pkg[-1]),
             textcoords="offset points", xytext=(8, 5),
             fontsize=11, fontweight='bold', color=TSMC_C, zorder=6)

# Right Y-axis: Hyperscaler Capex
ax2 = ax1.twinx()
capex = df['Hyperscaler_Capex_B'].values

ax2.fill_between(x, 0, capex, color=CAPEX_C, alpha=0.08, linewidth=0, zorder=1)
ax2.plot(x, capex, color=CAPEX_C, linewidth=2.0, zorder=3, linestyle='--')
ax2.scatter(x[-1], capex[-1], color=CAPEX_C, s=50, zorder=5, edgecolors='none')
ax2.annotate(f'${capex[-1]:.0f}B', (x[-1], capex[-1]),
             textcoords="offset points", xytext=(8, -12),
             fontsize=12, fontweight='bold', color=CAPEX_C, zorder=6)

# --- Left Y-axis ---
n_ticks = 5
y1_ticks = [0, 50, 100, 150, 200]
ax1.set_yticks(y1_ticks)
ax1.set_yticklabels([f'${v}B' for v in y1_ticks],
                     fontsize=14, fontweight='bold',
                     color=COLORS['text_secondary'])
ax1.set_ylim(0, 220)
ax1.tick_params(axis='y', length=0, pad=15)

# --- Right Y-axis (aligned ticks) ---
y2_ticks = np.linspace(0, 700, n_ticks)
ax2.set_yticks(y2_ticks)
ax2.set_yticklabels([f'${int(v)}B' for v in y2_ticks],
                     fontsize=14, fontweight='bold',
                     color=CAPEX_C)
ax2.set_ylim(0, 770)
ax2.tick_params(axis='y', length=0, pad=15)

# --- X-axis ---
ax1.set_xticks(x)
ax1.set_xticklabels([str(y) for y in years],
                     fontsize=14, fontweight='bold',
                     color=COLORS['text_secondary'])
ax1.tick_params(axis='x', length=0, pad=10)

# --- Grid (left axis only) ---
ax1.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax1.set_axisbelow(True)

# --- Spines ---
for spine in ax1.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

# --- Cascade arrows annotation ---
# Arrow from NVIDIA to supply chain
for i in range(1, len(years)):
    if nvidia_rev[i] > nvidia_rev[i-1] * 1.3:  # 30%+ growth triggers
        # Subtle upward arrow
        ax1.annotate('', xy=(x[i], nvidia_rev[i] * 0.85),
                     xytext=(x[i], nvidia_rev[i] * 0.65),
                     arrowprops=dict(arrowstyle='->', color=NVIDIA_C, alpha=0.3, lw=1.5))

# --- Save ---
fig.savefig(f'{output_dir}/nvidia_capex_cascade.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/nvidia_capex_cascade.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/nvidia_capex_cascade.png")
