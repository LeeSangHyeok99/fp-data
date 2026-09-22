"""
Visa Onchain Analytics - Stablecoin Adjusted Transaction Volume (Monthly, 2017~2026)
Data: Visa Onchain Analytics / Allium
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
from config import (create_figure, apply_style, save_chart,
                    COLORS, area_glow, endpoint_dot)

# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/visa_stablecoin_adjusted_volume.csv')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
df = df.sort_values('date')

dates = df['date']
values = df['adjusted_volume']

# ─── Chart ──────────────────────────────────────────────────────────────
fig, ax = create_figure('area')

area_color = '#5470c6'

ax.plot(dates, values, color=area_color, linewidth=2.0, zorder=4)
area_glow(ax, dates, values, color=area_color, n_layers=50, max_alpha=0.22, power=2.5)
endpoint_dot(ax, dates.iloc[-1], values.iloc[-1], color=area_color, size=60)

# ─── Y-axis ($B) ────────────────────────────────────────────────────────
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

def fmt_trillions(x, pos):
    return f'${x / 1e12:.1f}T'

ax.yaxis.set_major_formatter(FuncFormatter(fmt_trillions))

# ─── X-axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))

# ─── Style ───────────────────────────────────────────────────────────────
apply_style(fig, ax, 'area')
ax.set_ylim(bottom=0)

# ─── Save ────────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoins/volume'
png_path, svg_path = save_chart(fig, 'visa_stablecoin_adjusted_volume', output_dir)
print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
plt.close()
