"""
Who Held the Tokenized AMC Float (Sep 4, 2026, 08:12 UTC)
소스: 0xSammy (onchain, X post 2026-09-04). 레퍼런스 이미지 재현.
단일 스택 가로 바. 색 구성은 레퍼런스 그대로: 민트 / 라이트 퍼플 / 그레이.
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, gradient_barh, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'path'   # 글자 전부 패스(벡터)로

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/tokenized_amc_float_holders.csv'

MINT   = '#7fe3c0'
PURPLE = '#bda6fb'
GRAY   = '#3d3d3d'
PALETTE = {'mint': MINT, 'purple': PURPLE, 'gray': GRAY}

LABEL_FONT   = 19      # 바 안 라벨
CALLOUT_FONT = 17      # 아래쪽 콜아웃 라벨
TICK_FONT    = 20

BAR_HEIGHT   = 0.62
GRAD_FLOOR   = 0.82    # 왼쪽 밝기 (1에 가까울수록 그라데이션 약함)
X_MAX        = 1_100_000
X_TICKS      = [0, 200_000, 400_000, 600_000, 800_000, 1_000_000]
CALLOUT_DROP = -0.82   # 콜아웃 텍스트 y 위치 (바 아래)

OUT_NAME = 'tokenized_amc_float_holders'
OUT_DIR  = 'outputs/charts/tokenized-equities/amc'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
left = np.concatenate([[0], df['tokens'].cumsum().values[:-1]])

fig, ax = plt.subplots(figsize=(10.67, 2.7), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for name, sp in ax.spines.items():
    sp.set_visible(name == 'bottom')      # x축 가로선만 남긴다
ax.spines['bottom'].set_color(TEXT2)
ax.spines['bottom'].set_linewidth(1.2)

ax.set_xlim(0, X_MAX)
ax.set_ylim(-1.35, 0.55)

for l, row in zip(left, df.itertuples()):
    rect = ax.barh(0, row.tokens, left=l, height=BAR_HEIGHT,
                   color=PALETTE[row.color_role], zorder=3)[0]
    gradient_barh(ax, rect, PALETTE[row.color_role], floor=GRAD_FLOOR)

# imshow가 축 범위를 건드리므로 되돌린다
ax.set_xlim(0, X_MAX)
ax.set_ylim(-1.35, 0.55)

# 넓은 구간은 바 안에 라벨, 좁은 구간(ABSOLUTE CINEMA)은 아래로 빼서 콜아웃
for l, row in zip(left, df.itertuples()):
    mid = l + row.tokens / 2
    pct = f"{row.share * 100:.1f}%"
    if row.tokens / X_MAX > 0.1:
        body = f"{pct}\n{row.tokens / 1000:,.0f}K Tokens" if row.color_role != 'gray' else pct
        ax.text(mid, 0, body, ha='center', va='center',
                ma='center', color='#141414' if row.color_role != 'gray' else TEXT,
                fontsize=LABEL_FONT, fontweight='bold', linespacing=1.45, zorder=4)
    else:
        ax.plot([mid, mid], [-BAR_HEIGHT / 2, CALLOUT_DROP + 0.16],
                color=PALETTE[row.color_role], linewidth=1.4, zorder=4)
        ax.text(mid, CALLOUT_DROP, f"{pct}, {row.tokens / 1000:,.0f}K Tokens",
                ha='center', va='top', color=PALETTE[row.color_role],
                fontsize=CALLOUT_FONT, fontweight='bold', zorder=4)

ax.set_yticks([])
ax.set_xticks(X_TICKS)
ax.set_xticklabels([f"{t // 1000:.0f}K" for t in X_TICKS])
ax.tick_params(axis='x', labelsize=TICK_FONT, colors=TEXT2, length=6, width=1.2, pad=8)
ax.tick_params(axis='y', length=0)

fig.tight_layout()
print(save_chart(fig, OUT_NAME, OUT_DIR))
