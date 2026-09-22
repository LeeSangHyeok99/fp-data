"""
DeFi Median APY Trend
Bar (daily median APY) + Line (7-day average) overlay
Design: Four Pillars
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
from pathlib import Path
import sys

# ── Design config ──────────────────────────────────────────────
sys.path.append('.claude/skills/design/four-pillars')
from config import COLORS, GRID_CONFIG, AXIS_CONFIG, DPI

font_path = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'SUIT'
else:
    plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.weight'] = 'bold'

# ── Colors (reference-matched) ─────────────────────────────────
BAR_COLOR   = '#5cc5b4'   # teal green (median APY bars)
LINE_COLOR  = '#f08c5a'   # warm orange (7d average line)

# ── Data ───────────────────────────────────────────────────────
DATA_PATH = 'data/defi_median_apy.csv'
df = pd.read_csv(DATA_PATH, parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)
df = df[df['date'] >= '2024-01-01'].reset_index(drop=True)

# ── Figure ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ── Bar: Median APY ───────────────────────────────────────────
ax.bar(
    df['date'],
    df['median_apy'],
    width=0.8,
    color=BAR_COLOR,
    alpha=0.6,
    linewidth=0,
    zorder=2,
)

# ── Line: 7-day Average ──────────────────────────────────────
mask = df['7d_avg'].notna()
ax.plot(
    df.loc[mask, 'date'],
    df.loc[mask, '7d_avg'],
    color=LINE_COLOR,
    linewidth=1.8,
    zorder=3,
)

# ── Y-axis ────────────────────────────────────────────────────
ax.set_ylim(0, 10)
ax.yaxis.set_major_locator(mticker.MultipleLocator(2))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))

ax.tick_params(
    axis='y',
    labelsize=AXIS_CONFIG['y_tick']['fontsize'],
    pad=AXIS_CONFIG['y_tick']['pad'],
    length=0,
    colors=AXIS_CONFIG['y_tick']['color'],
)

# ── X-axis ────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

ax.tick_params(
    axis='x',
    labelsize=AXIS_CONFIG['x_tick']['fontsize'],
    pad=AXIS_CONFIG['x_tick']['pad'],
    length=0,
    colors=AXIS_CONFIG['x_tick']['color'],
    rotation=AXIS_CONFIG['x_tick']['rotation'],
)
for label in ax.xaxis.get_majorticklabels():
    label.set_ha('right')

# ── Grid ──────────────────────────────────────────────────────
ax.grid(
    True, axis='y',
    color=GRID_CONFIG['color'],
    alpha=GRID_CONFIG['alpha'],
    linestyle=tuple(GRID_CONFIG['linestyle']),
    linewidth=GRID_CONFIG['linewidth'],
)
ax.set_axisbelow(True)

# ── Spines ────────────────────────────────────────────────────
for spine in ax.spines.values():
    spine.set_visible(False)

# ── X range padding ──────────────────────────────────────────
ax.set_xlim(df['date'].min() - pd.Timedelta(days=10),
            df['date'].max() + pd.Timedelta(days=5))

# ── Save ──────────────────────────────────────────────────────
fig.tight_layout()

output_dir = Path('outputs/charts/defi')
output_dir.mkdir(parents=True, exist_ok=True)

filename = 'defi_median_apy'
fig.savefig(output_dir / f'{filename}.png', dpi=DPI, facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(output_dir / f'{filename}.svg', format='svg', facecolor='none',
            edgecolor='none', bbox_inches='tight', transparent=True)

print(f'Saved: {output_dir / filename}.png')
print(f'Saved: {output_dir / filename}.svg')
plt.close(fig)
