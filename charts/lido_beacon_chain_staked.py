"""
ETH Staked on the Beacon Chain through Lido middleware.
Four Pillars design theme. Reproduction of the Lido Dune area chart.

Stacked area (left axis, millions of ETH):
  - Lido Core | bc only  (bottom, coral)
  - Others    | bc only  (middle, grey)
  - Entry queue          (top, teal)
Line (right axis, %):
  - Lido Share | bc only, peaking ~32% (2022-23) and falling to ~21% by 2026.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import create_figure, apply_style, save_chart, COLORS, endpoint_dot

mpl.rcParams['svg.fonttype'] = 'none'

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/lido_beacon_staked.csv')
df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m')
df = df.sort_values('date').reset_index(drop=True)

dates = df['date']
lido = df['lido_core_m']
others = df['others_m']
entry = df['entry_queue_m']
share_bc = df['lido_share_pct']        # Lido Share | bc only
share_be = df['lido_share_be_pct']     # Lido Share | bc + entry queue

# ─── Colors ─────────────────────────────────────────────────────────────
LIDO = '#F0573E'    # Lido Core, coral (matches the Dune chart)
OTHERS = '#5b5e66'  # rest of beacon chain, muted grey
ENTRY = '#4FC8C4'   # validator entry queue, teal
SHARE_BC = '#9B8CE8'  # Lido Share | bc only, lavender
SHARE_BE = '#E6D74B'  # Lido Share | bc + entry queue, yellow

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('area')
fig.set_size_inches(13.5, 5.6)
ax2 = ax.twinx()

# ─── Left axis: stacked areas (Lido base → Others → Entry queue) ───────
base0 = lido
base1 = lido + others
base2 = lido + others + entry

ax.fill_between(dates, base0, 0, color=LIDO, alpha=0.92, linewidth=0, zorder=4)
ax.fill_between(dates, base1, base0, color=OTHERS, alpha=0.5, linewidth=0, zorder=2)
ax.fill_between(dates, base2, base1, color=ENTRY, alpha=0.6, linewidth=0, zorder=3)
ax.plot(dates, base0, color=LIDO, linewidth=1.6, zorder=5)
ax.plot(dates, base1, color=OTHERS, linewidth=1.0, alpha=0.7, zorder=2)

# ─── Right axis: Lido share lines (bc only + bc+entry queue) ───────────
ax2.plot(dates, share_be, color=SHARE_BE, linewidth=2.4, zorder=6)
ax2.plot(dates, share_bc, color=SHARE_BC, linewidth=2.4, zorder=7)
endpoint_dot(ax2, dates.iloc[-1], share_bc.iloc[-1], color=SHARE_BC, size=58)
endpoint_dot(ax2, dates.iloc[-1], share_be.iloc[-1], color=SHARE_BE, size=58)

# ─── Y axes (5 aligned ticks each) ─────────────────────────────────────
ax.set_ylim(0, 44)
left_ticks = [0, 10, 20, 30, 40]
ax.set_yticks(left_ticks)
ax.set_yticklabels([f'{v}M' for v in left_ticks])

ax2.set_ylim(0, 44)
right_ticks = [0, 10, 20, 30, 40]
ax2.set_yticks(right_ticks)
ax2.set_yticklabels([f'{v}%' for v in right_ticks])

# ─── X axis: yearly Jan ticks, Mon YYYY ────────────────────────────────
ax.xaxis.set_major_locator(mdates.YearLocator(month=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'area')

ax2.set_facecolor('none')
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=18, length=0, pad=15,
                colors=COLORS['text_secondary'])
for lbl in ax2.get_yticklabels():
    lbl.set_fontweight('bold')

ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', length=6, width=1, color=COLORS['text_secondary'])

ax.set_xlim(dates.min() - pd.Timedelta(days=3), dates.max())
# Drop the Jan 2021 edge tick (rotated label overflows the left margin)
ticks = [t for t in ax.get_xticks()
         if t >= mdates.date2num(pd.Timestamp('2022-01-01'))]
ax.set_xticks(ticks)
for label in ax.xaxis.get_majorticklabels():
    label.set_rotation(45)
    label.set_ha('right')

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/ethereum/staking'
png_path, svg_path = save_chart(fig, 'lido_beacon_chain_staked', output_dir)
print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
