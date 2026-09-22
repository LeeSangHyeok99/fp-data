"""Shared setup for the Trade[XYZ] ch6 HRC redraws.

Text roles follow the HRC dark spec; the point colour marks whichever series
the chart is actually about, everything else falls back to the grey ladder.
Reuses the ch4 market hues so CBRS / QNT / SPCX stay identifiable across
chapters.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

sys.path.append('charts')
from tradexyz_ch4_palette import (  # noqa: F401,E402
    TITLE, BODY, NOTE, POINT, MARKET_COLORS)

DPI = 150
DATA = Path('tradeXYZ_Inforgraphic_retouch/ch6')
OUT_DIR = Path('outputs/charts/tradexyz/ch6')

# the two dim companions the point colour is read against
DIM = '#5A5F66'
FILL = '#9CA3AF'
RED = '#E0574B'

# cohort hues for the June 5 cross-sections, borrowed from the ch4 markets
COHORT_COLORS = {
    'Korean listings': POINT,
    'US semiconductors': MARKET_COLORS['CBRS'],
    'Index reference': MARKET_COLORS['SPCX'],
}


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def base_axes(ax, axis='y', grid=True):
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    if grid:
        ax.grid(True, axis=axis, color=NOTE, alpha=0.35, linewidth=0.9,
                linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)


def save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'{name}.{ext}', dpi=DPI, facecolor='none',
                    edgecolor='none', transparent=True, bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / f'_preview_{name}.png', dpi=DPI,
                facecolor='#1a1a1a', bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR / f'{name}.png')
