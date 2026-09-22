import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, gradient_rounded_bar, save_chart

# =============================================================================
# Data: 국내 5대 원화거래소 알트코인 신규상장 대비 거래종료 비율
#   2022 ~ 2026년 7월 (빗썸은 8/18까지)
#   매거진한경 (박성훈 의원 제출자료), 2026-08-31
# =============================================================================
df = pd.read_csv('outputs/data/korea_cex_delisting_ratio.csv')
ratio = df['delist_ratio'] * 100
x = range(len(df))

# 거래소 브랜드 컬러 (charts/korea_cex_stablecoin_share.py와 동일)
COLORS = {'Gopax': '#787b86', 'Coinone': '#3ecf8e', 'Bithumb': '#ff8a1e',
          'Korbit': '#1e9bff', 'Upbit': '#1f47b3'}

fig, ax = create_figure('bar')

ax.set_yticks([0, 20, 40, 60])
ax.set_yticklabels(['0%', '20%', '40%', '60%'])
ax.set_ylim(0, 72)

ax.set_xticks(list(x))
ax.set_xticklabels(df['exchange_en'])
ax.set_xlim(-0.6, len(df) - 0.4)

for i, r in df.iterrows():
    v = r['delist_ratio'] * 100
    gradient_rounded_bar(ax, i, 0.55, v, COLORS[r['exchange_en']],
                         round_top=False, floor=0.62)
    ax.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom',
            fontsize=15, fontweight='bold', color='#d1d4dc', zorder=6)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=18)
ax.tick_params(axis='x', labelsize=17, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

png, svg = save_chart(fig, 'korea_cex_delisting_ratio',
                      'outputs/charts/korea_cex/listing')
plt.close(fig)
print(png)
