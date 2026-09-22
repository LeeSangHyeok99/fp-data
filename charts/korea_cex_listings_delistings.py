import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import GRID_CONFIG, apply_style, create_figure, gradient_barh, save_chart

# =============================================================================
# Data: 국내 5대 원화거래소 알트코인 신규상장 vs 거래종료 건수
#   2022 ~ 2026년 7월 (빗썸은 8/18까지)
#   매거진한경 (박성훈 의원 제출자료), 2026-08-31
# =============================================================================
df = pd.read_csv('outputs/data/korea_cex_delisting_ratio.csv')
y = np.arange(len(df))

COLOR_LIST = '#4d8dff'    # 신규상장
COLOR_DELIST = '#ff8a3d'  # 거래종료
H = 0.28
OFF = 0.20  # 그룹 안은 좁게, 그룹 사이는 넓게

fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(10.67, 5.5)  # 가로 막대 5그룹, 세로로 여유 있게

bars_list = ax.barh(y - OFF, df['listings'], height=H, color=COLOR_LIST, zorder=3)
bars_del = ax.barh(y + OFF, df['delistings'], height=H, color=COLOR_DELIST, zorder=3)
for rect in bars_list:
    gradient_barh(ax, rect, COLOR_LIST)
for rect in bars_del:
    gradient_barh(ax, rect, COLOR_DELIST)

for i, r in df.iterrows():
    ax.text(r['listings'] + 8, i - OFF, f"{r['listings']:,}", va='center',
            ha='left', fontsize=14, fontweight='bold', color='#d1d4dc', zorder=6)
    ax.text(r['delistings'] + 8, i + OFF, f"{r['delistings']:,}", va='center',
            ha='left', fontsize=14, fontweight='bold', color='#d1d4dc', zorder=6)

ax.set_xticks([0, 100, 200, 300, 400])
ax.set_xlim(0, 500)
ax.set_yticks(y)
ax.set_yticklabels(df['exchange_en'])
# gradient_barh(imshow)가 축을 이미지 경계에 맞춰버려서 여백을 되돌린다
# 위아래 여백을 그룹 사이 간격과 같게 맞춘다
PAD = OFF + H / 2 + (1 - 2 * (OFF + H / 2))
ax.set_ylim(-PAD, len(df) - 1 + PAD)

apply_style(fig, ax, 'horizontal_bar')
# 가로 막대는 세로 그리드로 바꾼다
ax.grid(False, axis='y')
ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=17)
ax.tick_params(axis='x', labelsize=16, rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

png, svg = save_chart(fig, 'korea_cex_listings_delistings',
                      'outputs/charts/korea_cex/listing')
plt.close(fig)
print(png)
