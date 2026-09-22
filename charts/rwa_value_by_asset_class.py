"""RWA total value by asset class (rwa.xyz, Distributed, ex-stablecoins).

Source: sources/rwa-token-timeseries-export-1786328149342.csv
Cross-checked against the live app.rwa.xyz trpc timeseries (identical, 2026-08-08).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

SRC = 'sources/rwa-token-timeseries-export-1786328149342.csv'
START = '2023-09-01'

# rwa.xyz official asset-class colors (group.color from the trpc payload)
RWA_COLORS = {
    'US Treasury Debt': '#05417a',
    'Commodities': '#daa520',
    'Active Strategies': '#4682b4',
    'Asset-Backed Credit': '#6b8e23',
    'Stocks': '#ff4500',
    'Specialty Finance': '#c71585',
    'Corporate Credit': '#8a2be2',
    'non-US Government Debt': '#b0c4de',
    'Private Equity': '#ffd700',
    'Venture Capital': '#BDECB6',
    'Diversified Credit': '#0d00ff',
    'Real Estate': '#d2691e',
    'Public Equity': '#ff4500',
}

TOP_N = 5
OTHERS_COLOR = '#787b86'

df = pd.read_csv(SRC, parse_dates=['Date'])
d = df.set_index('Date')[list(RWA_COLORS)].fillna(0).loc[START:] / 1e9

# Top 5 by latest value, everything else collapsed into Others
top = d.iloc[-1].sort_values(ascending=False).index[:TOP_N].tolist()
d['Others'] = d.drop(columns=top).sum(axis=1)
d = d[top + ['Others']]
RWA_COLORS['Others'] = OTHERS_COLOR

# Others at the very bottom, then smallest first so Treasury Debt caps the area
order = ['Others'] + d[top].iloc[-1].sort_values().index.tolist()

fig, ax = create_figure('stacked')
ax.stackplot(d.index, *[d[c] for c in order],
             colors=[RWA_COLORS[c] for c in order], alpha=0.85, linewidth=0)

ax.set_xlim(d.index.min(), d.index.max())
ax.set_ylim(0, 40)
ax.set_yticks([0, 10, 20, 30, 40])
ax.set_yticklabels([f'${v}B' for v in [0, 10, 20, 30, 40]])
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[3, 9]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'stacked')
# 축별 폰트 통일 (config 기본값 -2)
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 2)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 2)
fig.tight_layout()

png, svg = save_chart(fig, 'rwa_value_by_asset_class', 'outputs/charts/rwa/market_cap')
plt.close(fig)

total = d.iloc[-1].sum()
print(f'{d.index[-1].date()}  total ${total:.2f}B')
for c in reversed(order):
    print(f'  {c:24} ${d[c].iloc[-1]:6.2f}B  {d[c].iloc[-1]/total*100:5.1f}%')
print(png, svg, sep='\n')
