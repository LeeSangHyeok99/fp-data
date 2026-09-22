import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/revenue'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/hyperliquid_perp_fee_share.csv')
df['week_start'] = pd.to_datetime(df['week_start'])
df['hl_m'] = df['hl_fees'] / 1e6
df['others_m'] = df['others_fees'] / 1e6
df['total_m'] = df['total_fees'] / 1e6

# =============================================================================
# Chart: Stacked Area (HL vs Others) + Share % line — HRC theme
# =============================================================================
setup_font()

HL_GREEN = '#50e3c2'
OTHERS_GREY = '#747474'

fig, ax1 = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')

dates = df['week_start']

# Stacked area
ax1.fill_between(dates, 0, df['hl_m'],
                  color=HL_GREEN, alpha=0.65, zorder=3)
ax1.fill_between(dates, df['hl_m'], df['total_m'],
                  color=OTHERS_GREY, alpha=0.25, zorder=2)

# Y axis left
y_max = 175
y_ticks_left = [0, 50, 100, 150]
ax1.set_yticks(y_ticks_left)
ax1.set_yticklabels([f'${int(v)}M' for v in y_ticks_left],
                     fontsize=15, fontweight='bold',
                     color=COLORS['text_secondary'])
ax1.set_ylim(0, y_max)
ax1.tick_params(axis='y', length=0, pad=10)

# Share % line on secondary axis
ax2 = ax1.twinx()
ax2.plot(dates, df['share'], color='#ffffff', linewidth=2.0,
         alpha=0.9, zorder=5)
ax2.scatter(dates.iloc[-1], df['share'].iloc[-1],
            color='#ffffff', s=40, zorder=6, edgecolors='none')

# Annotate latest share
latest_share = df['share'].iloc[-1]
ax2.annotate(f'{latest_share:.0f}%',
             xy=(dates.iloc[-1], latest_share),
             xytext=(8, 0), textcoords='offset points',
             fontsize=14, fontweight='bold', color='#ffffff',
             va='center')

# Y axis right — 4 ticks matching left
y_ticks_right = [0, 25, 50, 75]
ax2.set_yticks(y_ticks_right)
ax2.set_yticklabels([f'{int(v)}%' for v in y_ticks_right],
                     fontsize=15, fontweight='bold',
                     color=COLORS['text_secondary'])
ax2.set_ylim(0, 110)
ax2.tick_params(axis='y', length=0, pad=10)

# 50% reference line
ax2.axhline(y=50, color=COLORS['text_secondary'], alpha=0.3,
            linestyle='--', linewidth=1, zorder=1)

# Grid
ax1.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax1.set_axisbelow(True)

# X axis
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax1.xaxis.get_majorticklabels(),
         fontsize=14, fontweight='bold',
         color=COLORS['text_secondary'],
         rotation=45, ha='right')
ax1.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

# Spines
for spine in ax1.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hyperliquid_perp_fee_share.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()
print('Done: hyperliquid_perp_fee_share.png / .svg (HRC + HL green + share line)')
print(f'Latest: HL ${df["hl_m"].iloc[-1]:.1f}M / Total ${df["total_m"].iloc[-1]:.1f}M = {latest_share:.1f}%')
