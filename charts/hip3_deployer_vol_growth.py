import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/hrc')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data (HL_Metrics_25_HRC.xlsx, HIP-3 Volume sheet)
# ══════════════════════════════════════════════════
df = pd.read_csv('/tmp/hip3_vol_sheet.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# Deployer columns (excl. XYZ), stacking order: Felix → VNTL → HyENA → Markets → Cash
deployers = ['FLX', 'VNTL', 'HyENA', 'Markets', 'Cash']

# Resample to weekly (Monday start), SUM for volume
weekly = df[deployers].resample('W-MON').sum()
weekly = weekly / 1e9  # Convert to $B
weekly = weekly.iloc[:-1]  # Drop last partial week

# ══════════════════════════════════════════════════
# Colors (muted blue-green palette, matching OI chart)
# ══════════════════════════════════════════════════
deployer_colors = {
    'FLX':     '#1B2A4A',  # darkest navy
    'VNTL':    '#7B9DB8',  # light steel blue
    'HyENA':   '#3B5998',  # medium navy
    'Markets': '#8FA88F',  # sage green
    'Cash':    '#B8C8B0',  # light sage
}

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Stacked bars
# ══════════════════════════════════════════════════
x = weekly.index
bar_width = 5

bottom = np.zeros(len(weekly))
for deployer in deployers:
    values = weekly[deployer].values
    ax.bar(x, values, width=bar_width, bottom=bottom,
           color=deployer_colors[deployer], edgecolor='none')
    bottom += values

# ══════════════════════════════════════════════════
# Y-axis (max 5 ticks, $M unit)
# ══════════════════════════════════════════════════
ax.set_ylim(0, 2.4)
ax.set_yticks([0, 0.6, 1.2, 1.8, 2.4])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'${x:.1f}B'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-m/%-d/%Y'))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=18, pad=15, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=12, pad=10, length=0,
               colors=COLORS['text_secondary'])

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'hip3_deployer_vol_growth',
                                'outputs/charts/hyperliquid')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
