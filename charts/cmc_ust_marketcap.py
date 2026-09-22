"""Terra UST (USTC) market cap, full history. Source: CoinMarketCap chart API."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import requests
import sys
from datetime import datetime, timezone

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, AXIS_CONFIG

COLOR = '#3b6ef6'
CMC_ID = 7129  # TerraClassicUSD (USTC)

r = requests.get('https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart',
                 params={'id': CMC_ID, 'range': 'ALL'},
                 headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'},
                 timeout=90).json()
pts = r['data']['points']
mcap = pd.Series({datetime.fromtimestamp(int(t), timezone.utc).replace(tzinfo=None): v['v'][2]
                  for t, v in pts.items()}).sort_index()
mcap.rename('ust_market_cap_usd').to_csv('outputs/data/ust_market_cap.csv')

y = mcap / 1e9
fig, ax = create_figure('line')
ax.plot(mcap.index, y, color=COLOR, linewidth=1.8)

ax.set_ylim(0, 20)
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels([f'${v}B' for v in [0, 5, 10, 15, 20]])
ax.set_xlim(mcap.index[0], mcap.index[-1])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 6)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 6)
fig.tight_layout()
save_chart(fig, 'ust_market_cap', 'outputs/charts/terra/stablecoin')
plt.close(fig)

peak = mcap.idxmax()
print(f'range: {mcap.index[0].date()} -> {mcap.index[-1].date()}  ({len(mcap)} pts)')
print(f'peak: ${mcap.max()/1e9:.2f}B on {peak.date()}')
print(f'latest: ${mcap.iloc[-1]/1e6:.2f}M')
