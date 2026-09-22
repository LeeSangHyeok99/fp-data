import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS, area_glow, endpoint_dot

# Data
df = pd.read_csv('outputs/data/polymarket_dau.csv')
df['day'] = pd.to_datetime(df['day'])

# Figure
fig, ax = create_figure('area')

# Polymarket brand color
color = '#4C82FB'

# Line
ax.plot(df['day'], df['dau'], color=color, linewidth=1.8, zorder=4)

# Glow
area_glow(ax, df['day'], df['dau'], color=color, n_layers=50, max_alpha=0.18, power=2.5)

# Endpoint
endpoint_dot(ax, df['day'].iloc[-2], df['dau'].iloc[-2], color=color, size=40)
# -2 because last day (04-08) is incomplete

# Y axis: 0 to 200K, ticks at 0, 50K, 100K, 150K, 200K
ax.set_ylim(0, 200000)
ax.yaxis.set_major_locator(mticker.FixedLocator([0, 50000, 100000, 150000, 200000]))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x/1000)}K'))

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['day'].min(), df['day'].iloc[-2])

# Style
apply_style(fig, ax, 'area')

# Event annotations
events = [
    ('2025-12-22', 'POLY L2\nAnnounced'),
    ('2026-03-18', 'Brahma\nAcquired'),
]

for date_str, label in events:
    event_date = pd.to_datetime(date_str)
    ax.axvline(event_date, color=COLORS['text_secondary'], alpha=0.4, linestyle='--', linewidth=0.8, zorder=3)
    ax.text(event_date, ax.get_ylim()[1] * 0.92, label,
            ha='center', va='top', fontsize=9, fontweight='bold',
            color=COLORS['text_secondary'], zorder=5)

# Save
output_dir = 'outputs/charts/polymarket/polygon_exit'
png_path, svg_path = save_chart(fig, 'polymarket_dau', output_dir)
plt.close(fig)
print(f'Saved: {png_path}')
