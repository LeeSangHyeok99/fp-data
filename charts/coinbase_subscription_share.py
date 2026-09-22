import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, endpoint_dot, save_chart

# =============================================================================
# Data: Coinbase subscription & services share of net revenue
#   Q4'24~Q4'25  = Coinbase Q4'25 shareholder letter (as-reported basis)
#   Q1'26~Q2'26  = Coinbase 10-Q filed 2026-07-30 (coin-20260630)
# =============================================================================
df = pd.read_csv('outputs/data/coinbase_revenue_mix.csv')
share = df['subscription_share'] * 100
x = range(len(df))

COLOR = '#0052FF'  # Coinbase 브랜드 블루

fig, ax = create_figure('line')

ax.plot(x, share, color=COLOR, linewidth=2.8, zorder=4)
ax.scatter(x, share, color=COLOR, s=45, zorder=5, edgecolors='none')
endpoint_dot(ax, len(df) - 1, share.iloc[-1], color=COLOR, size=110)

# 포인트 값 라벨 (첫 점만 아래, 나머지는 위)
for i, v in enumerate(share):
    below = i == 0
    ax.annotate(f'{v:.1f}%', (i, v), textcoords='offset points',
                xytext=(0, -22 if below else 12), ha='center',
                fontsize=13, fontweight='bold', color='#d1d4dc', zorder=6)

ax.set_yticks([20, 30, 40, 50])
ax.set_yticklabels(['20%', '30%', '40%', '50%'])
ax.set_ylim(20, 53)

ax.set_xticks(list(x))
ax.set_xticklabels(df['quarter'])
ax.set_xlim(-0.35, len(df) - 0.65)

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14, rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

png, svg = save_chart(fig, 'coinbase_subscription_share',
                      'outputs/charts/coinbase/revenue')
plt.close(fig)
print(png)
