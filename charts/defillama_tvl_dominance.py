"""DefiLlama TVL dominance: Ethereum vs other chains (100% stacked area)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import requests
import sys
from datetime import datetime

sys.path.append('.claude/skills/design/four-pillars')
from config import (create_figure, apply_style, save_chart, band_gradient,
                    COLORS, AXIS_CONFIG)

CHAINS = {
    'Ethereum': '#627eea',
    'Solana': '#9945ff',
    'Base': '#0052ff',
    'BSC': '#f0b90b',
    'Tron': '#eb0029',
    'Others': '#6b7280',
}

def hist(path):
    d = requests.get(f'https://api.llama.fi/v2/historicalChainTvl{path}', timeout=60).json()
    return pd.Series({datetime.utcfromtimestamp(x['date']).date(): x['tvl'] for x in d})

names = [c for c in CHAINS if c != 'Others']
df = pd.DataFrame({c: hist('/' + c.replace(' ', '%20')) for c in names})
df['_total'] = hist('')
df = df.sort_index().fillna(0.0)
df = df[df['_total'] > 0]
df['Others'] = (df['_total'] - df[names].sum(axis=1)).clip(lower=0)
df = df.drop(columns='_total')

pct = df.div(df.sum(axis=1), axis=0) * 100
pct.index = pd.to_datetime(pct.index)
pct = pct.resample('W').mean().dropna()
pct = pct[pct.index >= '2020-07-01']
pct.to_csv('outputs/data/defillama_tvl_dominance.csv')

fig, ax = create_figure('stacked')
xnum = mdates.date2num(pct.index)
lower = pd.Series(0.0, index=pct.index)
for c, color in CHAINS.items():
    upper = lower + pct[c]
    band_gradient(ax, xnum, lower.to_numpy(), upper.to_numpy(), color, spread=0.16)
    ax.plot(pct.index, upper, color=COLORS['background'], linewidth=0.4, zorder=3)
    lower = upper

ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels([f'{v}%' for v in [0, 25, 50, 75, 100]])
ax.set_xlim(pct.index[0], pct.index[-1])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'stacked')
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6)
fig.tight_layout()
save_chart(fig, 'defillama_tvl_dominance', 'outputs/charts/defi/tvl')
plt.close(fig)

print(pct.iloc[-1].round(1).to_string())
print('range:', pct.index[0].date(), '->', pct.index[-1].date())
