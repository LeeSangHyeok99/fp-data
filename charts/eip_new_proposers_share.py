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
df = pd.read_csv('outputs/data/eip_new_proposers_share.csv')

x = np.arange(len(df))

# =============================================================================
# 축 설정 (여기만 수정하면 됨)
# =============================================================================
# Y축
Y_MIN = 0                              # 아래 한계
Y_MAX = 112                            # 위 여백 (퍼센트 라벨 공간)
Y_TICKS = [0, 25, 50, 75, 100]         # Y축 눈금 (최대 5개)
Y_FONTSIZE = 24                        # Y축 글씨 크기

# X축
X_FONTSIZE = 17                        # X축 글씨 크기
X_LABEL_PAD = 14                       # X 라벨/틱마크 아래로 내리는 정도

# 바
BAR_WIDTH = 0.40                       # 바 너비
BAR_GAP = 0.06                         # 그룹 내 두 바 사이 간격
PCT_FONTSIZE = 11                      # 퍼센트 라벨 글씨 크기

# Figure
FIG_WIDTH = 16.0                       # 가로 길이 (넓힐수록 라벨 안 겹침)
FIG_HEIGHT = 6.0                       # 세로 길이

# ── Series colors ──
COLOR_ERC = '#fc8452'      # orange
COLOR_NON = '#73c0de'      # light blue

# ── Create figure ──
from config import setup_font, DPI
setup_font()
fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ── Bar centers (그룹 내 간격 BAR_GAP 적용) ──
erc_x = x - (BAR_WIDTH + BAR_GAP) / 2
non_x = x + (BAR_WIDTH + BAR_GAP) / 2

# ── Grouped bars ──
ax.bar(erc_x, df['erc_pct'], BAR_WIDTH, color=COLOR_ERC, zorder=3)
ax.bar(non_x, df['non_erc_pct'], BAR_WIDTH, color=COLOR_NON, zorder=3)

# ── Percent labels above bars (좌우로 살짝 벌려 겹침 방지) ──
for xi, v in zip(erc_x, df['erc_pct']):
    ax.annotate(f'{v:.1f}%', (xi, v), textcoords='offset points',
                xytext=(0, 7), ha='center', fontsize=PCT_FONTSIZE,
                fontweight='bold', color=COLOR_ERC, zorder=6)
for xi, v in zip(non_x, df['non_erc_pct']):
    ax.annotate(f'{v:.1f}%', (xi, v), textcoords='offset points',
                xytext=(0, 7), ha='center', fontsize=PCT_FONTSIZE,
                fontweight='bold', color=COLOR_NON, zorder=6)

# ── X-axis ──
ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str).tolist())
ax.set_xlim(-0.6, len(df) - 0.4)

# ── Y-axis ──
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_yticks(Y_TICKS)
ax.set_yticklabels([f'{t}%' for t in Y_TICKS])

# ── Apply four-pillars style ──
apply_style(fig, ax, 'bar')

# ── n labels below x-axis (ERC n / Non n) ──
for xi, (en, nn) in enumerate(zip(df['erc_n'], df['non_erc_n'])):
    ax.annotate(f'ERC n={en}', (xi, 0), xycoords=('data', 'axes fraction'),
                textcoords='offset points', xytext=(0, -52), ha='center',
                fontsize=10, fontweight='bold', color=COLOR_ERC, annotation_clip=False)
    ax.annotate(f'Non n={nn}', (xi, 0), xycoords=('data', 'axes fraction'),
                textcoords='offset points', xytext=(0, -68), ha='center',
                fontsize=10, fontweight='bold', color=COLOR_NON, annotation_clip=False)

# ── X-ticks font size + 아래로 내리기 ──
ax.tick_params(axis='x', pad=X_LABEL_PAD)
plt.setp(ax.xaxis.get_majorticklabels(),
         rotation=0, ha='center', fontweight='bold', fontsize=X_FONTSIZE)
for label in ax.yaxis.get_ticklabels():
    label.set_fontweight('bold')
    label.set_fontsize(Y_FONTSIZE)

# ── Save ──
png_path, svg_path = save_chart(fig, 'eip_new_proposers_share', 'outputs/charts/ethereum/eip')
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
