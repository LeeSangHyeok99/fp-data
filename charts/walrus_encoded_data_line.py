import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    COLORS, GRID_CONFIG
)

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
df = pd.read_csv('/Users/ijaheun/Desktop/Walrus_Encoded_Data_Volume.csv')
df['day_utc'] = pd.to_datetime(df['day_utc'])
df['capacity_pb'] = df['capacity_size'] / 1_000_000  # GB → PB

# Walrus brand color
WALRUS = '#97F0E5'

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
fig, ax = create_figure('line')

# ── Line + area fill ──
ax.fill_between(df['day_utc'], df['capacity_pb'], alpha=0.12, color=WALRUS)
ax.plot(df['day_utc'], df['capacity_pb'], color=WALRUS, linewidth=2.5, zorder=3)

# ══════════════════════════════════════════════════
# Y-axis (PB, max 5 ticks)
# ══════════════════════════════════════════════════
ax.set_ylim(0, 2.0)
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{x:.1f}PB'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['day_utc'].min(), df['day_utc'].max())

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
apply_style(fig, ax, 'line')

# x-tick rotation 45deg
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')


# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'walrus_encoded_data_line',
                                'outputs/charts/walrus')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
