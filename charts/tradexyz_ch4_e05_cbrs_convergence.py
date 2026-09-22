"""Trade[XYZ] ch4 e05: perp per-fill price against every Nasdaq CBRS trade.

Perp fills come from the reference SVG vector path; the Nasdaq trade cloud was
rasterised in the reference, so it is recovered pixel-wise from that raster.
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
    TITLE, BODY, NOTE, POINT, EVENT_COLORS)

FIRST_TRADE = datetime(2026, 5, 14, 16, 59, 43)


def setup_font():
    d = Path('assets/font/SUIT/SUIT-ttf')
    if d.exists():
        for f in d.glob('SUIT-*.ttf'):
            fm.fontManager.addfont(str(f))
        plt.rcParams['font.family'] = 'SUIT'


def draw_chart():
    setup_font()
    perp = pd.read_csv(DATA / 'e05_perp_fills.csv', parse_dates=['ts'])
    nas = pd.read_csv(DATA / 'e05_nasdaq_trades.csv', parse_dates=['ts'])

    fig, ax = plt.subplots(figsize=(12.6, 5.8), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=NOTE, labelsize=13)
    ax.grid(True, axis='y', color=NOTE, alpha=0.35, linewidth=0.9,
            linestyle=(0, (3.7, 1.6)))
    ax.set_axisbelow(True)

    ax.scatter(nas['ts'], nas['price'], s=1.2, color=TITLE,
               alpha=0.16, linewidths=0, zorder=3, rasterized=True)
    ax.plot(perp['ts'], perp['price'], color=POINT, linewidth=1.1, zorder=4)

    ax.axvline(FIRST_TRADE, color=EVENT_COLORS['pricing'], linewidth=1.5,
               alpha=0.9, zorder=5)
    ax.text(FIRST_TRADE, 348.5,
            '  Nasdaq First Trade\n  16:59:43 UTC   $350.00 × 4.37M Shares',
            fontsize=11, color=EVENT_COLORS['pricing'], ha='left', va='top',
            zorder=6,
            bbox=dict(boxstyle='round,pad=0.45', facecolor='none',
                      edgecolor=EVENT_COLORS['pricing'], linewidth=1.0))

    ax.text(datetime(2026, 5, 14, 16, 55, 20), 388, 'Trade[XYZ] Per-Fill Price',
            fontsize=11, color=POINT, fontweight='bold', va='center', zorder=6)
    ax.text(datetime(2026, 5, 14, 16, 55, 20), 384,
            'Nasdaq Per-Trade Price (Databento)', fontsize=11, color=BODY,
            va='center', zorder=6)

    ax.set_ylim(324, 392)
    ax.set_yticks([330, 350, 370, 390])
    ax.set_xlim(datetime(2026, 5, 14, 16, 55), datetime(2026, 5, 14, 17, 10))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw_chart()
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'e05_cbrs_convergence.{ext}', dpi=DPI,
                    facecolor='none', edgecolor='none', transparent=True,
                    bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor('#1a1a1a')
    fig.savefig(OUT_DIR / '_preview_e05.png', dpi=DPI, facecolor='#1a1a1a',
                bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR)
