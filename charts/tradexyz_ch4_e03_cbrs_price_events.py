"""Trade[XYZ] ch4 e03: CBRS perp through bookbuilding into the Nasdaq open.

Emitted as two separate charts meant to be stacked (price on top, daily
notional below). Both figures share the same width and the same axes rect in
figure fractions, and are saved WITHOUT a tight bbox, so their x-axes line up
pixel for pixel when placed one above the other. Plot-area heights keep the
reference's 2.22 : 1 ratio.

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
from tradexyz_ch4_palette import (  # noqa: E402
    TITLE, BODY, NOTE, POINT, EVENT_COLORS)

DATA = Path('outputs/data/tradexyz_ch4')
OUT_DIR = Path('outputs/charts/tradexyz/ch4')

# --- shared layout: identical width and horizontal axes rect in both files ---
FIG_W = 12.6            # inches
AX_LEFT, AX_WIDTH = 0.048, 0.860   # right margin holds the end annotations
PLOT_H_PRICE = 3.30     # inches of plot area
PLOT_H_VOL = PLOT_H_PRICE / 2.2196   # reference ratio 235.87pt : 106.27pt
PAD_TOP, PAD_BOTTOM, PAD_XLABELS = 0.20, 0.14, 0.42

X0, X1 = datetime(2026, 5, 1), datetime(2026, 5, 16)
PRICED = datetime(2026, 5, 13, 22, 9)
CONVERT = datetime(2026, 5, 14, 17, 0)
EVENTS = [
    (datetime(2026, 5, 4, 10, 13), EVENT_COLORS['offering'], (0, (5, 3))),
    (datetime(2026, 5, 10, 21, 38), EVENT_COLORS['offering'], (0, (5, 3))),
    (PRICED, EVENT_COLORS['pricing'], '-'),
    (CONVERT, EVENT_COLORS['nasdaq'], (0, (5, 3))),
]


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def make_panel(plot_h, pad_bottom):
    """Figure + axes with the shared horizontal rect."""
    fig_h = plot_h + PAD_TOP + pad_bottom
    fig = plt.figure(figsize=(FIG_W, fig_h), dpi=DPI)
    ax = fig.add_axes([AX_LEFT, pad_bottom / fig_h, AX_WIDTH, plot_h / fig_h])
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    ax.tick_params(axis='y', which='minor', length=0)
    ax.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
            linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)
    ax.set_xlim(X0, X1)
    for t, color, ls in EVENTS:
        ax.axvline(t, color=color, linewidth=1.2, linestyle=ls, alpha=0.9,
                   zorder=2)
    return fig, ax


def draw_price():
    perp = pd.read_csv(DATA / 'e03_perp.csv', parse_dates=['ts'])
    nas = pd.read_csv(DATA / 'e03_nasdaq.csv', parse_dates=['ts'])
    fig, ax = make_panel(PLOT_H_PRICE, PAD_BOTTOM)

    ax.fill_between([datetime(2026, 5, 4, 10, 13), datetime(2026, 5, 10, 21, 38)],
                    115, 125, color=NOTE, alpha=0.45, linewidth=0, zorder=1)
    ax.fill_between([datetime(2026, 5, 10, 21, 38), PRICED],
                    150, 160, color=NOTE, alpha=0.45, linewidth=0, zorder=1)

    ax.text(datetime(2026, 5, 4, 10, 13), 394, '  S-1/A: $115-125 Range',
            fontsize=10.5, color=EVENT_COLORS['offering'], ha='left', va='top', zorder=6)
    ax.text(datetime(2026, 5, 10, 21, 38), 394, '  Range Hike: $150-160',
            fontsize=10.5, color=EVENT_COLORS['offering'], ha='left', va='top', zorder=6)
    ax.text(datetime(2026, 5, 13, 21, 30), 374, 'Priced At $185  ',
            fontsize=10.5, color=EVENT_COLORS['pricing'], ha='right', va='top', zorder=6)
    ax.text(datetime(2026, 5, 14, 17, 30), 394,
            'Nasdaq Opens $350.00\nPerp Converts', fontsize=10.5,
            color=EVENT_COLORS['nasdaq'],
            ha='left', va='top', zorder=6)

    ax.plot([PRICED, CONVERT], [185, 185], color=BODY, linewidth=2.4,
            zorder=4, solid_capstyle='butt')
    ax.text(datetime(2026, 5, 14, 17, 30), 185, ' Issue Price $185',
            fontsize=10.5, color=BODY, va='center', zorder=6)

    ax.plot(perp['ts'], perp['price'], color=POINT, linewidth=1.0, zorder=5)
    for _, g in nas.groupby('seg'):
        ax.plot(g['ts'], g['price'], color=TITLE, linewidth=1.2, zorder=6)
    ax.plot([CONVERT], [350], marker='o', markersize=8, color=POINT,
            markeredgecolor=TITLE, markeredgewidth=1.0, zorder=7)

    ax.text(datetime(2026, 5, 1, 6), 168, 'Trade[XYZ] CBRS Perp (5m Last Trade)',
            fontsize=10.5, color=POINT, fontweight='bold', va='center', zorder=6)
    ax.text(datetime(2026, 5, 1, 6), 148, 'Nasdaq CBRS (1m, Regular Session)',
            fontsize=10.5, color=TITLE, va='center', zorder=6)

    ax.set_ylim(100, 400)
    ax.set_yticks([100, 200, 300, 400])
    ax.set_yticklabels([f'${v}' for v in (100, 200, 300, 400)])
    ax.set_xticks([])                      # x labels live on the lower chart
    return fig


def draw_notional():
    vol = pd.read_csv(DATA / 'e03_daily_notional.csv', parse_dates=['date'])
    fig, ax = make_panel(PLOT_H_VOL, PAD_XLABELS)

    noon = vol['date'] + pd.Timedelta(hours=12)
    conv = vol['date'] == datetime(2026, 5, 14)
    ax.bar(noon, vol['notional_usd'], width=0.72, color=BODY, alpha=0.55,
           linewidth=0, zorder=3)
    ax.bar(noon[conv], vol.loc[conv, 'notional_usd'], width=0.72, color=POINT,
           linewidth=0, zorder=4)

    for _, r in vol.iterrows():
        if r['date'] in (datetime(2026, 5, 13), datetime(2026, 5, 14),
                         datetime(2026, 5, 15)):
            ax.text(r['date'] + pd.Timedelta(hours=12),
                    r['notional_usd'] * 1.3, f"${r['notional_usd'] / 1e6:.1f}M",
                    fontsize=10.5, color=TITLE, ha='center', va='bottom',
                    zorder=5)
    ax.text(datetime(2026, 5, 2, 6), 3.2e8,
            r'Conversion Day \$281.4M = 5.87x The 13-Day Run-Up (\$47.9M)',
            fontsize=10.5, color=BODY, va='center', zorder=5)

    ax.set_yscale('log')
    ax.set_ylim(4e5, 9e8)
    ax.set_yticks([1e6, 1e7, 1e8])
    ax.set_yticklabels(['$1M', '$10M', '$100M'])
    ax.text(0.0, 1.02, 'Log Scale', transform=ax.transAxes, fontsize=10,
            color=NOTE, ha='left', va='bottom')

    ax.set_xticks([datetime(2026, 5, d) for d in range(1, 16)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
    return fig


def save(fig, name, preview=True):
    for ext in ('png', 'svg'):
        # no tight bbox: the fixed canvas is what keeps the two charts aligned
        fig.savefig(OUT_DIR / f'{name}.{ext}', dpi=DPI, facecolor='none',
                    edgecolor='none', transparent=True)
    if preview:
        fig.patch.set_alpha(1)
        fig.patch.set_facecolor('#1a1a1a')
        fig.savefig(OUT_DIR / f'_preview_{name}.png', dpi=DPI,
                    facecolor='#1a1a1a')
    plt.close(fig)


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    setup_font()
    save(draw_price(), 'e03a_cbrs_price')
    save(draw_notional(), 'e03b_cbrs_daily_notional')
    print('saved', OUT_DIR)
