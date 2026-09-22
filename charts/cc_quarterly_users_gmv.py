import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

setup_font()

# =============================================================================
# Data (extracted from reference: Collector Crypt quarterly new users vs GMV)
# Bars = new users (left axis); line = gross revenue / GMV ($M, right axis).
# GMV matches validated quarterly figures (Q1'26 ~$145M = Alea's $144.7M).
# =============================================================================
df = pd.read_csv('outputs/data/cc_quarterly_users_gmv.csv')

# 세로 그라데이션 바 (위 밝은 블루 -> 아래 어두운 블루). 사용자 스타일.
import matplotlib.colors as mcolors  # noqa: E402
BAR_TOP = '#5b9bd5'     # 바 상단 (밝은 블루)
BAR_BOTTOM = '#2f516f'  # 바 하단 (어두운 블루)
BAR_ANCHOR = 661        # 다크 앵커: baseline 아래 data 단위 (원본 SVG 그라데이션 재현)
LINE_COLOR = '#d6452f'  # brick red

OUTPUT_DIR = 'outputs/charts/collector_crypt/metrics'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def vgrad_bar(ax, x_center, width, value, zorder=2):
    """위(value)=BAR_TOP, 아래로 갈수록 BAR_BOTTOM 으로 가는 세로 그라데이션 사각 바."""
    if value <= 0:
        return
    light = np.array(mcolors.to_rgb(BAR_TOP))
    dark = np.array(mcolors.to_rgb(BAR_BOTTOM))
    n = 256
    grad = np.zeros((n, 1, 4))
    for j in range(n):
        data_y = value * j / (n - 1)            # 0(bottom)..value(top)
        t = (value - data_y) / (value + BAR_ANCHOR)  # 0=top(light) .. ->dark
        rgb = light * (1 - t) + dark * t
        grad[j, 0, :3] = rgb
        grad[j, 0, 3] = 1.0
    ax.imshow(grad, aspect='auto', origin='lower',
              extent=[x_center - width / 2, x_center + width / 2, 0, value],
              zorder=zorder, interpolation='bilinear')


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')

    x = np.arange(len(df))

    # bars: new users (left axis) - 세로 그라데이션
    for xi, v in zip(x, df['new_users']):
        vgrad_bar(ax, xi, 0.55, v, zorder=2)

    # line: GMV $M (right axis), square markers
    ax2.plot(x, df['gmv_musd'], color=LINE_COLOR, linewidth=2.4,
             marker='s', markersize=8, zorder=5)

    # left axis: new users (5 ticks)
    ax.set_yticks([0, 2000, 4000, 6000, 8000])
    ax.set_yticklabels([f'{t:,}' for t in [0, 2000, 4000, 6000, 8000]],
                       fontsize=12, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(0, 8250)

    # right axis: GMV $M. 26Q2 GMV ($258M) overflows the old $200M cap, so
    # extend to $250M (ylim 275 keeps the $250M tick aligned with the 8000 gridline)
    ax2.set_yticks([0, 50, 100, 150, 200, 250])
    ax2.set_yticklabels([f'${t}M' for t in [0, 50, 100, 150, 200, 250]],
                        fontsize=12, fontweight='bold', color=LINE_COLOR)
    ax2.set_ylim(0, 266)

    # x axis: "YYYY Qn" 형식 (사용자 스타일)
    ax.set_xticks(x)
    ax.set_xticklabels([q.replace('Q', ' Q') for q in df['quarter']],
                       fontsize=12, fontweight='bold', color=COLORS['text'])
    ax.set_xlim(-0.6, len(df) - 0.4)

    # grid (left axis only; right ticks align to same gridlines)
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', length=0)
    ax2.tick_params(axis='both', length=0)

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/cc_quarterly_users_gmv_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.2), 'wide')
print('Done: cc_quarterly_users_gmv')
print(f"  New users {df['new_users'].iloc[0]} -> {df['new_users'].iloc[-1]}"
      f" | GMV ${df['gmv_musd'].iloc[0]}M -> ${df['gmv_musd'].iloc[-1]}M")
