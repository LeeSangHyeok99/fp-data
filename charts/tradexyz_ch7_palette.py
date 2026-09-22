"""Shared setup for the Trade[XYZ] ch7 HRC redraws.

Chapter 7 is the deployer shake-out, so the roles are: Trade[XYZ] takes the
point colour, the deployers that wound down go red, whatever is still trading
sits on the grey ladder, and the one namespace that migrated gets the muted
violet so it reads as "moved", not "died".
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT  # noqa: F401,E402

DPI = 150
DATA = Path('tradeXYZ_Inforgraphic_retouch/ch7')
OUT_DIR = Path('outputs/charts/tradexyz/ch7')

DIM = '#5A5F66'      # the grey the point colour is read against
FILL = '#9CA3AF'
RED = '#E0574B'      # wound down in Q2
VIOLET = '#8B84B8'   # migrated to a new namespace

# one hue per deployer state, keyed by the namespace in the csv
NS_COLORS = {
    'xyz': POINT,
    'hyna': DIM,
    'para': DIM,
    'cash': RED,
    'flx': RED,
    'vntl': RED,
    'km': VIOLET,
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
