import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, save_chart, COLORS, SERIES_COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data (HL_Metrics_25_HRC.xlsx, HIP-3 OI sheet)
# ══════════════════════════════════════════════════
df = pd.read_csv('/tmp/hip3_oi_sheet.csv')
last_row = df.iloc[-1]

deployers = ['XYZ', 'Cash', 'HyENA', 'FLX', 'Markets', 'VNTL']
oi_values = [last_row['XYZ'], last_row['Cash'], last_row['HyENA'],
             last_row['FLX'], last_row['Markets'], last_row['VNTL']]

total_oi = sum(oi_values)
pct_values = [v / total_oi * 100 for v in oi_values]

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 5.2), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Colors
bar_colors = [SERIES_COLORS[i % len(SERIES_COLORS)] for i in range(len(deployers))]

bars = ax.bar(deployers, pct_values, width=0.55, color=bar_colors, edgecolor='none')

# Value labels on top
for bar, pct in zip(bars, pct_values):
    if pct > 5:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{pct:.1f}%', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color=COLORS['text'])
    else:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{pct:.1f}%', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=COLORS['text_secondary'])

# ══════════════════════════════════════════════════
# Y-axis
# ══════════════════════════════════════════════════
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}%'))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=16, pad=15, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=16, pad=10, length=0,
               colors=COLORS['text_secondary'])

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'hip3_deployer_oi_share',
                                'outputs/charts/hyperliquid')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
print(f"\nData as of: {last_row['Date']}")
print(f"Total OI: ${total_oi/1e6:.1f}M")
for d, v, p in zip(deployers, oi_values, pct_values):
    print(f"  {d}: ${v/1e6:.1f}M ({p:.1f}%)")
