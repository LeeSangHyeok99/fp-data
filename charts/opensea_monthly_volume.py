"""OpenSea monthly NFT marketplace volume.

Data: CSV exported from Dune query 3469 (@rchen8 OpenSea dashboard).
Refresh by re-downloading the CSV from dune.com/queries/3469.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import sys
from datetime import timedelta

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, AXIS_CONFIG

COLOR = '#2081e2'  # OpenSea brand blue

SRC = 'sources/OpenSea_monthly_volume.csv'
if os.path.exists(SRC):
    raw = pd.read_csv(SRC)
    raw['month'] = pd.to_datetime(raw['month'].str.replace(' UTC', '', regex=False))
    df = raw.pivot(index='month', columns='assetType',
                   values='volumeByAssetType').sort_index().fillna(0.0)
    df.to_csv('outputs/data/opensea_monthly_volume.csv')
else:  # source CSV not kept in repo; fall back to the exported pivot
    df = pd.read_csv('outputs/data/opensea_monthly_volume.csv',
                     index_col='month', parse_dates=True)
nft = (df['NFT Marketplace'] / 1e9).loc['2021-01-01':]

fig, ax = create_figure('bar')
ax.bar(nft.index, nft.values, width=22, color=COLOR, linewidth=0)

ax.set_ylim(0, 5.2)
ax.set_yticks([0, 2, 4])
ax.set_yticklabels(['$0B', '$2B', '$4B'])
ax.set_xlim(nft.index[0] - timedelta(days=20), nft.index[-1] + timedelta(days=20))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6)
fig.tight_layout()
save_chart(fig, 'opensea_monthly_volume', 'outputs/charts/opensea/volume')
plt.close(fig)

print(f'months: {len(nft)}  {nft.index[0].date()} -> {nft.index[-1].date()}')
print(f'peak: ${nft.max():.2f}B on {nft.idxmax().date()}')
print(f'latest: ${nft.iloc[-1]*1000:.1f}M ({nft.index[-1].date()})')
