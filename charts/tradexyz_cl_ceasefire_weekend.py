"""Trade[XYZ] CL perp through the June ceasefire weekend, hourly close.

The point of the chart is that the venue kept discovering price while CME was
shut, so the closed window is shaded and the perp mark takes the point colour.

Hourly closes from the Hyperliquid public API (candleSnapshot, xyz dex).
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT  # noqa: E402
from tradexyz_ch7_palette import RED, base_axes, setup_font  # noqa: E402
from tradexyz_q2_volume_by_asset_class import save  # noqa: E402

OUT_DIR = 'outputs/charts/tradexyz/volume'
SRC = 'outputs/data/tradexyz_cl_perp_hourly.csv'
START, END = datetime(2026, 6, 11), datetime(2026, 6, 17)

# CME energy: Friday 21:00 UTC close, Sunday 22:00 UTC reopen
CME_CLOSED = (datetime(2026, 6, 12, 21), datetime(2026, 6, 14, 22))
CEASEFIRE = datetime(2026, 6, 15, 12)
YLIM, YTICKS = (74.4, 91.6), (75, 80, 85, 90)


def draw_chart():
    setup_font()
    d = pd.read_csv(SRC, parse_dates=['ts'])
    d = d[d.ts.between(START, END)]

    fig, ax = plt.subplots(figsize=(10.9, 4.6), dpi=150)
    fig.patch.set_alpha(0)
    base_axes(ax)
    lo, hi = YLIM

    ax.axvspan(*CME_CLOSED, color=TITLE, alpha=0.05, linewidth=0, zorder=1)
    mid = CME_CLOSED[0] + (CME_CLOSED[1] - CME_CLOSED[0]) / 2
    ax.text(mid, hi - (hi - lo) * 0.04, 'Internal Session\n(CME Closed)',
            fontsize=11.5, color=BODY, ha='center', va='top', linespacing=1.35,
            zorder=5)

    ax.axvline(CEASEFIRE, color=RED, linewidth=1.3, linestyle=(0, (6, 4)),
               zorder=2)
    ax.text(CEASEFIRE, hi - (hi - lo) * 0.04, '  Jun 15\n  Ceasefire Announced',
            fontsize=11.5, color=RED, ha='left', va='top', linespacing=1.35,
            zorder=5)

    ax.plot(d.ts, d.close, color=POINT, linewidth=1.9, zorder=4)
    ax.text(d.ts.iloc[-1] + pd.Timedelta(hours=2), d.close.iloc[-1],
            'CL Perp ($/bbl)', fontsize=11.5, color=POINT, ha='left',
            va='center', zorder=5)

    ax.set_ylim(*YLIM)
    ax.set_yticks(list(YTICKS))
    ax.set_yticklabels([f'${v}' for v in YTICKS])
    ax.tick_params(axis='y', labelsize=13, pad=6)
    ax.set_xlim(START, END + pd.Timedelta(hours=14))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
    ax.tick_params(axis='x', labelsize=12, pad=5, length=5, width=1,
                   color=NOTE)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    import tradexyz_q2_volume_by_asset_class as base
    base.OUT_DIR = OUT_DIR
    save(draw_chart(), 'cl_ceasefire_weekend')
