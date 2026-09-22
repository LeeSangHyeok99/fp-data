"""
Pack-Tier Mix as a Share of Monthly GMV (100% stacked bar) - four-pillars 내재화
소스: Blockworks Research (레퍼런스 이미지 디지타이즈).
각 월 100% 정규화. 라벨은 레퍼런스와 동일하게 $250/$1,000/$2,500 티어에만 표기.
$25/$50(그레이), Other(다크)는 월 합이 100%가 되도록 복원.
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


def grad_segment(ax, xc, w, y0, h, color, bar_w=0.74):
    """세그먼트를 세로 그라데이션(아래 어둡게 → 위 밝게)으로 채운다."""
    if h <= 0:
        return
    x_left, x_right = xc - bar_w / 2, xc + bar_w / 2
    r, g, b = mcolors.to_rgb(color)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        f = 0.72 + 0.40 * (i / 255)  # 아래 0.72배 → 위 1.12배(살짝 밝게)
        grad[i, 0] = [min(r * f, 1), min(g * f, 1), min(b * f, 1), 1.0]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, y0, y0 + h], zorder=3,
                   interpolation='bilinear')
    clip = Rectangle((x_left, y0), bar_w, h, transform=ax.transData,
                     facecolor='none', edgecolor='none')
    ax.add_patch(clip)
    im.set_clip_path(clip)

setup_font()

df = pd.read_csv('outputs/data/cc_pack_tier_share.csv')
df['date'] = pd.to_datetime(df['month'])

# 스택 순서(아래→위)와 라벨 표기 대상
TIERS = ['p25', 'p50', 'p250', 'p1000', 'p2500', 'other']
TIER_COLORS = {
    'p25':   '#8a9097',  # 그레이
    'p50':   '#5b626b',  # 슬레이트 그레이
    'p250':  '#4cc6dd',  # 시안
    'p1000': '#6d6ce0',  # 퍼플-블루
    'p2500': '#ec6a5e',  # 코랄 레드
    'other': '#3a3e45',  # 다크 그레이 (배경 #141414 위에서도 보이게)
}
TIER_LABELS = {
    'p25': '$25', 'p50': '$50', 'p250': '$250',
    'p1000': '$1,000', 'p2500': '$2,500', 'other': 'Other',
}
LABEL_TIERS = ['p250', 'p1000', 'p2500']  # 세그먼트 안에 수치 표기할 티어

OUTPUT_DIR = 'outputs/charts/collector_crypt/gmv'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(11.5, 5.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(df))
bottom = np.zeros(len(df))
BAR_W = 0.74
for tier in TIERS:
    vals = df[tier].values
    for xi, b, v in zip(x, bottom, vals):
        grad_segment(ax, xi, BAR_W, b, v, TIER_COLORS[tier], bar_w=BAR_W)
    # 라벨 표기 (세그먼트 중앙)
    if tier in LABEL_TIERS:
        for xi, b, v in zip(x, bottom, vals):
            if v >= 6:
                ax.text(xi, b + v / 2, f'{v:.1f}', ha='center', va='center',
                        fontsize=10.5, fontweight='bold', color='#ffffff',
                        zorder=6)
    bottom += vals

# Y축 (퍼센트)
yticks = [0, 25, 50, 75, 100]
ax.set_yticks(yticks)
ax.set_yticklabels([f'{t}%' for t in yticks], fontsize=12,
                   fontweight='bold', color=COLORS['text_secondary'])
ax.set_ylim(0, 102)

ax.set_xticks(x)
ax.set_xticklabels([d.strftime('%b %Y') for d in df['date']],
                   fontsize=11, fontweight='bold',
                   color=COLORS['text_secondary'])
ax.set_xlim(-0.7, len(df) - 0.3)

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='both', length=0)

# 범례 (우측, 레퍼런스 순서: Other → $25 위에서 아래로)
legend_order = ['other', 'p2500', 'p1000', 'p250', 'p50', 'p25']
y0, dy = 0.93, 0.085
for i, tier in enumerate(legend_order):
    y = y0 - i * dy
    ax.add_patch(plt.Rectangle((1.025, y - 0.018), 0.022, 0.036,
                 transform=ax.transAxes, facecolor=TIER_COLORS[tier],
                 edgecolor='none', clip_on=False, zorder=5))
    ax.text(1.06, y, TIER_LABELS[tier], transform=ax.transAxes,
            ha='left', va='center', fontsize=10.5, fontweight='bold',
            color=COLORS['text_secondary'])

fig.tight_layout()
for fmt in ['png', 'svg']:
    fig.savefig(f'{OUTPUT_DIR}/cc_pack_tier_share.{fmt}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True, format=fmt if fmt == 'svg' else None)
plt.close()

print('Done: cc_pack_tier_share')
for _, r in df.iterrows():
    s = r['p25'] + r['p50'] + r['p250'] + r['p1000'] + r['p2500'] + r['other']
    print(f"  {r['month']}: sum={s:.1f}%")
