"""
Japan crypto users (millions), 2022–2025 actuals & projection — bar chart
Source: JVCEA (202604 public report PDF, 2026-05)
Style: four-pillars, transparent BG, no title/legend/source.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG

setup_font()

BLUE = '#2f8fd8'

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
df = pd.DataFrame({
    'year': ['2022', '2023', '2024', '2025'],
    'users_millions': [5.61, 6.46, 9.17, 12.4],
})
df.to_csv('outputs/data/japan_crypto_users.csv', index=False)

x = np.arange(len(df))

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
ax.bar(x, df['users_millions'], width=0.6, color=BLUE, zorder=3)

# value labels on top
for xi, v in zip(x, df['users_millions']):
    ax.annotate(f'{v:.2f}M', xy=(xi, v), xytext=(0, 8),
                textcoords='offset points', ha='center', va='bottom',
                fontsize=15, fontweight='bold', color=BLUE)

ax.set_ylim(0, 15)
ax.yaxis.set_major_locator(MultipleLocator(5))   # 0,5,10,15
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}M'))
ax.set_xticks(x)
ax.set_xticklabels(df['year'])
ax.set_xlim(-0.6, len(df) - 0.4)

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
ax.tick_params(axis='x', labelsize=16, pad=8, rotation=0,
               colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')
fig.tight_layout()

png, svg = save_chart(fig, 'japan_crypto_users', 'outputs/charts/macro/users')
plt.close(fig)
print('saved:', png)
print(df.to_string(index=False))
