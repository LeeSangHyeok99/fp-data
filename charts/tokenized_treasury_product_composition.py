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
# Data: rwa.xyz Tokenized Treasury Metrics > Total Value, by product
# =============================================================================
SRC = 'sources/rwa-xyz-treasury-market-caps.csv'
raw = pd.read_csv(SRC)
df = raw.set_index(pd.to_datetime(raw['Date']))[raw.columns[3:]].fillna(0.0)
df = df.loc['2024-01-01':]

# 지정된 6개만 개별 밴드, 나머지 74개는 Others.
# USTB는 rwa.xyz가 "Invesco Short Duration US Government Securities Fund"로
# 이름을 달아둔 Superstate 상품이다 (app.rwa.xyz/assets/USTB).
TOP = {
    'Circle USYC': 'USYC',
    'BlackRock USD Institutional Digital Liquidity Fund': 'BUIDL',
    'Ondo U.S. Dollar Yield': 'USDY',
    'iBENJI': 'iBENJI',
    'Invesco Short Duration US Government Securities Fund': 'USTB',
    'Janus Henderson Treasury Fund': 'JTRSY',
}

# 레퍼런스와 같은 쌓기 순서: 작은 쪽이 바닥, 가장 큰 USYC가 맨 위.
stack = pd.DataFrame(index=df.index)
stack['Others'] = df.drop(columns=list(TOP)).sum(axis=1) / 1e9
order = df[list(TOP)].iloc[-1].sort_values().index          # 작은 것부터
for c in order:
    stack[TOP[c]] = df[c] / 1e9

BRAND = {
    'USYC': '#8656ef',    # Circle 퍼플
    'BUIDL': '#b9c0c8',   # BlackRock 블랙 -> 라이트 그레이
    'USDY': '#262a31',    # Ondo 모노크롬 -> 니어 블랙 (Others 그레이와 분리)
    'iBENJI': '#1446e1',  # Franklin Templeton 블루
    'JTRSY': '#00539b',   # Janus Henderson 블루
    'USTB': '#c59f5e',    # Superstate 골드
    'Others': '#737b89',
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
ax.set_ylim(0, 17.5)
ax.set_yticks([0, 5, 10, 15])

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

out = 'outputs/charts/rwa/treasury'
Path(out).mkdir(parents=True, exist_ok=True)
name = 'tokenized_treasury_product_composition'
fig.savefig(f'{out}/{name}.png', dpi=DPI, bbox_inches='tight', transparent=True)
fig.savefig(f'{out}/{name}.svg', format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

stack.round(6).to_csv('outputs/data/tokenized_treasury_product_composition.csv')

total = stack.sum(axis=1)
print(f"Saved: {out}/{name}.png")
print(f"Range: {stack.index.min().date()} ~ {stack.index.max().date()}")
print(f"Latest total: ${total.iloc[-1]:.2f}B | 2024-01-01 ${total.iloc[0]:.2f}B "
      f"({total.iloc[-1]/total.iloc[0]:.1f}x)")
for c in stack.columns[::-1]:
    i = list(stack.columns).index(c)
    print(f"  {c:8s} {COLORS_[i]}  ${stack[c].iloc[-1]:5.2f}B  {stack[c].iloc[-1]/total.iloc[-1]*100:5.1f}%")
