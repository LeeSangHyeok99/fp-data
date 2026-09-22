"""Trade[XYZ] ch4 e07: cross-venue SPCX marks funnelling into the Nasdaq print.

Source data ships with the reference (e07_spcx_marks_funnel_data.csv).
Title, subtitle, axis labels and source footer dropped per house rules; the
legend block is replaced by an inline colour key.
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

from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT, VENUE_COLORS  # noqa: E402

VENUES = [(n, VENUE_COLORS[n], 2.0 if n == 'Trade[XYZ]' else 1.3)
          for n in ('Trade[XYZ]', 'Binance', 'OKX', 'Aster', 'Lighter',
                    'Ventuals')]

THIN_BOOKS = ('Lighter', 'Ventuals')   # quoted hourly, gaps on no-trade hours
VWAP30 = 160.97
NASDAQ_OPEN = 150.00
FIRST_PRINT = datetime(2026, 6, 12, 15, 46)   # the IPO cross
# "60-minute TWAPs before the session open": the session opens 13:30 UTC
# (09:30 ET), not at the delayed first print, so the window is 12:30 to 13:30
TWAP_START = datetime(2026, 6, 12, 12, 30)
TWAP_END = datetime(2026, 6, 12, 13, 30)


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e07_spcx_marks_funnel.csv')
    df['ts'] = pd.to_datetime(df['hour_ts_utc'], utc=True).dt.tz_localize(None)

    fig, (ax, axs) = plt.subplots(
        2, 1, figsize=(13.2, 7.4), dpi=DPI, sharex=True,
        gridspec_kw={'height_ratios': [1.25, 1], 'hspace': 0.13})
    fig.patch.set_alpha(0)
    for a in (ax, axs):
        a.set_facecolor('none')
        for sp in a.spines.values():
            sp.set_visible(False)
        a.tick_params(length=0, colors=NOTE, labelsize=13)
        a.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
               linestyle=(0, (3.7, 1.6)))
        a.set_axisbelow(True)
        a.axvspan(TWAP_START, TWAP_END, color=POINT, alpha=0.14,
                  linewidth=0, zorder=1)
        a.axvline(FIRST_PRINT, color=TITLE, linewidth=1.4,
                  linestyle=(0, (5, 3)), zorder=5)

    for name, color, lw in VENUES:
        s = df[['ts', name]].dropna()
        spread = (s[name] / VWAP30 - 1) * 100
        ax.plot(s['ts'], s[name], color=color, linewidth=lw, zorder=4)
        axs.plot(s['ts'], spread, color=color, linewidth=lw, zorder=4)
        if name in THIN_BOOKS:
            # lines run through no-trade hours; dots mark the traded ones
            ax.plot(s['ts'], s[name], linestyle='none', marker='o',
                    markersize=2.4, color=color, zorder=5)
            axs.plot(s['ts'], spread, linestyle='none', marker='o',
                     markersize=2.4, color=color, zorder=5)

    # --- inline colour key ---------------------------------------------------
    for i, (name, color, _) in enumerate(VENUES):
        ax.text(0.012 + i * 0.105, 1.045, name, transform=ax.transAxes,
                fontsize=11.5, fontweight='bold', color=color, ha='left',
                va='bottom')

    # --- top panel annotations ----------------------------------------------
    ax.annotate('Binance And Aster vs Trade[XYZ] And OKX:\n'
                'Per-Share Clusters 10.1% Apart (Jun 10)',
                xy=(datetime(2026, 6, 10, 21), 167),
                xytext=(datetime(2026, 6, 6, 6), 186),
                fontsize=11, color=TITLE, va='center', zorder=6,
                arrowprops=dict(arrowstyle='-', color=NOTE, linewidth=0.9,
                                connectionstyle='arc3,rad=-0.25'))
    ax.annotate('Final Pre-Listing Marks \$173 To \$177' '\n'
                '(60-Minute TWAPs Before The Session Open)',
                xy=(TWAP_END, 178),
                xytext=(datetime(2026, 6, 8, 12), 192),
                fontsize=11, color=POINT, va='center', ha='left', zorder=6,
                arrowprops=dict(arrowstyle='-', color=POINT, linewidth=0.9,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(FIRST_PRINT, 150, 'SpaceX Lists\nNasdaq First Print 15:46 UTC  ',
            fontsize=11, color=TITLE, ha='right', va='center', zorder=6)

    ax.set_ylim(145, 196)
    ax.set_yticks([150, 160, 170, 180, 190])
    ax.set_yticklabels([f'${v}' for v in (150, 160, 170, 180, 190)])

    # --- bottom panel --------------------------------------------------------
    axs.axhline(0, color=TITLE, linewidth=1.2, zorder=3)
    open_spread = (NASDAQ_OPEN / VWAP30 - 1) * 100
    axs.axhline(open_spread, color=NOTE, linewidth=1.0,
                linestyle=(0, (2, 2)), zorder=3)
    axs.text(datetime(2026, 6, 3, 3), open_spread + 1.6,
             'Nasdaq Open \$150.00' '\n' '(6.8% Below The VWAP)', fontsize=10.5,
             color=NOTE, va='bottom', zorder=6)
    axs.annotate('Final Marks: +7.5% To +10.1% vs The VWAP,\n'
                 '+15.3% To +18.1% vs The Open',
                 xy=(TWAP_END, 10),
                 xytext=(datetime(2026, 6, 8, 12), 17),
                 fontsize=11, color=POINT, va='center', ha='left', zorder=6,
                 arrowprops=dict(arrowstyle='-', color=POINT, linewidth=0.9,
                                 connectionstyle='arc3,rad=-0.3'))

    axs.set_ylim(-11, 22)
    axs.set_yticks([-10, -5, 0, 5, 10, 15, 20])
    axs.set_yticklabels(['-10%', '-5%', '+0%', '+5%', '+10%', '+15%', '+20%'])

    axs.set_xlim(df['ts'].min(), datetime(2026, 6, 12, 19, 0))
    axs.xaxis.set_major_locator(mdates.DayLocator())
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))
    plt.setp(axs.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e07_spcx_marks_funnel.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e07.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
