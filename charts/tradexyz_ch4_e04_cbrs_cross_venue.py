"""Trade[XYZ] ch4 e04: CBRS across venues through bookbuilding week.

Series recovered from the reference SVG paths (see outputs/data/tradexyz_ch4/).
Title, subtitle, legend, axis label and source footer dropped per house rules.
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
    TITLE, BODY, NOTE, POINT, EVENT_COLORS, EVENT_LINE)

HIIVE = '#7189C0'   # muted blue, the one series that needed to leave the greys

RANGE_HIKE = datetime(2026, 5, 10, 21, 39)
UPSIZE = datetime(2026, 5, 11, 17, 0)
GUIDANCE = datetime(2026, 5, 12, 22, 8)
PRICED = datetime(2026, 5, 13, 22, 8)
BLOOMBERG = datetime(2026, 5, 14, 15, 25)
NASDAQ_OPEN = datetime(2026, 5, 14, 16, 59)


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    perp = pd.read_csv(DATA / 'e04_tradexyz.csv', parse_dates=['ts'])
    poly = pd.read_csv(DATA / 'e04_polymarket.csv', parse_dates=['ts'])
    hiive = pd.read_csv(DATA / 'e04_hiive.csv', parse_dates=['ts'])

    fig, ax = plt.subplots(figsize=(13.5, 4.6), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    ax.grid(True, axis='y', color=NOTE, alpha=0.22, linewidth=0.9,
            linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)

    # 2h of left pad so the first Hiive marker is not sliced by the axes edge
    x0, x1 = datetime(2026, 5, 7, 22), datetime(2026, 5, 14, 18, 30)

    # --- underwriter range bands --------------------------------------------
    ax.fill_between([x0, RANGE_HIKE], 115, 125, color=NOTE, alpha=0.45,
                    linewidth=0, zorder=1)
    ax.fill_between([RANGE_HIKE, PRICED], 150, 160, color=NOTE, alpha=0.45,
                    linewidth=0, zorder=1)

    # --- event lines ---------------------------------------------------------
    OFFER = EVENT_COLORS['offering']
    NASDAQ, PRINT = EVENT_COLORS['nasdaq'], EVENT_COLORS['pricing']
    # labels live outside the plot, stacked above the lines they belong to, so
    # nothing has to be cut short or squeezed between the series
    xt = ax.get_xaxis_transform()
    EVENTS = [
        (RANGE_HIKE, OFFER, 'Range Hike', 'center', 1.03),
        (UPSIZE, OFFER, 'Upsize Confirmed', 'center', 1.11),
        (GUIDANCE, OFFER, 'Above-Range Guidance', 'center', 1.03),
        (PRICED, PRINT, 'Priced At $185', 'center', 1.03),
        (BLOOMBERG, OFFER, 'Bloomberg Radio $350', 'right', 1.11),
        (NASDAQ_OPEN, NASDAQ, 'Nasdaq Opens $350.00', 'right', 1.19),
    ]
    for t, color, label, ha, y in EVENTS:
        ax.axvline(t, color=color, **EVENT_LINE)
        ax.text(t, y, label, transform=xt, fontsize=9.5, color=color, ha=ha,
                va='bottom', zorder=6)

    # --- issue price ---------------------------------------------------------
    ax.plot([PRICED, x1], [185, 185], color=BODY, linewidth=2.4, zorder=4,
            solid_capstyle='butt')
    ax.text(PRICED, 180, 'Issue Price $185  ', fontsize=9.5, color=BODY,
            ha='right', va='top', zorder=6)

    # --- series --------------------------------------------------------------
    ax.plot(poly['ts'], poly['price'], color=TITLE, linewidth=1.6, zorder=4)
    ax.plot(perp['ts'], perp['price'], color=POINT, linewidth=1.8, zorder=5)
    ax.scatter(hiive['ts'], hiive['price'], s=52, color=HIIVE,
               edgecolors='none', zorder=6)
    ax.plot([NASDAQ_OPEN], [350], marker='o', markersize=10, color=POINT,
            markeredgecolor=TITLE, markeredgewidth=1.0, zorder=7)

    ax.text(datetime(2026, 5, 8, 3), 313, 'Trade[XYZ] IPOP (1h Mean Of 5m Closes)',
            fontsize=9.5, color=POINT, fontweight='bold', va='center', zorder=6)
    ax.text(datetime(2026, 5, 8, 3), 165, 'Polymarket-Implied Day-1 Close ($228 Strike, 150% Vol)',
            fontsize=9.5, color=TITLE, va='center', zorder=6)
    ax.text(datetime(2026, 5, 8, 3), 145, 'Hiive Secondary Print (Daily)',
            fontsize=9.5, color=HIIVE, va='center', zorder=6)

    ax.set_ylim(100, 360)
    ax.set_yticks([150, 200, 250, 300])
    ax.set_yticklabels([f'${v}' for v in (150, 200, 250, 300)])
    ax.set_xlim(x0, x1)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e04_cbrs_cross_venue.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e04.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
