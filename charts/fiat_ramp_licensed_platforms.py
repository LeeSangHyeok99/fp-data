"""
Fiat-ramp licensed crypto platforms by APAC jurisdiction — bar chart
Source: provided data table. Japan highlighted (brand green).
Style: four-pillars, transparent BG, no title/legend/source.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG, COLORS

setup_font()

GREEN = '#26a69a'   # 강조 (Japan)
GREY = '#5a5d63'    # 나머지

# ----------------------------------------------------------------------
# Data (표 기준, 내림차순)
# ----------------------------------------------------------------------
data = [
    ('Japan', 27), ('Hong Kong', 13), ('Singapore', 11),
    ('Thailand', 9), ('Malaysia', 6), ('South Korea', 5),
]
df = pd.DataFrame(data, columns=['jurisdiction', 'licensed_platforms'])
df.to_csv('outputs/data/fiat_ramp_licensed_platforms.csv', index=False)

x = np.arange(len(df))
colors = [GREEN if j == 'Japan' else GREY for j in df['jurisdiction']]

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
ax.bar(x, df['licensed_platforms'], width=0.62, color=colors, zorder=3)

ax.set_ylim(0, 30)
ax.yaxis.set_major_locator(MultipleLocator(10))   # 0,10,20,30
ax.set_xticks(x)
ax.set_xticklabels(df['jurisdiction'])
ax.set_xlim(-0.7, len(df) - 0.3)

# four-pillars styling
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'],
               pad=AXIS_CONFIG['y_tick']['pad'], length=0,
               colors=AXIS_CONFIG['y_tick']['color'])
ax.tick_params(axis='x', labelsize=15, pad=8, rotation=0,
               colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center', va='top')
fig.tight_layout()

png, svg = save_chart(fig, 'fiat_ramp_licensed_platforms',
                      'outputs/charts/platform/regulation')
plt.close(fig)
print('saved:', png)
print('jurisdictions:', len(df), '| max', df['licensed_platforms'].max())
