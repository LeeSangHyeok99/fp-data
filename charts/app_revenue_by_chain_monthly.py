"""
App Revenue by Chain, monthly stacked bar (Nov 2024 ~ Aug 2026).
소스: DefiLlama api.llama.fi/overview/fees/{chain}?dataType=dailyRevenue (전 체인, 월 합산).
표시: Solana, Hyperliquid L1, Ethereum, BSC, Polygon, Base + Others(나머지 전 체인 합).
캐시: outputs/data/defillama_revenue_by_chain_monthly_all.csv
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, save_chart, setup_font, gradient_rounded_bar, DPI  # noqa: E402

setup_font()
ORDER = [  # 스택 아래 -> 위, 브랜드 색
    ('Ethereum', '#627EEA'), ('Solana', '#8247E5'), ('Hyperliquid L1', '#97FCE4'),
    ('BSC', '#F0B90B'), ('Polygon', '#E5195B'), ('Base', '#0052FF'), ('Others', '#777B80'),
]

df = pd.read_csv('outputs/data/defillama_revenue_by_chain_monthly_all.csv', index_col=0, parse_dates=True) / 1e6
main = [n for n, _ in ORDER if n != 'Others']
df['Others'] = df.drop(columns=main).sum(axis=1)
df = df[[n for n, _ in ORDER]]
df.to_csv('outputs/data/defillama_app_revenue_by_chain_monthly.csv')

fig, ax = plt.subplots(figsize=(10.67, 3.9), dpi=DPI)
x = mdates.date2num(df.index)
bottom = np.zeros(len(df))
for name, color in ORDER:
    for xi, b, v in zip(x, bottom, df[name].values):
        gradient_rounded_bar(ax, x_center=xi, width=20, height=b + v, color=color,
                             floor=0.72, round_top=False, y0=b)
    bottom += df[name].values

ax.set_xlim(x[0] - 16, x[-1] + 16)
ax.set_yticks([0, 250, 500, 750, 1000])
ax.set_yticklabels(['$0M', '$250M', '$500M', '$750M', '$1,000M'])
ax.set_ylim(0, 1000)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=13)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

png, svg = save_chart(fig, 'app_revenue_by_chain_monthly', 'outputs/charts/blockchains/revenue')
plt.close(fig)
last = df.iloc[-1]; print(png, df.index[-1].date(), last.round(1).to_dict(), 'total', round(last.sum(), 1))
