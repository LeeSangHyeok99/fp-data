"""HIP-3 daily volume share by deployer, Trade[XYZ] against everyone else.

Trade[XYZ] report chart. Title, subtitle, legend and source footer are dropped
per house rules; the legend becomes direct labels inside the two bands, and the
endpoint share stays as an annotation.

Source: ASXN Hyperliquid API, GET /api/meta/hip3/daily-volume-chart?timeframe=all
(the bare endpoint only returns 30 days). Pulled 2026-08-26.
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

SRC = Path('outputs/data/hip3_daily_volume.json')
CSV = Path('outputs/data/hip3_volume_share_xyz.csv')

# the reference's own window, recovered by fitting our share series to the
# band boundary lifted out of the reference PNG (best RMSE 1.09pp, and the
# last day lands on the 99.8% the reference prints)
START, END = '2025-10-13', '2026-07-31'


def load():
    rows = json.loads(SRC.read_text())
    df = pd.DataFrame([
        {'date': pd.Timestamp(r['date']),
         'xyz': r['dex_volumes'].get('xyz', 0.0),
         'total': r['total_volume']}
        for r in rows
    ]).set_index('date').sort_index().loc[START:END]
    df['xyz_share'] = df['xyz'] / df['total'] * 100
    return df


def draw_chart(df):
    setup_font()
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0)
    axes(ax)

    x, share = df.index, df['xyz_share']
    # Trade[XYZ] is ~99% of the area, so a solid point-colour slab would be a
    # wall of gold: the band stays a wash and the point colour rides the
    # boundary line, which is the part actually worth reading
    ax.fill_between(x, 0, share, color=POINT, alpha=0.20, linewidth=0, zorder=3)
    ax.fill_between(x, share, 100, color=DIM, alpha=0.75, linewidth=0, zorder=3)
    ax.plot(x, share, color=POINT, linewidth=1.6, zorder=4)

    # direct band labels in place of the legend: Trade[XYZ] owns the body of
    # the chart, Others is only readable where the February dip opens it up
    ax.text(pd.Timestamp('2026-01-05'), 42, 'Trade[XYZ]', fontsize=20,
            fontweight='bold', color=POINT, ha='center', va='center', zorder=5)
    ax.text(pd.Timestamp('2026-02-20'), 84, 'Others', fontsize=14,
            fontweight='bold', color=TITLE, ha='center', va='center', zorder=5)

    last = x[-1]
    ax.text(last + pd.Timedelta(days=4), share.iloc[-1],
            f'{share.iloc[-1]:.1f}%', fontsize=18, fontweight='bold',
            color=TITLE, va='center', zorder=5, clip_on=False)

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlim(x[0], last)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    # the endpoint label sits outside the axes, so leave it room
    fig.tight_layout(rect=(0, 0, 0.93, 1))
    return fig


if __name__ == '__main__':
    df = load()
    assert len(df) == 292 and round(df['xyz_share'].iloc[-1], 1) == 99.8, \
        'window drifted off the reference'
    df[['xyz', 'total', 'xyz_share']].round(4).to_csv(CSV, index_label='date')
    save(draw_chart(df), 'hip3_volume_share_xyz_vs_others')
