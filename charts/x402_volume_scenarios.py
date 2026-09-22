"""
x402 payment volume scenarios (T2 vs T3) vs 2026 e-commerce / B2B benchmarks.
Broken x-axis: linear to $2.2T, then compressed panels for $6.68T and $186T.
"""
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from config import setup_font, save_chart, gradient_barh, COLORS, GRID_CONFIG, DPI

T2, T3, BENCH, NOTE = '#5470c6', '#fc8452', '#787b86', '#8fa7e3'
T = 1e12
# 패널별 (lo, hi, 눈금) — 값이 패널을 넘으면 막대가 다음 패널로 이어진다
PANELS = [(0, 2.2 * T, [0, .5, 1, 1.5, 2]),
          (6.35 * T, 6.95 * T, [6.4, 6.8]),
          (184.50 * T, 186.50 * T, [185, 186])]

df = pd.read_csv('outputs/data/x402/x402_volume_scenarios.csv')
sub = [r'T2 \$6.53B, T3 \$179.91B', r'T2 \$30.04B, T3 \$656.43B',
       r'T2 \$77.05B, T3 \$1.84T', 'Cumulative as of Sep 8, 2026',
       'Source: Shopify', 'Juniper Research estimate']
vlabel = [r'\$186.45B', r'\$686.47B', r'\$1.9161T',
          r'\$54.28M', r'\$6.68T', r'\$186T']
vsize = [11.5, 11.5, 11.5, 11.5, 11.5, 15]

setup_font()
fig = plt.figure(figsize=(13.0, 5.6), dpi=DPI)
gs = fig.add_gridspec(1, 3, width_ratios=[2.2, 1.0, 1.0], wspace=0.10,
                      left=0.255, right=0.975, top=0.94, bottom=0.13)
axes = [fig.add_subplot(gs[i]) for i in range(3)]
axL = axes[0]

H = 0.5
n = len(df)
# ponytail: 최소 폭 보정. $52M은 $2.2T 축에서 0px라 레퍼런스처럼 슬라이버로 보이게 띄운다
MIN_W = 0.006 * PANELS[0][1]

for ax, (lo, hi, ticks) in zip(axes, PANELS):
    ax.set_ylim(n - 0.5, -0.5)
    for name, sp in ax.spines.items():
        sp.set_visible(name == 'bottom')      # x축 가로선만 남긴다
    ax.spines['bottom'].set_color(COLORS['text_secondary'])
    ax.spines['bottom'].set_linewidth(1.2)
    ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=11, pad=8, length=6, width=1.2,
                   direction='out', colors=COLORS['text_secondary'])
    for lab in ax.get_xticklabels():
        lab.set_fontweight('bold')


def bench_segments(total):
    """벤치마크 막대를 패널별 (ax, x0, x1)로 쪼갠다. 이어지는 패널은 그라데이션이
    끊기지 않게 왼쪽으로 패널 폭만큼 더 빼서 그린다 (xlim이 잘라준다)."""
    for k, (ax, (lo, hi, _)) in enumerate(zip(axes, PANELS)):
        if total <= lo:
            break
        x0 = lo if k == 0 else lo - 1.5 * (hi - lo)
        yield k, ax, x0, min(total, hi)


for i, row in df.iterrows():
    if row['note'] == 'benchmark':
        bars = [(ax, ax.barh(i, x1 - x0, left=x0, height=H, zorder=3)[0], BENCH)
                for _, ax, x0, x1 in bench_segments(row['total_usd'])]
    elif row['note'] == 'scenario':
        bars = [(axL, axL.barh(i, row['t2_usd'], height=H, zorder=3)[0], T2),
                (axL, axL.barh(i, row['t3_usd'], left=row['t2_usd'], height=H,
                               zorder=3)[0], T3)]
    else:
        bars = [(axL, axL.barh(i, max(row['total_usd'], MIN_W), height=H,
                               zorder=3)[0], BENCH)]
    for ax, rect, color in bars:
        gradient_barh(ax, rect, color, floor=0.78)

    # category label + sublabel (left of axis)
    axL.text(-0.022, i - 0.13, row['scenario'], transform=axL.get_yaxis_transform(),
             va='center', ha='right', fontsize=14, fontweight='bold',
             color=COLORS['text'])
    axL.text(-0.022, i + 0.20, sub[i], transform=axL.get_yaxis_transform(),
             va='center', ha='right', fontsize=10.5, fontweight='bold',
             color=COLORS['text_secondary'])

    # 값 라벨은 막대가 끝나는 패널에 붙인다
    end = max(row['total_usd'], MIN_W)
    k = max((j for j, (lo, _, _) in enumerate(PANELS) if end > lo), default=0)
    lo, hi, _ = PANELS[k]
    axes[k].text(end + 0.03 * (hi - lo), i, vlabel[i], va='center', ha='left',
                 fontsize=vsize[i], fontweight='bold', color=COLORS['text'],
                 zorder=6, clip_on=False)

# B2B 막대 위 주석
axes[1].text(PANELS[1][0], n - 1 - 0.42, r'27.8$\times$ The E-Commerce Benchmark',
             va='center', ha='left', fontsize=11.5, fontweight='bold',
             color=NOTE, zorder=6, clip_on=False)

for ax in axes:              # imshow가 축을 이미지에 맞춰버려서 여백 복구
    ax.set_ylim(n - 0.5, -0.5)
for ax, (lo, hi, ticks) in zip(axes, PANELS):
    ax.set_xlim(lo, hi)
    ax.set_xticks([t * T for t in ticks])
    ax.set_xticklabels([r'\$0' if t == 0 else rf'\${t:g}T' for t in ticks])


def squiggle(xc, ya, yb, cycles=3):
    """패널 사이 갭에 그리는 축 절단 표시 (figure 좌표)."""
    t = np.linspace(0, 1, 200)
    fig.add_artist(Line2D(xc + 0.0022 * np.sin(t * np.pi * 2 * cycles),
                          ya + (yb - ya) * t, transform=fig.transFigure,
                          color=COLORS['text_secondary'], lw=1.2, zorder=7))


def fig_y(y):
    return fig.transFigure.inverted().transform(
        axL.transData.transform((0, y)))[1]


axis_y = axL.get_position().y0
for a, b in ((0, 1), (1, 2)):
    xc = (axes[a].get_position().x1 + axes[b].get_position().x0) / 2
    squiggle(xc, axis_y - 0.018, axis_y + 0.018)      # x축 절단
    for i, r in df.iterrows():                        # 갭을 가로지르는 막대마다
        if r['note'] == 'benchmark' and r['total_usd'] > PANELS[b][0]:
            squiggle(xc, fig_y(i + H / 2), fig_y(i - H / 2))

save_chart(fig, 'x402_volume_scenarios', output_dir='outputs/charts/x402/volume',
           tight=False)
plt.close()
print('saved')
