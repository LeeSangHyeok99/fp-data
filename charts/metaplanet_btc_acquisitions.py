"""
Metaplanet BTC Acquisitions (price line + purchase bubbles)
소스: StrategyTracker (data.strategytracker.com, ticker 3350.T), 실데이터.
BTC 가격 라인 위에 매입 이벤트를 매입량 비례 버블 + 글로우로 표시.
four-pillars dark theme, 투명 배경.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
TEXT2 = COLORS['text_secondary']
ORANGE = '#f7931a'   # Bitcoin 브랜드 오렌지

price = pd.read_csv('outputs/data/metaplanet_btc_price_line.csv', parse_dates=['date'])
buys = pd.read_csv('outputs/data/metaplanet_btc_acquisitions.csv', parse_dates=['date'])
buys = buys.dropna(subset=['price'])

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

# BTC 가격 라인
ax.plot(price['date'], price['price'], color=ORANGE, linewidth=1.3, zorder=3)

# 매입 버블: 매입량(BTC) 비례 크기. 면적 ∝ btc → s ∝ btc
core_s = buys['btc_bought'] * 0.34
# 글로우 (큰 + 흐린 오렌지 헤일로 2겹)
ax.scatter(buys['date'], buys['price'], s=core_s * 9, color=ORANGE,
           alpha=0.10, edgecolors='none', zorder=4)
ax.scatter(buys['date'], buys['price'], s=core_s * 4, color=ORANGE,
           alpha=0.16, edgecolors='none', zorder=4)
# 코어 도트: 오렌지 채움 + 흰 링
ax.scatter(buys['date'], buys['price'], s=core_s, color=ORANGE,
           edgecolors='white', linewidths=1.3, zorder=6)

# x축: Mon YYYY, 최대 5개
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(price['date'].iloc[0], price['date'].iloc[-1])
ax.tick_params(axis='x', colors=TEXT2, labelsize=12, length=6, width=1.2, pad=8)

# y축: 가격, 깔끔한 틱 ($60k ~ $120k)
ax.set_ylim(50000, 130000)
ax.set_yticks([60000, 80000, 100000, 120000])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:,.0f}k"))
ax.tick_params(axis='y', colors=TEXT2, labelsize=12, length=0, pad=8)
ax.grid(True, axis='y', color=TEXT2, alpha=0.16, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.07, right=0.99, top=0.97, bottom=0.10)

png, svg = save_chart(fig, 'metaplanet_btc_acquisitions', output_dir='outputs/charts/strategy/treasury')
print('saved:', png)
print(f"purchases {len(buys)}, biggest {buys['btc_bought'].max():.0f} BTC, total {buys['btc_bought'].sum():.0f} BTC")
