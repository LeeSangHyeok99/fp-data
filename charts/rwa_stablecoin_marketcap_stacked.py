"""
Stablecoin Market Cap - Stacked Area Chart (Gradient)
Data source: RWA.xyz (app.rwa.xyz/stablecoins)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

# Font
pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    pretendard_font = fm.FontProperties(fname=str(pretendard_path))
else:
    pretendard_font = None

# ─── Gradient stacked area helper ──────────────────────────────────────
def gradient_fill_between(ax, x, y_bottom, y_top, color, n_layers=40):
    """Fill between with vertical gradient: darker at bottom, brighter at top."""
    r, g, b = mcolors.to_rgb(color)
    for i in range(n_layers):
        frac_lo = i / n_layers
        frac_hi = (i + 1) / n_layers
        # Gradient: 40% brightness at bottom → 100% at top
        factor = 0.4 + 0.6 * (frac_hi ** 0.7)
        layer_color = (r * factor, g * factor, b * factor)
        y_lo = y_bottom + (y_top - y_bottom) * frac_lo
        y_hi = y_bottom + (y_top - y_bottom) * frac_hi
        ax.fill_between(x, y_lo, y_hi, color=layer_color,
                        edgecolor='none', linewidth=0, zorder=2)


# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/rwa_stablecoin_marketcap_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# Filter last 2 years
df = df[df.index >= '2024-04-01']

# Top 8 stablecoins + Others
top_coins = ['Tether USDt', 'USDC', 'USDS', 'Ethena USDe', 'Dai Stablecoin',
             'USD1', 'Paypal USD', 'Global Dollar']

data_cols = df.columns[2:]
others = df[data_cols].sum(axis=1)
for col in top_coins:
    if col in df.columns:
        others -= df[col].fillna(0)

pivot = pd.DataFrame(index=df.index)
for col in top_coins:
    if col in df.columns:
        pivot[col] = df[col].fillna(0) / 1e9
pivot['Others'] = others / 1e9

order = ['Tether USDt', 'USDC', 'USDS', 'Ethena USDe', 'Dai Stablecoin',
         'USD1', 'Paypal USD', 'Global Dollar', 'Others']
order = [c for c in order if c in pivot.columns]

# ─── Colors (brand colors) ─────────────────────────────────────────────
color_map = {
    'Tether USDt': '#26a17b',
    'USDC': '#2775ca',
    'USDS': '#1fc7a0',
    'Ethena USDe': '#b8b8d1',
    'Dai Stablecoin': '#f5ac37',
    'USD1': '#e63946',
    'Paypal USD': '#003087',
    'Global Dollar': '#00b894',
    'Others': '#787b86',
}

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')

# ─── Gradient Stacked Area ─────────────────────────────────────────────
dates = pivot.index
cumulative = np.zeros(len(dates))

for col in order:
    y_bottom = cumulative.copy()
    y_top = cumulative + pivot[col].values
    color = color_map.get(col, '#787b86')
    gradient_fill_between(ax, dates, y_bottom, y_top, color, n_layers=30)
    # Thin edge line at top of each layer
    ax.plot(dates, y_top, color='#1a1a1a', linewidth=0.3, zorder=3)
    cumulative = y_top

# ─── X axis ─────────────────────────────────────────────────────────────
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
for label in ax.xaxis.get_majorticklabels():
    label.set_fontsize(AXIS_CONFIG['x_tick']['fontsize'])
    label.set_fontweight('bold')
    label.set_color(AXIS_CONFIG['x_tick']['color'])
    label.set_rotation(45)
    label.set_ha('right')
    if pretendard_font:
        label.set_fontproperties(pretendard_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_ylim(0, 350)
y_ticks = [0, 100, 200, 300]
ax.set_yticks(y_ticks)
ax.set_yticklabels(
    ['$0B', '$100B', '$200B', '$300B'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
    fontproperties=pretendard_font,
)

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'stacked')
ax.tick_params(axis='x', length=0)
ax.tick_params(axis='y', pad=5)
ax.set_xlim(dates.min(), dates.max())

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoin/marketcap'
png_path, svg_path = save_chart(fig, 'stablecoin_marketcap_stacked', output_dir)
plt.close()
print(f'Saved: {png_path}')
