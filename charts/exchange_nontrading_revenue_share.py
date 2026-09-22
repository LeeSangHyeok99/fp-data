"""거래 수수료 밖에서 버는 돈: 두나무 vs 코인베이스 (2026년 상반기)

두 값 모두 기존 소스 CSV에서 파생시킨다(하드코딩 금지).
  두나무   = 1 - 거래플랫폼 수수료 비중 (2026 H1, 반기보고서)
  코인베이스 = (Q1+Q2 구독·서비스 매출) / (Q1+Q2 순매출) (10-Q, 2026-07-30 제출)
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, gradient_rounded_bar, save_chart

# ── Data ─────────────────────────────────────────────────────────────────
du = pd.read_csv('outputs/data/dunamu_fee_dependency.csv')
dunamu = (1 - du.loc[du['period'] == '2026 H1', 'fee_share'].iloc[0]) * 100

cb = pd.read_csv('outputs/data/coinbase_revenue_mix.csv')
h1 = cb[cb['quarter'].str.startswith('2026')]
coinbase = h1['subscription_rev_musd'].sum() / h1['net_revenue_musd'].sum() * 100

assert round(dunamu, 1) == 3.1, dunamu
assert round(coinbase, 1) == 45.7, coinbase

labels = ['Dunamu', 'Coinbase']
values = [dunamu, coinbase]
colors = ['#4d8dff', '#0052FF']  # 업비트 블루 / 코인베이스 블루

# ── Chart ────────────────────────────────────────────────────────────────
fig, ax = create_figure('bar')
fig.set_size_inches(8.6, 4.67)

ax.set_xlim(-0.6, 1.6)
ax.set_ylim(0, 53)
ax.set_yticks([0, 20, 40])
ax.set_yticklabels(['0%', '20%', '40%'])
ax.set_xticks([0, 1])
ax.set_xticklabels(labels)

for i, (v, c) in enumerate(zip(values, colors)):
    gradient_rounded_bar(ax, x_center=i, width=0.36, height=v, color=c,
                         round_top=False, floor=0.62)
    ax.annotate(f'{v:.1f}%', (i, v), textcoords='offset points', xytext=(0, 14),
                ha='center', fontsize=20, fontweight='bold',
                color='#d1d4dc', zorder=6)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=18)
ax.tick_params(axis='x', labelsize=18, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

png, svg = save_chart(fig, 'exchange_nontrading_revenue_share',
                      'outputs/charts/korea-cex/revenue')
plt.close(fig)
print(png)
print(svg)
