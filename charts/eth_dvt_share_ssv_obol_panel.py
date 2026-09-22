"""
Ethereum DVT Adoption: SSV vs Obol — 스탯 카드 단독.
막대 차트는 eth_dvt_share_ssv_obol.py, 여기는 우측 패널만 뽑는다.
분모(Ethereum 전체)는 레퍼런스 값 고정.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, GRID_CONFIG, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'path'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/eth_dvt_share_ssv_obol.csv'

PALETTE = {'SSV': '#fc8452', 'Obol': '#73c0de'}
SERIES = [('SSV Network', 'SSV'), ('Obol', 'Obol')]

# 점선 상한 레퍼런스 (Obol 자체 보고) — 막대 차트의 점선 바와 짝
OBOL_REF = [('SHARE', '1.63%'), ('STAKE', '~600,000 ETH'), ('AS OF', 'Jan 2026')]
REF_NAME = 'Obol · self-reported'

FIGSIZE = (3.4, 4.9)
NAME_FONT = 17
LABEL_FONT = 12
STAT_FONT = 15
SWATCH_SIZE = 150       # 범례 마크 크기 (points^2)
SWATCH_RADIUS = 0.25    # 코너 반경 / 변 = Rectangle 17925.svg 의 rx6/24

DENOM = {'Validators': 910357, 'ETH': 42990000}   # Ethereum 전체 (레퍼런스)

ROW_GAP = 0.085         # 스탯 행 간격
HEAD_GAP = 0.10         # 프로토콜명 → 첫 행
BLOCK_GAP = 0.13        # 블록 사이

OUT_NAME = 'eth_dvt_share_ssv_obol_panel'
OUT_DIR = 'outputs/charts/ethereum/staking'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
by_proto = {p: {r.unit: r.value for r in df[df['protocol'] == p].itertuples()}
            for p in PALETTE}
UNITS = (('Validators', 'VALIDATORS', ''), ('ETH', 'STAKE', 'ETH'))

fig = plt.figure(figsize=FIGSIZE, dpi=150)
fig.patch.set_alpha(0)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor('none')
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])
ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def rounded_square(r):
    """라운드 사각 마커 Path (단위 정사각, 코너는 2차 베지어 근사)."""
    h = 0.5
    verts, codes = [(-h + r, -h)], [MPath.MOVETO]
    corners = [((h - r, -h), (h, -h), (h, -h + r)),
               ((h, h - r), (h, h), (h - r, h)),
               ((-h + r, h), (-h, h), (-h, h - r)),
               ((-h, -h + r), (-h, -h), (-h + r, -h))]
    for start, ctrl, end in corners:
        verts.append(start); codes.append(MPath.LINETO)
        verts += [ctrl, end]; codes += [MPath.CURVE3, MPath.CURVE3]
    verts.append((-h + r, -h)); codes.append(MPath.CLOSEPOLY)
    return MPath(verts, codes)


SWATCH = rounded_square(SWATCH_RADIUS)


def fmt(v, unit):
    s = f"{v / 1e6:.2f}M" if v >= 1e6 else f"{v:,.0f}"
    return f"{s} {unit}".strip()


def stat(y, label, value):
    ax.text(0.0, y, label, ha='left', va='center', color=TEXT2,
            fontsize=LABEL_FONT, fontweight='bold')
    ax.text(1.0, y, value, ha='right', va='center', color=TEXT,
            fontsize=STAT_FONT, fontweight='bold')


y = 0.97
for name, key in SERIES:
    ax.scatter(0.03, y, s=SWATCH_SIZE, marker=SWATCH, color=PALETTE[key],
               linewidths=0, zorder=4)
    ax.text(0.12, y, name, ha='left', va='center', color=TEXT,
            fontsize=NAME_FONT, fontweight='bold')
    y -= HEAD_GAP
    for unit, label, suffix in UNITS:
        stat(y, label, fmt(by_proto[key][unit], suffix))
        y -= ROW_GAP
    y -= BLOCK_GAP - ROW_GAP

# 점선 스와치 범례 블록
ax.scatter(0.03, y, s=SWATCH_SIZE, marker=SWATCH, facecolor='none',
           edgecolor=PALETTE['Obol'], linewidths=1.2, linestyle=(0, (2, 1.5)), zorder=4)
ax.text(0.12, y, REF_NAME, ha='left', va='center', color=TEXT,
        fontsize=NAME_FONT, fontweight='bold')
y -= HEAD_GAP
for label, value in OBOL_REF:
    stat(y, label, value)
    y -= ROW_GAP
y -= BLOCK_GAP - ROW_GAP

ax.axhline(y + 0.04, color=GRID_CONFIG['color'], alpha=0.30, linewidth=1.0)
ax.text(0.0, y - 0.05, 'ETHEREUM · DENOMINATOR', ha='left', va='center',
        color=TEXT2, fontsize=LABEL_FONT, fontweight='bold')
y -= 0.05 + HEAD_GAP
for unit, label, suffix in UNITS:
    stat(y, label, fmt(DENOM[unit], suffix))
    y -= ROW_GAP

print(save_chart(fig, OUT_NAME, OUT_DIR))
