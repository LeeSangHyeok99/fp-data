"""
Tokenized Equity Market Cap by Issuer (horizontal bar)
소스: rwa.xyz, 2026-08-26. Ondo + xStocks + bStocks가 공급의 93% 차지.
레퍼런스 재현: four-pillars dark theme, 투명 배경, 제목/출처/범례 없음.

Ondo(1위)만 채도 높은 퍼플 가로 그라데이션, 나머지는 muted 라이트 퍼플.
큰 막대(Ondo, Backed)는 값 라벨을 막대 안(흰색), 작은 막대는 막대 밖(밝은 회색).

──────────────────────────────────────────────────────────────────────
편집: 아래 "✏️ EDIT HERE" 값만 수정. 그 아래 RENDER는 보통 건드릴 필요 없음.
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
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/tokenized_equity_mcap_by_platform.csv'  # issuer, mcap_musd, label

# 색상 (퍼플 2톤)
LEAD_LIGHT = '#c9a6dd'   # Ondo 막대 왼쪽 (밝은 퍼플)
LEAD_DARK  = '#a13fbe'   # Ondo 막대 오른쪽 (채도 높은 퍼플)
REST_COLOR = '#c4addb'   # 나머지 muted 라이트 퍼플

# 폰트 크기
TICK_FONT   = 22    # x축 틱 + y축(이슈어) 라벨
VALUE_FONT  = 19    # 막대 값 라벨

# 축 / 막대
X_MAX     = 1150    # M 단위, Ondo(1050) + 여백
X_TICKS   = [0, 200, 400, 600, 800, 1000]
BAR_HEIGHT = 0.62
INSIDE_MIN = 10**9  # 레퍼런스(Figma판)는 값 라벨 전부 막대 밖 → 안쪽 배치 비활성
VALUE_GAP  = 14     # 막대 밖 라벨 간격 (M)
MIN_BAR    = 3      # 렌더 가능한 최소 너비(M)만 확보, 나머지는 실제 값 그대로


def bar_width(val):
    """실제 값 그대로. 아주 작은 값만 렌더용 최소 너비 보장."""
    return max(val, MIN_BAR)

OUT_NAME = 'tokenized_equity_mcap_by_platform'
OUT_DIR  = 'outputs/charts/rwa/tokenized_equity'

# ======================================================================
# RENDER
# ======================================================================
TEXT  = COLORS['text']           # #d1d4dc
TEXT2 = COLORS['text_secondary'] # #787b86


def hgrad_rounded_bar(ax, y_center, height, width, c_left, c_right, alpha=0.98):
    """가로 막대: 오른쪽 끝 라운드 캡 + 좌→우 수평 그라데이션."""
    if width is None or width <= 0:
        return
    radius = min(height / 2, width / 2)
    rect_right = width - radius
    y_bot, y_top = y_center - height / 2, y_center + height / 2

    theta = np.linspace(-np.pi / 2, np.pi / 2, 40)
    arc_x = rect_right + radius * np.cos(theta)
    arc_y = y_center + radius * np.sin(theta)
    verts = [(0, y_bot), (rect_right, y_bot)]
    verts += list(zip(arc_x, arc_y))
    verts += [(rect_right, y_top), (0, y_top), (0, y_bot)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)

    rl, gl, bl = mcolors.to_rgb(c_left)
    rr, gr, br = mcolors.to_rgb(c_right)
    grad = np.zeros((1, 256, 4))
    for i in range(256):
        f = i / 255
        grad[0, i] = [rl + (rr - rl) * f, gl + (gr - gl) * f, bl + (br - bl) * f, alpha]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[0, width, y_bot, y_top], zorder=3,
                   interpolation='bilinear')
    im.set_clip_path(clip)


df = pd.read_csv(CSV_PATH)
n = len(df)
# 위→아래로 Ondo가 맨 위: y=0 을 맨 위 막대로 두고 아래로 내려감
y = np.arange(n)[::-1]

fig, ax = plt.subplots(figsize=(17.55, 6.38), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

for yi, (issuer, val, lab) in zip(y, zip(df['issuer'], df['mcap_musd'], df['label'])):
    is_lead = issuer == df['issuer'].iloc[0]
    if is_lead:
        hgrad_rounded_bar(ax, yi, BAR_HEIGHT, val, LEAD_LIGHT, LEAD_DARK)
    else:
        hgrad_rounded_bar(ax, yi, BAR_HEIGHT, bar_width(val), REST_COLOR, REST_COLOR)

    if val >= INSIDE_MIN:
        ax.text(val - VALUE_GAP, yi, lab, ha='right', va='center',
                color='#ffffff', fontsize=VALUE_FONT, fontweight='bold', zorder=5)
    else:
        ax.text(bar_width(val) + VALUE_GAP, yi, lab, ha='left', va='center',
                color='#ffffff', fontsize=VALUE_FONT, fontweight='bold', zorder=5)

# 축
ax.set_xlim(0, X_MAX)
ax.set_ylim(-0.7, n - 0.3)
ax.set_yticks(y)
ax.set_yticklabels(df['issuer'])
ax.tick_params(axis='y', colors=TEXT, labelsize=TICK_FONT, length=0, pad=10)

ax.set_xticks(X_TICKS)
def fmt_x(v, _):
    if v >= 1000:
        return f"${v/1000:.1f}B"
    return f"${v:.0f}M"
ax.xaxis.set_major_formatter(FuncFormatter(fmt_x))
ax.tick_params(axis='x', colors=TEXT2, labelsize=TICK_FONT, length=0, pad=8)
ax.grid(True, axis='x', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.19, right=0.98, top=0.97, bottom=0.09)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
