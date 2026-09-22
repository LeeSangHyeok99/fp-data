"""
Japan "sub-unit-only shareholders" — number (bars, left) vs composition ratio
(line, right). 2017–2023 dual-axis combo chart.
Style: four-pillars, transparent BG, no title/legend/source. Value labels kept.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG

setup_font()

GREY = '#6f7480'   # bars (persons)
BLUE = '#2C6CDF'   # line (composition ratio %)

# ----------------------------------------------------------------------
# Data (labels above bars / points in source image)
# ----------------------------------------------------------------------
data = [
    (2017,  4992525,  8.7),
    (2018,  4977938,  8.1),
    (2019,  5617258,  8.8),
    (2020,  7230923, 10.5),
    (2021,  8831587, 11.8),
    (2022, 10506638, 12.8),
    (2023, 11754451, 13.4),
]
df = pd.DataFrame(data, columns=['year', 'shareholders', 'composition_ratio_pct'])
df.to_csv('outputs/data/jp_sub_unit_shareholders.csv', index=False)

x = np.arange(len(df))
persons = df['shareholders'].values
ratio = df['composition_ratio_pct'].values

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 7.0), dpi=150)
ax2 = ax.twinx()

# Bars (left axis)
ax.bar(x, persons, width=0.6, color=GREY, zorder=3)

# Line + markers (right axis)
ax2.plot(x, ratio, color=BLUE, linewidth=3.0, zorder=4)
ax2.scatter(x, ratio, color=BLUE, s=130, zorder=5, edgecolors='none')

# ----------------------------------------------------------------------
# Value labels
# ----------------------------------------------------------------------
for xi, p in zip(x, persons):
    ax.text(xi, p + 300000, f'{p:,}', ha='center', va='bottom',
            fontsize=12.5, fontweight='bold', color='#b0b4bb', zorder=6)
for xi, r in zip(x, ratio):
    ax2.text(xi, r + 0.55, f'{r:.1f}', ha='center', va='bottom',
             fontsize=15, fontweight='bold', color=BLUE, zorder=6)

# ----------------------------------------------------------------------
# Axes (5 aligned ticks each)
# ----------------------------------------------------------------------
ax.set_ylim(0, 20_000_000)
left_ticks = [0, 5_000_000, 10_000_000, 15_000_000, 20_000_000]
ax.set_yticks(left_ticks)
ax.set_yticklabels([('0' if v == 0 else f'{v // 1_000_000}M') for v in left_ticks],
                   fontsize=18, fontweight='bold', color=AXIS_CONFIG['y_tick']['color'])

ax2.set_ylim(0, 16)
right_ticks = [0, 4, 8, 12, 16]
ax2.set_yticks(right_ticks)
ax2.set_yticklabels([f'{v}%' for v in right_ticks],
                    fontsize=18, fontweight='bold', color=BLUE)

ax.set_xticks(x)
ax.set_xticklabels(df['year'], fontsize=16, fontweight='bold',
                   color=AXIS_CONFIG['x_tick']['color'])
ax.set_xlim(-0.7, len(df) - 0.3)

# ----------------------------------------------------------------------
# four-pillars styling
# ----------------------------------------------------------------------
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2.set_facecolor('none')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax2.grid(False)
for spine in list(ax.spines.values()) + list(ax2.spines.values()):
    spine.set_visible(False)
ax.tick_params(axis='both', length=0, pad=12)
ax2.tick_params(axis='y', length=0, pad=12)

fig.tight_layout()
png, svg = save_chart(fig, 'jp_sub_unit_shareholders',
                      'outputs/charts/macro/shareholders')
plt.close(fig)
print('saved:', png)
print('years:', len(df), '| persons max', f'{persons.max():,}', '| ratio max', ratio.max())
