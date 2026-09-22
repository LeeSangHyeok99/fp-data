"""
Staked ETH - History of staked ETH (sum of all Effective Balances)
Four Pillars design theme.

Series calibrated to documented real reference points:
  - 2020-12 genesis  ~0.67M ETH (~21k validators)
  - 2022-09 The Merge ~13.7M ETH
  - 2023-04-12 Shapella 17.97M ETH (beaconcha.in tooltip)
  - 2026-06-01 current 39.26M ETH (ultrasound.money effective-balance-sum)
Monthly resolution; intermediate points interpolated along the known shape.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

# Export editable text (real <text>, not glyph <use> paths) so the SVG imports
# as separable layers in design tools instead of one merged blob.
mpl.rcParams['svg.fonttype'] = 'none'

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/ethereum_staked_eth.csv')
df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m')
df = df.sort_values('date').reset_index(drop=True)

dates = df['date']
staked = df['staked_eth_millions']

# ─── Color ──────────────────────────────────────────────────────────────
BLUE = '#6CA6E8'   # beaconcha.in sky blue

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('area')
fig.set_size_inches(13.5, 5.6)

# ─── Area + line ────────────────────────────────────────────────────────
ax.fill_between(dates, staked, 0, color=BLUE, alpha=0.55, linewidth=0, zorder=2)
ax.plot(dates, staked, color=BLUE, linewidth=2.4, zorder=4)

# ─── Y axis (5 clean ticks) ─────────────────────────────────────────────
ax.set_ylim(0, 42)
y_ticks = [0, 10, 20, 30, 40]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}M' for v in y_ticks])

# ─── X axis: yearly Jan ticks, Mon YYYY format ─────────────────────────
ax.xaxis.set_major_locator(mdates.YearLocator(month=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'area')

ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', length=0)
# Minimal left padding, but drop the Jan 2021 tick label
ax.set_xlim(dates.min() - pd.Timedelta(days=3), dates.max())
ticks = [t for t in ax.get_xticks() if t >= mdates.date2num(pd.Timestamp('2021-01-01'))]
ax.set_xticks(ticks)
# Horizontal, left-aligned x tick labels
for label in ax.xaxis.get_majorticklabels():
    label.set_rotation(0)
    label.set_ha('left')

# ─── Shapella hard fork marker (2023-04-12, enabled staking withdrawals) ──
shapella = pd.Timestamp('2023-04-12')
ax.axvline(shapella, color='#ffffff', linewidth=1.4,
           linestyle=(0, (5, 3)), zorder=5)
ax.text(shapella, 43.2, 'Shapella', color='#ffffff',
        fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=6,
        clip_on=False)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/ethereum/staking'
png_path, svg_path = save_chart(fig, 'ethereum_staked_eth', output_dir)
print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
