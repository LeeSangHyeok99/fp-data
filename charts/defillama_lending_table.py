"""
Leading Lending Protocols 테이블 (DefiLlama 스냅샷 재현)
matplotlib으로 렌더한 표 이미지. 투명 배경, four-pillars 다크 텍스트.
"""
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, DPI, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/defillama_lending_protocols.csv'

ROW_H      = 0.67      # 행 높이 (inch)
FIG_W      = 15.8
HEAD_FONT  = 23
NAME_FONT  = 23
SUB_FONT   = 17
VAL_FONT   = 23
RANK_FONT  = 20
LINE_GAP   = 5         # 이름/서브라벨 줄 간격 (pt)

# 컬럼 x 위치 (0~1, figure 좌표). 숫자 컬럼은 VAL_ALIGN 기준선.
# Name 컬럼만 넓게 잡고(긴 프로토콜명), 나머지 3개를 균등 분할한다.
NAME_COL = 0.30
COL_PAD  = 0.012
COL_X    = [NAME_COL + (1 - NAME_COL) / 3 * i for i in range(3)]
X_TVL, X_LOANS, X_SUPPLIED = (x + COL_PAD for x in COL_X)
VAL_ALIGN = 'left'          # 'left' | 'right'

# 1번 컬럼(Name) 안쪽: 랭크(우측정렬) → 아이콘 → 이름
X_RANK, X_ICON, X_NAME = 0.030, 0.056, 0.096
LOGO_DIR = Path('charts/assets/logos/defillama')
ICON_D   = 0.62        # 아이콘 지름 (행 높이 대비 비율)

OUT_NAME = 'defillama_lending_table'
OUT_DIR  = 'outputs/charts/defi/lending'
# ======================================================================

TEXT, TEXT2, GRID = COLORS['text'], COLORS['text_secondary'], COLORS['grid']


def circle_icon(fig, slug, cx, cy, d_fig_w, d_fig_h):
    """프로토콜 로고를 원형으로 마스킹해 figure 좌표 (cx, cy) 중심에 그린다.

    마스크를 4배 캔버스에서 그린 뒤 축소해 안티에일리어싱하고, 출력 픽셀 크기에
    맞춰 미리 리샘플한다. (imshow 보간에 맡기면 원 테두리가 계단처럼 깨진다.)
    """
    f = LOGO_DIR / f'{slug}.png'
    if not f.exists():
        return
    px = max(24, round(d_fig_h * fig.get_figheight() * DPI))
    im = Image.open(f).convert('RGBA').resize((px * 4, px * 4), Image.LANCZOS)
    mask = Image.new('L', (px * 4, px * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, px * 4 - 1, px * 4 - 1), fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), mask))
    im = im.resize((px, px), Image.LANCZOS)

    ax = fig.add_axes([cx - d_fig_w / 2, cy - d_fig_h / 2, d_fig_w, d_fig_h])
    ax.imshow(im, interpolation='none')
    ax.set_axis_off()
    ax.patch.set_alpha(0)


def slug(name):
    return name.lower().replace(' ', '-')


def fmt(v):
    """DefiLlama 표기 그대로: >=$1B는 b, 미만은 m. 후행 0 제거."""
    n, unit = (v, 'b') if v >= 1 else (v * 1000, 'm')
    s = f"{n:.3f}" if unit == 'b' else f"{n:.2f}"
    return f"${s.rstrip('0').rstrip('.')}{unit}"


df = pd.read_csv(CSV_PATH)
n = len(df)
fig_h = ROW_H * (n + 1.45)
fig = plt.figure(figsize=(FIG_W, fig_h), dpi=DPI)
fig.patch.set_alpha(0)

# 행 중심 y좌표 (figure 좌표, 위에서 아래로). 0번은 헤더.
def row_y(i):
    return 1 - (i + 0.85) * ROW_H / fig_h


def text(x, y, s, size, color, ha='left', weight='bold', va='center'):
    fig.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
             fontweight=weight)


# 헤더
hy = row_y(0)
text(X_NAME, hy, 'Name', HEAD_FONT, TEXT)
for x, label in ((X_TVL, 'TVL'), (X_LOANS, 'Active Loans'), (X_SUPPLIED, 'Supplied')):
    text(x, hy, label, HEAD_FONT, TEXT, ha=VAL_ALIGN)

# 구분선 (헤더 아래 + 각 행 아래)
for i in range(n + 1):
    y = row_y(i) - ROW_H / fig_h * 0.5
    fig.add_artist(plt.Line2D([0, 1], [y, y], color=GRID,
                              alpha=0.45 if i else 0.7, linewidth=0.9))

# 컬럼 구분 세로선 (헤더 아래부터, 헤더 구간에는 긋지 않는다)
y_top = row_y(0) - ROW_H / fig_h * 0.5
y_bot = row_y(n) - ROW_H / fig_h * 0.5
for x in COL_X:
    fig.add_artist(plt.Line2D([x, x], [y_bot, y_top], color=GRID,
                              alpha=0.45, linewidth=0.9))

# 이름+서브라벨 2줄 블록을 행 중심(=아이콘 중심)에 맞춘다. 폰트를 키워도 따라온다.
# 대문자 높이(≈0.72em) 기준으로 블록 높이를 잡고 베이스라인 두 개를 계산.
_pt = lambda v: v / 72 / fig_h              # pt → figure 좌표
CAP = 0.72
DY_NAME = _pt((CAP * (NAME_FONT + SUB_FONT) + LINE_GAP) / 2 - CAP * NAME_FONT)
DY_SUB = -_pt((CAP * (NAME_FONT + SUB_FONT) + LINE_GAP) / 2)

# 데이터 행
for i, r in df.iterrows():
    y = row_y(i + 1)
    text(X_RANK, y, str(r['rank']), RANK_FONT, TEXT2, ha='right')
    circle_icon(fig, slug(r['protocol']), X_ICON, y,
                ICON_D * ROW_H / FIG_W, ICON_D * ROW_H / fig_h)
    text(X_NAME, y + DY_NAME, r['protocol'], NAME_FONT, TEXT, va='baseline')
    chains = f"{r['chains']} chain" + ('s' if r['chains'] > 1 else '')
    text(X_NAME, y + DY_SUB, chains, SUB_FONT, TEXT2, va='baseline')
    for x, v in ((X_TVL, r['tvl']), (X_LOANS, r['active_loans']),
                 (X_SUPPLIED, r['supplied'])):
        text(x, y, fmt(v), VAL_FONT, TEXT, ha=VAL_ALIGN)

png, svg = save_chart(fig, OUT_NAME, OUT_DIR, tight=False)
print(png, svg)
