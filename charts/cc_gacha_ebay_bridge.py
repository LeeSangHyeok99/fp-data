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
# keep text as editable <text> elements in the SVG (not vector paths)
plt.rcParams['svg.fonttype'] = 'none'

# =============================================================================
# Data (extracted from reference: Collector Crypt gacha flow vs eBay sales)
# Bars = total gacha flow ($M, left axis); line = eBay sales as % of gacha
# flow (right axis). eBay $ labels = pct * gacha flow (internally consistent).
# =============================================================================
df = pd.read_csv('outputs/data/cc_gacha_ebay_bridge.csv')

import matplotlib.colors as mcolors  # noqa: E402
BAR_TOP = '#d4d7db'     # 바 상단 (밝은 회색)
BAR_BOTTOM = '#aeb1b4'  # 바 하단 (베이스 ~38% 어두운 톤, 원본 SVG 그라데이션 재현)
LINE_COLOR = '#b5432f'  # brick red line

OUTPUT_DIR = 'outputs/charts/collector_crypt/gacha'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def vgrad_bar(ax, x_center, width, value, zorder=2):
    """위(value)=BAR_TOP, 아래(0)=BAR_BOTTOM 인 세로 그라데이션 사각 바 (사용자 스타일)."""
    if value <= 0:
        return
    top = np.array(mcolors.to_rgb(BAR_TOP))
    bot = np.array(mcolors.to_rgb(BAR_BOTTOM))
    n = 256
    grad = np.zeros((n, 1, 4))
    for j in range(n):
        f = j / (n - 1)              # 0(bottom)..1(top)
        grad[j, 0, :3] = bot * (1 - f) + top * f
        grad[j, 0, 3] = 1.0
    ax.imshow(grad, aspect='auto', origin='lower',
              extent=[x_center - width / 2, x_center + width / 2, 0, value],
              zorder=zorder, interpolation='bilinear')


def fmt_usd(v):
    if v >= 1e6:
        return f'${v/1e6:.2f}M'
    return f'${v/1e3:.0f}K'


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')
    # hide axes background patches so no transparent rect overlaps the labels
    ax.patch.set_visible(False)
    ax2.patch.set_visible(False)

    x = np.arange(len(df))

    # bars: gacha flow (left axis) - 세로 그라데이션
    for xi, v in zip(x, df['gacha_musd']):
        vgrad_bar(ax, xi, 0.62, v, zorder=2)

    # bar value labels: drawn on the TOP axes (ax2) but positioned with the
    # left axis data coords, so in the SVG they sit above the bars as separate
    # editable text (not captured by the bar shapes in Figma)
    for xi, v in zip(x, df['gacha_musd']):
        ax2.text(xi, v + 8, f'${v}M', ha='center', va='bottom',
                 fontsize=10, fontweight='bold', color=COLORS['text_secondary'],
                 zorder=7, transform=ax.transData)

    # line: eBay % of gacha flow (right axis)
    ax2.plot(x, df['ebay_pct'], color=LINE_COLOR, linewidth=2.2,
             marker='o', markersize=7, zorder=5)

    # line point labels: pct (bold) + eBay $ above each marker
    for xi, pct, usd in zip(x, df['ebay_pct'], df['ebay_usd']):
        ax2.text(xi, pct + 0.10, f'{pct:.2f}%', ha='center', va='bottom',
                 fontsize=10.5, fontweight='bold', color=LINE_COLOR, zorder=6)
        ax2.text(xi, pct + 0.20, fmt_usd(usd), ha='center', va='bottom',
                 fontsize=9, fontweight='bold', color=LINE_COLOR, zorder=6)

    # left axis: gacha flow $M. Q2 26* ($489M) overflows the old $400M cap,
    # so extend one $100M tick to $500M (증분 유지)
    ax.set_yticks([0, 100, 200, 300, 400, 500])
    ax.set_yticklabels([f'${t}M' for t in [0, 100, 200, 300, 400, 500]],
                       fontsize=12, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(0, 560)

    # right axis: eBay % (5 ticks, aligned to left gridlines)
    ax2.set_yticks([0, 0.40, 0.80, 1.20, 1.60])
    ax2.set_yticklabels([f'{t:.2f}%' for t in [0, 0.40, 0.80, 1.20, 1.60]],
                        fontsize=12, fontweight='bold', color=LINE_COLOR)
    ax2.set_ylim(0, 1.80)

    # x axis
    ax.set_xticks(x)
    ax.set_xticklabels(df['quarter'], fontsize=12, fontweight='bold',
                       color=COLORS['text'])
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
        fig.savefig(f'{OUTPUT_DIR}/cc_gacha_ebay_bridge_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.2), 'wide')
print('Done: cc_gacha_ebay_bridge')
print(f"  Gacha flow {df['gacha_musd'].iloc[0]}M -> {df['gacha_musd'].iloc[-1]}M"
      f" | eBay share {df['ebay_pct'].iloc[0]}% -> {df['ebay_pct'].iloc[-1]}%")
