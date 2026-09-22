"""
Daily transaction count across major blockchains (Artemis export).
소스: Artemis Chain Transactions CSV (사용자 제공, outputs/data/artemis_chain_transactions_daily.csv).
6개 체인 모두 유지 (레퍼런스 그대로). 투명 배경, 인포그래픽 슬롯 비율.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, DPI  # noqa: E402

setup_font()
COLORS = {  # 레퍼런스(Artemis) 색 구성
    'Solana': '#22A05B', 'Base': '#1D4ED8', 'Tron': '#E11D2E',
    'Sui': '#60A5FA', 'Ethereum': '#8B93B8', 'Avalanche C-Chain': '#F0716B',
}

df = pd.read_csv('outputs/data/artemis_chain_transactions_daily.csv', encoding='utf-8-sig',
                 parse_dates=['DateTime']).set_index('DateTime').dropna(how='all') / 1e6
df = df.rolling(7, min_periods=1).mean().loc['2022-01-01':]   # 7일 이동평균 스무딩, 2022년부터

fig, ax = plt.subplots(figsize=(10.67, 3.9), dpi=DPI)
for name in reversed(list(COLORS)):
    s = df[name].dropna()
    ax.plot(s.index, s.values, color=COLORS[name], linewidth=1.1, zorder=3)

ax.set_yticks([0, 50, 100, 150, 200])
ax.set_yticklabels(['0M', '50M', '100M', '150M', '200M'])
ax.set_ylim(0, 225)
ax.set_xlim(df.index.min(), df.index.max())
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

png, svg = save_chart(fig, 'chain_transactions_daily', 'outputs/charts/blockchains/transactions')
plt.close(fig)
print(png, df.index.max().date(), df.iloc[-1].round(1).to_dict())
