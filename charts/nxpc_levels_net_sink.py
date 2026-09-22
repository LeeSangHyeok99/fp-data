"""
NXPC In-game Rewards vs Player Spending + Net Sink - Dual Axis Combo
Four Pillars theme recreation of NEXPACE NXPC flow chart.

Left axis (lines):
  - Player spending (solid blue)
  - In-game rewards (dashed orange)
Right axis (bars):
  - Net sink (green positive / gray negative)
"""

import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, FixedLocator

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

# -----------------------------------------------------------------------------
# Data (real source CSV)
# -----------------------------------------------------------------------------
df = pd.read_csv('outputs/data/nxpc_chart_data_raw_nxpc.csv')
df['date'] = pd.to_datetime(df['Month'])

rewards = df['In-game rewards (NXPC)'] / 1e6
spending = df['Player spending (NXPC)'] / 1e6
net_sink = df['Net sink (NXPC)'] / 1e6

COLOR_SPENDING = '#4f8fcf'   # blue solid line
COLOR_REWARDS = '#d4663a'    # orange dashed line
COLOR_POS = '#3f9c7c'        # net sink positive bar (green)
COLOR_NEG = '#9aa0ab'        # net sink negative bar (gray)

# -----------------------------------------------------------------------------
# Figure
# -----------------------------------------------------------------------------
fig, ax = create_figure('line')        # left axis: lines
ax2 = ax.twinx()                        # right axis: bars

# --- bars (net sink) on right axis, behind lines ---
bar_colors = [COLOR_POS if v >= 0 else COLOR_NEG for v in net_sink]
ax2.bar(df['date'], net_sink, width=20, color=bar_colors,
        alpha=0.55, zorder=1, edgecolor='none')

# --- lines on left axis, in front ---
ax.plot(df['date'], spending, color=COLOR_SPENDING, lw=3,
        marker='o', markersize=8, zorder=5)
ax.plot(df['date'], rewards, color=COLOR_REWARDS, lw=3, linestyle=(0, (6, 4)),
        marker='o', markersize=8, zorder=5)

# bring line axis to front, keep its background transparent
ax.set_zorder(ax2.get_zorder() + 1)
ax.patch.set_visible(False)

# -----------------------------------------------------------------------------
# Axes: dual-axis aligned ticks (5 ticks each, clean values)
# -----------------------------------------------------------------------------
# Left "Levels": 2M..6M
ax.set_ylim(2, 6)
ax.yaxis.set_major_locator(FixedLocator([2, 3, 4, 5, 6]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}M'))

# Right "Net sink": -4M..4M (0 aligns with left 4M gridline)
ax2.set_ylim(-4, 4)
ax2.yaxis.set_major_locator(FixedLocator([-4, -2, 0, 2, 4]))
ax2.yaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f'{v:+.0f}M' if v != 0 else '0M')
)

# X axis: month ticks, Mon YYYY
ax.set_xlim(df['date'].min() - pd.Timedelta(days=18),
            df['date'].max() + pd.Timedelta(days=18))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')

# style right axis to match theme (apply_style only touches left ax)
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=18, length=0, pad=15,
                colors=COLORS['text_secondary'])
for lbl in ax2.get_yticklabels():
    lbl.set_fontweight('bold')

fig.tight_layout()
png, svg = save_chart(fig, 'nxpc_levels_net_sink',
                      'outputs/charts/nexpace/metrics')
plt.close(fig)
print('Saved:', png)
print('Saved:', svg)
