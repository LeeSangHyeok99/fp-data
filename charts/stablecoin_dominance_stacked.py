"""
Stablecoin Market Cap Dominance - Stacked Area Chart
Top stablecoins market share evolution (2024-2026)
Source: rwa.xyz via stablecoin_market_cap_timeseries.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS

# ── Data ──
df = pd.read_csv('outputs/data/stablecoin_market_cap_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Filter from 2024-01-01
df = df[df['Date'] >= '2024-01-01'].copy()

# Top stablecoins to show
top_coins = ['Tether USDt', 'USDC', 'USDS', 'Ethena USDe', 'USD1', 'Dai Stablecoin', 'Paypal USD']
other_cols = [c for c in df.columns[3:] if c not in top_coins]

# Fill NaN with 0
for col in df.columns[3:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calculate Others
df['Others'] = df[other_cols].sum(axis=1)

series_order = ['Tether USDt', 'USDC', 'USDS', 'Ethena USDe', 'USD1', 'Dai Stablecoin', 'Paypal USD', 'Others']

# Brand colors
brand_colors = {
    'Tether USDt': '#26a17b',
    'USDC': '#2775ca',
    'USDS': '#1bab9b',
    'Ethena USDe': '#8b5cf6',
    'USD1': '#c9a84c',
    'Dai Stablecoin': '#f5ac37',
    'Paypal USD': '#003087',
    'Others': '#787b86',
}

# Weekly resample for smoother chart
df = df.set_index('Date')
weekly = df[series_order].resample('W').last().dropna()
dates = weekly.index

# Convert to billions
data_b = weekly / 1e9

# ── Chart ──
fig, ax = create_figure('stacked')

# Stacked area
y_stack = np.row_stack([data_b[col].values for col in series_order])
colors = [brand_colors[col] for col in series_order]
ax.stackplot(dates, y_stack, colors=colors, alpha=0.85, linewidth=0.5, edgecolor='#141414')

# Y axis
max_val = y_stack.sum(axis=0).max()
tick_max = int(np.ceil(max_val / 50) * 50)
y_ticks = np.arange(0, tick_max + 1, 50)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{int(v)}B' for v in y_ticks])
ax.set_ylim(0, tick_max)

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

apply_style(fig, ax, 'stacked')

# Output
output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_dominance_stacked', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_dominance_stacked.png')

# Print latest values for .md
latest = data_b.iloc[-1]
total = latest.sum()
print(f'\nLatest ({dates[-1].strftime("%Y-%m-%d")}):')
for col in series_order:
    share = latest[col] / total * 100
    print(f'  {col}: ${latest[col]:.1f}B ({share:.1f}%)')
print(f'  Total: ${total:.1f}B')
