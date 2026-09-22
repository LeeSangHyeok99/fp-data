import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    COLORS, AXIS_CONFIG
)

# ── Data (extracted from reference image) ──
df = pd.read_csv('outputs/data/eip_new_proposals_by_year.csv')

x = np.arange(len(df))
erc = df['erc'].values
non_erc = df['non_erc_eip'].values

# =============================================================================
# 축 설정 (여기만 수정하면 됨)
# =============================================================================
# Y축
Y_MIN = -12                       # 아래 여백 (라벨 잘림 방지)
Y_MAX = 215                       # 위 여백
Y_TICKS = [0, 50, 100, 150, 200]  # Y축 눈금 (5의 배수, 최대 5개)
Y_FONTSIZE = 24                   # Y축 글씨 크기

# X축
X_PAD_LEFT = 0.4                  # 왼쪽 여백 (첫 점 기준)
X_PAD_RIGHT = 0.4                 # 오른쪽 여백 (마지막 점 기준)
X_ROTATION = 45                   # X 라벨 회전 각도 (0 = 가로, 45 = 대각선)
X_FONTSIZE = 22                   # X축 글씨 크기
X_LABEL_PAD = 18                  # X 라벨/틱마크 아래로 내리는 정도

# ── Series colors ──
COLOR_ERC = '#fc8452'      # orange (solid)
COLOR_NON = '#73c0de'      # light blue (dashed)

# ── Create figure ──
fig, ax = create_figure('line')

# ── Lines ──
ax.plot(x, erc, color=COLOR_ERC, linewidth=2.6, zorder=5,
        marker='o', markersize=8, markerfacecolor=COLORS['background'],
        markeredgecolor=COLOR_ERC, markeredgewidth=2.4)
ax.plot(x, non_erc, color=COLOR_NON, linewidth=2.6, zorder=4,
        linestyle=(0, (5, 2.2)),
        marker='o', markersize=8, markerfacecolor=COLORS['background'],
        markeredgecolor=COLOR_NON, markeredgewidth=2.4)

# ── Value labels ──
for xi, v in zip(x, erc):
    off = -22 if v < non_erc[xi] else 16
    ax.annotate(f'{v}', (xi, v), textcoords='offset points',
                xytext=(0, off), ha='center', fontsize=13,
                fontweight='bold', color=COLOR_ERC, zorder=6)
for xi, v in zip(x, non_erc):
    off = 16 if v >= erc[xi] else -22
    ax.annotate(f'{v}', (xi, v), textcoords='offset points',
                xytext=(0, off), ha='center', fontsize=13,
                fontweight='bold', color=COLOR_NON, zorder=6)

# ── X-axis ──
ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str).tolist())
ax.set_xlim(-X_PAD_LEFT, len(df) - 1 + X_PAD_RIGHT)

# ── Y-axis ──
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_yticks(Y_TICKS)

# ── Apply four-pillars style ──
apply_style(fig, ax, 'line')

# ── X-ticks rotation + font size + 아래로 내리기 ──
ax.tick_params(axis='x', pad=X_LABEL_PAD)
plt.setp(ax.xaxis.get_majorticklabels(),
         rotation=X_ROTATION, ha='right' if X_ROTATION else 'center',
         fontweight='bold', fontsize=X_FONTSIZE)
for label in ax.yaxis.get_ticklabels():
    label.set_fontweight('bold')
    label.set_fontsize(Y_FONTSIZE)

# ── Save ──
png_path, svg_path = save_chart(fig, 'eip_new_proposals_by_year', 'outputs/charts/ethereum/eip')
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
