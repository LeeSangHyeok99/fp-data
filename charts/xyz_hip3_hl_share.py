import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, '.claude/skills/design/hrc')
from config import setup_font, COLORS, GRID_CONFIG, AXIS_CONFIG, DPI, DEFAULT_FIGSIZE

setup_font()

output_dir = 'outputs/charts/hyperliquid/volume'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/xyz_hip3_hl_share.csv')

# Parse percentages
df['xyz_pct'] = df['XYZ Share of HL'].str.rstrip('%').astype(float)
df['hip3_pct'] = df['HIP-3 Share of HL'].str.rstrip('%').astype(float)

# Parse start date from Period (e.g. "3/11/25" = Nov 3, 2025)
df['start_date'] = pd.to_datetime(df['Period'].str.split(' - ').str[0], format='%d/%m/%y')

# =============================================================================
# Chart: Area chart, XYZ + Others (HIP-3 - XYZ)
# =============================================================================
fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE, dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Stacked area: XYZ (bottom) + Others on top
others_pct = df['hip3_pct'] - df['xyz_pct']

ax.fill_between(df['start_date'], 0, df['xyz_pct'],
                color='#6b9b8a', alpha=0.85, zorder=3, label='XYZ')
ax.fill_between(df['start_date'], df['xyz_pct'], df['hip3_pct'],
                color='#3d6b5e', alpha=0.85, zorder=3, label='Other HIP-3')

# Top line
ax.plot(df['start_date'], df['hip3_pct'], color='#9cc5b5', linewidth=1.5, zorder=4)
ax.plot(df['start_date'], df['xyz_pct'], color='#8bb8a5', linewidth=1, zorder=4, alpha=0.6)

# Endpoint labels
last_date = df['start_date'].iloc[-1] + pd.Timedelta(days=3)
ax.text(last_date, df['hip3_pct'].iloc[-1], f'{df["hip3_pct"].iloc[-1]:.0f}%',
        color='#9cc5b5', fontsize=14, fontweight='bold', va='center')
ax.text(last_date, df['xyz_pct'].iloc[-1] - 1.5, f'{df["xyz_pct"].iloc[-1]:.0f}%',
        color='#6b9b8a', fontsize=14, fontweight='bold', va='center')

# Y axis
y_ticks = [0, 10, 20, 30, 40]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}%' for v in y_ticks],
                    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                    fontweight='bold',
                    color=AXIS_CONFIG['y_tick']['color'])
ax.set_ylim(0, 42)

# X axis - week labels
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'],
               pad=AXIS_CONFIG['x_tick']['pad'],
               colors=AXIS_CONFIG['x_tick']['color'])

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Spines
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', length=0, pad=15)

ax.margins(x=0.02)
fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/xyz_hip3_hl_share.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print(f'XYZ Share: {df["xyz_pct"].iloc[0]:.1f}% → {df["xyz_pct"].iloc[-1]:.1f}%')
print(f'HIP-3 Share: {df["hip3_pct"].iloc[0]:.1f}% → {df["hip3_pct"].iloc[-1]:.1f}%')
print(f'Other HIP-3: {others_pct.iloc[-1]:.1f}%')
print(f'\nDone: xyz_hip3_hl_share (png + svg)')
