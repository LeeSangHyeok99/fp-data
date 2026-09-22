"""
HIP-3 Monthly Volume 2025 (Bar Chart)
Design: Four Pillars
Source: ASXN API (Oct, Nov) + GLC (Dec)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
import sys

# ── Design config ──────────────────────────────────────────────
sys.path.append('.claude/skills/design/hrc')
from config import COLORS, GRID_CONFIG, AXIS_CONFIG, DPI, SERIES_COLORS

font_path = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'SUIT'
else:
    plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.weight'] = 'bold'

# ── Data ───────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/hip3_2025_monthly.csv')

months = df['month'].tolist()
volumes = df['volume'].tolist()

# ── Figure ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ── Bar ────────────────────────────────────────────────────────
x = np.arange(len(months))
bars = ax.bar(
    x,
    volumes,
    width=0.5,
    color=SERIES_COLORS[0],
    zorder=2,
)

# ── Y-axis ($B, max 5 ticks) ──────────────────────────────────
max_vol = max(volumes)
y_max = np.ceil(max_vol / 5e9) * 5e9
if y_max < max_vol * 1.1:
    y_max += 5e9
ax.set_ylim(0, y_max)

tick_step = y_max / 5
y_ticks = np.arange(0, y_max + tick_step * 0.5, tick_step)
ax.set_yticks(y_ticks)
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda v, _: f'${v / 1e9:.0f}B')
)

ax.tick_params(
    axis='y',
    labelsize=AXIS_CONFIG['y_tick']['fontsize'],
    pad=AXIS_CONFIG['y_tick']['pad'],
    length=0,
    colors=AXIS_CONFIG['y_tick']['color'],
)

# ── X-axis ─────────────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(months)

ax.tick_params(
    axis='x',
    labelsize=AXIS_CONFIG['x_tick']['fontsize'],
    pad=AXIS_CONFIG['x_tick']['pad'],
    length=0,
    colors=AXIS_CONFIG['x_tick']['color'],
)

# ── Grid ───────────────────────────────────────────────────────
ax.grid(
    True, axis='y',
    color=GRID_CONFIG['color'],
    alpha=GRID_CONFIG['alpha'],
    linestyle=tuple(GRID_CONFIG['linestyle']),
    linewidth=GRID_CONFIG['linewidth'],
)
ax.set_axisbelow(True)

# ── Spines ─────────────────────────────────────────────────────
for spine in ax.spines.values():
    spine.set_visible(False)

# ── Save ───────────────────────────────────────────────────────
fig.tight_layout()

output_dir = Path('outputs/charts/hip3')
output_dir.mkdir(parents=True, exist_ok=True)

filename = 'hip3_2025_monthly_volume'
fig.savefig(output_dir / f'{filename}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(output_dir / f'{filename}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)

print(f'Saved: {output_dir / filename}.png')
print(f'Saved: {output_dir / filename}.svg')
for m, v in zip(months, volumes):
    print(f'  {m}: ${v:,.0f}')
plt.close(fig)
