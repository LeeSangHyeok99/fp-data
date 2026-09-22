import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, gradient_rounded_bar, save_chart

# =============================================================================
# Data: Coinbase net revenue split (transaction vs subscription & services)
#   Q4'24~Q4'25  = Coinbase Q4'25 shareholder letter (as-reported basis)
#   Q1'26~Q2'26  = Coinbase 10-Q filed 2026-07-30 (coin-20260630)
# =============================================================================
df = pd.read_csv('outputs/data/coinbase_revenue_mix.csv')
x = range(len(df))

COLOR_TX = '#0052FF'   # Coinbase 브랜드 블루 (거래수수료)
COLOR_SUB = '#fc8452'  # 구독·서비스

fig, ax = create_figure('stacked_bar')

ax.set_yticks([0, 500, 1000, 1500, 2000])
ax.set_yticklabels(['$0M', '$500M', '$1,000M', '$1,500M', '$2,000M'])
ax.set_ylim(0, 2350)

ax.set_xticks(list(x))
ax.set_xticklabels(df['quarter'])
ax.set_xlim(-0.6, len(df) - 0.4)

# 스택 세그먼트: 평평한 마감, 각 세그먼트 구간에만 얕은 그라데이션
for i, r in df.iterrows():
    tx, sub = r['transaction_rev_musd'], r['subscription_rev_musd']
    gradient_rounded_bar(ax, i, 0.6, tx, COLOR_TX, round_top=False, floor=0.62)
    gradient_rounded_bar(ax, i, 0.6, tx + sub, COLOR_SUB, y0=tx,
                         round_top=False, floor=0.62)

# 세그먼트 값 라벨 (막대 안 중앙)
for i, r in df.iterrows():
    ax.text(i, r['transaction_rev_musd'] / 2, f"${r['transaction_rev_musd']:,.0f}M",
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#ffffff', zorder=5)
    ax.text(i, r['transaction_rev_musd'] + r['subscription_rev_musd'] / 2,
            f"${r['subscription_rev_musd']:,.0f}M",
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#141414', zorder=5)

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14, rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

png, svg = save_chart(fig, 'coinbase_revenue_stack',
                      'outputs/charts/coinbase/revenue')
plt.close(fig)
print(png)
