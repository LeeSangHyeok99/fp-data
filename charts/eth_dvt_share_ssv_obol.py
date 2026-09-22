"""
Ethereum DVT Adoption: SSV vs Obol (2026-09-10)
레퍼런스 이미지 재현. 그룹 가로 바 2조(활성 스테이크 점유 / 검증자 키 점유).
색 구성은 레퍼런스 그대로 오렌지(SSV) / 라이트 블루(Obol).
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, GRID_CONFIG, gradient_barh, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'path'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/eth_dvt_share_ssv_obol.csv'

SSV_COLOR = '#fc8452'
OBOL_COLOR = '#73c0de'
PALETTE = {'SSV': SSV_COLOR, 'Obol': OBOL_COLOR}

GROUP_FONT = 20     # 왼쪽 그룹 라벨
SERIES_FONT = 15    # 바 앞 시리즈 태그
VALUE_FONT = 20     # 퍼센트
SUB_FONT = 15       # 절대값
TICK_FONT = 18
VALUE_GAP_PX = 16   # 퍼센트와 절대값 사이 간격(px)

BAR_HEIGHT = 0.60
GRAD_FLOOR = 0.82
GROUP_GAP = 1.55    # 그룹 사이 간격
X_MAX = 20.0
X_TICKS = [0, 5, 10, 15, 20]
FIG_H = 6.2         # 세로 길이(inch)

# Obol 상한 레퍼런스(자체 보고, 날짜 불일치) — 점선 아웃라인 바
OBOL_REF = {'metric': 'Active Stake Share', 'share_pct': 1.63,
            'note': 'dashboard (1.63%: self-reported, Jan 2026)'}
LEGEND = [('SSV Network · Rated pool "SSV", 1d window', 'SSV', False),
          ('Obol · Obol Ecosystem Dashboard V2 (publicly tracked)', 'Obol', False),
          ('Obol self-reported, Jan 2026 (upper reference)', 'Obol', True)]
LEGEND_FONT = 13

OUT_NAME = 'eth_dvt_share_ssv_obol'
OUT_DIR = 'outputs/charts/ethereum/staking'

# ======================================================================
# RENDER
# ======================================================================
TEXT, TEXT2 = COLORS['text'], COLORS['text_secondary']

df = pd.read_csv(CSV_PATH)
groups = list(dict.fromkeys(df['metric']))

# y 좌표: 그룹당 2개 바, 그룹 사이는 GROUP_GAP 만큼 벌린다
ys, rows = [], []
for gi, g in enumerate(groups):
    sub = df[df['metric'] == g]
    for si, row in enumerate(sub.itertuples()):
        ys.append(gi * (1 + GROUP_GAP) + si)
        rows.append(row)

fig, ax = plt.subplots(figsize=(10.67, FIG_H), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for sp in ax.spines.values():
    sp.set_visible(False)

Y_LO, Y_HI = max(ys) + 0.85, -0.85
ax.set_xlim(0, X_MAX)
ax.set_ylim(Y_LO, Y_HI)

ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for y, row in zip(ys, rows):
    color = PALETTE[row.protocol]
    rect = ax.barh(y, row.share_pct, height=BAR_HEIGHT, color=color, zorder=3)[0]
    gradient_barh(ax, rect, color, floor=GRAD_FLOOR)

ax.set_xlim(0, X_MAX)   # imshow가 축을 건드리므로 되돌린다
ax.set_ylim(Y_LO, Y_HI)

# 점선 상한 바 + 주석
y_ref = next(y for y, r in zip(ys, rows)
             if r.metric == OBOL_REF['metric'] and r.protocol == 'Obol')
ax.add_patch(Rectangle((0, y_ref - BAR_HEIGHT / 2), OBOL_REF['share_pct'], BAR_HEIGHT,
                       fill=False, edgecolor=OBOL_COLOR, linewidth=1.3,
                       linestyle=(0, (3, 2)), zorder=4))

pct_texts = []
for y, row in zip(ys, rows):
    color = PALETTE[row.protocol]
    # 바 앞 시리즈 태그
    ax.text(-0.25, y, row.protocol, ha='right', va='center', color=color,
            fontsize=SERIES_FONT, fontweight='bold', zorder=4)
    # 바 끝 퍼센트
    pct = f"{row.share_pct:.2f}%" if row.share_pct < 1 else f"{row.share_pct:.1f}%"
    val = (f"{row.value / 1e6:.2f}M {row.unit}" if row.value >= 1e6
           else f"{row.value:,.0f} {row.unit}")
    if y == y_ref:
        pct += f" ({OBOL_REF['share_pct']:.2f}%)"
        val += f" · {OBOL_REF['note']}"
    val = '· ' + val
    x_lbl = max(row.share_pct, OBOL_REF['share_pct'] if y == y_ref else 0)
    t = ax.text(x_lbl + 0.35, y, pct, ha='left', va='center', color=TEXT,
                fontsize=VALUE_FONT, fontweight='bold', zorder=4)
    pct_texts.append((t, y, val))

# 그룹 라벨 (바 2개의 가운데)
for gi, g in enumerate(groups):
    ax.text(-0.055, gi * (1 + GROUP_GAP) + 0.5, g, transform=ax.get_yaxis_transform(),
            ha='right', va='center', color=TEXT, fontsize=GROUP_FONT,
            fontweight='bold', zorder=4)

ax.set_yticks([])
ax.set_xticks(X_TICKS)
ax.set_xticklabels([f"{t:.0f}%" for t in X_TICKS])
ax.tick_params(axis='x', labelsize=TICK_FONT, colors=TEXT2, length=0, pad=10)
ax.tick_params(axis='y', length=0)

handles = [Patch(facecolor='none' if dashed else PALETTE[k], edgecolor=PALETTE[k],
                 linestyle=(0, (3, 2)) if dashed else '-', linewidth=1.3, label=lbl)
           for lbl, k, dashed in LEGEND]
fig.legend(handles=handles, loc='lower left', ncol=3, frameon=False,
           prop={'size': LEGEND_FONT, 'weight': 'normal'}, labelcolor=TEXT, handlelength=1.8,
           columnspacing=2.0, bbox_to_anchor=(0.02, 0.0))
fig.tight_layout(rect=(0, 0.07, 1, 1))

# 절대값은 퍼센트 텍스트의 실제 폭 뒤에 붙인다.
# tight_layout이 축 크기를 바꾸므로 반드시 레이아웃 확정 후에 측정한다.
fig.canvas.draw()
inv = ax.transData.inverted()
for t, y, val in pct_texts:
    bb = t.get_window_extent(fig.canvas.get_renderer())
    x_val = inv.transform((bb.x1 + VALUE_GAP_PX, bb.y0))[0]
    ax.text(x_val, y, val, ha='left', va='center',
            color=TEXT2, fontsize=SUB_FONT, fontweight='bold', zorder=4)

print(save_chart(fig, OUT_NAME, OUT_DIR))
