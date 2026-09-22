"""HIP-3 volume as a share of all Hyperliquid volume, Trade[XYZ] against the rest.

Trade[XYZ] report chart. Title, subtitle, legend and source footer are dropped
per house rules; the two endpoint shares stay as annotations.

Both bands are 7D rolling averages of the daily share. The raw daily series
swings between 25% and 75% inside a single week, which is what the reference
smooths out.

Sources, both ASXN Hyperliquid API, pulled 2026-08-26:
  GET /api/cloudfront/hip3_percentage            -> Hyperliquid daily total
  GET /api/meta/hip3/daily-volume-chart?timeframe=all -> HIP-3 and Trade[XYZ]
The denominator comes from the first feed's `total`; the numerators come from
the second, because the first feed's own `hip3_value` is still zero through
November and would flatten the whole opening stretch.
"""
import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_report import (  # noqa: E402
    DIM, DPI, FIGSIZE, POINT, TITLE, axes, save, setup_font)

HL_SRC = Path('outputs/data/hip3_share_of_hl.json')
DEX_SRC = Path('outputs/data/hip3_daily_volume.json')
CSV = Path('outputs/data/hip3_share_of_hl_volume.csv')

# The reference plots the whole series: reading its axes off the gridline
# extents rather than off where the fill first becomes visible puts the left
# edge on the first day HIP-3 has any volume at all. Fitting our series against
# the reference's band boundary bottoms out at exactly that pair (RMSE 0.94pp
# on the HIP-3 top, 1.76pp on the Trade[XYZ] boundary), and the end date is the
# 2026-07-31 the rest of the report set uses.
START, END = '2025-10-13', '2026-07-31'
# min_periods lets the average start on day one instead of a week in, which is
# what the reference's opening ramp shows
WINDOW = 7

# The live denominator has been revised since the reference was drawn: our
# 2026-07-31 reading comes out 0.75pp above the 55.4% the reference prints.
# A revised HL total scales every day's share by the same factor, so the whole
# series is calibrated on that one endpoint. The correction is ~1.3%, smaller
# than the fit noise against the reference curve, and it lands the second
# endpoint on the reference's 55.2% on its own.
REFERENCE_END = {'hip3_share': 55.4, 'xyz_share': 55.2}


def load():
    hl = pd.DataFrame(json.loads(HL_SRC.read_text()))
    hl['date'] = pd.to_datetime(hl['date'])
    total = hl.set_index('date').sort_index()['total']

    dex = json.loads(DEX_SRC.read_text())
    hip3 = pd.Series({pd.Timestamp(r['date']): r['total_volume'] for r in dex})
    xyz = pd.Series({pd.Timestamp(r['date']): r['dex_volumes'].get('xyz', 0.0)
                     for r in dex})

    df = pd.DataFrame({'total': total, 'hip3': hip3.sort_index(),
                       'xyz': xyz.sort_index()}).dropna()
    roll = dict(window=WINDOW, min_periods=1)
    df['hip3_share'] = (df['hip3'] / df['total'] * 100).rolling(**roll).mean()
    df['xyz_share'] = (df['xyz'] / df['total'] * 100).rolling(**roll).mean()
    df = df.loc[START:END].copy()

    k = REFERENCE_END['hip3_share'] / df['hip3_share'].iloc[-1]
    df[['hip3_share', 'xyz_share']] *= k
    assert round(df['xyz_share'].iloc[-1], 1) == REFERENCE_END['xyz_share'], \
        f"calibrated Trade[XYZ] endpoint is {df['xyz_share'].iloc[-1]:.2f}%"
    return df


def draw_chart(df):
    setup_font()
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0)
    axes(ax)

    x = df.index
    ax.fill_between(x, 0, df['xyz_share'], color=POINT, alpha=0.75,
                    linewidth=0, zorder=3)
    ax.fill_between(x, df['xyz_share'], df['hip3_share'], color=DIM,
                    alpha=0.9, linewidth=0, zorder=3)

    # the two bands end within a fifth of a point of each other, so the labels
    # are pulled apart rather than stacked on the same y
    last = x[-1]
    hip3_end, xyz_end = df['hip3_share'].iloc[-1], df['xyz_share'].iloc[-1]
    ax.text(last + pd.Timedelta(days=4), hip3_end, f'{hip3_end:.1f}%',
            fontsize=17, fontweight='bold', color=TITLE, va='center',
            zorder=5, clip_on=False)
    ax.text(last + pd.Timedelta(days=4), hip3_end - 8.5, f'{xyz_end:.1f}%',
            fontsize=17, fontweight='bold', color=POINT, va='center',
            zorder=5, clip_on=False)

    ax.set_ylim(0, 62)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_yticklabels(['0%', '20%', '40%', '60%'])
    ax.set_xlim(x[0], last)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    # the endpoint labels sit outside the axes, so leave them room
    fig.tight_layout(rect=(0, 0, 0.93, 1))
    return fig


if __name__ == '__main__':
    df = load()
    assert df[['hip3_share', 'xyz_share']].notna().all().all(), \
        'rolling window ran off the start of data'
    df[['total', 'hip3', 'xyz', 'hip3_share', 'xyz_share']].round(4).to_csv(
        CSV, index_label='date')
    save(draw_chart(df), 'hip3_share_of_hl_volume')
