import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, band_gradient, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Data: rwa.xyz Tokenized Stock Metrics > Total Value, grouped by Platform
# =============================================================================
SRC = 'sources/rwa-xyz-stocks-market-caps.csv'
raw = pd.read_csv(SRC)
df = raw.set_index(pd.to_datetime(raw['Date']))[raw.columns[3:]].fillna(0.0)
df = df.loc['2025-09-01':]

TOP_N = 5
rank = df.iloc[-1].sort_values(ascending=False)
top = list(rank.head(TOP_N).index)

# 레퍼런스와 같은 쌓기 순서: 작은 플랫폼이 바닥, 가장 큰 Ondo가 맨 위.
stack = pd.DataFrame(index=df.index)
stack['Others'] = df.drop(columns=top).sum(axis=1) / 1e9
for c in reversed(top):
    stack[c] = df[c] / 1e9

BRAND = {
    'Ondo': '#d7d7db',                       # Ondo 모노크롬 -> 라이트
    'Backed Finance (xStocks)': '#00c39a',   # xStocks 틸 (미검증)
    'bStocks': '#f0b90b',                    # Binance 옐로우
    'Securitize': '#1e3a8a',                 # Securitize 네이비 (미검증)
    'Figure': '#c8aa55',                     # Figure 골드
    'Others': '#33383f',
}
COLORS_ = [BRAND[c] for c in stack.columns]

# =============================================================================
# Chart
# =============================================================================
fig, ax = create_figure('stacked')
# 밴드마다 브랜드 컬러 -> 밝은 톤 세로 그라데이션
xs = mdates.date2num(stack.index.to_pydatetime())
cum = stack.cumsum(axis=1)
lower = np.zeros(len(stack))
for c in stack.columns:
    upper = cum[c].values
    band_gradient(ax, xs, lower, upper, BRAND[c])
    lower = upper

# 밴드 사이 구분선. 맨 위 경계는 안 그린다(1일짜리 스파이크가 선에 먹힌다).
for c in list(stack.columns)[:-1]:
    ax.plot(stack.index, cum[c].values, color='#141414', linewidth=0.8, zorder=3)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))
ax.set_ylim(0, 3)
ax.set_yticks([0, 1, 2, 3])

ax.xaxis.set_major_locator(MonthLocator(bymonth=[9, 11, 1, 3, 5, 7]))
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
ax.set_xlim(stack.index.min(), stack.index.max())

apply_style(fig, ax, 'stacked')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

out = 'outputs/charts/rwa/stocks'
Path(out).mkdir(parents=True, exist_ok=True)
name = 'tokenized_stock_platform_composition'
fig.savefig(f'{out}/{name}.png', dpi=DPI, bbox_inches='tight', transparent=True)
fig.savefig(f'{out}/{name}.svg', format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

stack.round(6).to_csv('outputs/data/tokenized_stock_platform_composition.csv')

total = stack.sum(axis=1)
print(f"Saved: {out}/{name}.png")
print(f"Range: {stack.index.min().date()} ~ {stack.index.max().date()}")
print(f"Latest total: ${total.iloc[-1]*1000:.0f}M | peak ${total.max()*1000:.0f}M ({total.idxmax().date()})")
print(f"Ondo peak: ${stack['Ondo'].max()*1000:.0f}M ({stack['Ondo'].idxmax().date()})")
for c in stack.columns[::-1]:
    print(f"  {c:26s} ${stack[c].iloc[-1]*1000:7.1f}M  {stack[c].iloc[-1]/total.iloc[-1]*100:5.1f}%  {COLORS_[list(stack.columns).index(c)]}")
