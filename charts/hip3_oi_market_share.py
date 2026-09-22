import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, save_chart, COLORS, GRID_CONFIG, SERIES_COLORS, AXIS_CONFIG

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
data = {
    'deployer': ['XYZ', 'HyENA', 'dreamcash', 'Markets', 'Ventuals', 'Felix'],
    'oi_usd': [397787504, 32605783, 26918820, 6700491, 2848199, 2647782],
}
df = pd.DataFrame(data)
total = df['oi_usd'].sum()
df['pct'] = df['oi_usd'] / total * 100

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Colors per deployer
colors = SERIES_COLORS[:len(df)]

bars = ax.bar(df['deployer'], df['pct'], width=0.55, color=colors, zorder=3)

# ══════════════════════════════════════════════════
# Labels on bars
# ══════════════════════════════════════════════════
for bar, pct, oi in zip(bars, df['pct'], df['oi_usd']):
    h = bar.get_height()
    if pct >= 5:
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
                f'{pct:.1f}%',
                ha='center', va='bottom',
                fontsize=16, fontweight='bold',
                color=COLORS['text'])
    else:
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
                f'{pct:.1f}%',
                ha='center', va='bottom',
                fontsize=14, fontweight='bold',
                color=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# Y-axis
# ══════════════════════════════════════════════════
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y',
               labelsize=AXIS_CONFIG['y_tick']['fontsize'],
               pad=AXIS_CONFIG['y_tick']['pad'],
               length=0,
               colors=AXIS_CONFIG['y_tick']['color'])
ax.tick_params(axis='x',
               labelsize=AXIS_CONFIG['x_tick']['fontsize'],
               pad=AXIS_CONFIG['x_tick']['pad'],
               length=0,
               colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'hip3_oi_market_share',
                                'outputs/charts/hyperliquid')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
