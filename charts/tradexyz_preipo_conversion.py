"""Trade[XYZ] pre-IPO perps through their listing: CBRS and SPCX, hourly close.

Two panels in one canvas, each on its own price scale, so the shape of each
conversion is readable rather than the two being forced onto a common axis.
The perp mark takes the point colour, the IPO reference levels sit behind it:
offer price on the grey ladder, first trade in red.

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

OUT_DIR = 'outputs/charts/tradexyz/preipo'

PANELS = [
    dict(name='CBRS', label='CBRS: Perp Vs IPO (May 13-15)', src='outputs/data/tradexyz_cbrs_perp_hourly.csv',
         start=datetime(2026, 5, 13), end=datetime(2026, 5, 15),
         # 9:30 ET regular open on listing day, when the perp reprices
         listing=datetime(2026, 5, 14, 13, 30),
         offer=185, first_trade=350,
         ylim=(176, 400), yticks=(200, 250, 300, 350)),
    dict(name='SPCX', label='SPCX: Perp Vs IPO (Jun 11-13)', src='outputs/data/tradexyz_spcx_perp_hourly.csv',
         start=datetime(2026, 6, 11), end=datetime(2026, 6, 13),
         listing=datetime(2026, 6, 12, 13, 30),
         offer=135, first_trade=150,
         ylim=(130, 188), yticks=(140, 150, 160, 170, 180)),
]


def draw_panel(ax, cfg):
    d = pd.read_csv(cfg['src'], parse_dates=['ts'])
    d = d[d.ts.between(cfg['start'], cfg['end'])]
    base_axes(ax)

    lo, hi = cfg['ylim']
    ax.axhline(cfg['offer'], color=NOTE, linewidth=1.1,
               linestyle=(0, (1.6, 2.2)), zorder=2)
    ax.text(cfg['start'], cfg['offer'] + (hi - lo) * 0.018,
            f"  Offer ${cfg['offer']}", fontsize=10.5, color=NOTE,
            ha='left', va='bottom', zorder=5)

    ax.axhline(cfg['first_trade'], color=RED, linewidth=1.3,
               linestyle=(0, (6, 4)), zorder=2)
    ax.text(cfg['start'], cfg['first_trade'] + (hi - lo) * 0.018,
            f"  First Trade ${cfg['first_trade']}", fontsize=10.5, color=RED,
            ha='left', va='bottom', zorder=5)

    ax.axvline(cfg['listing'], color=BODY, linewidth=1.1,
               linestyle=(0, (1.6, 2.2)), zorder=2)
    ax.text(cfg['listing'], cfg['offer'] + (hi - lo) * 0.018, 'Listing Open  ',
            fontsize=10.5, color=BODY, ha='right', va='bottom', zorder=5)

    ax.plot(d.ts, d.close, color=POINT, linewidth=1.9, zorder=4)
    # name the series at the end of its own line instead of in a legend
    ax.text(d.ts.iloc[-1] + pd.Timedelta(hours=1), d.close.iloc[-1],
            'XYZ Perp', fontsize=11.5, color=POINT, ha='left', va='center',
            zorder=5)
    ax.text(cfg['start'], hi - (hi - lo) * 0.03,
            f"  {cfg['label']}", fontsize=12, color=POINT,
            ha='left', va='top', zorder=5)

    ax.set_ylim(*cfg['ylim'])
    ax.set_yticks(list(cfg['yticks']))
    ax.set_yticklabels([f'${v}' for v in cfg['yticks']])
    ax.tick_params(axis='y', labelsize=12, pad=6)
    # right margin holds the end-of-line series label
    ax.set_xlim(cfg['start'], cfg['end'] + pd.Timedelta(hours=7))
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=(0, 12)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Hh'))
    ax.tick_params(axis='x', labelsize=11, pad=5, length=5, width=1,
                   color=NOTE)


def draw_chart():
    setup_font()
    fig, axes = plt.subplots(1, 2, figsize=(10.9, 4.4), dpi=150)
    fig.patch.set_alpha(0)
    for ax, cfg in zip(axes, PANELS):
        draw_panel(ax, cfg)
    fig.tight_layout(w_pad=1.6)
    return fig


if __name__ == '__main__':
    import tradexyz_q2_volume_by_asset_class as base
    base.OUT_DIR = OUT_DIR
    save(draw_chart(), 'preipo_conversion')
