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
# Data: rwa.xyz Ondo Metrics > Total Value (CSV export, Bridged Token Value)
# =============================================================================
SRC = 'sources/rwa-token-timeseries-export-1787813788463.csv'
raw = pd.read_csv(SRC)
df = raw.set_index(pd.to_datetime(raw['Date']))[raw.columns[3:]].fillna(0.0)
df = df.loc['2024-01-01':]

TOP_N = 5
rank = df.iloc[-1].sort_values(ascending=False)
top = list(rank.head(TOP_N).index)

# 13밴드는 같은 색조 안에서 구분이 안 돼서 상위 5개 + Others로 줄였다.
# 쌓기 순서는 레퍼런스와 동일(작은 시리즈가 바닥, 가장 큰 USDY가 맨 위).
stack = pd.DataFrame(index=df.index)
stack['Others'] = df.drop(columns=top).sum(axis=1) / 1e9
for c in reversed(top):
    stack[c] = df[c] / 1e9

BRAND = {
    # Ondo 실제 브랜드는 흑백이지만, 다크 배경에서 회색 범벅이 돼서 블루 톤으로 간다.
    'Ondo U.S. Dollar Yield': '#2a5bff',
    'Ondo Short-Term US Government Bond Fund': '#8aa6ff',
    'Circle Internet Group (Ondo Tokenized)': '#2775ca',       # Circle
    'iShares Core S&P 500 ETF (Ondo Tokenized)': '#b9c0c8',    # iShares 블랙 -> 라이트 그레이
    'SPDR S&P 500 ETF (Ondo Tokenized)': '#c8102e',            # SPDR 레드
    'Others': '#4a5060',
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
ax.set_ylim(0, 5)
ax.set_yticks([0, 1, 2, 3, 4, 5])

ax.xaxis.set_major_locator(MonthLocator(bymonth=[1, 7]))
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

out = 'outputs/charts/ondo/rwa'
Path(out).mkdir(parents=True, exist_ok=True)
name = 'ondo_distributed_asset_composition'
fig.savefig(f'{out}/{name}.png', dpi=DPI, bbox_inches='tight', transparent=True)
fig.savefig(f'{out}/{name}.svg', format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

stack.round(6).to_csv('outputs/data/ondo_distributed_asset_composition.csv')

total = stack.sum(axis=1)
print(f"Saved: {out}/{name}.png")
print(f"Range: {stack.index.min().date()} ~ {stack.index.max().date()}")
print(f"Latest total: ${total.iloc[-1]:.2f}B | peak ${total.max():.2f}B ({total.idxmax().date()})")
print(f"YoY: ${total.loc[:total.index[-1] - pd.Timedelta(days=365)].iloc[-1]:.2f}B -> ${total.iloc[-1]:.2f}B")
for c in stack.columns:
    print(f"  {c:55s} ${stack[c].iloc[-1]*1000:7.1f}M  {stack[c].iloc[-1]/total.iloc[-1]*100:5.1f}%")
