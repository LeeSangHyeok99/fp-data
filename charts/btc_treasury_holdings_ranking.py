"""
Largest Public Bitcoin Treasuries (BTC held)
소스: BitcoinTreasuries.net. Metaplanet = 글로벌 3위 (Strategy, Twenty One 다음)
1:1 정사각 비율, four-pillars dark theme. 어두운->밝은 오렌지 2색 그라데이션.

──────────────────────────────────────────────────────────────────────
편집 방법: 아래 "✏️ EDIT HERE" 블록의 값만 바꾸면 차트가 바뀝니다.
          (그 아래 RENDER 영역은 건드리지 않아도 됩니다.)
──────────────────────────────────────────────────────────────────────
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
# SVG에서 글자를 path로 풀지 말고 <text>로 유지 → 벡터 노드 급감 + 글자 편집 가능
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE — 여기만 수정하세요
# ======================================================================

# --- 1. 데이터 (CSV에서 로드) ------------------------------------------
CSV_PATH = 'outputs/data/btc_treasury_holdings_ranking.csv'   # company, btc_held

# --- 2. 색상 -----------------------------------------------------------
BTC_ORANGE      = '#f7931a'   # 밝은 오렌지 (막대 상단)
BTC_ORANGE_DARK = '#a85f12'   # 어두운 오렌지 (막대 하단)

# --- 3. 폰트 크기 ------------------------------------------------------
TICK_FONT   = 20       # x·y축 라벨 폰트
VALUE_FONT  = 16       # 막대 위 값 라벨 폰트

# --- 4. x축 라벨 회전 (대각선) -----------------------------------------
X_ROTATION  = 45       # 0이면 수평, 45면 대각선
X_LABEL_HA  = 'right'  # 회전 시 정렬: 'right' 권장

# --- 5. 틱마크 --------------------------------------------------------
TICK_LENGTH = 6        # 틱마크 길이 (0이면 숨김)
TICK_WIDTH  = 1.2      # 틱마크 두께

# --- 6. 축 / 막대 ------------------------------------------------------
Y_MAX       = 920000
Y_TICKS     = [0, 200000, 400000, 600000, 800000]
BAR_WIDTH   = 0.6
VALUE_GAP   = 13000    # 막대 꼭대기에서 값 라벨까지 간격

# 출력 파일명 / 경로
OUT_NAME = 'btc_treasury_holdings_ranking'
OUT_DIR  = 'outputs/charts/bitcoin/treasury'

# ======================================================================
# RENDER — 아래는 보통 수정할 필요 없음
# ======================================================================

TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']


def gradient_bar_2color(ax, x_center, width, height, c_bottom, c_top, alpha=0.97):
    """라운드 탑 바 + 두 색(어두운 오렌지 -> 밝은 오렌지) 수직 그라데이션."""
    if height is None or height <= 0:
        return
    radius = min(width / 2, height * 0.35)
    rect_top = height - radius
    x_left, x_right = x_center - width / 2, x_center + width / 2

    theta = np.linspace(0, np.pi, 40)
    arc_x = x_center + radius * np.cos(theta)
    arc_y = rect_top + radius * np.sin(theta)
    verts = [(x_left, 0), (x_right, 0), (x_right, rect_top)]
    verts += list(zip(arc_x, arc_y))
    verts += [(x_left, rect_top), (x_left, 0)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)

    rb, gb, bb = mcolors.to_rgb(c_bottom)
    rt, gt, bt = mcolors.to_rgb(c_top)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        f = i / 255
        grad[i, 0] = [rb + (rt - rb) * f, gb + (gt - gb) * f, bb + (bt - bb) * f, alpha]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, height], zorder=3,
                   interpolation='bilinear')
    im.set_clip_path(clip)


df = pd.read_csv(CSV_PATH)
x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

for xi, v in zip(x, df['btc_held']):
    gradient_bar_2color(ax, x_center=xi, width=BAR_WIDTH, height=v,
                        c_bottom=BTC_ORANGE_DARK, c_top=BTC_ORANGE)
    ax.text(xi, v + VALUE_GAP, f"{v:,.0f}", ha='center', va='bottom',
            color=TEXT, fontsize=VALUE_FONT, fontweight='bold')

# 축
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, Y_MAX)
ax.set_xticks(x)
ax.set_xticklabels(df['company'], rotation=X_ROTATION,
                   ha=(X_LABEL_HA if X_ROTATION else 'center'))
ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT,
               length=TICK_LENGTH, width=TICK_WIDTH, pad=8)

ax.set_yticks(Y_TICKS)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:,.0f}K"))
ax.tick_params(axis='y', colors=TEXT2, labelsize=TICK_FONT,
               length=TICK_LENGTH, width=TICK_WIDTH, pad=8)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.12)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
