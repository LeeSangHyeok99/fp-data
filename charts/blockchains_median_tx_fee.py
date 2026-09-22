"""
Blockchains: Median Transaction Fee, monthly (mean of daily medians), log scale.
소스: Blockworks Analytics (studio visualization 8251, chain-compare-overview).
선택 네트워크만: Solana, Ethereum, Base, Arbitrum, Bitcoin, BNB Chain, Monad. 색은 Blockworks color_code.
캐시: outputs/data/blockworks_median_tx_fee_raw.csv (일별 전체).
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, DPI  # noqa: E402

setup_font()
API = ('https://blockworks.com/api/studio/dashboard/chain-compare-overview'
       '/visualization/8251/execution?limit=50000&page=1')
CACHE = 'outputs/data/blockworks_median_tx_fee_raw.csv'
CHAINS = {  # 이름 -> Blockworks 색 (레퍼런스 범례 순서)
    'Solana': '#92DC78', 'Ethereum': '#6487DE', 'Base': '#1B54E3', 'Arbitrum': '#78C1DB',
    'Bitcoin': '#F7931A', 'BNB Chain': '#DDC32C', 'Monad': '#6E54FF',
}
START, END = '2021-01-01', '2026-08-01'   # 마지막 완전한 달까지

try:
    rows = requests.get(API, timeout=90, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}).json()['data']
    pd.DataFrame(rows).to_csv(CACHE, index=False)
except Exception as exc:
    print(f'API fetch failed ({exc}), using {CACHE}')

df = pd.read_csv(CACHE, parse_dates=['date'])
df = df[df['title'].isin(CHAINS)].copy()
df['month'] = df['date'].dt.tz_localize(None).dt.to_period('M').dt.to_timestamp()
m = df.groupby(['month', 'title'])['median_fee_usd'].mean().unstack('title').loc[START:END]
m.to_csv('outputs/data/blockchains_median_tx_fee_monthly.csv')

fig, ax = plt.subplots(figsize=(10.67, 3.9), dpi=DPI)
for name, color in CHAINS.items():
    s = m[name].dropna()
    ax.plot(s.index, s.values, color=color, linewidth=1.8, zorder=3)

ax.set_yscale('log')
ax.set_ylim(3e-6, 60)
ax.set_yticks([10, 0.1, 0.001, 0.00001])
ax.set_yticklabels(['$10', '$0.1', '$0.001', '$0.00001'])
ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_xlim(m.index.min(), m.index.max())
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

png, svg = save_chart(fig, 'blockchains_median_tx_fee', 'outputs/charts/blockchains/fees')
plt.close(fig)
print(png, m.index.max().date(), m.iloc[-1].round(5).to_dict())
