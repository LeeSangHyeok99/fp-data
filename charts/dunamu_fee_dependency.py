import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, endpoint_dot, save_chart

# =============================================================================
# Data: 두나무 매출 중 거래플랫폼 수수료 비중
#   2024/2025 = 블로터(2026-03-30, 금감원 전자공시 기반)
#   2026 1Q/2Q/상반기 = 블로터(2026-08-20), 이투데이(2026-05-15 공시)
#   2026 2Q는 상반기에서 1분기를 뺀 파생값
# =============================================================================
df = pd.read_csv('outputs/data/dunamu_fee_dependency.csv')
share = df['fee_share'] * 100
x = range(len(df))

COLOR = '#4d8dff'  # 업비트 블루

fig, ax = create_figure('line')

ax.plot(x, share, color=COLOR, linewidth=2.8, zorder=4)
ax.scatter(x, share, color=COLOR, s=45, zorder=5, edgecolors='none')
endpoint_dot(ax, len(df) - 1, share.iloc[-1], color=COLOR, size=110)

for i, v in enumerate(share):
    ax.annotate(f'{v:.2f}%', (i, v), textcoords='offset points',
                xytext=(0, 12), ha='center', fontsize=13, fontweight='bold',
                color='#d1d4dc', zorder=6)

ax.set_yticks([96, 97, 98, 99])
ax.set_yticklabels(['96%', '97%', '98%', '99%'])
ax.set_ylim(95.6, 99.4)

ax.set_xticks(list(x))
ax.set_xticklabels(df['period'])
ax.set_xlim(-0.35, len(df) - 0.65)

apply_style(fig, ax, 'line')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14, rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')

png, svg = save_chart(fig, 'dunamu_fee_dependency',
                      'outputs/charts/dunamu/revenue')
plt.close(fig)
print(png)
