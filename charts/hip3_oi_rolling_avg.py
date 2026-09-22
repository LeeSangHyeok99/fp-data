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

import importlib.util
_spec = importlib.util.spec_from_file_location('fp_config', '.claude/skills/design/four-pillars/config.py')
_fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fp)
endpoint_dot = _fp.endpoint_dot

output_dir = 'outputs/charts/hyperliquid/hip3'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('/Users/ijaheun/Downloads/hip3_oi_rolling_avg.csv', parse_dates=['Date'])
df['7d-avg'] = pd.to_numeric(df['7d-avg'], errors='coerce')
df['14d-avg'] = pd.to_numeric(df['14d-avg'], errors='coerce')

# Convert to billions
df['7d_b'] = df['7d-avg'] / 1e9
df['14d_b'] = df['14d-avg'] / 1e9

# Drop rows where both are NaN
df = df.dropna(subset=['7d-avg', '14d-avg'], how='all')

# =============================================================================
# Chart
# =============================================================================
setup_font()

COLOR_7D = '#10b981'   # HRC neon green
COLOR_14D = '#06b6d4'  # HRC teal

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Simple fill for 7d (area_glow doesn't work on dark backgrounds)
df_7d = df.dropna(subset=['7d-avg'])
ax.fill_between(df_7d['Date'], 0, df_7d['7d_b'],
                color=COLOR_7D, alpha=0.08, zorder=1)

# Lines
ax.plot(df['Date'], df['14d_b'], color=COLOR_14D, linewidth=2.0, alpha=0.8, zorder=4)
ax.plot(df['Date'], df['7d_b'], color=COLOR_7D, linewidth=2.5, zorder=5)

# Endpoint dots only (no text)
last = df.iloc[-1]
if not pd.isna(last['7d_b']):
    endpoint_dot(ax, last['Date'], last['7d_b'], COLOR_7D, size=60)
if not pd.isna(last['14d_b']):
    endpoint_dot(ax, last['Date'], last['14d_b'], COLOR_14D, size=50)

# Y axis
y_max_raw = df[['7d_b', '14d_b']].max().max()
y_max = np.ceil(y_max_raw * 2) / 2  # round up to 0.5
y_ticks = np.arange(0, y_max + 0.5, 0.5)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v:.1f}B' if v > 0 else '' for v in y_ticks],
                    fontsize=16, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, y_max + 0.2)

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.tick_params(axis='x', labelsize=14, length=6, width=1,
               colors=COLORS['text_secondary'])
fig.autofmt_xdate(rotation=45, ha='right')
for label in ax.xaxis.get_majorticklabels():
    label.set_fontweight('bold')
    label.set_color(COLORS['text_secondary'])

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', length=0)

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hip3_oi_rolling_avg.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# Stats
print(f'Latest 7d avg: ${last["7d_b"]:.2f}B')
print(f'Latest 14d avg: ${last["14d_b"]:.2f}B')
print(f'Data range: {df["Date"].min().strftime("%Y-%m-%d")} to {df["Date"].max().strftime("%Y-%m-%d")}')
print(f'Total data points: {len(df)}')
print(f'Done: hip3_oi_rolling_avg.png')
