"""Trade[XYZ] open interest, 7D and 14D rolling averages.

HRC redraw of the reference. Title, subtitle, legend and source footer are
dropped per house rules; the legend becomes direct labels on the two line ends.
7D is the headline read so it takes the point colour, 14D rides underneath in
grey.

Source: ASXN Hyperliquid API, GET /api/meta/hip3/daily-oi-chart?timeframe=all
(the bare endpoint only returns 30 days; `timeframe=all` returns the full
history). Pulled 2026-08-26, dex namespace `xyz`.
"""
import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_report import (  # noqa: E402
    DPI, FIGSIZE, PEER, POINT, TITLE, axes, save, setup_font)

SRC = Path('outputs/data/hip3_daily_oi.json')
CSV = Path('outputs/data/tradexyz_oi_rolling.csv')
# the reference's own window, recovered by fitting our 7D series to the green
# line lifted out of the reference PNG (best RMSE $0.043B over a $0.15-3.7B
# range, a sharp minimum at these two dates)
START, END = '2025-12-21', '2026-07-29'


def load():
    rows = json.loads(SRC.read_text())
    s = pd.Series(
        {pd.Timestamp(r['date']): r['dex_oi'].get('xyz', 0.0) for r in rows}
    ).sort_index() / 1e9
    df = pd.DataFrame({'oi': s, 'avg_7d': s.rolling(7).mean(),
                       'avg_14d': s.rolling(14).mean()}).loc[START:END]
    return df


def draw_chart(df):
    setup_font()
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0)
    axes(ax)

    # the fill hugs whichever average is on top, as in the reference
    ax.fill_between(df.index, 0, df[['avg_7d', 'avg_14d']].max(axis=1),
                    color=POINT, alpha=0.05, linewidth=0, zorder=2)
    # both lines are averages of the same series, so they get equal weight
    ax.plot(df.index, df['avg_14d'], color=PEER, linewidth=2.2, zorder=3)
    ax.plot(df.index, df['avg_7d'], color=POINT, linewidth=2.2, zorder=4)

    last = df.index[-1]
    for col, color in (('avg_14d', PEER), ('avg_7d', POINT)):
        ax.plot(last, df[col].iloc[-1], 'o', color=color, markersize=7,
                zorder=5, clip_on=False)

    # the 7D peak is the point the chart is built around
    pk = df['avg_7d'].idxmax()
    ax.text(pk, df.loc[pk, 'avg_7d'] + 0.12,
            f'7D Peak ${df.loc[pk, "avg_7d"]:.2f}B  ', fontsize=12.5,
            color=TITLE, ha='right', va='bottom', zorder=6)

    ax.set_ylim(0, 4.05)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_yticklabels(['$0B', '$1B', '$2B', '$3B', '$4B'])
    ax.set_xlim(df.index[0], last)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
             rotation_mode='anchor')

    # nothing hangs outside the axes now
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    df = load()
    # rolling windows must be full: the first plotted day already has 14 days
    # of lead-in behind it, so nothing in the window is NaN
    assert df.notna().all().all(), 'rolling window ran off the start of data'
    df.round(4).to_csv(CSV, index_label='date')
    save(draw_chart(df), 'tradexyz_oi_rolling_avg')
