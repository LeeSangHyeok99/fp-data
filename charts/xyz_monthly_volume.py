import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, '.claude/skills/design/hrc')
from config import setup_font, COLORS, SERIES_COLORS, GRID_CONFIG, AXIS_CONFIG, DPI, DEFAULT_FIGSIZE

setup_font()

output_dir = 'outputs/charts/hyperliquid/volume'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
months = ['Nov\n2025', 'Dec\n2025', 'Jan\n2026', 'Feb\n2026', 'Mar\n2026']

xyz_vol = np.array([4.30, 7.49, 21.62, 32.68, 58.57])  # $B
hip3_vol = np.array([4.43, 8.12, 24.86, 40.23, 68.55])  # $B
others_vol = hip3_vol - xyz_vol  # other DEXs on HIP-3

mom_pct = [None, 74.1, 188.6, 51.1, 79.2]  # XYZ MoM %

# =============================================================================
# Chart: Stacked bar (XYZ + Others) with MoM% annotation
# =============================================================================
fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE, dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(months))
bar_width = 0.55

# Stacked bars
bars_xyz = ax.bar(x, xyz_vol, bar_width, color='#6b9b8a', zorder=3, label='XYZ')
bars_others = ax.bar(x, others_vol, bar_width, bottom=xyz_vol, color='#3d6b5e', zorder=3, label='Others')

# MoM% annotations on top of bars
for i, mom in enumerate(mom_pct):
    total = hip3_vol[i]
    if mom is not None:
        ax.text(x[i], total + 1.5, f'+{mom:.0f}%',
                ha='center', va='bottom',
                fontsize=13, fontweight='bold',
                color='#10b981')

# Value labels inside XYZ bars
for i, val in enumerate(xyz_vol):
    ax.text(x[i], val / 2, f'${val:.1f}B',
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            color='#ffffff')

# Y axis
y_ticks = [10, 30, 50, 70]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${int(v)}B' for v in y_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold',
                    color=AXIS_CONFIG['y_tick']['color'])
ax.set_ylim(0, 78)

# X axis
ax.set_xticks(x)
ax.set_xticklabels(months,
                    fontsize=14, fontweight='bold',
                    color=AXIS_CONFIG['x_tick']['color'])
ax.tick_params(axis='x', rotation=0, pad=8)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', length=0, pad=15)
ax.tick_params(axis='x', length=0)

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/xyz_monthly_volume.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print(f'XYZ Volume Growth: ${xyz_vol[0]:.1f}B → ${xyz_vol[-1]:.1f}B ({xyz_vol[-1]/xyz_vol[0]:.0f}x in 5 months)')
print(f'HIP-3 Total: ${hip3_vol[-1]:.1f}B (Mar)')
print(f'XYZ Share: {xyz_vol[-1]/hip3_vol[-1]*100:.1f}%')
print(f'\nDone: xyz_monthly_volume (png + svg)')
print(f'Output: {output_dir}/')
