"""
HIP-4 Two Venues: Markets Registered vs Lifetime Volume (Aug 29 ~ Sep 1, 2026)

Data:
  - lifetime_volume_usd: hl.eco SSE feed `research-hip4` (byVenue, 2026-08-29~31 합계)
    Outcome $2,552,546 / Skew $21,960 -> 레퍼런스의 $2.55M / $21.96K와 정확히 일치
  - markets_registered: 레퍼런스(hl.eco + Hyperliquid explorer) 값.
    배포자와 서브배포자의 성공한 템플릿 호출 수라 온체인 tx 카운트이며 피드에는 없다.
"""

import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import (COLORS, DPI, FIGURE_SIZES, _find_font,
                    gradient_rounded_bar, save_chart, setup_font)

# Pretendard는 Bold 파일만 등록되어 있어 weight로는 굵기가 안 빠진다
TITLE_FONT = fm.FontProperties(
    fname=str(_find_font('Pretendard/Pretendard-Medium.ttf')), size=15)

COLOR = {'Outcome': '#78DEC9', 'Skew': '#A78BFA'}

df = pd.read_csv('outputs/data/hip4_venue_registrations_vs_volume.csv')


def fmt_usd(v):
    return f'${v / 1e6:.2f}M' if v >= 1e6 else f'${v / 1e3:.2f}K'


PANELS = [
    ('Markets Registered, Aug 29 To Sep 1', 'markets_registered', str),
    ('Venue Volume, Lifetime', 'lifetime_volume_usd', fmt_usd),
]

setup_font()
fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZES['bar'], dpi=DPI)
fig.patch.set_alpha(0)

for ax, (header, col, fmt) in zip(axes, PANELS):
    ax.set_facecolor('none')
    vals = df[col].values
    top = vals.max()

    # 축을 먼저 확정해야 gradient_rounded_bar가 픽셀 기준 코너를 잡는다
    ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.set_ylim(0, top * 1.32)
    ax.set_xticks(range(len(vals)), df['venue'])

    for x, (v, name) in enumerate(zip(vals, df['venue'])):
        gradient_rounded_bar(ax, x, 0.46, v, COLOR[name],
                             floor=0.86, round_top=False)

    for x, v in enumerate(vals):
        ax.text(x, v + top * 0.035, fmt(v), ha='center', va='bottom',
                color=COLORS['text'], fontsize=19, fontweight='bold')

    ax.set_title(header, color=COLORS['text'], fontproperties=TITLE_FONT,
                 pad=18)

    # 바닥선만 남기고 축을 지운다
    ax.axhline(0, color=COLORS['text'], linewidth=1.6, zorder=4)
    ax.set_yticks([])
    ax.tick_params(axis='x', length=0, pad=12, labelsize=17,
                   colors=COLORS['text'])
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight('bold')
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.subplots_adjust(wspace=0.28)
fig.tight_layout()
png, svg = save_chart(fig, 'hip4_venue_registrations_vs_volume',
                      'outputs/charts/hyperliquid/hip4')
print(png, svg)
