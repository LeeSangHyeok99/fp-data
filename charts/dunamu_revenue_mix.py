import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, gradient_rounded_bar, save_chart

# =============================================================================
# Data: 두나무 연간 매출 구성 (거래플랫폼 수수료 vs 기타 사업), 단위 억원
#   블로터 「가상자산시장 한파에…두나무, 2025년 매출·영업익 동반 하락」
#   (2026-03-30, 금감원 전자공시 기반)
# =============================================================================
df = pd.read_csv('outputs/data/dunamu_revenue_mix.csv')
# 억원 -> 십억원(₩B). 축과 라벨 단위를 ₩B로 통일한다
for c in ('platform_fee_100m_krw', 'other_biz_100m_krw'):
    df[c] = df[c] / 10
x = range(len(df))

COLOR_FEE = '#0d3b8f'    # 업비트 네이비 (거래플랫폼 수수료)
COLOR_OTHER = '#fc8452'  # 기타 사업

fig, ax = create_figure('stacked_bar')

ax.set_yticks([0, 500, 1000, 1500])
ax.set_yticklabels(['₩0B', '₩500B', '₩1,000B', '₩1,500B'])
ax.set_ylim(0, 1900)

ax.set_xticks(list(x))
ax.set_xticklabels(df['period'].astype(str))
ax.set_xlim(-0.75, len(df) - 0.25)

for i, r in df.iterrows():
    fee, other = r['platform_fee_100m_krw'], r['other_biz_100m_krw']
    gradient_rounded_bar(ax, i, 0.42, fee, COLOR_FEE, round_top=False, floor=0.62)
    gradient_rounded_bar(ax, i, 0.42, fee + other, COLOR_OTHER, y0=fee,
                         round_top=False, floor=0.62)
    ax.text(i, fee / 2, f'₩{fee:,.0f}B', ha='center', va='center',
            fontsize=15, fontweight='bold', color='#ffffff', zorder=6)
    ax.text(i, fee + other + 42, f'₩{other:,.0f}B', ha='center', va='bottom',
            fontsize=14, fontweight='bold', color=COLOR_OTHER, zorder=6)

apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=17)
ax.tick_params(axis='x', labelsize=17, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

png, svg = save_chart(fig, 'dunamu_revenue_mix',
                      'outputs/charts/dunamu/revenue')
plt.close(fig)
print(png)
