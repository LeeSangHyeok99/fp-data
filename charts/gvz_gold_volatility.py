"""CBOE Gold Volatility Index (GVZ), 2022 - today. Four Pillars theme.

Reference: Yahoo Finance / AlphaSpace ^GVZ 5Y view (teal-green area line).
Data: Yahoo Finance ^GVZ daily close.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart

# Reference teal-green
LINE_COLOR = "#2f9e8f"

df = pd.read_csv('outputs/data/gvz_gold_volatility.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

fig, ax = create_figure('area')

dates = df['date']
gvz = df['gvz']

# Area fill under the line (light, like reference)
ax.fill_between(dates, gvz, 0, color=LINE_COLOR, alpha=0.10, linewidth=0, zorder=2)
ax.plot(dates, gvz, color=LINE_COLOR, linewidth=1.8, zorder=3)

# Endpoint dot
ax.scatter(dates.iloc[-1], gvz.iloc[-1], color=LINE_COLOR, s=42, zorder=5,
           edgecolors='none')

# Y axis: clean 10-point steps, %
ax.set_ylim(8, 48)
ax.set_yticks([10, 20, 30, 40])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{int(v)}%'))

# X axis: year ticks (include 2022 by pinning xlim to Jan 1)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_xlim(pd.Timestamp('2022-01-01'), dates.iloc[-1])

apply_style(fig, ax, 'area')

# Year labels look cleaner without rotation
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

out_dir = 'outputs/charts/gold/volatility'
save_chart(fig, 'gvz_gold_volatility', out_dir)
plt.close(fig)
print('saved to', out_dir)
