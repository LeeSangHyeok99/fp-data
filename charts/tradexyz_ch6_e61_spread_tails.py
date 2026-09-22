"""ch6 e61: quoted spread percentiles on the fifteen largest Trade[XYZ] markets.

The 90th percentile carries the finding, so it takes the point colour; the
75th and the median sit on the grey ladder behind it.
"""
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('charts')
from tradexyz_ch6_palette import (  # noqa: E402
    DATA, DPI, TITLE, BODY, NOTE, POINT, FILL, base_axes, save, setup_font)

Q2_START = datetime(2026, 4, 1)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e61_spread_tails_data.csv', parse_dates=['date'])

    fig, ax = plt.subplots(figsize=(12.6, 5.8), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    ax.axvspan(Q2_START, df['date'].iloc[-1], color=TITLE, alpha=0.045,
               zorder=0, linewidth=0)
    ax.text(Q2_START, 15.4, '  Q2 Reporting Period', fontsize=11, color=NOTE,
            ha='left', va='top', zorder=2)

    ax.fill_between(df['date'], df['p25'], df['p75'], color=FILL, alpha=0.13,
                    linewidth=0, zorder=1)
    ax.plot(df['date'], df['median'], color=NOTE, linewidth=1.4, zorder=3)
    ax.plot(df['date'], df['p75'], color=BODY, linewidth=1.6, zorder=4)
    ax.plot(df['date'], df['p90'], color=POINT, linewidth=2.2, zorder=5)

    last = df.iloc[-1]
    for value, color in ((last['p90'], POINT), (last['p75'], BODY),
                         (last['median'], NOTE)):
        ax.text(last['date'], value, f'  {value:.2f}', fontsize=12,
                color=color, ha='left', va='center', zorder=6)

    lbl_x = datetime(2026, 6, 1)
    ax.text(lbl_x, 14.6, '90th Percentile', fontsize=12,
            color=POINT, va='center', zorder=6)
    ax.text(lbl_x, 13.4, '75th Percentile', fontsize=12,
            color=BODY, va='center', zorder=6)
    ax.text(lbl_x, 12.2, 'Median, 7-Day Rolling (bps)',
            fontsize=12, color=NOTE, va='center', zorder=6)

    ax.set_ylim(0, 16)
    ax.set_yticks([0, 4, 8, 12, 16])
    ax.set_yticklabels(['0', '4', '8', '12', '16'])
    ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1])
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e61_spread_tails')
