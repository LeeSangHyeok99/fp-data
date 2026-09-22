"""Trade[XYZ] ch4 e09: hourly median book depth by venue into the SPCX cross.

Source data ships with the reference (e09_spcx_depth_listing.csv).
Title, subtitle, axis label and source footer dropped per house rules; the
reference's right-edge direct labels are kept.
"""
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

sys.path.append('.claude/skills/design/hrc')
sys.path.append('charts')
from config import DPI  # noqa: E402
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT, VENUE_COLORS  # noqa: E402

DATA = Path('outputs/data/tradexyz_ch4')
OUT_DIR = Path('outputs/charts/tradexyz/ch4')

CROSS = datetime(2026, 6, 12, 15, 46)
# venue -> label y, nudged off the last value where labels would collide
LABEL_Y = {'OKX': 1_438_800, 'Trade[XYZ]': 380_000, 'Binance': 232_000,
           'Lighter': 150_000, 'Aster': 100_000, 'Ventuals': 760}


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e09_spcx_depth_listing.csv')
    df['ts'] = pd.to_datetime(df['hour_ts'].str.replace(' UTC', '', regex=False))

    fig, ax = plt.subplots(figsize=(13.0, 6.0), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    ax.tick_params(axis='y', which='minor', length=0)
    ax.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
            linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)

    order = ['OKX', 'Trade[XYZ]', 'Binance', 'Lighter', 'Aster', 'Ventuals']
    for name in order:
        lw = 2.6 if name == 'Trade[XYZ]' else 1.6
        ax.plot(df['ts'], df[name], color=VENUE_COLORS[name], linewidth=lw,
                zorder=4 if name == 'Trade[XYZ]' else 3)
        ax.plot([df['ts'].iloc[-1]], [df[name].iloc[-1]], marker='o',
                markersize=6, color=VENUE_COLORS[name], zorder=5)
        ax.text(CROSS + pd.Timedelta(minutes=25), LABEL_Y[name], name,
                fontsize=12, fontweight='bold', color=VENUE_COLORS[name],
                va='center', ha='left', zorder=6)

    ax.axvline(CROSS, color=VENUE_COLORS['Ventuals'], linewidth=1.6,
               linestyle=(0, (5, 3)), zorder=5)
    ax.text(CROSS, 3.4e6, 'Nasdaq Opening Cross\nJun 12, 15:46 UTC  ',
            fontsize=11, color=VENUE_COLORS['Ventuals'], ha='right', va='top',
            zorder=6)

    ax.text(datetime(2026, 6, 10, 12), 3.4e6,
            'OKX: Sixfold Build Into The Cross\n'
            r'\$199k (Jun 8-10 Median) To \$1.28M (Jun 11-12 Median)',
            fontsize=11, color=BODY, ha='center', va='top', zorder=6)
    ax.text(datetime(2026, 6, 12, 8), 8.0e5,
            'Trade[XYZ]: Thinned Into The Cross\n'
            r'\$201k (Jun 8-10 Median) To \$150k (Jun 11-12 Median)',
            fontsize=11, color=POINT, ha='right', va='top', zorder=6)

    ax.set_yscale('log')
    ax.set_ylim(4e2, 5e6)
    ax.set_yticks([1e3, 1e4, 1e5, 1e6])
    ax.set_yticklabels(['$1k', '$10k', '$100k', '$1M'])
    ax.set_xlim(df['ts'].min(), datetime(2026, 6, 12, 20, 30))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e09_spcx_depth_listing.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e09.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
