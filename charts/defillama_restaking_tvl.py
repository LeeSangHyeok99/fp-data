"""DefiLlama Restaking category TVL (area line)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import requests
import sys
from datetime import datetime

sys.path.append('.claude/skills/design/four-pillars')
from config import (create_figure, apply_style, save_chart, area_glow,
                    AXIS_CONFIG)

COLOR = '#3b6ef6'
START = '2023-07-01'

protos = requests.get('https://api.llama.fi/protocols', timeout=90).json()
slugs = [p['slug'] for p in protos if p.get('category') == 'Restaking']

series = {}
for s in slugs:
    d = requests.get(f'https://api.llama.fi/protocol/{s}', timeout=90).json()
    tvl = d.get('tvl') or []
    if tvl:
        series[s] = pd.Series({datetime.utcfromtimestamp(x['date']).date(): x['totalLiquidityUSD']
                               for x in tvl})

df = pd.DataFrame(series).sort_index()
df.index = pd.to_datetime(df.index)
df = df[~df.index.duplicated(keep='last')].resample('D').last().ffill().fillna(0.0)
total = df.sum(axis=1)
total = total[total.index >= START]
total.rename('restaking_tvl_usd').to_csv('outputs/data/defillama_restaking_tvl.csv')

y = total / 1e9
fig, ax = create_figure('area')
ax.plot(total.index, y, color=COLOR, linewidth=1.8, zorder=4)
area_glow(ax, total.index, y.values, COLOR, max_alpha=0.5, power=1.6)

ax.set_ylim(0, 32)
ax.set_yticks([0, 10, 20, 30])
ax.set_yticklabels([f'${v}B' for v in [0, 10, 20, 30]])
ax.set_xlim(total.index[0], total.index[-1])
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6)
fig.tight_layout()
save_chart(fig, 'defillama_restaking_tvl', 'outputs/charts/defi/restaking')
plt.close(fig)

print(f'protocols: {len(series)}  range: {total.index[0].date()} -> {total.index[-1].date()}')
print(f'latest: ${y.iloc[-1]:.2f}B   peak: ${y.max():.2f}B on {y.idxmax().date()}')
