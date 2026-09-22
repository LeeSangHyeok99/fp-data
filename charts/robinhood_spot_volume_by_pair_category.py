"""Robinhood Chain daily spot volume share by pair category.

Data: Blockworks Research public dashboard API (visualization 10332,
"Robinhood: Spot Volume by Pair Category"). Shares are normalised across the
three plotted categories, which is how the source dashboard renders them.
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import requests

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, save_chart

API = ('https://blockworks.com/api/studio/dashboard/robinhood-spot-dexs'
       '/visualization/10332/execution?limit=50000&page=1')
CACHE = 'outputs/data/robinhood_spot_volume_by_pair_category.csv'
MONTH = '2026-07'

COLS = {  # column -> (label, colour) in stack order, bottom first
    'memes_volume_usd': ('Memecoins', '#CCFF00'),
    'native_stablecoin_volume_usd': ('ETH-Stablecoin', '#D4D4CE'),
    'tokenized_assets_volume_usd': ('Tokenized Assets', '#46A037'),
}

try:
    # plain requests without a UA gets served an HTML error page
    rows = requests.get(API, timeout=60,
                        headers={'User-Agent': 'Mozilla/5.0',
                                 'Accept': 'application/json'}).json()['data']
    pd.DataFrame(rows).to_csv(CACHE, index=False)
except Exception as exc:  # offline / API down -> last good pull
    print(f'API fetch failed ({exc}), using {CACHE}')

df = pd.read_csv(CACHE, parse_dates=['block_date'])
df = df[df['block_date'].dt.strftime('%Y-%m') == MONTH].sort_values('block_date')
share = df[list(COLS)].div(df[list(COLS)].sum(axis=1), axis=0) * 100

fig, ax = create_figure('stacked_bar')
x = range(len(df))
bottom = pd.Series(0.0, index=share.index)
for col, (_, color) in COLS.items():
    ax.bar(x, share[col], bottom=bottom, width=0.78, color=color, linewidth=0)
    bottom += share[col]

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.set_xlim(-0.6, len(df) - 0.4)
ticks = list(range(0, len(df), 3))
ax.set_xticks(ticks)
ax.set_xticklabels([df['block_date'].iloc[i].strftime('%b %-d') for i in ticks])

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=14)
fig.tight_layout()
print(save_chart(fig, 'robinhood_spot_volume_by_pair_category',
                 'outputs/charts/robinhood/volume')[0])
plt.close(fig)

for col, (label, _) in COLS.items():
    print(f'{label:16s} month avg {share[col].mean():5.1f}%  '
          f'first {share[col].iloc[0]:5.1f}%  last {share[col].iloc[-1]:5.1f}%')
