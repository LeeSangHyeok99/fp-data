import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import (
    setup_font, apply_style, save_chart, create_figure,
    COLORS, DPI, AXIS_CONFIG, GRID_CONFIG,
)

setup_font()

OI_COLOR = '#2f7dd6'
VOL_COLOR = '#55d292'

df = pd.read_csv('outputs/data/coinglass_crypto_futures_oi_volume.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

df['oi_B'] = df['oi_total'] / 1e9
df['vol_B'] = df['vol_total'] / 1e9

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax_vol = ax.twinx()
ax_vol.bar(df['date'], df['vol_B'], width=1.0,
           color=VOL_COLOR, alpha=0.85, linewidth=0, zorder=2)
ax_vol.set_ylim(0, 900)
vol_ticks = np.array([0, 300, 600, 900])
ax_vol.set_yticks(vol_ticks)
ax_vol.set_yticklabels(
    [f'${int(v)}B' for v in vol_ticks],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=VOL_COLOR,
)
ax_vol.set_ylabel('Volume', fontsize=AXIS_CONFIG['y_tick']['fontsize'],
                  fontweight='bold', color=VOL_COLOR, labelpad=12)
ax_vol.set_zorder(1)

ax.fill_between(df['date'], df['oi_B'], 0,
                color=OI_COLOR, alpha=0.45, linewidth=0, zorder=3)
ax.plot(df['date'], df['oi_B'], color=OI_COLOR, linewidth=1.6, zorder=4)
ax.set_zorder(2)
ax.patch.set_visible(False)

ax.set_ylim(0, 300)
y_ticks = np.array([0, 100, 200, 300])
ax.set_yticks(y_ticks)
ax.set_yticklabels(
    [f'${int(v)}B' for v in y_ticks],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=OI_COLOR,
)
ax.set_ylabel('Open Interest', fontsize=AXIS_CONFIG['y_tick']['fontsize'],
              fontweight='bold', color=OI_COLOR, labelpad=12)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.tick_params(axis='x',
               labelsize=AXIS_CONFIG['x_tick']['fontsize'],
               colors=COLORS['text_secondary'],
               length=AXIS_CONFIG['x_tick']['length'],
               width=AXIS_CONFIG['x_tick']['width'],
               pad=AXIS_CONFIG['x_tick']['pad'])
for label in ax.xaxis.get_majorticklabels():
    label.set_fontweight('bold')
    label.set_rotation(AXIS_CONFIG['x_tick']['rotation'])
    label.set_ha(AXIS_CONFIG['x_tick']['ha'])

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for a in (ax, ax_vol):
    for spine in a.spines.values():
        spine.set_visible(False)
    a.margins(x=0)
ax.tick_params(axis='y', length=0,
               labelsize=AXIS_CONFIG['y_tick']['fontsize'],
               pad=AXIS_CONFIG['y_tick']['pad'],
               colors=OI_COLOR)
ax_vol.tick_params(axis='y', length=0,
                   labelsize=AXIS_CONFIG['y_tick']['fontsize'],
                   pad=AXIS_CONFIG['y_tick']['pad'],
                   colors=VOL_COLOR)

fig.tight_layout()

out_dir = 'outputs/charts/bitcoin/futures'
Path(out_dir).mkdir(parents=True, exist_ok=True)
for fmt in ('png', 'svg'):
    fig.savefig(
        f'{out_dir}/btc_futures_oi_volume.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()
print(f'Saved: {out_dir}/btc_futures_oi_volume.png')
