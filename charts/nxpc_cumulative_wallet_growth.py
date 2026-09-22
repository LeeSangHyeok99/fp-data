"""
NXPC Cumulative Wallet Growth - Stacked Area Chart
Four Pillars theme recreation of NEXPACE monthly wallet profile.
NXPC Spenders (bottom) + Ecosystem Reach (top), cumulative wallets.
"""

import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
df = pd.read_csv('outputs/data/nxpc_cumulative_wallet_growth.csv')
df['date'] = pd.to_datetime(df['month'])

# brand-style palette: NXPC Spenders orange, Ecosystem Reach navy/indigo
COLOR_SPENDERS = '#e8833a'
COLOR_REACH = '#4a5aa8'

# -----------------------------------------------------------------------------
# Figure
# -----------------------------------------------------------------------------
fig, ax = create_figure('stacked')
apply_style(fig, ax, 'stacked')

ax.stackplot(
    df['date'],
    df['nxpc_spenders'], df['ecosystem_reach'],
    colors=[COLOR_SPENDERS, COLOR_REACH],
    alpha=0.85, edgecolor='none',
)

# subtle top edge lines on each band
total = df['nxpc_spenders'] + df['ecosystem_reach']
ax.plot(df['date'], df['nxpc_spenders'], color=COLOR_SPENDERS, lw=2, alpha=0.95)
ax.plot(df['date'], total, color=COLOR_REACH, lw=2, alpha=0.95)

# -----------------------------------------------------------------------------
# Axes
# -----------------------------------------------------------------------------
ax.set_xlim(df['date'].min(), df['date'].max())
ax.set_ylim(0, 900000)

# Y ticks: clean 200k steps, unit consistent
ax.yaxis.set_major_locator(MultipleLocator(200000))
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f'{int(v / 1000)}k')
)

# X ticks: Mon YYYY at quarter marks
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

fig.tight_layout()
png, svg = save_chart(fig, 'nxpc_cumulative_wallet_growth',
                      'outputs/charts/nexpace/metrics')
plt.close(fig)
print('Saved:', png)
print('Saved:', svg)
