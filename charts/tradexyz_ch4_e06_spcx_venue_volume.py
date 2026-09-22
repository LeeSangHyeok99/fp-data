"""Trade[XYZ] ch4 e06: daily SPCX perp $-volume by venue, absolute and share.

Source data ships with the reference (e06_spcx_venue_volume_data.csv).
Title, subtitle, legend, axis labels and source footer dropped per house rules;
the legend is replaced with direct labels on the stacked bands.
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

DATA = Path('outputs/data/tradexyz_ch4')
OUT_DIR = Path('outputs/charts/tradexyz/ch4')

from tradexyz_ch4_palette import (  # noqa: E402
    TITLE, BODY, NOTE, POINT, VENUE_COLORS, VENUE_INK, EVENT_LINE)

# bottom-to-top stack order, as in the reference
VENUES = [
    ('trade.xyz', 'Trade[XYZ]', VENUE_COLORS['trade.xyz']),
    ('ventuals', 'Ventuals', VENUE_COLORS['ventuals']),
    ('lighter', 'Lighter', VENUE_COLORS['lighter']),
    ('aster', 'Aster', VENUE_COLORS['aster']),
    ('binance', 'Binance', VENUE_COLORS['binance']),
    ('okx', 'OKX', VENUE_COLORS['okx']),
]

# the stack interpolates across the missing day, so the mask is Jun 8 12:00
# to Jun 9 12:00, as in the reference
GAP_START = datetime(2026, 6, 8, 12)
GAP_END = datetime(2026, 6, 9, 12)


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e06_spcx_venue_volume.csv', parse_dates=['date'])

    fig, (ax, axs) = plt.subplots(
        2, 1, figsize=(13.0, 6.6), dpi=DPI, sharex=True,
        gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.14})
    fig.patch.set_alpha(0)
    for a in (ax, axs):
        a.set_facecolor('none')
        for sp in a.spines.values():
            sp.set_visible(False)
        a.tick_params(length=0, colors=NOTE, labelsize=13)
        a.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
               linestyle=(0, (3.7, 1.6)))
        a.set_axisbelow(True)
        # excluded day: the reference masks it with a paper-coloured scrim on
        # top of the stack, so on dark it is a dark scrim
        a.axvspan(GAP_START, GAP_END, color='#141414', alpha=0.62,
                  linewidth=0, zorder=6)

    ax.stackplot(df['date'], *[df[f'{k}_usd'] / 1e6 for k, _, _ in VENUES],
                 colors=[c for _, _, c in VENUES], linewidth=0, zorder=3)
    # the CSV's *_share columns are rounded to 2dp and do not sum to 1, so the
    # share panel is recomputed from the notional columns, as the reference does
    share = {k: df[f'{k}_usd'] / df['total_usd'] * 100 for k, _, _ in VENUES}
    axs.stackplot(df['date'], *[share[k] for k, _, _ in VENUES],
                  colors=[c for _, _, c in VENUES], linewidth=0, zorder=3)

    # --- events ---------------------------------------------------------
    # one dashed line per event, coloured by whose event it is, drawn through
    # both panels; the labels sit in the empty upper half of the absolute panel,
    # one row per venue, each aligned so it ends or starts on its own line
    XYZ, BNB = VENUE_COLORS['trade.xyz'], VENUE_COLORS['binance']
    EVENTS = [
        (datetime(2026, 5, 17), XYZ, 'Trade[XYZ] Lists May 17  ', 'right', 445),
        (datetime(2026, 5, 18), XYZ,
         "  69% Of The Day's Flow A Day After Listing", 'left', 445),
        (datetime(2026, 5, 21), BNB,
         'Binance Lists May 21, Leads The Same Day  ', 'right', 505),
        (datetime(2026, 5, 31), BNB, '  Binance Peak 72% (31 May)', 'left', 505),
    ]
    LABEL_FLOOR = 410      # top-panel lines stop here, under the label rows
    for t, color, label, ha, y in EVENTS:
        ax.vlines(t, 0, LABEL_FLOOR, color=color, **EVENT_LINE)
        axs.axvline(t, color=color, **EVENT_LINE)
        ax.text(t, y, label, fontsize=9.5, color=color, ha=ha, va='top',
                zorder=6)

    axs.text(datetime(2026, 5, 10, 12), 50,
             "OKX Alone On The Tape,\n7 To 14 May", fontsize=9.5,
             color=VENUE_INK['okx'], ha='center', va='center', zorder=6)

    ax.text(datetime(2026, 6, 11), 552, 'Peak Day $521M (11 Jun)  ',
            fontsize=9.5, color=TITLE, ha='right', va='top', zorder=6)

    # --- direct band labels --------------------------------------------------
    for label, y, ink in (('Trade[XYZ]', 8, VENUE_INK['trade.xyz']),
                          ('Binance', 50, TITLE),
                          ('OKX', 90, VENUE_INK['okx'])):
        axs.text(datetime(2026, 6, 3), y, label, fontsize=10,
                 fontweight='bold', color=ink, ha='center', va='center',
                 zorder=7)

    ax.set_ylim(0, 560)
    ax.set_yticks([0, 200, 400])
    ax.set_yticklabels(['$0M', '$200M', '$400M'])
    axs.set_ylim(0, 100)
    axs.set_yticks([0, 25, 50, 75, 100])
    axs.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])

    axs.set_xlim(df['date'].min(), df['date'].max())
    axs.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b'))
    plt.setp(axs.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e06_spcx_venue_volume.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e06.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
