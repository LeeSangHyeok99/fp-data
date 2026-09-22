"""
Stablecoin Adjusted Transaction Volume - Area Chart (Monthly, 2021~2026)
Data: Artemis Analytics
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator, FuncFormatter
from config import (create_figure, apply_style, save_chart,
                    COLORS, area_glow, endpoint_dot)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/stablecoin_adjusted_txn_volume_monthly.csv', parse_dates=['date'])
df = df.sort_values('date')

dates = df['date']
values = df['adjusted_transaction_volume']

# ─── Chart ──────────────────────────────────────────────────────────────
fig, ax = create_figure('area')

area_color = '#ee6666'

# Line
ax.plot(dates, values, color=area_color, linewidth=2.0, zorder=4)

# Glow effect
area_glow(ax, dates, values, color=area_color, n_layers=50, max_alpha=0.20, power=2.5)

# Endpoint dot
endpoint_dot(ax, dates.iloc[-1], values.iloc[-1], color=area_color, size=60)

# ─── Y-axis ($B) ────────────────────────────────────────────────────────
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

def fmt_billions(x, pos):
    return f'${x / 1e9:.0f}B'

ax.yaxis.set_major_formatter(FuncFormatter(fmt_billions))

# ─── X-axis (Mon YYYY) ──────────────────────────────────────────────────
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

# ─── Style ───────────────────────────────────────────────────────────────
apply_style(fig, ax, 'area')
ax.set_ylim(bottom=0)

# ─── Save ────────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoins/volume'
png_path, svg_path = save_chart(fig, 'stablecoin_adjusted_txn_volume', output_dir)

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
plt.close()
