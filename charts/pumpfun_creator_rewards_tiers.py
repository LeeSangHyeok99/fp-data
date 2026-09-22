"""
Pump.fun Creator Rewards by Lifetime Earnings per Address
소스: Blockworks Research (레퍼런스 이미지 재현). 로그 스케일 바.
색 구성은 레퍼런스 그대로: 하위 3구간 민트, $1K~$10K 라이트 퍼플, $10K+ 퍼플.
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, GRID_CONFIG, gradient_rounded_bar, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'path'   # 글자를 전부 패스(벡터)로 변환

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/pumpfun_creator_rewards_tiers.csv'

MINT         = '#7fe3c0'   # 하위 3구간
PURPLE_LIGHT = '#bda6fb'   # $1K ~ $10K
PURPLE       = '#5b3ff0'   # Over $10K
BAR_COLORS = [MINT, MINT, MINT, PURPLE_LIGHT, PURPLE]

TICK_FONT  = 14
VALUE_FONT = 14
VALUE_PAD  = 8         # 바 꼭대기와 값 라벨 사이 간격 (pt)
BAR_WIDTH  = 0.45
GRAD_FLOOR = 0.72      # 바 아래쪽 밝기 (1에 가까울수록 그라데이션 약함)
X_ROTATION = 45
X_LABEL_HA = 'right'
Y_BASE     = 1_000
Y_MAX      = 6_000_000
Y_TICKS    = [1_000, 10_000, 100_000, 1_000_000]

OUT_NAME = 'pumpfun_creator_rewards_tiers'
OUT_DIR  = 'outputs/charts/pumpfun/rewards'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(10.67, 3.9), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.set_yscale('log')
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(Y_BASE, Y_MAX)

for xi, v, c in zip(x, df['addresses'], BAR_COLORS):
    gradient_rounded_bar(ax, x_center=xi, width=BAR_WIDTH, height=v, color=c,
                         floor=GRAD_FLOOR, round_top=False, y0=Y_BASE)

# 두 줄을 각각 따로 그린다. 멀티라인 텍스트는 SVG에서 text-anchor 없이
# 줄마다 좌표가 박혀 나와서, Figma 등에서 폰트 크기를 바꾸면 정렬이 깨진다.
for xi, v, p in zip(x, df['addresses'], df['share']):
    for txt, dy in ((f"({p * 100:.1f}%)", VALUE_PAD),
                    (f"{v:,.0f}", VALUE_PAD + VALUE_FONT * 1.25)):
        ax.annotate(txt, (xi, v), textcoords='offset points', xytext=(0, dy),
                    ha='center', va='bottom', color=TEXT,
                    fontsize=VALUE_FONT, fontweight='bold')

ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(Y_BASE, Y_MAX)
ax.set_xticks(x)
ax.set_xticklabels([t.replace('$', r'\$') for t in df['tier']])
ax.set_yticks(Y_TICKS)
ax.set_yticklabels(['1K', '10K', '100K', '1M'])
ax.minorticks_off()

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=TICK_FONT, colors=TEXT2, length=0, pad=10)
ax.tick_params(axis='x', labelsize=TICK_FONT, colors=TEXT2, length=6, width=1.2, pad=8,
               rotation=X_ROTATION)
plt.setp(ax.xaxis.get_majorticklabels(), ha=X_LABEL_HA, rotation_mode='anchor')

fig.tight_layout()
print(save_chart(fig, OUT_NAME, OUT_DIR))
