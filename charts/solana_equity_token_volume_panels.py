"""
Trading clusters in a handful of equity tokens: 12-month spot volume,
two horizontal-bar panels with separate scales - four-pillars 내재화.
소스: Allium (레퍼런스 이미지 수치, as of Aug 18, 2026).
투명 배경, 1600x540px 슬롯용. 제목/출처는 assemble 단계.
"""
import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory as blend

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, GRID_CONFIG, gradient_barh  # noqa: E402

setup_font()
df = pd.read_csv('outputs/data/solana_equity_token_volume_top3.csv')

W, H = 1600, 540
PX2PT = 0.72                     # dpi 100: px -> pt
GREEN, GREY = '#5FA86C', '#A9ADB8'
TEXT, SUB = '#D1D4DC', '#9CA3AF'

PANELS = [  # (panel key, axes px box (x, y, w, h), xmax, tick step)
    ('Stock And ETF-Linked Tokens', (170, 95, 450, 360), 2000, 500),
    ('PreStocks: Private-Company Exposure', (1010, 95, 380, 360), 400, 100),
]
VALUE_X = {0: 790, 1: 1590}      # 값 라벨 오른쪽 끝 px


def fmt(v):
    return f'${v / 1000:.1f}B' if v >= 1000 else f'${v:.0f}M'


fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
for i, (key, (x, y, w, h), xmax, step) in enumerate(PANELS):
    d = df[df['panel'] == key].reset_index(drop=True)
    ax = fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    ys = range(len(d))
    colors = [GREEN] + [GREY] * (len(d) - 1)
    bars = ax.barh(ys, d['volume_musd'], height=0.34, color=colors, zorder=3)
    for rect, c in zip(bars, colors):
        gradient_barh(ax, rect, c, floor=0.78)   # 원점 어둡게 -> 끝 밝게
    ax.set_xlim(0, xmax)
    ax.set_ylim(len(d) - 0.5, -0.5)
    ax.set_xticks(range(0, xmax + 1, step))
    ax.set_xticklabels([f'{t:,}' for t in range(0, xmax + 1, step)],
                       fontsize=22 * PX2PT, color=SUB)
    ax.set_yticks([])
    ax.tick_params(axis='x', length=0, pad=10)
    ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle='-', linewidth=0.8, zorder=0)
    for s in ax.spines.values():
        s.set_visible(False)
    # 값 라벨: 패널 오른쪽 끝에 우측 정렬
    tr = blend(fig.transFigure, ax.transData)
    for yi, (n, v, c) in enumerate(zip(d['name'], d['volume_musd'], [GREEN] + [GREY] * 2)):
        ax.text((x - 170) / W, yi, n, transform=tr, ha='left', va='center',
                fontsize=26 * PX2PT, fontweight='bold', color=TEXT, clip_on=False)
        ax.text(VALUE_X[i] / W, yi, fmt(v), transform=tr, ha='right', va='center',
                fontsize=30 * PX2PT, fontweight='bold', color=c, clip_on=False)
    # 패널 제목, 축 단위
    fig.text((x - 170) / W, 1 - 30 / H, key, fontsize=28 * PX2PT,
             fontweight='bold', color=TEXT, va='center')
    fig.text(VALUE_X[i] / W, 1 - 78 / H, 'Axis: $M', fontsize=20 * PX2PT,
             color=SUB, ha='right', va='center')

png, svg = save_chart(fig, 'solana_equity_token_volume_panels',
                      'outputs/charts/tokenized_equities/volume', tight=False)
plt.close(fig)
print(png, svg)
