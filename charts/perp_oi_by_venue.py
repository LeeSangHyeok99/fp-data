"""
Perp Open Interest by Venue (log-scale horizontal bar)
소스: Ondo Perps (api.ondoperps.xyz), Ostium (blog), Hyperliquid (ASXN). June 29 2026.
레퍼런스 재현: four-pillars dark theme, 투명 배경, 제목/1liner/출처는 차트 밖(위)에 표기.

Ondo Perps만 민트 브랜드 컬러로 강조, 나머지는 회색.
Hyperliquid는 $6~8B 레인지를 2톤(진회색 6B까지 + 밝은회색 6~8B)으로 표현.
X축은 로그 스케일 ($10M, $100M, $1B, $10B).

──────────────────────────────────────────────────────────────────────
편집: 아래 "✏️ EDIT HERE" 값만 수정.
──────────────────────────────────────────────────────────────────────
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
matplotlib.rcParams['svg.fonttype'] = 'none'

# ======================================================================
# ✏️  EDIT HERE
# ======================================================================
CSV_PATH = 'outputs/data/perp_oi_by_venue.csv'  # venue, oi_usd, oi_hi_usd, label

# 색상
MINT       = '#86e3c1'   # Ondo Perps 강조 (민트)
GREY_MID   = '#8a8d90'   # Ostium
GREY_DARK  = '#565a5f'   # Hyperliquid 본체
GREY_EXT   = '#6f7378'   # Hyperliquid 6~8B 레인지 연장

# 폰트 크기
NAME_FONT  = 22    # y축 venue 이름
VALUE_FONT = 21    # 막대 값 라벨
NOTE_FONT  = 15    # 보조 주석 (about 0.2% ...)

# 축 (로그 스케일)
X_MIN   = 1e7      # 막대 시작 = $10M
X_MAX   = 1.15e10  # 우측 여백
X_TICKS = [1e7, 1e8, 1e9, 1e10]  # $10M, $100M, $1B, $10B
BAR_H   = 0.5

OUT_NAME = 'perp_oi_by_venue'
OUT_DIR  = 'outputs/charts/ondo/perps'

# ======================================================================
# RENDER
# ======================================================================
TEXT  = COLORS['text']           # #d1d4dc
TEXT2 = COLORS['text_secondary'] # #787b86

df = pd.read_csv(CSV_PATH)
n = len(df)
y = np.arange(n)[::-1]  # 첫 행(Ondo)이 맨 위

fig, ax = plt.subplots(figsize=(16.0, 6.2), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.set_xscale('log')


def fmt_usd(v):
    if v >= 1e9:
        return f"${v/1e9:g}B"
    return f"${v/1e6:g}M"


for yi, row in zip(y, df.itertuples(index=False)):
    venue, val, hi, lab = row.venue, row.oi_usd, row.oi_hi_usd, row.label
    is_ondo = venue == df['venue'].iloc[0]
    color = MINT if is_ondo else (GREY_MID if venue == 'Ostium' else GREY_DARK)

    if pd.notna(hi) and hi > val:
        # 레인지 막대: X_MIN~val 본체 + val~hi 연장
        ax.barh(yi, val - X_MIN, left=X_MIN, height=BAR_H, color=color, zorder=3)
        ax.barh(yi, hi - val, left=val, height=BAR_H, color=GREY_EXT, zorder=3)
        label_x = hi * 1.12
    else:
        ax.barh(yi, val - X_MIN, left=X_MIN, height=BAR_H, color=color, zorder=3)
        label_x = val * 1.14

    val_color = MINT if is_ondo else TEXT
    ax.text(label_x, yi, lab, ha='left', va='center',
            color=val_color, fontsize=VALUE_FONT, fontweight='bold', zorder=5)

    # Ondo 보조 주석
    if is_ondo:
        ax.text(label_x * 3.0, yi, 'about 0.2% of Hyperliquid', ha='left',
                va='center', color=TEXT2, fontsize=NOTE_FONT, fontweight='bold',
                zorder=5)

# 축
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(-0.7, n - 0.3)
ax.set_yticks(y)
ax.set_yticklabels(df['venue'])
ax.tick_params(axis='y', colors=TEXT, labelsize=NAME_FONT, length=0, pad=14)

ax.xaxis.set_major_locator(FixedLocator(X_TICKS))
ax.xaxis.set_minor_locator(FixedLocator([]))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_usd(v)))
ax.tick_params(axis='x', colors=TEXT2, labelsize=VALUE_FONT, length=0, pad=10)
ax.grid(True, axis='x', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

# "log scale" 주석 (좌측 마진, 틱 라벨 높이에 맞춰 배치)
ax.annotate('log scale', xy=(-0.125, -0.055), xycoords='axes fraction',
            ha='left', va='center', color=TEXT2, fontsize=NOTE_FONT,
            fontweight='bold', style='italic')

fig.subplots_adjust(left=0.135, right=0.985, top=0.965, bottom=0.11)

png, svg = save_chart(fig, OUT_NAME, output_dir=OUT_DIR)
print('saved:', png)
