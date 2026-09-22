import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, area_glow, endpoint_dot

# Data (reconstructed from ASXN HyperCore DAU reference image, 7D AVG)
df = pd.read_csv('outputs/data/hypercore_dau.csv')
df['day'] = pd.to_datetime(df['day'])

# Figure
fig, ax = create_figure('area')

# HyperCore / Hyperliquid brand teal
color = '#50D2C1'

# Line
ax.plot(df['day'], df['dau'], color=color, linewidth=1.8, zorder=4)

# Glow under the line
area_glow(ax, df['day'], df['dau'], color=color, n_layers=50, max_alpha=0.18, power=2.5)

# Endpoint marker
endpoint_dot(ax, df['day'].iloc[-1], df['dau'].iloc[-1], color=color, size=40)

# Y axis: 0 to 60K, ticks at 0, 20K, 40K, 60K
ax.set_ylim(0, 60000)
ax.yaxis.set_major_locator(mticker.FixedLocator([0, 20000, 40000, 60000]))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x/1000)}K'))

# X axis
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['day'].min(), df['day'].max())

# Style
apply_style(fig, ax, 'area')

# Save
output_dir = 'outputs/charts/hyperliquid/metrics'
png_path, svg_path = save_chart(fig, 'hypercore_daily_active_users', output_dir)
plt.close(fig)
print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
