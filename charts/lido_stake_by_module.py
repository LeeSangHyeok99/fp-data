import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, SERIES_COLORS, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
df = pd.read_csv('outputs/data/Stake_by_module.csv')
df['day'] = pd.to_datetime(df['day'])
df = df.sort_values('day')
df = df[df['total_lido_stake'] > 0]

# Fill NaN with 0 for stacking
df['csm_stake'] = df['csm_stake'].fillna(0)
df['sdvt_stake'] = df['sdvt_stake'].fillna(0)
df['curated_stake'] = df['curated_stake'].fillna(0)

# Convert to millions
curated = df['curated_stake'].values / 1e6
sdvt = df['sdvt_stake'].values / 1e6
csm = df['csm_stake'].values / 1e6
x = df['day'].values

# Stack order (bottom to top): Curated, SDVT, CSM
series = [curated, sdvt, csm]
labels = ['Curated', 'SDVT', 'CSM']
# Lido brand-inspired palette
colors = ['#00A3FF', '#F69988', '#FFC170']  # Lido Blue, Coral, Amber

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Stacked area
# ══════════════════════════════════════════════════
ax.stackplot(x, *series, colors=colors, alpha=0.75, edgecolor='none', linewidth=0)

# Draw lines on top of each stacked boundary
bottom = np.zeros(len(curated))
for i, s in enumerate(series):
    bottom = bottom + s
    ax.plot(x, bottom, color=colors[i], linewidth=1.2)

# ══════════════════════════════════════════════════
# Y-axis (max 5 ticks, M ETH unit)
# ══════════════════════════════════════════════════
ax.set_ylim(0, 10)
ax.set_yticks([0, 2.5, 5, 7.5, 10])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.1f}M'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=14, pad=15, length=0,
               colors=COLORS['text_secondary'])

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'lido_stake_by_module',
                                'outputs/charts/lido')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
