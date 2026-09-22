"""
Depositors vs. Deposit per Depositor (dual-axis bar + line) - four-pillars 내재화
소스: Dune Analytics (Solana), 레퍼런스 이미지 디지타이즈. Jun 2026 ~23일까지.
좌축: unique depositors (바, 시안), 우축: USDC per depositor (라인, 코랄).
four-pillars dark theme, 투명 배경.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI  # noqa: E402


def grad_bar(ax, xc, w, h, color):
    """바를 세로 그라데이션(아래 어둡게 → 위 밝게)으로 채운다."""
    if h <= 0:
        return
    x_left, x_right = xc - w / 2, xc + w / 2
    r, g, b = mcolors.to_rgb(color)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        f = 0.72 + 0.40 * (i / 255)
        grad[i, 0] = [min(r * f, 1), min(g * f, 1), min(b * f, 1), 1.0]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, h], zorder=3,
                   interpolation='bilinear')
    clip = Rectangle((x_left, 0), w, h, transform=ax.transData,
                     facecolor='none', edgecolor='none')
    ax.add_patch(clip)
    im.set_clip_path(clip)

setup_font()
# SVG에서 텍스트를 path가 아닌 편집 가능한 <text> 요소로 출력
plt.rcParams['svg.fonttype'] = 'none'

df = pd.read_csv('outputs/data/depositors_vs_spend.csv')
df['date'] = pd.to_datetime(df['month'])

BAR_COLOR = '#4ea3c4'   # 시안 (depositors)
LINE_COLOR = '#e8726b'  # 코랄 (usdc per depositor)

OUTPUT_DIR = 'outputs/charts/solana/deposits'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(11.5, 5.4), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))

# 바 (좌축, depositors). 라벨은 바 안쪽 상단에 흰색으로 넣어 라인과 겹침 방지
for xi, v in zip(x, df['depositors']):
    grad_bar(ax, xi, 0.56, v, BAR_COLOR)
ax.set_xlim(-0.6, len(df) - 0.4)  # imshow autoscale 방지용 선설정
for xi, v in zip(x, df['depositors']):
    ax.text(xi, v - 230, f'{v:,.0f}', ha='center', va='top',
            fontsize=9.5, fontweight='bold', color='#ffffff', zorder=6)

ax.set_ylim(0, 6600)
ax.set_yticks([0, 2000, 4000, 6000])
ax.set_yticklabels(['0', '2,000', '4,000', '6,000'], fontsize=12,
                   fontweight='bold', color=BAR_COLOR)

# 라인 (우축, usdc per depositor)
ax2 = ax.twinx()
ax2.set_facecolor('none')
ax2.plot(x, df['usdc_per_depositor'], color=LINE_COLOR, linewidth=2.4,
         marker='o', markersize=6, markerfacecolor=LINE_COLOR,
         markeredgecolor='none', zorder=5)
# 라인 라벨: 항상 마커 위. 단 바 상단과 가까우면(마커가 바 꼭대기 근처면)
# 바 위쪽으로 밀어 올려 흰색 바 라벨과 겹치지 않게 한다.
vals = df['usdc_per_depositor'].values
scale = 33000 / 6600  # 우축/좌축 비율
for i, (xi, v) in enumerate(zip(x, vals)):
    bar_top_right = df['depositors'].iloc[i] * scale
    if 0 < bar_top_right - v < 3500:
        label_y = bar_top_right + 1200
    else:
        label_y = v + 1200
    ax2.text(xi, label_y, f'${v/1000:.1f}k', ha='center', va='bottom',
             fontsize=9.5, fontweight='bold', color=LINE_COLOR, zorder=6)

ax2.set_ylim(0, 33000)
ax2.set_yticks([0, 10000, 20000, 30000])
ax2.set_yticklabels(['$0k', '$10k', '$20k', '$30k'], fontsize=12,
                    fontweight='bold', color=LINE_COLOR)

# +3.7x 콜아웃
ax2.text(4, 31500, 'Spend Per Depositor +3.7× From October To June',
         ha='center', va='center', fontsize=10.5, fontweight='bold',
         color=LINE_COLOR, zorder=7)

# X축
ax.set_xticks(x)
ax.set_xticklabels([d.strftime("%b '%y") for d in df['date']],
                   fontsize=11, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.set_xlim(-0.6, len(df) - 0.4)

# 그리드/스파인
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='both', length=0)
ax2.tick_params(axis='both', length=0)

# 하단 인라인 범례
ax.scatter([], [])
leg_y = -0.12
ax.add_patch(plt.Rectangle((0.0, leg_y - 0.012), 0.016, 0.024,
             transform=ax.transAxes, facecolor=BAR_COLOR, edgecolor='none',
             clip_on=False, zorder=5))
ax.text(0.024, leg_y, 'unique depositors (left)', transform=ax.transAxes,
        ha='left', va='center', fontsize=10, fontweight='bold',
        color=COLORS['text_secondary'])
ax.plot([0.72, 0.745], [leg_y, leg_y], transform=ax.transAxes,
        color=LINE_COLOR, linewidth=2.2, clip_on=False, zorder=5)
ax.scatter([0.7325], [leg_y], transform=ax.transAxes, s=34, color=LINE_COLOR,
           clip_on=False, zorder=6)
ax.text(0.76, leg_y, 'USDC per depositor (right)', transform=ax.transAxes,
        ha='left', va='center', fontsize=10, fontweight='bold',
        color=COLORS['text_secondary'])

fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(f'{OUTPUT_DIR}/depositors_vs_spend.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True, format=fmt if fmt == 'svg' else None)
plt.close()

print('Done: depositors_vs_spend')
print(f"  ratio Jun/Oct = {df['usdc_per_depositor'].iloc[-1]/df['usdc_per_depositor'].iloc[0]:.2f}x")
