"""
Lido / Ethereum Consensus Layer client distribution (two donuts)
소스: Hex dashboard (Lido on Ethereum Validator Node metrics), 실데이터.
좌: Across Ethereum, 우: Across Lido Curated Module.
four-pillars dark theme, 투명 배경.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
BG = COLORS['background']
TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']

df = pd.read_csv('outputs/data/lido_consensus_clients.csv')

# 이미지 색 구성 재현 (클라이언트별)
COLOR = {
    'Lighthouse': '#3b82f6',  # 블루
    'Prysm':      '#f0897e',  # 살몬
    'Teku':       '#f5c518',  # 옐로우
    'Caplin':     '#ff8c1a',  # 오렌지 (Erigon)
    'Lodestar':   '#9b1fa8',  # 퍼플
    'Other':      '#1aa39a',  # 틸
    'Vouch':      '#c9b3e6',  # 라벤더
    'Nimbus':     '#d6a9e6',  # 라이트 퍼플
    'Grandine':   '#3cb44b',  # 그린
}
# Lido 차트의 작은 슬라이스 Caplin은 다크그린으로 (이미지의 짙은 녹색)
COLOR_LIDO_OVERRIDE = {'Caplin': '#2a8c3a'}


def draw_donut(ax, sub, sublabel, color_override=None):
    color_override = color_override or {}
    d = df[df['chart'] == sub].reset_index(drop=True)
    vals = d['pct'].values
    cols = [color_override.get(c, COLOR[c]) for c in d['client']]
    wedges, _ = ax.pie(
        vals, colors=cols, startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor=BG, linewidth=2.2))
    for w, client, v in zip(wedges, d['client'], vals):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x, y = np.cos(ang), np.sin(ang)
        # 클라이언트명: 링 바깥
        ha = 'left' if x >= 0 else 'right'
        ax.text(1.16 * x, 1.16 * y, client, ha=ha, va='center',
                fontsize=11, fontweight='bold', color=TEXT, zorder=5)
        # 퍼센트: 큰 슬라이스는 링 안(흰색), 작은 슬라이스는 이름 아래
        if v >= 4:
            ax.text(0.79 * x, 0.79 * y, f'{v:.2f}%', ha='center', va='center',
                    fontsize=9.5, fontweight='bold', color='#ffffff', zorder=5)
        else:
            ax.text(1.16 * x, 1.16 * y - 0.11, f'{v:.2f}%', ha=ha, va='center',
                    fontsize=9, fontweight='bold', color=TEXT2, zorder=5)
    ax.set_title(sublabel, fontsize=13, fontweight='bold', color=TEXT2, pad=14)
    ax.set(aspect='equal')


fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.2), dpi=150)
fig.patch.set_alpha(0)
for a in axes:
    a.set_facecolor('none')

draw_donut(axes[0], 'Ethereum', 'Across Ethereum')
draw_donut(axes[1], 'Lido', 'Across Lido Curated Module',
           color_override=COLOR_LIDO_OVERRIDE)

fig.subplots_adjust(left=0.04, right=0.96, top=0.92, bottom=0.04, wspace=0.30)

png, svg = save_chart(fig, 'lido_consensus_clients', output_dir='outputs/charts/lido/clients')
print('saved:', png)
