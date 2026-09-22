"""
Cost to mine one bitcoin vs. price, Q2 2026 (four-pillars horizontal bar).
Data: sources/data5_cost_per_btc.csv
Aug 30 price는 소스 CSV 값(77,304)이 9/3 종가라 data8 원본의 8/30 종가 78,232로 교정.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG, gradient_barh

setup_font()

TEAL, ORANGE, RED = '#2c837b', '#cf5e2d', '#a92b24'
PROD_COST, PRICE = 71667, 78232   # Q2 평균 생산가치, 2026-08-30 BTC 종가

items = [
    ('American Bitcoin Self-Mining Cost\n(Company Disclosure)', 36500, TEAL),
    ('MARA Total Power Cost\n(Company Website)', 38690, TEAL),
    ('CleanSpark Power Cost\n(10-Q Calculation)', 44400, TEAL),
    ('Riot Direct Cost\n(Excluding Depreciation)', 49912, TEAL),
    ('Bitcoin Miners Cash Cost Average\n(CoinShares, Q4 2025)', 79995, ORANGE),
    ('Riot All-In Cost\n(Including Depreciation)', 90631, RED),
]
labels, values, colors = zip(*items)
y = np.arange(len(items))

fig, ax = plt.subplots(figsize=(12.4, 5.6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bars = ax.barh(y, values, height=0.62, zorder=3)
for rect, col in zip(bars, colors):
    gradient_barh(ax, rect, col, floor=0.72)
ax.set_ylim(len(items) - 0.5, -0.5)   # imshow가 축을 이미지에 맞추므로 여백 복구

for yi, v in zip(y, values):
    ax.annotate(f'${v:,}', xy=(v, yi), xytext=(10, 0),
                textcoords='offset points', ha='left', va='center',
                fontsize=13, fontweight='bold', color=COLORS['text'], zorder=5)

ax.set_xlim(0, 108000)
ax.set_xticks([0, 20000, 40000, 60000, 80000, 100000])
ax.set_xticklabels([f'${v // 1000}K' for v in (0, 20000, 40000, 60000, 80000, 100000)],
                   fontweight='bold')
# 이름은 밝게, 괄호 안 출처는 회색으로. 한 Text에 두 색을 못 쓰므로 직접 그린다.
ax.set_yticks(y)
ax.set_yticklabels([])
for yi, lab in zip(y, labels):
    name, note = lab.split('\n')
    for txt, col, dy, va in ((name, COLORS['text'], 2, 'bottom'),
                             (note, COLORS['text_secondary'], -2, 'top')):
        ax.annotate(txt, xy=(0, yi), xytext=(-12, dy),
                    textcoords='offset points', ha='right', va=va,
                    fontsize=12, fontweight='bold', color=col,
                    annotation_clip=False)

# 기준선 2개: Q2 평균 생산가치(점선), 8/30 BTC 가격(실선)
ax.axvline(PROD_COST, color=COLORS['text_secondary'], linewidth=1.2,
           linestyle=(0, (5, 3)), zorder=4)
ax.axvline(PRICE, color='#fac858', linewidth=1.6, zorder=4)
# 두 기준선이 가까워서 라벨을 서로 반대쪽으로 붙인다.
for xv, txt, col, ha, dx in (
        (PROD_COST, f'Q2 Avg. Production Cost\n${PROD_COST:,}',
         COLORS['text_secondary'], 'right', -8),
        (PRICE, f'Aug 30 Price\n${PRICE:,}', '#fac858', 'left', 8)):
    ax.annotate(txt, xy=(xv, -0.5), xytext=(dx, 12), textcoords='offset points',
                ha=ha, va='bottom', fontsize=12, fontweight='bold',
                color=col, zorder=6)

ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', length=0, colors=COLORS['text_secondary'],
               labelsize=15, pad=10)
ax.tick_params(axis='y', length=0)

fig.tight_layout()
print(save_chart(fig, 'btc_cost_to_mine_vs_price',
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()
