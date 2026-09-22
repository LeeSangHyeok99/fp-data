"""
USDH HYPE Buybacks - Daily bar + Cumulative line (HRC theme)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'hrc'))
from config import create_figure, apply_style, save_chart, COLORS

# ── Data ──
df = pd.read_csv('/Users/ijaheun/Desktop/USDH_Buybacks.csv')
df['transfer_date'] = pd.to_datetime(df['transfer_date'])
df = df.sort_values('transfer_date')

# Skip first row (2025-11-22 $70K one-time seed, distorts scale)
df = df.iloc[1:].reset_index(drop=True)

dates = df['transfer_date']
daily = df['daily_usd_value']
cumulative = df['cumulative_usd'] / 1e3  # to thousands

# ── Chart ──
fig, ax1 = create_figure('bar')

# Daily bars
bar_color = '#50e3c2'
ax1.bar(dates, daily, width=0.8, color=bar_color, alpha=0.7, edgecolor='none')

# Y axis left (daily)
y1_max = int(np.ceil(daily.max() / 1000) * 1000)
y1_ticks = np.arange(0, y1_max + 1, 1000)
ax1.set_yticks(y1_ticks)
ax1.set_yticklabels([f'{int(v/1000)}K' if v >= 1000 else '0' for v in y1_ticks])
ax1.set_ylim(0, y1_max)

# Cumulative line on secondary axis
ax2 = ax1.twinx()
line_color = '#0d5c4a'
ax2.plot(dates, cumulative, color=line_color, linewidth=2.5, zorder=5)
ax2.scatter(dates.iloc[-1], cumulative.iloc[-1], color=line_color, s=50, zorder=6, edgecolors='none')

# Y axis right (cumulative)
cum_max = int(np.ceil(cumulative.max() / 100) * 100)
n_ticks = len(y1_ticks)
y2_ticks = np.linspace(0, cum_max, n_ticks)
y2_ticks = [int(round(v / 50) * 50) for v in y2_ticks]
ax2.set_yticks(y2_ticks)
ax2.set_yticklabels([f'{int(v)}K' if v > 0 else '0' for v in y2_ticks])
ax2.set_ylim(0, cum_max)

# X axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

apply_style(fig, ax1, 'bar')

# ax2 styling
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.tick_params(axis='y', labelsize=18, pad=15, length=0, colors=line_color)
ax2.grid(False)

fig.tight_layout()

output_dir = 'outputs/charts/hyperliquid/stablecoin'
save_chart(fig, 'usdh_buybacks_hrc', output_dir)
plt.close()
print(f'Saved to {output_dir}/usdh_buybacks_hrc.png')

# Stats
print(f'\nLatest ({dates.iloc[-1].strftime("%Y-%m-%d")}):')
print(f'  Daily: ${daily.iloc[-1]:,.0f}')
print(f'  Cumulative: ${df["cumulative_usd"].iloc[-1]:,.0f}')
